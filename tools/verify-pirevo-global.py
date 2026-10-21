#!/usr/bin/env python3
"""PIREVO global storefront source QA; no Amazon requests or simulated clicks."""
from pathlib import Path
import json,re,xml.etree.ElementTree as ET,subprocess
ROOT=Path(__file__).resolve().parent.parent
P=ROOT/"public/pirevo"
manifest=json.loads((ROOT/"marketing/pirevo/PIREVO_MARKETPLACE_READINESS_20261021.json").read_text())
evidence=json.loads((P/"regional-evidence.json").read_text())
sources=list((P/"products").glob("*/index.html"))+list((P/"categories").glob("*/index.html"))+[P/"index.html",P/"catalog/index.html",P/"international/index.html"]
assert len(sources)==162,len(sources)
for f in sources:
 s=f.read_text()
 assert s.count('<script src="/pirevo/marketplace-guide.js" defer></script>')==1,f
 assert s.count('<link rel="stylesheet" href="/pirevo/marketplace-guide.css">')==1,f
 assert s.count('<link rel="icon" type="image/svg+xml" href="/pirevo/favicon.svg">')==1,f
 assert '<link rel="canonical"' in s,f
catalog=(P/"catalog/index.html").read_text()
assert catalog.count('data-cat=')==138
assert "138 researched pages" in catalog
assert (P/"international/index.html").read_text().count('class="market-card"')==10
for f in [ROOT/"public/sitemap.xml",P/"sitemap.xml"]:
 t=ET.parse(f).getroot()
 urls=[node.text for node in t.iter() if node.tag.endswith("loc")]
 assert len(urls)==len(set(urls)),f
 assert "https://www.astralabsph.com/pirevo/international/" in urls,f
detail_files=list((P/"products").glob("*/index.html"))
assert len(detail_files)==139
held=[]
active=0
for file in detail_files:
 text=file.read_text()
 assert "As an Amazon Associate" in text,file
 assert not re.search(r'[★☆]|class="shop-rating"',text),file
 if "Amazon link pending verification" in text:
  held.append(file.parent.name)
  assert 'href="https://www.amazon.com/dp/' not in text,file
 else:
  links=re.findall(r'href="https://www\.amazon\.com/dp/([A-Z0-9]{10})\?tag=pirevo-20"',text)
  assert len(links)==1,(file,links)
  active+=1
assert sorted(held)==["elf-halo-glow-3"],held
assert active==138,active
allowed={"US","CA","UK","DE","FR","IT","ES","NL","PL","SE"}
for slug,markets in evidence["products"].items():
 assert (P/"products"/slug/"index.html").exists(),slug
 for c,v in markets.items():
  assert c in allowed and v["model"]=="checked" and re.fullmatch("[A-Z0-9]{10}",v["asin"])
js=(P/"marketplace-guide.js").read_text()
assert "pirevo-region-select" in js
assert "location.pathname" in js and "localStorage" in js
assert "amazon.com/dp" in js  # Only for recognizing existing anchors, not for rewriting them.
assert not re.search(r"\.(href|location)\s*=",js),"Shopper script must never rewrite affiliate links"
print(json.dumps({"result":"PASS","widget_pages":len(sources),"catalog_products":138,"detail_pages":len(detail_files),"active_US_tagged_buying_links":active,"held_unverified_products":held,"indexable_international_guide":True,"country_checks":{k:sorted(v) for k,v in evidence["products"].items()}},indent=2))
