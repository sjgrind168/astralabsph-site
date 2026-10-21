from pathlib import Path
import re,json,html,subprocess
root=Path(__file__).resolve().parent.parent;pub=root/"public/pirevo"
query='const fs=require("fs"),vm=require("vm"),w={window:{}};vm.runInNewContext(fs.readFileSync("public/pirevo/store-data.js","utf8"),w);console.log(JSON.stringify(w.window.PIREVO_STORE.products))'
items={x["slug"]:x for x in json.loads(subprocess.check_output(["node","-e",query],cwd=root,text=True))}
n=0
for f in (pub/"products").glob("*/index.html"):
 s=f.read_text();x=items.get(f.parent.name,{})
 name=x.get("fullName") or f.parent.name;why=x.get("bestFor") or "Check the exact product model and compatibility before buying."
 ttl=(name+" | PIREVO Product Buying Guide")[:145];desc=(name+". "+why+" Verify current Amazon seller, variant and availability.")[:260]
 s=re.sub(r'<div class="pdp-proof">.*?</div>','<div class="pdp-proof"><span><strong>Compare details</strong> Check exact model and retailer availability.</span></div>',s,flags=re.S)
 s=re.sub(r'<div class="shop-rating">.*?</div>',"",s,flags=re.S)
 s=re.sub(r'<p class="pdp-why">.*?</p>','<p class="pdp-why">'+html.escape(why)+'</p>',s,flags=re.S)
 s=re.sub(r'<li>[^<]*[★☆][^<]*</li>',"",s)
 for pattern,replacement in [(r'<title>.*?</title>',"<title>"+html.escape(ttl)+"</title>"),(r'<meta name="description" content="[^"]*">','<meta name="description" content="'+html.escape(desc,quote=True)+'">'),(r'<meta property="og:title" content="[^"]*">','<meta property="og:title" content="'+html.escape(ttl,quote=True)+'">'),(r'<meta property="og:description" content="[^"]*">','<meta property="og:description" content="'+html.escape(desc,quote=True)+'">')]:
  s=re.sub(pattern,replacement,s,flags=re.S)
 m=re.search(r'<script type="application/ld\+json">(.*?)</script>',s,re.S)
 if m:
  ld=json.loads(m.group(1))
  for z in ld.get("@graph",[]):
   if z.get("@type")=="WebPage":z.update(name=ttl,description=desc)
   if z.get("@type")=="Article":z.update(headline=ttl,description=desc)
  s=s[:m.start(1)]+json.dumps(ld,ensure_ascii=False).replace("<","\\u003c")+s[m.end(1):]
 f.write_text(s);n+=1
h=pub/"index.html";h.write_text(re.sub(r'<div class="shop-rating">.*?</div>',"",h.read_text(),flags=re.S))
for fname in ["shop.js","product.js"]:
 f=pub/fname;s=f.read_text()
 s=re.sub(r'<div class=\\"shop-rating\\">.*?</div>',"",s,flags=re.S)
 s=re.sub(r'<div class=\\"pdp-proof\\">.*?</div>','<div class=\\"pdp-proof\\"><span><strong>Compare details</strong> Check retailer listing.</span></div>',s,flags=re.S)
 s=s.replace("esc(p.why)","esc(p.bestFor)")
 s=re.sub(r'<em>★ .*?</em>','<em>Compare details</em>',s)
 f.write_text(s)
print(json.dumps({"cleaned_pages":n}))
