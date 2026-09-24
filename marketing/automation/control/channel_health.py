#!/usr/bin/env python3
"""Three real existing AstraLabs channel workflow health feeds, PUBLIC-SAFE READ ONLY.

Never queries private Buffer API, never publishes or exposes account secrets.
GitHub Action run success != Buffer queued or native post live.
"""
import json,os,time,urllib.request,urllib.error
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import quote
HERE=Path(__file__).resolve().parent
CFG=json.loads((HERE/"channels.json").read_text(encoding="utf-8"))
ROOT=Path(__file__).resolve().parents[3]
EXPECTED={
 "facebook":".github/workflows/astralabs-daily-two-per-app.yml",
 "pinterest":".github/workflows/astralabs-pinterest-queue.yml",
 "tiktok":".github/workflows/astralabs-tiktok-video.yml",
}
URL="https://api.github.com/repos/sjgrind168/astralabsph-site/actions/workflows/"
def recent(path):
    file=path.rsplit("/",1)[-1]
    headers={"Accept":"application/vnd.github+json",
             "User-Agent":"AstraLabs-Marketing-Control-ReadOnly/1.0"}
    # Use the existing scoped Actions token to avoid the public unauthenticated API limit.
    # Do not log the token or include it in generated public reports.
    token=os.getenv("GITHUB_TOKEN","").strip()
    if token:
        headers["Authorization"]="Bearer "+token
    req=urllib.request.Request(URL+quote(file)+"/runs?per_page=1",headers=headers)
    try:
        with urllib.request.urlopen(req,timeout=20) as response:
            payload=json.load(response)
    except urllib.error.HTTPError as error:
        if error.code in (403,429):
            return {"workflow_status":"API_RATE_LIMITED","run_url":None,
                    "started_at":None,"conclusion":None}
        raise
    rows=payload.get("workflow_runs") or []
    if not rows:return {"workflow_status":"NEVER_RUN_OR_NOT_VISIBLE","run_url":None,
                        "started_at":None,"conclusion":None}
    run=rows[0]
    return {"workflow_status":str(run.get("status") or "unknown"),
            "conclusion":run.get("conclusion"),
            "started_at":run.get("created_at"),
            "run_url":run.get("html_url")}
def main():
    statuses={}
    for name,path in EXPECTED.items():
        cfg=CFG["channel_routing"].get(name) or {}
        assert cfg.get("writer_workflow")==path, "Registry and real writer differ for "+name
        assert (ROOT/path).is_file(),"Writer YAML missing: "+path
        s=recent(path)
        # Retain the precise source-of-truth mode. A successful preflight does NOT
        # turn blocked Pinterest/TikTok writes into an active posting status.
        if name=="facebook":
            publication=("THREE_PER_APP_DAILY_WRITER_CONFIGURED_BUT_BUFFER_RATE_LIMITED" if s["conclusion"]=="failure" else "THREE_PER_APP_DAILY_WRITER_CONFIGURED; NATIVE_POST_COUNTS_UNVERIFIED")
        elif name=="pinterest":
            publication="WRITE_HELD_PENDING_ROOT_ONLY_ARTWORK_AND_BOARD_API"
        else:
            publication="FIRST_WAVE_ONLY_AUTO_NEW_VIDEO_WRITES_HELD"
        statuses[name]={
            "workflow_file":path,
            "provider":cfg["provider"],
            "configured_mode":cfg["mode"],
            "publication_status":publication,
            **s,
            "live_native_post_verified_by_this_report":False,
            "buffer_queue_counts_verified_by_this_report":False,
            "analytics_connected":False,
            "notice":"This is the exact GitHub Action health signal only, not live Buffer or native-platform proof."
        }
        print("CHANNEL_HEALTH",name,s["workflow_status"],str(s["conclusion"]),
              publication,s["run_url"],flush=True)
    out=HERE/"out"
    out.mkdir(exist_ok=True)
    now=datetime.now(timezone.utc).isoformat()
    data={"as_of_utc":now,"source":"Public GitHub Actions latest-run API; zero Buffer credentials or private data",
          "site":"https://www.astralabsph.com/","channels":statuses,
          "private_engagement_metrics":"NOT_CONNECTED; requires owner-scoped secure backend and relevant API authorization",
          "publishing_mutations_performed":0}
    (out/"channel_health.json").write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
    lines=["# AstraLabs three-channel workflow-health connections","",
        "Updated (UTC): "+now,"",
        "Read-only GitHub Actions execution signals, **not** Buffer queue totals, "
        "native post confirmation or engagement/sales analytics.","",
        "| Channel | Exact existing writer | Most recent run | Publishing gate |",
        "|---|---|---|---|"]
    for name,s in statuses.items():
        result=(s["workflow_status"]+" / "+str(s["conclusion"]))
        if s["run_url"]:result="["+result+"]("+s["run_url"]+")"
        lines.append("| "+name.title()+" | `"+s["workflow_file"]+"` | "+result+
                     " | "+s["publication_status"]+" |")
    lines+=["","No new accounts created; no workflows rerun; no social changes made.",
       "Keep only the already-approved Facebook writer. Pinterest and TikTok write holds remain.",
       "Dashboard/private analytics connection: NOT DONE; public viewer must never show private Buffer or Play Console metrics."]
    md="\n".join(lines)+"\n"
    (out/"channel_health.md").write_text(md,encoding="utf-8")
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf-8") as f:f.write(md)
    print("CONTROL_THREE_EXISTING_CHANNELS_MAPPED_NO_PUBLISHING",flush=True)
if __name__=="__main__":main()
