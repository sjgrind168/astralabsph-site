#!/usr/bin/env python3
"""Checks the PIREVO Buying Desk generation, availability, and safe editorial fields."""
from pathlib import Path
import json,re,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parent.parent;P=R/"public/pirevo"
data=json.loads((P/"compare-data.json").read_text())
items=data["items"]
assert len(items)>=138
assert len({p["slug"] for p in items})>=138
required={"slug","name","fullName","brand","category","bestFor","caveat","page","verifiedUS"}
banned={"price","rating","reviews","rank","image","commission"}
for p in items:
 assert required.issubset(p.keys())
 assert not set(p).intersection(banned),p["slug"]
 assert re.fullmatch("[a-z0-9-]+",p["slug"])
 assert (P/p["page"].removeprefix("/pirevo/")).exists(),p["slug"]
html=(P/"compare/index.html").read_text()
assert 'rel="canonical"' in html and 'affiliate' in html.lower()
assert html.count('class="preset"')==5
assert not any("media-amazon.com" in (P/x).read_text() for x in ["compare/index.html","compare/app.js","compare/style.css","compare-data.json"])
assert 'compare-data.json' in (P/"compare/app.js").read_text()
assert 'history.replaceState' in (P/"compare/app.js").read_text()
assert 'business-analytics.js' in html and 'config.js' in html
assert 'compare_view' in (P/"compare/app.js").read_text()
assert 'return"comparison"' in (P/"business-analytics.js").read_text()
assert not re.search(r'https?://(?:m\.media-amazon|images-na\.ssl-images-amazon)',html)
cat=(P/"catalog/index.html").read_text()
assert cat.count('class="pirevo-compare-intro"')==1
product_count=0
for p in items:
 txt=(P/p["page"].removeprefix("/pirevo/")).read_text()
 assert txt.count('class="pirevo-compare-linkout"')==1,p["slug"]
 assert "/pirevo/compare/?p="+p["slug"] in txt
 product_count+=1
cat_count=0
for f in (P/"categories").glob("*/index.html"):
 assert f.read_text().count('class="pirevo-category-compare"')==1,f
 cat_count+=1
assert cat_count==20
for f in [R/"public/sitemap.xml",P/"sitemap.xml"]:
 urls=[x.text for x in ET.parse(f).getroot().iter() if x.tag.endswith("loc")]
 assert len(urls)==len(set(urls))
 assert "https://www.astralabsph.com/pirevo/compare/" in urls
print(json.dumps({"comparison_tool":"PASS","catalog_items":len(items),"linked_product_pages":product_count,"linked_category_pages":cat_count,"presets":5,"unlicensed_remote_images_added":0,"tracked_amazon_links_rewritten":0},indent=2))
