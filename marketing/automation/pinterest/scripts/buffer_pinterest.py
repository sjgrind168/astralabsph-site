#!/usr/bin/env python3
"""AstraLabs: Pinterest-only organic queue; never publishes to PIREVO Finds."""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.buffer.com"
CHANNEL_ID = "6aa06411cd8b9c702c2ff8ff"
BOARD_NAME = "AstraLabs Apps | Astramate & Keepry"
TARGET = 1  # Controlled first-post proof. Increase only after confirmed success.
BANK = Path(__file__).with_name("buffer_pinterest_content.json")
DENIED = ("tidal computation", "tide calculator", "colregs", "imdg", "imsbc", "cloud sync", "ai ocr")


def quoted(value):
    return json.dumps(str(value), ensure_ascii=True)


def query(graphql):
    key = os.getenv("ASTRALABS_BUFFER_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Missing GitHub Actions Buffer secret")
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": graphql}).encode(),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json",
                 "User-Agent": "AstraLabs-Pinterest-Organic/1.0"},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.load(response)
    except urllib.error.HTTPError as err:
        raise RuntimeError(f"Buffer HTTP {err.code}; no retry to prevent duplicates") from None
    except urllib.error.URLError:
        raise RuntimeError("Buffer connection error; no retry to prevent duplicates") from None
    if result.get("errors"):
        # Do not print full response: it may contain identifiers or user data.
        raise RuntimeError("Buffer GraphQL request rejected; publication stopped")
    if not isinstance(result.get("data"), dict):
        raise RuntimeError("Buffer response missing data object")
    return result["data"]


def target():
    orgs = (query("query { account { organizations { id name } } }")
            .get("account") or {}).get("organizations") or []
    if len(orgs) != 1:
        raise RuntimeError("Ambiguous Buffer organization; stop")
    org_id = orgs[0]["id"]
    qs = ("query { channels(input:{organizationId:" + quoted(org_id) +
          "}) { id name displayName service isDisconnected isLocked isQueuePaused } }")
    channels = query(qs).get("channels") or []
    match = [c for c in channels if c.get("id") == CHANNEL_ID]
    if (len(match) != 1 or str(match[0].get("service", "")).lower() != "pinterest"
            or match[0].get("isDisconnected") or match[0].get("isLocked")
            or match[0].get("isQueuePaused")):
        raise RuntimeError("AstraLabs Pinterest channel unavailable or paused")
    board_data = query(
        "query { channel(input:{id:" + quoted(CHANNEL_ID) +
        "}) { metadata { ... on PinterestMetadata { boards { serviceId name url } } } } }")
    boards = (board_data.get("channel") or {}).get("metadata", {}).get("boards") or []
    matches = [b for b in boards if str(b.get("name", "")).strip().casefold() == BOARD_NAME.casefold()
               and b.get("serviceId")]
    if len(matches) != 1:
        print("WAITING_FOR_BOARD_SYNC: AstraLabs app board is not visible in Buffer yet. PIREVO Finds untouched.")
        return org_id, None
    print("CONFIRMED_APP_BOARD:", matches[0]["name"], "id:", matches[0]["serviceId"])
    return org_id, str(matches[0]["serviceId"])


def get_existing(org_id):
    q = ("query { posts(first:100,input:{organizationId:" + quoted(org_id) +
         ",filter:{status:[scheduled,sent,draft,error,sending],channelIds:[" + quoted(CHANNEL_ID) +
         "]},sort:[{field:dueAt,direction:desc}]})"
         " { edges { node { id text status dueAt channelId } } pageInfo { hasNextPage } } }")
    posts = query(q).get("posts")
    if not isinstance(posts, dict) or not isinstance(posts.get("edges"), list):
        raise RuntimeError("Buffer Pinterest queue/history not available; stop")
    if (posts.get("pageInfo") or {}).get("hasNextPage"):
        raise RuntimeError("Pinterest post history exceeds 100; manual reconciliation required")
    records = [e.get("node") for e in posts["edges"] if isinstance(e.get("node"), dict)]
    if any(item.get("channelId") != CHANNEL_ID for item in records):
        raise RuntimeError("Cross-channel post returned; stop")
    return records


def approved():
    document = json.loads(BANK.read_text(encoding="utf-8"))
    items = document["pins"]
    if document.get("boardName") != BOARD_NAME or len(items) != 9:
        raise RuntimeError("Expected 9 approved no-ETA Pins for the AstraLabs app board")
    if len({item["id"] for item in items}) != 9:
        raise RuntimeError("Duplicate content identifiers in Pinterest bank")
    for item in items:
        value = (item["title"] + " " + item["description"]).lower()
        if (item.get("channel") != "pinterest" or item.get("app") not in ("Astramate", "Keepry")
                or any(x in value for x in DENIED)
                or not item["imageUrl"].startswith("https://www.astralabsph.com/marketing/pins/")
                or not item["imageUrl"].endswith(".png")
                or not item["landingUrl"].startswith(
                    "https://www.astralabsph.com/" + item["app"].lower() + "/?")
                or "utm_content=" + item["id"] not in item["landingUrl"]):
            raise RuntimeError("Rejected unsupported feature, destination or creative for " + item.get("id", "?"))
    return items


def verify_public_image(url):
    request = urllib.request.Request(url, headers={"User-Agent": "AstraLabs-Pin-Asset-Proof/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            prefix = response.read(8)
            if (response.status != 200 or not response.headers.get("Content-Type", "").lower().startswith("image/png")
                    or prefix != b"\x89PNG\r\n\x1a\n"):
                raise RuntimeError("Pin image URL does not serve valid public PNG bytes")
    except urllib.error.HTTPError as err:
        raise RuntimeError(f"Pin image HTTP {err.code}") from None
    except urllib.error.URLError:
        raise RuntimeError("Pin image is not publicly accessible") from None


def publish_pin(item, board_id):
    # Board ID always comes from exact NAME match on the connected authorized channel.
    graph = ("mutation { createPost(input:{ text:" + quoted(item["description"] + "\n\nGet " + item["app"] + ": " + item["landingUrl"]) +
             " channelId:" + quoted(CHANNEL_ID) +
             " schedulingType:automatic mode:addToQueue aiAssisted:true"
             " assets:[{image:{url:" + quoted(item["imageUrl"]) + "}}]"
             " metadata:{pinterest:{boardServiceId:" + quoted(board_id) +
             " title:" + quoted(item["title"]) +
             " url:" + quoted(item["landingUrl"]) + "}} })"
             " { ... on PostActionSuccess { post { id dueAt } }"
             " ... on MutationError { message } } }")
    value = query(graph).get("createPost") or {}
    if not isinstance(value, dict) or not (value.get("post") or {}).get("id"):
        error = str(value.get("message", "No confirmed post returned"))[:140] if isinstance(value, dict) else "Invalid response"
        raise RuntimeError("Buffer Pinterest post unconfirmed: " + error + " | reconcile queue before retry")
    return value["post"]


def main():
    org_id, board_id = target()
    if not board_id:
        return
    items = approved()
    prior = get_existing(org_id)
    in_queue = sum(p.get("status") == "scheduled" for p in prior)
    already = {item["id"] for item in items
               if any("utm_content=" + item["id"] in str(p.get("text") or "") for p in prior)}
    unused = [item for item in items if item["id"] not in already]
    print("Pinterest queue:", in_queue, "approved unused:", len(unused))
    if os.getenv("ASTRALABS_PINTEREST_PUBLISH_ENABLED", "").lower() != "true":
        print("PIN_DRY_RUN: no posts modified; would schedule", max(0, min(TARGET-in_queue, len(unused))))
        return
    for item in unused[:max(0, TARGET - in_queue)]:
        current = get_existing(org_id)
        if sum(p.get("status") == "scheduled" for p in current) >= TARGET:
            break
        if any("utm_content=" + item["id"] in str(p.get("text") or "") for p in current):
            print("Already in Pinterest history:", item["id"])
            continue
        verify_public_image(item["imageUrl"])
        post = publish_pin(item, board_id)
        print("PIN_QUEUED", item["id"], "Buffer id:", post["id"], "dueAt:", post.get("dueAt"))
    done = get_existing(org_id)
    print("FINAL_PINTEREST_QUEUE:", sum(p.get("status") == "scheduled" for p in done))
    print("Only AstraLabs Apps board; no PIREVO Finds posts were written.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("PINTEREST_FAIL_CLOSED:", str(exc), file=sys.stderr)
        sys.exit(1)
