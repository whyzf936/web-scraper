"""通用网页爬虫命令行工具。

用法示例：
    # 解析 HTML（默认，不用写子命令）
    python cli.py https://example.com              # 基本信息
    python cli.py https://example.com -l           # 所有链接
    python cli.py https://example.com -i           # 所有图片
    python cli.py https://example.com -t           # 正文文本
    python cli.py https://example.com -s "h2"      # CSS 选择器
    python cli.py https://example.com -o r.json    # 导出 JSON

    # 调用 JSON API
    python cli.py api "https://api.xxx.com/u?id=1" -f "data.name"
    python cli.py api "https://api.xxx.com/u?id=1"           # 打印整个 JSON
"""
from __future__ import annotations

import argparse
import json
import sys

from scraper import fetch, parse, select, fetch_json, extract

# Windows 控制台默认 GBK 编码，这里切到 UTF-8。
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


def cmd_scrape(args: argparse.Namespace) -> None:
    """抓取网页并按需输出。"""
    try:
        html = fetch(args.url)
    except Exception as e:
        print(f"❌ 抓取失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 自定义 CSS 选择器优先
    if args.selector:
        results = select(html, args.selector)
        if not results:
            print(f"📭 选择器「{args.selector}」没有匹配到任何元素")
            return
        for r in results:
            print(r)
        return

    data = parse(html, base_url=args.url)

    if args.links:
        for link in data["links"]:
            print(f"{link['text'] or '(无文字)'}\n  {link['href']}")
        return

    if args.images:
        for img in data["images"]:
            print(f"{img['alt'] or '(无描述)'}\n  {img['src']}")
        return

    if args.text:
        print(data["text"])
        return

    print(f"标题: {data['title'] or '(无标题)'}")
    if data["description"]:
        print(f"描述: {data['description']}")
    print(f"链接数: {len(data['links'])}")
    print(f"图片数: {len(data['images'])}")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 结果已导出到 {args.output}")


def cmd_api(args: argparse.Namespace) -> None:
    """调用 JSON API 并提取字段。"""
    try:
        data = fetch_json(args.url)
    except Exception as e:
        print(f"❌ 请求失败: {e}", file=sys.stderr)
        sys.exit(1)

    if args.field:
        value = extract(data, args.field)
        if value is None:
            print(f"❌ 路径「{args.field}」没有取到值")
            sys.exit(1)
        if isinstance(value, (dict, list)):
            print(json.dumps(value, ensure_ascii=False, indent=2))
        else:
            print(value)
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))


def build_scrape_parser() -> argparse.ArgumentParser:
    """解析 HTML 的参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="scrape",
        description="通用网页爬虫：解析 HTML 或调用 JSON API",
    )
    parser.add_argument("url", help="要抓取的网页地址")
    parser.add_argument("-l", "--links", action="store_true", help="提取所有链接")
    parser.add_argument("-i", "--images", action="store_true", help="提取所有图片")
    parser.add_argument("-t", "--text", action="store_true", help="提取正文文本")
    parser.add_argument("-s", "--selector", help="CSS 选择器，如 h2.title")
    parser.add_argument("-o", "--output", help="结果导出为 JSON 文件")
    return parser


def build_api_parser() -> argparse.ArgumentParser:
    """调用 JSON API 的参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="api",
        description="调用 JSON API 并提取字段",
    )
    parser.add_argument("url", help="接口地址")
    parser.add_argument("-f", "--field", help="字段路径，如 data.card.name")
    return parser


def main() -> None:
    # 第一个参数是 api 时走 API 模式，否则默认走 HTML 解析模式
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        sys.argv.pop(1)
        args = build_api_parser().parse_args()
        cmd_api(args)
    else:
        args = build_scrape_parser().parse_args()
        cmd_scrape(args)


if __name__ == "__main__":
    main()
