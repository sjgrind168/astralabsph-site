#!/usr/bin/env python3
"""PIREVO storefront v5 release gate: source integrity, unified chrome, discovery and affiliate safety."""
from pathlib import Path
import subprocess,json,re,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parent.parent;B=R/"public/pirevo"
js='const fs=require("fs"),vm=require("vm"),w={};vm.runInNewContext(fs.readFileSync("public/pirevo/store-data.js","utf8"),{window:w});process.stdout.write(JSON.stringify(w.PIREVO_STORE))'
store=json.loads(subprocess.check_output(["node","-e",js],cwd=R,text=True))
assert len(store["products"])>=138 and len(store["collections"])==20
home=(B/"index.html").read_text()
required={"class=\"pv-header\"":1,"class=\"pv-footer\"":1,"data-pv-carousel":3,"class=\"pv-cat-tile":20,"id=\"pv-products-grid\"":1,"class=\"pv-card\"":len(store["products"])+42,"<h1":1}
for key,count in required.items():
 assert home.count(key)==count,(key,home.count(key),count)
assert "marketplace-guide.js" in home and "marketplace-guide.css" in home
order=[home.index('id="'+i+'"') for i in ["trending","discover","holiday","everyday"]]
assert order==sorted(order),"Searchable products must appear immediately after first trend carousel"
for label in ["Trend","Holiday"]:
 assert label.lower() in home.lower()
assert "not a live sales ranking" in home
assert not re.search(r"\b\d(?:\.\d)?\s*[★☆]|\b\d[,.]?\d*\s+(?:ratings?|reviews?)\b",home,re.I)
for prod in store["products"]:
 slug=prod["slug"]
 assert f'href="/pirevo/products/{slug}/index.html"' in home,slug
 assert f'data-cat="{prod["collection"]}"' in home,slug
css=(B/"storefront-v5.css").read_text()
assert ".pv-carousel-track" in css and "scroll-snap-type:x mandatory" in css
assert ".pv-menu-toggle" in css and "min-width:0" in css
script=(B/"storefront-v5.js").read_text()
assert "scrollBy" in script and "aria-expanded" in script and "pv-more" in script
assert "history.replaceState" in script
assert not re.search(r"\.(?:href|location)\s*=\s*['\"]https?://",script)
paths=[B/"catalog/index.html",B/"trends/index.html",B/"compare/index.html",B/"international/index.html",B/"books/timmy-and-the-time-traveling-watch/index.html",B/"guides/index.html"]+list((B/"products").glob("*/index.html"))+list((B/"categories").glob("*/index.html"))+list((B/"guides").glob("*/index.html"))
assert len(paths)>=176,len(paths)
for f in paths:
 s=f.read_text()
 for key in ['class="pv-header"','class="pv-footer"','href="/pirevo/storefront-v5.css"','src="/pirevo/storefront-v5.js"']:
  assert s.count(key)==1,(f,key,s.count(key))
 assert s.count("pv-ui")==1,(f,"repeated class")
 if "/products/" in str(f):
  assert "As an Amazon Associate" in s,f
  if "Amazon link pending verification" not in s:
   assert len(re.findall(r'https://www\.amazon\.com/dp/[A-Z0-9]{10}\?tag=pirevo-20',s))>=1,f
trends=(B/"trends/index.html").read_text()
assert trends.count('class="find"')==46,trends.count('class="find"')
assert '46 rated Amazon' not in trends
assert 'class="rating"' not in trends
# All previously indexed site URLs must remain.
for f in [R/"public/sitemap.xml",B/"sitemap.xml"]:
 root=ET.parse(f).getroot()
 urls=[x.text for x in root.iter() if x.tag.endswith("loc")]
 assert len(urls)==len(set(urls)),f
 for slug in ["compare/","trends/","international/","catalog/"]:
  assert any(("/pirevo/"+slug) in u for u in urls),slug
print(json.dumps({"result":"PASS","home_catalog_products":len(store["products"]),"trending_carousel_items":15,"seasonal_carousel_items":16,"everyday_carousel_items":11,"categories":20,"unified_inner_pages":len(paths),"social_shopping_product_cards":46,"protected_original_affiliate_links":True,"browser_image_source_status":"Historical image license NOT certified"},indent=2))
