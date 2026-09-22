#!/usr/bin/env python3
"""Owner-requested Keepry first TikTok release: move the single existing 30fps scheduled V2 post to now, never create duplicate."""
import importlib.util,json,re,sys,urllib.error
from datetime import datetime,timezone,timedelta
from pathlib import Path

HERE=Path(__file__).resolve().parent
f=HERE/"buffer_tiktok.py"
spec=importlib.util.spec_from_file_location("tt_keepry_release",f)
tt=importlib.util.module_from_spec(spec);spec.loader.exec_module(tt)
POST_ID="6ab1f356ffe5c8afb129534f"
MEDIA="https://www.astralabsph.com/marketing/videos/v2/keepry_v2_voice_music_30fps_FINAL.mp4"
CAPTION=("Your important PDF is saved. But where is its expiry date? "
         "Keep documents and reminders together. Try Keepry Free: astralabsph.com #Keepry")
def history(org,channel):
    q=('query { posts(first:100,input:{organizationId:'+tt.q(org)+
       ',filter:{status:[scheduled,sent,draft,error,sending],channelIds:['+tt.q(channel)+
       ']},sort:[{field:createdAt,direction:desc}]}) '
       '{ edges { node { id text status channelId dueAt externalLink assets { mimeType source } } } pageInfo { hasNextPage } } }')
    node=tt.gql(q).get("posts") or {}
    if not isinstance(node.get("edges"),list) or (node.get("pageInfo") or {}).get("hasNextPage"):
        raise RuntimeError("Incomplete TikTok history, no publication")
    result=[v["node"] for v in node["edges"] if isinstance(v.get("node"),dict)]
    if any(v.get("channelId")!=channel for v in result):raise RuntimeError("Channel mismatch")
    return result
def main():
    if len(CAPTION)>150 or "astralabsph.com/" in CAPTION or not tt.verify_media(MEDIA):
        raise RuntimeError("Official root CTA, media or caption verification failed")
    org,channel=tt.resolve_tiktok()
    rows=history(org,channel)
    target=[p for p in rows if p.get("id")==POST_ID]
    if len(target)!=1:raise RuntimeError("Expected scheduled original Keepry video missing; no duplicate created")
    p=target[0]
    if p.get("status")=="sent":
        print("KEEPRY_ALREADY_SENT",p["id"],p.get("externalLink"),flush=True);return
    if p.get("status")!="scheduled":raise RuntimeError("Keepry original is not in scheduled state "+str(p.get("status")))
    if len(p.get("assets") or [])!=1 or not (p["assets"][0].get("source") or "").startswith(MEDIA):
        raise RuntimeError("Scheduled Keepry video media changed; hold")
    due=p.get("dueAt")
    if not due:raise RuntimeError("Missing original dueAt")
    try:dt=datetime.fromisoformat(due.replace("Z","+00:00"))
    except ValueError:raise RuntimeError("Invalid dueAt")
    if not (datetime.now(timezone.utc)<dt<datetime.now(timezone.utc)+timedelta(days=10)):
        raise RuntimeError("Unexpected post schedule, hold before edit")
    recent=[v for v in rows if v["id"]!=POST_ID and
            v.get("status") in ("sent","sending") and
            ("keepry" in (v.get("text") or "").lower()) and
            (not v.get("dueAt") or datetime.fromisoformat(v["dueAt"].replace("Z","+00:00"))>datetime.now(timezone.utc)-timedelta(days=1))]
    if recent:
        print("KEEPRY_ALREADY_POSTED_RECENTLY",[(v["id"],v.get("status"),v.get("externalLink")) for v in recent],flush=True)
        return
    # Fresh read just before changing exact existing post. Omit assets to preserve approved 30fps file.
    latest=history(org,channel)
    found=[v for v in latest if v.get("id")==POST_ID]
    if len(found)!=1 or found[0].get("status")!="scheduled" or found[0].get("dueAt")!=due or found[0].get("assets")!=p.get("assets"):
        raise RuntimeError("Original Keepry post changed while checking; reconcile")
    q=('mutation { editPost(input:{id:'+tt.q(POST_ID)+
       ' text:'+tt.q(CAPTION)+' mode:shareNow aiAssisted:true })'+
       ' { ... on PostActionSuccess { post { id text status dueAt externalLink assets { mimeType source } } }'+
       ' ... on MutationError { message } } }')
    result=tt.gql(q).get("editPost") or {}
    posted=result.get("post") if isinstance(result,dict) else None
    if not isinstance(posted,dict) or posted.get("id")!=POST_ID:
        raise RuntimeError("Buffer edit unconfirmed: "+str(result.get("message","unknown"))[:140]+"; no automatic retries")
    print("KEEPRY_EXISTING_VIDEO_PUBLISH_NOW_ACCEPTED",posted["id"],posted.get("status"),
          "dueAt",posted.get("dueAt"),"externalLink",posted.get("externalLink"),
          "rootOnly",("astralabsph.com/" not in posted.get("text","")),flush=True)
    if posted.get("text")!=CAPTION:raise RuntimeError("Published Keepry caption does not match approved root-only text")
    if not posted.get("assets") or not str(posted["assets"][0].get("mimeType","")).startswith("video/"):
        raise RuntimeError("Unexpected media state after moving original video; inspect before further action")
    # Read exact post status once, not blind second publication.
    check=tt.gql('query { post(input:{id:'+tt.q(POST_ID)+
                 '}) { id status channelId externalLink sharedNow dueAt text assets { mimeType source } error { message } } }').get("post") or {}
    print("KEEPRY_NATIVE_PUBLICATION_STATUS",check.get("id"),check.get("status"),
          "externalLink",check.get("externalLink"),"sharedNow",check.get("sharedNow"),
          "error",str((check.get("error") or {}).get("message") or "")[:130],flush=True)
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("KEEPRY_RELEASE_FAIL_CLOSED",type(exc).__name__,str(exc),file=sys.stderr)
        sys.exit(1)
