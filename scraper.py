"""通用网页爬虫核心模块：支持解析 HTML 和调用 JSON API 两条路径。

两条路径对应爬虫的两大场景：
- 静态网站 → 解析 HTML（fetch + parse + select）
- 有接口的网站 → 直接调 JSON API（fetch_json + extract）
"""
from __future__ import annotations

import time
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


def _request(url: str, timeout: int = 10,
             retries: int = 3, delay: float = 1.0) -> requests.Response:
    """发送 GET 请求，网络失败时自动重试。

    重试机制解决"网络抖动"（如 SSL 偶发失败），失败几次后再抛出异常。
    """
    last_err = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
            resp.raise_for_status()  # 状态码非 2xx 时抛异常
            return resp
        except requests.RequestException as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(delay)  # 稍等再试，避免频繁请求
    raise last_err


def fetch(url: str, timeout: int = 10, retries: int = 3,
          delay: float = 1.0) -> str:
    """下载网页，返回 HTML 文本；网络错误最终会抛出异常。"""
    resp = _request(url, timeout, retries, delay)
    # 有些网站不声明编码，用自动检测避免中文乱码
    if resp.encoding is None or resp.encoding.lower() == "iso-8859-1":
        resp.encoding = resp.apparent_encoding
    return resp.text


def fetch_json(url: str, timeout: int = 10, retries: int = 3,
               delay: float = 1.0):
    """请求 JSON API，返回解析后的 dict / list。"""
    resp = _request(url, timeout, retries, delay)
    return resp.json()


def extract(data, path: str):
    """按「点路径」从嵌套结构里取字段，如 "data.card.name"。

    支持 dict 的键名和 list 的数字下标。取不到时返回 None。
    例：extract({"a": {"b": [10, 20]}}, "a.b.1") -> 20
    """
    for key in path.split("."):
        if isinstance(data, dict):
            data = data.get(key)
        elif isinstance(data, list) and key.isdigit():
            idx = int(key)
            data = data[idx] if idx < len(data) else None
        else:
            return None
        if data is None:
            return None
    return data


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
