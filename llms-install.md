# AgentRender MCP — install guide for AI agents

AgentRender turns a URL into a screenshot (image), a PDF, or a structured extract (title, main text, links). Rendering happens on the hosted AgentRender API, so no local browser is needed.

## 1. Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/) (provides `uvx`). Python 3.11+ is handled by uv.

## 2. API key (free, instant, no card)

- Ask the user for their AgentRender API key (starts with `akr_`).
- If they don't have one: they can get it instantly at https://agentrenderapi.com/#waitlist (150 renders/month, no card), **or** you can start the server without a key and call the `get_free_key` tool with the user's email; it returns a key and uses it for the session.

## 3. MCP settings

Add this server entry (Cline: `cline_mcp_settings.json`; Cursor: `~/.cursor/mcp.json`; Claude Desktop: `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "agentrender": {
      "command": "uvx",
      "args": ["agentrender-mcp"],
      "env": {
        "AGENTRENDER_API_KEY": "akr_your_key"
      }
    }
  }
}
```

`AGENTRENDER_API_KEY` may be omitted if you will use `get_free_key` first.

### Alternative: hosted endpoint (no local install)

```json
{
  "mcpServers": {
    "agentrender": {
      "url": "https://api.agentrenderapi.com/mcp",
      "headers": { "Authorization": "Bearer akr_your_key" }
    }
  }
}
```

## 4. Verify

Call `extract` with `{"url": "https://example.com"}`; you should get back the page title "Example Domain". Then try `screenshot` on the same URL.

## Tools

| Tool | Purpose |
|------|---------|
| `screenshot` | Screenshot of a URL, returned as an image (optional `save_path`, `format`, `full_page`) |
| `pdf` | Render a URL to PDF, saved locally; returns the path |
| `extract` | Title, meta description, canonical, main text, links |
| `get_free_key` | Issue a free API key for an email (150 renders/month) |

Support: hello@agentrenderapi.com
