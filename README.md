
***

## 📂 仓库文件结构与用途

本仓库自动聚合 MoonTV / LunaTV 的影视源配置，并每日检测可用性。文件按用途分四类：

### 1. 核心脚本（可手动修改）
| 文件 | 作用 |
|------|------|
| `main.py` | 主程序：`input.json` + `LunaTV-config.json` → 生成 `output.json` / `LunaTV-config.json` 并做 Base58 编码；Top20 由 `refine_output.py` 基于健康报告按「可搜索」过滤生成 |
| `refine_output.py` | 精修脚本：从全量结果屏蔽成人/AV、保留变体并生成 Top20（手动重跑用） |
| `check_api.js` | 每日检测各源可用性，输出 `report.md` |
| `update_readme.js` | 把 `report.md` 的可用性表格同步进本 README |
| `.github/workflows/all-check.yml` | CI：每天自动跑上述流程并提交产物 |

### 2. 配置与源数据（手改入口）
| 文件 | 作用 |
|------|------|
| `LunaTV-config.json` | **线上配置**，被 App / `CORSAPI` / `web-editor` 直接读取；自动化会向其追加新源 |
| `config初始.json` | 初始种子配置（参考用；当前自动化未读取，如不需要可删除） |

### 3. 自动生成产物（CI 产出，**请勿手动修改**，会被下一次运行覆盖）
| 文件 | 作用 |
|------|------|
| `input.json` / `input.txt` | `output.json` 的副本 / 其 Base58（流程中间产物） |
| `output.json` / `output_base58.txt` | 全量结果：保留多域名变体、已屏蔽成人/AV |
| `output_top20.json` / `output_top20_base58.txt` | 综合评分最高的 20 个节点（同名资源仅留最优变体） |
| `jingjian.json` / `jingjian.txt` | 去掉 `_comment` 标记后的配置 |
| `jin18.json` / `jin18.txt` | 在 `jingjian` 基础上再去掉成人/AV 的配置 |
| `LunaTV-config.txt` | `LunaTV-config.json` 的 Base58 |
| `report.md` | API 健康报告（由 `check_api.js` 生成） |
| `failed_apis.log` / `github_sources.log` | 运行日志（抓取出错源 / GitHub 源列表） |

### 4. 子项目 / 依赖
| 文件/目录 | 作用 |
|-----------|------|
| `CORSAPI/` | Cloudflare Worker：为源接口提供 CORS 代理（读取 `LunaTV-config.json`） |
| `web-editor/` | 浏览器端可视化编辑 `LunaTV-config.json` 的小工具 |
| `requirements.txt` | Python 依赖（aiohttp / requests / base58） |

> 注：App 端实际使用 Base58 文件（如 `LunaTV-config.txt`、`output_top20_base58.txt`）；`*.json` 为便于审阅与二次处理的明文版本。

***

<!-- CONFIG_COMPARE_START -->
## 📦 配置源对比

（以下内容由 CI 自动生成，请勿手动修改）

| 配置源 | 资源数量 | 成人内容 | 适用场景 |
| - | - | - | - |
| 🏆 Top20 (output_top20) | 20 个 | 已过滤 | 推荐：综合评分最优的 20 个节点（同名仅留最优变体） |
| 全量 (output) | 66 个 | 已过滤 | 完整功能、最大兼容性（保留多域名变体） |
| 主配置 (LunaTV-config) | 60 个 | 已过滤 | App 默认配置：手工精选 + 全量变体 |

<!-- CONFIG_COMPARE_END -->

🧩 **前缀替换逻辑**

- 若 JSON 中的 `api` 字段已包含旧前缀（`?url=`），系统会自动去除旧前缀并替换为新的代理前缀。
- 可自定义代理路径，方便接入私有 API 或多 Worker 配置。

***

# API 健康报告（每日自动检测API状态）

## API 状态（最近更新：2026-08-03 10:26 CST）

- 总 API 数量：60
- 成功 API 数量：58
- 失败 API 数量：2
- 平均可用率：99.1%
- 完美可用率（100%）：50 个
- 高可用率（80%-99%）：10 个
- 中等可用率（50%-79%）：0 个
- 低可用率（<50%）：0 个

<div style="font-size: 11px;">

<!-- API_TABLE_START -->
| 状态 | 资源名称 | 地址 | API | 搜索功能 | 成功次数 | 失败次数 | 成功率 | 最近7天趋势 |
|------|---------|-----|-----|---------|---------:|--------:|-------:|--------------|
| ✅ | 🎬 ikunzy资源 | [Link](https://www.ikunzy.com) | [Link](https://www.ikunzy.com/api.php/provide/vod/) | ✅ | 18 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 🎬 无广1线 (非凡) | [Link](https://yonghu.ffzyapi8.com) | [Link](https://yonghu.ffzyapi8.com/api.php/provide/vod/from/ffm3u8/at/json/) | ✅ | 18 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 🎬-爱奇艺- | [Link](https://iqiyizyapi.com) | [Link](https://iqiyizyapi.com/api.php/provide/vod) | ✅ | 30 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 🎬360 资源 | [Link](https://360zy.com) | [Link](https://360zyzz.com/api.php/provide/vod) | ✅ | 30 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 🎬iKun资源 | [Link](https://ikunzy.com) | [Link](https://ikunzyapi.com/api.php/provide/vod) | ✅ | 21 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 🎬U酷影视 | [Link](https://www.ukuzy.com) | [Link](https://api.ukuapi88.com/api.php/provide/vod) | ✅ | 30 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 🎬如意资源 | [Link](https://www.ryzyw.com) | [Link](https://cj.rycjapi.com/api.php/provide/vod) | ✅ | 21 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 🎬新浪资源 | [Link](https://xinlangapi.com) | [Link](https://api.xinlangapi.com/xinlangapi.php/provide/vod) | ✅ | 30 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 🎬暴风资源 | [Link](https://bfzy.tv) | [Link](https://bfzyapi.com/api.php/provide/vod) | ✅ | 21 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 🎬百度云zy | [Link](https://bdzy1.com) | [Link](https://pz.v88.qzz.io/?url=https://api.apibdzy.com/api.php/provide/vod) | ✅ | 21 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 🎬红牛资源 | [Link](https://www.hongniuzy.com) | [Link](https://www.hongniuzy2.com/api.php/provide/vod) | ✅ | 30 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 🎬豪华资源 | [Link](https://www.haohuazy.com) | [Link](https://hhzyapi.com/api.php/provide/vod) | ✅ | 21 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 🎬速播资源 | [Link](https://www.subozy.com) | [Link](https://subocaiji.com/api.php/provide/vod) | ✅ | 30 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 🎬量子资源 | [Link](https://cj.lzcaiji.com) | [Link](https://cj.lzcaiji.com/api.php/provide/vod) | ✅ | 20 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 🎬金鹰点播 | [Link](https://jinyingzy.com) | [Link](https://jyzyapi.com/provide/vod/from/jinyingyun/at/json) | ✅ | 21 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 🎬魔都动漫 | [Link](https://caiji.moduapi.cc) | [Link](https://caiji.moduapi.cc/api.php/provide/vod) | ✅ | 30 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 🎬魔都资源 | [Link](https://www.moduzy.net) | [Link](https://www.mdzyapi.com/api.php/provide/vod) | ✅ | 30 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 🔅飞速资源ᴴ | [Link](http://fszy1.com) | [Link](http://fszy1.com/api.php/provide/vod) | ❌ | 21 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 1080资源 | [Link](https://api.1080zyku.com) | [Link](https://api.1080zyku.com/inc/api_mac10.php) | ✅ | 21 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 1080资源 | [Link](https://1080zyk.com) | [Link](https://api.yzzy-api.com/inc/api_mac10.php) | ✅ | 18 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 360资源 | - | [Link](https://360zy.com/api.php/provide/vod) | ✅ | 21 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | TV-神马云 | [Link](https://api.1080zyku.com) | [Link](https://api.1080zyku.com/inc/apijson.php/) | ✅ | 21 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | TV-麒麟资源 | [Link](https://www.qilinzyz.com/) | [Link](https://www.qilinzyz.com/api.php/provide/vod) | ❌ | 30 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | U酷资源 | [Link](https://api.ukuapi.com) | [Link](https://api.ukuapi.com/api.php/provide/vod) | ✅ | 21 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | U酷资源 | - | [Link](https://api.ukuapi88.com/api.php/provide/art/?ac=list) | 不匹配 | 21 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 丫丫点播 | [Link](https://cj.yayazy.net) | [Link](https://cj.yayazy.net/api.php/provide/vod) | ❌ | 30 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 优质资源 | [Link](https://api.yzzy-api.com) | [Link](https://api.yzzy-api.com/inc/apijson.php) | ✅ | 30 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 优质资源库1080zyk6.com高清 | - | [Link](https://api.yzzy-api.com/inc/ldg_api_all.php/provide/vod) | ❌ | 21 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 天涯影视资源 | [Link](https://tyyszyapi.com) | [Link](https://tyyszyapi.com/api.php/provide/vod) | ❌ | 30 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 天涯资源 | - | [Link](https://tyyszy.com/api.php/provide/vod) | ❌ | 30 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 建安资源站 | - | [Link](http://154.219.117.232:9981/jacloudapi.php/provide/vod/) | 不匹配 | 30 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 新浪 | [Link](https://api.xinlangapi.com) | [Link](https://api.xinlangapi.com/xinlangapi.php/provide/vod/josn) | ✅ | 18 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 无尽资源 | [Link](https://wujinzy.net) | [Link](https://api.wujinapi.me/api.php/provide/vod) | ✅ | 30 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 无尽资源 | [Link](https://api.wujinapi.cc) | [Link](https://api.wujinapi.cc/api.php/provide/vod) | ✅ | 21 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 无尽资源 | [Link](https://api.wujinapi.com) | [Link](https://api.wujinapi.com/api.php/provide/vod) | ✅ | 21 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 无尽资源 | [Link](https://api.wujinapi.net) | [Link](https://api.wujinapi.net/api.php/provide/vod) | ✅ | 21 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 无水印资源网采集接口 | - | [Link](https://api.wsyzy.net/api.php/provide/vod) | ❌ | 30 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 杏吧资源 | [Link](https://sex8zy8.com) | [Link](https://xingba222.com/api.php/provide) | ❌ | 18 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 牛牛点播 | [Link](https://api.niuniuzy.me) | [Link](https://api.niuniuzy.me/api.php/provide/vod) | ❌ | 30 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 神马资源 | [Link](https://img.smdyw.top) | [Link](https://img.smdyw.top/api.php/provide/vod) | ❌ | 18 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 红牛资源 | [Link](https://www.hongniuzy3.com) | [Link](https://www.hongniuzy3.com/api.php/provide/vod) | ✅ | 21 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 索尼资源 | [Link](https://suonizy.net) | [Link](https://suoniapi.com/api.php/provide/vod) | ❌ | 30 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 豆瓣资源 | [Link](https://dbzy.tv) | [Link](https://dbzy.tv/api.php/provide/vod) | 无结果 | 21 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 豆瓣资源 | [Link](https://dbzy.tv) | [Link](https://caiji.dbzy5.com/api.php/provide/vod) | 无结果 | 30 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 辣椒资源黄黄 | - | [Link](https://apilj.com/api.php/provide) | ❌ | 21 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 量子资源 | - | [Link](https://cj.lziapi.com/api.php/provide/vod) | ✅ | 29 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 金鹰资源 | [Link](https://jyzyapi.com) | [Link](https://jyzyapi.com/api.php/provide/vod) | ✅ | 30 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 闪电资源 | [Link](https://sdzyapi.com) | [Link](https://sdzyapi.com/api.php/provide/vod) | ❌ | 21 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 闪电资源 | [Link](https://xsd.sdzyapi.com) | [Link](https://xsd.sdzyapi.com/api.php/provide/vod) | ❌ | 30 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 非凡影视 | [Link](http://ffzy5.tv) | [Link](http://ffzy5.tv/api.php/provide/vod) | ✅ | 30 | 0 | 100.0% | ✅✅✅✅✅✅✅ |
| ✅ | 🎬最大资源 | [Link](https://zuida.xyz) | [Link](https://api.zuidapi.com/api.php/provide/vod) | ✅ | 29 | 1 | 96.7% | ❌✅✅✅✅✅✅ |
| ✅ | 快车资源阿 | [Link](https://kuaichezy.com) | [Link](https://caiji.kuaichezy.org/api.php/provide) | ❌ | 29 | 1 | 96.7% | ❌✅✅✅✅✅✅ |
| ✅ | 快车资源阿 | - | [Link](https://caiji.kuaichezy.org/api.php/provide/vod) | ❌ | 29 | 1 | 96.7% | ❌✅✅✅✅✅✅ |
| ✅ | 樱花资源 | - | [Link](https://m3u8.apiyhzy.com/api.php/provide/vod) | ❌ | 29 | 1 | 96.7% | ✅✅✅✅✅✅✅ |
| ✅ | 🔅樱花资源ᴴ | [Link](https://yhzy.cc) | [Link](https://yhzy.cc/api.php/provide/vod) | ✅ | 20 | 1 | 95.2% | ✅✅✅✅✅✅✅ |
| ✅ | 最大点播 | [Link](http://zuidazy.me) | [Link](http://zuidazy.me/api.php/provide/vod) | ✅ | 20 | 1 | 95.2% | ❌✅✅✅✅✅✅ |
| ❌ | 猫眼资源 | [Link](https://www.maoyanzy.com) | [Link](https://api.maoyanapi.top/api.php/provide) | ❌ | 17 | 1 | 94.4% | ✅✅✅✅✅✅❌ |
| ✅ | 虎牙资源 | [Link](https://www.huyaapi.com) | [Link](https://www.huyaapi.com/api.php/provide/vod) | ✅ | 28 | 2 | 93.3% | ✅✅✅✅✅✅✅ |
| ❌ | 🎬猫眼资源 | [Link](https://www.maoyanzy.com) | [Link](https://api.maoyanapi.top/api.php/provide/vod) | ❌ | 27 | 3 | 90.0% | ✅✅✅✅✅✅❌ |
| ✅ | 雨哥哥资源 | [Link](http://cj.baozi66.top:66) | [Link](http://cj.baozi66.top:66/api.php/provide/vod) | ❌ | 16 | 2 | 88.9% | ✅✅✅✅✅✅✅ |
<!-- API_TABLE_END -->

***

# 免责声明

> **在使用本仓库前，请务必仔细阅读本声明。**
> 任何以任何形式访问、使用、复制、修改或分发本仓库内容的行为，均视为已阅读并同意本免责声明的全部条款。

***

## 一、定义与范围

- **本仓库**：指本 GitHub 仓库及其直接或间接相关的其他仓库。
- **维护者**：指本仓库的管理员、维护者及任何参与内容整理与分享的人员。
- **仓库内容**：指本仓库中提供的全部配置文件、源定义、代码片段、文档说明及引用的外部资源信息。

***

## 二、仓库用途说明（MoonTV / LunaTV 源配置）

1. 本仓库主要提供 **MoonTV / LunaTV 等相关项目的源配置、订阅定义或配置示例**，内容均整理自互联网公开信息。
2. 本仓库内容 **仅用于学习、测试与技术研究目的**，包括但不限于配置格式研究、源聚合方式分析及客户端兼容性测试。
3. **本仓库不存储、不托管、不分发任何音视频文件、媒体流或受版权保护的内容**，亦不提供任何形式的媒体服务。
4. 除非另有明确书面声明，本仓库 **不授予任何商业使用许可**。
5. 严禁将本仓库内容用于任何违反法律法规、版权规则或所在司法辖区政策的用途。

***

## 三、无任何担保声明

本仓库及其内容均以 **“现状（AS IS）”** 方式提供，维护者不作出任何形式的明示或暗示担保，包括但不限于：

- 合法性
- 准确性
- 完整性
- 可用性
- 适用于特定目的

使用本仓库内容所产生的一切风险均由使用者自行承担。

***

## 四、责任限制

1. 因使用、误用、修改或分发本仓库内容而导致的任何直接或间接损失，包括但不限于数据丢失、系统故障、服务中断、法律风险等，维护者概不负责。
2. 用户在使用本仓库内容过程中，如违反其所在国家或地区的法律法规，所产生的一切法律责任均由用户自行承担，与本仓库及维护者无关。

***

## 五、第三方软件与项目声明

1. MoonTV、LunaTV 及任何在本仓库中提及的第三方软件、硬件、服务或项目，均 **与本仓库不存在任何隶属、合作、授权或背书关系**。
2. 本仓库不对任何第三方软件或服务的功能、合法性或可用性作出保证。
3. 因使用第三方软件或服务所产生的一切后果，均由使用者自行承担。

***

## 六、转载与分发限制

1. 未经维护者明确授权，**禁止以任何形式在其他平台、网站、公众号、自媒体或镜像站点转载、发布或再分发本仓库内容**。
2. 允许在 GitHub 平台内出于学习和研究目的进行 fork，但须保留本免责声明且不得改变仓库性质或用途。
3. 通过正常开发工具获取的域名、地址或配置信息，且未涉及逆向工程或网络攻击行为的，不构成对计算机系统的非法侵入。

***

## 七、知识产权与侵权处理

1. 若任何单位或个人认为本仓库内容可能侵犯其合法权益，请及时联系维护者，并提供有效的身份证明及权属证明材料。
2. 在核实相关材料后，维护者将依法依规尽快删除或处理相关内容。

***

## 八、使用期限与删除建议

1. 本仓库内容仅供 **临时学习与研究参考**。
2. 任何关于使用时限（如 24 小时）的表述，均属于风险提示性质，并非强制性法律义务（法律另有规定的除外）。
3. 建议用户在完成学习或研究后，及时删除本仓库内容的本地副本。
4. 如对相关功能存在长期或生产环境需求，请自行独立开发实现。

***

## 九、司法辖区提示

1. 本仓库内容 **不建议在中国大陆地区使用**，尤其是在相关应用或配置可能违反当地法律法规的情形下。
2. 用户应自行评估并承担因使用本仓库内容所带来的合规与法律风险。

***

## 十、免责声明的修改与接受

1. 维护者保留在不另行通知的情况下，随时修改或补充本免责声明的权利。
2. 任何对本仓库内容的访问、使用、复制、修改或分发行为，均视为已充分阅读并接受本免责声明的全部内容。

**若您不同意本免责声明中的任何条款，请立即停止使用并删除本仓库的全部内容。**

***

## ⭐ Star History

[![Star History](https://starchart.cc/hafrey1/LunaTV-config.svg?variant=light)](https://starchart.cc/hafrey1/LunaTV-config)
