from pathlib import Path
from collections import defaultdict
from urllib.parse import urlencode
import csv,json,subprocess,re
root=Path(__file__).resolve().parents[2]
m=root/'marketing/pirevo'
js="const fs=require('fs'),vm=require('vm'),w={};vm.runInNewContext(fs.readFileSync('public/pirevo/store-data.js','utf8'),{window:w});process.stdout.write(JSON.stringify(w.PIREVO_STORE))"
store=json.loads(subprocess.check_output(['node','-e',js],cwd=root,text=True))
live=json.loads((m/'PIREVO_LIVE_PIN_RECONCILIATION_20261022.json').read_text())
matched=defaultdict(list)
for pin in live:
 if pin.get('slug'): matched[pin['slug']].append(pin)
categories={c['id']:c['name'] for c in store['collections']}
boards={'kitchen':'1143844074049638244','coffee-bar':'1143844074049638244','home-organization':'1143844074049638244','cleaning':'1143844074049638244','beauty':'1143844074049638237','bags':'1143844074049638231'}
angles={'beauty':'Beauty Routine Reset','kitchen':'Weeknight Kitchen Ideas','coffee-bar':'A Calmer Coffee Corner','home-organization':'The Small Space Reset','sleep-bedroom':'Softer Bedroom Setup','tools-diy':'Practical Weekend Projects','bags':'Thoughtful Everyday Carry','tech':'Everyday Tech Ideas','travel':'Pack Smarter Next Trip','cleaning':'The Fresh Home Edit','fitness':'Home Fitness Essentials','gaming':'Gaming Room Refresh'}
priority=['clean-skin-club','medicube','mighty-patch','airtag','earth-rated','owala','bedsure','vtopmart','aeropress','govee','levoit','black-decker']
rows=[]
for p in store['products']:
 slug=p['slug'];category=p['collection'];old=matched.get(slug,[])
 angle=angles.get(category,categories[category]+' Inspiration')
 purpose=re.sub(r'\s+',' ',p.get('bestFor','')).strip()[:145]
 caveat=re.sub(r'\s+',' ',p.get('caveat','')).strip()[:95]
 title=(p['shortName']+' | '+angle)[:100]
 description=(purpose+' Check: '+caveat+' See exact product details and variant on PIREVO before shopping at Amazon. Illustrative lifestyle creative; appearance may differ. As an Amazon Associate, PIREVO earns from qualifying purchases.')[:800]
 dest='https://www.astralabsph.com/pirevo/products/'+slug+'/index.html?'+urlencode({'utm_source':'pinterest','utm_medium':'organic','utm_campaign':'pirevo_direct_pins_20261022','utm_content':slug+'_01'})
 scene=('One original full-bleed ultra realistic 2:3 photographic lifestyle scene illustrating '+angle+' and the use case: '+purpose+'. Large legible 3-7 word editorial headline, subtle PIREVO signature, natural materials, photographic lighting, no fake branded product, no sales or star claims, no frames, no cards, no Amazon logos. Add small illustrative-scene disclosure.')
 rows.append({'slug':slug,'category':categories[category],'category_id':category,'brand':p['brand'],'name':p['shortName'],'asin_us':p['asin'],'pirevo_url':'https://www.astralabsph.com/pirevo/products/'+slug+'/index.html','amazon_url':'https://www.amazon.com/dp/'+p['asin']+'?tag=pirevo-20','product_site_status':'LIVE','bestseller_status':'NOT_INDEPENDENTLY_VERIFIED_FOR_EXACT_ASIN','research_note':purpose,'buying_caveat':caveat,'pin_priority':'P1' if any(x in slug for x in priority) else 'P2','pin_board_id':boards.get(category,'1143844074049522281'),'pin_title':title,'pin_description':description,'pin_alt_text':'Illustrative lifestyle scene for '+p['shortName']+'. Check actual model at the linked PIREVO research page.','pin_destination':dest,'portrait_visual_prompt':scene,'creative_asset_path':'','creative_rights':'GENERATED_OR_LICENSED_REQUIRED','visual_qa':'NOT_REVIEWED','new_pin_status':'NOT_PUBLISHED','new_pin_id':'','new_pin_url':'','old_live_pin_count':len(old),'old_live_pin_urls':' | '.join(x['url'] for x in old),'old_pin_quality':'REVIEW_REQUIRED' if old else 'NO_MATCHED_PIN','notes':'No scheduler; publish direct only after image-level visual QA'})
# Preserve all completed image reviews and verified posts on repeat executions.
previous_path=m/'PIREVO_PRODUCT_PIN_MASTER_20261022.csv'
previous={}
if previous_path.exists():
 with previous_path.open(encoding='utf-8-sig',newline='') as f:
  previous={r['slug']:r for r in csv.DictReader(f)}
for row in rows:
 old=previous.get(row['slug'],{})
 for field in ('creative_asset_path','creative_rights','visual_qa','new_pin_status','new_pin_id','new_pin_url','pin_destination'):
  value=old.get(field,'')
  if value and (field!='new_pin_status' or value=='PUBLISHED'):
   row[field]=value
 if row['new_pin_status']=='PUBLISHED':
  assert row['new_pin_id'].isdigit() and row['new_pin_url'].startswith('https://www.pinterest.com/pin/'),row['slug']

assert len(rows)==142 and len({r['slug'] for r in rows})==142
rows.sort(key=lambda x:(x['pin_priority'],x['old_live_pin_count']>0,x['category_id'],x['slug']))
with (m/'PIREVO_PRODUCT_PIN_MASTER_20261022.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n");w.writeheader();w.writerows(rows)
roundups=[]
for c in store['collections']:
 count=sum(p['collection']==c['id'] for p in store['products'])
 roundups.append({'category':c['name'],'published':count,'target':50,'category_url':'https://www.astralabsph.com/pirevo/categories/'+c['id']+'/','creative':'One unique full-bleed photorealistic editorial thematic Pin','pin_status':'CONCEPT_ONLY','claim_50_allowed':count>=50})
with (m/'PIREVO_CATEGORY_ROUNDUP_PLAN_20261022.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(roundups[0]),lineterminator="\n");w.writeheader();w.writerows(roundups)
status={'as_of':'2026-10-22','execution_mode':'DIRECT_ACTIVE_SESSION_ONLY_NO_SCHEDULES','catalog_products':len(rows),'product_pin_metadata_prepared':len(rows),'category_roundup_concepts':len(roundups),'main_board_live_pins_reconciled':len(live),'existing_matched_live_product_pin_instances':sum(r['old_live_pin_count'] for r in rows),'unique_products_with_existing_live_pins':sum(bool(r['old_live_pin_count']) for r in rows),'unique_products_without_matched_live_pins':sum(not r['old_live_pin_count'] for r in rows),'new_pins_published_now':sum(x['new_pin_status']=='PUBLISHED' for x in rows),'new_creative_approved_now':sum('OWNER_APPROVED' in x['visual_qa'] for x in rows),'first_unpinned_priority':[r['slug'] for r in rows if not r['old_live_pin_count']][:12]}
status_path=m/'PIREVO_DIRECT_EXECUTION_STATUS_20261022.json'
if status_path.exists():
 prior=json.loads(status_path.read_text())
 for optional in ('generated_canva_media_pending_QA','rejected_image_attempt','draft_canva_asset','rejected_generated_collage','pinterest_create_permission','first_photo_pin_batch','verified_published_pin_urls','profile_live_after_publication','boards_live_after_publication'):
  if optional in prior:status[optional]=prior[optional]
status_path.write_text(json.dumps(status,indent=2)+'\n')
print(json.dumps(status,indent=2))
