#!/usr/bin/env python3
"""Surgical text-only upgrade of legacy scheduled Facebook captions; preserve schedule and asset state."""
import importlib.util,json,os,re,sys
from datetime import datetime,timezone,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("fb_legacy_edit",ROOT/"buffer_facebook.py")
fb=importlib.util.module_from_spec(spec);spec.loader.exec_module(fb)
BANK=json.loads((ROOT/"buffer_facebook_content.json").read_text(encoding="utf-8"))["posts"]
COPY={
"fb_a02":"Before you use a compass reading, check what your inputs actually mean. Astramate's supported Compass Error tool shows the calculation steps using an observed compass direction and an independently verified true bearing or approved azimuth. Review the figures clearly, then independently verify any operational decision.",
"fb_a03":"You have the cargo weight, but will the parcel fit the hold? Astramate brings stowage factor, cargo weight and volume calculations together with visible working, so you can check the relationship between your own entered numbers before comparing with approved vessel data.",
"fb_a04":"Forward and aft draft marks tell different parts of the story. Astramate lets you work through supported simple mean draft and trim calculations, with visible working for a clearer independent review of your shipboard numbers.",
"fb_a05":"A loading check rarely comes down to one number. Astramate brings supported cargo, draft, trim and compass calculations into one maritime toolkit, with visible steps so you can inspect the inputs before professional verification.",
"fb_k01":"An important document is in your camera roll, while its expiry date is buried elsewhere. Keepry brings imported files, user-entered important dates and reminders together in a local-first personal Vault so the record and next step are easier to review.",
"fb_k02":"Passport, licence, insurance: each important document has its own renewal date. Organize the files and the dates you enter in Keepry Validity and configure reminders to help plan ahead. No more relying on a scattered set of notes to find your next step.",
"fb_k03":"Ever searched your phone for a PDF you saved months ago? Keepry Vault gives your images and PDFs a dedicated local-first home with searchable details, so important records are easier to organize and review when you need them.",
"fb_k04":"A family paperwork task is easier when its document and deadline are in the same organizer. Keepry combines a personal Vault, important dates, Life Admin tasks and reminders to help you review everyday responsibilities together.",
"fb_k05":"Managing important records for more than one person? Keepry Plus expands supported People-profile and document allowances and recurring reminders. Start with the free essentials on Android and explore the optional one-time upgrade when you need additional capacity."
}
ROOT_URL="https://www.astralabsph.com/"
def history(org):
    query=("query { posts(first:100,input:{organizationId:"+fb.quoted(org)+
           ",filter:{status:[scheduled],channelIds:["+fb.quoted(fb.EXPECTED_PAGE_ID)+
           "]},sort:[{field:dueAt,direction:asc}]})"+
           " { edges { node { id text status dueAt channelId assets { mimeType source } } } pageInfo { hasNextPage } } }")
    resp=fb.buffer_query(query).get("posts") or {}
    if not isinstance(resp.get("edges"),list) or (resp.get("pageInfo") or {}).get("hasNextPage"):
        raise RuntimeError("Scheduled history incomplete; no legacy edits")
    rows=[e["node"] for e in resp["edges"] if isinstance(e.get("node"),dict)]
    if any(p.get("channelId")!=fb.EXPECTED_PAGE_ID for p in rows):raise RuntimeError("Wrong FB channel")
    return rows
def main():
    if os.environ.get("ASTRALABS_LEGACY_COPY_REWRITE")!="true":
        raise RuntimeError("Explicit legacy rewrite authorization missing")
    if datetime.now(timezone.utc).date().isoformat()>"2026-09-30":
        print("LEGACY_REWRITE_EXPIRED: no further legacy edits",flush=True)
        return
    org=fb.verified_target()
    old={x["id"]:x for x in BANK}
    changed=0
    for post in history(org):
        candidates=[x for x in BANK if "utm_content="+x["id"] in str(post.get("text") or "")]
        if len(candidates)!=1 or candidates[0]["id"] not in COPY:continue
        item=candidates[0];pid=item["id"]
        if post.get("text")!=item["text"] or post.get("assets"):
            print("LEGACY_PRESERVED_MODIFIED_OR_MEDIA",pid,post.get("id"),flush=True);continue
        due=post.get("dueAt")
        try:due_date=datetime.fromisoformat(due.replace("Z","+00:00"))
        except Exception:raise RuntimeError("Unparseable dueAt for "+pid)
        if due_date<datetime.now(timezone.utc)+timedelta(minutes=45):
            print("LEGACY_TOO_CLOSE_TO_PUBLICATION",pid,flush=True);continue
        marker="utm_content="+pid
        urlmatch=re.search(r"https://www\.astralabsph\.com/(?:astramate|keepry)/\?[^\s]+",item["text"])
        if not urlmatch or marker not in urlmatch.group(0):raise RuntimeError("Missing original UTM URL")
        page=urlmatch.group(0)
        app=item["app"]
        offer=("Start free on Android; unlock more supported tools with the optional one-time Astramate Premium upgrade."
               if app=="Astramate" else
               "Start free on Android; optional one-time Keepry Plus expands document/People allowances and supported recurring reminders.")
        text=(COPY[pid]+"\n\n"+offer+
              "\n\nGet "+app+" from our official page: "+page+
              "\nOfficial AstraLabs PH website: "+ROOT_URL+
              ("\n\n#Astramate #Seafarers #MaritimeTools" if app=="Astramate"
               else "\n\n#Keepry #LifeAdmin #DocumentOrganizer"))
        if app=="Astramate" and re.search(r"\beta\b",text,re.I):raise RuntimeError("ETA prohibited")
        before=[p for p in history(org) if p.get("id")==post["id"]]
        if len(before)!=1 or before[0].get("text")!=item["text"] or before[0].get("dueAt")!=due or before[0].get("assets"):
            print("LEGACY_CHANGED_DURING_RECONCILE",pid,flush=True);continue
        mutation=("mutation { editPost(input:{id:"+fb.quoted(post["id"])+
                  " text:"+fb.quoted(text)+" metadata:{facebook:{type:post}} aiAssisted:true })"+
                  " { ... on PostActionSuccess { post { id text status dueAt } }"+
                  " ... on MutationError { message } } }")
        result=fb.buffer_query(mutation).get("editPost") or {}
        updated=result.get("post") if isinstance(result,dict) else None
        if not isinstance(updated,dict) or updated.get("id")!=post["id"] or updated.get("text")!=text:
            raise RuntimeError("Legacy edit unconfirmed for "+pid+"; inspect queue, do not retry blindly "+
                               str(result.get("message",""))[:100])
        if updated.get("status")!="scheduled" or updated.get("dueAt")!=due:
            raise RuntimeError("Edited post schedule changed unexpectedly for "+pid+"; owner reconcile required")
        changed+=1
        print("LEGACY_COPY_UPGRADED",pid,post["id"],"dueAt_unchanged",due,
              "main_site",ROOT_URL,flush=True)
        break  # One edit per invocation avoids Buffer API throttling; reconcile remaining on next scheduled run.
    print("LEGACY_EDIT_RECONCILE_DONE",changed,"upgraded",flush=True)
if __name__=="__main__":
    try:main()
    except Exception as e:
        print("LEGACY_EDIT_FAIL_CLOSED",type(e).__name__,str(e),file=sys.stderr)
        sys.exit(1)
