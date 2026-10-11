#!/usr/bin/env python3
"""AgentRender MCP server (stdio) — tools: screenshot, pdf, extract, get_free_key.

Calls the AgentRender HTTP API. Configure:

  AGENTRENDER_API_KEY    your akr_ key (free, instant, no card:
                         https://agentrenderapi.com/#waitlist)
  AGENTRENDER_BASE_URL   default https://api.agentrenderapi.com

Run (stdio):

  uvx agentrender-mcp
"""

from __future__ import annotations

import base64
import os
import re
import tempfile
import time
from pathlib import Path
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP
from mcp.types import ImageContent, TextContent

from agentrender_mcp import __version__

FREE_KEY_URL = "https://agentrenderapi.com/#waitlist"
SUPPORT_EMAIL = "hello@agentrenderapi.com"
PRICING_URL = "https://agentrenderapi.com/#pricing"
NO_KEY_MESSAGE = (
    "AGENTRENDER_API_KEY is not set. Get a free key instantly "
    f"(150 renders/month, no card): {FREE_KEY_URL} — or call the get_free_key "
    "tool with your email. Then set AGENTRENDER_API_KEY=akr_... in this MCP "
    "server's env config and restart it."
)

mcp = FastMCP(
    "agentrender",
    instructions=(
        "AgentRender tools: screenshot a URL (returns an image), print a URL to PDF "
        "(saved to a local file), and extract a page's main text/links as JSON. "
        "Requires AGENTRENDER_API_KEY. No key yet? Call get_free_key with the user's "
        f"email, or get one instantly at {FREE_KEY_URL} (free, 150 renders/month, no card)."
    ),
)

try:  # report our package version in serverInfo (best effort)
    mcp._mcp_server.version = __version__  # type: ignore[attr-defined]
except Exception:
    pass

# Key obtained via get_free_key during this session (used if env var is unset).
_session_key: str = ""


def _base_url() -> str:
    return os.getenv("AGENTRENDER_BASE_URL", "https://api.agentrenderapi.com").rstrip("/")


def _api_key() -> str:
    key = os.getenv("AGENTRENDER_API_KEY", "").strip()
    if key:
        return key
    raw = os.getenv("RENDER_API_KEYS", "").strip()
    if raw:
        return raw.split(",")[0].strip()
    return _session_key


def _headers(with_key: bool = True) -> dict[str, str]:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": f"agentrender-mcp/{__version__}",
    }
    key = _api_key() if with_key else ""
    if key:
        headers["Authorization"] = f"Bearer {key}"
    return headers


def _request(path: str, body: dict[str, Any], *, timeout: float, with_key: bool) -> dict[str, Any]:
    url = f"{_base_url()}{path}"
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, json=body, headers=_headers(with_key))
    try:
        data = resp.json()
    except Exception:
        data = {"ok": False, "error": {"code": "bad_response", "message": resp.text[:500]}}
    if resp.status_code >= 400:
        err = data.get("error") if isinstance(data, dict) else None
        msg = err.get("message") if isinstance(err, dict) else None
        if not msg and isinstance(data, dict) and isinstance(data.get("detail"), str):
            msg = data["detail"]
        msg = msg or resp.text[:300]
        code = err.get("code") if isinstance(err, dict) else None
        if resp.status_code == 401:
            if FREE_KEY_URL not in msg:
                msg = f"{msg} Get a free key instantly (150 renders/month, no card): {FREE_KEY_URL}"
        elif resp.status_code == 402 or code == "quota_exceeded":
            up = (err or {}).get("upgrade_url") or resp.headers.get("x-upgrade-url") or PRICING_URL
            if up not in msg:
                msg = f"{msg} Upgrade: {up}"
            msg += " (Tell the user: open the upgrade link to subscribe; this same API key keeps working with the new limits right after checkout.)"
        elif resp.status_code == 429:
            msg = f"{msg} Wait a minute and retry, or upgrade for higher limits: {PRICING_URL}"
        raise RuntimeError(f"HTTP {resp.status_code}: {msg}")
    quota = _quota_from_headers(resp.headers)
    if quota and isinstance(data, dict):
        data["quota"] = quota
    return data  # type: ignore[return-value]


def _quota_from_headers(h: Any) -> dict[str, Any] | None:
    """Remaining monthly renders (from X-Quota-* response headers)."""
    rem = h.get("x-quota-remaining")
    lim = h.get("x-quota-limit")
    if rem is None or lim is None:
        return None
    try:
        q: dict[str, Any] = {"plan": h.get("x-quota-plan") or "free", "remaining": int(rem), "limit": int(lim)}
    except ValueError:
        return None
    if h.get("x-upgrade-url"):
        q["upgrade_url"] = h.get("x-upgrade-url")
        q["note"] = "Running low on renders this month — upgrade to keep going."
    return q


def _post(path: str, body: dict[str, Any], *, timeout: float = 90.0) -> dict[str, Any]:
    if not _api_key():
        raise RuntimeError(NO_KEY_MESSAGE)
    return _request(path, body, timeout=timeout, with_key=True)


def _out_path(save_path: str | None, suffix: str) -> Path:
    if save_path:
        p = Path(save_path).expanduser()
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
    d = Path(tempfile.gettempdir()) / "agentrender"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"agentrender-{time.strftime('%Y%m%d-%H%M%S')}-{os.getpid()}{suffix}"


def _receipt_summary(data: dict[str, Any]) -> dict[str, Any]:
    r = data.get("receipt") if isinstance(data, dict) else None
    if not isinstance(r, dict):
        return {}
    keep = ("render_id", "url", "final_url", "captured_at", "bytes", "sha256", "format", "viewport")
    return {k: r[k] for k in keep if k in r and r[k] is not None}


@mcp.tool()
def screenshot(
    url: str,
    format: str = "jpeg",
    full_page: bool = False,
    width: int = 1280,
    height: int = 720,
    save_path: str | None = None,
) -> list[ImageContent | TextContent]:
    """Capture a public URL as an image (jpeg default; png or webp). Returns the image itself
    plus a short receipt. Optionally also saves the file to save_path."""
    body = {
        "url": url,
        "format": format,
        "full_page": full_page,
        "viewport": {"width": width, "height": height},
    }
    data = _post("/v1/screenshot", body)
    b64 = data.get("image_base64") or ""
    if not b64:
        raise RuntimeError(f"No image returned from API. Contact {SUPPORT_EMAIL}.")
    raw = base64.b64decode(b64)
    mime = data.get("content_type") or f"image/{'jpeg' if format == 'jpg' else format}"
    info = {"ok": True, "content_type": mime, "bytes": len(raw), "receipt": _receipt_summary(data)}
    if data.get("quota"):
        info["quota"] = data["quota"]
    if save_path:
        p = _out_path(save_path, "")
        p.write_bytes(raw)
        info["saved_to"] = str(p)
    return [
        ImageContent(type="image", data=b64, mimeType=mime),
        TextContent(type="text", text=_json(info)),
    ]


@mcp.tool()
def pdf(
    url: str,
    print_background: bool = True,
    landscape: bool = False,
    save_path: str | None = None,
) -> dict[str, Any]:
    """Print a public URL to PDF. Saves the PDF to a local file (save_path, or a temp
    file) and returns its path, size, and page count — not the raw bytes."""
    body = {
        "url": url,
        "print_background": print_background,
        "landscape": landscape,
    }
    data = _post("/v1/pdf", body)
    b64 = data.get("pdf_base64") or ""
    if not b64:
        raise RuntimeError(f"No PDF returned from API. Contact {SUPPORT_EMAIL}.")
    raw = base64.b64decode(b64)
    p = _out_path(save_path, ".pdf")
    p.write_bytes(raw)
    pages = len(re.findall(rb"/Type\s*/Page(?!s)", raw))
    out = {
        "ok": True,
        "saved_to": str(p),
        "bytes": len(raw),
        "pages": pages or None,
        "content_type": "application/pdf",
        "receipt": _receipt_summary(data),
    }
    if data.get("quota"):
        out["quota"] = data["quota"]
    return out


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


@mcp.tool()
def get_free_key(email: str) -> dict[str, Any]:
    """Get a free AgentRender API key instantly (150 renders/month, no card) for this
    email. The key works immediately for this session; add it to AGENTRENDER_API_KEY
    in your MCP config to keep it."""
    global _session_key
    data = _request(
        "/v1/eval-key",
        {"email": email, "use_case": "agents"},
        timeout=30.0,
        with_key=False,
    )
    key = (data.get("api_key") or "").strip() if isinstance(data, dict) else ""
    if not key:
        raise RuntimeError(f"No key returned. Get one at {FREE_KEY_URL} or email {SUPPORT_EMAIL}.")
    _session_key = key
    return {
        "ok": True,
        "api_key": key,
        "plan": data.get("plan", "free"),
        "note": (
            "Key is active for this session now. To keep it, set "
            "AGENTRENDER_API_KEY to this value in your MCP server config and restart. "
            "Store it like a password."
        ),
    }


def _json(obj: Any) -> str:
    import json

    return json.dumps(obj, default=str)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
