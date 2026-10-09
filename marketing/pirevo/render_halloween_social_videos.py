#!/usr/bin/env python3
from __future__ import annotations
import subprocess
from pathlib import Path
from PIL import Image, ImageFilter

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"public/pirevo/assets/pins/wave3-halloween"
OUT=ROOT/"public/pirevo/assets/social/halloween-wave3"
WORK=ROOT/"marketing/pirevo/.halloween-video-work"

GROUPS={
  "01_outdoor-haunt":["01_zpisf-spider-webs.jpg","02_ocato-giant-spider-web.jpg","05_joyin-hanging-ghosts.jpg","06_aiseno-skeleton-stakes.jpg"],
  "02_webs-walls-cozy":["03_piteno-bat-wall.jpg","04_cyantor-creepy-cloth.jpg","15_sophena-ghost-door.jpg","16_miulee-ghost-pillows.jpg"],
  "03_lights-glow":["10_brizled-purple-orange.jpg","11_ljlnion-purple-lights.jpg","09_denicmic-solar-path.jpg","08_goothy-pumpkin-path.jpg"],
  "04_porch-party":["14_hexagram-doormat.jpg","12_eldnacele-skull-candles.jpg","13_homemory-tealights.jpg","07_goosh-skeleton-puppy.jpg"],
}

OUT.mkdir(parents=True,exist_ok=True)
WORK.mkdir(parents=True,exist_ok=True)

def make_frame(src:Path,dst:Path):
    im=Image.open(src).convert("RGB")
    # 9:16 background from the same creative, blurred and darkened.
    bg=im.resize((1080,1920),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(28))
    overlay=Image.new("RGBA",(1080,1920),(0,0,0,80))
    bg=Image.alpha_composite(bg.convert("RGBA"),overlay).convert("RGB")
    fg=im.resize((1080,1620),Image.Resampling.LANCZOS)
    bg.paste(fg,(0,150))
    bg.save(dst,quality=92,optimize=True)

for name,files in GROUPS.items():
    group_dir=WORK/name
    group_dir.mkdir(parents=True,exist_ok=True)
    concat=[]
    for i,f in enumerate(files,1):
        src=SRC/f
        if not src.exists():
            raise SystemExit(f"missing source {src}")
        frame=group_dir/f"{i:02d}.jpg"
        make_frame(src,frame)
        concat.append(f"file '{frame.as_posix()}'\nduration 3\n")
    # ffmpeg concat demuxer needs the final image repeated.
    concat.append(f"file '{(group_dir/'04.jpg').as_posix()}'\n")
    listfile=group_dir/"concat.txt"
    listfile.write_text("".join(concat),encoding="utf-8")
    out=OUT/f"{name}.mp4"
    subprocess.run([
      "ffmpeg","-y","-f","concat","-safe","0","-i",str(listfile),
      "-vf","fps=30,format=yuv420p",
      "-c:v","libx264","-preset","medium","-crf","20",
      "-movflags","+faststart",str(out)
    ],check=True)
    print(out)

print("PIREVO_HALLOWEEN_SOCIAL_VIDEO_OK count=4")
