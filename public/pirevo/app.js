const C=window.PIREVO_CONFIG||{},MEDIA=window.PIREVO_GUIDE_IMAGES||{};
function initGA(){if(!C.ga4Id)return;const s=document.createElement("script");s.async=true;s.src="https://www.googletagmanager.com/gtag/js?id="+encodeURIComponent(C.ga4Id);document.head.appendChild(s);window.dataLayer=window.dataLayer||[];window.gtag=function(){dataLayer.push(arguments)};gtag("js",new Date());gtag("config",C.ga4Id,{anonymize_ip:true})}
function guideUrl(slug){return"/pirevo/guides/"+slug+"/"}
function esc(s){return String(s??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]))}
function entries(){return Object.entries(window.PIREVO_GUIDES||{})}
function guideCard(slug,g,featured=false){const m=MEDIA[slug]||{};return `<article class="${featured?"feature-card":"guide-card guide-card-premium"}">
<a class="${featured?"feature-visual":"guide-visual"}" href="${guideUrl(slug)}" aria-label="Read ${esc(g.title)}">
${m.image?`<img src="${m.image}" alt="${esc(g.title)}" loading="lazy">`:""}
<span class="visual-shade"></span>
${featured?`<div class="feature-copy"><span>${esc(g.category)}</span><h3>${esc(g.title)}</h3><div>Open guide →</div></div>`:""}
</a>
${featured?"":`<div class="guide-body guide-body-premium"><div class="meta"><span>${esc(g.category)}</span><span>•</span><span>${esc(g.readTime)}</span></div><h3>${esc(g.title)}</h3><p>${esc(g.dek)}</p><a class="premium-link" href="${guideUrl(slug)}">Read the guide <span>→</span></a></div>`}
</article>`}
function renderFeatured(){const root=document.querySelector("#featuredGuides");if(!root)return;root.innerHTML=entries().slice(0,3).map(([slug,g])=>guideCard(slug,g,true)).join("")}
function renderHome(filter="All"){const root=document.querySelector("#guides");if(!root)return;const items=entries().filter(([,g])=>filter==="All"||g.category===filter);root.innerHTML=items.map(([slug,g])=>guideCard(slug,g,false)).join("")}
function renderFilters(){const root=document.querySelector("#categoryFilter");if(!root)return;const cats=["All",...new Set(entries().map(([,g])=>g.category))];root.innerHTML=cats.map((c,i)=>`<button class="filter-chip ${i===0?"active":""}" data-cat="${esc(c)}">${esc(c)}</button>`).join("");root.querySelectorAll("button").forEach(b=>b.addEventListener("click",()=>{root.querySelectorAll("button").forEach(x=>x.classList.remove("active"));b.classList.add("active");renderHome(b.dataset.cat);document.querySelector("#guides")?.scrollIntoView({behavior:"smooth",block:"start"})}))}
function setHero(){const img=document.querySelector("#heroFeatureImage");const m=MEDIA["small-apartment-organization"];if(img&&m?.image)img.src=m.image}
function setYear(){document.querySelectorAll("[data-year]").forEach(x=>x.textContent=new Date().getFullYear())}
initGA();setHero();renderFeatured();renderFilters();renderHome();setYear();