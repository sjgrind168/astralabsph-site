(()=>{
  if(window.PIREVO_ANALYTICS)return;
  const C=window.PIREVO_CONFIG||{};
  const GPC=navigator.globalPrivacyControl===true;
  const DNT=(navigator.doNotTrack||window.doNotTrack||navigator.msDoNotTrack)==="1";
  const allowed=()=>!GPC&&!DNT;
  const safe=(v,n=220)=>String(v??"").replace(/\s+/g," ").trim().slice(0,n);
  const uid=()=>{
    if(globalThis.crypto?.randomUUID)return crypto.randomUUID();
    return "p_"+Date.now().toString(36)+"_"+Math.random().toString(36).slice(2);
  };
  const store=(s,k,v)=>{try{s.setItem(k,v)}catch{}};
  const load=(s,k)=>{try{return s.getItem(k)||""}catch{return""}};
  let visitorId=load(localStorage,"pirevo_vid");
  if(!visitorId){visitorId=uid();store(localStorage,"pirevo_vid",visitorId)}
  let sessionId=load(sessionStorage,"pirevo_sid");
  if(!sessionId){sessionId=uid();store(sessionStorage,"pirevo_sid",sessionId)}

  function pageType(){
    const p=location.pathname;
    if(/\/pirevo\/products\//.test(p))return"product";
    if(/\/pirevo\/guides\//.test(p))return"guide";
    if(/\/pirevo\/analytics\//.test(p))return"analytics";
    if(/\/pirevo\/?$/.test(p))return"storefront";
    return"pirevo_other";
  }
  function productContext(){
    if(pageType()!=="product")return{};
    const slug=(location.pathname.match(/\/products\/([^/]+)/)||[])[1]||"";
    const h1=document.querySelector("h1");
    const amazon=document.querySelector('a[href*="amazon.com"]');
    const asin=(amazon?.href.match(/\/dp\/([A-Z0-9]{10})/i)||[])[1]||"";
    const category=document.querySelector(".product-breadcrumb a:last-child")?.textContent||"";
    return {product_slug:slug,item_id:asin,item_name:safe(h1?.textContent),item_category:safe(category)};
  }
  function deriveAttribution(){
    const qs=new URLSearchParams(location.search);
    const fromQuery={};
    ["utm_source","utm_medium","utm_campaign","utm_content","utm_term"].forEach(k=>{
      const v=qs.get(k); if(v)fromQuery[k]=safe(v,220);
    });
    const ref=document.referrer||"";
    let source=safe(fromQuery.utm_source,120).toLowerCase();
    let refHost="";
    try{refHost=ref?new URL(ref).hostname.toLowerCase():""}catch{}
    if(!source){
      if(/pinterest\./i.test(refHost))source="pinterest";
      else if(/google\./i.test(refHost))source="google";
      else if(refHost&&refHost!==location.hostname.toLowerCase())source=refHost.replace(/^www\./,"");
      else source="direct";
    }
    const existing=load(sessionStorage,"pirevo_attr");
    if(Object.keys(fromQuery).length){
      const fresh={...fromQuery,traffic_source:source,referrer_host:refHost};
      store(sessionStorage,"pirevo_attr",JSON.stringify(fresh));
      return fresh;
    }
    if(existing){
      try{return JSON.parse(existing)}catch{}
    }
    const fresh={traffic_source:source,referrer_host:refHost};
    store(sessionStorage,"pirevo_attr",JSON.stringify(fresh));
    return fresh;
  }
  const ATTR=deriveAttribution();

  function gaReady(){
    if(!C.ga4Id||!allowed())return false;
    if(window.gtag){window.__PIREVO_GA_INIT=true;return true}
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
  function gaEvent(name,params={}){
    if(!gaReady())return;
    gtag("event",name,{...ATTR,page_type:pageType(),...productContext(),...params});
  }
  function dbEvent(name,params={}){
    if(!allowed()||!C.analyticsDbUrl||!C.analyticsAnonKey)return;
    if(pageType()==="analytics")return;
    const ctx=productContext();
    const body={
      visitor_id:visitorId,
      session_id:sessionId,
      event_name:name,
      path:location.pathname,
      page_type:pageType(),
      product_slug:safe(params.product_slug??ctx.product_slug,160)||null,
      item_id:safe(params.item_id??ctx.item_id,40)||null,
      item_name:safe(params.item_name??ctx.item_name,240)||null,
      item_category:safe(params.item_category??ctx.item_category,160)||null,
      traffic_source:safe(ATTR.traffic_source,120)||"direct",
      utm_source:safe(ATTR.utm_source,160)||null,
      utm_medium:safe(ATTR.utm_medium,160)||null,
      utm_campaign:safe(ATTR.utm_campaign,220)||null,
      utm_content:safe(ATTR.utm_content,220)||null,
      utm_term:safe(ATTR.utm_term,220)||null,
      referrer_host:safe(ATTR.referrer_host,220)||null,
      search_term:safe(params.search_term,180)||null,
      scroll_depth:Number.isFinite(params.scroll_depth)?params.scroll_depth:null,
      link_text:safe(params.link_text,160)||null
    };
    fetch(C.analyticsDbUrl+"/rest/v1/pirevo_events",{
      method:"POST",
      keepalive:true,
      headers:{
        apikey:C.analyticsAnonKey,
        Authorization:"Bearer "+C.analyticsAnonKey,
        "Content-Type":"application/json",
        Prefer:"return=minimal"
      },
      body:JSON.stringify(body)
    }).catch(()=>{});
  }
  function event(name,params={}){
    dbEvent(name,params);
    if(name==="view_item"||name==="affiliate_click"||name==="product_click"||name==="search"||name==="scroll_depth"||name==="app_click")gaEvent(name,params);
  }
  function init(){
    if(window.__PIREVO_ANALYTICS_BOUND)return;
    window.__PIREVO_ANALYTICS_BOUND=true;
    gaReady();
    if(!allowed()||pageType()==="analytics")return;

    if(!load(sessionStorage,"pirevo_session_started")){
      store(sessionStorage,"pirevo_session_started","1");
      dbEvent("session_start",{});
      if((ATTR.traffic_source||"").toLowerCase()==="pinterest"){
        gaEvent("pinterest_landing",{campaign:ATTR.utm_campaign||"",creative:ATTR.utm_content||""});
      }
    }
    dbEvent("page_view",{});

    if(pageType()==="product"){
      const ctx=productContext();
      event("view_item",{...ctx,items:[{item_id:ctx.item_id,item_name:ctx.item_name,item_category:ctx.item_category}]});
    }

    document.addEventListener("click",e=>{
      const a=e.target.closest("a"); if(!a)return;
      const href=a.href||"";
      if(/amazon\.com/i.test(href)){
        const ctx=productContext();
        const asin=(href.match(/\/dp\/([A-Z0-9]{10})/i)||[])[1]||ctx.item_id||"";
        event("affiliate_click",{item_id:asin,link_text:safe(a.textContent,100)});
        return;
      }
      const appTarget=(href.match(/\/(astramate|keepry)\/(?:\?|#|$)/i)||[])[1];
      if(appTarget){
        event("app_click",{item_name:appTarget.toLowerCase(),link_text:safe(a.textContent,100)});
        return;
      }
      if(/\/pirevo\/products\//.test(href)){
        const slug=(href.match(/\/products\/([^/?#]+)/)||[])[1]||"";
        event("product_click",{product_slug:slug,link_text:safe(a.textContent,100)});
      }
    },{capture:true});

    const search=document.querySelector("#shopSearch");
    if(search){
      let last="";
      const fire=()=>{const q=safe(search.value,80);if(q.length>=2&&q!==last){last=q;event("search",{search_term:q})}};
      search.addEventListener("change",fire);
      search.addEventListener("keydown",e=>{if(e.key==="Enter")fire()});
    }

    let s50=false,s90=false;
    const onScroll=()=>{
      const d=document.documentElement;
      const max=Math.max(1,d.scrollHeight-innerHeight);
      const pct=Math.round((scrollY/max)*100);
      if(pct>=50&&!s50){s50=true;event("scroll_depth",{scroll_depth:50})}
      if(pct>=90&&!s90){s90=true;event("scroll_depth",{scroll_depth:90});removeEventListener("scroll",onScroll)}
    };
    addEventListener("scroll",onScroll,{passive:true});
  }
  window.PIREVO_ANALYTICS={
    init,
    event,
    status:()=>({ga4Id:C.ga4Id||"",enabled:allowed(),pageType:pageType(),attribution:ATTR,product:productContext()})
  };
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();