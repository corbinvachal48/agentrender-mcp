# AgentRender MCP

[![Listed on MCP Servers](https://img.shields.io/badge/MCP%20Servers-listed-0A7AEA)](https://mcpservers.org/servers/agentrenderapi-com) [![Glama](https://img.shields.io/badge/MCP-Glama-0A7CFF)](https://glama.ai/mcp/servers/corbinvachal48/agentrender-mcp)

**URL → screenshot, PDF, or structured extract for AI agents** via [MCP](https://modelcontextprotocol.io) (stdio) + REST.

- Site: https://agentrenderapi.com  
- API: https://api.agentrenderapi.com  

Tools: `screenshot` · `pdf` · `extract`

## Install

```bash
pip install agentrender-mcp
# or from this repo:
pip install .
```

Requires an AgentRender API key (`akr_…`) from https://agentrenderapi.com (free waitlist path or paid Starter $17 / Growth $79 / Scale $259).

## Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `AGENTRENDER_API_KEY` | _(required)_ | Bearer API key |
| `AGENTRENDER_BASE_URL` | `https://api.agentrenderapi.com` | API base |

## Run (stdio)

```bash
export AGENTRENDER_API_KEY=akr_your_key
agentrender-mcp
# or: python -m agentrender_mcp.server
```

## Cursor / Claude Desktop

```json
{
  "mcpServers": {
    "agentrender": {
      "command": "agentrender-mcp",
      "env": {
        "AGENTRENDER_API_KEY": "akr_your_key",
        "AGENTRENDER_BASE_URL": "https://api.agentrenderapi.com"
      }
    }
  }
}
```

If `agentrender-mcp` is not on `PATH`, use your Python:

```json
{
  "mcpServers": {
    "agentrender": {
      "command": "python",
      "args": ["-m", "agentrender_mcp.server"],
      "env": {
        "AGENTRENDER_API_KEY": "akr_your_key"
      }
    }
  }
}
```

## Tools

| Tool | Maps to | Notes |
|------|---------|--------|
| `screenshot` | `POST /v1/screenshot` | PNG/JPEG/WebP; returns `image_base64` + receipt |
| `pdf` | `POST /v1/pdf` | Returns `pdf_base64` + receipt |
| `extract` | `POST /v1/extract` | Title, meta, canonical, text, links (non-LLM) |

## REST smoke

```bash
curl -s https://api.agentrenderapi.com/health
curl -s -X POST https://api.agentrenderapi.com/v1/extract \
  -H "Authorization: Bearer $AGENTRENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

## Notes

- Hosted Streamable HTTP MCP is not shipped in this package yet; use stdio as above.
- Do not commit API keys. Rotate any key that leaks.
- Support: hello@agentrenderapi.com

## License

MIT

<!-- mcp-name: io.github.corbinvachal48/agentrender-mcp -->
