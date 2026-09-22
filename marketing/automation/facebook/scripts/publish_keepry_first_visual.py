#!/usr/bin/env python3
"""One-time Keepry Facebook visual launch with exact-brand and duplicate guards."""
import importlib.util
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
f=ROOT/"facebook"/"scripts"/"buffer_facebook.py"
spec=importlib.util.spec_from_file_location("fb_keepry_visual",f)
fb=importlib.util.module_from_spec(spec);spec.loader.exec_module(fb)
CHANNEL=fb.EXPECTED_PAGE_ID
MARKER="utm_content=fb_keepry_visual_first_20260922"
IMAGE="https://www.astralabsph.com/marketing/campaigns/facebook/K01_keepry_facebook_4x5.png"
LANDING="https://www.astralabsph.com/keepry/?utm_source=facebook&utm_medium=organic_social&utm_campaign=global_android_launch&"+MARKER
HOME="https://www.astralabsph.com/"
COPY=("Where did you save that important document? Keep your images, PDFs, expiry dates and reminders organized in Keepry, a local-first personal organizer. Start free on Android.\n\n"
      "Discover Keepry: "+LANDING+"\n"
      "AstraLabs PH: "+HOME+"\n\n"
      "#Keepry #DocumentOrganizer #LifeAdmin #AndroidApps")
def all_status_posts(org):
    query=("query { posts(first:100,input:{organizationId:"+fb.quoted(org)+
           ",filter:{status:[scheduled,sent,draft,error,sending],channelIds:["+fb.quoted(CHANNEL)+
           "]},sort:[{field:createdAt,direction:desc}]})"
           " { edges { node { id text status channelId externalLink assets { mimeType source } } }"
           " pageInfo { hasNextPage } } }")
    resp=fb.buffer_query(query).get("posts") or {}
    if not isinstance(resp.get("edges"),list) or (resp.get("pageInfo") or {}).get("hasNextPage"):
        raise RuntimeError("Incomplete Facebook history; stop to prevent duplicate")
    rows=[e["node"] for e in resp["edges"] if isinstance(e.get("node"),dict)]
    if any(x.get("channelId")!=CHANNEL for x in rows):raise RuntimeError("Facebook target mismatch")
    return rows

def image_ok():
    req=urllib.request.Request(IMAGE,headers={"Range":"bytes=0-31","User-Agent":"AstraLabs-Approved-Keepry-Proof/1.0"})
    with urllib.request.urlopen(req,timeout=20) as res:
        sig=res.read(16)
        return res.status in (200,206) and res.headers.get("Content-Type","").startswith("image/png") and sig.startswith(b"\x89PNG\r\n\x1a\n")
def main():
    if os.environ.get("ASTRALABS_APPROVED_KEEPRY_VISUAL_NOW")!="true":
        raise RuntimeError("One-shot posting not authorized by workflow")
    org=fb.verified_target()
    rows=all_status_posts(org)
    seen=[x for x in rows if MARKER in str(x.get("text") or "")]
    if seen:
        print("KEEPRY_VISUAL_ALREADY_EXISTS",[(x.get("id"),x.get("status"),x.get("externalLink")) for x in seen],flush=True)
        return
    if not image_ok():raise RuntimeError("Approved Keepry image unavailable; no Facebook write")
    if len([x for x in rows if x.get("status")=="scheduled"])>=10:
        raise RuntimeError("Facebook queue at free cap; no new post")
    rows=all_status_posts(org)
    if any(MARKER in str(x.get("text") or "") for x in rows):
        print("KEEPRY_VISUAL_RACE_DEDUPED");return
    mutation=("mutation { createPost(input:{text:"+fb.quoted(COPY)+
              " channelId:"+fb.quoted(CHANNEL)+
              " schedulingType:automatic mode:shareNow aiAssisted:true"+
              " metadata:{facebook:{type:post}}"+
              " assets:[{image:{url:"+fb.quoted(IMAGE)+"}}]})"+
              " { ... on PostActionSuccess { post { id status assets { mimeType source } } }"+
              " ... on MutationError { message } } }")
    response=fb.buffer_query(mutation).get("createPost") or {}
    post=response.get("post") if isinstance(response,dict) else None
    if not isinstance(post,dict) or not post.get("id"):
        raise RuntimeError("Facebook publication unconfirmed; inspect Buffer before retry "+str(response.get("message",""))[:150])
    if not any(str(a.get("mimeType","")).startswith("image/") for a in post.get("assets") or []):
        raise RuntimeError("Facebook accepted post without confirmed image; inspect exact post before retry")
    print("KEEPRY_VISUAL_SHARE_NOW_ACCEPTED",post["id"],post.get("status"),"official_domain",HOME,flush=True)
    time.sleep(10)
    updated=[x for x in all_status_posts(org) if x.get("id")==post["id"]]
    print("KEEPRY_VISUAL_POST_STATUS",post["id"],updated[0].get("status") if updated else "not_in_first100",
          "live_url",updated[0].get("externalLink") if updated else None,flush=True)
if __name__=="__main__":
    try:main()
    except Exception as err:
        print("FAIL_CLOSED",type(err).__name__,str(err),file=sys.stderr)
        sys.exit(1)
