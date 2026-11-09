"""Transkript na R2. Bez secreta: ništa, red u Pozivi i dalje ide."""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
from datetime import datetime, timezone
from urllib.parse import quote

logger = logging.getLogger("lina.r2")


def _env() -> dict[str, str] | None:
    treba = (
        "R2_BUCKET",
        "R2_PUBLIC_BASE",
        "R2_ENDPOINT",
        "R2_ACCESS_KEY_ID",
        "R2_SECRET_ACCESS_KEY",
    )
    vals = {k: os.getenv(k, "").strip() for k in treba}
    if not all(vals.values()):
        return None
    host = vals["R2_ENDPOINT"].removeprefix("https://").removeprefix("http://").strip("/")
    if not host or host.startswith(".") or ".." in host or "<" in host:
        logger.error("R2_ENDPOINT nije ispravan")
        return None
    vals["host"] = host
    return vals


def _potpis(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode(), hashlib.sha256).digest()


async def stavi(key: str, tekst: str) -> str | None:
    """Vraća javni URL ili None. Ne baca — log ne smije pasti zbog uploada."""
    cfg = _env()
    if cfg is None or not tekst.strip():
        return None
    try:
        import aiohttp
    except ImportError:
        logger.error("aiohttp nije tu, preskačem upload")
        return None
    body = tekst.encode("utf-8")
    now = datetime.now(timezone.utc)
    amz_date = now.strftime("%Y%m%dT%H%M%SZ")
    datestamp = now.strftime("%Y%m%d")
    payload_hash = hashlib.sha256(body).hexdigest()
    canonical_uri = "/" + quote(cfg["R2_BUCKET"], safe="") + "/" + quote(key, safe="/")
    canonical_headers = (
        f"host:{cfg['host']}\n"
        f"x-amz-content-sha256:{payload_hash}\n"
        f"x-amz-date:{amz_date}\n"
    )
    signed = "host;x-amz-content-sha256;x-amz-date"
    canonical = "\n".join(
        ["PUT", canonical_uri, "", canonical_headers, signed, payload_hash]
    )
    scope = f"{datestamp}/auto/s3/aws4_request"
    string_to_sign = "\n".join(
        [
            "AWS4-HMAC-SHA256",
            amz_date,
            scope,
            hashlib.sha256(canonical.encode()).hexdigest(),
        ]
    )
    k = _potpis(("AWS4" + cfg["R2_SECRET_ACCESS_KEY"]).encode(), datestamp)
    k = _potpis(k, "auto")
    k = _potpis(k, "s3")
    k = _potpis(k, "aws4_request")
    signature = hmac.new(k, string_to_sign.encode(), hashlib.sha256).hexdigest()
    auth = (
        "AWS4-HMAC-SHA256 "
        f"Credential={cfg['R2_ACCESS_KEY_ID']}/{scope}, "
        f"SignedHeaders={signed}, Signature={signature}"
    )
    url = f"https://{cfg['host']}{canonical_uri}"
    headers = {
        "Authorization": auth,
        "x-amz-date": amz_date,
        "x-amz-content-sha256": payload_hash,
        "Content-Type": "text/plain; charset=utf-8",
    }
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with aiohttp.ClientSession(timeout=timeout) as s:
            async with s.put(url, data=body, headers=headers) as r:
                if r.status not in (200, 201):
                    logger.error("R2 PUT nije uspio: %s", r.status)
                    return None
    except Exception:
        logger.exception("R2 PUT fehlgeschlagen")
        return None
    base = cfg["R2_PUBLIC_BASE"].rstrip("/")
    return f"{base}/{key}"
