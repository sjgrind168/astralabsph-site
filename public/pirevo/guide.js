const C=window.PIREVO_CONFIG||{};
function esc(s){return String(s??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]))}
function amazonUrl(q,asin){const u=asin?new URL("https://www.amazon.com/dp/"+encodeURIComponent(asin)):new URL("https://www.amazon.com/s");if(!asin)u.searchParams.set("k",q);if(C.affiliateEnabled&&C.amazonAssociateTag)u.searchParams.set("tag",C.amazonAssociateTag);return u.toString()}
function trackAmazon(slug,pick){if(window.gtag)gtag("event","affiliate_click",{guide_slug:slug,item_name:pick,market:"GLOBAL"})}
function initGA(){if(!C.ga4Id)return;const s=document.createElement("script");s.async=true;s.src="https://www.googletagmanager.com/gtag/js?id="+encodeURIComponent(C.ga4Id);document.head.appendChild(s);window.dataLayer=window.dataLayer||[];window.gtag=function(){dataLayer.push(arguments)};gtag("js",new Date());gtag("config",C.ga4Id,{anonymize_ip:true})}
function ensureScript(globalName,src){if(window[globalName])return Promise.resolve();return new Promise((resolve,reject)=>{const s=document.createElement("script");s.src=src;s.onload=resolve;s.onerror=reject;document.head.appendChild(s)})}function ensureVisuals(){return ensureScript("PIREVO_GUIDE_IMAGES","/pirevo/guide-images.js")}function ensureProducts(){return ensureScript("PIREVO_PRODUCT_SHORTLISTS","/pirevo/products.js")}
function relatedCards(slug){const media=window.PIREVO_GUIDE_IMAGES||{};return Object.entries(window.PIREVO_GUIDES||{}).filter(([s])=>s!==slug).slice(0,3).map(([s,g])=>{const m=media[s]||{};return `<a class="related-card" href="/pirevo/guides/${s}/">${m.image?`<img src="${m.image}" alt="${esc(g.title)}" loading="lazy">`:""}<span class="visual-shade"></span><div><small>${esc(g.category)}</small><strong>${esc(g.title)}</strong><em>Read guide →</em></div></a>`}).join("")}
function shortlistBlock(slug){const s=window.PIREVO_PRODUCT_SHORTLISTS?.[slug];if(!s)return"";return `<section class="shortlist-section"><div class="article-section-head"><div><span>PIREVO SHORTLIST</span><h2>${esc(s.heading)}</h2></div><p>${esc(s.intro)}</p></div><div class="shortlist-grid">${s.products.map((p,i)=>`<article class="shortlist-card"><div class="shortlist-top"><span>${String(i+1).padStart(2,"0")}</span><small>${esc(p.brand)}</small></div><h3>${esc(p.name)}</h3><p><strong>Why it fits:</strong> ${esc(p.fit)}</p><p><strong>Verify before buying:</strong> ${esc(p.verify)}</p><div class="shortlist-signal">${esc(p.signal)}</div><a class="amazon-btn shortlist-btn" href="${amazonUrl(p.search,p.asin)}" target="_blank" rel="sponsored nofollow noopener" data-shortlist="${esc(p.name)}">${p.asin?"View product on Amazon":"Search exact product on Amazon"} <span>→</span></a></article>`).join("")}</div><p class="shortlist-note">PIREVO does not claim hands-on testing for these named candidates. Product listings, sellers, variants, ratings and availability can change, so verify the current Amazon listing before purchase.</p></section>`}function render(){const slug=document.body.dataset.slug,g=window.PIREVO_GUIDES?.[slug],root=document.querySelector("#article");if(!g||!root){if(root)root.innerHTML="<h1>Guide not found</h1>";return}const media=window.PIREVO_GUIDE_IMAGES||{},m=media[slug]||{};
document.title=g.title+" | PIREVO";document.querySelector('meta[name="description"]')?.setAttribute("content",g.dek);document.querySelector('link[rel="canonical"]')?.setAttribute("href",C.siteUrl+"/guides/"+slug+"/");
const disclosure=C.affiliateEnabled?'<div class="editorial-note"><strong>Affiliate disclosure</strong><p>As an Amazon Associate I earn from qualifying purchases. Editorial criteria are independent of commission.</p></div>':'<div class="editorial-note"><strong>Editorial note</strong><p>This guide currently uses standard Amazon.com search links without an Associates tracking tag. Prices, sellers and availability can change.</p></div>';
const takeaways=(g.checklist||[]).slice(0,3).map(x=>`<li>${esc(x)}</li>`).join("");
root.className="article article-premium";
root.innerHTML=`
<div class="breadcrumb"><a href="/pirevo/">PIREVO</a><span>/</span><span>${esc(g.category)}</span></div>
<section class="article-hero">
  <div class="article-hero-media">${m.image?`<img src="${m.image}" alt="${esc(g.title)}">`:""}<span class="visual-shade"></span></div>
  <div class="article-hero-copy">
    <div class="eyebrow">${esc(g.category)} · SHOPPING GUIDE</div>
    <h1>${esc(g.title)}</h1>
    <p class="dek">${esc(g.dek)}</p>
    <div class="article-meta"><span>Updated ${esc(g.updated)}</span><span>•</span><span>${esc(g.readTime)}</span><span>•</span><span>Practical buying guide</span></div>
  </div>
</section>
<section class="quick-take">
  <div><span>THE QUICK TAKE</span><h2>What matters before you buy</h2><p>${esc(g.intro?.[0]||g.dek)}</p></div>
  <ul>${takeaways}</ul>
</section>
${disclosure}
<section class="article-prose">${(g.intro||[]).slice(1).map(p=>"<p>"+esc(p)+"</p>").join("")}</section>
<div class="article-section-head"><div><span>COMPARE SMARTER</span><h2>${esc(g.listHeading||"What to look for")}</h2></div><p>Use these as comparison categories, then verify the exact listing before checkout.</p></div>
<div class="pick-list premium-picks">${g.picks.map((p,i)=>`
<section class="pick premium-pick">
  <div class="pick-number">${String(i+1).padStart(2,"0")}</div>
  <div class="pick-content"><h3>${esc(p.name)}</h3><p><strong>Why it earns a look:</strong> ${esc(p.why)}</p><p><strong>Check before buying:</strong> ${esc(p.lookFor)}</p>
  <a class="amazon-btn" href="${amazonUrl(p.search)}" target="_blank" rel="sponsored nofollow noopener" data-pick="${esc(p.name)}">Explore on Amazon <span>→</span></a></div>
</section>`).join("")}</div>
${shortlistBlock(slug)}
<section class="deep-dive">${g.sections.map(s=>`<article><span>BUYING NOTE</span><h2>${esc(s.heading)}</h2>${s.paragraphs.map(p=>"<p>"+esc(p)+"</p>").join("")}</article>`).join("")}</section>
<section class="checklist-panel"><div><span>FINAL CHECK</span><h2>Before you place the order</h2></div><ul>${g.checklist.map(x=>"<li>"+esc(x)+"</li>").join("")}</ul></section>
<p class="smallprint">PIREVO does not display live Amazon prices. Check the retailer page for current price, stock, shipping, dimensions, compatibility, returns and warranty information before purchasing.</p>
<section class="related-section"><div class="article-section-head"><div><span>KEEP EXPLORING</span><h2>Related PIREVO guides</h2></div></div><div class="related-grid">${relatedCards(slug)}</div></section>
<div class="article-end"><a class="btn btn-dark" href="/pirevo/">Browse all PIREVO guides</a></div>`;
root.querySelectorAll("[data-pick]").forEach(a=>a.addEventListener("click",()=>trackAmazon(slug,a.dataset.pick)));root.querySelectorAll("[data-shortlist]").forEach(a=>a.addEventListener("click",()=>{trackAmazon(slug,a.dataset.shortlist);if(window.gtag)gtag("event","product_shortlist_click",{guide_slug:slug,item_name:a.dataset.shortlist,market:"GLOBAL"})}));
const schema={"@context":"https://schema.org","@type":"Article",headline:g.title,description:g.dek,dateModified:g.updated,author:{"@type":"Organization","name":"PIREVO"},publisher:{"@type":"Organization","name":"PIREVO"},mainEntityOfPage:C.siteUrl+"/guides/"+slug+"/",about:g.keywords};
const j=document.createElement("script");j.type="application/ld+json";j.textContent=JSON.stringify(schema);document.head.appendChild(j)}
initGA();Promise.allSettled([ensureVisuals(),ensureProducts()]).then(render).catch(render);