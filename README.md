# web-scraper

一个通用的命令行网页爬虫工具。给任意网址，就能提取网页的标题、描述、正文、所有链接、所有图片，还支持用 CSS 选择器自定义提取，结果可导出为 JSON。

## 功能特性

- 🌐 **通用解析**：不绑定任何网站，对任意 URL 提取标题 / 描述 / 正文 / 链接 / 图片
- 🔗 **链接提取**：自动把相对路径转成绝对地址
- 🖼️ **图片提取**：提取所有图片地址和 alt 描述
- 🎯 **CSS 选择器**：自定义提取任意元素（如 `h2.title`、`div.item p`）
- 📡 **调用 JSON API**：直接请求接口，用点路径提取字段（如 `data.card.name`）
- 🔁 **自动重试**：网络抖动时自动重试，提高稳定性
- 💾 **导出 JSON**：结果可保存为结构化文件
- 🧪 单元测试覆盖解析、选择器、字段提取逻辑

## 环境要求

- Python 3.9+
- `requests`、`beautifulsoup4`（`pip install requests beautifulsoup4`）

## 快速开始

### 方式一：解析 HTML（静态网站，默认）

```bash
# 提取基本信息（标题、描述、链接/图片数量）
python cli.py https://example.com

# 提取所有链接（-l）
python cli.py https://example.com -l

# 提取所有图片（-i）
python cli.py https://example.com -i

# 提取正文文本（-t）
python cli.py https://example.com -t

# 用 CSS 选择器自定义提取（-s）
python cli.py https://example.com -s "h2.title"

# 结果导出为 JSON（-o）
python cli.py https://example.com -o result.json
```

### 方式二：调用 JSON API（有接口的网站）

```bash
# 打印整个 JSON 返回
python cli.py api "https://api.xxx.com/user?id=1"

# 用点路径提取某个字段（-f）
python cli.py api "https://api.xxx.com/user?id=1" -f "data.card.name"
```

## 参数速查

| 短参数 | 长参数 | 作用 |
|---|---|---|
| `-l` | `--links` | 提取所有链接 |
| `-i` | `--images` | 提取所有图片 |
| `-t` | `--text` | 提取正文文本 |
| `-s` | `--selector` | CSS 选择器自定义提取 |
| `-o` | `--output` | 导出 JSON 文件 |
| `-f` | `--field` | API 字段路径（点路径） |

## 运行测试

```bash
python -m unittest test_scraper -v
```

## 项目结构

```
web-scraper/
├── cli.py           # 命令行入口
├── scraper.py       # 核心：fetch 下载 + parse 解析 + select 选择器
├── test_scraper.py  # 单元测试
└── README.md
```

## 设计说明

- **解析与网络分离**：`parse()` 和 `extract()` 是纯函数（不发起网络请求），可以直接用本地样本做单元测试，不必真的联网。
- **两条路径**：静态网站走「解析 HTML」，有接口的网站走「调用 API」，对应爬虫的两大场景。
- **自动重试**：`_request()` 对网络抖动做重试，提高稳定性。
- **礼貌抓取**：设置 User-Agent 伪装成浏览器；实际使用时请控制抓取频率，遵守目标网站的 robots.txt 与服务条款。

## 免责声明

本项目仅供学习 HTML 解析与爬虫技术。请勿用于抓取需要登录、有版权限制或明确禁止爬取的网站内容。
