#!/usr/bin/env python3
"""One controlled retry after exact diagnosed TikTok low-FPS rejection; NEVER retry an unknown error."""
import importlib.util
import json
import os
import time
import urllib.request
from pathlib import Path

BASE=Path(__file__).resolve().parent
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,str(path))
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj)
    return obj
tt=load(BASE.parent/"tiktok"/"scripts"/"buffer_tiktok.py","tt_v2")
live=load(BASE/"one_time_live_launch.py","live_v2")
FAILED_ID="6ab1f12dffe5c8afb1291a9b"
NEW_VIDEO="https://www.astralabsph.com/marketing/videos/v2/astramate_v2_voice_music_30fps_FINAL.mp4"
MARKER="#MaritimeToolkitV2"

def main():
    org,ch=tt.resolve_tiktok()
    old=tt.gql("query { post(input:{id:"+tt.q(FAILED_ID)+
               "}) { id channelId status error { message } externalLink } }").get("post") or {}
    message=str((old.get("error") or {}).get("message") or "").lower()
    if old.get("id")!=FAILED_ID or old.get("channelId")!=ch or old.get("status")!="error" or "frame rate" not in message:
        print("DO_NOT_RETRY: original V2 no longer has the exact known frame-rate error")
        return
    rows=live.history(tt.gql,org,ch)
    if any(MARKER in str(row.get("text") or "") for row in rows):
        print("TIKTOK_FIXED_ALREADY_CREATED: no repeat",[(r["id"],r["status"]) for r in rows if MARKER in str(r.get("text") or "")])
        return
    if any(r.get("status") in ("scheduled","sending") for r in rows):
        print("TIKTOK_QUEUE_BUSY: no new post")
        return
    if not tt.verify_media(NEW_VIDEO):raise RuntimeError("New 30fps video URL not a public valid MP4")
    text=tt.approved()[0]["text"]+" "+MARKER
    if len(text)>150:raise RuntimeError("TikTok caption >150")
    if os.getenv("ASTRALABS_FIXED_TIKTOK_LIVE")!="true":
        print("DRY_RUN_FIXED_VIDEO",NEW_VIDEO);return
    if any(MARKER in str(r.get("text") or "") for r in live.history(tt.gql,org,ch)):
        print("RACE_STOP: already exists");return
    mutation=("mutation { createPost(input:{text:"+tt.q(text)+
              " channelId:"+tt.q(ch)+
              " schedulingType:automatic mode:shareNow aiAssisted:true"+
              " metadata:{tiktok:{isAiGenerated:true}}"+
              " assets:[{video:{url:"+tt.q(NEW_VIDEO)+
              " metadata:{thumbnailOffset:2000}}}]})"+
              " { ... on PostActionSuccess { post { id status schedulingType assets { mimeType source } } }"+
              " ... on MutationError { message } } }")
    result=tt.gql(mutation).get("createPost") or {}
    p=result.get("post") if isinstance(result,dict) else None
    if not p or not p.get("id"):
        raise RuntimeError("Corrected first post unconfirmed; do not automatically retry: "+str(result.get("message","unknown"))[:120])
    print("TIKTOK_30FPS_ACCEPTED",p["id"],"status",p.get("status"),"mode",p.get("schedulingType"),
          "assets",[(a.get("mimeType"),a.get("source")) for a in p.get("assets") or []])
    time.sleep(15)
    audit=tt.gql("query { post(input:{id:"+tt.q(p["id"])+
                 "}) { id status externalLink error { message supportUrl } } }").get("post") or {}
    print("TIKTOK_30FPS_STATUS",audit.get("id"),audit.get("status"),
          "url",audit.get("externalLink"),"error",json.dumps(audit.get("error")))
    if audit.get("status")=="error":
        raise RuntimeError("Corrected TikTok video failed; stop further attempts and inspect error")
if __name__=="__main__":main()
