"""通用网页爬虫命令行工具。

用法示例：
    # 解析 HTML
    python cli.py https://example.com                 # 提取基本信息
    python cli.py https://example.com --links         # 提取所有链接
    python cli.py https://example.com --selector "h2" # 自定义 CSS 选择器

    # 调用 JSON API
    python cli.py api "https://api.xxx.com/user?id=1" --field "data.name"
    python cli.py api "https://api.xxx.com/user?id=1" # 打印整个 JSON
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
        # 没指定字段，打印整个 JSON
        print(json.dumps(data, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="scrape",
        description="通用爬虫：解析 HTML 或调用 JSON API 抓取数据",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_scrape = sub.add_parser("scrape", help="解析 HTML 网页")
    p_scrape.add_argument("url", help="要抓取的网页地址")
    p_scrape.add_argument("--links", action="store_true", help="提取所有链接")
    p_scrape.add_argument("--images", action="store_true", help="提取所有图片")
    p_scrape.add_argument("--text", action="store_true", help="提取正文文本")
    p_scrape.add_argument("--selector", help="自定义 CSS 选择器，如 h2.title")
    p_scrape.add_argument("-o", "--output", help="把结果导出为 JSON 文件")
    p_scrape.set_defaults(func=cmd_scrape)

    p_api = sub.add_parser("api", help="调用 JSON API")
    p_api.add_argument("url", help="接口地址")
    p_api.add_argument("--field", help="要提取的字段路径，如 data.card.name")
    p_api.set_defaults(func=cmd_api)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
