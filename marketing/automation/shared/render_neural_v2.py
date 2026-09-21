#!/usr/bin/env python3
"""One-time, commercial-use-permissive Kokoro V2 voice PREVIEWS. No social posting."""
from pathlib import Path
import json
import math
import subprocess
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "public" / "marketing"
MODEL = Path("/tmp/astra-kokoro-v1.0.onnx")
VOICES = Path("/tmp/astra-kokoro-voices-v1.0.bin")
OUT = BASE / "previews"
OUT.mkdir(parents=True, exist_ok=True)
DURATION = 16.0
FS = 48000
ENGINE = Kokoro(str(MODEL), str(VOICES))
CAMPAIGNS = (
    ("astramate", "am_michael",
     "Still juggling maritime calculations? From voyage and compass to cargo, draft, and trim, Astramate keeps your tools together. Get Astramate on Android."),
    ("keepry", "af_heart",
     "Too many dates and documents to remember? Keepry brings your records, renewals, tasks, and reminders together. Get Keepry on Android."),
)

def make_music(app, dest):
    """Generate our own instrumental bed from mathematical oscillators; no stock/music rights."""
    count = int(DURATION * FS)
    t = np.arange(count, dtype=np.float64) / FS
    seed = 20260922 if app == "astramate" else 20260923
    rng = np.random.default_rng(seed)
    prog = ([146.83, 174.61, 130.81, 164.81] if app == "astramate"
            else [196.0, 220.0, 174.61, 261.63])
    out = np.zeros(count, dtype=np.float64)
    # Evolving four-chord airy pad, with octave shimmer, warm bass, and light transient pulse.
    for bar, root in enumerate(prog):
        x = t - bar * 4
        active = np.maximum(0, np.minimum(1, x / 0.27)) * np.maximum(0, np.minimum(1, (4-x) / 0.4))
        active *= ((x >= 0) & (x < 4))
        for ratio, level in ((1.0, .30), (1.25, .20), (1.5, .22), (2.0, .11)):
            f = root * ratio
            out += active * level * (np.sin(2*np.pi*f*t) + 0.19*np.sin(4*np.pi*f*t))
    for b in np.arange(0, 16, (1.6 if app == "astramate" else 1.0)):
        ix = int(b * FS)
        size = min(int(.18*FS), count-ix)
        if size <= 0: continue
        tt = np.arange(size) / FS
        hit = np.sin(2*np.pi*(780 if app == "astramate" else 1080)*tt) * np.exp(-tt*31)
        out[ix:ix+size] += (0.075 if app == "astramate" else 0.065)*hit
    out += .0012*rng.standard_normal(count) * (0.5 + .5*np.sin(2*np.pi*0.17*t))
    out *= np.minimum(1., t/.4) * np.minimum(1., (DURATION-t)/.55)
    out /= max(1, float(np.max(np.abs(out)))*2.5)
    sf.write(str(dest), out.astype("float32"), FS, subtype="PCM_16")

def run(cmd):
    subprocess.run(cmd, check=True)

def make_one(app, voice, text):
    src = BASE / "videos" / (app + "_16sec_vertical_motion_ad.mp4")
    if not src.is_file():
        raise RuntimeError("Missing original approved video: "+str(src))
    raw = OUT / (app + "_v2_neural_voice_raw.wav")
    bed = OUT / (app + "_v2_original_music.wav")
    final = OUT / (app + "_v2_neural_voice_music_PREVIEW.mp4")
    audio, sr = ENGINE.create(text, voice=voice, speed=1.08, lang="en-us")
    sf.write(str(raw), audio, sr, subtype="PCM_16")
    duration = len(audio) / sr
    print("VOICE_SPEAK_DURATION",app,round(duration,2),"sec",flush=True)
    if duration < 8 or duration > 15.2:
        raise RuntimeError("Narration does not fit approved 16s storyboard; rewrite and rerun before any publishing")
    make_music(app, bed)
    run(["ffmpeg","-hide_banner","-nostdin","-loglevel","error","-y",
         "-i",str(src),"-i",str(raw),"-i",str(bed),
         "-filter_complex",
         "[1:a]aresample=48000,pan=stereo|c0=c0|c1=c0,adelay=180|180,volume=1.2,apad,atrim=duration=16[voice];"
         "[2:a]aresample=48000,volume=0.15,atrim=duration=16[bed];"
         "[voice][bed]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.90,afade=t=out:st=15.6:d=0.4[mix]",
         "-map","0:v:0","-map","[mix]","-c:v","copy","-c:a","aac","-b:a","192k",
         "-t","16","-movflags","+faststart",str(final)])
    verify = subprocess.check_output(["ffprobe","-v","error","-show_entries",
         "stream=codec_type,codec_name:format=duration",
         "-of","json",str(final)],text=True)
    v=json.loads(verify)
    streams=v["streams"]
    if {s.get("codec_type") for s in streams} != {"video","audio"}:
        raise RuntimeError("Final video lacks one required stream")
    if abs(float(v["format"]["duration"]) - 16.0) > 0.13:
        raise RuntimeError("Unexpected final duration")
    print("V2_PREVIEW_RENDERED",app,str(final),"bytes",final.stat().st_size,flush=True)

for job in CAMPAIGNS:
    make_one(*job)
print("V2_PREVIEWS_COMPLETE. Neither clip was submitted to Buffer. Owner sound and visual QA required.",flush=True)
