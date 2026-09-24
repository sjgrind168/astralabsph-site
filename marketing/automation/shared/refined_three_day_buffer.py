#!/usr/bin/env python3
"""Finite three-day AstraLabs Buffer deployment.

Owner-authorized Sep24 2026 PHT. Preserves all existing posts, uses exact existing
AstraLabs channels, schedules only the refined Sep26-28 pack, then expires.
"""
import argparse
import importlib.util
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

HERE=Path(__file__).resolve().parent
AUTOMATION=HERE.parent
MANIFEST=HERE/"ASTRALABS_REFINED_3DAY_BUFFER_PACK_20260926.json"
PHT=ZoneInfo("Asia/Manila")
HOME="https://www.astralabsph.com/"
MAX_QUEUE=10
MAX_NEW_PER_RUN=2
CHANNELS=("facebook","pinterest","tiktok")
EXPECTED_FB="6ab15144ea19ca0bdea6d621"
EXPECTED_PIN="6aa06411cd8b9c702c2ff8ff"
EXPECTED_BOARD="1143844074049569906"

def load_module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

def load_pack():
    data=json.loads(MANIFEST.read_text(encoding="utf-8"))
    posts=data.get("posts")
    if (data.get("schema_version")!=1 or data.get("timezone")!="Asia/Manila"
            or data.get("official_site")!=HOME or data.get("start_date_pht")!="2026-09-26"
            or data.get("end_date_pht")!="2026-09-28" or not isinstance(posts,list)
            or len(posts)!=18 or len({p.get("id") for p in posts})!=18):
        raise RuntimeError("Unexpected refined 3-day manifest")
    for channel in CHANNELS:
        selected=[p for p in posts if p.get("channel")==channel]
        if len(selected)!=6:
            raise RuntimeError("Expected six "+channel+" placements")
        for day in ("2026-09-26","2026-09-27","2026-09-28"):
            day_rows=[p for p in selected if p.get("day_pht")==day]
            if len(day_rows)!=2 or {p.get("app") for p in day_rows}!={"Astramate","Keepry"}:
                raise RuntimeError("Daily app pair missing for "+channel+" "+day)
    for p in posts:
        if p.get("app") not in ("Astramate","Keepry") or not p.get("caption") or HOME not in p["caption"]:
            raise RuntimeError("Bad app/caption "+str(p.get("id")))
        try:
            day=datetime.strptime(p["day_pht"],"%Y-%m-%d").date()
            hh,mm=map(int,p["time_pht"].split(":"))
            datetime(day.year,day.month,day.day,hh,mm,tzinfo=PHT)
        except Exception:
            raise RuntimeError("Bad local due time "+str(p.get("id"))) from None
        u=urllib.parse.urlparse(p.get("landing_url",""))
        qs=urllib.parse.parse_qs(u.query)
        if (u.scheme!="https" or u.netloc!="www.astralabsph.com" or u.path!="/"
                or qs.get("utm_content")!=[p["id"]] or qs.get("utm_source")!=[p["channel"]]
                or qs.get("app")!=[p["app"].lower()]):
            raise RuntimeError("Bad tracked main-site landing "+p["id"])
        if p["channel"]=="pinterest":
            if len(p["caption"])>500 or not isinstance(p.get("pinterest_title"),str) or not 10<=len(p["pinterest_title"])<=100:
                raise RuntimeError("Pinterest copy invalid "+p["id"])
        elif p["channel"]=="tiktok":
            if len(p["caption"])>500:
                raise RuntimeError("TikTok copy invalid "+p["id"])
    return data

def due_pht(p):
    day=datetime.strptime(p["day_pht"],"%Y-%m-%d").date()
    hh,mm=map(int,p["time_pht"].split(":"))
    return datetime(day.year,day.month,day.day,hh,mm,tzinfo=PHT)

def media_ok(url,channel):
    parsed=urllib.parse.urlparse(url)
    want=".mp4" if channel=="tiktok" else ".png"
    if (parsed.scheme!="https" or parsed.netloc!="www.astralabsph.com"
            or not parsed.path.startswith("/marketing/campaigns/seven_day/day1/")
            or not parsed.path.lower().endswith(want) or parsed.query):
        return False
    req=urllib.request.Request(url,headers={"Range":"bytes=0-31","User-Agent":"AstraLabs-Refined3-MediaProof/1.0"})
    try:
        with urllib.request.urlopen(req,timeout=20) as resp:
            prefix=resp.read(32)
            mime=resp.headers.get("Content-Type","").split(";")[0].lower()
            if resp.status not in (200,206): return False
            if channel=="tiktok":
                return mime in ("video/mp4","application/octet-stream") and len(prefix)>=12 and prefix[4:8]==b"ftyp"
            return mime=="image/png" and prefix[:8]==b"\x89PNG\r\n\x1a\n"
    except (urllib.error.HTTPError,urllib.error.URLError):
        return False

def parse_due(value):
    if not value: return None
    try:return datetime.fromisoformat(value.replace("Z","+00:00")).astimezone(PHT)
    except Exception:return None

def resolve(channel):
    if channel=="facebook":
        mod=load_module(AUTOMATION/"facebook/scripts/buffer_facebook.py","refined_fb")
        org=mod.verified_target()
        return mod,org,EXPECTED_FB,None,mod.buffer_query,mod.quoted
    if channel=="tiktok":
        mod=load_module(AUTOMATION/"tiktok/scripts/buffer_tiktok.py","refined_tt")
        org,cid=mod.resolve_tiktok()
        return mod,org,cid,None,mod.gql,mod.q
    mod=load_module(AUTOMATION/"pinterest/scripts/buffer_pinterest.py","refined_pin")
    org,board=mod.target()
    if board!=EXPECTED_BOARD:
        raise RuntimeError("Exact AstraLabs Apps Pinterest board not verified")
    return mod,org,EXPECTED_PIN,board,mod.query,mod.quoted

def history(org,cid,graphql,quote):
    doc=("query { posts(first:100,input:{organizationId:"+quote(org)+
         ",filter:{status:[scheduled,sent,draft,error,sending],channelIds:["+quote(cid)+
         "]},sort:[{field:createdAt,direction:desc}]}) { edges { node { id text status dueAt channelId externalLink assets { mimeType source } } } pageInfo { hasNextPage } } }")
    obj=graphql(doc).get("posts")
    if not isinstance(obj,dict) or not isinstance(obj.get("edges"),list) or (obj.get("pageInfo") or {}).get("hasNextPage"):
        raise RuntimeError("Complete Buffer history unavailable; no writes")
    rows=[e["node"] for e in obj["edges"] if isinstance(e.get("node"),dict)]
    if any(r.get("channelId")!=cid for r in rows):
        raise RuntimeError("Cross-channel Buffer history")
    return rows

def seen(rows,p):
    marker="utm_content="+p["id"]
    return any(marker in str(r.get("text") or "") or
               any(a.get("source")==p["media_url"] for a in r.get("assets") or [])
               for r in rows)

def scheduled_near(rows,due):
    for r in rows:
        if r.get("status") not in ("scheduled","sending"): continue
        rd=parse_due(r.get("dueAt"))
        if rd and abs((rd-due).total_seconds())<35*60:
            return True
    return False

def create(channel,cid,board,p,due,graphql,quote):
    utc=due.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00","Z")
    if channel=="facebook":
        meta="metadata:{facebook:{type:post}}"
        asset="assets:[{image:{url:"+quote(p["media_url"])+"}}]"
    elif channel=="pinterest":
        meta=("metadata:{pinterest:{boardServiceId:"+quote(board)+
              " title:"+quote(p["pinterest_title"])+" url:"+quote(p["landing_url"])+"}}")
        asset="assets:[{image:{url:"+quote(p["media_url"])+"}}]"
    else:
        meta="metadata:{tiktok:{isAiGenerated:true}}"
        asset="assets:[{video:{url:"+quote(p["media_url"])+" metadata:{thumbnailOffset:2000}}}]"
    doc=("mutation { createPost(input:{text:"+quote(p["caption"])+" channelId:"+quote(cid)+
         " schedulingType:automatic mode:customScheduled dueAt:"+quote(utc)+
         " aiAssisted:true "+meta+" "+asset+"}) { ... on PostActionSuccess { post { id status dueAt assets { mimeType source } } } ... on MutationError { message } } }")
    out=graphql(doc).get("createPost") or {}
    post=out.get("post") if isinstance(out,dict) else None
    if not isinstance(post,dict) or not post.get("id"):
        raise RuntimeError("Buffer create unconfirmed for "+p["id"]+": "+str(out.get("message",""))[:140]+"; no blind retry")
    if post.get("status")!="scheduled" or not post.get("assets"):
        raise RuntimeError("Unexpected created state for "+p["id"]+" exact Buffer ID "+str(post.get("id")))
    return post

def run(channel):
    pack=load_pack()
    now=datetime.now(PHT)
    # Finite campaign. After final due + 30 minutes, it permanently becomes read-only.
    if now>datetime(2026,9,28,21,15,tzinfo=PHT):
        print("REFINED3_EXPIRED",channel,"no writes",flush=True);return
    enabled=os.getenv("ASTRALABS_REFINED3_PUBLISH_ENABLED","false").lower()=="true"
    mod,org,cid,board,graphql,quote=resolve(channel)
    rows=history(org,cid,graphql,quote)
    candidates=sorted([p for p in pack["posts"] if p["channel"]==channel],key=due_pht)
    queued=sum(r.get("status") in ("scheduled","sending") for r in rows)
    print("REFINED3_PREFLIGHT",channel,"queued",queued,"history",len(rows),"enabled",enabled,flush=True)
    created=0
    for p in candidates:
        if created>=MAX_NEW_PER_RUN or queued>=MAX_QUEUE: break
        due=due_pht(p)
        if seen(rows,p):
            print("REFINED3_DEDUPED",channel,p["id"],flush=True);continue
        if due<now+timedelta(minutes=25):
            print("REFINED3_STALE_NO_CATCHUP",channel,p["id"],due.isoformat(),flush=True);continue
        if scheduled_near(rows,due):
            print("REFINED3_SLOT_OCCUPIED_PRESERVED",channel,p["id"],due.isoformat(),flush=True);continue
        if not media_ok(p["media_url"],channel):
            raise RuntimeError("First-party media unavailable "+p["id"])
        if not enabled:
            print("REFINED3_DRY_RUN",channel,p["id"],due.isoformat(),flush=True);continue
        latest=history(org,cid,graphql,quote)
        if (sum(r.get("status") in ("scheduled","sending") for r in latest)>=MAX_QUEUE
                or seen(latest,p) or scheduled_near(latest,due)):
            print("REFINED3_RACE_GUARD",channel,p["id"],flush=True);return
        post=create(channel,cid,board,p,due,graphql,quote)
        rows=latest+[{"id":post["id"],"status":post["status"],"dueAt":post.get("dueAt"),
                      "channelId":cid,"text":p["caption"],"assets":post.get("assets",[])}]
        queued+=1;created+=1
        print("REFINED3_BUFFER_SCHEDULED",channel,p["id"],p["app"],"PHT",due.isoformat(),
              "Buffer",post["id"],"dueAt",post.get("dueAt"),flush=True)
    pending=[p["id"] for p in candidates if not seen(rows,p) and due_pht(p)>=now+timedelta(minutes=25)]
    print("REFINED3_RUN_COMPLETE",channel,"new",created,"pending",len(pending),"queued",queued,flush=True)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--channel",choices=CHANNELS,required=True)
    args=ap.parse_args()
    try:run(args.channel)
    except Exception as exc:
        print("REFINED3_FAIL_CLOSED",args.channel,type(exc).__name__,str(exc),file=sys.stderr,flush=True)
        sys.exit(1)
