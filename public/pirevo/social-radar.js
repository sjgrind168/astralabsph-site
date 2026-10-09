(()=>{
"use strict";
const grid=document.getElementById("socialRadarGrid"),
      status=document.getElementById("socialRadarStatus"),
      countLabel=document.getElementById("socialRadarCount"),
      search=document.getElementById("socialRadarSearch"),
      categorySelect=document.getElementById("socialRadarCategory"),
      sortSelect=document.getElementById("socialRadarSort"),
      more=document.getElementById("socialRadarMore");
if(!grid)return;
const library=window.PIREVO_STORE?.products||[];
const catalog=new Map(library.map(p=>[p.slug,p]));
let items=[],filter="all",searchTerm="",category="all",sort="featured",visible=16;
const BATCH=16;
const labelOf=id=>library.find(p=>p.collection===id)?.collection||id;
function el(tag,cls,text){const n=document.createElement(tag);if(cls)n.className=cls;if(text!=null)n.textContent=String(text);return n}
function link(href,title,external=false){
 const a=el("a",null,title);a.href=href;
 if(external){a.target="_blank";a.rel="noopener noreferrer"}
 return a;
}
function buildCategories(){
 const categories=[...new Set(items.filter(x=>x.status==="in_catalog").map(x=>x.category).filter(Boolean))].sort();
 for(const id of categories){
  const c=window.PIREVO_STORE?.collections?.find(x=>x.id===id);
  const option=el("option",null,c?.name||labelOf(id));option.value=id;
  categorySelect.append(option);
 }
}
function results(){
 const text=searchTerm.toLowerCase();
 const matches=items.filter(x=>{
  if(x.status!=="in_catalog")return false;
  if(filter!=="all"&&!x.platforms?.includes(filter))return false;
  if(category!=="all"&&x.category!==category)return false;
  const p=catalog.get(x.slug);
  if(!p||Number(x.rating)<4.5||!x.asin)return false;
  return !text||[x.name,x.signal,x.category,p.brand,p.fullName,p.collection].some(v=>String(v||"").toLowerCase().includes(text));
 });
 if(sort==="rating")matches.sort((a,b)=>b.rating-a.rating||b.reviews-a.reviews);
 else if(sort==="reviews")matches.sort((a,b)=>b.reviews-a.reviews||b.rating-a.rating);
 return matches;
}
function createCard(item){
 const p=catalog.get(item.slug);
 const card=el("article","social-radar-card");
 const media=link(item.product_url,"");media.className="social-radar-img";media.setAttribute("aria-label","View "+item.name);
 const img=el("img");img.src=p.image;img.loading="lazy";img.alt=p.fullName;img.referrerPolicy="no-referrer";media.append(img);
 const body=el("div","social-radar-copy"),tags=el("div","social-radar-tags");
 for(const platform of item.platforms)tags.append(el("span",null,platform));
 body.append(tags,el("h3",null,item.name));
 const rating=el("div","social-radar-rating");
 rating.append(el("strong",null,"★ "+Number(item.rating).toFixed(1)),document.createTextNode(" · "+Number(item.reviews).toLocaleString("en-US")+" Amazon reviews*"));
 body.append(rating,el("p",null,item.signal));
 const scope=item.scope==="product"?"Exact product/family source":item.scope==="brand/category"?"Brand/category evidence":item.scope==="category hypothesis"?"Content idea · category hypothesis":"Category-level evidence, not SKU sales";
 body.append(el("div","social-radar-scope",scope));
 const sources=el("div","social-radar-links");
 sources.append(link(item.product_url,"View PIREVO pick ↗"));
 if(item.sources?.[0]?.url)sources.append(link(item.sources[0].url,"Trend/source ↗",true));
 body.append(sources);card.append(media,body);
 return card;
}
function paint(){
 grid.replaceChildren();
 const matches=results();
 const shown=matches.slice(0,visible);
 const fragment=document.createDocumentFragment();
 for(const item of shown)fragment.append(createCard(item));
 if(!shown.length)fragment.append(el("p","social-radar-empty","No matches for this search or category. Try a different filter."));
 grid.append(fragment);
 if(countLabel)countLabel.textContent="Showing "+shown.length+" of "+matches.length+" matching rated products · "+items.filter(x=>x.status==="in_catalog").length+" total picks";
 if(more){more.hidden=shown.length>=matches.length;more.textContent="Show "+Math.min(BATCH,matches.length-shown.length)+" more researched products ↓";}
}
function reset(){visible=BATCH;paint()}
async function start(){
 try{
  const resp=await fetch("/pirevo/social-trend-research.json",{cache:"no-store"});
  if(!resp.ok)throw Error("Trend data unavailable");
  const data=await resp.json();
  items=Array.isArray(data.products)?data.products:[];
  buildCategories();
  const listed=items.filter(x=>x.status==="in_catalog").length;
  if(status)status.textContent=listed+" quality-screened catalog matches · Research updated "+data.reviewed_at+" · Amazon ratings reviewed Oct 9 (not live) · Sources linked per product.";
  paint();
 }catch{
  grid.replaceChildren();
  grid.append(el("p","social-radar-empty","Trend research is temporarily unavailable. Browse the rest of our PIREVO collections below."));
  if(countLabel)countLabel.textContent="Trend research temporarily unavailable";
 }
}
for(const b of document.querySelectorAll("[data-radar-filter]")){
 b.addEventListener("click",()=>{
  filter=b.dataset.radarFilter;
  document.querySelectorAll("[data-radar-filter]").forEach(x=>x.setAttribute("aria-pressed",String(x===b)));
  reset();
 });
}
search?.addEventListener("input",()=>{searchTerm=search.value.trim();reset()});
categorySelect?.addEventListener("change",()=>{category=categorySelect.value;reset()});
sortSelect?.addEventListener("change",()=>{sort=sortSelect.value;reset()});
more?.addEventListener("click",()=>{visible+=BATCH;paint()});
start();
})();