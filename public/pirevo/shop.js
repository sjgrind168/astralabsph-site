(()=>{
const S=window.PIREVO_STORE||{collections:[],products:[]};
const $=(s,r=document)=>r.querySelector(s);
const $$=(s,r=document)=>[...r.querySelectorAll(s)];
const esc=s=>String(s??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]));
const compact=n=>n>=100000?(n/1000).toFixed(0)+"k":n>=10000?(n/1000).toFixed(0)+"k":n>=1000?(n/1000).toFixed(1)+"k":String(n||0);
function qs(){const p=new URLSearchParams(location.search),k=new URLSearchParams();["utm_source","utm_medium","utm_campaign","utm_content"].forEach(x=>{if(p.get(x))k.set(x,p.get(x))});return k.toString()}
function productUrl(p){const b="/pirevo/products/"+p.slug+"/index.html",q=qs();return q?b+"?"+q:b}
function giftGroup(p){return p.holidayGroup||p.holidayGiftGroup||""}
function card(p){
  const group=p.seasonalGroup||giftGroup(p);
  return `<article class="shop-product-card" data-collection="${esc(p.collection)}" data-seasonal-group="${esc(p.seasonalGroup||"")}" data-holiday-group="${esc(giftGroup(p))}" data-search="${esc((p.fullName+" "+p.shortName+" "+p.brand+" "+p.bestFor+" "+(p.trend||"")+" "+group).toLowerCase())}">
  <a class="shop-product-media" href="${productUrl(p)}" aria-label="View ${esc(p.fullName)}"><span class="shop-badge">${esc(p.badge)}</span><img src="${esc(p.image)}" alt="${esc(p.fullName)}" loading="lazy" referrerpolicy="no-referrer"></a>
  <div class="shop-product-copy"><div class="shop-brand">${esc(p.brand)}</div><h3><a href="${productUrl(p)}">${esc(p.shortName)}</a></h3>
  <div class="shop-rating"><strong>★ ${Number(p.rating||0).toFixed(1)}</strong><span>${compact(p.reviews)} ratings</span></div>
  <p>${esc(p.why)}</p><div class="shop-card-actions"><a class="shop-view" href="${productUrl(p)}">View product</a><span>Check price on Amazon</span></div></div></article>`}
function renderShelf(id,items){const root=$("#shelf-"+id);if(root)root.innerHTML=items.map(card).join("")}
function ensureDynamicCollections(){
  const root=$("#dynamicCollections"); if(!root)return;
  S.collections.forEach(c=>{
    if(c.id==="seasonal"||document.getElementById("shelf-"+c.id))return;
    root.insertAdjacentHTML("beforeend",`<section class="shop-section" id="${esc(c.id)}"><div class="shop-wrap"><div class="shop-section-head"><div><span>${esc(c.kicker||"PIREVO EDIT")}</span><h2>${esc(c.name)}</h2></div><p>${esc(c.description||"Research-backed product picks.")}</p></div><div class="shop-collection-signal">${esc(c.signal||"Current demand + review confidence + search intent")}</div><div class="shop-grid" id="shelf-${esc(c.id)}"></div></div></section>`);
  });
  const filters=$(".shop-filter-row");
  if(filters)S.collections.forEach(c=>{if(c.id!=="seasonal"&&!filters.querySelector('[data-target="'+c.id+'"]'))filters.insertAdjacentHTML("beforeend",`<button class="shop-filter-chip" data-target="${esc(c.id)}">${esc(c.name)}</button>`)});
}
function renderTop50(){
  const root=$("#top50Grid"); if(!root)return;
  const order=["home-organization","kitchen","beauty","tech","gaming","pets","fitness","travel","car","kids"];
  const picks=S.products.filter(p=>String(p.badge||"").includes("TOP 50")).sort((a,b)=>{const ao=order.indexOf(a.collection),bo=order.indexOf(b.collection);return ao!==bo?ao-bo:(b.reviews||0)-(a.reviews||0)});
  root.innerHTML=picks.map((p,i)=>`<a class="top50-item" href="${productUrl(p)}"><span class="top50-rank">${i+1}</span><span class="top50-copy"><small>${esc((S.collections.find(c=>c.id===p.collection)||{}).name||p.collection)}</small><strong>${esc(p.shortName)}</strong><em>★ ${Number(p.rating).toFixed(1)} · ${compact(p.reviews)} ratings</em></span><span class="top50-arrow">→</span></a>`).join("");
}
function render(){
  ensureDynamicCollections();
  S.collections.forEach(c=>{
    if(c.id==="seasonal"){
      const halloween=S.products.filter(p=>p.collection==="seasonal"&&p.season==="halloween").sort((a,b)=>(b.reviews||0)-(a.reviews||0));
      const christmas=S.products.filter(p=>p.season==="christmas"||p.holidayGiftGroup)
        .sort((a,b)=>{const order={decor:0,kids:1,adults:2};const ag=giftGroup(a),bg=giftGroup(b);return (order[ag]??9)!==(order[bg]??9)?(order[ag]??9)-(order[bg]??9):(b.reviews||0)-(a.reviews||0)});
      renderShelf("seasonal",halloween); renderShelf("christmas",christmas);
    } else renderShelf(c.id,S.products.filter(p=>p.collection===c.id));
  });
  renderTop50();
}
let activeHalloweenGroup="all",activeChristmasGroup="all";
function applyCardVisibility(){
  const input=$("#shopSearch"),q=(input?.value||"").trim().toLowerCase();
  $$(".shop-product-card").forEach(c=>{
    const searchMiss=!!q&&!String(c.dataset.search||"").includes(q);
    const h=c.closest("#shelf-seasonal"),x=c.closest("#shelf-christmas");
    const hMiss=!!h&&activeHalloweenGroup!=="all"&&c.dataset.seasonalGroup!==activeHalloweenGroup;
    const xMiss=!!x&&activeChristmasGroup!=="all"&&c.dataset.holidayGroup!==activeChristmasGroup;
    c.hidden=searchMiss||hMiss||xMiss;
  });
  const ss=$("#searchStatus"); if(ss)ss.textContent=q?`Showing matches for “${input.value.trim()}”`:"";
  const hs=$("#halloweenFilterStatus"); if(hs)hs.textContent=activeHalloweenGroup==="all"?"Showing all Halloween picks.":`Showing ${$$('#shelf-seasonal .shop-product-card:not([hidden])').length} Halloween picks in this style.`;
  const cs=$("#christmasFilterStatus"); if(cs)cs.textContent=activeChristmasGroup==="all"?`Showing all ${$$('#shelf-christmas .shop-product-card:not([hidden])').length} Christmas picks.`:`Showing ${$$('#shelf-christmas .shop-product-card:not([hidden])').length} Christmas picks in this group.`;
}
function setupSearch(){
  const input=$("#shopSearch"),clear=$("#clearSearch"); if(!input)return;
  input.addEventListener("input",applyCardVisibility);
  clear?.addEventListener("click",()=>{input.value="";applyCardVisibility();input.focus()});
}
function setupChips(){
  $$(".shop-filter-chip").forEach(b=>b.addEventListener("click",()=>{
    const id=b.dataset.target;
    if(id==="all"){window.scrollTo({top:$("#shop").offsetTop-80,behavior:"smooth"});return}
    document.getElementById(id)?.scrollIntoView({behavior:"smooth",block:"start"});
  }));
}
function setupSeasonalFilters(){
  $$("[data-halloween-group]").forEach(b=>b.addEventListener("click",()=>{
    activeHalloweenGroup=b.dataset.halloweenGroup||"all";
    $$("[data-halloween-group]").forEach(x=>x.classList.toggle("active",x===b));applyCardVisibility();
  }));
  $$("[data-christmas-group]").forEach(b=>b.addEventListener("click",()=>{
    activeChristmasGroup=b.dataset.christmasGroup||"all";
    $$("[data-christmas-group]").forEach(x=>x.classList.toggle("active",x===b));applyCardVisibility();
  }));
}
function initGA(){
  const C=window.PIREVO_CONFIG||{}; if(!C.ga4Id)return;
  const s=document.createElement("script");s.async=true;s.src="https://www.googletagmanager.com/gtag/js?id="+encodeURIComponent(C.ga4Id);document.head.appendChild(s);
  window.dataLayer=window.dataLayer||[];window.gtag=function(){dataLayer.push(arguments)};gtag("js",new Date());gtag("config",C.ga4Id,{anonymize_ip:true});
}
render();setupSearch();setupChips();setupSeasonalFilters();applyCardVisibility();initGA();$$("[data-year]").forEach(x=>x.textContent=new Date().getFullYear());
})();