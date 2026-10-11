# AgentRender MCP

<p align="center">
  <img src="https://raw.githubusercontent.com/corbinvachal48/agentrender-mcp/main/assets/logo.png" alt="AgentRender" width="160" height="160" />
</p>

[![Listed on MCP Servers](https://img.shields.io/badge/MCP%20Servers-listed-0A7AEA)](https://mcpservers.org/servers/agentrenderapi-com) [![Glama](https://img.shields.io/badge/MCP-Glama-0A7CFF)](https://glama.ai/mcp/servers/corbinvachal48/agentrender-mcp)

**URL → screenshot, PDF, or structured extract for AI agents** via [MCP](https://modelcontextprotocol.io).

> **Get a free API key instantly — 150 renders/month, no card:** https://agentrenderapi.com/#waitlist
> (or just ask your agent to call the `get_free_key` tool with your email)
>
> **Pricing:** Free — 150 renders/month with the free key (no card). Need more? Starter $17/month (2,000 renders/month): https://agentrenderapi.com/#pricing

Tools: `screenshot` (returns the image) · `pdf` (saves a file, returns its path) · `extract` (title, text, links as JSON) · `get_free_key`

## Quick start

1. Get a free key: https://agentrenderapi.com/#waitlist (instant, no card).
2. Add the server to your client (below) with `uvx agentrender-mcp`. Needs [uv](https://docs.astral.sh/uv/getting-started/installation/).
3. Ask your agent: *"Take a screenshot of https://example.com"*.

### Claude Code

```bash
claude mcp add agentrender -e AGENTRENDER_API_KEY=akr_your_key -- uvx agentrender-mcp
```

### Cursor (`~/.cursor/mcp.json`) / Claude Desktop (`claude_desktop_config.json`)

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

### Hosted MCP (no install)

Remote Streamable HTTP endpoint: `https://api.agentrenderapi.com/mcp` with header `Authorization: Bearer akr_your_key`.

```bash
claude mcp add --transport http agentrender https://api.agentrenderapi.com/mcp \
  --header "Authorization: Bearer akr_your_key"
```

Cursor:

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

### pip instead of uvx

```bash
pip install agentrender-mcp
export AGENTRENDER_API_KEY=akr_your_key
agentrender-mcp          # or: python -m agentrender_mcp.server
```

## Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `AGENTRENDER_API_KEY` | _(required)_ | Your `akr_` key — [free, instant](https://agentrenderapi.com/#waitlist) |
| `AGENTRENDER_BASE_URL` | `https://api.agentrenderapi.com` | API base |

## Tools

| Tool | Maps to | Returns |
|------|---------|---------|
| `screenshot` | `POST /v1/screenshot` | MCP image block (JPEG by default; `format` = png/webp) + short receipt. Optional `save_path`. |
| `pdf` | `POST /v1/pdf` | Saves the PDF locally (`save_path` or temp dir); returns path, bytes, page count. |
| `extract` | `POST /v1/extract` | Title, meta description, canonical, main text, links (non-LLM). |
| `get_free_key` | `POST /v1/eval-key` | Issues a free key (150/mo) for your email and uses it for the session. |

## Plans

Free: 150 renders/month with the free key, no card. Then Starter $17/month (2,000 renders) · Growth $79 · Scale $259 — https://agentrenderapi.com/#pricing

Every result includes a `quota` block (renders left this month). When the free 150 run out, tools return a clear `quota_exceeded` error with an `upgrade_url` — a Stripe checkout link tied to your key. Subscribe there and **the same key is upgraded within seconds**; just retry. Starting fresh from the website instead? Your new key is shown on the checkout confirmation page and emailed instantly.

## REST

```bash
curl -s https://api.agentrenderapi.com/health
curl -s -X POST https://api.agentrenderapi.com/v1/extract \
  -H "Authorization: Bearer $AGENTRENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

## Notes

- Do not commit API keys. Rotate any key that leaks.
- Support: hello@agentrenderapi.com

## License

MIT

<!-- mcp-name: io.github.corbinvachal48/agentrender-mcp -->
