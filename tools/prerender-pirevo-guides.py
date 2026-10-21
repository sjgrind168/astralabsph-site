from pathlib import Path
import subprocess,json,re,html
R=Path.cwd();P=R/'public/pirevo'
def read(name,key):
 j='const fs=require("fs"),vm=require("vm"),w={};vm.runInNewContext(fs.readFileSync("public/pirevo/'+name+'","utf8"),{window:w});process.stdout.write(JSON.stringify(w.'+key+'))'
 return json.loads(subprocess.check_output(['node','-e',j],text=True))
G=read('content.js','PIREVO_GUIDES')
H=lambda x:html.escape(str(x or ''),quote=True)
CSS='<style>.guide-pre{max-width:1060px;margin:auto;padding:22px 16px 70px;line-height:1.75}.guide-pre h1{font-size:clamp(32px,5vw,58px);line-height:1.09;letter-spacing:-.04em}.guide-pre h2{font-size:28px;margin-top:35px}.guide-pre .tiles{display:grid;grid-template-columns:1fr 1fr;gap:17px}.guide-pre article{background:#fff;border:1px solid #dbe3d9;border-radius:15px;padding:20px}.guide-pre .note{background:#e6efdf;padding:18px;border-radius:13px}.guide-pre p{color:#475a4a}@media(max-width:700px){.guide-pre .tiles{grid-template-columns:1fr}}</style>'
for slug,g in G.items():
 f=P/'guides'/slug/'index.html';s=f.read_text()
 if 'data-prerendered="yes"' in s:
  s=re.sub(r'<main id="article" data-prerendered="yes"[\s\S]*?</main>','<main id="article" class="article"><p>Loading guide…</p></main>',s,count=1)
  s=re.sub(r'<script type="application/ld\+json" data-pirevo-source>[\s\S]*?</script>','',s)
  s=s.replace(CSS,'')
 expect='<main id="article" class="article"><p>Loading guide…</p></main>'
 assert expect in s,slug
 intro=''.join('<p>'+H(t)+'</p>' for t in g['intro'])
 cards=''.join('<article><h3>'+H(t['name'])+'</h3><p><b>Why consider:</b> '+H(t['why'])+'</p><p><b>Check before buying:</b> '+H(t['lookFor'])+'</p></article>' for t in g['picks'])
 sections=''.join('<section><h2>'+H(t['heading'])+'</h2>'+''.join('<p>'+H(x)+'</p>' for x in t['paragraphs'])+'</section>' for t in g['sections'])
 check='<ul>'+''.join('<li>'+H(x)+'</li>' for x in g['checklist'])+'</ul>'
 main='<main id="article" data-prerendered="yes" class="article guide-pre"><nav><a href="/pirevo/">PIREVO</a> / <a href="/pirevo/guides/">Buying guides</a></nav><h1>'+H(g['title'])+'</h1><p>'+H(g['dek'])+'</p><p>Updated '+H(g['updated'])+' · Independent editorial research, not first-hand product testing.</p><div class="note"><strong>Affiliate disclosure:</strong> As an Amazon Associate I earn from qualifying purchases. Prices, shipping and product identity must be checked at Amazon.</div>'+intro+'<h2>'+H(g.get('listHeading','What to compare'))+'</h2><div class="tiles">'+cards+'</div>'+sections+'<h2>Before you buy</h2>'+check+'<p><a href="/pirevo/catalog/">See researched product pages</a> · <a href="/pirevo/international/">International shopping guide</a></p></main>'
 s=s.replace(expect,main)
 schema={"@context":"https://schema.org","@type":"Article","headline":g['title'],"description":g['dek'],"dateModified":g['updated'],"mainEntityOfPage":"https://www.astralabsph.com/pirevo/guides/"+slug+"/","author":{"@type":"Organization","name":"PIREVO"}}
 ld='<script type="application/ld+json" data-pirevo-source>'+json.dumps(schema)+'</script>'
 if ld not in s:s=s.replace('</head>',CSS+ld+'</head>',1)
 f.write_text(s)
cards=''.join('<article><h2><a href="/pirevo/guides/'+slug+'/">'+H(g['title'])+'</a></h2><p>'+H(g['dek'])+'</p></article>' for slug,g in G.items())
directory='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Product Buying Guides and Comparisons | PIREVO</title><meta name="description" content="Practical PIREVO buying guides for kitchen, home organization, travel, desks, gifts and more."><link rel="canonical" href="https://www.astralabsph.com/pirevo/guides/">'+CSS+'</head><body style="background:#f6f6f0;font-family:system-ui"><main class="guide-pre"><p><a href="/pirevo/">PIREVO</a> / Buying guides</p><h1>Useful buying guides and comparisons</h1><p>Compare product categories by actual fit, buying constraints and tradeoffs, without invented ratings or live prices.</p><div class="tiles">'+cards+'</div><p>As an Amazon Associate I earn from qualifying purchases. <a href="/pirevo/affiliate-disclosure.html">Affiliate disclosure</a> · <a href="/pirevo/catalog/">All products</a></p></main></body></html>'
(P/'guides/index.html').write_text(directory)
f=P/'catalog/index.html';s=f.read_text();s=re.sub(r'<section class="pirevo-guides-discovery"[\s\S]*?</section>','',s)
links=''.join('<a href="/pirevo/guides/'+slug+'/">'+H(g['title'])+'</a> ' for slug,g in list(G.items())[:4])
s=s.replace('</main>','<section class="pirevo-guides-discovery" style="background:#e7efe7;border-radius:16px;padding:22px;margin:22px 0"><h2>Browse buying guides</h2><p>Product decisions, category comparisons and useful checklists.</p><nav style="display:flex;gap:13px;flex-wrap:wrap">'+links+'</nav><p><a href="/pirevo/guides/">All ten guides →</a></p></section></main>',1)
f.write_text(s)
for loc in ['public/sitemap.xml','public/pirevo/sitemap.xml']:
 f=R/loc;s=f.read_text();url='https://www.astralabsph.com/pirevo/guides/'
 if '<loc>'+url+'</loc>' not in s:s=s.replace('</urlset>','<url><loc>'+url+'</loc><lastmod>2026-10-22</lastmod></url></urlset>')
 f.write_text(s)
print(json.dumps({"guides_prerendered":len(G),"directory":"/pirevo/guides/","word_lengths":{x:len(re.sub('<[^>]*>',' ',(P/'guides'/x/'index.html').read_text()).split()) for x in G}},indent=2))
