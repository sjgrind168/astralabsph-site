#!/usr/bin/env python3
"""Curated Facebook-only Buffer queue refiller. No Pinterest/Pirevo writes or AI-generated claims."""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

BUFFER_URL = "https://api.buffer.com"
EXPECTED_PAGE_ID = "6ab15144ea19ca0bdea6d621"
QUEUE_TARGET = 5  # A week at the configured five Buffer slots; below free tier queue limit.
CONTENT_PATH = Path(__file__).with_name("buffer_facebook_content.json")
LAUNCH_MARKER = "utm_campaign=global_android_launch"
DISALLOWED = ("tide calculator", "tidal computation", "colregs", "imsbc", "imdg", "weather routing", "cloud sync")


def quoted(value):
    return json.dumps(str(value), ensure_ascii=True)


def buffer_query(graphql):
    token = os.environ.get("ASTRALABS_BUFFER_API_KEY", "").strip()
    if not token:
        raise RuntimeError("GitHub Actions secret ASTRALABS_BUFFER_API_KEY is missing")
    request = urllib.request.Request(
        BUFFER_URL, data=json.dumps({"query": graphql}).encode("utf-8"),
        headers={"Authorization": "Bearer " + token,
                 "Content-Type": "application/json",
                 "User-Agent": "AstraLabs-Organic-Queue/1.0"},
        method="POST")
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError("Buffer HTTP " + str(error.code)) from None
    except urllib.error.URLError:
        raise RuntimeError("Buffer network unavailable") from None
    if payload.get("errors"):
        raise RuntimeError("Buffer GraphQL query rejected; stop without repeating a post")
    if not isinstance(payload.get("data"), dict):
        raise RuntimeError("Buffer returned no data")
    return payload["data"]


def verified_target():
    orgs = (buffer_query("query { account { organizations { id name } } }")
            .get("account") or {}).get("organizations") or []
    if len(orgs) != 1:
        raise RuntimeError("Ambiguous organization; stop")
    org_id = orgs[0]["id"]
    graph = "query { channels(input:{organizationId:" + quoted(org_id) + "}) { id name displayName service isDisconnected isLocked isQueuePaused } }"
    channels = buffer_query(graph).get("channels") or []
    matched = [c for c in channels if c.get("id") == EXPECTED_PAGE_ID]
    if len(matched) != 1:
        raise RuntimeError("Authorized AstraLabs PH Facebook channel was not found; stop")
    channel = matched[0]
    name = str(channel.get("displayName") or channel.get("name") or "")
    if (str(channel.get("service", "")).lower() != "facebook"
            or "astralabs" not in name.lower()
            or channel.get("isDisconnected") or channel.get("isLocked") or channel.get("isQueuePaused")):
        raise RuntimeError("Facebook channel identity/connection/schedule check failed")
    return org_id


def get_existing(org_id):
    # Search scheduled AND already sent posts; unique campaign markers prevent accidental reuse.
    # Fail closed on pagination rather than assuming an unseen earlier post was never published.
    graph = (
        "query { posts(first:100,input:{organizationId:" + quoted(org_id) +
        ",filter:{status:[scheduled,sent],channelIds:[" + quoted(EXPECTED_PAGE_ID) +
        "]},sort:[{field:dueAt,direction:desc}]})"
        " { edges { node { id text status dueAt channelId } }"
        " pageInfo { hasNextPage endCursor } } }"
    )
    node = buffer_query(graph).get("posts")
    if not isinstance(node, dict) or not isinstance(node.get("edges"), list):
        raise RuntimeError("Buffer queue/history response unavailable; stop")
    if (node.get("pageInfo") or {}).get("hasNextPage"):
        raise RuntimeError("Buffer queue/history has more than 100 records; manual reconciliation required")
    found = [x.get("node") for x in node["edges"] if isinstance(x.get("node"), dict)]
    if any(p.get("channelId") != EXPECTED_PAGE_ID for p in found):
        raise RuntimeError("Cross-channel post detected in Facebook audit response")
    return found


def candidates():
    records = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))["posts"]
    if len(records) != 10 or len({x["id"] for x in records}) != 10:
        raise RuntimeError("Curated 10-post launch bank has changed unexpectedly")
    for item in records:
        txt = item["text"]
        if (item.get("channel") != "facebook" or item.get("app") not in ("Astramate", "Keepry")
                or "utm_content=" + item["id"] not in txt or LAUNCH_MARKER not in txt
                or any(blocked in txt.lower() for blocked in DISALLOWED)):
            raise RuntimeError("Unapproved claim, channel or tracking marker in " + item.get("id", "?"))
    return records


def create_post(text):
    graph = ("mutation { createPost(input:{ text:" + quoted(text) +
             " channelId:" + quoted(EXPECTED_PAGE_ID) +
             " schedulingType:automatic mode:addToQueue aiAssisted:true })"
             " { ... on PostActionSuccess { post { id dueAt } }"
             " ... on MutationError { message } } }")
    payload = buffer_query(graph).get("createPost") or {}
    if not isinstance(payload, dict) or not (payload.get("post") or {}).get("id"):
        raise RuntimeError("Buffer did not confirm a queued post; reconcile remotely before retry")
    return payload["post"]


def main():
    dry_run = os.environ.get("ASTRALABS_PUBLISH_ENABLED", "false").lower() != "true"
    org_id = verified_target()
    content = candidates()
    existing = get_existing(org_id)
    queued = sum(p.get("status") == "scheduled" for p in existing)
    seen = {item["id"] for item in content
            if any("utm_content=" + item["id"] in str(p.get("text") or "") for p in existing)}
    remaining = [item for item in content if item["id"] not in seen]
    print("AstraLabs FB | page verified | queued:", queued, "| approved unused:", len(remaining))
    print("PINTEREST / PIREVO untouched. No app graphics or video represented by these text/link posts.")
    if dry_run:
        print("DRY_RUN: would queue at most", max(0, min(QUEUE_TARGET - queued, len(remaining))), "Facebook text/link posts")
        return
    for item in remaining[:max(0, QUEUE_TARGET - queued)]:
        # Recheck on each iteration before a write; never exceed queue target.
        current = get_existing(org_id)
        if sum(p.get("status") == "scheduled" for p in current) >= QUEUE_TARGET:
            break
        if any("utm_content=" + item["id"] in str(p.get("text") or "") for p in current):
            print("Already exists in Buffer, skipping", item["id"])
            continue
        post = create_post(item["text"])
        print("QUEUED", item["id"], "Buffer post:", post["id"], "dueAt:", post.get("dueAt"))
    after = get_existing(org_id)
    print("FINAL FACEBOOK QUEUED:", sum(x.get("status") == "scheduled" for x in after))
    print("APPROVED CONTENT BANK EXHAUSTS AFTER TEN POSTS; NO CONTENT WILL BE REPEATED.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("FAIL CLOSED:", str(exc), file=sys.stderr)
        sys.exit(1)
