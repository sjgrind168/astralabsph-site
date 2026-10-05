(()=>{
  if(window.PIREVO_ANALYTICS)return;
  const C=window.PIREVO_CONFIG||{};
  const qs=new URLSearchParams(location.search);
  const ATTR_KEYS=["utm_source","utm_medium","utm_campaign","utm_content","utm_term"];
  const ATTR={};
  ATTR_KEYS.forEach(k=>{const v=qs.get(k);if(v)ATTR[k]=v.slice(0,160)});
  const GPC=navigator.globalPrivacyControl===true;
  const DNT=(navigator.doNotTrack||window.doNotTrack||navigator.msDoNotTrack)==="1";
  const allowed=()=>!!C.ga4Id&&!GPC&&!DNT;
  function safeText(v,n=180){return String(v||"").replace(/\s+/g," ").trim().slice(0,n)}
  function pageType(){
    const p=location.pathname;
    if(/\/pirevo\/products\//.test(p))return"product";
    if(/\/pirevo\/guides\//.test(p))return"guide";
    if(/\/pirevo\/?$/.test(p))return"storefront";
    return"pirevo_other";
  }
  function productContext(){
    if(pageType()!=="product")return{};
    const slug=(location.pathname.match(/\/products\/([^/]+)/)||[])[1]||"";
    const h1=document.querySelector("h1");
    const amazon=document.querySelector('a[href*="amazon.com"]');
    const asin=(amazon?.href.match(/\/dp\/([A-Z0-9]{10})/i)||[])[1]||"";
    const collection=document.querySelector(".product-breadcrumb a:last-child")?.textContent||"";
    return {product_slug:slug,item_id:asin,item_name:safeText(h1?.textContent),item_category:safeText(collection)};
  }
  function attribution(){
    const ref=document.referrer||"";
    let source=ATTR.utm_source||"";
    if(!source&&/pinterest\./i.test(ref))source="pinterest";
    else if(!source&&/google\./i.test(ref))source="google";
    return {...ATTR,traffic_source:source||"direct",referrer_host:(()=>{try{return ref?new URL(ref).hostname:""}catch{return""}})()};
  }
  function ensureGA(){
    if(!allowed())return false;
    if(window.__PIREVO_GA_INIT)return !!window.gtag;
    window.__PIREVO_GA_INIT=true;
    window.dataLayer=window.dataLayer||[];
    window.gtag=window.gtag||function(){dataLayer.push(arguments)};
    const s=document.createElement("script");
    s.async=true;s.src="https://www.googletagmanager.com/gtag/js?id="+encodeURIComponent(C.ga4Id);
    document.head.appendChild(s);
    gtag("js",new Date());
    gtag("config",C.ga4Id,{
      anonymize_ip:true,
      allow_google_signals:false,
      allow_ad_personalization_signals:false,
      send_page_view:true
    });
    return true;
  }
  function event(name,params={}){
    if(!ensureGA()||!window.gtag)return;
    gtag("event",name,{...attribution(),page_type:pageType(),...productContext(),...params});
  }
  function init(){
    ensureGA();
    if(!allowed())return;
    const ctx=productContext(),attr=attribution();
    event("pirevo_landing",{landing_path:location.pathname,...attr});
    if(pageType()==="product"){
      event("view_item",{items:[{item_id:ctx.item_id,item_name:ctx.item_name,item_category:ctx.item_category}]});
    }
    if(attr.traffic_source==="pinterest")event("pinterest_landing",{campaign:attr.utm_campaign||"",creative:attr.utm_content||""});
    document.addEventListener("click",e=>{
      const a=e.target.closest("a"); if(!a)return;
      const href=a.href||"";
      if(/amazon\.com/i.test(href)){
        const asin=(href.match(/\/dp\/([A-Z0-9]{10})/i)||[])[1]||ctx.item_id||"";
        event("affiliate_click",{outbound_domain:"amazon.com",item_id:asin,link_text:safeText(a.textContent,100)});
        return;
      }
      if(/\/pirevo\/products\//.test(href)){
        const slug=(href.match(/\/products\/([^/?#]+)/)||[])[1]||"";
        event("product_click",{target_product_slug:slug,link_text:safeText(a.textContent,100)});
      }
    },{capture:true});
    const search=document.querySelector("#shopSearch");
    if(search){
      let last="";
      const fire=()=>{const q=safeText(search.value,80);if(q.length>=2&&q!==last){last=q;event("search",{search_term:q})}};
      search.addEventListener("change",fire);
      search.addEventListener("keydown",e=>{if(e.key==="Enter")fire()});
    }
    let s50=false,s90=false;
    const onScroll=()=>{
      const d=document.documentElement;
      const max=Math.max(1,d.scrollHeight-innerHeight);
      const pct=Math.round((scrollY/max)*100);
      if(pct>=50&&!s50){s50=true;event("scroll_depth",{percent_scrolled:50})}
      if(pct>=90&&!s90){s90=true;event("scroll_depth",{percent_scrolled:90});removeEventListener("scroll",onScroll)}
    };
    addEventListener("scroll",onScroll,{passive:true});
  }
  window.PIREVO_ANALYTICS={init,event,status:()=>({ga4Id:C.ga4Id||"",enabled:allowed(),gpc:GPC,dnt:DNT,pageType:pageType(),attribution:attribution(),product:productContext()})};
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();
