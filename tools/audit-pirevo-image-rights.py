#!/usr/bin/env python3
"""Audits image origins; blocks NEW unapproved Amazon CDN references after frozen baseline.
Historical refs are NOT deemed licensed by inclusion in the baseline."""
import json,re,hashlib,sys
from pathlib import Path
from urllib.parse import urlsplit
R=Path(__file__).resolve().parent.parent
P=R/"public/pirevo"
report=R/"marketing/pirevo/PIREVO_IMAGE_PROVENANCE_20261022.json"
paths=list((P/"products").glob("*/index.html"))+[P/"index.html",P/"store-data.js",P/"guide-images.js",P/"pdp-gallery.js"]
remote=[]
hosts={}
for file in paths:
 t=file.read_text()
 # Include all known Amazon image CDN references, whether HTML tags or JS strings.
 urls=set(re.findall(r'https://(?:m\.media-amazon\.com|images-na\.ssl-images-amazon\.com)/[^\s\"\'<>)]+',t))
 if urls:
  remote.extend([{"source":str(file.relative_to(R)),"host":urlsplit(u).netloc,"hash":hashlib.sha256(u.encode()).hexdigest()[:24]} for u in sorted(urls)])
  hosts[str(file.relative_to(R))]=len(urls)
refset=sorted({r["hash"] for r in remote})
if report.exists():
 prior=json.loads(report.read_text())
 baseline=set(prior.get("historical_unverified_image_hashes",[]))
 new=set(refset)-baseline
 if new:
  print("BLOCKED: added unverified Amazon CDN image references",len(new))
  sys.exit(1)
else:
 if "--create-baseline" not in sys.argv:
  print("Missing image provenance baseline; explicitly run with --create-baseline first.")
  sys.exit(1)
 baseline=set(refset)
out={"audit_date":"2026-10-22","status":"REQUIRES_AUTHORITATIVE_LICENSE_PROOF","note":"Historical URL baseline exists to block additional risk; it is not proof of image rights. No copying or caching performed.","unique_current_amazon_image_urls":len(refset),"source_occurrences":len(remote),"files_with_cdn_content":len(hosts),"source_counts":hosts,"historical_unverified_image_hashes":sorted(baseline),"new_unauthorized_references":0,"next_actions":["For existing Amazon CDN assets, obtain official API/Creators API display entitlement or seller/manufacturer written image permission before claiming compliance.","Do not copy, cache, alter, crop, or distribute seller images to Pinterest or other media without documented authorization.","Replace unverifiable imagery with genuinely licensed, original photos or transparent editorial non-photographic presentation in a controlled redesign."]}
report.parent.mkdir(parents=True,exist_ok=True)
report.write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps({k:v for k,v in out.items() if k not in ("source_counts","historical_unverified_image_hashes","next_actions")},indent=2))
