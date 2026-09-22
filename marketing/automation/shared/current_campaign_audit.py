#!/usr/bin/env python3
"""Read-only current Astramate/Keepry campaign status on all authorized channels."""
import importlib.util
import json
from pathlib import Path
base=Path(__file__).resolve().parent.parent
def load(name):
    p=base/name/"scripts"/("buffer_"+name+".py")
    spec=importlib.util.spec_from_file_location("audit_"+name,str(p))
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
fb=load("facebook")
pn=load("pinterest")
tt=load("tiktok")
org=fb.verified_target()
for label,channel,api in (("FB",fb.EXPECTED_PAGE_ID,fb.buffer_query),("TT",tt.resolve_tiktok()[1],tt.gql)):
    query=('query { posts(first:100,input:{organizationId:'+json.dumps(org)+
           ',filter:{status:[scheduled,sent,draft,error,sending],channelIds:['+json.dumps(channel)+
           ']},sort:[{field:createdAt,direction:desc}]}) { edges { node { id text status dueAt channelId externalLink schedulingType assets { mimeType source } } } pageInfo { hasNextPage } } }')
    obj=api(query).get("posts") or {}
    if not isinstance(obj.get("edges"),list) or (obj.get("pageInfo") or {}).get("hasNextPage"):
        raise RuntimeError(label+" incomplete history; no posting")
    rows=[e["node"] for e in obj["edges"] if isinstance(e.get("node"),dict)]
    if any(x.get("channelId")!=channel for x in rows):raise RuntimeError(label+" channel mismatch")
    for product in ("Astramate","Keepry"):
        matches=[p for p in rows if product.lower() in str(p.get("text") or "").lower()
                 and (("keepry" not in str(p.get("text") or "").lower()) if product=="Astramate" else True)]
        counts={state:sum(x.get("status")==state for x in matches) for state in ("sent","scheduled","draft","error","sending")}
        print("CAMPAIGN_AUDIT",label,product,json.dumps(counts),flush=True)
        for p in matches[:12]:
            print("CAMPAIGN_POST",label,product,p.get("id"),p.get("status"),p.get("dueAt"),
                  "url",p.get("externalLink"),"media",
                  [str(a.get("source") or "") for a in p.get("assets") or []],
                  "website",("astralabsph.com" in str(p.get("text") or "")),
                  "eta",("eta" in str(p.get("text") or "").lower()),flush=True)
porg,bid=pn.target()
if porg!=org:raise RuntimeError("Pinterest different organization")
print("PINTEREST_APPS_BOARD_READY",bool(bid),flush=True)
if bid:
    pposts=pn.get_existing(org)
    print("PINTEREST_POSTS",json.dumps([(p.get("id"),p.get("status"),p.get("dueAt")) for p in pposts[:12]]),flush=True)
print("CAMPAIGN_READ_ONLY_AUDIT_COMPLETE",flush=True)
