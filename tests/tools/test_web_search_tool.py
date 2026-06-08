"""Tests for web search tools module."""

import json
import pytest
from unittest.mock import patch, MagicMock

from src.tools.web_search_tool import web_search, check_web_search_available
from src.tools.registry import ToolRegistry


class TestWebSearch:
    """Tests for web_search tool function."""

    def test_empty_query_returns_error(self):
        """测试空搜索词返回错误。"""
        result = json.loads(web_search(query=""))
        assert result["status"] == "error"
        assert "不能为空" in result["message"]

    def test_whitespace_query_returns_error(self):
        """测试纯空白搜索词返回错误。"""
        result = json.loads(web_search(query="   "))
        assert result["status"] == "error"

    @patch("src.tools.web_search_tool.DDGS")
    def test_text_search_success(self, mock_ddgs_class):
        """测试文本搜索成功。"""
        mock_ddgs = MagicMock()
        mock_ddgs.__enter__ = MagicMock(return_value=mock_ddgs)
        mock_ddgs.__exit__ = MagicMock(return_value=False)
        mock_ddgs.text.return_value = [
            {
                "title": "Test Result 1",
                "href": "https://example.com/1",
                "body": "Description 1",
            },
            {
                "title": "Test Result 2",
                "href": "https://example.com/2",
                "body": "Description 2",
            },
        ]
        mock_ddgs_class.return_value = mock_ddgs

        result = json.loads(web_search(query="Python", max_results=2))
        assert result["status"] == "success"
        assert result["mode"] == "text"
        assert result["query"] == "Python"
        assert result["count"] == 2
        assert result["results"][0]["title"] == "Test Result 1"
        assert result["results"][0]["url"] == "https://example.com/1"

    @patch("src.tools.web_search_tool.DDGS")
    def test_news_search_success(self, mock_ddgs_class):
        """测试新闻搜索成功。"""
        mock_ddgs = MagicMock()
        mock_ddgs.__enter__ = MagicMock(return_value=mock_ddgs)
        mock_ddgs.__exit__ = MagicMock(return_value=False)
        mock_ddgs.news.return_value = [
            {
                "title": "News Title",
                "url": "https://news.example.com",
                "description": "News body",
                "source": "News Source",
                "date": "2024-01-01",
            },
        ]
        mock_ddgs_class.return_value = mock_ddgs

        result = json.loads(web_search(query="AI", backend="news"))
        assert result["status"] == "success"
        assert result["mode"] == "news"
        assert result["count"] == 1

    @patch("src.tools.web_search_tool.DDGS")
    def test_no_results_returns_empty(self, mock_ddgs_class):
        """测试无结果返回空列表。"""
        mock_ddgs = MagicMock()
        mock_ddgs.__enter__ = MagicMock(return_value=mock_ddgs)
        mock_ddgs.__exit__ = MagicMock(return_value=False)
        mock_ddgs.text.return_value = []
        mock_ddgs_class.return_value = mock_ddgs

        result = json.loads(web_search(query="nonexistent_xyz_123"))
        assert result["status"] == "success"
        assert result["count"] == 0
        assert result["results"] == []

    def test_search_error_handling(self):
        """测试搜索异常处理。"""
        with patch("src.tools.web_search_tool.DDGS") as mock_ddgs_class:
            mock_ddgs_class.side_effect = Exception("Network error")

            result = json.loads(web_search(query="test"))
            assert result["status"] == "error"
            assert "搜索失败" in result["message"]

    def test_max_results_clamped(self):
        """测试结果数被限制在合理范围内。"""
        with patch("src.tools.web_search_tool.DDGS") as mock_ddgs_class:
            mock_ddgs = MagicMock()
            mock_ddgs.__enter__ = MagicMock(return_value=mock_ddgs)
            mock_ddgs.__exit__ = MagicMock(return_value=False)
            mock_ddgs.text.return_value = []
            mock_ddgs_class.return_value = mock_ddgs

            # 负数应被钳位到 1
            web_search(query="test", max_results=-5)
            # 验证 DDGS.text 被调用时 max_results >= 1
            mock_ddgs.text.assert_called()
            call_kwargs = mock_ddgs.text.call_args
            assert call_kwargs.kwargs.get("max_results", 1) >= 1


class TestCheckWebSearchAvailable:
    """Tests for web search availability check."""

    def test_available_when_importable(self):
        """测试库可导入时返回 True。"""
        assert check_web_search_available() is True

    def test_unavailable_when_not_importable(self):
        """测试库不可导入时返回 False。"""
        import sys
        # 临时移除 duckduckgo_search
        saved = sys.modules.get("duckduckgo_search")
        sys.modules["duckduckgo_search"] = None

        try:
            result = check_web_search_available()
            assert result is False
        finally:
            if saved is not None:
                sys.modules["duckduckgo_search"] = saved
            else:
                sys.modules.pop("duckduckgo_search", None)


class TestWebSearchRegistration:
    """Tests for web search tool registration."""

    def test_tool_registered_in_registry(self):
        """测试工具已注册到 ToolRegistry。"""
        # 确保模块已加载
        from src.tools import web_search_tool
        import importlib
        importlib.reload(web_search_tool)

        entry = ToolRegistry.get_tool("web_search")
        assert entry is not None
        assert entry.name == "web_search"
        assert entry.toolset == "web"
        assert entry.check_fn is not None

    def test_tool_schema_has_required_fields(self):
        """测试工具 schema 包含必要字段。"""
        from src.tools import web_search_tool
        import importlib
        importlib.reload(web_search_tool)

        entry = ToolRegistry.get_tool("web_search")
        schema = entry.schema

        assert schema["name"] == "web_search"
        assert "description" in schema
        assert "parameters" in schema
        props = schema["parameters"]["properties"]
        assert "query" in props
        assert "query" in schema["parameters"]["required"]
        assert "max_results" in props
        assert "region" in props
        assert "backend" in props

    def test_tool_in_web_toolset(self):
        """测试 web 工具集包含 web_search。"""
        from src.tools.toolsets import TOOLSETS
        assert "web" in TOOLSETS
        assert "web_search" in TOOLSETS["web"]
