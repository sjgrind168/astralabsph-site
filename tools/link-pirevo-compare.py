#!/usr/bin/env python3
"""Connect PIREVO Buying Desk to catalog, categories, and product detail pages.
Run after catalog and product generators. Idempotent, preserves Amazon tagged links.
"""
from pathlib import Path
import json, subprocess,re,html
R=Path(__file__).resolve().parent.parent;P=R/"public/pirevo"
raw='const fs=require("fs"),vm=require("vm"),w={};vm.runInNewContext(fs.readFileSync("public/pirevo/store-data.js","utf8"),{window:w});process.stdout.write(JSON.stringify(w.PIREVO_STORE))'
store=json.loads(subprocess.check_output(["node","-e",raw],cwd=R,text=True))
preamble='<div class="pirevo-compare-intro" style="max-width:1120px;margin:24px auto;padding:19px 24px;background:#e6efdf;border:1px solid #d1dfcf;border-radius:14px;color:#294831"><strong>Compare your options before buying.</strong> Explore which product fits your routine, available space and priorities. <a href="/pirevo/compare/" style="font-weight:850">Open the PIREVO Buying Desk →</a></div>'
f=P/"catalog/index.html";s=f.read_text();s=s.replace(preamble,"")
if '</main>' not in s:raise ValueError("catalog no main")
s=s.replace('<h2>Shop by category</h2>',preamble+'<h2>Shop by category</h2>',1)
f.write_text(s)
n=0
for p in store["products"]:
 f=P/"products"/p["slug"]/"index.html"
 if not f.exists():raise FileNotFoundError(str(f))
 s=f.read_text()
 s=re.sub(r'<aside class="pirevo-compare-linkout"[\s\S]*?</aside>','',s)
 path="/pirevo/compare/?p="+p["slug"]
 label='<aside class="pirevo-compare-linkout" aria-label="Compare products" style="max-width:1120px;margin:24px auto;padding:19px 23px;border:1px solid #d2ded3;background:#eff4e9;color:#274738;border-radius:14px"><strong>Still deciding?</strong> <a href="'+path+'" style="font-weight:850">Compare this product with other PIREVO finds →</a><p style="font-size:12px;margin:7px 0 0">Editorial product fit and tradeoffs, not live Amazon prices or ratings.</p></aside>'
 if '</main>' not in s:raise RuntimeError("No main "+p["slug"])
 s=s.replace('</main>',label+'</main>',1)
 f.write_text(s);n+=1
for c in store["collections"]:
 f=P/"categories"/c["id"]/"index.html"
 if not f.exists():continue
 s=f.read_text()
 s=re.sub(r'<aside class="pirevo-category-compare"[\s\S]*?</aside>','',s)
 h='<aside class="pirevo-category-compare" aria-label="Compare products" style="max-width:1120px;margin:20px auto;padding:18px 23px;background:#ecf2e9;border-radius:14px"><strong>Compare products:</strong> <a href="/pirevo/compare/">Open Buying Desk →</a> to compare fit and product tradeoffs side by side.</aside>'
 if '</main>' not in s:raise RuntimeError("no main "+c["id"])
 s=s.replace('</main>',h+'</main>',1);f.write_text(s)
home=P/"index.html";s=home.read_text()
s=re.sub(r'<aside class="pirevo-home-compare"[\s\S]*?</aside>','',s)
if '</main>' in s:
 s=s.replace('</main>','<aside class="pirevo-home-compare" style="max-width:1100px;margin:25px auto;padding:18px;background:#e7efe7;border-radius:15px;text-align:center">Choosing between similar products? <a href="/pirevo/compare/" style="font-weight:850">Use the PIREVO Buying Desk →</a></aside></main>',1)
 home.write_text(s)
print(json.dumps({"catalog_entry":True,"product_comparison_entries":n,"category_entries":len(store["collections"]),"homepage_entry":True}))
