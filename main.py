
import json
import aiohttp
import asyncio
import requests
import time
from datetime import datetime
from aiohttp import ClientTimeout
import os
import base58
import shutil
# 配置项
INPUT_FILE = 'input.json'
OUTPUT_FILE = 'output.json'
FAILED_LOG_FILE = 'failed_apis.log'
GITHUB_LOG_FILE = 'github_sources.log'
MAX_GITHUB_RESULTS = 2000
MAX_RETRIES = 3
GITHUB_TOKEN = os.getenv("GH_TOKEN", "")

SENSITIVE_KEYWORDS = [
    "内射", "中出", "强奸", "调教", "乱伦", "sm", "黑料", "母狗", "精液", "无码", "有码"]
DEFAULT_CATEGORIES = [
    { "name": "热门", "type": "movie", "query": "热门" },
    { "name": "最新", "type": "movie", "query": "最新" },
    { "name": "经典", "type": "movie", "query": "经典" },
    { "name": "豆瓣高分", "type": "movie", "query": "豆瓣高分" },
    { "name": "冷门佳片", "type": "movie", "query": "冷门佳片" },
    { "name": "华语", "type": "movie", "query": "华语" },
    { "name": "欧美", "type": "movie", "query": "欧美" },
    { "name": "韩国", "type": "movie", "query": "韩国" },
    { "name": "日本", "type": "movie", "query": "日本" },
    { "name": "动作", "type": "movie", "query": "动作" },
    { "name": "喜剧", "type": "movie", "query": "喜剧" },
    { "name": "爱情", "type": "movie", "query": "爱情" },
    { "name": "科幻", "type": "movie", "query": "科幻" },
    { "name": "悬疑", "type": "movie", "query": "悬疑" },
    { "name": "恐怖", "type": "movie", "query": "恐怖" },
    { "name": "R级", "type": "movie", "query": "R级" },
    { "name": "三级", "type": "movie", "query": "三级" },
    { "name": "情色", "type": "movie", "query": "情色" },
    { "name": "热门", "type": "tv", "query": "热门" },
    { "name": "美剧", "type": "tv", "query": "美剧" },
    { "name": "英剧", "type": "tv", "query": "英剧" },
    { "name": "韩剧", "type": "tv", "query": "韩剧" },
    { "name": "日剧", "type": "tv", "query": "日剧" },
    { "name": "国产剧", "type": "tv", "query": "国产剧" },
    { "name": "港剧", "type": "tv", "query": "港剧" },
    { "name": "日本动画", "type": "tv", "query": "日本动画" },
    { "name": "综艺", "type": "tv", "query": "综艺" },
    { "name": "纪录片", "type": "tv", "query": "纪录片" }
]
def replace_input_with_output():
    try:
        shutil.copyfile(OUTPUT_FILE, INPUT_FILE)
        print("✅ input.json 已被 output.json 替换")
    except Exception as e:
        print(f"❌ 替换 input.json 失败: {e}")

# ✅ 步骤 2：将 output.json 内容进行 Base58 编码并输出
def encode_output_base58():
    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            raw_data = f.read()
        encoded = base58.b58encode(raw_data.encode('utf-8')).decode('utf-8')

        with open('output_base58.txt', 'w', encoding='utf-8') as f:
            f.write(encoded)
        print("✅ output.json 已编码为 Base58 并保存为 output_base58.txt")
    except Exception as e:
        print(f"❌ Base58 编码失败: {e}")

# 将 input.json 的 api_site 添加到 LunaTV-config.json 的分割标记之后
def update_luna_tv_config():
    """
    将 input.json 的 api_site 添加到 LunaTV-config.json 的分割标记之后
    步骤：
    1. 读取 LunaTV-config.json 文件
    2. 找到分割标记项（lovedan.net）
    3. 清除分割标记之后的所有 api_site 项目
    4. 读取 input.json 文件，获取其 api_site
    5. 将 input.json 的 api_site 添加到分割标记之后
    6. 保存修改后的 LunaTV-config.json 文件
    """
    LUNA_CONFIG_FILE = 'LunaTV-config.json'
    try:
        # 读取 LunaTV-config.json
        with open(LUNA_CONFIG_FILE, 'r', encoding='utf-8') as f:
            luna_data = json.load(f)
        
        # 读取 input.json
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
        
        input_api_site = input_data.get('api_site', {})
        
        # 找到分割标记项的位置
        split_key = None
        api_site_items = list(luna_data.get('api_site', {}).items())
        for i, (key, value) in enumerate(api_site_items):
            if value.get('_comment') == '无法搜索1-分割标记':
                split_key = key
                split_index = i
                break
        
        if split_key:
            # 保留分割标记之前的项目，加上分割标记本身
            new_api_site = dict(api_site_items[:split_index + 1])
            
            # 添加 input.json 的 api_site
            new_api_site.update(input_api_site)
            
            # 更新 luna_data
            luna_data['api_site'] = new_api_site
            
            # 保存修改后的文件
            with open(LUNA_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(luna_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 已将 input.json 的 api_site 添加到 {LUNA_CONFIG_FILE} 的分割标记之后")
        else:
            print("❌ 未找到分割标记项")
    except Exception as e:
        print(f"❌ 更新 LunaTV-config.json 失败: {e}")
def validate_token(token):
    try:
        r = requests.get("https://api.github.com/user", headers={"Authorization": f"token {token}"})
        if r.status_code == 200:
            print("✅ GitHub Token 验证成功")
        else:
            print(f"❌ Token 验证失败: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"❌ Token 请求异常: {e}")
validate_token(GITHUB_TOKEN)
# 日志函数
def log_failed(api_url, reason):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(FAILED_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {api_url} - {reason}\n")

def log_github_source(url, status, extra=None):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {status} - {url}"
    if extra:
        line += f" - {extra}"
    with open(GITHUB_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + "\n")

# GitHub 请求头
def github_headers():
    return {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_TOKEN}"
    }

# 本地 JSON 加载
def load_local_json():
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f).get("api_site", {})
    except Exception as e:
        print(f"⚠️ 无法加载本地文件：{e}")
        return {}

# GitHub 搜索
def search_github_configs():
    url = "https://api.github.com/search/code"
    params = {
        "q": '"cache_time": 7200 "api_site" in:file language:JSON',
        "sort": "indexed",
        "order": "desc"
    }
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=github_headers(), params=params, timeout=10)
            response.raise_for_status()
            return response.json().get("items", [])[:MAX_GITHUB_RESULTS]
        except Exception as e:
            print(f"⚠️ GitHub 搜索失败（尝试 {attempt}/{MAX_RETRIES}）：{e}")
            time.sleep(2)
    return []

# 安全解析 JSON
def safe_json_load(text, raw_url=None):
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "api_site" in data:
            return {
                "api_site": data["api_site"],
                "custom_category": data.get("custom_category", [])
            }
        else:
            log_github_source(raw_url, "❌ 非预期结构", f"类型: {type(data).__name__}")
            return {"api_site": {}, "custom_category": []}
    except json.JSONDecodeError as e:
        log_github_source(raw_url, "❌ JSON语法错误", str(e))
        if raw_url:
            debug_file = f"debug_{raw_url.split('/')[-1]}"
            with open(debug_file, "w", encoding="utf-8") as f:
                f.write(text)
        return {"api_site": {}, "custom_category": []}
    except Exception as e:
        log_github_source(raw_url, "❌ 解析异常", str(e))
        return {"api_site": {}, "custom_category": []}

# 提取 GitHub 配置
def fetch_and_extract_api_sites(item):
    raw_url = item["html_url"].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    repo = item.get("repository", {})
    author = repo.get("owner", {}).get("login", "unknown")
    updated_at = repo.get("updated_at", "unknown")
    size_kb = item.get("size", 0) / 1024

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(raw_url, headers=github_headers(), timeout=5)
            response.raise_for_status()
            text = response.content.decode('utf-8-sig')
            result = safe_json_load(text, raw_url)
            if result["api_site"]:
                log_github_source(
                    raw_url,
                    "✅ 解析成功",
                    f"作者: {author}, 更新时间: {updated_at}, 大小: {size_kb:.1f} KB"
                )
            return result
        except Exception as e:
            if attempt == MAX_RETRIES:
                log_github_source(
                    raw_url,
                    "❌ 请求失败",
                    f"作者: {author}, 更新时间: {updated_at}, 错误: {str(e)}"
                )
            time.sleep(1)
    return {"api_site": {}, "custom_category": []}

# 分类项合并去重
def merge_custom_categories(all_categories):
    seen = set()
    merged = []
    for item in all_categories:
        key = (item.get("name"), item.get("type"), item.get("query"))
        if key not in seen:
            seen.add(key)
            merged.append(item)
    return merged

# API 可用性检测
async def check_api(session, api_url, name):
    try:
        async with session.get(api_url, timeout=ClientTimeout(total=5)) as response:
            if response.status != 200:
                log_failed(api_url, f"Status {response.status}")
                return False
            text = await response.text()
            for keyword in SENSITIVE_KEYWORDS:
                if keyword.lower() in name.lower():
                    log_failed(api_url, f"Filtered by name: {keyword}")
                    return False
                if keyword.lower() in text.lower():
                    log_failed(api_url, f"Filtered by content: {keyword}")
                    return False
            return True
    except Exception as e:
        log_failed(api_url, str(e))
        return False

# URL规范化函数
def normalize_api_url(url):
    """
    规范化API URL，去掉特定参数部分
    规则：
    1. 去掉查询参数（以?开头的部分）
    2. 去掉/at/xxx部分
    3. 去掉/from/xxx/at/xxx部分
    """
    # 去掉查询参数
    if '?' in url:
        url = url.split('?')[0]
    
    # 去掉/from/xxx/at/xxx部分
    if '/from/' in url:
        parts = url.split('/from/')
        if len(parts) > 1:
            base_part = parts[0]
            url = base_part
    
    # 去掉/at/xxx部分
    if '/at/' in url:
        parts = url.split('/at/')
        if len(parts) > 1:
            url = parts[0]
    
    # 移除末尾的斜杠
    url = url.rstrip('/')
    
    return url

# 主流程
async def main():
    all_sites = {}
    normalized_urls = set()  # 用于存储规范化后的URL
    all_categories = []

    local_sites = load_local_json()
    for site in local_sites.values():
        api_url = site.get("api")
        if api_url:
            normalized = normalize_api_url(api_url)
            if normalized not in normalized_urls:
                normalized_urls.add(normalized)
                all_sites[api_url] = site

    for item in search_github_configs():
        result = fetch_and_extract_api_sites(item)
        for site in result["api_site"].values():
            api_url = site.get("api")
            if api_url:
                normalized = normalize_api_url(api_url)
                if normalized not in normalized_urls:
                    normalized_urls.add(normalized)
                    all_sites[api_url] = site
        all_categories.extend(result["custom_category"])

    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [check_api(session, api_url, site.get("name", "")) for api_url, site in all_sites.items()]
        results = await asyncio.gather(*tasks)

    new_api_site = {}
    index = 1
    for i, (api_url, site) in enumerate(all_sites.items()):
        if results[i]:
            new_api_site[str(index)] = site
            index += 1

    new_data = {
     "cache_time": 7200,
    "api_site": new_api_site,
    "custom_category": merge_custom_categories(DEFAULT_CATEGORIES + all_categories)
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 完成：保留 {len(new_api_site)} 个合法且可用 API")
    print(f"📄 错误日志已保存到 {FAILED_LOG_FILE}")
    print(f"📄 GitHub 日志已保存到 {GITHUB_LOG_FILE}")
    print(f"💾 输出文件已保存为 {OUTPUT_FILE}")
    replace_input_with_output()
    encode_output_base58()
    update_luna_tv_config()
# 运行
if __name__ == '__main__':
    asyncio.run(main())
