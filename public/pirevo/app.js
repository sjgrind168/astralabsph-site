const C=window.PIREVO_CONFIG||{},MEDIA=window.PIREVO_GUIDE_IMAGES||{};
function initGA(){if(!C.ga4Id)return;const s=document.createElement("script");s.async=true;s.src="https://www.googletagmanager.com/gtag/js?id="+encodeURIComponent(C.ga4Id);document.head.appendChild(s);window.dataLayer=window.dataLayer||[];window.gtag=function(){dataLayer.push(arguments)};gtag("js",new Date());gtag("config",C.ga4Id,{anonymize_ip:true})}
function guideUrl(slug){return"/pirevo/guides/"+slug+"/"}
function esc(s){return String(s??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]))}
function renderHome(){const root=document.querySelector("#guides");if(!root||!window.PIREVO_GUIDES)return;root.className="guides-grid";root.innerHTML=Object.entries(PIREVO_GUIDES).map(([slug,g])=>{const m=MEDIA[slug]||{};return `<article class="guide-card guide-card-premium">
<a class="guide-visual" href="${guideUrl(slug)}" aria-label="Read ${esc(g.title)}">${m.image?`<img src="${m.image}" alt="${esc(g.title)}" loading="lazy">`:""}<span class="guide-visual-shine"></span></a>
<div class="guide-body guide-body-premium"><div class="meta"><span>${esc(g.category)}</span><span>•</span><span>${esc(g.readTime)}</span></div><h3>${esc(g.title)}</h3><p>${esc(g.dek)}</p><a class="premium-link" href="${guideUrl(slug)}">Read the guide <span>→</span></a></div></article>`}).join("")}
function setYear(){document.querySelectorAll("[data-year]").forEach(x=>x.textContent=new Date().getFullYear())}
initGA();renderHome();setYear();