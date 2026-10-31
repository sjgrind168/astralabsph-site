#!/usr/bin/env python3
"""AstraLabs zero-cost operations controller: source-backed pipeline triage.

No secret values in reports, no guessed conversions, no uncontrolled deploys.
Publishing mutations are handled by separately-tested, idempotent campaign jobs.
"""
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "tools" / "growth_operator" / "out"
ISSUE_TITLE = "AstraLabs Growth Operator | Open publishing and website blockers"
REPO = os.getenv("GH_REPO", "sjgrind168/astralabsph-site")
WATCH = {
    "Facebook": "astralabs-daily-two-per-app.yml",
    "Pinterest apps": "astralabs-pinterest-queue.yml",
    "TikTok": "astralabs-tiktok-video.yml",
}
BASE = "https://www.astralabsph.com"
SITES = [(p, BASE + p) for p in ("/", "/astramate/", "/keepry/", "/pirevo/", "/merchlab/")] + [("pirevo-claimed-domain", "https://pirevo.astralabsph.com/")]


def gh(*args):
    r = subprocess.run(["gh", *args], text=True, capture_output=True, timeout=60)
    if r.returncode:
        raise RuntimeError("gh command failed " + " ".join(args[:3]) + ": " + r.stderr[:250])
    return r.stdout


def latest(workflow):
    runs = json.loads(gh("run", "list", "-R", REPO, "--workflow", workflow,
                         "--limit", "8", "--json",
                         "databaseId,conclusion,status,createdAt,headBranch"))
    return next((x for x in runs if x["status"] == "completed" and
                 x["headBranch"] == "main"), None)


def workflow_check():
    blockers = []
    summaries = {}
    for channel, name in WATCH.items():
        try:
            run = latest(name)
            if not run:
                blockers.append(channel + ": no completed main-branch run")
                summaries[channel] = {"state": "unverified"}
                continue
            log = gh("run", "view", str(run["databaseId"]), "-R", REPO, "--log")
            observations = []
            if "NO_APPROVED_CURRENT_3DAY_CANDIDATES" in log:
                observations.append("no approved current campaign candidates")
                blockers.append(channel + ": campaign expired, no publishable content")
            if "APPROVED_CONTENT_EXHAUSTED" in log:
                observations.append("approved content exhausted")
                blockers.append(channel + ": content exhausted; refiller must recover")
            match = re.findall(r"DAILY_EDITORIAL_COMPLETE created (\d+)", log)
            if match:
                observations.append("confirmed scheduled creates=" + match[-1])
            created = len(re.findall(r"EDITORIAL_SCHEDULED\s", log))
            if created:
                observations.append("Buffer scheduled confirmations=" + str(created))
            if run["conclusion"] != "success":
                blockers.append(channel + ": GitHub run " + str(run["conclusion"]))
            summaries[channel] = {
                "state": run["conclusion"], "run": run["databaseId"],
                "observations": observations or ["no publish confirmation observed"]
            }
        except Exception as e:
            summaries[channel] = {"state": "unavailable", "reason": str(e)[:140]}
            blockers.append(channel + ": could not verify latest workflow")
    return summaries, blockers


def website_check():
    site = {}
    problems = []
    for path, url in SITES:
        req = urllib.request.Request(url,
                headers={"User-Agent": "AstraLabs-Operations-Health/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read(8192)
                ok = resp.status == 200 and (
                    b"<html" in data.lower() or b"<!doctype" in data.lower())
                if path == "pirevo-claimed-domain":
                    ok = ok and b"pirevo" in data.lower()
                site[path] = {"http": resp.status, "html": bool(ok)}
                if not ok:
                    problems.append("Website " + path + ": HTTP 200/HTML check failed")
        except Exception as e:
            site[path] = {"state": "unavailable", "reason": type(e).__name__}
            problems.append("Website " + path + ": unavailable ("+type(e).__name__+")")
    return site, problems


def affiliate_check():
    proc = subprocess.run(["node", "tests/pirevo-affiliate-links.cjs"],
                          cwd=ROOT, text=True, capture_output=True, timeout=80)
    # Never include private links, tokens or product identifiers in public issue body.
    return ({"passed": proc.returncode == 0},
            [] if proc.returncode == 0 else
            ["PIREVO link attribution contract: tests failed; inspect job logs"])


def update_issue(blockers):
    if not os.getenv("GH_TOKEN"):
        return "skipped (no authenticated GitHub token)"
    rows = json.loads(gh("issue", "list", "-R", REPO, "--state", "open", "--limit", "100",
                         "--json", "number,title,body"))
    existing = next((x for x in rows if x["title"] == ISSUE_TITLE), None)
    if not blockers:
        if existing:
            gh("issue", "close", str(existing["number"]), "-R", REPO,
               "--comment", "All monitored blockers cleared by the latest verified checks.")
            return "closed #" + str(existing["number"])
        return "none open"
    body = ("Automated public-surface operations tracker. A GitHub Actions SUCCESS "
            "does not prove a social post was published.\n\n"
            "### Verified current blockers\n" +
            "".join("- " + x + "\n" for x in sorted(set(blockers))) +
            "\n### Operator action\n"
            "Fix the root cause with tested, reversible changes; reconcile Buffer/native "
            "post status; verify before/after IDs and clicks separately. No fabricated sales.\n")
    if existing:
        if (existing.get("body") or "").strip() == body.strip():
            return "unchanged #" + str(existing["number"])
        gh("issue", "edit", str(existing["number"]), "-R", REPO, "--body", body)
        return "updated #" + str(existing["number"])
    gh("issue", "create", "-R", REPO, "--title", ISSUE_TITLE, "--body", body)
    return "created"


def main():
    workflow, blockers = workflow_check()
    sites, site_problems = website_check()
    affiliate, affiliate_problems = affiliate_check()
    blockers.extend(site_problems + affiliate_problems)
    result = {"checked_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "workflow": workflow, "websites": sites, "affiliate": affiliate,
              "blockers": sorted(set(blockers)),
              "note": "Scheduled posts are not verified published posts; no sales inferred."}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "status.json").write_text(json.dumps(result, indent=2) + "\n")
    try:
        result["issue_sync"] = update_issue(blockers)
    except Exception as e:
        result["issue_sync"] = "failed: " + type(e).__name__
        blockers.append("Operator issue sync failed: check GitHub issue permissions")
    (OUT / "status.json").write_text(json.dumps(result, indent=2) + "\n")
    print("ASTRALABS_OPERATOR", json.dumps({
        "checked": result["checked_at_utc"], "blockers": len(set(blockers)),
        "issue_sync": result["issue_sync"], "facebook": workflow.get("Facebook")}))
    summary = os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as f:
            f.write("## AstraLabs Growth Operations\n\n")
            f.write("Monitored blockers: **"+str(len(set(blockers)))+"**.\n\n")
            for b in sorted(set(blockers)):
                f.write("- "+b+"\n")
            f.write("\nDetails in run artifact status.json.\n")
    if not affiliate["passed"] or site_problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
