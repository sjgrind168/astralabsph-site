#!/usr/bin/env python3
"""Add a non-deceptive global shopper guide and country selector to PIREVO static pages.
Does not modify Amazon product links, taxes, payouts or checkout behavior.
Re-run after tools/generate-pirevo-catalog.py to retain inclusions on regenerated pages.
"""
from pathlib import Path
from html import escape
import json, re, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent.parent
WEB=ROOT/"public/pirevo"
GUIDE=WEB/"international"/"index.html"
MANIFEST=ROOT/"marketing/pirevo/PIREVO_MARKETPLACE_READINESS_20261021.json"
manifest=json.loads(MANIFEST.read_text())
iso={"US":"United States","CA":"Canada","UK":"United Kingdom","DE":"Germany","FR":"France","IT":"Italy","ES":"Spain","NL":"Netherlands","PL":"Poland","SE":"Sweden"}
records=manifest.get("regional_product_spotchecks_20261021",{})
sample={}
for slug,regions in records.items():
 if not isinstance(regions,dict):continue
 checked={}
 for region,detail in regions.items():
  if region not in iso or not isinstance(detail,dict):continue
  state=str(detail.get("status",""))
  asin=detail.get("asin")
  if (state.startswith("EXACT_") or state in ("CORRECT_PRODUCT","EXACT_BRAND_AND_MODEL_IN_STOCK_WHEN_CHECKED")) and isinstance(asin,str) and re.fullmatch("[A-Z0-9]{10}",asin):
   checked[region]={"model":"checked","asin":asin,"checked":"October 21, 2026"}
 if checked:sample[slug]=checked
for slug,asin in {"levoit-core-200s":"B08FJ678YK","govee-table-lamp-2":"B0D41XL87F","cosrx-snail-mucin-96":"B00PBX3L7K"}.items():
 sample.setdefault(slug,{})["US"]={"model":"checked","asin":asin,"checked":"October 21, 2026"}
evidence={"verified_at":"2026-10-21","notes":"Human-observed model identity only; no real-time stock, country-specific delivery, OneLink redirect, or commission proof. Other products and countries are unverified.","products":sample}
(WEB/"regional-evidence.json").write_text(json.dumps(evidence,indent=2)+"\n")
countries=[
 ("US","United States","amazon.com"),("CA","Canada","amazon.ca"),("UK","United Kingdom","amazon.co.uk"),
 ("DE","Germany","amazon.de"),("FR","France","amazon.fr"),("IT","Italy","amazon.it"),
 ("ES","Spain","amazon.es"),("NL","Netherlands","amazon.nl"),("PL","Poland","amazon.pl"),("SE","Sweden","amazon.se")
]
tiles="".join('<div class="market-card"><strong>'+escape(c)+'</strong><span>'+escape(domain)+'</span><small>Included in global earning preferences</small></div>' for _,c,domain in countries)
url="https://www.astralabsph.com/pirevo/international/"
title="Shop PIREVO Internationally | Amazon OneLink Country Guide"
description="How PIREVO's Amazon affiliate product links work for US, Canada, UK, Germany, France, Italy, Spain, Netherlands, Poland and Sweden. Learn how regional product matches, shipping and affiliate offers differ."
schema={"@context":"https://schema.org","@graph":[{"@type":"WebPage","name":title,"url":url,"description":description},{"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"PIREVO","item":"https://www.astralabsph.com/pirevo/"},{"@type":"ListItem","position":2,"name":"International shopping","item":url}]}]}
styles="""<style>
:root{font:16px/1.65 Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#172f29;background:#f7faf7}
*{box-sizing:border-box}body{margin:0}a{color:#24533e}header{background:#15332a;padding:16px max(20px,calc((100vw - 1170px)/2));display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;color:#fff}header a{color:#f7fff5;text-decoration:none}header b{letter-spacing:.16em;font-size:23px}header nav{display:flex;gap:18px;flex-wrap:wrap;font-size:14px}
main{max-width:1120px;margin:auto;padding:34px 20px 90px}.crumbs{font-size:13px;color:#536c5d}.eyebrow{color:#437c58;letter-spacing:.13em;text-transform:uppercase;font-size:12px;font-weight:800;margin-top:33px}
h1{font-size:clamp(35px,5vw,64px);line-height:1.1;letter-spacing:-.043em;max-width:820px;margin:14px 0 22px}
.intro{max-width:800px;font-size:19px;line-height:1.7;color:#4d6557}
h2{font-size:clamp(25px,3vw,35px);line-height:1.2;letter-spacing:-.03em;margin:42px 0 14px}
.market-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;margin:23px 0}
.market-card{padding:18px 16px;border-radius:13px;background:white;border:1px solid #d8e5da;display:flex;flex-direction:column;gap:4px}
.market-card strong{font-size:16px}.market-card span{font-size:13px;color:#385d43}.market-card small{font-size:11px;color:#718373;line-height:1.35;margin-top:6px}
.panel{background:#e8f0e7;border-radius:18px;padding:23px 27px;margin:26px 0}.panel strong{font-size:16px}
.steps{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:15px;margin:22px 0}.step{border:1px solid #dce6df;background:#fff;border-radius:17px;padding:24px}
.step b{display:inline-grid;place-items:center;border-radius:50%;width:32px;height:32px;background:#163f30;color:#fff}
.step h3{margin:13px 0 9px;line-height:1.3}.step p{font-size:14px;color:#476354;line-height:1.65}
.rule{border-bottom:1px solid #dce5dc;padding:20px 0}.rule h3{font-size:18px;line-height:1.4;margin:0 0 7px}.rule p{margin:0;color:#4d6356}
.button{display:inline-block;padding:13px 21px;background:#193c2b;border-radius:10px;color:white;text-decoration:none;font-weight:800}
footer{background:#173229;color:#e9f6ec;text-align:center;padding:35px 20px;font-size:13px}footer a{color:white}
@media(max-width:980px){.market-grid{grid-template-columns:repeat(3,1fr)}.steps{grid-template-columns:1fr}}
@media(max-width:590px){.market-grid{grid-template-columns:repeat(2,1fr)}.panel{padding:19px 16px}main{padding:24px 14px 65px}}
</style>"""
page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>'''+escape(title)+'''</title><meta name="description" content="'''+escape(description,quote=True)+'''"><meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="'''+url+'''"><meta property="og:title" content="'''+escape(title,quote=True)+'''"><meta property="og:description" content="'''+escape(description,quote=True)+'''">
<script type="application/ld+json">'''+json.dumps(schema,ensure_ascii=False)+'''</script>'''+styles+'''</head>
<body><header><a href="/pirevo/"><b>PIREVO</b></a><nav><a href="/pirevo/catalog/">All products</a><a href="/pirevo/categories/tech/">Tech</a><a href="/pirevo/affiliate-disclosure.html">Disclosure</a></nav></header>
<main><div class="crumbs"><a href="/pirevo/">Home</a> / International shopping</div>
<div class="eyebrow">Independent product discovery · Global buying guide</div><h1>One discovery store. Ten eligible Amazon marketplaces.</h1>
<p class="intro">PIREVO curates product buying notes and refers shoppers to Amazon. Our US Associates store ID is <strong>pirevo-20</strong>. Amazon's Global Earning Preferences currently include ten marketplaces. This does <strong>not</strong> mean that each product is listed, deliverable or commissionable in every country.</p>
<section class="panel"><strong>What Amazon Support confirmed on October 22, 2026</strong><p>Our existing US-based Global Earning Preferences cover the ten marketplaces below. The support agent said separate Associates registrations for the Netherlands, Poland and Sweden are not required under this account setup. Japan is outside the ten and requires a separate Associates account. Individual product matching, redirects and commissions were not independently tested by a purchase.</p></section>
<h2 id="countries">Countries in our current earning preferences</h2><div class="market-grid">'''+tiles+'''</div>
<h2>How to shop through PIREVO</h2><div class="steps">
<div class="step"><b>1</b><h3>Explore and compare</h3><p>Use our product catalog, categories and independent buying notes. Read the exact variant, compatibility and fit information before visiting a retailer.</p></div>
<div class="step"><b>2</b><h3>Choose your country</h3><p>Set your shopping country in the selector. This shows eligible marketplace guidance. We do not collect your GPS location or silently rewrite the affiliate product URL.</p></div>
<div class="step"><b>3</b><h3>Check the final Amazon listing</h3><p>Tap the Amazon link to open the retailer. OneLink may redirect you to a regional listing of an identical or similar product. Confirm the title, seller, size, price, delivery and final checkout terms.</p></div></div>
<h2>Questions international shoppers should ask</h2>
<div class="rule"><h3>Will every PIREVO product be sold in my country?</h3><p>No. Amazon marketplace inventories, product identifiers, variations, sellers and shipping restrictions differ. Some US products have a different ASIN overseas, while others have no match. The final retailer page is the source of truth.</p></div>
<div class="rule"><h3>Why does a US product link lead to a different product?</h3><p>Amazon's localization may select the same product or a similar local offering when an exact match is not available. Check the local title, model, size, color and seller. Never order on the assumption that two regional listings are identical.</p></div>
<div class="rule"><h3>Do I pay PIREVO?</h3><p>No. PIREVO is an independent affiliate discovery website, not an Amazon-owned store or checkout. Amazon is responsible for stock, shipping estimates, currency display, payment and customer service. As an Amazon Associate I earn from qualifying purchases.</p></div>
<div class="rule"><h3>Are prices displayed in my currency?</h3><p>We do not publish volatile retailer prices or exchange-rate estimates. Amazon displays its current local prices and applicable shipping and taxes during shopping and checkout.</p></div>
<div class="rule"><h3>Can I shop from Japan or Australia?</h3><p>These are not part of the ten enabled Global Earning Preferences verified for PIREVO. Their separate Associates arrangements are not yet confirmed. You may browse our research, but a compatible affiliate referral or delivery service is not guaranteed.</p></div>
<div class="rule"><h3>What does “model checked” mean on a product page?</h3><p>A model-identity note records that a particular variant was observed in a marketplace on a dated research check. It does not verify live stock, availability for your address, exact Amazon OneLink redirection or a commission payment.</p></div>
<section class="panel"><strong>Trust and limitations</strong><p>Amazon Support confirmed our account preferences and payment assignments; product-level matching is a separate audit. We do not fabricate reviews, star ratings, in-stock labels or current prices. If an exact Amazon listing cannot be confirmed, its buying button may be held for verification.</p>
<a href="/pirevo/editorial-policy.html">Read PIREVO's editorial policy →</a></section>
<p><a class="button" href="/pirevo/catalog/">Browse researched PIREVO finds →</a></p>
</main><footer><strong>PIREVO · Smart finds worth discovering.</strong><p>Independent affiliate discovery. Amazon handles checkout.</p><a href="/pirevo/affiliate-disclosure.html">Affiliate disclosure</a> · <a href="/pirevo/privacy.html">Privacy</a></footer></body></html>'''
GUIDE.parent.mkdir(parents=True,exist_ok=True)
GUIDE.write_text(page)
jslink='<script src="/pirevo/marketplace-guide.js" defer></script>'
csslink='<link rel="stylesheet" href="/pirevo/marketplace-guide.css">'
favlink='<link rel="icon" type="image/svg+xml" href="/pirevo/favicon.svg">'
files=list((WEB/"products").glob("*/index.html"))+list((WEB/"categories").glob("*/index.html"))+[WEB/"catalog/index.html",WEB/"index.html",GUIDE]
updated=0
for file in files:
 s=file.read_text()
 if jslink not in s:
  if "</body>" not in s:raise RuntimeError("body missing "+str(file))
  s=s.replace("</body>",jslink+"</body>",1)
  updated+=1
 if csslink not in s:
  if "</head>" not in s:raise RuntimeError("head missing "+str(file))
  s=s.replace("</head>",csslink+"</head>",1)
 if favlink not in s:
  s=s.replace("</head>",favlink+"</head>",1)
 file.write_text(s)
for xml in [ROOT/"public/sitemap.xml",WEB/"sitemap.xml"]:
 s=xml.read_text()
 entry='<url><loc>'+url+'</loc><lastmod>2026-10-22</lastmod></url>'
 if url not in s:s=s.replace("</urlset>",entry+"\n</urlset>")
 xml.write_text(s)
print(json.dumps({"widget_pages":len(files),"new_script_injections":updated,"evidence_products":{x:list(y.keys()) for x,y in sample.items()},"guide":url},indent=2))
