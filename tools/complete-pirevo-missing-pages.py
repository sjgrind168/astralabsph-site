from pathlib import Path
import subprocess,json,re,html,datetime
ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/"public/pirevo"
cmd='const fs=require("fs"),vm=require("vm"),c={window:{}};vm.runInNewContext(fs.readFileSync("public/pirevo/store-data.js","utf8"),c);console.log(JSON.stringify(c.window.PIREVO_STORE))'
store=json.loads(subprocess.check_output(["node","-e",cmd],cwd=ROOT,text=True))
ids=["levoit-core-200s","govee-table-lamp-2","cosrx-snail-mucin-96","elf-halo-glow-3"]
verify={"levoit-core-200s":"US identity verified on Amazon.com; stock shown at selected location","govee-table-lamp-2":"US identity verified on Amazon.com; stock shown at selected location","cosrx-snail-mucin-96":"US identity verified on Amazon.com; selected shipping destination unavailable","elf-halo-glow-3":"ASIN present in existing catalog; direct Amazon detail check timed out; exact variant must be independently confirmed"}
esc=lambda s:html.escape(str(s or ""),quote=True)
skip=re.compile(r"(ratings?|reviews?|bought|purchased|best.?seller|demand|rank|sales|star|★)",re.I)
today="2026-10-21"
css="""<style>
:root{color:#1b251f;background:#f6f4ec;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
*{box-sizing:border-box}body{margin:0}a{color:inherit}a:focus-visible{outline:3px solid #739c3f;outline-offset:3px}
.header{background:#1c2d26;color:#f4f8f2;padding:18px max(20px,calc((100vw - 1150px)/2));display:flex;gap:20px;justify-content:space-between;align-items:center;flex-wrap:wrap}
.header a{text-decoration:none}.brand{font-weight:900;letter-spacing:.14em;font-size:23px}.nav{display:flex;gap:18px;align-items:center;font-size:13px}
.main{max-width:1150px;padding:28px 22px 80px;margin:auto}.crumb{font-size:13px;color:#687667;margin-bottom:28px}
.hero{display:grid;grid-template-columns:1fr 1fr;gap:22px}.visual,.details{background:#fff;border:1px solid #dce3d8;border-radius:25px;min-width:0}
.visual{padding:18px}.canvas{aspect-ratio:1/1;border-radius:19px;background:radial-gradient(ellipse at 76% 17%,#e3e7cd,#cadccc 45%,#9cbbab);display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:38px;color:#21362f}
.canvas .monogram{border:2px solid #52725d;border-radius:22px;width:125px;height:125px;display:grid;place-items:center;font-family:Georgia,serif;font-size:56px;margin-bottom:24px}
.canvas .product-type{font-weight:800;font-size:16px;max-width:320px;line-height:1.4}.small-note{font-size:12px;line-height:1.6;color:#778477;margin:15px 5px 4px}
.details{padding:34px;align-self:start}.eyebrow{font-size:11px;font-weight:900;letter-spacing:.17em;color:#47765c;text-transform:uppercase}
h1{font-family:Georgia,serif;letter-spacing:-.04em;font-weight:500;font-size:clamp(35px,4.5vw,60px);line-height:1.06;margin:15px 0}
.subtitle{font-size:16px;line-height:1.65;color:#58665b}.brandline{font-size:13px;font-weight:800;color:#54715b}
.buyer{background:#ebf2e7;border-radius:15px;padding:16px;margin:24px 0 22px;line-height:1.7;font-size:13px}
.cta{display:flex;align-items:center;justify-content:space-between;gap:12px;background:#20352b;color:#fff;padding:16px;border-radius:12px;text-decoration:none;font-weight:800}
.cta:hover{background:#325b41}.policy{font-size:12px;line-height:1.6;color:#687769;margin:17px 0}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:17px;margin-top:27px}.panel{background:#fff;border:1px solid #dce3d8;border-radius:20px;padding:24px}
h2{font-size:23px;letter-spacing:-.025em;margin:0 0 16px}li{margin:12px 0;line-height:1.55}
.panel p{font-size:15px;line-height:1.7;color:#58665b}.meta{border-top:1px solid #e5e9e1;padding-top:16px;margin-top:16px;font-size:13px;line-height:1.8;color:#57665a}
.bottom{margin-top:30px;padding:23px;border-radius:16px;background:#e5ece5;line-height:1.6}.footer{background:#1c2d26;color:#f0f6f0;text-align:center;padding:27px 20px;font-size:13px;line-height:1.8}.footer a{color:#f0f6f0}
@media(max-width:790px){.hero,.grid{grid-template-columns:1fr}.details{padding:25px}.main{padding:24px 15px 56px}}
</style>"""
for slug in ids:
 p=next(p for p in store["products"] if p["slug"]==slug)
 path=BASE/"products"/slug/"index.html"
 if path.exists():
  path.unlink()  # Rebuild only these four dedicated generated pages, not manually edited pages.
 asin=p["asin"]
 if not re.fullmatch("[A-Z0-9]{10}",asin):raise ValueError("Invalid ASIN "+slug)
 url=f"https://www.astralabsph.com/pirevo/products/{slug}/index.html"
 cat=next(c for c in store["collections"] if c["id"]==p["collection"])
 title=p["fullName"]+" | PIREVO Buying Guide"
 description=(f"Explore {p['fullName']}. Compare intended use, specifications, and potential tradeoffs before shopping on Amazon.")[:260]
 best=p.get("bestFor") or "Check the exact product use case."
 caveat=p.get("caveat") or "Check seller, size, variant and local shipping before buying."
 feature=[str(a) for a in p.get("about",[]) if not skip.search(str(a))]
 if not feature:feature=["Compare features against the current manufacturer's specifications."]
 specs=[(k,v) for k,v in p.get("details",[]) if not skip.search(k) and not skip.search(v)]
 feature_html="".join(f"<li>{esc(a)}</li>" for a in feature[:5])
 spec_html="".join(f"<div><strong>{esc(k)}:</strong> {esc(v)}</div>" for k,v in specs[:6])
 name=p["shortName"]
 url_amzn=p["amazon"]
 if url_amzn!=f"https://www.amazon.com/dp/{asin}?tag=pirevo-20":raise ValueError("Affiliate target mismatch "+slug)
 item_note=verify[slug]
 requires_identity_check=(slug=="elf-halo-glow-3")
 buy_cta=('<div class="buyer"><strong>Amazon link pending verification.</strong> We are checking the exact Shade 3 listing and have temporarily disabled outbound buying from this page.</div>' if requires_identity_check else f'<a class="cta" href="{esc(url_amzn)}" target="_blank" rel="sponsored nofollow noopener noreferrer">Verify exact product on Amazon <span aria-hidden="true">↗</span></a>')
 # Editorial markup deliberately excludes Product rich-result types, unverifiable offers and customer ratings.
 ld={"@context":"https://schema.org","@graph":[{"@type":"Article","headline":title,"description":description,"mainEntityOfPage":url,"author":{"@type":"Organization","name":"PIREVO"},"publisher":{"@type":"Organization","name":"PIREVO","url":"https://www.astralabsph.com/pirevo/"},"about":{"@type":"Thing","name":p["fullName"],"identifier":asin}},{"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"PIREVO","item":"https://www.astralabsph.com/pirevo/"},{"@type":"ListItem","position":2,"name":cat["name"],"item":"https://www.astralabsph.com/pirevo/categories/"+p["collection"]+"/"},{"@type":"ListItem","position":3,"name":name,"item":url}]}]}
 ld_json=json.dumps(ld,ensure_ascii=False).replace("<",chr(92)+"u003c")
 page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}"><meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{url}"><meta property="og:type" content="article"><meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{url}">
<script type="application/ld+json">{ld_json}</script>{css}</head>
<body><header class="header"><a href="/pirevo/" class="brand">PIREVO</a><nav class="nav" aria-label="Main navigation"><a href="/pirevo/catalog/">All finds</a><a href="/pirevo/categories/{esc(p["collection"])}/">{esc(cat["name"])}</a><a href="/pirevo/affiliate-disclosure.html">Disclosure</a></nav></header>
<main class="main"><div class="crumb"><a href="/pirevo/">Home</a> / <a href="/pirevo/categories/{esc(p["collection"])}/">{esc(cat["name"])}</a> / {esc(name)}</div>
<div class="hero"><section class="visual"><div class="canvas"><div class="monogram" aria-hidden="true">{esc(p["brand"][0].upper())}</div><div class="eyebrow">{esc(p["brand"])}</div><div class="product-type">{esc(name)}</div></div><p class="small-note">Editorial product card. This is not a retail photograph. Verify the exact product image, finish and variant at Amazon.</p></section>
<section class="details"><div class="eyebrow">Independent buying notes</div><h1>{esc(name)}</h1><p class="brandline">{esc(p["brand"])} · Model reference {esc(asin)}</p>
<p class="subtitle">{esc(best)}</p><div class="buyer"><strong>Before you buy</strong><div>{esc(caveat)}</div></div>
{buy_cta}
<p class="policy">As an Amazon Associate I earn from qualifying purchases. Amazon handles checkout. Price, seller, shipping, stock and regional product availability can change.</p></section></div>
<div class="grid"><section class="panel"><h2>What to compare</h2><ul>{feature_html}</ul><p>Information summarizes the listed model. Confirm specifications and current availability on the retailer page before ordering.</p></section>
<section class="panel"><h2>Variant and fit checklist</h2><div class="meta">{spec_html}<div><strong>US reference ASIN:</strong> {esc(asin)}</div></div><p><strong>Important:</strong> {esc(caveat)}</p></section></div>
<section class="bottom"><strong>Shopping outside the United States?</strong> Eligible Amazon OneLink visits may route to another Amazon marketplace, but exact product matching, eligibility and delivery differ by country. PIREVO has not verified this product in every region. Check the final local product details and its seller before placing an order.</section>
<p><a href="/pirevo/catalog/">← Browse all researched PIREVO products</a></p>
</main><footer class="footer"><strong>PIREVO</strong> · Smart finds worth discovering.<p>Independent product research; purchases are completed on Amazon.</p><a href="/pirevo/affiliate-disclosure.html">Affiliate disclosure</a> · <a href="/pirevo/editorial-policy.html">Editorial policy</a></footer><script src="/pirevo/config.js" defer></script><script src="/pirevo/business-analytics.js" defer></script></body></html>'''
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(page)
 print("created",slug,"identity="+item_note)
for sitemap in [ROOT/"public/sitemap.xml",BASE/"sitemap.xml"]:
 s=sitemap.read_text()
 for slug in ids:
  target=f"https://www.astralabsph.com/pirevo/products/{slug}/index.html"
  found=re.search(r'(<url><loc>'+re.escape(target)+r'</loc><lastmod>)([^<]+)(</lastmod></url>)',s)
  if found:s=s[:found.start(2)]+today+s[found.end(2):]
  else:s=s.replace("</urlset>",f"<url><loc>{target}</loc><lastmod>{today}</lastmod></url>\\n</urlset>")
 sitemap.write_text(s)
manifest=ROOT/"marketing/pirevo/PIREVO_MARKETPLACE_READINESS_20261021.json"
data=json.loads(manifest.read_text())
for item in data["products"]:
 if item["slug"] in ids:
  item["detail_page_exists"]=True
  item["us_product_identity_20261021"]=verify[item["slug"]]
data["four_missing_product_pages_fixed_20261021"]={"created":ids,"images":"No unlicensed retailer images used for new pages","stock":"No live price or availability assertions on PIREVO","affiliate":"Original valid US pirevo-20 destinations preserved"}
manifest.write_text(json.dumps(data,indent=2)+"\n")
print("updated sitemaps, verification ledger")
