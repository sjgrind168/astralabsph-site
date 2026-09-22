#!/usr/bin/env python3
"""Render two original, editorial-only Pinterest QUESTION pilot previews.

NO Buffer/Pinterest API, no social publishing, no fabricated phone/app UI, no private
document samples, no offsite stock imagery. Both use original Pillow vector artwork;
reviewer must still visually QA/approve before release ledger may be touched.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "public/marketing/campaigns/seven_day/previews"
OUT.mkdir(parents=True, exist_ok=True)
W,H = 1000,1500
FONTREG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTBOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
HOME="www.astralabsph.com"
CREATIVES=(
    {"id":"S26D1KQ","app":"KEEPRY","theme":"Life-admin note",
     "title":["Passport photo saved.","Expiry date remembered?"],
     "description":["A document photo holds a date.","A reminder needs a plan."],
     "question":["What deadline do you check","before a trip?"],
     "privacy":"Reply with the document type only. Keep personal details private.",
     "bg":"#EFF8F3","dark":"#123A32","accent":"#187D5D","highlight":"#F4B860"},
    {"id":"S26D1AQ","app":"ASTRAMATE","theme":"Cargo calculation note",
     "title":["Cargo weight looks fine.","Will the parcel fit?"],
     "description":["Weight and usable hold volume","answer different questions."],
     "question":["Which cargo input do you","check first, and why?"],
     "privacy":"Use approved vessel information for operational decisions.",
     "bg":"#F0F6FA","dark":"#142F49","accent":"#176C95","highlight":"#F4B860"},
)

def font(size, heavy=False):
    return ImageFont.truetype(FONTBOLD if heavy else FONTREG,size)

def text(draw, at, value, size, color, heavy=False, anchor=None):
    draw.text(at,value,fill=color,font=font(size,heavy),anchor=anchor,
              stroke_width=0)

def card(draw, bounds, fill, radius=33, stroke=None, width=1):
    draw.rounded_rectangle(bounds,radius=radius,fill=fill,outline=stroke,width=width)

def document_scene(draw, p):
    d=p["dark"]; a=p["accent"]
    # Honest conceptual illustration: no passport data or simulated Keepry UI.
    card(draw,(143,548,623,1020),"#F8FCFA",27,"#D2E3DA",3)
    card(draw,(196,603,560,702),d,13)
    text(draw,(220,626),"DOCUMENT",26,"#FFFFFF",True)
    for y,w in ((766,290),(809,260),(852,302)):
        card(draw,(200,y,200+w,y+12),"#CEE2D6",6)
    card(draw,(505,758,851,1018),"#FFFFFF",25,"#BADBD0",4)
    card(draw,(505,758,851,824),a,20)
    text(draw,(526,773),"DATE CHECK",21,"#FFFFFF",True)
    for xx in (552,648,744):
        for yy in (862,927):
            card(draw,(xx,yy,xx+45,yy+37),"#D8ECE2",9)
    draw.ellipse((735,948,849,1062),fill=p["highlight"],outline="#FFFFFF",width=7)
    draw.line([(760,1007),(781,1025),(822,980)],fill=d,width=9,joint="curve")

def cargo_scene(draw,p):
    d=p["dark"];a=p["accent"]
    # Abstract cargo hold/parcel educational illustration, no vessel-specific data.
    card(draw,(132,573,868,1039),"#F8FCFF",28,"#CEDCE8",4)
    draw.polygon([(193,691),(827,691),(756,956),(261,956)],fill="#E3EFF5",
                 outline=a,width=5)
    draw.line([(193,691),(261,956),(756,956),(827,691)],fill=d,width=8,
              joint="curve")
    for x,y in ((286,724),(418,724),(550,724),(353,824),(485,824)):
        card(draw,(x,y,x+105,y+94),"#76B2CD",10,d,3)
        draw.line((x,y+47,x+105,y+47),fill="#3D87A7",width=3)
        draw.line((x+52,y,x+52,y+94),fill="#3D87A7",width=3)
    card(draw,(620,858,822,1046),"#FFFFFF",26,"#C5DDE7",4)
    draw.line([(666,958),(714,910),(772,958),(666,958)],fill=a,width=8,
              joint="curve")
    text(draw,(720,995),"REVIEW",19,d,True,anchor="mm")

def make(p):
    image=Image.new("RGB",(W,H),p["bg"])
    d=ImageDraw.Draw(image)
    dark,accent=p["dark"],p["accent"]
    d.ellipse((745,-152,1220,365),fill="#D5EADD" if p["app"]=="KEEPRY" else "#DCEBF5")
    d.ellipse((-185,1070,330,1585),fill="#E0F1E7" if p["app"]=="KEEPRY" else "#DFEDF5")
    card(d,(72,68,928,145),dark,36)
    text(d,(111,92),"ASTRALABS PH",27,"#FFFFFF",True)
    text(d,(880,94),p["app"],23,p["highlight"],True,anchor="ra")
    text(d,(89,202),p["theme"].upper(),23,accent,True)
    for i,line in enumerate(p["title"]):
        text(d,(84,275+80*i),line,51,dark,True)
    for i,line in enumerate(p["description"]):
        text(d,(87,472+46*i),line,29,dark)
    if p["app"]=="KEEPRY":
        document_scene(d,p)
    else:
        cargo_scene(d,p)
    card(d,(70,1088,930,1307),"#FFFFFF",30,"#D4E5DD" if p["app"]=="KEEPRY" else "#CFDFE8",2)
    text(d,(101,1110),"YOUR TAKE",22,accent,True)
    for i,line in enumerate(p["question"]):
        text(d,(98,1156+45*i),line,32,dark,True)
    text(d,(85,1340),p["privacy"],20,dark)
    card(d,(0,1408,W,H),dark,0)
    text(d,(77,1436),HOME,33,"#FFFFFF",True)
    text(d,(930,1444),"EXPLORE "+p["app"].title(),18,p["highlight"],True,anchor="ra")
    output=OUT/(p["id"]+"_pinterest_original_PREVIEW.png")
    image.save(output,optimize=True)
    with Image.open(output) as proof:
        proof.verify()
    with Image.open(output) as proof:
        assert proof.format=="PNG" and proof.size==(1000,1500) and proof.mode=="RGB"
    h=hashlib.sha256(output.read_bytes()).hexdigest()
    print("PIN_PILOT_RENDERED",p["id"],"resolution=1000x1500","bytes="+str(output.stat().st_size),
          "sha256="+h,"preview_not_approved_no_social_post",flush=True)
    return {"creative_id":p["id"],"app":p["app"],"path":output.relative_to(ROOT).as_posix(),
            "sha256":h,"size":"1000x1500","approval":"VISUAL_AND_PRODUCT_CLAIM_QA_PENDING_NO_BUFFER_WRITE",
            "source":"Original in-repo Pillow geometric illustration, no third-party photos, screenshots or generated app UI",
            "font":"DejaVu Sans installed by runner; font files are not redistributed",
            "root_footer":HOME}

if __name__=="__main__":
    record=[make(p) for p in CREATIVES]
    log=ROOT/"marketing/automation/shared/creative_drafts/pinterest_first_question_pilot_preview_manifest.json"
    log.parent.mkdir(parents=True,exist_ok=True)
    log.write_text(json.dumps({"policy":"PREVIEW_ONLY_NOT_APPROVED_NO_SOCIAL_WRITE",
                               "human_app_claims_media_rights_mobile_visual_review_required":True,
                               "assets":record},indent=2)+"\n",encoding="utf-8")
    print("PINTEREST_PREVIEW_ONLY: both original draft media files rendered. No release ledger, Buffer post or existing assets modified.")
