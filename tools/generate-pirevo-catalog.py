#!/usr/bin/env python3
"""Generate PIREVO static curated categories and repair unsupported merchant schema."""
import json
import re
import html
import subprocess
import pathlib
from collections import Counter

ROOT=pathlib.Path(__file__).resolve().parent.parent
PUBLIC=ROOT/"public"/"pirevo"
BASE="https://www.astralabsph.com"
DATE="2026-10-21"
node_script='const fs=require("fs"),vm=require("vm"),ctx={window:{}};vm.runInNewContext(fs.readFileSync("public/pirevo/store-data.js","utf8"),ctx,{timeout:3000});process.stdout.write(JSON.stringify(ctx.window.PIREVO_STORE));'
store=json.loads(subprocess.check_output(["node","-e",node_script],cwd=ROOT,text=True,timeout=12))
def esc(x):return html.escape(str(x or ""),quote=True)
def slug_ok(x):return bool(re.fullmatch("[a-z0-9][a-z0-9-]*",str(x)))
def url(slug):return "/pirevo/products/"+slug+"/index.html"
def title(p):return p.get("fullName") or p.get("shortName") or p["slug"].replace("-"," ").title()
CATEGORIES={
"kitchen":("Kitchen Tools & Cooking","Compare how each kitchen tool fits your cooking routine, space and cleanup needs.","Dimensions|Capacity or power requirements|Cleaning and daily usefulness"),
"bags":("Everyday Bags & Carry","Find bags by capacity, closure, straps and the practical details you carry each day.","Dimensions and compartments|Closure and material|Strap fit and durability"),
"beauty":("Skincare & Beauty","Look beyond trends to ingredients, skin compatibility and the exact product variant.","Ingredient list|Size and authenticity|Skin and routine compatibility"),
"gaming":("Gaming Room & Accessories","Explore compatible setup accessories that improve comfort, lighting or organization.","Device compatibility|Desk space and wiring|Power and mounting requirements"),
"seasonal":("Christmas Decorations & Holiday Gifts","Compare holiday lighting, decorations and family gifts by size, safety and retailer availability.","Indoor or outdoor suitability|Size and setup|Regional stock and delivery"),
"gifts":("Thoughtful & Practical Gifts","Browse gift ideas based on the recipient's interests and everyday needs.","Recipient needs|Variant and sizing|Shipping and returns"),
"fall-home":("Cozy Home Decor","Compare versatile, easy-to-maintain home accents for everyday comfort.","Room dimensions|Cleaning and care|Year-round usefulness"),
"home-organization":("Home Organization & Storage","Choose organizers that fit real cabinets, drawers and small spaces.","Measure before ordering|Material and load capacity|Clearance and layout"),
"tech":("Smart Home & Everyday Tech","Explore gadgets based on device compatibility and realistic daily utility.","Device standards|Power and setup|Warranty and model version"),
"pets":("Pet Care & Cleanup","Compare pet accessories based on safe fit, maintenance and your pet's routine.","Pet size and safety|Materials and cleaning|Use instructions"),
"fitness":("Fitness & Active Life","Research equipment for intended activity, fit, storage and durability.","Size and usage limits|Storage space|Maintenance requirements"),
"travel":("Packing & Travel Essentials","Explore useful travel gear with practical baggage limits and compatibility in mind.","Bag dimensions|Airline and battery policies|Weight and organization"),
"car":("Car Essentials","Look for accessories that fit your vehicle without compromising driving safety.","Vehicle fit|Clearance from airbags|Installation and upkeep"),
"kids":("Kids' Activities & Creative Play","Find play and learning products suited to the child's age and supervision needs.","Age and safety instructions|Included pieces|Activity and cleanup"),
"home-office":("Home Office & Desk","Choose desk tools that match your devices, workspace and working habits.","Desk measurements|Cable and power fit|Daily ergonomic needs"),
"cleaning":("Cleaning Tools","Compare cleaning accessories for surface compatibility and reusable convenience.","Surface suitability|Replacement consumables|Safe storage"),
"coffee-bar":("Coffee & Home Café","Explore drink-making tools for your kitchen space and favorite routine.","Machine footprint|Electrical requirements|Cleaning and capacity"),
"tools-diy":("Tools & DIY","Research DIY essentials around compatibility, reliability and safe use.","Tool compatibility|Safety directions|Parts and storage"),
"sleep-bedroom":("Sleep & Bedroom Comfort","Compare bedding and comfort accessories according to measurements and materials.","Sizing and fit|Material and care|Return terms"),
"outdoor-garden":("Outdoor & Garden","Browse outdoor gear based on exposure, space, installation and upkeep.","Weather rating|Mounting or anchoring|Cleaning and storage")
}
def catmeta(c):return CATEGORIES.get(c["id"],(c["name"],"Compare the specific product variant, fit and maintenance before buying.","Measurements|Compatibility|Return terms"))
products=[p for p in store["products"] if not p.get("archivedSeason") and slug_ok(p.get("slug")) and (PUBLIC/"products"/p["slug"]/"index.html").exists()]
missing=[p["slug"] for p in store["products"] if not p.get("archivedSeason") and p not in products]
groups={c["id"]:[p for p in products if p.get("collection")==c["id"]] for c in store["collections"]}
CSS="""<style>
:root{font-family:system-ui,-apple-system,sans-serif;color:#1c302b;background:#f7f9f6}*{box-sizing:border-box}body{margin:0}a{color:inherit}
header{background:#142d27;color:#fff;padding:20px max(18px,calc((100vw - 1160px)/2));display:flex;gap:22px;flex-wrap:wrap;justify-content:space-between;align-items:center}
header a{color:#fff;text-decoration:none}header nav{display:flex;gap:20px;flex-wrap:wrap;font-size:14px}header strong{letter-spacing:.13em;font-size:22px}
main{max-width:1160px;margin:auto;padding:34px 20px 70px}.crumb{font-size:13px;color:#52685e;margin-bottom:25px}
.eyebrow{font-size:12px;font-weight:800;letter-spacing:.12em;color:#487465;text-transform:uppercase}
h1{font-size:clamp(30px,5vw,54px);line-height:1.12;letter-spacing:-.03em;margin:10px 0 18px}h2{margin:42px 0 18px}
.intro{font-size:18px;line-height:1.7;max-width:760px;color:#455b53}.tip{padding:22px;border-radius:15px;background:#e6eee8;line-height:1.6;margin:26px 0}.tip li{margin:8px 0}
.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:15px}.card{background:#fff;border:1px solid #dce5dd;border-radius:13px;overflow:hidden;text-decoration:none;display:flex;flex-direction:column}
.card:hover{border-color:#84b297}.card img{width:100%;aspect-ratio:1/1;object-fit:contain;background:#f5f5f2;display:block}
.card div{padding:13px;display:flex;flex-direction:column;gap:8px;flex:1}.card small{font-size:11px;letter-spacing:.07em;text-transform:uppercase;color:#477566}
.card strong{font-size:15px;line-height:1.4}.card span{font-size:12px;line-height:1.5;color:#567066}.card b{font-size:13px;color:#2d7051;margin-top:auto}
.cat-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
.cat-grid a{background:#fff;border:1px solid #dce5dd;border-radius:12px;padding:15px;text-decoration:none;font-weight:700;display:flex;justify-content:space-between;gap:8px}
.cat-grid small{color:#587566}.inputs{display:flex;gap:12px;flex-wrap:wrap;margin:22px 0}.inputs input,.inputs select{flex:1;min-width:220px;padding:14px;border-radius:10px;border:1px solid #afc2b5;font:inherit}
footer{background:#142d27;color:#ebf5ed;padding:28px 18px;text-align:center;font-size:13px;line-height:1.6}footer a{color:#ebf5ed}
@media(max-width:1000px){.grid,.cat-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:670px){.grid,.cat-grid{grid-template-columns:repeat(2,minmax(0,1fr))}main{padding:22px 13px 50px}}
@media(max-width:360px){.grid,.cat-grid{grid-template-columns:1fr}}[hidden]{display:none!important}
</style>"""
HEADER='<header><a href="/pirevo/"><strong>PIREVO</strong></a><nav aria-label="Site navigation"><a href="/pirevo/catalog/">All products</a><a href="/pirevo/#gifts">Gift ideas</a><a href="/pirevo/editorial-policy.html">Our research</a></nav></header>'
FOOTER='<footer><p><strong>PIREVO</strong> · Smart finds worth discovering.</p><p>Independent research, not an Amazon merchant checkout. Always verify live price, seller, shipping and local stock on Amazon.</p><p>As an Amazon Associate I earn from qualifying purchases.</p><p><a href="/pirevo/affiliate-disclosure.html">Disclosure</a> · <a href="/pirevo/editorial-policy.html">Editorial policy</a></p></footer>'
def card(p):
 name=title(p);image=p.get("image","");brand=p.get("brand","");cat=p.get("collection","")
 img=('<img src="'+esc(image)+'" alt="'+esc(name)+'" loading="lazy" decoding="async">') if (image.startswith("https://") or image.startswith("/")) else ""
 reason=p.get("bestFor","") if isinstance(p.get("bestFor"),str) else ""
 return '<a class="card" href="'+url(p["slug"])+'" data-cat="'+esc(cat)+'"><div>'+img+'<small>'+esc(brand)+'</small><strong>'+esc(name)+'</strong><span>'+esc(reason)[:155]+'</span><b>View buying notes →</b></div></a>'
def wrap(headtitle,description,canonical,robots,body,graph,extra=""):
 ld=json.dumps({"@context":"https://schema.org","@graph":graph},ensure_ascii=False).replace("<","\\u003c")
 return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
  '<title>'+esc(headtitle)+'</title><meta name="description" content="'+esc(description)+'"><meta name="robots" content="'+robots+'">'
  '<link rel="canonical" href="'+esc(canonical)+'"><meta property="og:type" content="website"><meta property="og:title" content="'+esc(headtitle)+'">'
  '<meta property="og:description" content="'+esc(description)+'"><meta property="og:url" content="'+esc(canonical)+'">'
  '<script type="application/ld+json">'+ld+'</script>'+CSS+'</head><body>'+HEADER+'<main>'+body+'</main>'+FOOTER+extra+'</body></html>')
def crumbs(label,canonical):
 return {"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"PIREVO","item":BASE+"/pirevo/"},{"@type":"ListItem","position":2,"name":label,"item":canonical}]}
generated=[]
for c in store["collections"]:
 if not slug_ok(c["id"]) or not groups.get(c["id"]):continue
 arr=groups[c["id"]];label,intro,checks=catmeta(c);canonical=BASE+"/pirevo/categories/"+c["id"]+"/"
 heading=label+" | Product Picks & Buying Notes | PIREVO"
 description=intro+" Explore "+str(len(arr))+" product detail pages."
 checklist="".join("<li>"+esc(x)+"</li>" for x in checks.split("|"))
 body='<div class="crumb"><a href="/pirevo/">Home</a> / <a href="/pirevo/catalog/">Categories</a> / '+esc(label)+'</div><div class="eyebrow">Curated products · '+str(len(arr))+' picks</div><h1>'+esc(label)+'</h1><p class="intro">'+esc(intro)+'</p>'
 body+='<section class="tip"><strong>What to check when shopping</strong><ul>'+checklist+'</ul></section><h2>Compare the products</h2><div class="grid">'+"".join(card(p) for p in arr)+'</div>'
 body+='<section class="tip"><strong>International buying:</strong> These are US Amazon product references. OneLink may redirect qualifying visitors to a matching regional Amazon page. We have not verified every product in each country. Check the exact variant, current availability and price on Amazon.</section><p><a href="/pirevo/catalog/">Browse all product categories →</a></p>'
 graph=[{"@type":"CollectionPage","name":label,"description":description,"url":canonical},crumbs(label,canonical),{"@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"name":title(p),"url":BASE+url(p["slug"])} for i,p in enumerate(arr)]}]
 dest=PUBLIC/"categories"/c["id"]/"index.html";dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(wrap(heading,description,canonical,"index,follow,max-image-preview:large" if len(arr)>=3 else "noindex,follow",body,graph))
 if len(arr)>=3:generated.append(canonical)
catalogurl=BASE+"/pirevo/catalog/"
catlinks="".join('<a href="/pirevo/categories/'+esc(c["id"])+'/">'+esc(catmeta(c)[0])+'<small>'+str(len(groups[c["id"]]))+'</small></a>' for c in store["collections"] if groups.get(c["id"]))
options="".join('<option value="'+esc(c["id"])+'">'+esc(catmeta(c)[0])+'</option>' for c in store["collections"] if groups.get(c["id"]))
body='<div class="crumb"><a href="/pirevo/">Home</a> / Product directory</div><p class="eyebrow">Curated product directory · '+str(len(products))+' researched pages</p><h1>Find something useful.</h1><p class="intro">Browse independent product research by category, from kitchen tools and storage to electronics, beauty and gifts. PIREVO is an affiliate discovery site; Amazon handles prices, stock and checkout.</p>'
body+='<h2>Shop by category</h2><nav class="cat-grid" aria-label="Shop by category">'+catlinks+'</nav><h2>Search the product directory</h2><div class="inputs"><input type="search" id="q" aria-label="Search products" placeholder="Search products and brands"><select id="c" aria-label="Choose a category"><option value="">All categories</option>'+options+'</select></div><p id="count" aria-live="polite">'+str(len(products))+' products</p><div class="grid" id="items">'+"".join(card(p) for p in products)+'</div><p id="none" hidden>No matches. Try another search or category.</p>'
body+='<section class="tip"><strong>Regional availability:</strong> Products and variants may differ between Amazon marketplaces. Verify exact details and checkout availability with Amazon before ordering.</section>'
extra="""<script>(function(){var q=document.getElementById('q'),c=document.getElementById('c'),cards=[...document.querySelectorAll('#items a.card')],count=document.getElementById('count'),none=document.getElementById('none');function run(){var t=q.value.trim().toLowerCase(),g=c.value,n=0;cards.forEach(function(x){var yes=(!t||x.textContent.toLowerCase().includes(t))&&(!g||x.dataset.cat===g);x.hidden=!yes;if(yes)n++;});count.textContent=n+' matching products';none.hidden=n!==0;}q.addEventListener('input',run);c.addEventListener('change',run);})();</script>"""
graph=[{"@type":"CollectionPage","name":"PIREVO Product Directory","url":catalogurl},crumbs("Product Directory",catalogurl)]
dest=PUBLIC/"catalog"/"index.html";dest.parent.mkdir(parents=True,exist_ok=True)
dest.write_text(wrap("Browse Curated Products by Category | PIREVO","Browse useful kitchen, home, tech, beauty, gifts and travel products. Independent PIREVO product research with Amazon checkout.",catalogurl,"index,follow,max-image-preview:large",body,graph,extra))
generated.append(catalogurl)
home=PUBLIC/"index.html"
s=home.read_text()
if 'class="pirevo-evergreen-catalog"' not in s:
 anchors="".join('<a href="/pirevo/categories/'+esc(c["id"])+'/">'+esc(catmeta(c)[0])+' →</a> ' for c in store["collections"] if groups.get(c["id"]))
 section='<section class="pirevo-evergreen-catalog" style="padding:30px 22px;background:#eaf2ec;color:#16372b"><div style="max-width:1160px;margin:auto"><h2>Browse practical finds by category</h2><p>Explore '+str(len(products))+' researched product pages. Amazon handles checkout, live prices and local stock.</p><nav aria-label="PIREVO categories" style="display:flex;flex-wrap:wrap;gap:10px">'+anchors+'</nav><p><a href="/pirevo/catalog/"><strong>Search all products →</strong></a></p></div></section>'
 if s.count("<main>")!=1:raise RuntimeError("Unexpected PIREVO homepage main")
 home.write_text(s.replace("<main>","<main>"+section,1))
# Replace invalid product rich-result claims with editorial Article facts, not invented offers or reviews.
fixed=0
for file in (PUBLIC/"products").glob("*/index.html"):
 s=file.read_text()
 m=re.search(r'<script type="application/ld\+json">([\s\S]*?)</script>',s)
 if not m:continue
 try:d=json.loads(m.group(1))
 except json.JSONDecodeError:continue
 graph=d.get("@graph",[])
 if not isinstance(graph,list):continue
 invalid=[x for x in graph if x.get("@type")=="Product" and not any(x.get(k) for k in ("offers","review","aggregateRating"))]
 if not invalid:continue
 page=next((x for x in graph if x.get("@type")=="WebPage"),{})
 for p in invalid:
  graph.remove(p)
  graph.append({"@type":"Article","headline":str(p.get("name") or file.parent.name)+" - PIREVO buying research","description":page.get("description") or p.get("description") or "Independent product selection notes.","mainEntityOfPage":page.get("url") or BASE+url(file.parent.name),"author":{"@type":"Organization","name":"PIREVO"},"publisher":{"@type":"Organization","name":"PIREVO","url":BASE+"/pirevo/"},"about":{"@type":"Thing","name":p.get("name"),"identifier":p.get("sku"),"brand":p.get("brand")}})
 s=s[:m.start(1)]+json.dumps(d,ensure_ascii=False).replace("<","\\u003c")+s[m.end(1):]
 s=s.replace('<meta property="og:type" content="product">','<meta property="og:type" content="article">')
 file.write_text(s);fixed+=1
for sitemap in [ROOT/"public"/"sitemap.xml",PUBLIC/"sitemap.xml"]:
 if not sitemap.exists():continue
 s=sitemap.read_text()
 s=re.sub(r'<url>\s*<loc>https://www\.astralabsph\.com/pirevo/(?:categories/[a-z0-9-]+/|catalog/)</loc>[\s\S]*?</url>\s*',"",s)
 if "</urlset>" not in s:raise RuntimeError("Unexpected sitemap "+str(sitemap))
 new="".join("<url><loc>"+x+"</loc><lastmod>"+DATE+"</lastmod></url>\n" for x in generated)
 sitemap.write_text(s.replace("</urlset>",new+"</urlset>",1))
print(json.dumps({"linked_product_pages":len(products),"data_products_without_pages":missing,"categories_written":sum(bool(v) for v in groups.values()),"indexable_category_pages":len(generated)-1,"catalog_page":catalogurl,"invalid_product_jsonld_replaced":fixed,"sitemap_entries_added":len(generated)}))
