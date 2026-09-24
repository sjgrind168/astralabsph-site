#!/usr/bin/env python3
"""Owner-authorized, one-time, six-original-Pin pilot in the EXISTING Pinterest writer.
No new account, no PIREVO writes, no paid service, no duplicate/retry catch-up.
This intentionally uses first-party screenshot-based PNGs, not generated fake-app mockups.
"""
import argparse
import importlib.util
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "shared" / "ASTRALABS_ONE_TIME_HOURLY_PIN_20260924.json"
PHT = ZoneInfo("Asia/Manila")
HOME = "https://www.astralabsph.com/"
MAX_QUEUE = 10
EXPECTED_BOARD = "AstraLabs Apps | Astramate & Keepry"
EXPECTED_BOARD_ID = "1143844074049569906"
EXPECTED_CHANNEL = "6aa06411cd8b9c702c2ff8ff"

def load():
    obj = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = obj.get("posts")
    if (obj.get("max_posts") != 6 or obj.get("official_website") != HOME or
        obj.get("timezone") != "Asia/Manila" or obj.get("board") != EXPECTED_BOARD or
        obj.get("board_service_id") != EXPECTED_BOARD_ID or
        obj.get("channel_id") != EXPECTED_CHANNEL or
        not isinstance(rows, list) or len(rows) != 6 or
        len({x["id"] for x in rows}) != 6 or
        len({x["image_url"] for x in rows}) != 6):
        raise RuntimeError("Campaign inventory, destination, or board unexpectedly changed")
    start = datetime.fromisoformat(rows[0]["due_pht"])
    for idx, row in enumerate(rows):
        due = datetime.fromisoformat(row["due_pht"])
        if (due.utcoffset() != timedelta(hours=8) or due != start + timedelta(hours=idx) or
            row["app"] != ("Astramate" if idx % 2 == 0 else "Keepry") or
            not row["image_url"].startswith(HOME + "marketing/campaigns/seven_day/day1/") or
            not row["image_url"].endswith(".png") or not row["caption"].count(HOME) >= 2 or
            "utm_content=" + row["id"].lower() not in row["caption"] or
            row["url"] not in row["caption"] or
            len(row["caption"]) > 500 or
            not 10 <= len(row["title"]) <= 100):
            raise RuntimeError("A scheduled post fails unique-asset, hour, app, site, or copy checks")
    return rows

def target():
    path = Path(__file__).with_name("buffer_pinterest.py")
    spec = importlib.util.spec_from_file_location("astralabs_existing_pin_client", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    org, board = mod.target()
    if board != EXPECTED_BOARD_ID or mod.CHANNEL_ID != EXPECTED_CHANNEL:
        raise RuntimeError("Exact authorized AstraLabs Apps board ID did not match; PIREVO protected")
    return mod, org

def history(mod, org):
    doc = ("query { posts(first:100,input:{organizationId:" + mod.quoted(org) +
           ",filter:{status:[scheduled,sent,draft,error,sending],channelIds:[" +
           mod.quoted(EXPECTED_CHANNEL) +
           "]},sort:[{field:createdAt,direction:desc}]}) { edges { node { id text status channelId dueAt externalLink assets { mimeType source } } } pageInfo { hasNextPage } } }")
    obj = mod.query(doc).get("posts")
    if not isinstance(obj, dict) or not isinstance(obj.get("edges"), list) or (obj.get("pageInfo") or {}).get("hasNextPage"):
        raise RuntimeError("Incomplete Pinterest history; no posting")
    rows = [x["node"] for x in obj["edges"] if isinstance(x.get("node"), dict)]
    if any(x.get("channelId") != EXPECTED_CHANNEL for x in rows):
        raise RuntimeError("Cross-channel result; no posting")
    return rows

def verify_png(url):
    req = urllib.request.Request(url, headers={"User-Agent":"AstraLabs-Original-Pin-ReadOnly/1.0",
                                                "Range":"bytes=0-31"})
    with urllib.request.urlopen(req, timeout=20) as response:
        if response.status not in (200, 206) or not response.headers.get("Content-Type","").lower().startswith("image/png") or response.read(8) != b"\x89PNG\r\n\x1a\n":
            raise RuntimeError("First-party original Pin PNG is not publicly available")

def planned_due(row):
    return datetime.fromisoformat(row["due_pht"]).astimezone(PHT)

def find_original(rows, cid):
    hits = [p for p in rows if "utm_content=" + cid.lower() in str(p.get("text") or "").lower()]
    if len(hits) > 1:
        raise RuntimeError("Multiple existing copies of a unique campaign; stop and reconcile")
    return hits[0] if hits else None

def attempt(mod, org, plan, now, dry_run):
    rows = history(mod, org)
    scheduled = [p for p in rows if p.get("status") in ("scheduled","sending")]
    if len(scheduled) >= MAX_QUEUE:
        print("PINTEREST_FREE_QUEUE_FULL; preserved; no writes", flush=True)
        return
    for idx, item in enumerate(plan):
        due = planned_due(item)
        existing = find_original(rows, item["id"])
        if existing:
            if existing.get("status") == "sent":
                if not existing.get("externalLink"):
                    print("HOLD_SENT_WITHOUT_NATIVE_LINK", item["id"], "Buffer", existing["id"], flush=True)
                    return
                print("PIN_SENT_CONFIRMED", item["id"], "Buffer", existing["id"],
                      "native", existing["externalLink"], flush=True)
                continue
            print("PRESERVE_EXISTING_PIN", item["id"], existing["status"],
                  "Buffer", existing["id"], "dueAt", existing.get("dueAt"), flush=True)
            return
        # Never move to a later post if the preceding one is absent or unverified.
        if idx and not find_original(rows, plan[idx-1]["id"]):
            print("HOLD_PREVIOUS_HOURLY_PIN_NOT_CREATED", flush=True)
            return
        if due <= now + timedelta(minutes=15):
            print("EXPIRED_OR_TOO_NEAR_HOURLY_SLOT", item["id"], due.isoformat(),
                  "NO_LATE_CATCH_UP", flush=True)
            return
        if any(p.get("status") in ("scheduled","sending") and p.get("dueAt") and
               abs((datetime.fromisoformat(p["dueAt"].replace("Z","+00:00")) - due.astimezone(timezone.utc)).total_seconds()) < 40*60
               for p in rows):
            print("EXISTING_PIN_NEAR_SLOT_PRESERVED", item["id"], flush=True)
            return
        verify_png(item["image_url"])
        if dry_run:
            print("HOURLY_PIN_DRY_RUN", item["id"], due.isoformat(),
                  "official_site", HOME, "exact_app_board", EXPECTED_BOARD, flush=True)
            return
        # Final read immediately before writing. Ambiguous mutation results are never blindly retried.
        fresh = history(mod, org)
        if (find_original(fresh, item["id"]) or
            sum(p.get("status") in ("scheduled","sending") for p in fresh) >= MAX_QUEUE):
            print("HOLD_PIN_QUEUE_CHANGED_NO_WRITE", item["id"], flush=True)
            return
        utc = due.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00","Z")
        graph = ("mutation { createPost(input:{ text:" + mod.quoted(item["caption"]) +
                 " channelId:" + mod.quoted(EXPECTED_CHANNEL) +
                 " schedulingType:automatic mode:customScheduled dueAt:" + mod.quoted(utc) +
                 " aiAssisted:true assets:[{image:{url:" + mod.quoted(item["image_url"]) +
                 "}}] metadata:{pinterest:{boardServiceId:" + mod.quoted(EXPECTED_BOARD_ID) +
                 " title:" + mod.quoted(item["title"]) + " url:" + mod.quoted(item["url"]) +
                 "}} }) { ... on PostActionSuccess { post { id status dueAt assets { mimeType source } } }" +
                 " ... on MutationError { message } } }")
        response = mod.query(graph).get("createPost") or {}
        post = response.get("post") if isinstance(response,dict) else None
        if not isinstance(post,dict) or not post.get("id"):
            raise RuntimeError("Pin create unconfirmed for " + item["id"] +
                               "; reconcile provider before retry; " +
                               str(response.get("message",""))[:100])
        print("HOURLY_PIN_BUFFER_SCHEDULED", item["id"], item["app"],
              "Buffer", post["id"], "dueAt", post.get("dueAt"),
              "official_site", HOME, flush=True)
        return
    print("HOURLY_SIX_PIN_CAMPAIGN_COMPLETE; no more posts", flush=True)

if __name__ == "__main__":
    try:
        plan = load()
        parser = argparse.ArgumentParser()
        parser.add_argument("--validate-only", action="store_true")
        opts = parser.parse_args()
        if opts.validate_only:
            print("HOURLY_SIX_PIN_MANIFEST_VALID",len(plan),"unique at 1-hour intervals; root-site captions",flush=True)
        else:
            enabled = os.getenv("ASTRALABS_ONE_TIME_HOURLY_PIN_ENABLED","false").lower() == "true"
            now = datetime.now(PHT)
            # Campaign is strictly one night, not an eternal 1h spam loop.
            if now > planned_due(plan[-1]) + timedelta(minutes=25):
                print("HOURLY_PIN_CAMPAIGN_WINDOW_ENDED; no writes",flush=True)
            else:
                mod, org = target()
                attempt(mod, org, plan, now, dry_run=not enabled)
    except Exception as exc:
        print("HOURLY_PIN_FAIL_CLOSED", type(exc).__name__, str(exc)[:220], file=sys.stderr,flush=True)
        sys.exit(1)
