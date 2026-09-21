#!/usr/bin/env python3
"""Read-only Buffer channel/queue preflight. Never creates posts or prints API keys."""
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.buffer.com"


def query(document):
    token = os.getenv("ASTRALABS_BUFFER_API_KEY", "").strip()
    if not token:
        raise RuntimeError("Missing repository Actions secret: ASTRALABS_BUFFER_API_KEY")
    request = urllib.request.Request(
        API,
        data=json.dumps({"query": document}).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "User-Agent": "AstraLabs-Buffer-ReadOnly-Audit/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Buffer HTTP {exc.code}; check token and permissions") from None
    except urllib.error.URLError:
        raise RuntimeError("Buffer connection failed; retry later") from None
    if payload.get("errors"):
        raise RuntimeError("Buffer API returned query errors; check API schema and key scopes")
    if not isinstance(payload.get("data"), dict):
        raise RuntimeError("Buffer API did not return a data object")
    return payload["data"]


def qstr(value):
    return json.dumps(str(value), ensure_ascii=True)


def main():
    print("AstraLabs marketing preflight | READ ONLY | no posts will be created")
    organizations = query("query { account { organizations { id name } } }")["account"]["organizations"]
    if not organizations:
        raise RuntimeError("No organization found for this Buffer token")
    if len(organizations) > 1:
        raise RuntimeError("Multiple organizations found; select organization explicitly before proceeding")
    org = organizations[0]
    print("Organization: " + str(org.get("name", "unnamed")))
    response = query(
        "query { channels(input:{organizationId:" + qstr(org["id"]) +
        "}) { id name displayName service isDisconnected isLocked isQueuePaused } }"
    )
    channels = response.get("channels") or []
    if not isinstance(channels, list):
        raise RuntimeError("Channel response is unavailable")
    print("Connected channels: " + str(len(channels)))
    fb = [c for c in channels if str(c.get("service", "")).lower() == "facebook"
          and "astralabs" in str(c.get("displayName") or c.get("name") or "").lower()]
    pn = [c for c in channels if str(c.get("service", "")).lower() == "pinterest"]
    for service, selected in (("facebook", fb), ("pinterest", pn)):
        if len(selected) != 1:
            raise RuntimeError(f"Expected one unambiguous {service} channel; found {len(selected)}")
        channel = selected[0]
        if channel.get("isDisconnected") or channel.get("isLocked"):
            raise RuntimeError(f"{service} needs reconnection or is locked")
        print(f"{service}: CONNECTED; channel id: {channel['id']}; queue paused: {bool(channel.get('isQueuePaused'))}")
    # Check the actual queue and available Pinterest boards before scheduling.
    board_query = (
        "query { channel(input:{id:" + qstr(pn[0]["id"]) +
        "}) { metadata { ... on PinterestMetadata { boards { serviceId name url } } } } }"
    )
    try:
        board_data = query(board_query)
        boards = (board_data.get("channel") or {}).get("metadata", {}).get("boards") or []
        print("Pinterest boards: " + json.dumps(
            [{"name": b.get("name"), "serviceId": b.get("serviceId")} for b in boards],
            ensure_ascii=True
        ))
        target = [b for b in boards if str(b.get("name", "")).strip().lower() == "astralabs apps | astramate & keepry"]
        if len(target) == 1 and target[0].get("serviceId"):
            print("APP_BOARD_CONFIRMED id:", str(target[0]["serviceId"]))
        else:
            print("APP_BOARD_NOT_YET_VISIBLE_IN_BUFFER: do not publish Pinterest posts")
    except (RuntimeError, ValueError, TypeError):
        print("Pinterest board metadata unavailable: do not schedule Pinterest posts")
    try:
        posts_query = (
            "query { posts(first:100,input:{organizationId:" + qstr(org["id"]) +
            ",filter:{status:[scheduled]},sort:[{field:dueAt,direction:asc}]})"
            " { edges { node { id channelId status dueAt } } } }"
        )
        posts = (query(posts_query).get("posts") or {}).get("edges") or []
        for service, selected in (("facebook", fb), ("pinterest", pn)):
            scheduled = [
                e.get("node") for e in posts
                if (e.get("node") or {}).get("channelId") == selected[0]["id"]
            ]
            print(service + " scheduled queue count: " + str(len(scheduled)))
    except (RuntimeError, ValueError, TypeError):
        print("Buffer scheduled queue unavailable: publishing must remain disabled")
    print("Both targets found. This workflow is a connection audit only.")
    print("No posts queued, scheduled, published or modified.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Never print request headers or exception objects containing the API token.
        print(f"PRECHECK FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
