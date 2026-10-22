#!/usr/bin/env python3
"""Inject expandable, locally searchable category grids. Read-only browsing of real published products."""
from pathlib import Path
import re,json,subprocess
R=Path(__file__).resolve().parent.parent
P=R/"public/pirevo"
s='const fs=require("fs"),vm=require("vm"),w={};vm.runInNewContext(fs.readFileSync("public/pirevo/store-data.js","utf8"),{window:w});console.log(JSON.stringify(w.PIREVO_STORE))'
catalog=json.loads(subprocess.check_output(["node","-e",s],cwd=R,text=True))
updated=0
for c in catalog["collections"]:
 path=P/"categories"/c["id"]/"index.html"
 if not path.is_file():raise ValueError("Missing "+str(path))
 html=path.read_text()
 html=re.sub(r'<section class="pv-category-tools"[\s\S]*?</section>','',html)
 js='<script src="/pirevo/category-browse.js" defer></script>'
 html=html.replace(js,'')
 # Keep product-list controls as close as possible to the cards.
 widget='''<section class="pv-category-tools" aria-label="Browse category products">
<div class="pv-category-search-row"><input type="search" maxlength="95" placeholder="Search within these researched products…" aria-label="Search products in this category"><button type="button" data-clear>Clear</button></div>
<div class="pv-category-meta"><span data-count role="status" aria-live="polite"></span><button type="button" data-more hidden>Show more products ↓</button></div>
<p class="pv-category-disclaimer">Showing published editorial research, not a live Amazon bestseller ranking. Listings, stock and offers can change.</p>
</section>'''
 match=re.search(r'<div class="grid">',html)
 if not match:raise ValueError("Missing category grid "+c["id"])
 html=html[:match.start()]+widget+html[match.start():]
 html=html.replace('</body>',js+'</body>',1)
 path.write_text(html)
 updated+=1
print(json.dumps({"categories_upgraded":updated,"search":"only published items","initial_cards_per_category":12,"load_more_batch":12,"target_capacity":"50 and beyond"}))
