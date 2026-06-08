## Context

NanoHermes 当前没有任何网络搜索能力。Agent 只能访问本地文件系统、会话历史、内存和技能。用户询问最新信息时，Agent 无法回答。

参考 Hermes Agent 的 `web` 工具集（包含 `web_search` 工具），使用 `duckduckgo-search` 库作为搜索后端，无需 API Key，适合个人/小团队使用。

## Goals / Non-Goals

**Goals:**
- Agent 能够通过 `web_search` 工具搜索互联网
- 支持文本搜索和新闻搜索两种模式
- 返回结构化 JSON 结果，与现有工具返回格式一致
- 无需 API Key 即可使用
- 支持多语言和区域设置

**Non-Goals:**
- 不实现网页内容抓取（那是 `browser` 工具集的职责）
- 不实现图片/视频搜索（后续可扩展）
- 不实现 Google/Bing 等需要 API Key 的搜索引擎
- 不实现搜索缓存（第一阶段不需要）

## Decisions

### 1. 使用 duckduckgo-search 作为搜索后端

**Decision**: 使用 `duckduckgo-search` Python 库（`DDGS` 类）。

**Why**: 
- 无需 API Key，零配置
- 支持文本搜索、新闻搜索、即时回答
- 纯 Python 实现，无需浏览器驱动
- MIT 许可证，适合开源项目

**Alternatives considered**:
- `googlesearch-python`：需要解析 Google HTML，容易被封禁
- `SerpAPI`/`Google Custom Search API`：需要 API Key 和配额
- `requests + 直接爬取搜索引擎`：维护成本高，易被封禁

### 2. 工具返回结构化 JSON

**Decision**: 所有搜索结果返回 `json.dumps()` 格式，包含 `status`、`results`、`count` 字段。

**Why**: 与现有工具（file_tool、session_search_tool 等）返回格式一致，便于对话循环统一处理。

### 3. 默认 5 条结果

**Decision**: `max_results` 默认值为 5。

**Why**: 平衡信息量和 token 消耗。LLM 通常不需要大量搜索结果来回答问题。用户可按需增加。

### 4. 区域默认 "wt-wt"（全球）

**Decision**: `region` 默认值为 "wt-wt"（worldwide）。

**Why**: 最通用的设置。用户可通过参数指定 `zh-cn` 获取中文结果。

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| DuckDuckGo 限流/封禁 | 实现错误重试和退避；返回友好错误信息而非堆栈 |
| 搜索结果质量不稳定 | 工具描述中提示用户优化 query；支持 region 参数调整 |
| 网络不可用 | 可用性检查函数检测库和网络连通性 |
| 依赖版本兼容 | 锁定 `duckduckgo-search>=6.0.0`，定期更新 |

## Open Questions

- 是否需要支持搜索结果的中文翻译？（第一阶段不需要，用户可用 LLM 自行翻译）
- 是否需要支持搜索结果的分页？（第一阶段不需要，用 max_results 控制即可）
