#!/usr/bin/env python3
from __future__ import annotations
import io, json, math, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT=Path(__file__).resolve().parents[2]
COPY=ROOT/"marketing/pirevo/PINTEREST_PIN_COPY_CHRISTMAS_WAVE4_20261009.json"
STORE=ROOT/"public/pirevo/store-data.js"
OUT=ROOT/"public/pirevo/assets/pins/wave4-christmas"
BASE_URL="https://www.astralabsph.com/pirevo/assets/pins/wave4-christmas"
FONT_BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def rgb(h):
    h=h.lstrip("#")
    return tuple(int(h[i:i+2],16) for i in (0,2,4))

def load_store():
    s=STORE.read_text(encoding="utf-8").strip()
    prefix="window.PIREVO_STORE = "
    if not s.startswith(prefix): raise SystemExit("unexpected store-data.js format")
    if s.endswith(";"): s=s[:-1]
    return json.loads(s[len(prefix):])

def fetch_image(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 PIREVO-Pinterest-Christmas/4.0","Accept":"image/avif,image/webp,image/apng,image/*,*/*;q=0.8"})
    with urllib.request.urlopen(req,timeout=35) as r:
        return Image.open(io.BytesIO(r.read())).convert("RGBA")

def wrap(draw,text,font,max_width):
    words=str(text).split(); lines=[]; line=""
    for w in words:
        c=w if not line else line+" "+w
        if draw.textbbox((0,0),c,font=font)[2] <= max_width: line=c
        else:
            if line: lines.append(line)
            line=w
    if line: lines.append(line)
    return lines

def fit(draw,text,max_width,max_lines=4):
    for size in range(70,44,-2):
        f=ImageFont.truetype(FONT_BOLD,size)
        lines=wrap(draw,text,f,max_width)
        if len(lines)<=max_lines:return f,lines
    f=ImageFont.truetype(FONT_BOLD,44)
    return f,wrap(draw,text,f,max_width)[:max_lines]

def star(draw,x,y,r,fill):
    pts=[]
    for i in range(10):
        a=-math.pi/2+i*math.pi/5
        rr=r if i%2==0 else r*.42
        pts.append((x+math.cos(a)*rr,y+math.sin(a)*rr))
    draw.polygon(pts,fill=fill)

copy=json.loads(COPY.read_text(encoding="utf-8"))
pins=copy.get("pins") or []
if len(pins)!=20: raise SystemExit("expected 20 Christmas Wave 4 pins")
store=load_store()
products={p["slug"]:p for p in store.get("products",[])}
OUT.mkdir(parents=True,exist_ok=True)

font_brand=ImageFont.truetype(FONT_BOLD,38)
font_label=ImageFont.truetype(FONT_BOLD,21)
font_support=ImageFont.truetype(FONT_REG,29)
font_cta=ImageFont.truetype(FONT_BOLD,27)
font_footer=ImageFont.truetype(FONT_REG,20)
manifest={"campaign":"PIREVO Pinterest Christmas Wave 4","count":20,"generated":"2026-10-09","pins":[]}

for idx,pin in enumerate(pins,1):
    p=products.get(pin["slug"])
    if not p: raise SystemExit(f"missing product {pin['slug']}")
    accent=rgb(pin["accent"])
    canvas=Image.new("RGBA",(1000,1500),(249,247,239,255))
    d=ImageDraw.Draw(canvas)

    # Evergreen / champagne editorial background.
    d.rectangle((0,0,1000,1500),fill=(246,245,237,255))
    d.rectangle((0,0,1000,790),fill=(24,61,45,255))
    d.ellipse((650,-210,1190,330),fill=accent+(54,))
    d.ellipse((-260,1020,330,1610),fill=(150,48,58,22))
    # Tiny stars / snow points, deterministic.
    for x,y,r in [(86,150,8),(190,86,5),(840,122,7),(910,240,4),(740,55,4),(110,670,5),(870,710,6)]:
        star(d,x,y,r,(241,220,169,130))
    for x,y in [(125,210),(228,172),(775,210),(895,360),(75,505),(920,575)]:
        d.ellipse((x-3,y-3,x+3,y+3),fill=(255,251,235,120))

    # Product card
    shadow=Image.new("RGBA",canvas.size,(0,0,0,0))
    sd=ImageDraw.Draw(shadow)
    sd.rounded_rectangle((85,118,915,790),radius=42,fill=(0,0,0,78))
    shadow=shadow.filter(ImageFilter.GaussianBlur(26))
    canvas.alpha_composite(shadow)
    d=ImageDraw.Draw(canvas)
    d.rounded_rectangle((75,105,925,775),radius=38,fill=(255,253,247,255),outline=(197,164,92,100),width=3)

    try:
        im=fetch_image(p["image"])
        if im.getbbox(): im=im.crop(im.getbbox())
        im.thumbnail((755,575),Image.Resampling.LANCZOS)
        canvas.alpha_composite(im,(500-im.width//2,430-im.height//2))
    except Exception:
        d.text((140,380),p.get("brand","PIREVO"),font=ImageFont.truetype(FONT_BOLD,54),fill=(30,51,41))
        d.text((140,450),p.get("shortName","Christmas Pick")[:34],font=ImageFont.truetype(FONT_REG,32),fill=(82,76,70))

    d=ImageDraw.Draw(canvas)
    d.rounded_rectangle((42,35,248,91),radius=19,fill=(255,253,247,242))
    d.text((61,47),"PIREVO",font=font_brand,fill=(23,58,43))
    d.text((764,44),"HOLIDAY EDIT",font=ImageFont.truetype(FONT_BOLD,19),fill=(235,220,180))

    label=pin["label"]
    lw=min(830,max(315,d.textbbox((0,0),label,font=font_label)[2]+54))
    d.rounded_rectangle((42,805,42+lw,858),radius=18,fill=accent+(255,))
    d.text((68,819),label,font=font_label,fill=(255,251,242))

    f_title,lines=fit(d,pin["headline"],890,4)
    y=900
    for line in lines:
        d.text((52,y),line,font=f_title,fill=(30,57,45));y+=int(f_title.size*1.12)
    y+=18
    for line in wrap(d,pin["support"],font_support,890)[:3]:
        d.text((52,y),line,font=font_support,fill=(91,85,76));y+=43

    d.rounded_rectangle((52,1307,352,1387),radius=27,fill=(34,83,61,255))
    d.text((82,1330),"SEE THE PICK  →",font=font_cta,fill=(255,251,242))
    d.text((52,1434),"Christmas Preview · Curated by PIREVO",font=font_footer,fill=(115,105,90))
    d.text((700,1434),"astralabsph.com/pirevo",font=font_footer,fill=(115,105,90))

    out=OUT/pin["file"]
    canvas.convert("RGB").save(out,quality=91,optimize=True,progressive=True,subsampling=0)
    q=dict(pin);q["imageUrl"]=f"{BASE_URL}/{pin['file']}";q["asset_status"]="PUBLIC_ASSET_READY";q["campaign"]="pirevo_christmas_wave4"
    manifest["pins"].append(q)

(OUT/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
qa=Image.new("RGB",(1000,1200),(238,237,230))
for i,pin in enumerate(pins):
    im=Image.open(OUT/pin["file"]).convert("RGB").resize((200,300),Image.Resampling.LANCZOS)
    qa.paste(im,((i%5)*200,(i//5)*300))
qa.save(OUT/"QA_contact_sheet.jpg",quality=88,optimize=True,progressive=True)
print("PIREVO_CHRISTMAS_WAVE4_RENDER_OK count=20")
