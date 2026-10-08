#!/usr/bin/env python3
from __future__ import annotations
import io, json, urllib.request, urllib.error
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parents[2]
COPY=ROOT/"marketing/pirevo/PINTEREST_PIN_COPY_WAVE2_20261009.json"
STORE=ROOT/"public/pirevo/store-data.js"
OUT=ROOT/"public/pirevo/assets/pins/wave2"
BASE_URL="https://www.astralabsph.com/pirevo/assets/pins/wave2"
FONT_BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def load_store():
    s=STORE.read_text(encoding="utf-8").strip()
    prefix="window.PIREVO_STORE = "
    if not s.startswith(prefix): raise SystemExit("unexpected store-data.js format")
    if s.endswith(";"): s=s[:-1]
    return json.loads(s[len(prefix):])

def rgb(h):
    h=h.lstrip("#")
    return tuple(int(h[i:i+2],16) for i in (0,2,4))

def wrap(draw,text,font,max_width):
    words=str(text).split(); lines=[]; line=""
    for word in words:
        c=word if not line else line+" "+word
        if draw.textbbox((0,0),c,font=font)[2] <= max_width: line=c
        else:
            if line: lines.append(line)
            line=word
    if line: lines.append(line)
    return lines

def fit(draw,text,max_width,max_lines=4):
    for size in range(76,46,-2):
        f=ImageFont.truetype(FONT_BOLD,size)
        lines=wrap(draw,text,f,max_width)
        if len(lines)<=max_lines: return f,lines
    f=ImageFont.truetype(FONT_BOLD,46)
    return f,wrap(draw,text,f,max_width)[:max_lines]

def fetch_image(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 PIREVO-Pinterest-Renderer/2.0","Accept":"image/avif,image/webp,image/apng,image/*,*/*;q=0.8"})
    with urllib.request.urlopen(req,timeout=35) as r:
        raw=r.read()
    return Image.open(io.BytesIO(raw)).convert("RGBA")

copy=json.loads(COPY.read_text(encoding="utf-8"))
pins=copy.get("pins") or []
if len(pins)!=10: raise SystemExit("expected 10 wave2 pins")
store=load_store()
products={p["slug"]:p for p in store.get("products",[])}
OUT.mkdir(parents=True,exist_ok=True)

font_brand=ImageFont.truetype(FONT_BOLD,40)
font_label=ImageFont.truetype(FONT_BOLD,22)
font_support=ImageFont.truetype(FONT_REG,31)
font_cta=ImageFont.truetype(FONT_BOLD,29)
font_footer=ImageFont.truetype(FONT_REG,22)

manifest={"campaign":"PIREVO Pinterest Wave 2","count":10,"generated":"2026-10-09","pins":[]}
for i,pin in enumerate(pins,1):
    slug=pin["slug"]
    product=products.get(slug)
    if not product: raise SystemExit(f"missing product slug {slug}")
    accent=rgb(pin["accent"])
    canvas=Image.new("RGBA",(1000,1500),(246,244,238,255))
    d=ImageDraw.Draw(canvas)

    # Hero area with soft editorial tint.
    hero_bg=Image.new("RGBA",(1000,780),accent+(35,))
    canvas.alpha_composite(hero_bg,(0,0))
    for r,a in [(430,22),(320,18),(220,14)]:
        glow=Image.new("RGBA",(1000,780),(0,0,0,0))
        gd=ImageDraw.Draw(glow)
        gd.ellipse((500-r,-120-r,500+r,-120+r),fill=(255,255,255,a))
        canvas.alpha_composite(glow,(0,0))

    try:
        im=fetch_image(product["image"])
        # White/transparent product shots get premium card treatment.
        bbox=im.getbbox()
        if bbox: im=im.crop(bbox)
        im.thumbnail((760,610),Image.Resampling.LANCZOS)
        card=Image.new("RGBA",(840,650),(255,255,255,238))
        cd=ImageDraw.Draw(card)
        cd.rounded_rectangle((0,0,839,649),radius=34,fill=(255,255,255,238),outline=accent+(55,),width=2)
        shadow=Image.new("RGBA",canvas.size,(0,0,0,0))
        sd=ImageDraw.Draw(shadow)
        sd.rounded_rectangle((92,92,908,712),radius=38,fill=(0,0,0,40))
        shadow=shadow.filter(ImageFilter.GaussianBlur(24))
        canvas.alpha_composite(shadow)
        canvas.alpha_composite(card,(80,70))
        x=500-im.width//2; y=385-im.height//2
        canvas.alpha_composite(im,(x,y))
    except Exception as e:
        # Fail visually safe rather than fail workflow due to retailer hotlink quirks.
        d.rounded_rectangle((110,120,890,680),radius=42,fill=(255,255,255,235),outline=accent+(70,),width=3)
        d.text((160,340),product.get("brand","PIREVO"),font=ImageFont.truetype(FONT_BOLD,54),fill=(28,31,28))
        d.text((160,410),product.get("shortName",slug)[:34],font=ImageFont.truetype(FONT_REG,34),fill=(70,75,72))

    d=ImageDraw.Draw(canvas)
    d.rounded_rectangle((42,34,250,92),radius=20,fill=(255,255,255,240))
    d.text((62,47),"PIREVO",font=font_brand,fill=(18,24,20))
    label=pin["label"]
    lw=min(820,max(320,d.textbbox((0,0),label,font=font_label)[2]+50))
    d.rounded_rectangle((42,110,42+lw,162),radius=18,fill=accent+(240,))
    d.text((66,124),label,font=font_label,fill="white")

    d.rectangle((0,760,1000,1500),fill=(249,247,242,255))
    d.rounded_rectangle((52,815,160,828),radius=7,fill=accent+(255,))
    f_title,lines=fit(d,pin["headline"],890,4)
    y=858
    for line in lines:
        d.text((52,y),line,font=f_title,fill=(20,26,23)); y+=int(f_title.size*1.12)
    y+=18
    for line in wrap(d,pin["support"],font_support,890)[:3]:
        d.text((52,y),line,font=font_support,fill=(82,86,82)); y+=45

    d.rounded_rectangle((52,1300,350,1382),radius=28,fill=accent+(255,))
    d.text((82,1323),"SEE THE PICK  →",font=font_cta,fill="white")
    d.text((52,1428),"Curated by PIREVO",font=font_footer,fill=(82,86,82))
    d.text((682,1428),"astralabsph.com/pirevo",font=font_footer,fill=(82,86,82))

    out=OUT/pin["file"]
    canvas.convert("RGB").save(out,quality=91,optimize=True,progressive=True,subsampling=0)

    q=dict(pin)
    q["imageUrl"]=f"{BASE_URL}/{pin['file']}"
    q["asset_status"]="PUBLIC_ASSET_READY"
    q["campaign"]="pirevo_wave2"
    manifest["pins"].append(q)

(OUT/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")

qa=Image.new("RGB",(1000,1500),(235,235,235))
thumbs=[]
for p in pins:
    im=Image.open(OUT/p["file"]).convert("RGB").resize((200,300),Image.Resampling.LANCZOS)
    thumbs.append(im)
for idx,im in enumerate(thumbs):
    qa.paste(im,((idx%5)*200,(idx//5)*300))
qa=qa.resize((1000,600),Image.Resampling.LANCZOS)
qa.save(OUT/"QA_contact_sheet.jpg",quality=88,optimize=True,progressive=True)
print("PIREVO_WAVE2_RENDER_OK count=10")
