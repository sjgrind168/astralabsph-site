(()=>{
"use strict";
const grid=document.getElementById("socialRadarGrid"),status=document.getElementById("socialRadarStatus");
if(!grid)return;
const library=window.PIREVO_STORE?.products||[];
let items=[],filter="all";
function el(tag,classname,txt){const n=document.createElement(tag);if(classname)n.className=classname;if(txt!=null)n.textContent=String(txt);return n}
function anchor(href,text,external=false){const n=el("a",null,text);n.href=href;if(external){n.target="_blank";n.rel="noopener noreferrer"}return n}
function paint(){
 grid.replaceChildren();
 const list=items.filter(x=>x.status==="in_catalog"&&(filter==="all"||x.platforms.includes(filter)));
 if(!list.length){grid.append(el("p","social-radar-empty","No source-backed catalog matches in this channel yet."));return}
 for(const item of list){
  const product=library.find(p=>p.slug===item.slug);
  if(!product)continue;
  const card=el("article","social-radar-card");
  const media=anchor(item.product_url,"");media.className="social-radar-img";media.setAttribute("aria-label","View "+item.name);
  const img=el("img");img.src=product.image;img.loading="lazy";img.alt=product.fullName;img.referrerPolicy="no-referrer";media.append(img);
  const body=el("div","social-radar-copy");
  const tags=el("div","social-radar-tags");
  for(const platform of item.platforms)tags.append(el("span",null,platform));
  body.append(tags,el("h3",null,item.name));
  const rating=el("div","social-radar-rating");rating.append(el("strong",null,"★ "+Number(item.rating).toFixed(1)),document.createTextNode(" · "+Number(item.reviews).toLocaleString("en-US")+" Amazon ratings*"));
  body.append(rating,el("p",null,item.signal),el("div","social-radar-scope",item.scope==="product"?"Exact-product trend evidence":"Brand/category-level trend evidence"));
  const links=el("div","social-radar-links");
  links.append(anchor(item.product_url,"View PIREVO pick ↗"));
  const source=item.sources?.[0];if(source)links.append(anchor(source.url,"Why this trend? ↗",true));
  body.append(links);card.append(media,body);grid.append(card);
 }
}
async function start(){
 try{
  const r=await fetch("/pirevo/social-trend-research.json",{cache:"no-store"});if(!r.ok)throw Error("Unavailable");
  const data=await r.json();items=data.products||[];
  status.textContent="Editorial review "+data.reviewed_at+" · ★ ratings from Oct 9 catalog snapshots, not live Amazon data. Trend sources linked per item.";
  paint();
 }catch{grid.replaceChildren();grid.append(el("p","social-radar-empty","Trend research is temporarily unavailable. Browse our Trend 50 products below."))}
}
for(const b of document.querySelectorAll("[data-radar-filter]"))b.addEventListener("click",()=>{filter=b.dataset.radarFilter;document.querySelectorAll("[data-radar-filter]").forEach(a=>a.setAttribute("aria-pressed",String(a===b)));paint()});
start();
})();