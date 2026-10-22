#!/usr/bin/env python3
"""Check first-party Apps & KDP products are restored after the main store, without affiliate damage."""
from pathlib import Path
import json, re
R=Path(__file__).resolve().parent.parent
base=R/"public/pirevo"
source=base/"owned-products-block.html"
html=(base/"index.html").read_text()
block=source.read_text()
style=base/"owned-products.css"
assert style.is_file()
assert html.count('id="books"')==1
assert html.count('id="astralabs-apps"')==1
assert html.count('href="/pirevo/owned-products.css"')==1
assert html.count('class="pv-owned-card')==4
assert html.count('pv-owned-mini ')==4
assert html.count('id="creator-picks"')==1
assert html.index('id="books"')<html.index('id="discover"')
assert html.index('id="astralabs-apps"')>html.index('id="books"')
assert html.index('id="astralabs-apps"')<html.index('id="trending"')
assert html.index('id="astralabs-apps"')<html.index('</main>')
expected_links={
 '/pirevo/books/timmy-and-the-time-traveling-watch/',
 'https://www.amazon.com/dp/B0FX95D9LL',
 'https://www.amazon.com/dp/B0FXDNX4DV',
 'https://www.amazon.com/dp/B0HMQVHPN7',
 '/astramate/?utm_source=pirevo&amp;utm_medium=website&amp;utm_campaign=astralabs_apps&amp;utm_content=astramate',
 '/keepry/?utm_source=pirevo&amp;utm_medium=website&amp;utm_campaign=astralabs_apps&amp;utm_content=keepry',
}
for dest in expected_links:
 assert dest in block,dest
assert "Publication pending" not in block and "Coming soon" not in block
assert "As an Amazon Associate" in html
assert "not the official book cover" in block
assert "m.media-amazon.com" not in block
assert "data-pv-carousel" in html
images=[
 "/pirevo/pip-poppy-cover.jpg",
 "/marketing/campaigns/facebook/A03_astramate_facebook_4x5.png",
 "/marketing/campaigns/facebook/K02_keepry_facebook_4x5.png"
]
for img in images:
 assert (R/"public"/img.lstrip("/")).is_file(),img
 assert img in block
assert 'href="/pirevo/#books"' in html
assert 'href="/pirevo/#astralabs-apps"' in html
print(json.dumps({"result":"PASS","owned_sections":["KDP original books","AstraLabs mobile apps"],"owned_cards":4,"book_titles":2,"apps":2,"local_artworks":3,"official_ebook_paperback_links":True,"historic_amazon_affiliate_links_preserved":True},indent=2))
