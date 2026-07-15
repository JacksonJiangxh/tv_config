# -*- coding: utf-8 -*-
"""
对现有输出做一次性精修（不过度去重）：
1. 全量集合（output.json / LunaTV-config.json）只屏蔽成人/AV，保留多域名变体；
2. 综合评估最好的 20 个节点单独输出，并在这 20 个里按资源核心名去重、只保留最优质的一个变体；
3. 输出：
   output.json（仅过滤成人/AV 的全量，保留变体，重编号）
   output_base58.txt
   output_top20.json（综合评估最好的 20 个节点，已同名去重）
   output_top20_base58.txt（用户要的「单独 base 编码文件」）

设计取舍（按用户反馈）：
- 不要"在集合里直接去重"，因为同名多域名变体（如「无尽资源」的 .me/.cc/.com）应保留在全量里；
- 去重只在挑选最终 20 个时做：同名只保留综合评分最高的那一个变体。
"""
import json
import re
import os
import sys
import io
import subprocess
import base58
import shutil

# 强制 stdout/stderr 为 UTF-8，避免 Windows GBK 控制台打印 emoji/中文时报错
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.abspath(__file__))


# ------------------------- 基础工具 -------------------------
def normalize_api_url(url):
    """规范化 API URL：忽略协议/常见前缀、去掉查询参数、/from/、/at/、结尾斜杠"""
    if not url:
        return ""
    u = url.strip()
    u = re.sub(r"^https?://", "", u, flags=re.I)
    u = re.sub(r"^www\.", "", u, flags=re.I)
    if "?" in u:
        u = u.split("?")[0]
    if "/from/" in u:
        u = u.split("/from/")[0]
    if "/at/" in u:
        u = u.split("/at/")[0]
    u = u.rstrip("/")
    return u.lower()


# ------------------------- 同名去重：核心名归一化（基于全量 549 个资源名聚类分析得出） -------------------------
# 通用中文词：可出现在任意位置，去掉不影响品牌识别
GEN_CJK = ["资源", "影视", "视频", "电影", "电视剧", "点播", "采集", "合集", "接口",
           "在线", "免费", "最新", "高清", "直播", "仓库", "专用", "网络", "网", "站",
           "短剧", "联盟", "备用", "新版"]
# 通用拉丁词：作为整词或含 api 的域名痕迹需剔除（保留 CK/1080/souav/ok 等品牌拉丁）
GENERIC_LATIN = {"tv", "new", "com", "www", "http", "https"}
# 尾随语气词/填充噪声（如「资源阿」「啊啊」），真实品牌不会以这些结尾
FILLER = "阿啊呀哈哦呢嘛哪呃嘞"

# 全角→半角映射
_FW_MAP = str.maketrans(
    "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ０１２３４５６７８９",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")


def clean_name(name):
    """提取资源核心名，用于同名去重（规则来自对仓库全部资源名的聚类分析）。

    关键结论：不能删除所有拉丁/数字（否则 CK/1080/souav 等品牌被清空而误并），
    只能「弱化」装饰与通用词，保留中文品牌与拉丁/数字品牌。

    步骤：
      1. 小写 + 全角转半角
      2. 仅保留「中文 + 字母数字」，删除 emoji/符号/空格/括号
      3. 删除通用中文词（资源/影视/点播/采集/站/网/备用/新版 …）
      4. 删除通用拉丁词及含 api 的域名痕迹（wujinapi/api/com/tv/new）
      5. 删除独立尾序号（版本号，如「无尽资源1」→ 无尽）；多位数品牌(1080/360/91)保留
      6. 删除尾随语气词填充噪声（阿/啊啊 …）
      7. 若清空则回退原名（小写），避免大规模误并
    """
    if not name:
        return ""
    s = name.lower().translate(_FW_MAP)
    # 仅保留中文 + 字母数字，删掉 emoji/符号/空格/括号等一切装饰
    s = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", s)
    # 删除通用中文词（任意位置）
    for g in GEN_CJK:
        s = s.replace(g, "")
    # 拆词：保留中文片段与品牌拉丁/数字，剔除域名痕迹
    runs = re.findall(r"[a-z0-9]+|[一-鿿]+", s)
    kept = []
    for t in runs:
        if re.search(r"[一-鿿]", t):          # 中文片段保留
            kept.append(t)
            continue
        low = t.lower()
        if "api" in low:                       # wujinapi 等域名痕迹
            continue
        if low in GENERIC_LATIN:
            continue
        kept.append(t)                          # 品牌拉丁/数字保留（CK/1080/souav/ok…）
    key = "".join(kept)
    # 删除独立尾序号（版本号）：仅当尾随单数字且前接非数字时
    key = re.sub(r"(?<=[一-鿿a-z])\d$", "", key)
    # 删除尾随语气词填充噪声
    key = re.sub(r"[" + FILLER + "]+$", "", key)
    return key if key else name.lower()         # 兜底：避免清空后误并


# 成人 / AV 关键词（小写匹配）
ADULT_KEYWORDS = [
    "av", "成人", "色情", "番号", "白嫖", "淫水", "美少女", "香奶儿",
    "性爱", "麻豆", "高潮", "做爱", "无码", "有码", "内射", "中出",
    "强奸", "调教", "乱伦", "母狗", "精液", "黑料", "sm",
]


def is_adult(site):
    if site.get("is_adult") or site.get("isAdult"):
        return True
    name = site.get("name") or ""
    if "🔞" in name:
        return True
    low = name.lower()
    if re.search(r"\bav\b", low) or low.startswith("av") or "av-" in low or "av资源" in low:
        return True
    for kw in ADULT_KEYWORDS:
        if kw in low:
            return True
    return False


# ------------------------- 健康数据解析 -------------------------
def parse_health(report_path):
    health = {}
    if not os.path.exists(report_path):
        print("⚠️ 未找到 report.md，评分将使用默认满分")
        return health
    text = open(report_path, encoding="utf-8").read()
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")]
        # ['', 状态, 名称, 地址, API, 搜索, 成功, 失败, 成功率, 趋势, '']
        if len(cells) < 10:
            continue
        name, detail, api, search, ok, fail, rate, trend = (
            cells[2], cells[3], cells[4], cells[5], cells[6], cells[7], cells[8], cells[9]
        )
        m = re.search(r"\[Link\]\(([^)]*)\)", api)
        if not m:
            continue
        api_url = m.group(1)
        try:
            rate_v = float(rate.replace("%", ""))
        except ValueError:
            rate_v = 100.0
        health[normalize_api_url(api_url)] = {
            "name": name,
            "search": search,
            "ok": int(ok) if ok.isdigit() else 0,
            "fail": int(fail) if fail.isdigit() else 0,
            "rate": rate_v,
            "trend": trend,
        }
    return health


# ------------------------- 过滤 / 挑选 -------------------------
def filter_adults_only(sites):
    """全量集合：只过滤成人/AV，保留多域名变体。分割标记等特殊项永远保留"""
    result = {}
    removed = 0
    for key, site in sites.items():
        if "分割标记" in (site.get("_comment") or ""):
            result[key] = site
            continue
        if is_adult(site):
            removed += 1
            continue
        result[key] = site
    return result, removed


def evaluate(site, health):
    """综合评分（用于选出最好的 20 个节点）：健康成功率 + 搜索 + 7天趋势 + https + 直连 + detail"""
    api = site.get("api", "")
    h = health.get(normalize_api_url(api), {})
    rate = h.get("rate", 100.0)
    search = 1 if h.get("search") == "✅" else 0
    trend = h.get("trend", "")
    tg = trend.count("✅")
    https = 1 if api.lower().startswith("https") else 0
    proxied = 1 if ("pz." in api or "?url=" in api or "qzz.io" in api) else 0
    detail = 1 if site.get("detail") else 0
    return rate + search * 15 + tg * 3 + https * 5 + (1 - proxied) * 5 + detail * 3


def pick_top20_distinct(sites, health, n=20):
    """按综合评分排序后，按资源核心名去重（同名只保留最优质的一个变体），取前 n 个"""
    ranked = sorted(sites.values(), key=lambda s: evaluate(s, health), reverse=True)
    out = {}
    i = 1
    seen = set()
    for s in ranked:
        cn = clean_name(s.get("name", ""))
        key = cn if cn else ("_uniq", id(s))   # 无名条目各自独立，避免误并
        if key in seen:
            continue
        seen.add(key)
        out[str(i)] = s
        i += 1
        if len(out) >= n:
            break
    return out


def reindex(sites):
    out = {}
    i = 1
    for site in sites.values():
        out[str(i)] = site
        i += 1
    return out


def write_base58(json_obj, txt_path):
    raw = json.dumps(json_obj, ensure_ascii=False, indent=2)
    enc = base58.b58encode(raw.encode("utf-8")).decode("utf-8")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(enc)
    return raw


# ------------------------- 主流程 -------------------------
def main():
    health = parse_health(os.path.join(ROOT, "report.md"))

    # ---- 全量来源：以当前 output.json 为准（已含多域名变体）；缺失时才回退 git HEAD ----
    src_path = os.path.join(ROOT, "output.json")
    try:
        with open(src_path, encoding="utf-8") as f:
            src = json.load(f)
        print("📥 使用当前 output.json 作为全量来源（保留多域名变体）")
    except FileNotFoundError:
        raw = subprocess.check_output(["git", "show", "HEAD:output.json"], cwd=ROOT).decode("utf-8")
        src = json.loads(raw)
        print("📥 当前 output.json 缺失，从 git HEAD 读取原始全量")

    # ---- 1) 全量只过滤成人/AV，保留变体 ----
    full, ra = filter_adults_only(src.get("api_site", {}))
    full_re = reindex(full)
    new_out = {
        "cache_time": src.get("cache_time", 7200),
        "api_site": full_re,
        "custom_category": src.get("custom_category", []),
    }
    write_base58(new_out, os.path.join(ROOT, "output_base58.txt"))
    with open(src_path, "w", encoding="utf-8") as f:
        json.dump(new_out, f, ensure_ascii=False, indent=2)
    print(f"✅ output.json 已精修：仅屏蔽成人/AV {ra} 条，保留多域名变体共 {len(full_re)} 条")

    # ---- 2) 综合评估最好的 20 个节点（同名只保留最优变体）----
    top20 = pick_top20_distinct(full, health, 20)
    top_out = {
        "cache_time": src.get("cache_time", 7200),
        "api_site": top20,
        "custom_category": src.get("custom_category", []),
    }
    write_base58(top_out, os.path.join(ROOT, "output_top20_base58.txt"))
    with open(os.path.join(ROOT, "output_top20.json"), "w", encoding="utf-8") as f:
        json.dump(top_out, f, ensure_ascii=False, indent=2)
    print(f"✅ 已生成 output_top20.json / output_top20_base58.txt（共 {len(top20)} 个，已同名去重）")
    print("🏆 综合评估 Top20：")
    for i, s in enumerate(top20.values(), 1):
        print(f"  {i:2d}. {s.get('name','')}  ->  {s.get('api','')}")

    # ---- 3) 同步精修 LunaTV-config.json（含备份）----
    # 保留分割标记之前的手工精选条目，再追加「保留变体、仅屏蔽成人」的全量 output，
    # 与后续 python main.py 的 update_luna_tv_config 行为保持一致
    luna_path = os.path.join(ROOT, "LunaTV-config.json")
    if os.path.exists(luna_path):
        shutil.copyfile(luna_path, luna_path + ".bak")
        with open(luna_path, encoding="utf-8") as f:
            luna = json.load(f)
        items = list(luna.get("api_site", {}).items())
        split_idx = next((i for i, (k, v) in enumerate(items)
                          if v.get("_comment") == "无法搜索1-分割标记"), -1)
        if split_idx >= 0:
            head = dict(items[:split_idx + 1])            # 含分割标记
            appended = {k: v for k, v in full.items() if not is_adult(v)}
            merged = {}
            idx = 1
            for k, v in list(head.items()) + list(appended.items()):
                merged[str(idx)] = v
                idx += 1
            luna["api_site"] = merged
        else:
            luna_full, _ = filter_adults_only(luna.get("api_site", {}))
            luna["api_site"] = reindex(luna_full)
        with open(luna_path, "w", encoding="utf-8") as f:
            json.dump(luna, f, ensure_ascii=False, indent=2)
        adult_in_full = sum(1 for v in full.values() if is_adult(v))
        print(f"✅ LunaTV-config.json 已同步精修（备份为 .bak）：保留变体共 {len(luna['api_site'])} 条（全量含成人 {adult_in_full} 条已排除）")


if __name__ == "__main__":
    main()
