#!/usr/bin/env python3
from __future__ import annotations
import subprocess, shutil
from pathlib import Path
from PIL import Image, ImageFilter

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"public/pirevo/assets/pins/wave4-christmas"
OUT=ROOT/"public/pirevo/assets/social/christmas-wave4"
WORK=ROOT/"marketing/pirevo/.christmas-video-work"

GROUPS={
  "01_christmas-decor":["01_window-candles.jpg","02_tree-candles.jpg","03_prelit-garland.jpg","04_fairy-lights.jpg"],
  "02_kids-creative-gifts":["05_rock-painting-kit.jpg","06_magic-light-brush.jpg","07_crayola-art-case.jpg","08_playdoh-36.jpg"],
  "03_kids-teen-tech-gifts":["09_sticker-book.jpg","10_joycon.jpg","11_echo-dot.jpg","14_bluetooth-speaker.jpg"],
  "04_adult-host-cozy-gifts":["12_crockpot-lunchbox.jpg","13_charcuterie-board.jpg","15_stanley.jpg","20_bedsure-throw.jpg"],
  "05_adult-travel-creative-gifts":["16_lego-plants.jpg","17_jbl-clip.jpg","18_airtag.jpg","19_bagsmart.jpg"],
}
OUT.mkdir(parents=True,exist_ok=True)
WORK.mkdir(parents=True,exist_ok=True)
FFMPEG=shutil.which("ffmpeg")
if not FFMPEG:
    try:
        import imageio_ffmpeg
        FFMPEG=imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:
        raise SystemExit("ffmpeg unavailable; install ffmpeg or imageio-ffmpeg") from exc

def make_frame(src:Path,dst:Path):
    im=Image.open(src).convert("RGB")
    bg=im.resize((1080,1920),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(28))
    overlay=Image.new("RGBA",(1080,1920),(17,48,35,68))
    bg=Image.alpha_composite(bg.convert("RGBA"),overlay).convert("RGB")
    fg=im.resize((1080,1620),Image.Resampling.LANCZOS)
    bg.paste(fg,(0,150))
    bg.save(dst,quality=92,optimize=True)

for name,files in GROUPS.items():
    group=WORK/name;group.mkdir(parents=True,exist_ok=True)
    concat=[]
    for i,f in enumerate(files,1):
        src=SRC/f
        if not src.exists(): raise SystemExit(f"missing source {src}")
        frame=group/f"{i:02d}.jpg";make_frame(src,frame)
        concat.append(f"file '{frame.as_posix()}'\nduration 3\n")
    concat.append(f"file '{(group/'04.jpg').as_posix()}'\n")
    listfile=group/"concat.txt";listfile.write_text("".join(concat),encoding="utf-8")
    out=OUT/f"{name}.mp4"
    subprocess.run([FFMPEG,"-y","-f","concat","-safe","0","-i",str(listfile),"-vf","fps=30,format=yuv420p","-c:v","libx264","-preset","medium","-crf","20","-movflags","+faststart",str(out)],check=True)
print("PIREVO_CHRISTMAS_SOCIAL_VIDEO_OK count=5")
