## Why

NanoHermes 的 Agent 目前只能通过本地工具（terminal、file、memory、session_search 等）获取信息，无法主动搜索互联网上的最新内容。为了支持实时信息查询、学术研究、新闻获取等场景，需要新增 web_search 工具，让 Agent 能够搜索互联网并获取结构化的搜索结果。

## What Changes

- 新增 `web_search` 工具模块（`src/tools/web_search_tool.py`），基于 `duckduckgo-search` 库实现
- 实现三种搜索模式：文本搜索（text）、新闻搜索（news）、即时回答（instant answer）
- 支持多语言（zh/en）、最大结果数限制、安全搜索级别
- 注册到现有工具注册表，归属于 `web` 工具集
- 实现可用性检查函数（验证 duckduckgo-search 库是否安装）
- 编写单元测试

## Capabilities

### New Capabilities

- `web-search-tool`: web 搜索工具，支持文本搜索、新闻搜索、即时回答三种模式。基于 duckduckgo-search 库，无需 API Key。返回结构化的 JSON 搜索结果，包含标题、URL、摘要、发布时间等字段。

### Modified Capabilities

- `tool-runtime`: 在 `TOOLSETS` 中新增 `web` 工具集，包含 `web_search` 工具
- `tool-runtime`: 在 `init_all_tools()` 的工具模块列表中添加 `src.tools.web_search_tool`

## Impact

- 新增 `src/tools/web_search_tool.py` 文件
- 修改 `src/tools/toolsets.py`：新增 `web` 工具集
- 修改 `src/tools/registry.py`：工具模块列表添加 web_search_tool
- 新增依赖：`duckduckgo-search`（`pyproject.toml`）
- 新增测试文件：`tests/tools/test_web_search_tool.py`
- 无破坏性变更
