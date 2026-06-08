"""Web 搜索工具：基于 DuckDuckGo 的网页搜索。

通过 duckduckgo_search 库实现无需 API Key 的网络搜索。
支持两种后端：
- text: 普通网页搜索（默认）
- news: 新闻搜索

设计理由：
- 使用 DuckDuckGo 而非 Google/Bing：无需注册 API Key，零配置即可使用
- 返回 JSON 格式结果：与项目其他工具保持一致的输出格式
- 独立的可用性检查：验证库是否正常安装且网络可达
"""

from __future__ import annotations

import json
import logging
from typing import Any

from duckduckgo_search import DDGS
from src.tools.registry import register_tool

logger = logging.getLogger(__name__)

# 搜索结果上限，防止滥用和超时
MAX_RESULTS_LIMIT = 50


def web_search(
    query: str = "",
    max_results: int = 5,
    region: str = "wt-wt",
    safesearch: str = "moderate",
    timelimit: str = "",
    backend: str = "text",
    task_id: str = None,
    **kwargs,
) -> str:
    """执行网络搜索。

    设计理由：
    - 参数与 duckduckgo_search DDGS API 保持一致，降低学习成本
    - 返回值统一为 JSON 字符串，便于下游解析
    - 所有异常统一捕获，返回错误 JSON 而非抛异常

    Args:
        query: 搜索关键词。
        max_results: 返回结果数量（1-50）。
        region: 地区代码，默认 "wt-wt"（全球）。
        safesearch: 安全搜索级别（on/moderate/off）。
        timelimit: 时间过滤（d=天, w=周, m=月, y=年）。
        backend: 搜索模式（text/news）。
        task_id: 任务 ID。

    Returns:
        JSON 字符串，包含搜索结果或错误信息。
    """
    # 参数校验：搜索词不能为空
    if not query or not query.strip():
        return json.dumps({
            "status": "error",
            "message": "搜索词不能为空"
        }, ensure_ascii=False)

    # 限制最大结果数
    max_results = min(max(max_results, 1), MAX_RESULTS_LIMIT)

    try:
        with DDGS() as ddgs:
            # 根据 backend 选择搜索方法
            # text: DDGS.text() 返回网页搜索结果
            # news: DDGS.news() 返回新闻搜索结果
            if backend == "news":
                results = list(ddgs.news(
                    keywords=query,
                    max_results=max_results,
                    region=region,
                    safesearch=safesearch,
                    timelimit=timelimit if timelimit else None,
                ))
                mode = "news"
            else:
                results = list(ddgs.text(
                    keywords=query,
                    max_results=max_results,
                    region=region,
                    safesearch=safesearch,
                    timelimit=timelimit if timelimit else None,
                ))
                mode = "text"

        # 统一结果格式：提取 title, url, description
        formatted_results = []
        for r in results:
            formatted_results.append({
                "title": r.get("title", ""),
                "url": r.get("href") or r.get("url", ""),
                "description": r.get("body") or r.get("description", ""),
            })

        return json.dumps({
            "status": "success",
            "mode": mode,
            "query": query,
            "results": formatted_results,
            "count": len(formatted_results),
        }, ensure_ascii=False)

    except ImportError:
        return json.dumps({
            "status": "error",
            "message": "duckduckgo-search 库未安装，请运行: pip install duckduckgo-search"
        }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Web 搜索失败: {e}", exc_info=True)
        return json.dumps({
            "status": "error",
            "message": f"搜索失败: {str(e)}"
        }, ensure_ascii=False)


def check_web_search_available() -> bool:
    """检查 web_search 工具是否可用。

    验证 duckduckgo_search 库是否正确安装。
    不检查网络连通性，因为可用性检查应尽可能快速。
    """
    try:
        from duckduckgo_search import DDGS
        return True
    except ImportError:
        return False
    except Exception:
        return False


register_tool(
    name="web_search",
    toolset="web",
    schema={
        "name": "web_search",
        "description": (
            "Search the web using DuckDuckGo. No API key required.\n\n"
            "Use this tool when you need current information from the internet, "
            "such as news, recent events, product information, or answers to questions "
            "that require up-to-date knowledge.\n\n"
            "Parameters:\n"
            "- query (required): Search keywords\n"
            "- max_results: Number of results (1-50, default 5)\n"
            "- region: Region code (default 'wt-wt' for worldwide)\n"
            "- safesearch: 'on', 'moderate', or 'off' (default 'moderate')\n"
            "- timelimit: 'd' (day), 'w' (week), 'm' (month), 'y' (year)\n"
            "- backend: 'text' for web search, 'news' for news search (default 'text')"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (required)."
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (1-50, default 5).",
                    "default": 5,
                },
                "region": {
                    "type": "string",
                    "description": "Region code (default 'wt-wt' for worldwide).",
                    "default": "wt-wt",
                },
                "safesearch": {
                    "type": "string",
                    "description": "Safe search level: 'on', 'moderate', or 'off'.",
                    "default": "moderate",
                },
                "timelimit": {
                    "type": "string",
                    "description": "Time limit: 'd' (day), 'w' (week), 'm' (month), 'y' (year).",
                    "default": "",
                },
                "backend": {
                    "type": "string",
                    "description": "Search mode: 'text' for web search, 'news' for news search.",
                    "default": "text",
                },
            },
            "required": ["query"],
        },
    },
    handler=web_search,
    check_fn=check_web_search_available,
    description="网络搜索工具",
)
