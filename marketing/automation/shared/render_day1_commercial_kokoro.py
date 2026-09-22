#!/usr/bin/env python3
"""Six distinct Day 1 AstraLabs voice+subtitle marketing assets. Commercial-safe Kokoro, no HeyGen Free voice. Creates MEDIA only, no Buffer posts."""
import json, math, re, subprocess, hashlib, os, zipfile, urllib.request
from pathlib import Path
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/"public/marketing/campaigns/seven_day/day1"
OUT=Path("/tmp/astra-day1-release")
OUT.mkdir(parents=True,exist_ok=True); BASE.mkdir(parents=True,exist_ok=True)
ENGINE=Kokoro("/tmp/astra-kokoro-v1.0.onnx","/tmp/astra-kokoro-voices-v1.0.bin")
SOURCE=os.environ["ASTRALABS_DAY1_SOURCE_ZIP_URL"]
urllib.request.urlretrieve(SOURCE,str(OUT/"previews.zip"))
with zipfile.ZipFile(OUT/"previews.zip") as z:
    safe=[x for x in z.namelist() if x.startswith(("VIDEOS/","CAPTIONS/","QA/")) and ".." not in x]
    for x in safe:
        if x.endswith("/"):continue
        path=OUT/x;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(z.read(x))
SCRIPTS={
"S26D1AV":"The parcel weight looks acceptable. But will it fit the usable hold space? Those are separate checks. Astramate brings supported cargo weight, volume and stowage-factor tools into one Android toolkit with working to review. Always verify shipboard decisions against approved vessel information. Try it free at AstraLabs PH dot com. Which figure would you check next?",
"S26D1AC":"Before trusting a cargo estimate, record the cargo weight, stowage factor and usable volume. Check the units and review the working against approved data. Astramate collects supported cargo calculations in one toolkit. Find the free Android app at AstraLabs PH dot com.",
"S26D1AQ":"Cargo question: the weight looks fine, but space is tight. Would you review stowage factor, usable hold volume or both? Explain the input check, not a loading approval. Astramate shows working for supported cargo tools. Discover it at AstraLabs PH dot com.",
"S26D1KV":"Packing tonight? A passport photo may be saved, but did you check its expiry date on the original? Keep a safe document copy, the date you enter and supported reminders together with Keepry. Start free on Android at AstraLabs PH dot com. Which document do you check first before a trip?",
"S26D1KC":"Here's a short pre-trip routine: inspect the original document, record its actual expiry date, review your reminder settings and keep a safe backup. Keepry organizes imported records and entered dates in one local-first place. Explore the free Android app at AstraLabs PH dot com.",
"S26D1KQ":"Quick quiz: does saving a document photo automatically set a renewal reminder? No. You still need to verify the date and configure a supported reminder. Keepry helps keep the two together. What other deadline is on your travel checklist? AstraLabs PH dot com."
}
def stamp(t):
    n=int(round(t*1000));h,n=divmod(n,3600000);m,n=divmod(n,60000);s,ms=divmod(n,1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
def probe(p):
    return json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration:stream=codec_type,codec_name,width,height,r_frame_rate","-of","json",str(p)],text=True))
records=[]
for id,script in SCRIPTS.items():
    src=OUT/"VIDEOS"/f"{id}_ORIGINAL_9x16_MUSIC_PREVIEW_NOT_FINAL.mp4"
    if not src.is_file():raise RuntimeError("Missing source "+str(src))
    sentences=re.split(r"(?<=[.!?])\s+",script)
    voice="af_heart" if id[5]=="K" else "am_michael"
    # Sentence-level neural synthesis provides measured caption and voice timing, not guessed total-word timing.
    sr=24000; voice_chunks=[];subtitles=[];cursor=0.12;k=1
    for sentence in sentences:
        sound, fs=ENGINE.create(sentence,voice=voice,speed=1.12,lang="en-us")
        if fs!=sr:raise RuntimeError("Unexpected voice sample rate")
        snd=np.asarray(sound,dtype=np.float32)
        if not len(snd):raise RuntimeError("Neural TTS silence "+id)
        words=sentence.split()
        parts=[" ".join(words[t:t+7]) for t in range(0,len(words),7)]
        weights=[max(1,sum(len(w) for w in p.split())) for p in parts]
        total=sum(weights);start=cursor;duration=len(snd)/sr
        for part,weight in zip(parts,weights):
            finish=min(start+duration*weight/total,cursor+duration)
            subtitles += [str(k), stamp(start)+" --> "+stamp(finish),part,""]
            k+=1;start=finish
        voice_chunks.append((cursor,snd))
        cursor+=duration+0.08
    wav=np.zeros(int(math.ceil((cursor+0.15)*sr)),dtype=np.float32)
    for start,snd in voice_chunks:
        j=int(round(start*sr));wav[j:j+len(snd)]=snd
    voice_file=OUT/(id+"_kokoro_original.wav")
    sf.write(str(voice_file),wav,sr,subtype="PCM_16")
    subs=OUT/(id+".srt");subs.write_text("\n".join(subtitles),encoding="utf-8")
    old_len=float(probe(src)["format"]["duration"]);duration=round(max(old_len,cursor+0.5),1)
    final=BASE/(id+".mp4")
    filt=("[0:v]tpad=stop_mode=clone:stop_duration=16,trim=duration="+str(duration)
       +",scale=720:1090:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:0:color=0x102c30"
       +",subtitles="+str(subs)+":force_style='FontName=Montserrat,FontSize=8,Alignment=2,MarginV=9,BorderStyle=3,BackColour=&H99000000,Outline=1,Shadow=0'[v];"
       +"[0:a]volume=0.15,apad,atrim=duration="+str(duration)+"[bed];"
       +"[1:a]aresample=48000,volume=1.45,apad,atrim=duration="+str(duration)+"[speech];"
       +"[bed][speech]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.92,afade=t=out:st="
       +str(max(0,duration-.45))+":d=0.4[mix]")
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-nostdin","-y","-i",str(src),"-i",str(voice_file),"-filter_complex",filt,"-map","[v]","-map","[mix]","-t",str(duration),"-r","30","-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-movflags","+faststart",str(final)],check=True)
    checks=probe(final);v=next(x for x in checks["streams"] if x["codec_type"]=="video");a=next(x for x in checks["streams"] if x["codec_type"]=="audio")
    if not(v["codec_name"]=="h264" and v["width"]==720 and v["height"]==1280 and v["r_frame_rate"]=="30/1" and a["codec_name"]=="aac"):raise RuntimeError("Video/audio export invalid "+id)
    rec={"id":id,"app":"Keepry" if id[5]=="K" else "Astramate","file":"public/marketing/campaigns/seven_day/day1/"+id+".mp4","size":final.stat().st_size,"sha256":hashlib.sha256(final.read_bytes()).hexdigest(),"seconds":float(checks["format"]["duration"]),"voice":"Kokoro v1.0 ONNX, Apache 2.0, not HeyGen Free","music":"original mathematical synthesis from first-party Day1 music-only source","footage":"user-provided genuine released-app screen within new native vertical artwork","status":"TECH_QA_PASS_HUMAN_VISUAL_AUDIO_AND_NATIVE_ACCOUNT_QA_PENDING"}
    records.append(rec);print("DAY1_COMMERCIAL_CANDIDATE_RENDERED",id,rec["seconds"],rec["size"],flush=True)
(OUT/"day1_render_qa.json").write_text(json.dumps(records,indent=2)+"\n")
print("DAY1_KOKORO_ALL6_TECH_PASS_NOT_BUFFER_POSTED",flush=True)
