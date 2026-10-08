#!/usr/bin/env python3
from __future__ import annotations
import io, json, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT=Path(__file__).resolve().parents[2]
COPY=ROOT/"marketing/pirevo/PINTEREST_PIN_COPY_HALLOWEEN_WAVE3_20261009.json"
STORE=ROOT/"public/pirevo/store-data.js"
OUT=ROOT/"public/pirevo/assets/pins/wave3-halloween"
BASE_URL="https://www.astralabsph.com/pirevo/assets/pins/wave3-halloween"
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
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 PIREVO-Pinterest-Halloween/3.0","Accept":"image/avif,image/webp,image/apng,image/*,*/*;q=0.8"})
    with urllib.request.urlopen(req,timeout=35) as r:
        return Image.open(io.BytesIO(r.read())).convert("RGBA")

def wrap(draw,text,font,max_width):
    words=str(text).split(); lines=[]; line=""
    for w in words:
        c=w if not line else line+" "+w
        if draw.textbbox((0,0),c,font=font)[2] <= max_width:
            line=c
        else:
            if line: lines.append(line)
            line=w
    if line: lines.append(line)
    return lines

def fit(draw,text,max_width,max_lines=4):
    for size in range(72,44,-2):
        f=ImageFont.truetype(FONT_BOLD,size)
        lines=wrap(draw,text,f,max_width)
        if len(lines)<=max_lines:
            return f,lines
    f=ImageFont.truetype(FONT_BOLD,44)
    return f,wrap(draw,text,f,max_width)[:max_lines]

def web(draw,cx,cy,r,fill):
    for rr in range(40,r+1,40):
        draw.arc((cx-rr,cy-rr,cx+rr,cy+rr),180,270,fill=fill,width=2)
    for deg in (180,195,210,225,240,255,270):
        import math
        x=cx+r*math.cos(math.radians(deg)); y=cy+r*math.sin(math.radians(deg))
        draw.line((cx,cy,x,y),fill=fill,width=2)

copy=json.loads(COPY.read_text(encoding="utf-8"))
pins=copy.get("pins") or []
if len(pins)!=16: raise SystemExit("expected 16 Halloween Wave 3 pins")
store=load_store()
products={p["slug"]:p for p in store.get("products",[])}
OUT.mkdir(parents=True,exist_ok=True)

font_brand=ImageFont.truetype(FONT_BOLD,38)
font_label=ImageFont.truetype(FONT_BOLD,21)
font_support=ImageFont.truetype(FONT_REG,29)
font_cta=ImageFont.truetype(FONT_BOLD,27)
font_footer=ImageFont.truetype(FONT_REG,20)
font_skull=ImageFont.truetype(FONT_BOLD,66)

manifest={"campaign":"PIREVO Pinterest Halloween Wave 3","count":16,"generated":"2026-10-09","pins":[]}

for i,pin in enumerate(pins,1):
    product=products.get(pin["slug"])
    if not product: raise SystemExit(f"missing product slug {pin['slug']}")
    accent=rgb(pin["accent"])
    canvas=Image.new("RGBA",(1000,1500),(21,17,23,255))
    d=ImageDraw.Draw(canvas)

    # Moody editorial background.
    d.rectangle((0,0,1000,1500),fill=(24,18,26,255))
    d.ellipse((620,-160,1220,440),fill=accent+(48,))
    d.ellipse((-300,1060,360,1660),fill=(244,122,42,26))
    web(d,980,0,330,(255,247,235,38))
    web(d,0,1500,260,(255,247,235,22))
    d.text((43,24),"☠",font=font_skull,fill=(255,247,235,28))

    # Product hero card.
    shadow=Image.new("RGBA",canvas.size,(0,0,0,0))
    sd=ImageDraw.Draw(shadow)
    sd.rounded_rectangle((85,120,915,790),radius=42,fill=(0,0,0,95))
    shadow=shadow.filter(ImageFilter.GaussianBlur(28))
    canvas.alpha_composite(shadow)
    d=ImageDraw.Draw(canvas)
    d.rounded_rectangle((75,105,925,775),radius=38,fill=(248,244,236,255),outline=accent+(110,),width=3)

    try:
        im=fetch_image(product["image"])
        if im.getbbox(): im=im.crop(im.getbbox())
        im.thumbnail((760,575),Image.Resampling.LANCZOS)
        canvas.alpha_composite(im,(500-im.width//2,430-im.height//2))
    except Exception:
        d.text((140,380),product.get("brand","PIREVO"),font=ImageFont.truetype(FONT_BOLD,56),fill=(32,28,31))
        d.text((140,455),product.get("shortName","Halloween Pick")[:34],font=ImageFont.truetype(FONT_REG,33),fill=(82,76,80))

    d=ImageDraw.Draw(canvas)
    d.rounded_rectangle((42,35,248,91),radius=19,fill=(255,247,235,242))
    d.text((61,47),"PIREVO",font=font_brand,fill=(27,22,26))
    label=pin["label"]
    lw=min(830,max(315,d.textbbox((0,0),label,font=font_label)[2]+54))
    d.rounded_rectangle((42,805,42+lw,858),radius=18,fill=accent+(255,))
    d.text((68,819),label,font=font_label,fill=(255,248,238))

    f_title,lines=fit(d,pin["headline"],890,4)
    y=900
    for line in lines:
        d.text((52,y),line,font=f_title,fill=(255,247,235)); y+=int(f_title.size*1.12)
    y+=18
    for line in wrap(d,pin["support"],font_support,890)[:3]:
        d.text((52,y),line,font=font_support,fill=(202,191,198)); y+=43

    d.rounded_rectangle((52,1307,352,1387),radius=27,fill=accent+(255,))
    d.text((82,1330),"SEE THE PICK  →",font=font_cta,fill="white")
    d.text((52,1434),"Halloween Edit · Curated by PIREVO",font=font_footer,fill=(176,165,172))
    d.text((700,1434),"astralabsph.com/pirevo",font=font_footer,fill=(176,165,172))

    out=OUT/pin["file"]
    canvas.convert("RGB").save(out,quality=91,optimize=True,progressive=True,subsampling=0)

    q=dict(pin)
    q["imageUrl"]=f"{BASE_URL}/{pin['file']}"
    q["asset_status"]="PUBLIC_ASSET_READY"
    q["campaign"]="pirevo_halloween_wave3"
    manifest["pins"].append(q)

(OUT/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")

# 4 x 4 QA contact sheet.
qa=Image.new("RGB",(800,1200),(34,29,35))
for idx,p in enumerate(pins):
    im=Image.open(OUT/p["file"]).convert("RGB").resize((200,300),Image.Resampling.LANCZOS)
    qa.paste(im,((idx%4)*200,(idx//4)*300))
qa.save(OUT/"QA_contact_sheet.jpg",quality=88,optimize=True,progressive=True)
print("PIREVO_HALLOWEEN_WAVE3_RENDER_OK count=16")
