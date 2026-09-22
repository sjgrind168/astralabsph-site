#!/usr/bin/env python3
"""AstraLabs marketing control center: read-only ledger, never social publishing."""
import json
import os
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[3]
CONTROL = Path(__file__).resolve().parent
CFG = json.loads((CONTROL / "channels.json").read_text(encoding="utf-8"))
PLAN = json.loads((ROOT / CFG["source_7day_manifest"]).read_text(encoding="utf-8"))
ITEMS = PLAN.get("content", [])
assert CFG["activation"].startswith("READ_ONLY"), "This program must never publish"
assert len(ITEMS) == 42, "Expected 42 records; require explicit plan schema update"
assert len({x["id"] for x in ITEMS}) == len(ITEMS), "Duplicate creative IDs"
counts = Counter((x["date"], x["app"]) for x in ITEMS)
assert len(counts) == 14 and all(v == 3 for v in counts.values()), "Expected 3 creative concepts per app per day for seven days"
allowed = {"Astramate", "Keepry"}
assert {x["app"] for x in ITEMS} == allowed
for item in ITEMS:
    assert item.get("approval") and item["approval"] != "PUBLISHED", "Do not call planning-only creative published"
    target = urlsplit(item["destination"])
    assert target.scheme == "https" and target.netloc == "www.astralabsph.com" and target.path == "/", "Root-only campaign destination required"
    assert item["app"].lower() in item["destination"] and item["id"] in item["destination"], "Campaign/app tracking missing"
    assert item.get("caption_facebook") and "www.astralabsph.com/" in item["caption_facebook"]
    assert item.get("qa_gates") and isinstance(item["qa_gates"], list)
    # Actual completed media may be added by Work, but cannot be approved without explicit audit.
    if item.get("approval") == "PLANNED_ASSETS_NOT_RENDERED_NO_AUTOPUBLISH":
        assert item.get("asset_path") is None, "Asset attached without changing its QA status: reconcile"
channels = CFG["channel_routing"]
assert len(channels) >= 7
for name, channel in channels.items():
    workflow = channel.get("writer_workflow")
    if workflow:
        assert (ROOT / workflow).is_file(), "Configured workflow missing for " + name
    assert channel.get("gate") and channel.get("mode")
active_facebook = channels["facebook"]["writer_workflow"]
assert active_facebook == ".github/workflows/astralabs-daily-two-per-app.yml", "Do not activate a duplicate Facebook writer"
assert "READ_ONLY" in CFG["activation"] and CFG["official_storefront"] == "https://www.astralabsph.com/"
ready = [x for x in ITEMS if x.get("asset_path") and x.get("approval") not in ("PLANNED_ASSETS_NOT_RENDERED_NO_AUTOPUBLISH", "HOLD")]
hold = [x for x in ITEMS if x.get("approval") == "HOLD"]
planned = len(ITEMS) - len(ready) - len(hold)
lines = [
    "# AstraLabs PH Marketing Control Center",
    "",
    "**Report:** read-only planning/QA inventory, not a live Buffer or native-platform post status.",
    "**Storefront:** " + CFG["official_storefront"],
    "**Activation:** " + CFG["activation"],
    "",
    "## Production readiness",
    f"- Total creative records: **{len(ITEMS)}**",
    f"- Ready-for-human-QA records (not necessarily publishable): **{len(ready)}**",
    f"- Planning-only records: **{planned}**",
    f"- Explicit holds: **{len(hold)}**",
    "",
    "## Seven-day content ledger (unique concepts, not platform post counts)",
    "| Day (PHT) | Astramate | Keepry |",
    "|---|---:|---:|",
]
for day in sorted({k[0] for k in counts}):
    lines.append(f"| {day} | {counts[(day, 'Astramate')]} | {counts[(day, 'Keepry')]} |")
lines += ["", "## Platform gates", "| Platform | Current configured mode | Pending gate |", "|---|---|---|"]
for name, channel in channels.items():
    lines.append(f"| {name} | {channel['mode']} | {channel['gate'].replace('|', '/')} |")
lines += [
    "", "## Authoritative links",
    "- [Marketing global SOP](../shared/ASTRALABS_GLOBAL_GROWTH_SOP_20260922.md)",
    "- [Seven-day creative manifest](../shared/ASTRALABS_7DAY_42_CREATIVE_MANIFEST_20260923.json)",
    "- [Three-platform 3/app/day publishing SOP](../shared/ASTRALABS_THREE_CHANNEL_PUBLISHING_SOP_20260922.md)",
    "- [Latest connected-chat execution return](../shared/ASTRALABS_THREE_CHANNEL_EXECUTION_RETURN_20260922_1907PHT.md)",
    "- [Historical Work return handoff](../shared/ASTRALABS_WORK_RETURN_HANDOFF_20260922.md)",
    "",
    "## Fail-closed next steps",
    "1. Keep the existing SINGLE Facebook 3/app/day writer; it is enabled but Buffer HTTP 429 prevents claims of verified live delivery. Do not create a parallel Facebook writer.",
    "2. Preserve the 42-item plan as six original concepts/day; distribute across three channels only with actual approved platform-specific media and per-channel dueAt/native permalink.",
    "3. Pinterest 3/app/day check configured but WRITE HELD: approve genuinely new root-printed 2:3 media, exact Apps board serviceId, and native proof before enabling.",
    "4. TikTok 3/app/day check configured but WRITE HELD: existing Keepry first-wave ID must be reconciled and distinct new 30fps masters approved. Other channels retain their gates; native permalink is required for LIVE.",
    "5. Reconcile API limits and existing scheduled/sent/error/draft posts before every new write. Never publish from this inventory script.",
]
report = "\n".join(lines) + "\n"
out = CONTROL / "out"
out.mkdir(exist_ok=True)
(out / "control_status.md").write_text(report, encoding="utf-8")
(out / "control_status.json").write_text(json.dumps({
    "total_creatives": len(ITEMS),
    "planning_only": planned,
    "ready_for_review": len(ready),
    "explicit_holds": len(hold),
    "platform_modes": {k: v["mode"] for k, v in channels.items()},
    "publication_proof": "NOT_CHECKED; this script makes no Buffer or platform requests",
}, indent=2) + "\n", encoding="utf-8")
summary = os.getenv("GITHUB_STEP_SUMMARY")
if summary:
    with open(summary, "a", encoding="utf-8") as f:
        f.write(report)
print("CONTROL_CENTER_READ_ONLY_PASS 42 originals; 3 each app/day; 7 days; main site; no social writes")
print("CREATIVE_STATUS planned", planned, "review_candidates", len(ready), "hold", len(hold))
print("REPORT", out / "control_status.md")
