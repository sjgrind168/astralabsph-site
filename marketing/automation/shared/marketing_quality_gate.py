#!/usr/bin/env python3
"""No-write marketing quality gate for approved publishing banks and public conversion pages."""
import importlib.util,json,re,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name):
    p=ROOT/name/"scripts"/("buffer_"+name+".py")
    spec=importlib.util.spec_from_file_location("quality_"+name,p)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
fb=load("facebook");pn=load("pinterest");tt=load("tiktok")
dailyfile=ROOT/"facebook"/"scripts"/"daily_two_per_app.py"
spec=importlib.util.spec_from_file_location("marketing_daily_quality",dailyfile)
daily=importlib.util.module_from_spec(spec);spec.loader.exec_module(daily)
bank=daily.candidates()
if len(bank)!=28 or len({p["id"] for p in bank})!=28:raise RuntimeError("Editorial bank not exactly 28 distinct posts")
for item in bank:
    image,caption=daily.build_post(item)
    app=item["app"]
    if not all(x in caption for x in ("https://www.astralabsph.com/","https://www.astralabsph.com/"+app.lower()+"/?","utm_content="+item["id"])):
        raise RuntimeError("Main website or product landing link missing "+item["id"])
    if not any(x in caption for x in ("Premium","Plus")) or "one-time" not in caption or "Free" not in caption:
        raise RuntimeError("Free entry or honest paid-offer reason missing "+item["id"])
    if app=="Astramate" and re.search(r"\beta\b",caption,re.I):raise RuntimeError("ETA in next-wave Astramate caption")
    if caption.count("#")>3:raise RuntimeError("Overstuffed hashtags")
    if len(caption)>1250:raise RuntimeError("Caption too long")
    if "astramate.vercel.app" in caption or "www.astralabsph.com/" not in caption:
        raise RuntimeError("Legacy website appeared in caption")
    if not daily.public_png(image):raise RuntimeError("Public media unavailable "+item["id"])
print("QUALITY_PASS_FACEBOOK",len(bank),"distinct upcoming persuasive copies, working verified creative URLs",flush=True)
pins=pn.approved()
if len(pins)!=9 or any(re.search(r"\beta\b",p["title"]+" "+p["description"],re.I) for p in pins if p["app"]=="Astramate"):
    raise RuntimeError("Pinterest bank includes ETA or missing no-ETA creatives")
print("QUALITY_PASS_PINTEREST",len(pins),"approved no-ETA Pins",flush=True)
items=tt.approved()
for item in items:
    if not tt.verify_media(item["videoUrl"]):raise RuntimeError("TikTok approved final media URL invalid")
    if "astralabsph.com/" not in item["text"] or "astramate.vercel.app" in item["text"]:
        raise RuntimeError("TikTok must use official site")
print("QUALITY_PASS_TIKTOK",len(items),"previously approved V2 first-wave assets, no new posting",flush=True)
for app,feature in [("astramate",b"Checking a cargo parcel against available hold space?"),
                    ("keepry",b"Your documents and renewal dates should not be scattered")]:
    url="https://www.astralabsph.com/"+app+"/"
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"AstraLabs-Campaign-QA/1.0"}),timeout=18) as res:
        body=res.read(350000)
        valid=(res.status==200 and feature in body and b'var keys=["utm_source","utm_medium","utm_campaign","utm_content"]' in body
            and b"Get "+app.title().encode()+b" free on Google Play" in body)
        print("LANDING_PAGE",app,"http",res.status,"buyer_story",feature in body,"campaign_attribution",b"var keys=" in body,"ok",valid,flush=True)
        if not valid:raise RuntimeError("Published landing page awaiting deploy or missing buyer story "+app)
print("GLOBAL_CAMPAIGN_QUALITY_GATE_PASSED",flush=True)
