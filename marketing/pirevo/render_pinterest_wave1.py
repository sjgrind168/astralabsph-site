#!/usr/bin/env python3
"""Render PIREVO Pinterest Wave 1 assets from the approved AI visual source.

Fail-closed: writes only the PIREVO Wave 1 asset folder + manifest public URLs.
No social publication occurs here.
"""
from __future__ import annotations
import base64, io, json, os
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parents[2]
SOURCE_B64=ROOT/"marketing/pirevo/assets/pirevo_pin_source_contact_q45.b64"
COPY=ROOT/"marketing/pirevo/PINTEREST_PIN_COPY_20260927.json"
LAUNCH=ROOT/"marketing/pirevo/PINTEREST_LAUNCH_20260927.json"
OUT=ROOT/"public/pirevo/assets/pins/wave1"
BASE_URL="https://www.astralabsph.com/pirevo/assets/pins/wave1"

GUIDE_META={
"small-apartment-organization":("SMALL SPACE & ORGANIZATION","#1769FF"),
"home-office-desk-upgrades":("HOME OFFICE & DESK","#E66A00"),
"carry-on-travel-essentials":("TRAVEL ESSENTIALS","#008C7A"),
"weeknight-kitchen-tools":("KITCHEN FINDS","#E4483B"),
"renter-bathroom-storage":("BATHROOM & RENTER","#6A50C9"),
"dorm-room-upgrades":("DORM ROOM FINDS","#D79B00"),
"pet-cleanup-organization":("PET HOME","#2E8B57"),
"car-organization-road-trip":("CAR & ROAD TRIP","#0B6DB7"),
"gifts-under-30":("GIFTS & EVERYDAY FINDS","#D13D76"),
"cozy-fall-home-upgrades":("COZY HOME","#7A5B43"),
}
GUIDE_ORDER=list(GUIDE_META)

FONT_BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
for p in (SOURCE_B64,COPY,LAUNCH):
    if not p.exists(): raise SystemExit(f"missing required input: {p}")
for f in (FONT_BOLD,FONT_REG):
    if not Path(f).exists(): raise SystemExit(f"missing font: {f}")

raw=base64.b64decode("".join(SOURCE_B64.read_text().split()))
src=Image.open(io.BytesIO(raw)).convert("RGB")
if src.size != (1536,1024): raise SystemExit(f"unexpected source size {src.size}")
copy_doc=json.loads(COPY.read_text(encoding="utf-8"))
pins=copy_doc.get("pins") or []
if len(pins)!=30: raise SystemExit(f"expected 30 pins, got {len(pins)}")
launch=json.loads(LAUNCH.read_text(encoding="utf-8"))
launch_pins=launch.get("pins") or []
if len(launch_pins)!=30: raise SystemExit("launch manifest must contain 30 pins")

def rgb(h):
    h=h.lstrip("#")
    return tuple(int(h[i:i+2],16) for i in (0,2,4))

def scene_crop(row,col):
    x0=round(col*src.width/10); x1=round((col+1)*src.width/10)
    y0=round(row*src.height/3); y1=round((row+1)*src.height/3)
    yy0=y0+int((y1-y0)*0.50); yy1=y0+int((y1-y0)*0.78)
    return src.crop((x0+3,yy0,x1-3,yy1))

def wrap(draw,text,font,max_width):
    words=str(text).split(); lines=[]; line=""
    for word in words:
        candidate=word if not line else line+" "+word
        if draw.textbbox((0,0),candidate,font=font)[2] <= max_width:
            line=candidate
        else:
            if line: lines.append(line)
            line=word
    if line: lines.append(line)
    return lines

def fit_title(draw,text,max_width,max_lines=4):
    for size in range(80,52,-2):
        font=ImageFont.truetype(FONT_BOLD,size)
        lines=wrap(draw,text,font,max_width)
        if len(lines)<=max_lines: return font,lines
    font=ImageFont.truetype(FONT_BOLD,52)
    return font,wrap(draw,text,font,max_width)

OUT.mkdir(parents=True,exist_ok=True)
font_brand=ImageFont.truetype(FONT_BOLD,40)
font_cat=ImageFont.truetype(FONT_BOLD,23)
font_sub=ImageFont.truetype(FONT_REG,32)
font_cta=ImageFont.truetype(FONT_BOLD,29)
font_small=ImageFont.truetype(FONT_REG,23)

rendered=[]
for idx,pin in enumerate(pins):
    guide=pin["guide"]
    if guide not in GUIDE_META: raise SystemExit(f"unknown guide: {guide}")
    col=GUIDE_ORDER.index(guide); row=idx%3
    # enforce exact 3-pin grouping
    if idx//3 != col: raise SystemExit(f"pin ordering mismatch at {idx}: {guide}")
    category,color=GUIDE_META[guide]; accent=rgb(color)
    scene=scene_crop(row,col)
    canvas=Image.new("RGBA",(1000,1500),(248,246,241,255))
    hero=ImageOps.fit(scene,(1000,760),method=Image.Resampling.LANCZOS)
    hero=ImageEnhance.Contrast(hero).enhance(1.06)
    hero=ImageEnhance.Color(hero).enhance(1.06)
    hero=hero.filter(ImageFilter.UnsharpMask(radius=1.2,percent=120,threshold=4))
    hero=hero.filter(ImageFilter.GaussianBlur(0.18)).convert("RGBA")
    canvas.paste(hero,(0,0),hero)
    canvas.alpha_composite(Image.new("RGBA",(1000,760),accent+(18,)),(0,0))
    d=ImageDraw.Draw(canvas)
    d.rounded_rectangle((42,36,250,94),radius=22,fill=(255,255,255,238))
    d.text((62,48),"PIREVO",font=font_brand,fill=(16,25,38))
    cat_w=min(760,max(270,d.textbbox((0,0),category,font=font_cat)[2]+48))
    d.rounded_rectangle((42,112,42+cat_w,166),radius=20,fill=accent+(236,))
    d.text((64,128),category,font=font_cat,fill="white")
    d.rectangle((0,710,1000,1500),fill=(249,247,242,255))
    d.rounded_rectangle((52,775,148,789),radius=7,fill=accent+(255,))
    title=str(pin["title"])
    font_title,lines=fit_title(d,title,900)
    y=822; line_h=int(font_title.size*1.10)
    for line in lines:
        d.text((52,y),line,font=font_title,fill=(19,26,36)); y+=line_h
    y+=18
    desc=str(pin.get("description") or "")
    # Description file appends a second sentence; use first sentence for artwork.
    subtitle=desc.split(" Explore the full PIREVO guide",1)[0].strip()
    for line in wrap(d,subtitle,font_sub,890)[:4]:
        d.text((52,y),line,font=font_sub,fill=(76,82,90)); y+=45
    d.rounded_rectangle((52,1310,420,1390),radius=28,fill=accent+(255,))
    d.text((82,1332),"READ THE GUIDE  →",font=font_cta,fill="white")
    d.text((52,1430),"Smart finds worth discovering.",font=font_small,fill=(79,84,91))
    d.text((670,1430),"astralabsph.com/pirevo",font=font_small,fill=(79,84,91))
    fname=pin["file"]
    if not fname.endswith(".jpg"): raise SystemExit("asset filename must be jpg")
    path=OUT/fname
    canvas.convert("RGB").save(path,quality=90,optimize=True,progressive=True,subsampling=0)
    rendered.append(path)
    launch_pin=launch_pins[idx]
    if launch_pin.get("guide")!=guide: raise SystemExit("launch/copy manifest mismatch")
    launch_pin["asset_file"]=fname
    launch_pin["public_asset_url"]=f"{BASE_URL}/{fname}"
    launch_pin["asset_status"]="PUBLIC_ASSET_READY"
    launch_pin["publish_status"]="READY_FOR_BUFFER_STAGING"

# Public machine-readable pack manifest
public_manifest={"campaign":"PIREVO Pinterest Wave 1","count":30,"pins":[]}
for idx,p in enumerate(pins):
    q=dict(p)
    q["imageUrl"]=f"{BASE_URL}/{p['file']}"
    public_manifest["pins"].append(q)
(OUT/"manifest.json").write_text(json.dumps(public_manifest,indent=2,ensure_ascii=False),encoding="utf-8")

# QA contact sheet, 5x6
qa=Image.new("RGB",(1250,2250),(236,236,236))
for i,path in enumerate(rendered):
    im=Image.open(path).convert("RGB").resize((250,375),Image.Resampling.LANCZOS)
    qa.paste(im,((i%5)*250,(i//5)*375))
qa.save(OUT/"QA_contact_sheet.jpg",quality=87,optimize=True,progressive=True)

launch["asset_pack"]["public_base_url"]=BASE_URL
launch["asset_pack"]["public_manifest"]=f"{BASE_URL}/manifest.json"
launch["asset_pack"]["qa_url"]=f"{BASE_URL}/QA_contact_sheet.jpg"
launch["asset_pack"]["rendered_by"]="marketing/pirevo/render_pinterest_wave1.py"
LAUNCH.write_text(json.dumps(launch,indent=2,ensure_ascii=False),encoding="utf-8")
print(f"PIREVO_PIN_RENDER_OK count={len(rendered)} out={OUT}")
