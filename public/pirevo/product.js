(()=>{
const S=window.PIREVO_STORE||{collections:[],products:[]};
const slug=document.body.dataset.productSlug;
const p=S.products.find(x=>x.slug===slug); if(!p)return;
const c=S.collections.find(x=>x.id===p.collection);
const $=(s,r=document)=>r.querySelector(s);
const esc=s=>String(s??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]));
const compact=n=>n>=100000?(n/1000).toFixed(0)+"k":n>=1000?(n/1000).toFixed(n>=10000?0:1)+"k":String(n);
function sourceQuery(){const u=new URLSearchParams(location.search);return ["utm_source","utm_medium","utm_campaign","utm_content"].map(k=>u.get(k)?k+"="+encodeURIComponent(u.get(k)):"").filter(Boolean).join("&")}
function productUrl(x){const b="/pirevo/products/"+x.slug+"/index.html";const q=sourceQuery();return q?b+"?"+q:b}
function amazonClick(e){if(window.gtag)gtag("event","amazon_click",{asin:p.asin,product:p.slug,collection:p.collection,utm_campaign:new URLSearchParams(location.search).get("utm_campaign")||""})}
const root=$("#productRoot");
root.innerHTML=`
<div class="product-breadcrumb"><a href="/pirevo/">PIREVO</a><span>/</span><a href="/pirevo/#${esc(c.id)}">${esc(c.name)}</a></div>
<section class="pdp-hero">
  <div class="pdp-gallery"><div class="pdp-image-wrap"><span class="shop-badge">${esc(p.badge)}</span><img src="${esc(p.image)}" alt="${esc(p.fullName)}" referrerpolicy="no-referrer"></div><div class="pdp-media-note">Retailer image served externally. Product color/variant may differ. Verify the current Amazon listing.</div></div>
  <div class="pdp-buy">
    <div class="shop-brand">${esc(p.brand)}</div><h1>${esc(p.shortName)}</h1>
    <p class="pdp-fullname">${esc(p.fullName)}</p>
    <div class="pdp-proof"><span><strong>★ ${p.rating.toFixed(1)}</strong> Amazon rating snapshot</span><span><strong>${compact(p.reviews)}</strong> ratings snapshot</span><span><strong>${esc(p.rank)}</strong></span></div>
    <div class="pdp-trend"><span>WHY IT'S HERE</span><strong>${esc(p.trend)}</strong></div>
    <p class="pdp-why">${esc(p.why)}</p>
    <ul class="pdp-bullets">${p.bullets.map(x=>`<li>${esc(x)}</li>`).join("")}</ul>
    <div class="pdp-price-note">Prices, coupons, seller and stock change. PIREVO does not display a pretend live Amazon price.</div>
    <a class="pdp-amazon" href="${esc(p.amazon)}" target="_blank" rel="sponsored nofollow noopener noreferrer">Check current price on Amazon <span>↗</span></a>
    <p class="pdp-disclosure">As an Amazon Associate I earn from qualifying purchases. Product research updated Oct. 3, 2026.</p>
  </div>
</section>
<section class="pdp-info-grid">
 <article><span>BEST FOR</span><h2>Who this fits</h2><p>${esc(p.bestFor)}</p></article>
 <article><span>GOOD TO KNOW</span><h2>One tradeoff to check</h2><p>${esc(p.caveat)}</p></article>
 <article><span>PIREVO FILTER</span><h2>Why it passed</h2><p>Trend relevance, Amazon sales evidence, review confidence, commission economics and Pinterest visual potential all cleared our launch threshold.</p></article>
 <article><span>RETAILER CHECK</span><h2>Verify before checkout</h2><p>Confirm the exact variant, dimensions, materials, current seller, return terms, stock and current offer on Amazon.</p></article>
</section>
<section class="pdp-related"><div class="shop-section-head"><div><span>KEEP SHOPPING</span><h2>More from ${esc(c.name)}</h2></div><a href="/pirevo/#${esc(c.id)}">View collection →</a></div><div class="shop-grid">${S.products.filter(x=>x.collection===p.collection&&x.slug!==p.slug).map(x=>`<article class="shop-product-card compact"><a class="shop-product-media" href="${productUrl(x)}"><img src="${esc(x.image)}" alt="${esc(x.fullName)}" loading="lazy" referrerpolicy="no-referrer"></a><div class="shop-product-copy"><div class="shop-brand">${esc(x.brand)}</div><h3><a href="${productUrl(x)}">${esc(x.shortName)}</a></h3><div class="shop-rating"><strong>★ ${x.rating.toFixed(1)}</strong><span>${compact(x.reviews)} ratings</span></div></div></article>`).join("")}</div></section>
<section class="pdp-research"><div><span>RESEARCH STANDARD</span><h2>Not a random affiliate pick.</h2></div><p>PIREVO uses current Pinterest demand signals and Amazon category evidence to shortlist products, then checks rating depth, positioning, review confidence, value and likely return friction before publishing. A trend is discovery evidence, not a guarantee of quality or future popularity.</p></section>
`;
$(".pdp-amazon")?.addEventListener("click",amazonClick);
document.title=p.shortName+" | PIREVO";

})();