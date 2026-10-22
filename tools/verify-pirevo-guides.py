from pathlib import Path
from html.parser import HTMLParser
import re,sys,json,xml.etree.ElementTree as ET
p=Path('public/pirevo');guides=list((p/'guides').glob('*/index.html'));assert len(guides)==11,len(guides)
pre=[x for x in guides if 'data-prerendered="yes"' in x.read_text()];assert len(pre)==10
words={}
for f in pre:
 s=f.read_text();t=re.sub('<[^>]+>',' ',s);words[f.parent.name]=len(t.split());assert words[f.parent.name]>=450,(f,words[f.parent.name]);assert 'Loading guide…' not in s
 assert s.count('data-pirevo-source')==1 and 'application/ld+json' in s
 assert 'As an Amazon Associate I earn from qualifying purchases' in s
 assert 'rel="canonical"' in s
 assert s.count('<h1')==1
satchel=(p/'guides/work-satchel-comparison/index.html').read_text();assert 'Review count snapshot' not in satchel and 'class="rating"' not in satchel
catalog=(p/'catalog/index.html').read_text();assert '/pirevo/guides/' in catalog
links=sum('class="pirevo-guide-linkout"' in x.read_text() for x in (p/'products').glob('*/index.html'))+sum('class="pirevo-guide-linkout"' in x.read_text() for x in (p/'categories').glob('*/index.html'))
assert links>=158,links
for f in [Path('public/sitemap.xml'),p/'sitemap.xml']:
 urls=[e.text for e in ET.parse(f).getroot().iter() if e.tag.endswith('loc')];assert len(urls)==len(set(urls));assert 'https://www.astralabsph.com/pirevo/guides/' in urls
print(json.dumps({'status':'PASS','guide_pages':len(guides),'pre_rendered_guides':len(pre),'prerendered_words':words,'crawlable_related_guide_links':links},indent=2))
