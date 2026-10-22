#!/usr/bin/env python3
"""Ensure 50-pick expansion uses only published canonical pages, not fabricated inventory."""
from pathlib import Path
import json,re,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parent.parent;P=R/'public/pirevo'
ledger=json.loads((R/'marketing/pirevo/CATEGORY_50_BACKLOG_20261022.json').read_text())
assert ledger['goal_total_placements']==1000
assert ledger['current_published_category_placements']==ledger['published_products']
assert ledger['missing_published_placements']==sum(x['gap'] for x in ledger['categories'])
assert len(ledger['categories'])==20
assert ledger['new_researched_products_published_in_first_batch']==4
assert len({x['asin'] for x in ledger['non_published_research_candidates']})==len(ledger['non_published_research_candidates'])
current=0
for cat in ledger['categories']:
 f=P/'categories'/cat['id']/'index.html'
 s=f.read_text()
 assert s.count('class="pv-category-tools"')==1,(f,'browse controls')
 assert s.count('src="/pirevo/category-browse.js"')==1,f
 assert 'not a live Amazon bestseller ranking' in s,f
 assert re.search('(?s)class="pv-category-tools".{0,1200}<div class="grid">',s),f
 n=len(re.findall(r'<a class="card"',s))
 assert n==cat['published'],(f,n,cat['published'])
 assert cat['goal']==50 and cat['gap']==50-cat['published']
 current+=n
assert current==ledger['published_products']
js=(P/'category-browse.js').read_text()
assert 'limit=12' in js and 'history.replaceState' in js and 'more.addEventListener' in js
html=(P/'index.html').read_text()
assert html.index('id="categories"')<html.index('id="creator-picks"')<html.index('id="trending"')
assert html.count('class="pv-owned-card')==4
for item in ledger['non_published_research_candidates']:
 assert not (P/'products'/item['candidate'].lower().replace(" ","-")/'index.html').exists()
print(json.dumps({'status':'PASS','published':current,'target':1000,'remaining':ledger['missing_published_placements'],'staged_researched_candidates':len(ledger['non_published_research_candidates']),'category_search_and_load_more':20,'books_apps_position':'immediately after categories'},indent=2))
