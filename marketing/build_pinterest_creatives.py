#!/usr/bin/env python3
"""Render original, product-accurate 2:3 organic Pinterest PNGs, no fake app screenshots.

Requires Pillow. Uses existing official app icons, only system fonts, and curated copy.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import re

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "public" / "marketing" / "pins"
DEST.mkdir(parents=True, exist_ok=True)
W, H = 1000, 1500
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BANK = [
    ("astramate_eta", "Astramate", "Need to estimate\nyour ETA?", "VOYAGE • TIME • DISTANCE", "Explore the FREE core toolkit.", "astramate"),
    ("keepry_vault", "Keepry", "Where did you\nsave that document?", "PRIVATE VAULT • IMAGES • PDFS", "Keep your records findable.", "keepry"),
    ("astramate_compass", "Astramate", "Compass error\nto check?", "OBSERVATION • TRUE BEARING", "Start with a FREE core calculator.", "astramate"),
    ("keepry_validity", "Keepry", "Important expiry\ndates, organized.", "PASSPORTS • LICENCES • RECORDS", "Find dates in one personal space.", "keepry"),
    ("astramate_cargo", "Astramate", "Cargo figures\nat your fingertips.", "STOWAGE • VOLUME • WEIGHT", "See the formulas and working.", "astramate"),
    ("keepry_reminders", "Keepry", "Less scattered\nlife admin.", "DUE DATES • TASKS • REMINDERS", "Start with Keepry Free.", "keepry"),
    ("astramate_trim", "Astramate", "Quick draft and\ntrim checks.", "MEAN DRAFT • TRIM", "Explore the FREE core tools.", "astramate"),
    ("keepry_people", "Keepry", "Whose document\nis this?", "PEOPLE • DOCUMENTS • TASKS", "Organize records by person.", "keepry"),
    ("astramate_tools", "Astramate", "Maritime tools,\none pocket.", "VOYAGE • COMPASS • CARGO", "11 FREE tools • More with Premium.", "astramate"),
    ("keepry_organize", "Keepry", "Your documents.\nYour dates.\nOne place.", "VAULT • VALIDITY • ADMIN", "Start free on Android.", "keepry"),
]

def font(size, strong=False):
    return ImageFont.truetype(BOLD if strong else FONT, size=size)

def lines(draw, text, left, top, f, fill, gap=19):
    spacing = f.size + gap
    for i, line in enumerate(text.split("\n")):
        draw.text((left, top + i * spacing), line, font=f, fill=fill, stroke_width=0)
    return top + len(text.split("\n")) * spacing

def poster(item):
    filename, brand, title, label, sub, family = item
    dark = family == "astramate"
    base = (8, 25, 44) if dark else (3, 44, 34)
    accent = (110, 219, 204) if dark else (140, 243, 174)
    ivory = (242, 253, 250)
    canvas = Image.new("RGB", (W, H), base)
    p = canvas.load()
    # Gentle linear gradient, rendered locally; no stock imagery or invented app UI.
    for y in range(H):
        f = y / H
        for x in range(W):
            radial = max(0, 1 - math.hypot(x - 820, y - 210) / 1060)
            p[x, y] = tuple(int(min(255, base[i] + (35 if dark else 26) * radial * (1 - f * .38))) for i in range(3))
    d = ImageDraw.Draw(canvas, "RGBA")
    d.ellipse((545, -115, 1220, 570), outline=(*accent, 80), width=4)
    d.ellipse((600, -65, 1170, 505), outline=(*accent, 45), width=3)
    d.rounded_rectangle((74, 70, 926, 1432), radius=48, outline=(*accent, 65), width=2)
    # Product icon from actual AstraLabs site repository.
    icon_path = ROOT / ("src/assets/app-icons/astramate.png" if dark else "public/keepry-icon.webp")
    icon = Image.open(icon_path).convert("RGBA")
    icon.thumbnail((116, 116), Image.Resampling.LANCZOS)
    canvas.paste(icon, (98, 106), icon)
    d = ImageDraw.Draw(canvas, "RGBA")
    d.text((238, 122), "ASTRALABS PH  /  " + brand.upper(), fill=ivory, font=font(31, True))
    d.rounded_rectangle((98, 310, 902, 365), radius=20, fill=(*accent, 36))
    d.text((118, 318), label, fill=accent, font=font(23, True))
    y = lines(d, title, 98, 460, font(68, True), ivory, gap=25)
    d.rounded_rectangle((98, max(830, y + 36), 902, max(836, y + 42)), radius=4, fill=(*accent, 230))
    d.text((98, max(888, y + 90)), sub, fill=(220, 243, 238), font=font(31))
    d.rounded_rectangle((98, 1158, 902, 1255), radius=22, fill=(*accent, 255))
    d.text((125, 1184), "GET " + brand.upper() + " ON GOOGLE PLAY", fill=(10, 39, 31), font=font(30, True))
    d.text((98, 1303), "Android available now  •  iOS coming soon", fill=ivory, font=font(22))
    d.text((98, 1354), "astralabsph.com/" + brand.lower(), fill=accent, font=font(26, True))
    path = DEST / (filename + ".png")
    canvas.save(path, format="PNG", optimize=True)
    print(path.relative_to(ROOT), path.stat().st_size)

if __name__ == "__main__":
    for element in BANK:
        poster(element)
