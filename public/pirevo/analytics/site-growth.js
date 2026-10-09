(()=>{
"use strict";
const $=id=>document.getElementById(id);
const status=$("growthStatus");
if(!status)return;
const C=window.PIREVO_CONFIG||{};
let token="";
try{token=localStorage.getItem("pirevo_analytics_access")||""}catch{}
const fmt=n=>n==null?"—":new Intl.NumberFormat("en-US").format(Number(n));
const label=x=>x==="astramate"?"Astramate":x==="keepry"?"Keepry":x;
function pretty(path){
 if(path==="/")return "AstraLabs home";
 if(/^\/astramate\/?$/.test(path))return "Astramate";
 if(/^\/keepry\/?$/.test(path))return "Keepry";
 return path.replace("/guides/","Guide: ").replace(/-/g," ");
}
if(!token||!C.analyticsDbUrl||!C.analyticsAnonKey){status.textContent="Unlock the private dashboard to view site counters.";return}
async function load(){
 try{
  const res=await fetch(C.analyticsDbUrl+"/rest/v1/rpc/pirevo_growth_counters",{
   method:"POST",cache:"no-store",
   headers:{apikey:C.analyticsAnonKey,Authorization:"Bearer "+C.analyticsAnonKey,"Content-Type":"application/json"},
   body:JSON.stringify({p_days:7,p_token:token})
  });
  if(!res.ok)throw new Error("Unavailable");
  const d=await res.json(),a=d.astralabs||{},p=d.pirevo||{};
  const fields={
   growthSiteVisitors:a.visitors,growthSiteSessions:a.sessions,growthSitePageviews:a.page_views,
   growthPirevoPageviews:p.page_views,growthPirevoAppClicks:p.app_clicks,growthSiteStoreClicks:a.store_clicks
  };
  Object.keys(fields).forEach(id=>{const el=$(id);if(el)el.textContent=fmt(fields[id])});
  const apps=Array.isArray(d.apps)?d.apps:[];
  $("growthAppRows").innerHTML=apps.map(x=>'<tr><td>'+label(x.app)+'</td><td>'+fmt(x.pirevo_app_clicks)+
   '</td><td>'+fmt(x.app_landing_views)+'</td><td>'+fmt(x.site_app_clicks)+
   '</td><td>'+fmt(x.google_play_clicks)+'</td><td>'+fmt(x.app_store_clicks)+'</td></tr>').join("")||
   '<tr><td colspan="6">Waiting for tracked app interest.</td></tr>';
  const pages=Array.isArray(d.top_pages)?d.top_pages:[];
  $("growthTopPages").innerHTML=pages.map(x=>'<div class="growth-page"><span>'+
   pretty(x.path)+'</span><strong>'+fmt(x.views)+'</strong></div>').join("")||
   '<div class="empty">AstraLabs website tracking starts from this deployment.</div>';
  const last=a.last_event_at?new Date(a.last_event_at).toLocaleString("en-PH",{
   month:"short",day:"numeric",hour:"numeric",minute:"2-digit"}):"awaiting first website visit";
  status.textContent="First-party counters · last AstraLabs event: "+last+
   " · refresh 15s · excludes qa_ campaigns";
 }catch{status.textContent="Site counters temporarily unavailable. Retrying automatically."}
}
load();
setInterval(()=>{if(document.visibilityState==="visible")load()},15000);
document.addEventListener("visibilitychange",()=>{if(document.visibilityState==="visible")load()});
})();
