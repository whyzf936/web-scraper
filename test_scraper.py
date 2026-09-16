"""单元测试：验证 HTML 解析逻辑（不发起真实网络请求）。

运行方式：
    python -m unittest test_scraper -v
"""
from __future__ import annotations

import unittest

from scraper import parse, select, extract

# 一段示例 HTML，用于测试解析逻辑
SAMPLE_HTML = """
<html>
<head>
    <title>测试页面</title>
    <meta name="description" content="这是一个测试页面">
</head>
<body>
    <h1>欢迎</h1>
    <p>这是正文内容。</p>
    <a href="/page1">链接一</a>
    <a href="https://example.com/page2">链接二</a>
    <img src="/img/logo.png" alt="logo">
    <img src="https://example.com/pic.jpg" alt="图片">
    <script>console.log('这段应被忽略')</script>
</body>
</html>
"""


class TestParse(unittest.TestCase):
    """测试 parse 函数。"""

    def test_title(self):
        data = parse(SAMPLE_HTML)
        self.assertEqual(data["title"], "测试页面")

    def test_description(self):
        data = parse(SAMPLE_HTML)
        self.assertEqual(data["description"], "这是一个测试页面")

    def test_links(self):
        data = parse(SAMPLE_HTML)
        self.assertEqual(len(data["links"]), 2)
        self.assertEqual(data["links"][0]["text"], "链接一")

    def test_links_resolve_relative(self):
        """相对链接应被转成绝对地址。"""
        data = parse(SAMPLE_HTML, base_url="https://example.com")
        self.assertEqual(data["links"][0]["href"], "https://example.com/page1")

    def test_images(self):
        data = parse(SAMPLE_HTML)
        self.assertEqual(len(data["images"]), 2)
        self.assertEqual(data["images"][0]["alt"], "logo")

    def test_script_ignored_in_text(self):
        """脚本内容不应出现在正文里。"""
        data = parse(SAMPLE_HTML)
        self.assertNotIn("console.log", data["text"])
        self.assertIn("这是正文内容", data["text"])

    def test_empty_title(self):
        """没有标题时返回空字符串。"""
        data = parse("<html><body><p>无标题</p></body></html>")
        self.assertEqual(data["title"], "")


class TestSelect(unittest.TestCase):
    """测试 CSS 选择器提取。"""

    def test_select_h1(self):
        results = select(SAMPLE_HTML, "h1")
        self.assertEqual(results, ["欢迎"])

    def test_select_links(self):
        results = select(SAMPLE_HTML, "a")
        self.assertEqual(len(results), 2)

    def test_select_no_match(self):
        results = select(SAMPLE_HTML, ".not-exist")
        self.assertEqual(results, [])


class TestExtract(unittest.TestCase):
    """测试点路径提取字段。"""

    def test_simple_key(self):
        data = {"name": "Alice", "age": 20}
        self.assertEqual(extract(data, "name"), "Alice")
        self.assertEqual(extract(data, "age"), 20)

    def test_nested_dict(self):
        data = {"data": {"card": {"name": "Bob"}}}
        self.assertEqual(extract(data, "data.card.name"), "Bob")

    def test_list_index(self):
        data = {"items": [{"title": "a"}, {"title": "b"}]}
        self.assertEqual(extract(data, "items.1.title"), "b")

    def test_missing_returns_none(self):
        data = {"a": 1}
        self.assertIsNone(extract(data, "a.b.c"))


if __name__ == "__main__":
    unittest.main()
