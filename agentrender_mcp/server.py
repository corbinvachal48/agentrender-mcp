#!/usr/bin/env python3
"""AgentRender MCP server (stdio) — tools: screenshot, pdf, extract.

Calls the AgentRender HTTP API. Configure:

  AGENTRENDER_BASE_URL   default https://api.agentrenderapi.com
  AGENTRENDER_API_KEY    Bearer token (required for production)

Run (stdio):

  export AGENTRENDER_API_KEY=akr_…
  python -m agentrender_mcp.server
"""

from __future__ import annotations

import base64
import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "agentrender",
    instructions=(
        "AgentRender tools: capture URL screenshots/PDFs and extract main content. "
        "Set AGENTRENDER_API_KEY and optionally AGENTRENDER_BASE_URL "
        "(default https://api.agentrenderapi.com)."
    ),
)


def _base_url() -> str:
    return os.getenv("AGENTRENDER_BASE_URL", "https://api.agentrenderapi.com").rstrip("/")


def _api_key() -> str:
    key = os.getenv("AGENTRENDER_API_KEY", "").strip()
    if key:
        return key
    raw = os.getenv("RENDER_API_KEYS", "").strip()
    if raw:
        return raw.split(",")[0].strip()
    return ""


def _headers() -> dict[str, str]:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    key = _api_key()
    if key:
        headers["Authorization"] = f"Bearer {key}"
    return headers


def _post(path: str, body: dict[str, Any], *, timeout: float = 90.0) -> dict[str, Any]:
    if not _api_key():
        raise RuntimeError(
            "AGENTRENDER_API_KEY is not set. Get a key via https://agentrenderapi.com "
            "or your waitlist welcome email."
        )
    url = f"{_base_url()}{path}"
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, json=body, headers=_headers())
        try:
            data = resp.json()
        except Exception:
            data = {"ok": False, "error": {"code": "bad_response", "message": resp.text[:500]}}
        if resp.status_code >= 400:
            err = data.get("error") if isinstance(data, dict) else None
            msg = err.get("message") if isinstance(err, dict) else resp.text[:300]
            raise RuntimeError(f"HTTP {resp.status_code}: {msg}")
        return data  # type: ignore[return-value]


@mcp.tool()
def screenshot(
    url: str,
    format: str = "png",
    full_page: bool = False,
    width: int = 1280,
    height: int = 720,
) -> dict[str, Any]:
    """Capture a public URL as an image (PNG/JPEG/WebP). Returns JSON with image_base64 + receipt."""
    body = {
        "url": url,
        "format": format,
        "full_page": full_page,
        "viewport": {"width": width, "height": height},
    }
    data = _post("/v1/screenshot", body)
    if isinstance(data, dict) and data.get("image_base64"):
        b64 = data["image_base64"]
        data = {
            **data,
            "image_base64": b64,
            "image_bytes_approx": len(base64.b64decode(b64)) if b64 else 0,
        }
    return data


@mcp.tool()
def pdf(url: str, print_background: bool = True, landscape: bool = False) -> dict[str, Any]:
    """Capture a public URL as a PDF. Returns JSON with pdf_base64 + receipt."""
    body = {
        "url": url,
        "print_background": print_background,
        "landscape": landscape,
    }
    data = _post("/v1/pdf", body)
    if isinstance(data, dict) and data.get("pdf_base64"):
        b64 = data["pdf_base64"]
        data = {
            **data,
            "pdf_base64": b64,
            "pdf_bytes_approx": len(base64.b64decode(b64)) if b64 else 0,
        }
    return data


@mcp.tool()
def extract(
    url: str,
    include_links: bool = True,
    max_text_chars: int = 20000,
) -> dict[str, Any]:
    """Extract title, meta description, canonical, main text, and links from a URL (non-LLM)."""
    body = {
        "url": url,
        "include_links": include_links,
        "max_text_chars": max_text_chars,
    }
    return _post("/v1/extract", body)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
