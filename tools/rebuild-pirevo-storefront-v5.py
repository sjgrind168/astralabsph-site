#!/usr/bin/env python3
"""PIREVO v5 unified editorial storefront.
Keeps all original affiliate destinations; reuses ONLY pre-existing catalog image URLs.
Runs after legacy catalog/detail generators. Idempotent.
"""
from pathlib import Path
from html import escape as E
import subprocess,json,re,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parent.parent;B=R/"public/pirevo"
js='const fs=require("fs"),vm=require("vm"),w={};vm.runInNewContext(fs.readFileSync("public/pirevo/store-data.js","utf8"),{window:w});process.stdout.write(JSON.stringify(w.PIREVO_STORE))'
store=json.loads(subprocess.check_output(["node","-e",js],cwd=R,text=True))
products=[p for p in store["products"] if not p.get("archivedSeason")]; cats=store["collections"]; P={p["slug"]:p for p in products}
assert len(products)>=120 and len(cats)==20
def safe(v):return E(str(v or ""),quote=True)
def brief(v,n=108):
 t=str(v or "").strip()
 if re.search(r"\d[.,]?\d*\s*(?:star|rating|review|sold|bought)\b|#\d+|% mom|% month",t,re.I):return "See the product's buying notes and current retailer specifications."
 return t if len(t)<=n else t[:n-1].rsplit(" ",1)[0]+"…"
def link(p):return "/pirevo/products/"+p["slug"]+"/index.html"
HEADER='''<header class="pv-header"><a class="pv-logo" href="/pirevo/" aria-label="PIREVO Home">PIREVO<small>SMART FINDS WORTH DISCOVERING</small></a><button type="button" class="pv-menu-toggle" aria-controls="pv-header-nav" aria-expanded="false">Menu ☰</button><nav class="pv-header-nav" id="pv-header-nav" aria-label="Main navigation"><a href="/pirevo/">Home</a><a href="/pirevo/#trending">Trending finds</a><a href="/pirevo/#categories">Categories</a><a href="/pirevo/trends/">Social shopping</a><a href="/pirevo/guides/">Buying guides</a><a href="/pirevo/compare/">Compare</a><a href="/pirevo/international/">Worldwide</a><a class="pv-nav-cta" href="/pirevo/#discover">Shop all →</a></nav></header>'''
FOOTER='''<footer class="pv-footer"><div class="pv-footer-grid"><div><strong>PIREVO</strong><p>Smart finds worth discovering. An independent product-discovery and buying-guide website from AstraLabs PH. Shop thoughtfully, then verify current product details and complete checkout with Amazon.</p></div><div><h3>Explore</h3><a href="/pirevo/#trending">Trending-inspired finds</a><a href="/pirevo/#categories">Browse categories</a><a href="/pirevo/catalog/">All products</a><a href="/pirevo/#books">Original books</a><a href="/pirevo/#astralabs-apps">AstraLabs apps</a><a href="/pirevo/trends/">Social shopping</a><a href="/pirevo/compare/">Buying Desk</a></div><div><h3>Information</h3><a href="/pirevo/guides/">Buying guides</a><a href="/pirevo/international/">Global shopping</a><a href="/pirevo/editorial-policy.html">Editorial standards</a><a href="/pirevo/affiliate-disclosure.html">Affiliate disclosure</a><a href="/pirevo/privacy.html">Privacy</a></div></div><div class="pv-footer-note">As an Amazon Associate I earn from qualifying purchases. PIREVO is independent from Amazon and does not process orders. Product images, stock, prices, seller, regional availability and shipping must be verified with the retailer. © 2026 PIREVO.</div></footer>'''
def card(p,tag="EDITOR'S PICK",eager=False):
 return '<article class="pv-card" data-cat="'+safe(p["collection"])+'" data-search="'+safe((p["brand"]+" "+p["shortName"]+" "+p["fullName"]+" "+p.get("bestFor","")).lower())+'"><a class="pv-card-img" href="'+link(p)+'" aria-label="Read buying notes for '+safe(p["shortName"])+'"><span class="pv-tag">'+safe(tag)+'</span><img src="'+safe(p["image"])+'" alt="'+safe(p["fullName"])+'" loading="'+("eager" if eager else "lazy")+'" decoding="async"></a><div class="pv-card-copy"><small>'+safe(p["brand"])+'</small><a class="pv-card-title" href="'+link(p)+'">'+safe(p["shortName"])+'</a><p>'+safe(brief(p.get("bestFor",""),115))+'</p><div class="pv-card-bottom"><a href="'+link(p)+'">View buying notes ↗</a><span>Amazon checkout</span></div></div></article>'
def pick(slugs, fallback=None):
 selected=[P[s] for s in slugs if s in P]
 if len(selected)<8 and fallback:selected.extend(p for p in products if p["collection"] in fallback and p not in selected)
 return selected
spotlight=pick(["churboro-spice-jars-25","apple-airtag-2","cosrx-snail-mucin-96","aeropress-original-b0047","fullstar-pro-chopper","vtopmart-under-sink-drawers-4","govee-table-lamp-2","wrangler-satchel","echo-dot-charcoal","bagsmart-hanging-toiletry","bissell-little-green","ugreen-nexode-pro-65w","crockpot-design-7qt","ninja-possiblecooker-pro-plus","circle-joy-rechargeable-frother","levoit-core-mini-p-air-purifier"],["kitchen","tech","beauty"])
holiday=[p for p in products if p.get("season")=="christmas" or p.get("holidayGiftGroup")]
holiday=list(dict((p["slug"],p) for p in holiday).values())[:16]
if len(holiday)<8:holiday=pick(["eddie-bauer-sherpa-throw","govee-table-lamp-2","amazon-basics-storage-cubes-6","apple-airtag-2","aeropress-original-b0047","cosrx-snail-mucin-96","echo-dot-charcoal","bagsmart-hanging-toiletry"],["gifts"])
everyday=pick(["vtopmart-drawer-organizers-25","amazon-basics-storage-cubes-6","crockpot-manual-7qt","churboro-spice-jars-25","travel-inspira-luggage-scale","bissell-little-green","levoit-core-mini-p-air-purifier","veken-shower-caddy-6","ugreen-nexode-pro-65w","aeropress-original-b0047","govee-table-lamp-2","bagsmart-hanging-toiletry"],["home-organization","kitchen"])
def carousel(id,title,summary,items,target,text_tag):
 return '<section class="pv-section" id="'+id+'"><div class="pv-heading"><div><span class="pv-eyebrow">'+safe(text_tag)+'</span><h2>'+safe(title)+'</h2><p>'+safe(summary)+'</p></div><a href="'+target+'">Browse collection ↗</a></div><div class="pv-carousel-shell" data-pv-carousel><div class="pv-carousel-track" tabindex="0" aria-label="'+safe(title)+' swipeable product carousel">'+''.join(card(p,"CURATED FIND") for p in items)+'</div><div class="pv-carousel-nav"><span class="pv-car-status" aria-live="polite"></span><button type="button" class="pv-car-btn" data-dir="prev" aria-label="Scroll '+safe(title)+' left">←</button><button type="button" class="pv-car-btn" data-dir="next" aria-label="Scroll '+safe(title)+' right">→</button></div></div></section>'
promos=[P[s] for s in ["shareconn-48-prelit-christmas-wreath","homemory-christmas-tree-candles","lego-botanicals-tiny-plants"] if s in P]
mini=''.join('<a class="pv-mini" href="'+link(p)+'"><figure><img src="'+safe(p["image"])+'" alt="'+safe(p["shortName"])+'" loading="eager"></figure><small>'+safe(p["brand"])+'</small><strong>'+safe(p["shortName"])+'</strong><span>Explore the buying notes ↗</span></a>' for p in promos)
cat_tiles=[]
for i,c in enumerate(cats):
 example=P.get("shareconn-48-prelit-christmas-wreath") if c["id"]=="seasonal" else next((p for p in products if p["collection"]==c["id"]),None)
 pic='<div class="pv-cat-picture"><img src="'+safe(example["image"])+'" alt="" loading="lazy"></div>' if example else ""
 extra=" pv-extra-cat" if i>=10 else ""
 cat_tiles.append('<a class="pv-cat-tile'+extra+'" href="/pirevo/categories/'+safe(c["id"])+'/"'+(" hidden" if i>=10 else "")+'>'+pic+'<span><strong>'+safe(c["name"])+'</strong><small>'+str(sum(p["collection"]==c["id"] for p in products))+' researched finds ↗</small></span></a>')
cat_options=''.join('<option value="'+safe(c["id"])+'">'+safe(c["name"])+'</option>' for c in cats)
quick=''.join('<a href="/pirevo/#discover" data-quick-category="'+safe(i)+'">'+safe(label)+' ↗</a>' for i,label in [("beauty","Beauty"),("bags","Bags"),("kitchen","Kitchen"),("home-organization","Home"),("tech","Tech"),("travel","Travel")])
meta={"@context":"https://schema.org","@type":"CollectionPage","name":"PIREVO: Curated Finds and Product Buying Guides","url":"https://www.astralabsph.com/pirevo/","description":"Browse 138 curated product research pages across 20 categories, with buying notes, comparisons and global shopping guidance.","hasPart":[{"@type":"ItemList","name":"Trending-inspired PIREVO picks","itemListElement":[{"@type":"ListItem","position":i+1,"url":"https://www.astralabsph.com"+link(p),"name":p["shortName"]} for i,p in enumerate(spotlight[:12])]}]}
body='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PIREVO | Thoughtful Finds, Trending Picks & Product Buying Guides</title><meta name="description" content="Browse 138 practical product finds across 20 categories, explore trending-inspired carousels, compare products and shop smarter with PIREVO buying notes."><meta name="robots" content="index,follow,max-image-preview:large"><meta name="theme-color" content="#174235"><link rel="canonical" href="https://www.astralabsph.com/pirevo/"><meta property="og:type" content="website"><meta property="og:title" content="PIREVO · Smart finds worth discovering"><meta property="og:description" content="A more thoughtful way to discover everyday finds, gifts, and practical upgrades."><link rel="icon" type="image/svg+xml" href="/pirevo/favicon.svg"><link rel="stylesheet" href="/pirevo/storefront-v5.css"><link rel="stylesheet" href="/pirevo/marketplace-guide.css"><script type="application/ld+json">'''+json.dumps(meta,ensure_ascii=False)+'''</script></head><body class="pv-ui pv-home">'''+HEADER+'''<main><section class="pv-hero"><div class="pv-wrap pv-hero-grid"><div><div class="pv-eyebrow">CHRISTMAS 2026 · CURATED GIFT DISCOVERY</div><h1>Thoughtful gifts.<br><em>Easier Christmas shopping.</em></h1><p>Discover real holiday gift ideas, useful everyday picks and thoughtful Christmas home touches. Compare the exact item before buying on Amazon.</p><div class="pv-actions"><a class="pv-btn pv-btn-primary" href="#holiday">Explore Christmas picks ↓</a><a class="pv-btn pv-btn-ghost" href="#discover">See every product ↗</a></div><p class="pv-hero-note">Independent affiliate discovery · Trending themes are editorial, not a live sales ranking.</p></div><div class="pv-hero-stack" aria-label="Featured product research">'''+mini+'''</div></div></section><div class="pv-stats"><div class="pv-wrap pv-stat-row"><span><strong>138</strong> products to explore</span><span><strong>20</strong> searchable categories</span><span><strong>11</strong> buying guides</span><span><strong>10</strong> country shopping references</span></div></div><div class="pv-wrap pv-content">
<section class="pv-section" id="categories"><div class="pv-heading"><div><span class="pv-eyebrow">BROWSE BY INTEREST</span><h2>Find your kind of good.</h2><p>Useful upgrades, thoughtful gifts, everyday tech, and the little things that make life easier.</p></div><a href="/pirevo/catalog/">All categories ↗</a></div><nav class="pv-category-chips" aria-label="Popular shopping themes">'''+quick+'''</nav><div class="pv-cat-grid">'''+''.join(cat_tiles)+'''</div><button type="button" class="pv-expand" id="pv-all-cats" aria-expanded="false">View all 20 categories ↓</button></section>
'''+carousel("trending","Trending-inspired finds","An editorial shortlist inspired by shopping and seasonal themes. These are research picks, not verified real-time sales leaders.",spotlight,"/pirevo/trends/","IN THE CONVERSATION")+carousel("holiday","2026 Christmas gift & cozy home edit","Discover thoughtful decorations, creative gifts, tech treats and cozy comforts for holiday shopping. Confirm availability and shipping by country.",holiday,"/pirevo/categories/gifts/","SEASONAL DISCOVERY")+carousel("everyday","Everyday upgrades worth exploring","Practical tools and small comforts for living spaces, routines and workdays.",everyday,"/pirevo/catalog/","WORTH A CLOSER LOOK")+'''
<section class="pv-section"><div class="pv-callouts"><article class="pv-callout"><span class="pv-eyebrow">MAKE THE BETTER CHOICE</span><h3>Side by side.<br>Without the guesswork.</h3><p>Compare up to three product finds by intended use and tradeoffs, no invented prices or star ratings.</p><a href="/pirevo/compare/">Open the Buying Desk ↗</a></article><article class="pv-callout"><span class="pv-eyebrow">SHOP BEYOND BORDERS</span><h3>Find it here.<br>Check it locally.</h3><p>Our US Associates account includes ten earning marketplaces. Exact stock, variants and delivery vary by country.</p><a href="/pirevo/international/">International shopping guide ↗</a></article></div></section>
<section class="pv-section" id="discover"><div class="pv-heading"><div><span class="pv-eyebrow">THE WHOLE PIREVO COLLECTION</span><h2>All the good finds.</h2><p>Use search and filters to browse the 138-product catalog without getting lost in dozens of pages.</p></div><a href="/pirevo/catalog/">Open full directory ↗</a></div><div class="pv-discovery"><div class="pv-filters"><input type="search" id="pv-search" aria-label="Search product names, brands and uses" placeholder="Search products, brands, and what you need…" autocomplete="off"><select id="pv-cat-select" aria-label="Filter by category"><option value="">All 20 categories</option>'''+cat_options+'''</select><button type="button" id="pv-clear">Clear</button></div><p id="pv-count" class="pv-filter-status" role="status" aria-live="polite">Browse 138 products</p><div id="pv-products-grid" class="pv-discovery-grid">'''+''.join(card(p,"CURATED") for p in products)+'''</div><p class="pv-empty" id="pv-no-matches" hidden>No matching products yet. Try a different name or category.</p><button type="button" class="pv-loadmore" id="pv-more">Show more products ↓</button></div></section>
<section class="pv-section"><div class="pv-heading"><div><span class="pv-eyebrow">MORE THAN A LIST OF LINKS</span><h2>Discover with context.</h2><p>Buying guides and social-shopping themes help you compare what matters before visiting a retailer.</p></div><a href="/pirevo/guides/">Explore all guides ↗</a></div><div class="pv-callouts"><article class="pv-callout"><span class="pv-eyebrow">11 BUYING GUIDES</span><h3>Read before<br>you order.</h3><p>Notes about everyday storage, kitchen tools, travel essentials, gifts, and more.</p><a href="/pirevo/guides/">All buying guides ↗</a></article><article class="pv-callout"><span class="pv-eyebrow">SOCIAL SHOPPING</span><h3>What's being<br>talked about?</h3><p>Explore themed product research inspired by Pinterest, TikTok, and Instagram shopping conversations. Themes are not verified live sales.</p><a href="/pirevo/trends/">Explore social shopping ↗</a></article></div></section>
</div></main>'''+FOOTER+'''<script src="/pirevo/storefront-v5.js" defer></script><script src="/pirevo/marketplace-guide.js" defer></script><script src="/pirevo/config.js" defer></script><script src="/pirevo/business-analytics.js" defer></script></body></html>'''
# Keep the full searchable catalog near the top, directly after the first carousel.
discovery_start=body.index('<section class="pv-section" id="discover">')
discovery_end=body.index('</section>',discovery_start)+len('</section>')
discovery_block=body[discovery_start:discovery_end]
body=body[:discovery_start]+body[discovery_end:]
insert_at=body.index('<section class="pv-section" id="everyday">')
body=body[:insert_at]+discovery_block+body[insert_at:]
# The compact owner-made books and apps shelf is shown right after category cards.
owned=(B/"owned-products-block.html").read_text().strip()
assert owned.count('id="books"')==1 and owned.count('id="astralabs-apps"')==1
end_categories=body.index('</section>',body.index('<section class="pv-section" id="categories">'))+len('</section>')
body=body[:end_categories]+owned+body[end_categories:]
body=body.replace('<link rel="stylesheet" href="/pirevo/storefront-v5.css">','<link rel="stylesheet" href="/pirevo/storefront-v5.css"><link rel="stylesheet" href="/pirevo/owned-products.css">',1)
(B/"index.html").write_text(body.replace("138",str(len(products))))
# Unified visible chrome and product browse styling on every public consumer route. No account/analytics/admin pages.
dest=[B/"catalog/index.html",B/"trends/index.html",B/"compare/index.html",B/"international/index.html",B/"books/timmy-and-the-time-traveling-watch/index.html"]+list((B/"products").glob("*/index.html"))+list((B/"categories").glob("*/index.html"))+list((B/"guides").glob("*/index.html"))+[B/"guides/index.html"]
count=0
for file in dest:
 text=file.read_text()
 if "<body" not in text:continue
 text=re.sub(r'<header(?:\s[^>]*)?>[\s\S]*?</header>',HEADER,text,count=1)
 if 'class="pv-header"' not in text:
  text=re.sub(r'(<body(?:\s[^>]*)?>)',r'\1'+HEADER,text,count=1)
 text=re.sub(r'<footer(?:\s[^>]*)?>[\s\S]*?</footer>',FOOTER,text,count=1)
 if 'class="pv-footer"' not in text:text=text.replace("</body>",FOOTER+"</body>",1)
 # Remove stale standalone holiday top strips on individual product pages.
 if file.parent.parent.name=="categories":
  # Preserve the original shopper checklist, but put product cards above long advice.
  advice=re.search(r'<section class="tip">[\s\S]*?</section>',text)
  if advice:
   tip=advice.group(0)
   text=text[:advice.start()]+text[advice.end():]
   text=text.replace('</main>',tip+'</main>',1)
 if file.parent.parent.name=="products":
  text=re.sub(r'<div class="shop-announcement"[^>]*>[\s\S]*?</div>','',text,count=1)
 match=re.search(r'<body(?:\s+[^>]*)?>',text)
 old_class=re.search(r'\bclass="([^"]*)"',match.group(0)) if match else None
 preserved=[c for c in (old_class.group(1).split() if old_class else []) if c!='pv-ui']
 text=re.sub(r'<body(?:\s+[^>]*)?>','<body class="pv-ui'+(' '+' '.join(preserved) if preserved else '')+'">',text,count=1)
 # Ensure shared storefront styling and menu interaction are each inserted exactly once.
 style='<link rel="stylesheet" href="/pirevo/storefront-v5.css">'
 script='<script src="/pirevo/storefront-v5.js" defer></script>'
 if style not in text:text=text.replace('</head>',style+'</head>',1)
 if script not in text:text=text.replace('</body>',script+'</body>',1)
 # Trends hero copy previously claimed "46 rated" and repeated review counts; remove unsupported claims.
 if file==B/"trends/index.html":
  text=text.replace("Explore 46 rated Amazon catalog matches","Explore 46 researched Amazon catalog matches")
  text=re.sub(r'<p class="rating">[\s\S]*?</p>','',text)
  text=re.sub(r'<span class="rating">[\s\S]*?</span>','',text)
  text=text.replace("Individual ratings and review counts are catalog snapshots from Oct 9, 2026, not live Amazon values.","Product-match research reflects earlier editorial checks, not verified live Amazon rankings, stock or sales.")
 file.write_text(text)
 count+=1
# Trend source may include static percentage/review text in product cards; don't use ratings as current evidence.
# Discoverable Social Shopping section: indexed in both canonical sitemaps.
for sm in [R/"public/sitemap.xml",B/"sitemap.xml"]:
 xml=sm.read_text()
 url="https://www.astralabsph.com/pirevo/trends/"
 if "<loc>"+url+"</loc>" not in xml:
  xml=xml.replace("</urlset>",'<url><loc>'+url+'</loc><lastmod>2026-10-22</lastmod></url>\n</urlset>',1)
  sm.write_text(xml)
print(json.dumps({"home_products":len(products),"categories":len(cats),"carousel_trend_items":len(spotlight),"carousel_seasonal_items":len(holiday),"carousel_everyday_items":len(everyday),"unified_other_pages":count},indent=2))
