#!/usr/bin/env python3
"""Non-Amazon HTTP verification: internal PIREVO pages, saved US affiliate link syntax, disclosures."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from urllib.request import Request,urlopen
from urllib.error import URLError, HTTPError
import re,json,datetime,time,collections
root=Path(__file__).resolve().parent.parent
pub=root/"public/pirevo"
product_pages=sorted((pub/"products").glob("*/index.html"))
category_pages=sorted((pub/"categories").glob("*/index.html"))
urls=[("product",f"https://www.astralabsph.com/pirevo/products/{f.parent.name}/index.html") for f in product_pages]
urls+=[("category",f"https://www.astralabsph.com/pirevo/categories/{f.parent.name}/") for f in category_pages]
urls.append(("catalog","https://www.astralabsph.com/pirevo/catalog/"))
urls.append(("international","https://www.astralabsph.com/pirevo/international/"))
urls.append(("homepage","https://www.astralabsph.com/pirevo/"))
urls.append(("trends","https://www.astralabsph.com/pirevo/trends/"))
urls.append(("compare","https://www.astralabsph.com/pirevo/compare/"))
urls.append(("guides","https://www.astralabsph.com/pirevo/guides/"))
urls += [("guide",f"https://www.astralabsph.com/pirevo/guides/{f.parent.name}/") for f in (pub/"guides").glob("*/index.html")]
checks=[]
for f in product_pages:
 html=f.read_text()
 match=re.search(r'https://www\.amazon\.com/dp/([A-Z0-9]{10})\?tag=([a-z0-9-]+)',html)
 checks.append({"slug":f.parent.name,"us_asin":match.group(1) if match else None,"tracking_tag":match.group(2) if match else None,"disclosure_present":"As an Amazon Associate" in html,"editorial_jsonld":"\"Article\"" in html,"reviews_displayed":bool(re.search(r'[★☆]|class="shop-rating"',html)),"amazon_image_url_present":"m.media-amazon.com/images" in html,"manual_verification_hold":"Amazon link pending verification" in html})
def probe(entry):
 type_,url=entry
 try:
  r=urlopen(Request(url,method="HEAD",headers={"User-Agent":"PIREVO-internal-QA/1.0"}),timeout=12)
  return {"kind":type_,"url":url,"status":r.status}
 except HTTPError as e:return {"kind":type_,"url":url,"status":e.code}
 except URLError as e:return {"kind":type_,"url":url,"status":"NETWORK_ERROR","reason":str(e.reason)[:100]}
 except Exception as e:return {"kind":type_,"url":url,"status":"UNKNOWN","reason":str(e)[:100]}
results=[]
with ThreadPoolExecutor(max_workers=6) as pool:
 futures=[pool.submit(probe,x) for x in urls]
 for f in as_completed(futures):results.append(f.result())
results.sort(key=lambda x:x["url"])
bad=[x for x in results if x["status"]!=200]
report={"audit_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"scope":"GET/HEAD of owned website only. No Amazon requests or simulated customer clicks.","own_site_urls_tested":len(results),"own_site_http_200":len(results)-len(bad),"own_site_non_200":bad,"source_product_pages":len(product_pages),"source_product_link_checks":checks,"source_invalid_us_tag_count":sum((not x["manual_verification_hold"]) and (x["tracking_tag"]!="pirevo-20" or not x["us_asin"]) for x in checks),"source_held_unverified_products":[x["slug"] for x in checks if x["manual_verification_hold"]],"source_active_affiliate_links":sum(x["tracking_tag"]=="pirevo-20" and not x["manual_verification_hold"] for x in checks),"source_missing_disclosures":sum(not x["disclosure_present"] for x in checks),"source_disallowed_rating_blocks":sum(x["reviews_displayed"] for x in checks),"image_license_unknown_count":sum(x["amazon_image_url_present"] for x in checks),"product_region_evidence":"Separate manifest: PIREVO_MARKETPLACE_READINESS_20261021.json; no bulk Amazon scraping."}
out=root/"marketing/pirevo/PIREVO_LIVE_FUNNEL_QA_20261021.json"
out.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({k:v for k,v in report.items() if k not in ("source_product_link_checks","own_site_non_200")},indent=2))
print("LIVE_NON_200",bad[:20])
if bad or report["source_invalid_us_tag_count"] or report["source_missing_disclosures"] or report["source_disallowed_rating_blocks"]:
 raise SystemExit("QA FAIL: unresolved website or affiliate source validation")
