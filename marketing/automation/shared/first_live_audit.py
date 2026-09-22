#!/usr/bin/env python3
"""AstraLabs three-channel preflight. No writes. Fail closed on ambiguous accounts."""
import importlib.util, json, urllib.request
from pathlib import Path
BASE=Path(__file__).resolve().parent
def module(name):
    p=BASE.parent/name/"scripts"/("buffer_"+name+".py")
    spec=importlib.util.spec_from_file_location(name,str(p))
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

def main():
    fb=module("facebook"); pn=module("pinterest"); tt=module("tiktok")
    org=fb.verified_target()
    posts=fb.get_existing(org)
    scheduled=[x for x in posts if x.get("status")=="scheduled"]
    print("FACEBOOK_PAGE_VERIFIED; scheduled",len(scheduled),"sent",sum(x.get("status")=="sent" for x in posts))
    for p in scheduled[:7]:
        print("FB_QUEUED",p.get("id"),p.get("dueAt"),"campaign",str(p.get("text") or "").split("utm_content=")[-1][:12])
    porg,bid=pn.target()
    if porg != org: raise RuntimeError("Different Pinterest organization")
    print("PINTEREST_APP_BOARD", "READY" if bid else "NOT_IN_BUFFER")
    if bid:
        pinposts=pn.get_existing(org)
        print("PINTEREST_SCHEDULED",sum(x.get("status")=="scheduled" for x in pinposts))
    torg,tc=tt.resolve_tiktok()
    if torg != org: raise RuntimeError("Different TikTok organization")
    posts=tt.current_posts(org,tc)
    print("TIKTOK_SCHEDULED",sum(x.get("status")=="scheduled" for x in posts),
          "sent",sum(x.get("status")=="sent" for x in posts))
    for x in posts:
        if x.get("status")=="scheduled":
            print("TT_QUEUED",x["id"],x.get("dueAt"),"mode",x.get("schedulingType"))
    q=("query { posts(first:100,input:{organizationId:"+tt.q(org)+
       ",filter:{status:[draft],channelIds:["+tt.q(tc)+"]}})"+
       " { edges { node { id text status channelId } } pageInfo { hasNextPage } } }")
    obj=tt.gql(q).get("posts") or {}
    if (obj.get("pageInfo") or {}).get("hasNextPage"): raise RuntimeError("Draft pagination")
    draft=[e["node"] for e in obj.get("edges") or [] if isinstance(e.get("node"),dict)]
    print("TIKTOK_DRAFTS",len(draft),
          "silent_original_preserved",any(x.get("id")=="6ab1948d7a0ab2bcc80c7f5f" for x in draft))
    for app in ("astramate","keepry"):
        url="https://www.astralabsph.com/marketing/previews/"+app+"_v2_neural_voice_music_PREVIEW.mp4"
        print("V2_MEDIA",app,tt.verify_media(url))
    print("READ_ONLY_AUDIT_COMPLETE")
if __name__=="__main__": main()
