#!/usr/bin/env python3
"""PIREVO Pinterest queue writer for the existing AstraLabs Pinterest channel.

Scope is intentionally narrow:
- PIREVO Finds board only
- seasonal queue only: Halloween Wave 3 first, Christmas Wave 4 next
- exact PIREVO product-page destinations
- max 3 new pins per run
- fail closed on ambiguous board/channel/history/public asset validation
"""
from __future__ import annotations
import json, os, sys, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

API="https://api.buffer.com"
CHANNEL_ID="6aa06411cd8b9c702c2ff8ff"
BOARD_NAME="PIREVO Finds"
QUEUE_TARGET=3
TOTAL_QUEUE_CAP=3
MAX_ADD_PER_RUN=3
ROOT=Path(__file__).resolve().parents[2]
MANIFESTS=[
    ("wave3-halloween",ROOT/"public/pirevo/assets/pins/wave3-halloween/manifest.json",16,"https://www.astralabsph.com/pirevo/assets/pins/wave3-halloween/"),
    ("wave4-christmas",ROOT/"public/pirevo/assets/pins/wave4-christmas/manifest.json",0,"https://www.astralabsph.com/pirevo/assets/pins/wave4-christmas/"),
]
REPORT=ROOT/"marketing/pirevo/PIREVO_PINTEREST_QUEUE_STATUS.json"

def q(v): return json.dumps(str(v),ensure_ascii=True)

def gql(query):
    key=os.getenv("ASTRALABS_BUFFER_API_KEY","").strip()
    if not key: raise RuntimeError("Missing GitHub Actions Buffer secret")
    req=urllib.request.Request(API,data=json.dumps({"query":query}).encode(),
        headers={"Authorization":"Bearer "+key,"Content-Type":"application/json",
                 "User-Agent":"PIREVO-Pinterest-Organic/1.0"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=30) as r: payload=json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Buffer HTTP {e.code}; stop to prevent duplicates") from None
    except urllib.error.URLError:
        raise RuntimeError("Buffer connection error; stop to prevent duplicates") from None
    if payload.get("errors"): raise RuntimeError("Buffer GraphQL rejected request")
    data=payload.get("data")
    if not isinstance(data,dict): raise RuntimeError("Buffer response missing data")
    return data

def resolve_target():
    orgs=((gql("query { account { organizations { id name } } }").get("account") or {}).get("organizations") or [])
    if len(orgs)!=1: raise RuntimeError("Ambiguous Buffer organization")
    org=orgs[0]["id"]
    channels=gql("query { channels(input:{organizationId:"+q(org)+"}) { id service isDisconnected isLocked isQueuePaused } }").get("channels") or []
    match=[c for c in channels if c.get("id")==CHANNEL_ID]
    if len(match)!=1 or str(match[0].get("service","")).lower()!="pinterest":
        raise RuntimeError("Expected Pinterest channel not found")
    c=match[0]
    if c.get("isDisconnected") or c.get("isLocked") or c.get("isQueuePaused"):
        raise RuntimeError("Pinterest channel unavailable/paused")
    meta=gql("query { channel(input:{id:"+q(CHANNEL_ID)+"}) { metadata { ... on PinterestMetadata { boards { serviceId name url } } } } }")
    boards=((meta.get("channel") or {}).get("metadata") or {}).get("boards") or []
    board=[b for b in boards if str(b.get("name","")).strip().casefold()==BOARD_NAME.casefold() and b.get("serviceId")]
    if len(board)!=1:
        raise RuntimeError("PIREVO Finds board not uniquely visible in Buffer")
    return org,str(board[0]["serviceId"])

def history(org):
    query=("query { posts(first:100,input:{organizationId:"+q(org)+
           ",filter:{status:[scheduled,sent,sending,draft,error],channelIds:["+q(CHANNEL_ID)+
           "]},sort:[{field:createdAt,direction:desc}]}) { edges { node { id text status dueAt channelId externalLink } } pageInfo { hasNextPage } } }")
    p=gql(query).get("posts")
    if not isinstance(p,dict) or not isinstance(p.get("edges"),list):
        raise RuntimeError("Buffer Pinterest history unavailable")
    if (p.get("pageInfo") or {}).get("hasNextPage"):
        raise RuntimeError("Pinterest history exceeds safe reconciliation window")
    rows=[e.get("node") for e in p["edges"] if isinstance(e.get("node"),dict)]
    if any(x.get("channelId")!=CHANNEL_ID for x in rows):
        raise RuntimeError("Cross-channel history returned")
    return rows

def load_pins():
    """Load seasonal Wave 3 first, then preserve remaining Wave 2 backlog."""
    all_pins=[]; seen=set()
    for wave,path,expected,image_prefix in MANIFESTS:
        if not path.exists():
            if wave=="wave3-halloween":
                raise RuntimeError("Halloween Wave 3 manifest not rendered yet")
            continue
        doc=json.loads(path.read_text(encoding="utf-8"))
        pins=doc.get("pins") or []
        if expected and len(pins)!=expected: raise RuntimeError(f"Expected exactly {expected} pins in {wave}")
        if wave=="wave4-christmas" and not pins: continue
        for p in pins:
            pid=p.get("id")
            if not pid or pid in seen: raise RuntimeError("Duplicate/missing pin id across manifests")
            seen.add(pid)
            if len(str(p.get("title","")))>100: raise RuntimeError("Pinterest title over 100 chars")
            img=str(p.get("imageUrl",""))
            dest=str(p.get("destination",""))
            if not img.startswith(image_prefix) or not img.endswith(".jpg"):
                raise RuntimeError(f"Unapproved PIREVO image URL in {wave}")
            if not dest.startswith("https://www.astralabsph.com/pirevo/products/"):
                raise RuntimeError("Unapproved PIREVO product landing URL")
            all_pins.append(p)
    return all_pins

def landing(pin):
    u=urllib.parse.urlsplit(pin["destination"])
    qs=urllib.parse.parse_qsl(u.query,keep_blank_values=True)
    qs += [("utm_source","pinterest"),("utm_medium","organic"),("utm_campaign",str(pin.get("campaign") or "pirevo_pinterest")),("utm_content",pin["id"])]
    return urllib.parse.urlunsplit((u.scheme,u.netloc,u.path,urllib.parse.urlencode(qs),u.fragment))

def marker(pid): return "utm_content="+pid

def verify_image(url):
    req=urllib.request.Request(url,headers={"Range":"bytes=0-15","User-Agent":"PIREVO-Pin-Asset-Proof/1.0"})
    try:
        with urllib.request.urlopen(req,timeout=20) as r:
            head=r.read(3); ct=(r.headers.get("Content-Type") or "").lower()
            if r.status not in (200,206) or head!=b"\xff\xd8\xff" or "image/jpeg" not in ct:
                raise RuntimeError("public Pin URL did not return JPEG")
    except urllib.error.HTTPError as e: raise RuntimeError(f"Pin image HTTP {e.code}") from None
    except urllib.error.URLError: raise RuntimeError("Pin image URL unreachable") from None

def create_pin(pin,board_id):
    url=landing(pin)
    desc=str(pin.get("description") or "").strip()
    text=(desc+"\n\nSee the full PIREVO pick: "+url).strip()
    if len(text)>800: text=text[:760].rsplit(" ",1)[0]+"…\n\n"+url
    mutation=("mutation { createPost(input:{ text:"+q(text)+
              " channelId:"+q(CHANNEL_ID)+
              " schedulingType:automatic mode:addToQueue aiAssisted:true"+
              " assets:[{image:{url:"+q(pin["imageUrl"])+"}}]"+
              " metadata:{pinterest:{boardServiceId:"+q(board_id)+
              " title:"+q(pin["title"])+" url:"+q(url)+"}} })"+
              " { ... on PostActionSuccess { post { id dueAt status } }"+
              " ... on MutationError { message } } }")
    out=gql(mutation).get("createPost") or {}
    post=out.get("post") if isinstance(out,dict) else None
    if not post or not post.get("id"):
        raise RuntimeError("Buffer did not confirm PIREVO Pin creation: "+str(out.get("message","unknown"))[:120])
    return post

def write_report(data):
    REPORT.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding="utf-8")

def main():
    org,board_id=resolve_target()
    pins=load_pins()
    prior=history(org)
    scheduled=[x for x in prior if x.get("status")=="scheduled"]
    pirevo_scheduled=[x for x in scheduled if "/pirevo/" in str(x.get("text") or "")]
    used={p["id"] for p in pins if any(marker(p["id"]) in str(x.get("text") or "") for x in prior)}
    unused=[p for p in pins if p["id"] not in used]
    capacity=max(0,min(QUEUE_TARGET-len(pirevo_scheduled),TOTAL_QUEUE_CAP-len(scheduled),MAX_ADD_PER_RUN,len(unused)))
    report={"generated_at_utc":datetime.now(timezone.utc).isoformat(),"board":BOARD_NAME,
            "scheduled_total_before":len(scheduled),"pirevo_scheduled_before":len(pirevo_scheduled),
            "unused_before":len(unused),"capacity":capacity,"created":[]}
    if os.getenv("PIREVO_PINTEREST_PUBLISH_ENABLED","").lower()!="true":
        report["mode"]="dry_run"; write_report(report)
        print("PIREVO_PIN_DRY_RUN",json.dumps(report)); return
    for pin in unused[:capacity]:
        # Reconcile before every write.
        current=history(org)
        if len([x for x in current if x.get("status")=="scheduled"])>=TOTAL_QUEUE_CAP: break
        if any(marker(pin["id"]) in str(x.get("text") or "") for x in current): continue
        verify_image(pin["imageUrl"])
        post=create_pin(pin,board_id)
        report["created"].append({"pin_id":pin["id"],"buffer_id":post["id"],"dueAt":post.get("dueAt")})
    after=history(org)
    report["mode"]="write"
    report["scheduled_total_after"]=len([x for x in after if x.get("status")=="scheduled"])
    report["pirevo_scheduled_after"]=len([x for x in after if x.get("status")=="scheduled" and "/pirevo/" in str(x.get("text") or "")])
    write_report(report)
    print("PIREVO_PIN_QUEUE_OK",json.dumps(report))

if __name__=="__main__":
    try: main()
    except Exception as e:
        print("PIREVO_PIN_QUEUE_FAIL_CLOSED:",str(e),file=sys.stderr)
        sys.exit(1)
