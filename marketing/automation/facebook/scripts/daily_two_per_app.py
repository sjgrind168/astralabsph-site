#!/usr/bin/env python3
"""Finite, duplicate-safe AstraLabs FB editorial refiller. Up to 3 distinct posts per app/day PHT."""
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
SLOTS={"Astramate":(clock(9,30),clock(14,10),clock(19,10)),
       "Keepry":(clock(10,40),clock(15,40),clock(20,40))}
MAX_QUEUE=10
DAILY_TARGET=3
MAX_NEW_PER_RUN=2  # Limit Buffer API writes; next refill continues safely.
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
    if b.get("base_url")!=HOME or len(b.get("posts") or [])!=42:
        raise RuntimeError("Unexpected or changed 42-post approved editorial bank")
    entries=b["posts"]
    if len({i["id"] for i in entries})!=42:raise RuntimeError("Duplicate ID in editorial bank")
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
    # Choose real remaining editorial slots, never compress missed morning posts into evening.
    for planned in SLOTS[app]:
        proposed=datetime.combine(day,planned,tzinfo=PHT)
        if proposed<now+timedelta(minutes=25):continue
        if any((due:=utcdate(p.get("dueAt"))) and p.get("status") in ("scheduled","sending")
               and abs((due-proposed).total_seconds())<45*60 for p in rows):
            continue
        return proposed
    # One non-spam late recovery slot on the current launch day when afternoon
    # API throttling prevented the planned slot; preserve at least 45m from other queued posts.
    if day==now.date() and now.hour>=18:
        base=max(now+timedelta(minutes=35),
                 datetime.combine(day,SLOTS[app][-1],tzinfo=PHT)+timedelta(minutes=25))
        candidate=base.replace(second=0,microsecond=0)
        candidate+=timedelta(minutes=(15-base.minute%15)%15)
        if candidate<=base:candidate+=timedelta(minutes=15)
        for _ in range(4):
            if candidate.date()!=day or candidate.hour>=23:break
            if not any((due:=utcdate(p.get("dueAt"))) and p.get("status") in ("scheduled","sending")
                       and abs((due-candidate).total_seconds())<45*60 for p in rows):
                return candidate
            candidate+=timedelta(minutes=50)
    return None
def build_post(item):
    app=item["app"]
    image=MEDIA+item["creative"]+"_"+app.lower()+"_facebook_4x5.png"
    landing=(HOME+"?utm_source=facebook&"
             "utm_medium=organic_social&utm_campaign=global_android_launch&utm_content="+item["id"]+
             "&app="+app.lower())
    if app=="Astramate":
        offer={
            "A03":"Try Astramate Free on Android. Need additional maritime calculation tools? Explore the optional one-time lifetime Premium upgrade.",
            "A04":"Start with the free Android tools. When your calculations call for more supported tools, explore the optional one-time Astramate Premium upgrade.",
            "A02":"Try Astramate Free on Android. Unlock the wider supported toolkit with optional one-time lifetime Premium when you need it."
        }[item["creative"]]
        tags="\n\n#Astramate #Seafarers #CargoCalculations" if item["creative"]=="A03" else "\n\n#Astramate #Seafarers #MaritimeToolkit"
        call="Want a clearer view of your own calculations? "
    else:
        offer={
            "K02":"Try Keepry Free on Android. Need expanded reminders and supported recurring options? Explore the optional one-time Plus upgrade.",
            "K03":"Start with Keepry Free. More documents to organize? Optional one-time Plus expands supported Vault capacity.",
            "K04":"Start with Keepry Free. If your household needs more records, People profiles and Life Admin allowances, explore optional one-time Plus."
        }[item["creative"]]
        tags="\n\n#Keepry #DocumentOrganizer #LifeAdmin"
        call="Ready to organize your own records? "
    caption=(item["copy"]+"\n\n"+offer+"\n\n"+call+
             "Explore "+app+" and our other apps at AstraLabs PH: "+landing+
             "\nOfficial website: "+HOME+tags)
    return image,caption
def queue_one(item,when,org,rows):
    # Reuse the verified per-run snapshot to avoid a burst of wasteful Buffer reads.
    if any("utm_content="+item["id"] in (r.get("text") or "") for r in rows):
        print("ALREADY_USED",item["id"],flush=True);return False
    if sum(r.get("status")=="scheduled" for r in rows)>=MAX_QUEUE:
        print("BUFFER_FREE_QUEUE_FULL",sum(r.get("status")=="scheduled" for r in rows),flush=True);return False
    day=when.date()
    if sum(on_day(r,day) and in_scope(r,item["app"]) and r.get("status") in ("sent","scheduled","sending") for r in rows)>=DAILY_TARGET:
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
    if sum(on_day(r,day) and in_scope(r,item["app"]) and r.get("status") in ("sent","scheduled","sending") for r in rows)>=DAILY_TARGET:
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
    rows.append({"id":post["id"],"status":post["status"],"dueAt":post["dueAt"],
                 "text":caption,"assets":post["assets"],"channelId":fb.EXPECTED_PAGE_ID})
    print("EDITORIAL_SCHEDULED",item["id"],item["app"],"PHT",when.isoformat(),
          "Buffer",post["id"],"dueAt",post.get("dueAt"),flush=True)
    return True
def main():
    org=fb.verified_target()
    bank=candidates()
    now=datetime.now(PHT)
    rows=full_history(org) # One complete verified snapshot, updated only on confirmed mutation.
    created=0
    # Preserve existing sent/scheduled posts. Refill today, then at most one future day.
    for offset in (0,1):
        day=(now+timedelta(days=offset)).date()
        for app in ("Astramate","Keepry"):
            for ordinal in range(DAILY_TARGET):
                if created>=MAX_NEW_PER_RUN:
                    print("SAFE_BATCH_LIMIT: future scheduled refill continues",flush=True)
                    return
                if sum(on_day(r,day) and in_scope(r,app) and r.get("status") in ("sent","scheduled","sending") for r in rows)>=DAILY_TARGET:
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
                # Three DAILY placements must use different verified artwork for the same app.
                fresh=[i for i in options if not any(i["creative"] in u for u in prior_creatives)]
                if not fresh:
                    print("DAILY_CREATIVE_VARIATION_EXHAUSTED",app,day.isoformat(),"no repeated artwork forced",flush=True)
                    break
                fresh.sort(key=lambda i:i["id"])
                item=fresh[0]
                when=pick_slot(day,app,ordinal,rows,now)
                if not when:
                    print("NO_SAFE_TIME_SLOT",app,day.isoformat(),flush=True)
                    continue
                created+=bool(queue_one(item,when,org,rows))
    print("DAILY_EDITORIAL_COMPLETE","created",created,"main_domain",HOME,"PHT",now.isoformat(),flush=True)
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("DAILY_EDITORIAL_FAIL_CLOSED",type(exc).__name__,str(exc),file=sys.stderr)
        sys.exit(1)
