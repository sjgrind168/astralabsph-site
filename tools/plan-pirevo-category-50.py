#!/usr/bin/env python3
"""PIREVO product-category expansion control: 50 audited picks per category.
Read-only audit of live catalog, plus staged, NON-PUBLISHED research records.
"""
from pathlib import Path
import json, subprocess, re
from datetime import date
R=Path(__file__).resolve().parent.parent
target=50
script='const fs=require("fs"),vm=require("vm"),w={};vm.runInNewContext(fs.readFileSync("public/pirevo/store-data.js","utf8"),{window:w});console.log(JSON.stringify(w.PIREVO_STORE))'
data=json.loads(subprocess.check_output(["node","-e",script],cwd=R,text=True))
records=data["products"]
cats=data["collections"]
assert len(cats)==20
assert len(records)==len({p["slug"] for p in records})
known_asins={p["asin"] for p in records}
for p in records:
 assert re.fullmatch('[A-Z0-9]{10}',p["asin"]),(p["slug"],p["asin"])
 assert p["collection"] in {c["id"] for c in cats}
 assert (R/"public/pirevo/products"/p["slug"]/"index.html").exists()
counts={c["id"]:sum(p["collection"]==c["id"] for p in records) for c in cats}
published=sum(counts.values())
# Listings checked directly in Amazon.com product detail pages; these are
# research candidates, not products guaranteed to be best sellers or published.
seeds=[
 {"asin":"B0725WFLMB","brand":"Bedsure","candidate":"Satin Pillowcases Queen, set of 2, Grey","category":"sleep-bedroom","evidence":"Exact US Amazon product title and ASIN observed 2026-10-22","status":"model_identity_checked__editorial_and_rights_review_pending","next":"Manufacturer material/sizing verification, original comparison, static page QA"},
 {"asin":"B0D145689D","brand":"Bedsure","candidate":"Twin/Twin XL Prewashed Comforter Set, Emerald Green","category":"sleep-bedroom","evidence":"Exact US Amazon product title and ASIN observed 2026-10-22","status":"model_identity_checked__editorial_and_rights_review_pending","next":"Size and color variant, fabric, included pieces, first-party illustrations"},
 {"asin":"B0CSYXYWDZ","brand":"Bedsure","candidate":"100% Washed Cotton Duvet Cover Set, Oversized King","category":"sleep-bedroom","evidence":"Exact US Amazon product title and ASIN observed 2026-10-22","status":"model_identity_checked__editorial_and_rights_review_pending","next":"Check duvet cover (not comforter) distinction, size & origin"},
 {"asin":"B005NNF0YU","brand":"BLACK+DECKER","candidate":"20V MAX Cordless Drill/Driver LDX120C","category":"tools-diy","evidence":"Exact US Amazon product title and ASIN observed 2026-10-22","status":"model_identity_checked__editorial_and_rights_review_pending","next":"Confirm charger and battery bundle, model/voltage safety caveats"},
]
published_seed_asins={p["asin"] for p in seeds if p["asin"] in known_asins}
seeds=[p for p in seeds if p["asin"] not in published_seed_asins]
for p in seeds:
 assert re.fullmatch("[A-Z0-9]{10}",p["asin"])
 assert p["category"] in counts
assert len({p["asin"] for p in seeds})==len(seeds)
categories=[{"id":c["id"],"name":c["name"],"published":counts[c["id"]],"goal":target,"gap":max(0,target-counts[c["id"]]),"research_candidates_checked":sum(x["category"]==c["id"] for x in seeds),"status":"in_progress" if counts[c["id"]]<target else "goal_reached"} for c in cats]
categories.sort(key=lambda x:(x["published"],x["name"]))
manifest={
 "release_date":"2026-10-22",
 "goal_definition":"50 independently useful, category-relevant and editorially researched product pages in EACH category, not 50 unverified search matches",
 "published_products":len(records),
 "category_count":len(cats),
 "goal_total_placements":len(cats)*target,
 "current_published_category_placements":published,
 "missing_published_placements":sum(x["gap"] for x in categories),
 "published_unique_asins":len(known_asins),
 "candidate_asins_checked_not_published":len(seeds),
 "new_researched_products_published_in_first_batch":len(published_seed_asins),
 "seo_rule":"Do not claim best-seller rankings, live reviews, shipping, stock, direct testing or licensed imagery without independent evidence",
 "amazon_rule":"Exact ASIN and product variant checked; live product page URL may include pirevo-20 only AFTER editorial/brand/image review and static PDP QA. No copied Amazon images without authorization.",
 "catalog_status":"138 live products unchanged; additional products remain research only until published",
 "categories":categories,
 "non_published_research_candidates":seeds
}
f=R/"marketing/pirevo/CATEGORY_50_BACKLOG_20261022.json"
f.parent.mkdir(parents=True,exist_ok=True)
f.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"published":published,"goal":len(cats)*target,"gap":manifest["missing_published_placements"],"research_candidates":len(seeds),"thin_categories":categories[:6]},indent=2))
