#!/usr/bin/env python3
"""Publish only exact-ASIN verified, originally researched PIREVO product records.
Includes original typographic category art, no copied seller photos or ratings.
"""
from pathlib import Path
import json,re,html,subprocess
R=Path(__file__).resolve().parent.parent;P=R/"public/pirevo"
data=[
{"slug":"bedsure-satin-pillowcase-queen-grey-2","asin":"B0725WFLMB","brand":"Bedsure","shortName":"Satin Pillowcases, Queen Set of 2","fullName":"Bedsure Satin Pillowcases, Queen Size, Grey, Pack of 2","collection":"sleep-bedroom","bestFor":"An easy-to-wash pillowcase alternative with a satin-style finish for a queen-size pillow setup.","caveat":"Satin is a weave, not proof of genuine silk. Confirm fabric composition, pillowcase dimensions, envelope closure and care instructions for the selected color.","details":[["Size","Queen; verify exact dimensions on Amazon"],["Included","Two pillowcases"],["Material","Confirm fiber content in seller's exact listing"]],"about":["Choosing satin-style covers is mainly about care, comfort and correct pillow size.","A two-pack helps replace matching cases together, but check the closure style and fabric label."],"evidence":"Amazon.com exact product title and ASIN checked 2026-10-22; historic source overview: asinsight.com report. Not a first-hand review."},
{"slug":"bedsure-prewashed-comforter-twin-xl-green","asin":"B0D145689D","brand":"Bedsure","shortName":"Prewashed Comforter, Twin/Twin XL","fullName":"Bedsure Prewashed Comforter Set, Twin/Twin XL, Emerald Green","collection":"sleep-bedroom","bestFor":"Dorm, guest-room or Twin XL bedroom comfort using a lighter synthetic comforter set.","caveat":"Confirm fill weight, included pillowcase count, true Twin XL dimensions, laundry instructions and warmth preference. This is a comforter set, not a duvet cover.","details":[["Listed format","Twin/Twin XL comforter set"],["Color","Emerald Green at checked ASIN"],["Included","Comforter with matching case; verify quantity"],["Care","Verify exact care label"]],"about":["A practical bedroom comparison should start with mattress dimensions and the desired warmth level.","Check whether synthetic fill and machine washing suit the user instead of assuming all comforters breathe the same."],"evidence":"Amazon.com exact ASIN/title checked 2026-10-22; current manufacturer has related prewashed-polyester line, but specifications vary by SKU."},
{"slug":"bedsure-washed-cotton-duvet-oversized-king","asin":"B0CSYXYWDZ","brand":"Bedsure","shortName":"Washed Cotton Duvet Cover, Oversized King","fullName":"Bedsure PureWoven 100% Washed Cotton Duvet Cover Set, Oversized King, 3 Pieces","collection":"sleep-bedroom","bestFor":"Large-bedding setups needing an oversized king duvet cover without replacing the duvet insert.","caveat":"This listing is for a duvet cover set, NOT a filled comforter. Confirm oversized king dimensions, insert compatibility, fabric, zipper closure and actual included pillow shams.","details":[["Type","Duvet cover set; duvet insert not included"],["Size","Oversized King; check 120 × 98 inch variant"],["Pieces","Three pieces at checked ASIN"],["Material","Washed cotton; verify exact seller listing"]],"about":["For duvet covers, compare attachment ties, closure design and the duvet-insert dimensions first.","Cotton and polyester bedding have different care and breathability characteristics; compare based on climate and washing habits."],"evidence":"Amazon.com exact ASIN/title checked 2026-10-22. Manufacturer Bedsure and retailer Lowe's describe related washed cotton line; check SKU-specific variation."},
{"slug":"black-decker-ldx120c-cordless-drill","asin":"B005NNF0YU","brand":"BLACK+DECKER","shortName":"20V MAX Cordless Drill/Driver LDX120C","fullName":"BLACK+DECKER LDX120C 20V MAX Cordless Drill and Driver, 3/8 Inch","collection":"tools-diy","bestFor":"Common household drill and screwdriving tasks using a compact cordless drill with adjustable clutch.","caveat":"Check the exact drill/battery/charger bundle, chuck size, material suitability, safety instructions and compatibility with existing 20V MAX batteries before ordering.","details":[["Model","LDX120C"],["Chuck","3/8 inch"],["Control","11-position clutch"],["Power","20V MAX battery system; check actual included bundle"]],"about":["The 11-position clutch helps regulate driving force for different fastening tasks.","Built-in LED can help illuminate darker workspaces, but the correct bit and workpiece safety remain essential."],"evidence":"Amazon.com exact LDX120C title and ASIN verified 2026-10-22; manufacturer BLACK+DECKER lists 11 clutch positions and 20V MAX system."}
]
f=R/"marketing/pirevo/PRODUCT_EXPANSION_BATCH_20261022.json"
f.write_text(json.dumps({"date":"2026-10-22","provenance":"Direct Amazon.com exact product identity plus manufacturer/editorial research. No price, bestseller rank, reviews, delivery, licensing or commission guarantee.","research_type":"model and variant checked, editorial descriptions written without first-hand testing","records":data},indent=2,ensure_ascii=False)+"\n")
store=P/"store-data.js"
text=store.read_text()
existing=set(re.findall(r'"slug":\s*"([a-z0-9-]+)"',text))
for p in data:
 if p["slug"] in existing:continue
 record={k:v for k,v in p.items() if k not in ("evidence",)}
 record.update({"image":"/pirevo/editorial/"+p["slug"]+".svg","amazon":"https://www.amazon.com/dp/"+p["asin"]+"?tag=pirevo-20","galleryIds":[]})
 j=json.dumps(record,ensure_ascii=False,indent=4)
 if not text.endswith("  ]\n};\n"):raise ValueError("Unexpected end of canonical store-data.js")
 text=text.removesuffix("  ]\n};\n")+",\n"+j+"\n  ]\n};\n"
 existing.add(p["slug"])
store.write_text(text)
icons={"sleep-bedroom":"REST & COMFORT","tools-diy":"TOOLS & PROJECTS"}
assetdir=P/"editorial";assetdir.mkdir(exist_ok=True)
for p in data:
 category=icons.get(p["collection"],"EDITORIAL RESEARCH")
 brand=html.escape(p["brand"],quote=True)
 label=html.escape(p["shortName"],quote=True)
 svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" role="img" aria-label="Editorial typography for {label}, not a manufacturer photo">
<rect width="600" height="600" rx="27" fill="#e8f1e9"/><path d="M0 392 Q140 323 298 406 T600 368 V600 H0 Z" fill="#bfd7c5"/>
<circle cx="445" cy="142" r="100" fill="#d7e7d5"/><circle cx="445" cy="142" r="58" fill="#87ae99" opacity=".65"/>
<text x="45" y="75" fill="#38634d" font-family="Arial,sans-serif" font-weight="700" font-size="23" letter-spacing="4">{html.escape(category)}</text>
<text x="45" y="253" fill="#194733" font-family="Georgia,serif" font-weight="700" font-size="60">PIREVO</text>
<text x="45" y="313" fill="#37674e" font-family="Arial,sans-serif" font-size="26">{brand}</text>
<text x="45" y="500" fill="#1d5038" font-family="Arial,sans-serif" font-size="24">BUYING RESEARCH</text>
<text x="45" y="545" fill="#577866" font-family="Arial,sans-serif" font-size="18">Editorial illustration · Not a product photo</text>
</svg>'''
 (assetdir/(p["slug"]+".svg")).write_text(svg)
 page=P/"products"/p["slug"]/"index.html";page.parent.mkdir(parents=True,exist_ok=True)
 url="https://www.astralabsph.com/pirevo/products/"+p["slug"]+"/index.html"
 sub=f"{p['fullName']} | Buyer Notes | PIREVO"
 summary=f"Explore how {p['fullName']} fits your use case. Check variants, dimensions and tradeoffs before purchasing from Amazon."
 schema={"@context":"https://schema.org","@type":"Article","headline":sub,"description":summary,"mainEntityOfPage":url,"author":{"@type":"Organization","name":"PIREVO"}}
 list_html="".join("<li>"+html.escape(x)+"</li>" for x in p["about"])
 details="".join("<tr><th>"+html.escape(k)+"</th><td>"+html.escape(v)+"</td></tr>" for k,v in p["details"])
 content=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(sub)}</title><meta name="description" content="{html.escape(summary)}">
<link rel="canonical" href="{url}"><meta name="robots" content="index,follow,max-image-preview:large">
<script type="application/ld+json">{json.dumps(schema,ensure_ascii=False)}</script>
<style>
main.pdp-wrap{{max-width:1090px;margin:auto;padding:33px 20px 65px;color:#183d2c}}.pdp-hero{{display:grid;grid-template-columns:minmax(0,45%) 1fr;gap:33px;align-items:start}}
.pdp-art{{background:#f0f6f0;border-radius:18px;padding:22px;border:1px solid #d9e7da}}.pdp-art img{{width:100%;display:block;border-radius:14px}}
.pdp-panel{{background:#fff;border:1px solid #d7e6da;border-radius:20px;padding:28px}}.pdp-panel h1{{font:500 clamp(32px,4vw,50px)/1.15 Georgia,serif;letter-spacing:-.035em;margin:14px 0 18px}}
.pdp-eyebrow{{color:#4f8565;font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:.09em}}
.pdp-panel p,.pdp-note p{{font-size:15px;line-height:1.75;color:#53665a}}
.pdp-action{{display:inline-block;background:#164f38;color:#fff!important;text-decoration:none;font-weight:800;padding:14px 19px;border-radius:11px;margin:10px 0}}
.pdp-disclaimer{{font-size:12px!important;color:#647e6b!important}}
.pdp-detail-grid{{display:grid;grid-template-columns:1fr 1fr;gap:19px;margin-top:23px}}.pdp-note{{background:#fff;border:1px solid #d8e5db;border-radius:17px;padding:23px}}
.pdp-note h2{{font:500 28px/1.2 Georgia,serif}}.pdp-note li{{margin:10px 0;line-height:1.6}}.pdp-note table{{border-collapse:collapse;width:100%;font-size:13px}}.pdp-note th,.pdp-note td{{padding:11px 6px;text-align:left;border-bottom:1px solid #e6eee7;vertical-align:top}}.pdp-note th{{width:34%}}
@media(max-width:750px){{.pdp-hero,.pdp-detail-grid{{grid-template-columns:1fr}}.pdp-art{{max-width:480px;margin:auto}}main.pdp-wrap{{padding:20px 15px 42px}}}}
</style></head><body>
<main class="pdp-wrap">
<nav aria-label="Breadcrumb"><a href="/pirevo/">PIREVO</a> / <a href="/pirevo/categories/{p['collection']}/">Category</a> / {html.escape(p['shortName'])}</nav>
<div class="pdp-hero"><div class="pdp-art"><img src="/pirevo/editorial/{p['slug']}.svg" alt="PIREVO editorial illustration, not a retail product photograph" loading="eager"><p class="pdp-disclaimer">Textual editorial graphic. Visit Amazon for current product photographs and variation choices.</p></div>
<div class="pdp-panel"><div class="pdp-eyebrow">Independent buying notes · {html.escape(p['brand'])}</div>
<h1>{html.escape(p['shortName'])}</h1><p>{html.escape(p['bestFor'])}</p><p><strong>What to check:</strong> {html.escape(p['caveat'])}</p>
<a class="pdp-action" href="https://www.amazon.com/dp/{p['asin']}?tag=pirevo-20" target="_blank" rel="sponsored nofollow noopener noreferrer">Check exact model on Amazon ↗</a>
<p class="pdp-disclaimer">As an Amazon Associate I earn from qualifying purchases. Price, availability, seller, delivery and variant must be confirmed at the retailer.</p>
<p class="pdp-disclaimer">Model checked against Amazon.com ASIN {p['asin']} on October 22, 2026. Not hands-on product testing or proof of a current bestseller rank.</p></div></div>
<div class="pdp-detail-grid"><section class="pdp-note"><h2>What matters before buying</h2><ul>{list_html}</ul></section>
<section class="pdp-note"><h2>Model and fit</h2><table>{details}</table></section></div>
<section class="pdp-note" style="margin-top:20px"><h2>Buying across countries?</h2><p>Amazon's global earning preferences include ten marketplaces, but this particular ASIN has not been verified for stock, identical variants, shipping or commission attribution across countries. Check the local product title and terms after clicking through.</p>
<p><a href="/pirevo/international/">International shopping guide →</a> · <a href="/pirevo/compare/?p={p['slug']}">Compare in PIREVO Buying Desk →</a></p></section></main>
</body></html>'''
 page.write_text(content)
 for sitemap in [R/"public/sitemap.xml",P/"sitemap.xml"]:
  xml=sitemap.read_text()
  if "<loc>"+url+"</loc>" not in xml:
   xml=xml.replace("</urlset>","<url><loc>"+url+"</loc><lastmod>2026-10-22</lastmod></url>\n</urlset>")
  sitemap.write_text(xml)
print(json.dumps({"new_product_pages":len(data),"categories":{"sleep-bedroom":3,"tools-diy":1},"photo_rights":"No Amazon images used","direct_verification":"Amazon exact title and ASIN 2026-10-22"},indent=2))
