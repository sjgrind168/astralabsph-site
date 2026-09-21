#!/usr/bin/env python3
"""Verify live Pinterest PNG image URLs from GitHub Actions; no post writes."""
import urllib.request
import urllib.error
from pathlib import Path

ROOT = "https://www.astralabsph.com/marketing/pins/"
files = ("astramate_eta.png", "keepry_vault.png")
for file in files:
    url = ROOT + file
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "AstraLabs-Marketing-Asset-QA/1.0"})
        with urllib.request.urlopen(request, timeout=20) as response:
            content_type = response.headers.get("Content-Type", "")
            prefix = response.read(8)
            if response.status != 200 or not content_type.lower().startswith("image/png") or prefix != b"\x89PNG\r\n\x1a\n":
                raise RuntimeError("Not a publicly served PNG")
            print("PUBLIC_PNG_OK", file, response.status, content_type)
    except Exception as exc:
        print("PUBLIC_PNG_FAILED", file, type(exc).__name__, str(exc)[:110])
        raise
