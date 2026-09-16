"""通用网页爬虫命令行工具。

用法示例：
    python cli.py https://example.com                 # 提取基本信息
    python cli.py https://example.com --links         # 提取所有链接
    python cli.py https://example.com --images        # 提取所有图片
    python cli.py https://example.com --text          # 提取正文文本
    python cli.py https://example.com --selector "h2" # 自定义 CSS 选择器
    python cli.py https://example.com -o result.json  # 结果导出为 JSON
"""
from __future__ import annotations

import argparse
import json
import sys

from scraper import fetch, parse, select

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

    # 按标志输出不同内容
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

    # 默认：输出基本信息摘要
    print(f"标题: {data['title'] or '(无标题)'}")
    if data["description"]:
        print(f"描述: {data['description']}")
    print(f"链接数: {len(data['links'])}")
    print(f"图片数: {len(data['images'])}")

    # 需要导出时写 JSON
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 结果已导出到 {args.output}")


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="scrape",
        description="通用网页爬虫：提取任意网页的标题、链接、图片、正文",
    )
    parser.add_argument("url", help="要抓取的网页地址")
    parser.add_argument("--links", action="store_true", help="提取所有链接")
    parser.add_argument("--images", action="store_true", help="提取所有图片")
    parser.add_argument("--text", action="store_true", help="提取正文文本")
    parser.add_argument("--selector", help="自定义 CSS 选择器，如 h2.title")
    parser.add_argument("-o", "--output", help="把结果导出为 JSON 文件")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    cmd_scrape(args)


if __name__ == "__main__":
    main()
