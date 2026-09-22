#!/usr/bin/env python3
"""AstraLabs TikTok-only video queue. Fail closed on channel/media uncertainty."""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.buffer.com"
BANK = Path(__file__).with_name("buffer_tiktok_content.json")
PUBLIC_PREFIX = "https://www.astralabsph.com/marketing/videos/v2/"
QUEUE_LIMIT = 1  # One controlled proof before expanding. Never re-use sent posts.

def q(value):
    return json.dumps(str(value), ensure_ascii=True)

def gql(document):
    key = os.environ.get("ASTRALABS_BUFFER_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Buffer secret not installed; publishing stopped")
    req = urllib.request.Request(
        API, data=json.dumps({"query": document}).encode(),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json",
                 "User-Agent": "AstraLabs-TikTok-Queue/1.0"},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            payload = json.load(resp)
    except (urllib.error.HTTPError, urllib.error.URLError) as exc:
        raise RuntimeError("Buffer connection failed; reconcile before retry") from None
    if payload.get("errors") or not isinstance(payload.get("data"), dict):
        raise RuntimeError("Buffer GraphQL response rejected; no publishing")
    return payload["data"]

def resolve_tiktok():
    orgs = (gql("query { account { organizations { id name } } }")
            .get("account") or {}).get("organizations") or []
    if len(orgs) != 1:
        raise RuntimeError("Ambiguous Buffer organization")
    org_id = orgs[0]["id"]
    doc = ("query { channels(input:{organizationId:" + q(org_id) +
           "}) { id name displayName service isDisconnected isLocked isQueuePaused } }")
    channels = gql(doc).get("channels") or []
    matches = [c for c in channels if str(c.get("service", "")).lower() == "tiktok"
               and "astralabsph" in str(c.get("displayName") or c.get("name") or "").lower()]
    if len(matches) != 1:
        raise RuntimeError("Expected exactly one authorized @astralabsph TikTok channel")
    channel = matches[0]
    if channel.get("isDisconnected") or channel.get("isLocked") or channel.get("isQueuePaused"):
        raise RuntimeError("TikTok channel unavailable, locked or paused")
    print("TARGET VERIFIED: TikTok @astralabsph (channel ID omitted)")
    return org_id, channel["id"]

def current_posts(org_id, channel_id):
    doc = ("query { posts(first:100,input:{organizationId:" + q(org_id) +
           ",filter:{status:[scheduled,sent],channelIds:[" + q(channel_id) +
           "]},sort:[{field:dueAt,direction:desc}]})"
           " { edges { node { id text status dueAt channelId schedulingType assets { mimeType source } } }"
           " pageInfo { hasNextPage } } }")
    result = gql(doc).get("posts")
    if not isinstance(result, dict) or not isinstance(result.get("edges"), list):
        raise RuntimeError("Buffer TikTok queue/history unavailable")
    if (result.get("pageInfo") or {}).get("hasNextPage"):
        raise RuntimeError("TikTok post history over 100: reconcile before auto-posting")
    posts = [edge["node"] for edge in result["edges"] if isinstance(edge.get("node"), dict)]
    if any(p.get("channelId") != channel_id for p in posts):
        raise RuntimeError("Channel mismatch in TikTok history")
    return posts

def approved():
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    items = bank.get("posts") or []
    if len(items) != 2 or len({p["id"] for p in items}) != 2:
        raise RuntimeError("Expected the two approved unique first-wave videos")
    for p in items:
        url = p["videoUrl"]
        if (p.get("app") not in ("Astramate", "Keepry")
                or not url.startswith(PUBLIC_PREFIX)
                or not url.endswith(".mp4")
                or not p["text"].strip() or len(p["text"]) > 150
                or "tide calculator" in p["text"].lower()
                or "cloud sync" in p["text"].lower()):
            raise RuntimeError("Unapproved TikTok post metadata")
    return items

def verify_media(url):
    # A direct public MP4 is required; /mnt/data sandbox and Library links are not accepted by Buffer.
    req = urllib.request.Request(url, headers={"User-Agent": "AstraLabs-TikTok-Media-Proof/1.0",
                                              "Range": "bytes=0-15"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            mime = resp.headers.get("Content-Type", "").split(";")[0].strip().lower()
            sig = resp.read(16)
            return (resp.status in (200, 206)
                    and mime in ("video/mp4", "application/octet-stream")
                    and len(sig) >= 12 and sig[4:8] == b"ftyp")
    except (urllib.error.HTTPError, urllib.error.URLError):
        return False

def add_post(channel_id, item):
    doc = ("mutation { createPost(input:{ text:" + q(item["text"]) +
           " channelId:" + q(channel_id) +
           " schedulingType:automatic mode:addToQueue aiAssisted:true"
           " metadata:{tiktok:{isAiGenerated:true}}"
           " assets:[{video:{url:" + q(item["videoUrl"]) +
           " metadata:{thumbnailOffset:2000}}}] })"
           " { ... on PostActionSuccess { post { id dueAt } }"
           " ... on MutationError { message } } }")
    result = gql(doc).get("createPost") or {}
    if not isinstance(result, dict) or not isinstance(result.get("post"), dict) or not result["post"].get("id"):
        raise RuntimeError("TikTok createPost unconfirmed; do not retry without queue review")
    return result["post"]

def main():
    org_id, channel_id = resolve_tiktok()
    posts = current_posts(org_id, channel_id)
    items = approved()
    scheduled = sum(p.get("status") == "scheduled" for p in posts)
    unused = [i for i in items if not any(p.get("text") == i["text"] for p in posts)]
    print("TikTok scheduled:", scheduled, "| approved unused:", len(unused))
    for post in posts:
        if post.get("status") == "scheduled":
            media = post.get("assets") or []
            print("QUEUED_VIDEO_AUDIT:", post["id"], "publish_mode:", post.get("schedulingType"),
                  "video_assets:", sum(str(a.get("mimeType", "")).startswith("video/") for a in media),
                  "approved_url:", any(str(a.get("source", "")).startswith(PUBLIC_PREFIX) for a in media),
                  "dueAt:", post.get("dueAt"))
    if scheduled >= QUEUE_LIMIT or not unused:
        print("Queue full or approved first-wave videos exhausted. No duplicate posts.")
        return
    item = unused[0]
    if not verify_media(item["videoUrl"]):
        print("MEDIA_NOT_HOSTED: approved MP4 is not publicly accessible at the fixed AstraLabs URL. No post created.")
        return
    if os.environ.get("ASTRALABS_TIKTOK_PUBLISH_ENABLED", "").lower() != "true":
        print("DRY_RUN: video reachable; would schedule one", item["app"], "TikTok video. No post created.")
        return
    # Recheck before writing, in case the owner manually queued an identical video.
    latest = current_posts(org_id, channel_id)
    if sum(p.get("status") == "scheduled" for p in latest) >= QUEUE_LIMIT:
        print("Queue filled since preflight; no post created.")
        return
    if any(p.get("text") == item["text"] for p in latest):
        print("Identical video caption already scheduled/sent; no post created.")
        return
    created = add_post(channel_id, item)
    print("TIKTOK_VIDEO_QUEUED:", item["id"], "post:", created["id"], "dueAt:", created.get("dueAt"))
    print("This confirms scheduling only; verify actual TikTok publication after dueAt.")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("FAIL_CLOSED:", str(exc), file=sys.stderr)
        sys.exit(1)
