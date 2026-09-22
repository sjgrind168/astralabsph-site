#!/usr/bin/env python3
"""One-writer, proof-gated TikTok/Pinterest refiller for the EXISTING AstraLabs project.

Facebook retains its sole working daily_two_per_app.py writer. This program does NOT
create posts without channel-specific finished, manually approved releases; no Buffer
request is made when approval inventory is empty or channel write flag is OFF.
"""
import argparse
import importlib.util
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
AUTOMATION = HERE.parent
CONFIG = HERE / "ASTRALABS_THREE_CHANNEL_DAILY_CONFIG_20260922.json"
RELEASES = HERE / "ASTRALABS_THREE_CHANNEL_APPROVED_RELEASES_20260922.json"
MANIFEST = HERE / "ASTRALABS_7DAY_42_CREATIVE_MANIFEST_20260923.json"
PHT = ZoneInfo("Asia/Manila")
HOME = "https://www.astralabsph.com/"
MAX_QUEUE = 10
MAX_NEW_PER_RUN = 2
CHANNELS = ("tiktok", "pinterest")
FORMATS = ("voiceover_video", "carousel", "education_question_image")
APP_ORDER = ("Astramate", "Keepry")
FIRST_WAVE_KEEPRY = "6ab1f356ffe5c8afb129534f"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def module(filename, name):
    spec = importlib.util.spec_from_file_location(name, filename)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

def parse_time(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(PHT)
    except (ValueError, AttributeError, TypeError):
        return None

def source_plan(cfg):
    m = load(MANIFEST)
    rows = m.get("content", [])
    if len(rows) != 42 or len({x["id"] for x in rows}) != 42:
        raise RuntimeError("Not exactly 42 unique original editorial concepts")
    if m.get("root_destination") != HOME or cfg.get("site_destination") != HOME:
        raise RuntimeError("Root storefront changed: no publications")
    # A source day has 3 distinct concepts for each app. This check prevents
    # accidentally treating the 9 old Pinterest Pins or the two old MP4s as the bank.
    for day in range(1, 8):
        d = [x for x in rows if x.get("day") == day]
        for app in APP_ORDER:
            one = [x for x in d if x.get("app") == app]
            if len(one) != 3 or {x.get("format") for x in one} != set(FORMATS):
                raise RuntimeError("Missing video/carousel/question for " + app + " day " + str(day))
            if any(x.get("approval") != "PLANNED_ASSETS_NOT_RENDERED_NO_AUTOPUBLISH" for x in one):
                raise RuntimeError("Unexpected source editorial status: review new manifest")
    return rows

def valid_root_link(url, creative_id, app, channel):
    try:
        u = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(u.query, strict_parsing=True)
        return (u.scheme == "https" and u.netloc == "www.astralabsph.com"
                and u.path == "/" and not u.fragment and
                qs.get("app") == [app.lower()] and
                qs.get("utm_source") == [channel] and
                qs.get("utm_content") == [creative_id])
    except (ValueError, TypeError):
        return False

def validate_releases(channel, cfg, manifest):
    ledger = load(RELEASES)
    all_rows = ledger.get("releases")
    if not isinstance(all_rows, list):
        raise RuntimeError("Approval ledger invalid")
    indexed = {p["id"]: p for p in manifest}
    ids, media_urls, selected = set(), set(), []
    for r in all_rows:
        cid, ch = r.get("creative_id"), r.get("channel")
        key = (cid, ch)
        if key in ids:
            raise RuntimeError("Duplicate release key " + str(key))
        ids.add(key)
        if ch not in CHANNELS or cid not in indexed:
            raise RuntimeError("Unknown channel/editorial ID " + str(key))
        original = indexed[cid]
        if r.get("app") != original["app"] or r.get("format") != original["format"]:
            raise RuntimeError("App/format mismatch in " + str(key))
        # Each original concept needs a unique rendered media master on each platform.
        url = r.get("media_url", "")
        parsed = urllib.parse.urlparse(url)
        extension = ".mp4" if ch == "tiktok" else ".png"
        if (parsed.scheme != "https" or parsed.netloc != "www.astralabsph.com"
                or not parsed.path.startswith("/marketing/campaigns/seven_day/")
                or not parsed.path.lower().endswith(extension) or parsed.query
                or url in media_urls):
            raise RuntimeError("Unapproved, repeated or off-domain media URL: " + str(key))
        media_urls.add(url)
        if r.get("approved") is not True or any(
                not isinstance(r.get(k), str) or not r[k].strip()
                for k in ("reviewed_by", "feature_proof", "authentic_screenshot_proof",
                          "commercial_rights_record", "native_format_qa", "last_review_pht")):
            raise RuntimeError("Missing manual approval and authentic proof/rights: " + str(key))
        if r["reviewed_by"].strip().lower() in ("automated", "ai", "bot", "none"):
            raise RuntimeError("Requires owner/authorized human review: " + str(key))
        if not valid_root_link(r.get("landing_url"), cid, original["app"], ch):
            raise RuntimeError("Landing URL is not tracked root-only: " + str(key))
        caption = r.get("caption", "")
        if not isinstance(caption, str) or len(caption) < 40 or HOME not in caption:
            raise RuntimeError("Missing useful root-storefront caption: " + str(key))
        urls = re.findall(r"https?://[^\s<>\")]+", caption)
        if any(not urllib.parse.urlparse(u.rstrip(".,"))._replace(query="",fragment="").geturl() == HOME
               for u in urls):
            raise RuntimeError("Non-root promotional link in caption: " + str(key))
        if any(x in caption.lower() for x in ("astramate.vercel.app", "/keepry/", "/astramate/",
                                             "guaranteed", "ai ocr", "cloud sync", "colregs", "imdg")):
            raise RuntimeError("Unverified claim or old CTA " + str(key))
        if ch == "tiktok":
            if len(caption) > 500 or r.get("native_format_qa", "").find("30fps") < 0:
                raise RuntimeError("TikTok video/native-format QA missing " + str(key))
        else:
            if not isinstance(r.get("pinterest_title"), str) or not 10 <= len(r["pinterest_title"]) <= 100:
                raise RuntimeError("Missing useful Pinterest title " + str(key))
        if ch == channel:
            selected.append(r)
    return selected

def check_public_media(url, channel):
    header = {"Range": "bytes=0-31", "User-Agent": "AstraLabs-Approved-Original/1.0"}
    req = urllib.request.Request(url, headers=header)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            prefix = resp.read(32)
            mime = resp.headers.get("Content-Type", "").split(";")[0].strip().lower()
            if (resp.status not in (200, 206)
                    or (channel == "tiktok" and not (mime in ("video/mp4", "application/octet-stream")
                                                     and len(prefix) >= 12 and prefix[4:8] == b"ftyp"))
                    or (channel == "pinterest" and not (mime == "image/png"
                                                        and prefix[:8] == b"\x89PNG\r\n\x1a\n"))):
                raise RuntimeError("Approved original media format not verified")
    except (urllib.error.HTTPError, urllib.error.URLError):
        raise RuntimeError("Approved media is not publicly reachable; hold publication") from None

def history(org, channel_id, graphql, quote):
    doc = ("query { posts(first:100,input:{organizationId:" + quote(org) +
           ",filter:{status:[scheduled,sent,draft,error,sending],channelIds:[" + quote(channel_id) +
           "]},sort:[{field:createdAt,direction:desc}]})"
           " { edges { node { id text status channelId dueAt externalLink assets { mimeType source } } }"
           " pageInfo { hasNextPage } } }")
    result = graphql(doc).get("posts")
    if not isinstance(result, dict) or not isinstance(result.get("edges"), list):
        raise RuntimeError("Full Buffer channel history unavailable: do not write")
    if (result.get("pageInfo") or {}).get("hasNextPage"):
        raise RuntimeError("Buffer channel has more than 100 history items; do not guess")
    rows = [e["node"] for e in result["edges"] if isinstance(e.get("node"), dict)]
    if any(p.get("channelId") != channel_id for p in rows):
        raise RuntimeError("Cross-channel results; stop")
    return rows

def published_on_day(row, app, day):
    when = parse_time(row.get("dueAt"))
    text = str(row.get("text") or "").lower()
    assets = [str(x.get("source") or "").lower() for x in row.get("assets") or []]
    match = app.lower() in text or any(app.lower() in s for s in assets)
    return bool(when and when.date() == day and match
                and row.get("status") in ("sent", "scheduled", "sending"))

def scheduled_window(cfg, channel, original, now):
    day = datetime.fromisoformat(original["date"]).date()
    code = {"voiceover_video": 0, "carousel": 1, "education_question_image": 2}[original["format"]]
    hhmm = cfg["slots_pht"][channel][original["app"]][code]
    hh, mm = map(int, hhmm.split(":"))
    due = datetime(day.year, day.month, day.day, hh, mm, tzinfo=PHT)
    if due < now + timedelta(minutes=25):
        return None
    return due

def create_one(channel, channel_id, board_id, original, release, due, graphql, quote):
    due_utc = due.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    caption = release["caption"]
    media = release["media_url"]
    if channel == "tiktok":
        meta = "metadata:{tiktok:{isAiGenerated:true}}"
        asset = "assets:[{video:{url:" + quote(media) + " metadata:{thumbnailOffset:2000}}}]"
    else:
        meta = ("metadata:{pinterest:{boardServiceId:" + quote(board_id) +
                " title:" + quote(release["pinterest_title"]) +
                " url:" + quote(release["landing_url"]) + "}}")
        asset = "assets:[{image:{url:" + quote(media) + "}}]"
        caption += "\n\n" + release["landing_url"]
    doc = ("mutation { createPost(input:{text:" + quote(caption) +
           " channelId:" + quote(channel_id) +
           " schedulingType:automatic mode:customScheduled dueAt:" + quote(due_utc) +
           " aiAssisted:true " + meta + " " + asset + "})"
           " { ... on PostActionSuccess { post { id status dueAt assets { mimeType source } } }"
           " ... on MutationError { message } } }")
    response = graphql(doc).get("createPost") or {}
    p = response.get("post") if isinstance(response, dict) else None
    if not isinstance(p, dict) or not p.get("id"):
        raise RuntimeError("Buffer post create unconfirmed for " + original["id"] +
                           ": " + str(response.get("message", ""))[:120] + "; no blind retry")
    if p.get("status") != "scheduled" or not p.get("assets"):
        raise RuntimeError("Created post state/asset unexpected; reconcile exact ID " + p["id"])
    print("BUFFER_SCHEDULED", channel, original["id"], original["app"],
          due.isoformat(), "post_id", p["id"], flush=True)
    return p, caption

def run(channel):
    cfg = load(CONFIG)
    originals = source_plan(cfg)
    approved = validate_releases(channel, cfg, originals)
    approved_by_id = {r["creative_id"]: r for r in approved}
    print("DAILY_TARGET", channel, "3_per_app_6_total", "approved_originals", len(approved), flush=True)
    if not approved:
        print("HELD_NO_APPROVED_ORIGINAL_MEDIA: 42 briefs are planning only; no Buffer API called", flush=True)
        return
    if os.getenv("ASTRALABS_" + channel.upper() + "_THREE_DAILY_PUBLISH_ENABLED", "false").lower() != "true":
        print("HELD_CHANNEL_WRITES_OFF: no Buffer API called; never publish unproven master", flush=True)
        return
    now = datetime.now(PHT)
    candidates = [p for p in originals if p["id"] in approved_by_id
                  and 0 <= (datetime.fromisoformat(p["date"]).date() - now.date()).days <= 1]
    if not candidates:
        print("NO_APPROVED_CURRENT_OR_NEXT_DAY_CANDIDATES: no Buffer API called", flush=True)
        return
    # Use one existing approved publisher identity and its proven exact channel ID.
    if channel == "tiktok":
        tt = module(AUTOMATION / "tiktok/scripts/buffer_tiktok.py", "astralabs_existing_tiktok")
        org, channel_id = tt.resolve_tiktok()
        board_id, graphql, quote = None, tt.gql, tt.q
    else:
        pin = module(AUTOMATION / "pinterest/scripts/buffer_pinterest.py", "astralabs_existing_pinterest")
        org, board_id = pin.target()  # exact AstraLabs Apps board match, never PIREVO
        if not board_id:
            print("HELD_PINTEREST_BOARD_NOT_API_VERIFIED; no write", flush=True)
            return
        channel_id, graphql, quote = pin.CHANNEL_ID, pin.query, pin.quoted
    rows = history(org, channel_id, graphql, quote)
    if channel == "tiktok":
        first = [p for p in rows if p.get("id") == FIRST_WAVE_KEEPRY]
        if len(first) != 1 or first[0].get("status") != "sent" or not first[0].get("externalLink"):
            print("HELD_KEEPRY_FIRST_WAVE_UNRECONCILED: exact pre-existing ID not native-live verified", flush=True)
            return
    queued = sum(p.get("status") in ("scheduled", "sending") for p in rows)
    if queued >= MAX_QUEUE:
        print("BUFFER_FREE_QUEUE_CAP: old posts preserved; no new write", flush=True)
        return
    created = 0
    # Current PHT day first. No catch-up compression, no irrelevant expired slots.
    candidates.sort(key=lambda p: (p["date"], scheduled_window(cfg, channel, p, now)
                                   or datetime.max.replace(tzinfo=PHT)))
    for p in candidates:
        if created >= MAX_NEW_PER_RUN or queued >= MAX_QUEUE:
            break
        due = scheduled_window(cfg, channel, p, now)
        if not due:
            continue
        item = approved_by_id[p["id"]]
        if any(p["id"] in str(x.get("text") or "") or
               any(a.get("source") == item["media_url"] for a in x.get("assets") or [])
               for x in rows):
            print("DEDUPED_FROM_FULL_HISTORY", channel, p["id"], flush=True)
            continue
        if sum(published_on_day(x, p["app"], due.date()) for x in rows) >= 3:
            print("APP_DAY_CAP_REACHED", channel, p["app"], due.date(), flush=True)
            continue
        if any(x.get("status") in ("scheduled", "sending") and
               (x_due := parse_time(x.get("dueAt"))) and
               abs((x_due - due).total_seconds()) < 25 * 60 for x in rows):
            print("EXISTING_POST_NEAR_SLOT", channel, p["id"], flush=True)
            continue
        check_public_media(item["media_url"], channel)
        # Reread before the mutation. A throttle/error stops safely instead of guessing.
        latest = history(org, channel_id, graphql, quote)
        if (sum(x.get("status") in ("scheduled", "sending") for x in latest) >= MAX_QUEUE or
            any(p["id"] in str(x.get("text") or "") or
                any(a.get("source") == item["media_url"] for a in x.get("assets") or [])
                for x in latest) or
            sum(published_on_day(x, p["app"], due.date()) for x in latest) >= 3):
            print("RACE_GUARD: queue/content changed, no write", flush=True)
            return
        post, caption = create_one(channel, channel_id, board_id, p, item, due, graphql, quote)
        rows = latest + [{"id":post["id"],"status":post["status"],"dueAt":post.get("dueAt"),
                          "channelId":channel_id,"text":caption,"assets":post.get("assets",[])}]
        queued += 1
        created += 1
    print("SAFE_BATCH_COMPLETE", channel, "new_scheduled", created,
          "requires_future_native_live_proof", flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", choices=CHANNELS, required=True)
    args = parser.parse_args()
    try:
        run(args.channel)
    except Exception as error:
        print("FAIL_CLOSED", args.channel, type(error).__name__, str(error), file=sys.stderr, flush=True)
        sys.exit(1)
