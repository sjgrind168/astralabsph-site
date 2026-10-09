(()=>{
"use strict";
if(window.__ASTRALABS_SITE_TRACKER)return;
window.__ASTRALABS_SITE_TRACKER=true;
const C=window.PIREVO_CONFIG||{};
if(!C.analyticsDbUrl||!C.analyticsAnonKey||navigator.globalPrivacyControl===true||
  (navigator.doNotTrack||window.doNotTrack||navigator.msDoNotTrack)==="1"||
  navigator.webdriver===true)return;
const pathname=location.pathname;
if(!(pathname==="/"||/^\/(?:astramate|keepry)(?:\/|$)/.test(pathname)||pathname.startsWith("/guides/")))return;
const key="astralabsph_";
const get=(storage,k)=>{try{return storage.getItem(k)||""}catch{return""}};
const put=(storage,k,v)=>{try{storage.setItem(k,v)}catch{}};
const id=()=>globalThis.crypto?.randomUUID?.()||"a_"+Date.now().toString(36)+"_"+Math.random().toString(36).slice(2);
let visitor=get(localStorage,key+"vid");
if(!visitor){visitor=id();put(localStorage,key+"vid",visitor)}
let session=get(sessionStorage,key+"sid");
if(!session){session=id();put(sessionStorage,key+"sid",session)}
const qs=new URLSearchParams(location.search);
const safe=(v,max)=>String(v||"").trim().slice(0,max);
const focus=pathname.startsWith("/astramate")?"astramate":pathname.startsWith("/keepry")?"keepry":
  ["astramate","keepry"].includes(qs.get("app"))?qs.get("app"):null;
let source=safe(qs.get("utm_source"),120).toLowerCase();
let refer="";
try{
 const u=new URL(document.referrer);
 if(u.origin===location.origin&&u.pathname.startsWith("/pirevo"))refer="pirevo";
 else if(u.origin!==location.origin){
   const host=u.hostname.replace(/^www\./,"").toLowerCase();
   refer=/pinterest\./.test(host)?"pinterest":/google\./.test(host)?"google":host;
 }
}catch{}
if(!source)source=get(sessionStorage,key+"source")||refer||"direct";
if(!get(sessionStorage,key+"source")||qs.has("utm_source"))put(sessionStorage,key+"source",source);
const campaign=safe(qs.get("utm_campaign"),140)||get(sessionStorage,key+"campaign")||null;
if(qs.has("utm_campaign"))put(sessionStorage,key+"campaign",campaign||"");
function log(event_name,target_app=null,destination=null){
 const data={visitor_id:visitor,session_id:session,event_name,
   path:pathname,target_app,destination,traffic_source:source,utm_campaign:campaign};
 try{
  fetch(C.analyticsDbUrl+"/rest/v1/astralabs_site_events",{
   method:"POST",keepalive:true,
   headers:{apikey:C.analyticsAnonKey,Authorization:"Bearer "+C.analyticsAnonKey,
    "Content-Type":"application/json",Prefer:"return=minimal"},
   body:JSON.stringify(data)
  }).catch(()=>{});
 }catch{}
}
if(!get(sessionStorage,key+"started")){
 put(sessionStorage,key+"started","1");log("session_start",focus);
}
log("page_view",focus);
document.addEventListener("click",e=>{
 const a=e.target.closest?.("a[href]");
 if(!a)return;
 let url;
 try{url=new URL(a.href,location.href)}catch{return}
 const p=url.pathname;
 const play=url.hostname==="play.google.com";
 const apple=url.hostname==="apps.apple.com";
 let app=null;
 if(play){
  const id=url.searchParams.get("id")||"";
  app=id==="com.astralabs.astramate"?"astramate":id==="com.astralabs.keepry"?"keepry":null;
 }else if(apple&&p.includes("/astramate/"))app="astramate";
 if(app&&(play||apple)){log("store_click",app,play?"google_play":"app_store");return}
 if(url.origin===location.origin){
  const match=p.match(/^\/(astramate|keepry)\/?$/);
  if(match)log("app_click",match[1]);
 }
},{capture:true});
})();
