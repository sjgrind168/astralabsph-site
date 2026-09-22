#!/usr/bin/env python3
"""Finite, duplicate-safe AstraLabs FB editorial refiller. 2 distinct posts per app/day PHT."""
import importlib.util
import json
import os
import sys
import urllib.request
from datetime import datetime,timedelta,timezone,time as clock
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("fb_daily",ROOT/"buffer_facebook.py")
fb=importlib.util.module_from_spec(spec);spec.loader.exec_module(fb)
BANK=ROOT/"daily_two_per_app_content.json"
PHT=ZoneInfo("Asia/Manila")
MEDIA="https://www.astralabsph.com/marketing/campaigns/facebook/"
HOME="https://www.astralabsph.com/"
SLOTS={"Astramate":(clock(9,30),clock(18,30)),
       "Keepry":(clock(12,30),clock(20,30))}
MAX_QUEUE=10
DENY=("colregs","imdg","imsbc","tidal","tide calculator","cloud sync")
def full_history(org):
    q=('query { posts(first:100,input:{organizationId:'+fb.quoted(org)+
       ',filter:{status:[scheduled,sent,draft,error,sending],channelIds:['+fb.quoted(fb.EXPECTED_PAGE_ID)+
       ']},sort:[{field:createdAt,direction:desc}]})'
       ' { edges { node { id text status dueAt channelId assets { mimeType source } } }'
       ' pageInfo { hasNextPage } } }')
    obj=fb.buffer_query(q).get("posts") or {}
    if not isinstance(obj.get("edges"),list) or (obj.get("pageInfo") or {}).get("hasNextPage"):
        raise RuntimeError("Buffer Facebook post history incomplete: never assume unseen post unused")
    rows=[edge["node"] for edge in obj["edges"] if isinstance(edge.get("node"),dict)]
    if any(x.get("channelId")!=fb.EXPECTED_PAGE_ID for x in rows):
        raise RuntimeError("Cross-channel Facebook results, stop")
    return rows
def utcdate(text):
    if not text:return None
    try:return datetime.fromisoformat(text.replace("Z","+00:00")).astimezone(PHT)
    except (TypeError,ValueError):return None
def on_day(p,day):
    dt=utcdate(p.get("dueAt"))
    return bool(dt and dt.date()==day)
def in_scope(p,app):
    text=str(p.get("text") or "").lower()
    return app.lower() in text and ("keepry" not in text if app=="Astramate" else "astramate" not in text)
def candidates():
    b=json.loads(BANK.read_text(encoding="utf-8"))
    if b.get("base_url")!=HOME or len(b.get("posts") or [])!=28:
        raise RuntimeError("Unexpected or changed 28-post approved editorial bank")
    entries=b["posts"]
    if len({i["id"] for i in entries})!=28:raise RuntimeError("Duplicate ID in editorial bank")
    for i in entries:
        if (i.get("app") not in SLOTS or i.get("creative") not in (("A02","A03","A04") if i["app"]=="Astramate" else ("K02","K03","K04"))
            or not i["id"].startswith("daily_"+("a" if i["app"]=="Astramate" else "k")+"_")
            or len(i["copy"])<100 or any(token in i["copy"].lower() for token in DENY)
            or (i["app"]=="Astramate" and __import__("re").search(r"\beta\b",i["copy"],__import__("re").I))
            or "guaranteed" in i["copy"].lower() or "replace" in i["copy"].lower() and "never" not in i["copy"].lower()):
            raise RuntimeError("Unapproved marketing claim or asset detected in "+i.get("id","?"))
    return entries
def public_png(url):
    req=urllib.request.Request(url,headers={"Range":"bytes=0-15","User-Agent":"AstraLabs-Editorial/1.0"})
    try:
        with urllib.request.urlopen(req,timeout=20) as resp:
            return resp.status in (200,206) and resp.headers.get("Content-Type","").startswith("image/png") and resp.read(8)==b"\x89PNG\r\n\x1a\n"
    except Exception:
        return False
def pick_slot(day,app,ordinal,rows,now):
    first=SLOTS[app][ordinal]
    start=datetime.combine(day,first,tzinfo=PHT)
    for hour in range(0,5):
        proposed=start+timedelta(minutes=55*hour)
        if proposed.date()!=day or proposed.hour>=23:break
        if proposed<now+timedelta(minutes=35):continue
        if any((due:=utcdate(p.get("dueAt"))) and p.get("status") in ("scheduled","sending")
               and abs((due-proposed).total_seconds())<45*60 for p in rows):
            continue
        return proposed
    return None
def build_post(item):
    app=item["app"]
    image=MEDIA+item["creative"]+"_"+app.lower()+"_facebook_4x5.png"
    landing=("https://www.astralabsph.com/"+app.lower()+"/?utm_source=facebook&"
             "utm_medium=organic_social&utm_campaign=global_android_launch&utm_content="+item["id"])
    caption=(item["copy"]+"\n\nExplore "+app+": "+landing+
             "\nAstraLabs PH: "+HOME+
             "\nAndroid available now. iOS coming soon (subject to review)."+
             ("\n\n#Astramate #Seafarers #MaritimeCalculations" if app=="Astramate"
              else "\n\n#Keepry #LifeAdmin #DocumentOrganizer"))
    return image,caption
def queue_one(item,when,org):
    rows=full_history(org)
    if any("utm_content="+item["id"] in (r.get("text") or "") for r in rows):
        print("ALREADY_USED",item["id"],flush=True);return False
    if sum(r.get("status")=="scheduled" for r in rows)>=MAX_QUEUE:
        print("BUFFER_FREE_QUEUE_FULL",sum(r.get("status")=="scheduled" for r in rows),flush=True);return False
    day=when.date()
    if sum(on_day(r,day) and in_scope(r,item["app"]) and r.get("status") in ("sent","scheduled","sending") for r in rows)>=2:
        print("APP_DAY_ALREADY_FULL",item["app"],day.isoformat(),flush=True);return False
    media,caption=build_post(item)
    if not public_png(media):raise RuntimeError("Approved image not available: "+media)
    if os.getenv("ASTRALABS_DAILY_FB_PUBLISH_ENABLED","false").lower()!="true":
        print("DRY_RUN",item["id"],when.isoformat(),flush=True);return False
    rows=full_history(org)
    if any("utm_content="+item["id"] in (r.get("text") or "") for r in rows):
        print("RACE_DEDUPED",item["id"],flush=True);return False
    if sum(r.get("status")=="scheduled" for r in rows)>=MAX_QUEUE:
        print("QUEUE_FILLED_CONCURRENTLY",flush=True);return False
    if sum(on_day(r,day) and in_scope(r,item["app"]) and r.get("status") in ("sent","scheduled","sending") for r in rows)>=2:
        print("APP_DAY_FILLED_CONCURRENTLY",item["app"],flush=True);return False
    utc=when.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00","Z")
    graph=("mutation { createPost(input:{text:"+fb.quoted(caption)+
           " channelId:"+fb.quoted(fb.EXPECTED_PAGE_ID)+
           " schedulingType:automatic mode:customScheduled dueAt:"+fb.quoted(utc)+
           " aiAssisted:true metadata:{facebook:{type:post}}"+
           " assets:[{image:{url:"+fb.quoted(media)+"}}]})"+
           " { ... on PostActionSuccess { post { id status dueAt assets { mimeType source } } }"+
           " ... on MutationError { message } } }")
    response=fb.buffer_query(graph).get("createPost") or {}
    post=response.get("post") if isinstance(response,dict) else None
    if not isinstance(post,dict) or not post.get("id"):
        raise RuntimeError("Unconfirmed Buffer createPost for "+item["id"]+
                           ": "+str(response.get("message",""))[:130]+"; do not retry blindly")
    if post.get("status")!="scheduled" or not any(str(a.get("mimeType","")).startswith("image/") for a in (post.get("assets") or [])):
        raise RuntimeError("Created post missing scheduled state or image; reconcile before retry "+str(post["id"]))
    print("EDITORIAL_SCHEDULED",item["id"],item["app"],"PHT",when.isoformat(),
          "Buffer",post["id"],"dueAt",post.get("dueAt"),flush=True)
    return True
def main():
    org=fb.verified_target()
    bank=candidates()
    now=datetime.now(PHT)
    created=0
    # Keep at most one future day prefilled; next daily run refills after prior posts leave free slots.
    for offset in (0,1):
        day=(now+timedelta(days=offset)).date()
        for app in ("Astramate","Keepry"):
            for ordinal in (0,1):
                rows=full_history(org)
                if sum(on_day(r,day) and in_scope(r,app) and r.get("status") in ("sent","scheduled","sending") for r in rows)>=2:
                    print("DAILY_TARGET_ALREADY_MET",app,day.isoformat(),flush=True)
                    break
                if sum(r.get("status")=="scheduled" for r in rows)>=MAX_QUEUE:
                    print("BUFFER_FREE_CAP_REACHED; no posts removed or replaced",flush=True)
                    return
                seen={item["id"] for item in bank if any("utm_content="+item["id"] in str(r.get("text") or "") for r in rows)}
                prior_creatives={str(a.get("source") or "") for r in rows if r.get("status") in ("sent","scheduled") and on_day(r,day) and in_scope(r,app) for a in r.get("assets") or []}
                options=[i for i in bank if i["app"]==app and i["id"] not in seen]
                if not options:
                    print("APPROVED_CONTENT_EXHAUSTED",app,"manual creative refill required",flush=True)
                    break
                # Avoid the same picture used in another post for this app on the same date.
                options.sort(key=lambda i:(any(i["creative"] in u for u in prior_creatives),i["id"]))
                item=options[0]
                when=pick_slot(day,app,ordinal,rows,now)
                if not when:
                    print("NO_SAFE_TIME_SLOT",app,day.isoformat(),flush=True)
                    continue
                created+=bool(queue_one(item,when,org))
    print("DAILY_EDITORIAL_COMPLETE","created",created,"main_domain",HOME,"PHT",now.isoformat(),flush=True)
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("DAILY_EDITORIAL_FAIL_CLOSED",type(exc).__name__,str(exc),file=sys.stderr)
        sys.exit(1)
