from pathlib import Path
import subprocess,json,re,html
R=Path(__file__).resolve().parent.parent;P=R/'public/pirevo'
js='const fs=require("fs"),vm=require("vm"),w={};vm.runInNewContext(fs.readFileSync("public/pirevo/store-data.js","utf8"),{window:w});process.stdout.write(JSON.stringify(w.PIREVO_STORE))'
S=json.loads(subprocess.check_output(['node','-e',js],cwd=R,text=True))
category={
"kitchen":("Kitchen tools for weeknight meals","weeknight-kitchen-tools"),
"bags":("Work satchel comparison","work-satchel-comparison"),
"beauty":("Practical gift buying ideas","gifts-under-30"),
"gaming":("Home office and desk setup","home-office-desk-upgrades"),
"seasonal":("Useful gift buying ideas","gifts-under-30"),
"gifts":("Practical gifts by budget","gifts-under-30"),
"fall-home":("Cozy home upgrades","cozy-fall-home-upgrades"),
"home-organization":("Small apartment organization","small-apartment-organization"),
"tech":("Desk upgrades that reduce friction","home-office-desk-upgrades"),
"pets":("Pet cleanup buying advice","pet-cleanup-organization"),
"fitness":("Travel-friendly everyday essentials","carry-on-travel-essentials"),
"travel":("Carry-on travel essentials","carry-on-travel-essentials"),
"car":("Car organization and road trips","car-organization-road-trip"),
"kids":("Dorm-room and shared-space ideas","dorm-room-upgrades"),
"home-office":("Home-office desk upgrades","home-office-desk-upgrades"),
"cleaning":("Pet and home cleanup","pet-cleanup-organization"),
"coffee-bar":("Kitchen tools for everyday routines","weeknight-kitchen-tools"),
"tools-diy":("Small apartment and renter storage","small-apartment-organization"),
"sleep-bedroom":("Cozy home essentials","cozy-fall-home-upgrades"),
"outdoor-garden":("Useful home buying ideas","cozy-fall-home-upgrades")
}
count=0
def change(file,cat):
 global count
 s=file.read_text();s=re.sub(r'<aside class="pirevo-guide-linkout"[\s\S]*?</aside>','',s)
 title,slug=category.get(cat,("Explore useful buying guides",None))
 href="/pirevo/guides/"+slug+"/" if slug else "/pirevo/guides/"
 extra='<aside class="pirevo-guide-linkout" aria-label="Related buying guides" style="max-width:1120px;margin:28px auto 38px;padding:18px 22px;border:1px solid #d9e4d7;background:#f1f5eb;border-radius:13px;color:#254331"><strong>Before you order:</strong> <a href="'+href+'">'+html.escape(title)+' →</a> · <a href="/pirevo/guides/">All buying guides</a></aside>'
 if '</main>' not in s:raise RuntimeError('Missing main '+str(file))
 s=s.replace('</main>',extra+'</main>',1)
 file.write_text(s)
 count+=1
for product in S['products']:
 file=P/'products'/product['slug']/'index.html'
 if file.exists():change(file,product['collection'])
for c in S['collections']:
 file=P/'categories'/c['id']/'index.html'
 if file.exists():change(file,c['id'])
print(json.dumps({'product_and_category_related_guide_links_added':count},indent=2))
