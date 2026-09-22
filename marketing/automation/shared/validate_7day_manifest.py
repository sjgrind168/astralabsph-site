#!/usr/bin/env python3
"""Read-only 7-day marketing plan validation; DOES NOT approve media or publish."""
import json,re
from collections import Counter
from datetime import date,timedelta
from pathlib import Path
p=Path(__file__).with_name("ASTRALABS_7DAY_42_CREATIVE_MANIFEST_20260923.json")
b=json.loads(p.read_text(encoding="utf-8"))
rows=b["content"]
assert b["activation"].startswith("PLANNING_ONLY")
assert b["root_destination"]=="https://www.astralabsph.com/"
assert len(rows)==42 and len({r["id"] for r in rows})==42
expected={"voiceover_video":14,"carousel":14,"education_question_image":14}
assert dict(Counter(r["format"] for r in rows))==expected
for i in range(7):
    day=date(2026,9,23)+timedelta(days=i)
    for app in ("Astramate","Keepry"):
        subset=[r for r in rows if r["date"]==day.isoformat() and r["app"]==app]
        assert len(subset)==3,(day,app,len(subset))
        assert {r["format"] for r in subset}==set(expected)
        assert len({r["slot_ph"] for r in subset})==3
for r in rows:
    assert r["destination"].startswith("https://www.astralabsph.com/?utm_source=facebook&")
    assert "&app="+r["app"].lower() in r["destination"]
    assert r["root"]=="https://www.astralabsph.com/"
    assert r["approval"]=="PLANNED_ASSETS_NOT_RENDERED_NO_AUTOPUBLISH"
    assert r["asset_path"] is None
    assert r["hook"] and r["proof_asset_spec"] and r["creative_instructions"]
    assert len(r["qa_gates"])>=8
    caption=r["caption_facebook"]
    assert r["destination"] in caption and r["root"] in caption
    assert "one-time" in caption and ("Free" in caption or "free" in caption)
    assert "https://www.astralabsph.com/astramate/" not in caption
    assert "https://www.astralabsph.com/keepry/" not in caption
    assert "astramate.vercel.app" not in caption
    assert not re.search(r"\bETA\b",caption,re.I)
    assert r["caption_tiktok"] is None or len(r["caption_tiktok"])<=150
    if r["format"]=="voiceover_video":
        words=len(r["voiceover"].split())
        assert 42<=words<=82,(r["id"],words)
        assert "astralabsph.com" in r["voiceover"]
        assert r["caption_tiktok"] is not None
    else:
        assert r["voiceover"] is None and r["caption_tiktok"] is None
print("SEVEN_DAY_PLAN_QA_PASS: 42 unique briefs, 14 voiceover scripts, 14 carousels, 14 images, root-only campaign links.")
print("MEDIA_NOT_YET_RENDERED_OR_APPROVED: no 3-post/day publishing activation or account mutations made.")
