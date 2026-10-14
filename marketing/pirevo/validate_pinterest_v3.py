#!/usr/bin/env python3
"""Fail-closed PIREVO Pinterest full-bleed V3 approval gate.

An image may be uploaded only after this validator returns exit 0 with
--require-ready. This program does NOT publish Pins or approve creative automatically.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT / "marketing/pirevo/approved_pins_v3.json"
BANNED_RENDERERS = (
    "marketing/pirevo/render_pinterest_wave1.py",
    "marketing/pirevo/render_pinterest_wave2.py",
    "marketing/pirevo/render_pinterest_halloween_wave3.py",
    "marketing/pirevo/render_pinterest_christmas_wave4.py",
    "marketing/pirevo/buffer_pinterest_pirevo.py",
)
BANNED_ASSET_PARTS = {"wave1", "wave2", "wave3-halloween", "wave4-christmas"}
ALLOWED_SOURCE_RIGHTS = {"original_generated", "owned_photography", "licensed_for_marketing"}
APPROVED_PREFIX = "public/pirevo/assets/pins/v3/"
REQUIRED_TRUE = (
    "full_bleed_approved", "no_card_layout", "thumbnail_readable",
    "product_variant_verified", "affiliate_tag_verified", "landing_verified",
    "title_verified", "ai_disclosure_checked",
)

class Rejected(ValueError):
    pass

def require(ok, message):
    if not ok:
        raise Rejected(message)

def get_store(root: Path):
    raw = (root / "public/pirevo/store-data.js").read_text(encoding="utf-8").strip()
    require(raw.startswith("window.PIREVO_STORE"), "missing current PIREVO catalog")
    return json.loads(raw.split("=", 1)[1].rstrip(";").strip())

def check_banned_renderers(root: Path):
    for rel in BANNED_RENDERERS:
        content = (root / rel).read_text(encoding="utf-8")
        require("PIREVO_LEGACY_TEMPLATE_DISABLED_V3" in content,
                f"LEGACY RENDERER ENABLED: {rel}")

def thumbnail_photo_coverage(im):
    """Conservative uniform-panel detector; cannot replace human design QA."""
    from PIL import ImageStat
    image = im.convert("RGB")
    w, h = image.size
    zones = [
        (0.05, 0.56, 0.35, 0.74),
        (0.39, 0.56, 0.65, 0.74),
        (0.69, 0.56, 0.95, 0.74),
        (0.05, 0.75, 0.35, 0.93),
        (0.39, 0.75, 0.65, 0.93),
        (0.69, 0.75, 0.95, 0.93),
    ]
    scores = []
    for x0, y0, x1, y1 in zones:
        tile = image.crop((int(w*x0), int(h*y0), int(w*x1), int(h*y1))).resize((96, 96))
        scores.append(sum(ImageStat.Stat(tile).stddev)/3.0)
    require(sum(x > 15 for x in scores) >= 4,
            f"Too much flat space / boxed template detected: zone stddev {scores!r}")
    return scores

def dhash(im):
    from PIL import Image
    sm = im.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
    px = list(sm.getdata())
    return sum((1 << (r*8 + c)) for r in range(8) for c in range(8)
               if px[r*9+c] > px[r*9+c+1])

def check_one(entry, store, root):
    from PIL import Image
    require(isinstance(entry, dict), "approval item is not an object")
    pid = str(entry.get("pin_id", "")).strip()
    require(re.fullmatch(r"[a-z0-9][a-z0-9_-]{7,80}", pid),
            f"missing or unsafe unique pin ID: {pid!r}")
    rel = str(entry.get("image_path", ""))
    require(rel.startswith(APPROVED_PREFIX), f"{pid}: not in approved V3 source location")
    require(not set(Path(rel).parts).intersection(BANNED_ASSET_PARTS), f"{pid}: legacy asset reused")
    file = (root / rel).resolve()
    require(file.is_relative_to(root.resolve()) and file.is_file(), f"{pid}: missing V3 file")
    require(file.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}, f"{pid}: unsupported image format")
    sha = hashlib.sha256(file.read_bytes()).hexdigest()
    require(sha == entry.get("image_sha256"), f"{pid}: image changed after approval; re-review needed")
    require(entry.get("source_rights") in ALLOWED_SOURCE_RIGHTS, f"{pid}: missing media rights")
    for key in REQUIRED_TRUE:
        require(entry.get(key) is True, f"{pid}: '{key}' not explicitly approved")
    reviewer = str(entry.get("reviewer", "")).strip()
    require(len(reviewer)>=3 and reviewer.lower() not in {"bot", "auto", "none", "pending"},
            f"{pid}: human visual QA reviewer missing")
    ts = str(entry.get("reviewed_at_utc", "")).replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(ts)
    except ValueError:
        raise Rejected(f"{pid}: invalid review timestamp") from None
    require(parsed.tzinfo is not None and parsed <= datetime.now(timezone.utc),
            f"{pid}: review timestamp not evidence-based")
    with Image.open(file) as image:
        image.load()
        w, h = image.size
        require(w >= 1000 and h >= 1500 and abs(w/h - 2/3)<0.01,
                f"{pid}: image must be at least 1000x1500, 2:3, got {w}x{h}")
        require(image.mode in {"RGB", "RGBA", "P"}, f"{pid}: unexpected color mode")
        scores = thumbnail_photo_coverage(image)
        visualhash = dhash(image)
    products = {p["slug"]:p for p in store["products"]}
    slug = entry.get("product_slug")
    require(slug in products, f"{pid}: product not in current PIREVO catalog")
    product = products[slug]
    asin = entry.get("asin")
    require(asin == product["asin"], f"{pid}: product variant/ASIN mismatch")
    url = urlparse(str(entry.get("destination", "")))
    require(url.scheme=="https" and url.netloc=="www.astralabsph.com",
            f"{pid}: pin destination must be first-party HTTPS")
    require(url.path == f"/pirevo/products/{slug}/index.html" or
            url.path == f"/pirevo/products/{slug}/",
            f"{pid}: destination product slug mismatch")
    qs = parse_qs(url.query)
    require(qs.get("utm_source")==["pinterest"] and
            qs.get("utm_medium", [None])[0] in {"organic", "organic_social"} and
            qs.get("utm_content")==[pid], f"{pid}: missing unique Pinterest UTM")
    amazon = urlparse(product.get("amazon", ""))
    aq = parse_qs(amazon.query)
    require(amazon.netloc in {"www.amazon.com", "amazon.com"} and
            re.search(r"/dp/"+re.escape(asin)+r"(?:$|/)", amazon.path) and
            aq.get("tag")==["pirevo-20"], f"{pid}: affiliate link not exact ASIN + tag")
    title = str(entry.get("title", "")).strip()
    require(2<=len(title.split())<=12 and len(title)<=100, f"{pid}: title too long/short")
    desc = str(entry.get("description", ""))
    require("affiliate" in desc.casefold() or "qualifying purchases" in desc.casefold(),
            f"{pid}: required affiliate disclosure absent")
    require(entry.get("board") and len(entry["board"])>=5, f"{pid}: relevant board not selected")
    require(entry.get("status") in {"APPROVED_FOR_PUBLISH", "PUBLISHED"},
            f"{pid}: no published/approved status allowed")
    return {"pin_id":pid, "sha256":sha, "dhash":visualhash, "photo_scores":scores}

def validate(root=ROOT, manifest=DEFAULT, require_ready=False):
    check_banned_renderers(root)
    data = json.loads(manifest.read_text(encoding="utf-8"))
    require(data.get("standard")=="PIREVO_FULLBLEED_V3",
            "Wrong/missing V3 approval manifest standard")
    entries=data.get("pins")
    require(isinstance(entries, list), "V3 manifest must contain an approvals array")
    if require_ready:
        require(entries, "FAIL CLOSED: no individually approved full-bleed Pins exist yet")
    store=get_store(root)
    seen_ids=set(); seen_hashes=set(); visual=[]
    for entry in entries:
        result=check_one(entry,store,root)
        pid=result["pin_id"]
        require(pid not in seen_ids, f"Duplicate pin id {pid}")
        require(result["sha256"] not in seen_hashes, f"{pid}: exact duplicate image")
        for prev in visual:
            dist=(result["dhash"]^prev["dhash"]).bit_count()
            require(dist>=8, f"{pid}: suspiciously similar creative to {prev['pin_id']} ({dist}/64)")
        seen_ids.add(pid); seen_hashes.add(result["sha256"]); visual.append(result)
        print(f"PIREVO_V3_PASS {pid} photo_zones={list(map(lambda x: round(x,1),result['photo_scores']))}")
    print(f"PIREVO_V3_POLICY_OK approved={len(visual)} publish_allowed={bool(visual)}")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",type=Path,default=DEFAULT)
    ap.add_argument("--root",type=Path,default=ROOT)
    ap.add_argument("--require-ready",action="store_true")
    args=ap.parse_args()
    try: validate(args.root, args.manifest, args.require_ready)
    except (Rejected,FileNotFoundError,KeyError,ImportError) as e:
        print(f"PIREVO_V3_RELEASE_BLOCKED: {e}")
        return 1
    return 0

if __name__=="__main__":
    raise SystemExit(main())
