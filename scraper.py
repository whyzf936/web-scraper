"""通用网页爬虫核心模块：负责下载网页并解析出结构化信息。

特点：不绑定任何特定网站，对任意 URL 都能提取标题、描述、正文、链接、图片，
还支持用 CSS 选择器自定义提取。
"""
from __future__ import annotations

from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# 伪装成浏览器，避免被一些网站直接拒绝
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}


def fetch(url: str, timeout: int = 10) -> str:
    """下载网页，返回 HTML 文本；网络错误会抛出异常。"""
    resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    resp.raise_for_status()  # 状态码非 2xx 时抛异常
    # 有些网站不声明编码，用自动检测避免中文乱码
    if resp.encoding is None or resp.encoding.lower() == "iso-8859-1":
        resp.encoding = resp.apparent_encoding
    return resp.text


def parse(html: str, base_url: str = "") -> dict:
    """解析 HTML，返回标题、描述、正文、链接、图片等结构化信息。

    纯函数：不发起网络请求，方便单元测试。
    """
    soup = BeautifulSoup(html, "html.parser")

    # 标题
    title = soup.title.get_text(strip=True) if soup.title else ""

    # meta 描述
    description = ""
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        description = meta_desc["content"].strip()

    # 正文纯文本：先剔除脚本/样式，再取纯文本
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = " ".join(soup.get_text(separator=" ", strip=True).split())[:2000]

    # 所有链接（相对路径转成绝对路径）
    links = []
    for a in soup.find_all("a", href=True):
        href = urljoin(base_url, a["href"]) if base_url else a["href"]
        links.append({"text": a.get_text(strip=True), "href": href})

    # 所有图片
    images = []
    for img in soup.find_all("img", src=True):
        src = urljoin(base_url, img["src"]) if base_url else img["src"]
        images.append({"alt": img.get("alt", ""), "src": src})

    return {
        "title": title,
        "description": description,
        "text": text,
        "links": links,
        "images": images,
    }


def select(html: str, selector: str) -> list[str]:
    """按 CSS 选择器提取匹配元素的文本（如 "h2.title"、"div.item p"）。"""
    soup = BeautifulSoup(html, "html.parser")
    return [el.get_text(strip=True) for el in soup.select(selector)]
