(()=>{
const S=window.PIREVO_STORE||{collections:[],products:[]};
const $=(s,r=document)=>r.querySelector(s);
const $$=(s,r=document)=>[...r.querySelectorAll(s)];
const esc=s=>String(s??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]));
function qs(){const p=new URLSearchParams(location.search);const keep=new URLSearchParams();["utm_source","utm_medium","utm_campaign","utm_content"].forEach(k=>{if(p.get(k))keep.set(k,p.get(k))});return keep.toString()}
function productUrl(p){const base="/pirevo/products/"+p.slug+"/index.html";const q=qs();return q?base+"?"+q:base}
function compact(n){return n>=100000?(n/1000).toFixed(n>=100000?0:1)+"k":n>=1000?(n/1000).toFixed(n>=10000?0:1)+"k":String(n)}
function card(p){return `<article class="shop-product-card" data-collection="${esc(p.collection)}" data-search="${esc((p.fullName+" "+p.brand+" "+p.bestFor).toLowerCase())}">
<a class="shop-product-media" href="${productUrl(p)}" aria-label="View ${esc(p.fullName)}">
<span class="shop-badge">${esc(p.badge)}</span><img src="${esc(p.image)}" alt="${esc(p.fullName)}" loading="lazy" referrerpolicy="no-referrer">
</a>
<div class="shop-product-copy"><div class="shop-brand">${esc(p.brand)}</div><h3><a href="${productUrl(p)}">${esc(p.shortName)}</a></h3>
<div class="shop-rating"><strong>★ ${p.rating.toFixed(1)}</strong><span>${compact(p.reviews)} ratings</span></div>
<p>${esc(p.why)}</p><div class="shop-card-actions"><a class="shop-view" href="${productUrl(p)}">View product</a><span>Check price on Amazon</span></div></div></article>`}
function renderShelf(id,items){const root=$("#shelf-"+id);if(root)root.innerHTML=items.map(card).join("")}
function render(){S.collections.forEach(c=>renderShelf(c.id,S.products.filter(p=>p.collection===c.id)));}
function setupSearch(){const input=$("#shopSearch"),clear=$("#clearSearch");if(!input)return;const cards=()=>$$(".shop-product-card");const apply=()=>{const q=input.value.trim().toLowerCase();cards().forEach(c=>c.hidden=!!q&&!c.dataset.search.includes(q));$("#searchStatus").textContent=q?`Showing matches for “${input.value.trim()}”`:"";};input.addEventListener("input",apply);clear?.addEventListener("click",()=>{input.value="";apply();input.focus()})}
function setupChips(){ $$(".shop-filter-chip").forEach(b=>b.addEventListener("click",()=>{const id=b.dataset.target;if(id==="all"){scrollTo({top:$("#shop").offsetTop-80,behavior:"smooth"});return;}document.getElementById(id)?.scrollIntoView({behavior:"smooth",block:"start"})}))}
function initGA(){const C=window.PIREVO_CONFIG||{};if(!C.ga4Id)return;const s=document.createElement("script");s.async=true;s.src="https://www.googletagmanager.com/gtag/js?id="+encodeURIComponent(C.ga4Id);document.head.appendChild(s);window.dataLayer=window.dataLayer||[];window.gtag=function(){dataLayer.push(arguments)};gtag("js",new Date());gtag("config",C.ga4Id,{anonymize_ip:true})}
render();setupSearch();setupChips();initGA();$$("[data-year]").forEach(x=>x.textContent=new Date().getFullYear());
})();