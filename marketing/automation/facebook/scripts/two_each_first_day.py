#!/usr/bin/env python3
"""Two unique extra first-day FB visuals, one each app. Never repeats or deletes existing queue."""
import importlib.util,json,os,sys,time,urllib.request
from pathlib import Path
p=Path(__file__).resolve().with_name("buffer_facebook.py")
spec=importlib.util.spec_from_file_location("af",p);fb=importlib.util.module_from_spec(spec);spec.loader.exec_module(fb)
ASSETS="https://www.astralabsph.com/marketing/campaigns/facebook/"
HOME="https://www.astralabsph.com/"
CAMPAIGNS=[
("Astramate","A03_astramate_facebook_4x5.png","fb_visual_cargo_firstday_20260922",
 "Cargo weight, hold volume and stowage factor all matter when you are reviewing a loading calculation. Astramate brings cargo-weight, cargo-volume, stowage-factor and hold-utilization tools together, with visible calculation steps. Always check against approved shipboard information. Explore the Android toolkit: "),
("Keepry","K02_keepry_facebook_4x5.png","fb_visual_validity_firstday_20260922",
 "The document is saved, but when does it expire? Keepry brings your important files, user-entered expiry dates and reminders together in a private, local-first Android organizer. Explore Keepry: ")
]
def hist(org):
    q=('query { posts(first:100,input:{organizationId:'+fb.quoted(org)+
       ',filter:{status:[scheduled,sent,draft,error,sending],channelIds:['+fb.quoted(fb.EXPECTED_PAGE_ID)+
       ']},sort:[{field:createdAt,direction:desc}]})'
       ' { edges { node { id text status channelId externalLink assets { mimeType source } } } pageInfo { hasNextPage } } }')
    result=fb.buffer_query(q).get("posts") or {}
    if not isinstance(result.get("edges"),list) or (result.get("pageInfo") or {}).get("hasNextPage"):raise RuntimeError("Incomplete history")
    rows=[e["node"] for e in result["edges"] if isinstance(e.get("node"),dict)]
    if any(z.get("channelId")!=fb.EXPECTED_PAGE_ID for z in rows):raise RuntimeError("Wrong channel")
    return rows
def media_ok(url):
    req=urllib.request.Request(url,headers={"Range":"bytes=0-20"})
    with urllib.request.urlopen(req,timeout=22) as r:
        return r.status in (200,206) and r.headers.get("Content-Type","").startswith("image/png") and r.read(8)==b"\x89PNG\r\n\x1a\n"
def main():
    if os.getenv("ASTRALABS_2_PER_APP_FIRSTDAY")!="true":raise RuntimeError("Explicit first-day approval missing")
    org=fb.verified_target()
    for app,img,marker,copy in CAMPAIGNS:
        rows=hist(org)
        if any("utm_content="+marker in (x.get("text") or "") for x in rows):
            print("ALREADY_EXISTS",app,marker,flush=True);continue
        if sum(x.get("status")=="scheduled" for x in rows)>=10:
            print("QUEUE_FULL",app,flush=True);continue
        path=ASSETS+img
        if not media_ok(path):raise RuntimeError("Approved PNG failed "+app)
        url="https://www.astralabsph.com/"+app.lower()+"/?utm_source=facebook&utm_medium=organic_social&utm_campaign=global_android_launch&utm_content="+marker
        message=copy+url+"\nAstraLabs PH: "+HOME+"\nAndroid available now. iOS coming soon.\n\n#"+app+" #"+("MaritimeCalculations #CargoOperations" if app=="Astramate" else "DocumentOrganizer #LifeAdmin")
        if any("utm_content="+marker in (x.get("text") or "") for x in hist(org)):
            print("RACE_DEDUPED",app,flush=True);continue
        mutation=("mutation { createPost(input:{text:"+fb.quoted(message)+
            " channelId:"+fb.quoted(fb.EXPECTED_PAGE_ID)+
            " schedulingType:automatic mode:shareNow aiAssisted:true metadata:{facebook:{type:post}}"+
            " assets:[{image:{url:"+fb.quoted(path)+"}}]})"+
            " { ... on PostActionSuccess { post { id status assets { mimeType source } } }"+
            " ... on MutationError { message } } }")
        response=fb.buffer_query(mutation).get("createPost") or {}
        post=response.get("post") if isinstance(response,dict) else None
        if not isinstance(post,dict) or not post.get("id"):
            raise RuntimeError("Post unconfirmed for "+app+" "+str(response.get("message",""))[:160])
        print("FIRSTDAY_SHARE_ACCEPTED",app,post["id"],post.get("status"),"image_count",len(post.get("assets") or []),flush=True)
        time.sleep(9)
        rows=[x for x in hist(org) if x.get("id")==post["id"]]
        print("FIRSTDAY_VERIFY",app,post["id"],rows[0].get("status") if rows else "unconfirmed","live_url",rows[0].get("externalLink") if rows else None,flush=True)
        if not rows or rows[0].get("status")!="sent":raise RuntimeError("First-day FB actual publication unverified, reconcile before posting next")
        time.sleep(4)
if __name__=="__main__":
    try:main()
    except Exception as e:
        print("FIRSTDAY_FAIL_CLOSED",type(e).__name__,str(e),file=sys.stderr)
        sys.exit(1)
