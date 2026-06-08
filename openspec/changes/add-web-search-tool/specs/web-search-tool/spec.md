# Web Search Tool

Web search tool capability: the Agent can search the internet using DuckDuckGo and receive structured JSON results.

## Requirements

### REQ-1: Text Search

The system SHALL support text search via DuckDuckGo.

- Call `DDGS.text(query, max_results, region, safesearch, timelimit)` to retrieve results
- Each result SHALL include: `title`, `url`, `description`, `body` (if available)

### REQ-2: News Search

The system SHALL support news search via DuckDuckGo.

- Call `DDGS.news(query, max_results, region, safesearch, timelimit)` to retrieve results
- Each result SHALL include: `title`, `url`, `description`, `source`, `date` (publication date)

### REQ-3: Structured JSON Response

The system SHALL return results as a JSON string with the following structure:

```json
{
  "status": "success",
  "mode": "text|news",
  "query": "the search query",
  "results": [
    {
      "title": "result title",
      "url": "https://...",
      "description": "snippet",
      "source": "source name (news only)",
      "date": "publication date (news only)"
    }
  ],
  "count": 3
}
```

### REQ-4: Error Handling

The system SHALL handle errors gracefully:

- Network errors: return `{"status": "error", "message": "..."}`  JSON string
- Rate limiting: return error with retry suggestion
- No results: return `{"status": "success", "results": [], "count": 0}`
- Missing query: return error indicating query is required

### REQ-5: Tool Registration

The tool SHALL be registered via `register_tool()` with:

- name: `"web_search"`
- toolset: `"web"`
- handler: `web_search` function
- check_fn: `check_web_search_available` function
- schema: OpenAI-compatible tool schema with all parameters documented

### REQ-6: Availability Check

The system SHALL provide an availability check function that:

- Verifies `duckduckgo_search` package is installed
- Returns `True` if available, `False` otherwise

### REQ-7: Parameter Validation

The tool SHALL validate parameters:

- `query`: required, non-empty string
- `max_results`: integer, 1-50, default 5
- `region`: valid DuckDuckGo region code (e.g., "zh-cn", "en-us", "wt-wt")
- `safesearch`: one of "on", "moderate", "off", default "moderate"
- `timelimit`: one of "d", "w", "m", "y", or empty
- `backend`: one of "text", "news", default "text"

### REQ-8: Toolset Integration

The `web` toolset SHALL be added to `TOOLSETS` in `toolsets.py`:

```python
"web": ["web_search"]
```
