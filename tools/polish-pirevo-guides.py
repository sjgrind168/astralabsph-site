from pathlib import Path
r=Path(__file__).resolve().parent.parent
g=r/'public/pirevo/guides'
ico='<link rel="icon" type="image/svg+xml" href="/pirevo/favicon.svg">'
for p in list(g.glob('*/index.html'))+[g/'index.html']:
 s=p.read_text()
 if ico not in s:s=s.replace('</head>',ico+'</head>',1)
 p.write_text(s)
f=g/'index.html'
s=f.read_text()
if '/pirevo/guides/work-satchel-comparison/' not in s:
 card='<article><h2><a href="/pirevo/guides/work-satchel-comparison/">Compare work satchels: LOVEVOOK, Wrangler, Angel Kiss</a></h2><p>A closer comparison of capacity, dimensions and daily carry styles.</p></article>'
 s=s.replace('</div><p>As an Amazon Associate',card+'</div><p>As an Amazon Associate',1)
f.write_text(s)
p=r/'public/pirevo/catalog/index.html'
p.write_text(p.read_text().replace('All ten guides →','All eleven guides →'))
print('All 11 guides linked and icon ready')
