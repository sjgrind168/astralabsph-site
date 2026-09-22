#!/usr/bin/env python3
"""One-shot Astramate organic live tests. Never modifies scheduled FB posts or legacy media."""
import importlib.util
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

BASE=Path(__file__).resolve().parent
ALL_STATUSES="[scheduled,sent,draft,error,sending]"

def mod(name):
    p=BASE.parent/name/"scripts"/("buffer_"+name+".py")
    spec=importlib.util.spec_from_file_location("channel_"+name,p)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def history(api, org, channel):
    q=('query { posts(first:100,input:{organizationId:'+json.dumps(org)+
       ',filter:{status:'+ALL_STATUSES+',channelIds:['+json.dumps(channel)+
       ']},sort:[{field:createdAt,direction:desc}]})'
       ' { edges { node { id text status dueAt channelId assets { mimeType source } } }'
       ' pageInfo { hasNextPage } } }')
    node=api(q).get("posts") or {}
    if not isinstance(node.get("edges"),list) or (node.get("pageInfo") or {}).get("hasNextPage"):
        raise RuntimeError("Incomplete channel history: do not post")
    rows=[e.get("node") for e in node["edges"] if isinstance(e.get("node"),dict)]
    if any(r.get("channelId")!=channel for r in rows):
        raise RuntimeError("Cross-channel history: do not post")
    return rows

def check_image(url):
    req=urllib.request.Request(url,headers={"Range":"bytes=0-31","User-Agent":"AstraLabs-First-Publish/1.0"})
    with urllib.request.urlopen(req,timeout=20) as response:
        head=response.read(16)
        return response.status in (200,206) and response.headers.get("Content-Type","").startswith("image/png") and head.startswith(b"\x89PNG\r\n\x1a\n")

def post_fb():
    fb=mod("facebook")
    org=fb.verified_target()
    channel=fb.EXPECTED_PAGE_ID
    marker="utm_content=fb_visual_a01_20260922"
    url="https://www.astralabsph.com/marketing/campaigns/facebook/A01_astramate_facebook_4x5.png"
    link="https://www.astralabsph.com/astramate/?utm_source=facebook&utm_medium=organic_social&utm_campaign=global_android_launch&"+marker
    text=("Still calculating ETA from scattered notes? Astramate brings voyage, compass and cargo tools together for seafarers and maritime students. Explore the free Android app on Google Play: "+link+
          "\n\n#Astramate #Seafarers #MaritimeCalculations")
    rows=history(fb.buffer_query,org,channel)
    if any(marker in str(p.get("text") or "") for p in rows):
        print("FACEBOOK_ALREADY_CREATED: unique test marker exists; no repeat.")
        return
    if sum(p.get("status")=="scheduled" for p in rows)>=10:
        print("FACEBOOK_QUEUE_FULL: existing posts preserved; no new post")
        return
    if not check_image(url): raise RuntimeError("Facebook approved media URL invalid")
    if os.getenv("ASTRALABS_ONE_SHOT_FB")!="true":
        print("FB_DRY_RUN: image and account verified, no post created")
        return
    # Last read immediately before a shareNow write.
    if any(marker in str(p.get("text") or "") for p in history(fb.buffer_query,org,channel)):
        print("FACEBOOK_RACE_DEDUPED");return
    graph=("mutation { createPost(input:{text:"+fb.quoted(text)+
         " channelId:"+fb.quoted(channel)+
         " schedulingType:automatic mode:shareNow aiAssisted:true"+
         " metadata:{facebook:{type:post}}"+
         " assets:[{image:{url:"+fb.quoted(url)+"}}]})"+
         " { ... on PostActionSuccess { post { id status dueAt assets { mimeType source } } }"+
         " ... on MutationError { message } } }")
    result=fb.buffer_query(graph).get("createPost") or {}
    p=result.get("post") if isinstance(result,dict) else None
    if not p or not p.get("id"):
        raise RuntimeError("FB creation unconfirmed; inspect Buffer before retry: "+str(result.get("message","unknown"))[:150])
    print("FB_SHARE_NOW_ACCEPTED",p["id"],"status",p.get("status"),"image_assets",len(p.get("assets") or []))
    time.sleep(10)
    matched=[x for x in history(fb.buffer_query,org,channel) if x.get("id")==p["id"]]
    print("FB_POST_VERIFY",p["id"],"status",matched[0].get("status") if matched else "not_in_first100")

def post_pinterest():
    pn=mod("pinterest")
    org,board=pn.target()
    if not board:
        print("PINTEREST_NOT_POSTED: approved Apps board absent from authorized Buffer Pinterest metadata; PIREVO Finds protected.")
        return
    rows=history(pn.query,org,pn.CHANNEL_ID)
    item=pn.approved()[0]
    marker="utm_content="+item["id"]
    if any(marker in str(p.get("text") or "") for p in rows):
        print("PINTEREST_ALREADY_CREATED: board test marker exists; no repeat")
        return
    if sum(p.get("status")=="scheduled" for p in rows)>=pn.TARGET:
        print("PINTEREST_QUEUE_FULL: preserved")
        return
    pn.verify_public_image(item["imageUrl"])
    if os.getenv("ASTRALABS_ONE_SHOT_PIN")!="true":
        print("PIN_DRY_RUN: verified board and media");return
    if any(marker in str(p.get("text") or "") for p in history(pn.query,org,pn.CHANNEL_ID)):
        print("PINTEREST_RACE_DEDUPED");return
    # Inject source marker in text so Buffer history can prevent duplicate re-posting.
    caption=item["description"]+"\nGet Astramate: "+item["landingUrl"]
    graph=("mutation { createPost(input:{text:"+pn.quoted(caption)+
           " channelId:"+pn.quoted(pn.CHANNEL_ID)+
           " schedulingType:automatic mode:shareNow aiAssisted:true"+
           " assets:[{image:{url:"+pn.quoted(item["imageUrl"])+"}}]"+
           " metadata:{pinterest:{boardServiceId:"+pn.quoted(board)+
           " title:"+pn.quoted(item["title"])+" url:"+pn.quoted(item["landingUrl"])+"}}})"+
           " { ... on PostActionSuccess { post { id status dueAt } }"+
           " ... on MutationError { message } } }")
    response=pn.query(graph).get("createPost") or {}
    p=response.get("post") if isinstance(response,dict) else None
    if not p or not p.get("id"):
        raise RuntimeError("Pinterest creation unconfirmed; reconcile Buffer: "+str(response.get("message","unknown"))[:160])
    print("PIN_SHARE_NOW_ACCEPTED",p["id"],"status",p.get("status"),"board",pn.BOARD_NAME)

def post_tiktok():
    tt=mod("tiktok")
    org,channel=tt.resolve_tiktok()
    base="https://www.astralabsph.com/marketing/previews/"
    url=base+"astramate_v2_neural_voice_music_PREVIEW.mp4"
    # Unique V2 marker survives queue/draft/sent/error history, prevents retry duplication.
    marker="#AstramateV2"
    item=tt.approved()[0]
    txt=item["text"]+" "+marker
    if len(txt)>150:raise RuntimeError("TikTok caption longer than approved limit")
    rows=history(tt.gql,org,channel)
    if any(marker in str(p.get("text") or "") for p in rows):
        print("TIKTOK_V2_ALREADY_CREATED: unique marker exists; no repeat")
        return
    if sum(p.get("status") in ("scheduled","sending") for p in rows)>=tt.QUEUE_LIMIT:
        print("TIKTOK_QUEUE_BUSY: preserving existing queue");return
    if not tt.verify_media(url):raise RuntimeError("V2 AI voice MP4 not publicly accessible")
    if os.getenv("ASTRALABS_ONE_SHOT_TT")!="true":
        print("TT_DRY_RUN: V2 voice and account verified");return
    if any(marker in str(p.get("text") or "") for p in history(tt.gql,org,channel)):
        print("TIKTOK_RACE_DEDUPED");return
    graph=("mutation { createPost(input:{text:"+tt.q(txt)+
           " channelId:"+tt.q(channel)+
           " schedulingType:automatic mode:shareNow aiAssisted:true"+
           " metadata:{tiktok:{isAiGenerated:true}}"+
           " assets:[{video:{url:"+tt.q(url)+
           " metadata:{thumbnailOffset:2000}}}]})"+
           " { ... on PostActionSuccess { post { id status dueAt schedulingType assets { mimeType source } } }"+
           " ... on MutationError { message } } }")
    response=tt.gql(graph).get("createPost") or {}
    p=response.get("post") if isinstance(response,dict) else None
    if not p or not p.get("id"):
        raise RuntimeError("TikTok creation unconfirmed; inspect Buffer before retry: "+str(response.get("message","unknown"))[:160])
    print("TIKTOK_V2_SHARE_NOW_ACCEPTED",p["id"],"status",p.get("status"),
          "mode",p.get("schedulingType"),"attached_videos",
          sum(str(a.get("mimeType","")).startswith("video/") for a in p.get("assets") or []))
    time.sleep(10)
    matches=[x for x in history(tt.gql,org,channel) if x.get("id")==p["id"]]
    print("TIKTOK_V2_POST_VERIFY",p["id"],"status",matches[0].get("status") if matches else "not_in_first100")

if __name__=="__main__":
    mode=os.getenv("ASTRALABS_TEST_CHANNEL")
    if mode=="facebook":post_fb()
    elif mode=="pinterest":post_pinterest()
    elif mode=="tiktok":post_tiktok()
    else:raise RuntimeError("Explicit single-channel test mode required")
