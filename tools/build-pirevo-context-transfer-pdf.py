#!/usr/bin/env python3
"""Create a searchable, page-numbered PDF from the canonical PIREVO context handoff."""
from pathlib import Path
import re, html
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

ROOT=Path(__file__).resolve().parent.parent
md=ROOT/"docs/PIREVO_FULL_CONTEXT_TRANSFER_2026-10-22_CANONICAL.md"
dest=md.with_suffix(".pdf")
source=md.read_text(encoding="utf-8")
fonts=[
("/System/Library/Fonts/Supplemental/Arial.ttf","/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
("/System/Library/Fonts/Supplemental/DejaVuSans.ttf","/System/Library/Fonts/Supplemental/DejaVuSans-Bold.ttf"),
]
font,fbold="Helvetica","Helvetica-Bold"
for regular,bold in fonts:
 if Path(regular).exists() and Path(bold).exists():
  pdfmetrics.registerFont(TTFont("PirevoSans",regular))
  pdfmetrics.registerFont(TTFont("PirevoSansBold",bold))
  pdfmetrics.registerFontFamily("PirevoSans",normal="PirevoSans",bold="PirevoSansBold",italic="PirevoSans",boldItalic="PirevoSansBold")
  font,fbold="PirevoSans","PirevoSansBold"
  break

GREEN=HexColor("#164831")
TEXT=HexColor("#23392e")
MUTED=HexColor("#5c7465")
SOFT=HexColor("#e3ece5")
style={
 "meta":ParagraphStyle("meta",fontName=font,fontSize=9.4,leading=14,textColor=MUTED,spaceAfter=5),
 "h1":ParagraphStyle("h1",fontName=fbold,fontSize=20,leading=25,textColor=GREEN,spaceAfter=15),
 "h2":ParagraphStyle("h2",fontName=fbold,fontSize=12.7,leading=18,textColor=GREEN,spaceBefore=18,spaceAfter=8,keepWithNext=True),
 "h3":ParagraphStyle("h3",fontName=fbold,fontSize=10.8,leading=16,textColor=GREEN,spaceBefore=12,spaceAfter=6,keepWithNext=True),
 "body":ParagraphStyle("body",fontName=font,fontSize=9.2,leading=14.4,textColor=TEXT,spaceAfter=6,splitLongWords=1),
 "bullet":ParagraphStyle("bullet",fontName=font,fontSize=9.15,leading=14.3,textColor=TEXT,leftIndent=15,firstLineIndent=-10,spaceAfter=5,splitLongWords=1),
 "path":ParagraphStyle("path",fontName=font,fontSize=8.6,leading=13,textColor=MUTED,leftIndent=14,spaceAfter=3,splitLongWords=1),
 "small":ParagraphStyle("small",fontName=font,fontSize=8,leading=12,textColor=MUTED,spaceAfter=3)
}

def clean_line(line):
 line=line.strip()
 line=html.escape(line,quote=False)
 line=re.sub(r"\*\*(.*?)\*\*",r"<b>\1</b>",line)
 # Slightly reduce risk of very long unbroken file paths pushing outside frame.
 return line

story=[Spacer(1,17)]
for ln in source.splitlines():
 s=ln.rstrip()
 if not s.strip():
  story.append(Spacer(1,3))
  continue
 if s.startswith("# "):
  story.append(Paragraph(clean_line(s[2:]),style["h1"]))
  story.append(HRFlowable(width="100%",thickness=1,color=SOFT,spaceAfter=13))
 elif s.startswith("## "):
  story.append(Paragraph(clean_line(s[3:]),style["h2"]))
 elif s.startswith("### "):
  story.append(Paragraph(clean_line(s[4:]),style["h3"]))
 elif s.startswith("- "):
  story.append(Paragraph("&#8226;&nbsp;"+clean_line(s[2:]),style["bullet"]))
 elif s.startswith("  ") and not s.startswith("    "):
  story.append(Paragraph(clean_line(s),style["path"]))
 elif s.startswith("---"):
  story.append(HRFlowable(width="100%",thickness=0.5,color=SOFT,spaceAfter=10))
 elif s.startswith("Version:") or s.startswith("Project:") or s.startswith("Status:") or s.startswith("Owner instruction:"):
  story.append(Paragraph(clean_line(s),style["meta"]))
 else:
  story.append(Paragraph(clean_line(s),style["body"]))

def header_footer(c,doc):
 c.saveState()
 w,h=A4
 c.setStrokeColor(SOFT);c.setLineWidth(.6)
 c.line(45,45,w-45,45)
 c.setFont(fbold,8);c.setFillColor(GREEN)
 c.drawString(45,h-31,"PIREVO  /  ASTRA LABS PH")
 c.setFont(font,8);c.setFillColor(MUTED)
 c.drawRightString(w-45,h-31,"CONTEXT TRANSFER  /  22 OCT 2026")
 c.drawString(45,29,"PIN SOP v3 hard lock  |  Direct Pinterest publishing only  |  No schedules")
 c.drawRightString(w-45,29,f"Page {doc.page}")
 c.restoreState()
doc=SimpleDocTemplate(str(dest),pagesize=A4,rightMargin=45,leftMargin=45,topMargin=50,bottomMargin=59,
 title="PIREVO Full Context Transfer - Canonical 2026-10-22",author="AstraLabs PH / PIREVO",subject="Website, growth roadmap, product inventory, Amazon OneLink, Pinterest creative SOP, approved published Pins, Batch2 pending approvals, next-step runbook",pageCompression=1)
doc.build(story,onFirstPage=header_footer,onLaterPages=header_footer)
print("PDF",dest)
print("PDF_BYTES",dest.stat().st_size)
print("SOURCE_CHARS",len(source),"FONT",font)
