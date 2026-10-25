/* MerchLab PH first-party measurement. No cookies, IP collection, purchase claims, or Shopee API. */
(()=>{
"use strict";
if(window.MERCHLAB_ANALYTICS)return;
const C=window.PIREVO_CONFIG||{};
const allowedEvents=new Set(["session_start","page_view","product_view","category_view","search","add_to_bag","remove_from_bag","cart_qty_change","bag_view","shopee_handoff_view","outbound_shopee"]);
const DNT=navigator.globalPrivacyControl===true||[navigator.doNotTrack,window.doNotTrack,navigator.msDoNotTrack].includes("1");
const productionHost=["astralabsph.com","www.astralabsph.com"].includes(location.hostname);
const blocked=DNT||navigator.webdriver===true||new URLSearchParams(location.search).has("metrics_qa")||!productionHost||!/^\/merchlab(?:\/|$)/.test(location.pathname)||!C.analyticsDbUrl||!C.analyticsAnonKey;
const prefix="merchlabph_a1_",read=(s,k)=>{try{return s.getItem(prefix+k)||"";}catch{return"";}};
const save=(s,k,v)=>{try{s.setItem(prefix+k,v);}catch{/* Browser storage disabled. */}};
const uuid=()=>crypto?.randomUUID?.()||"ml_"+Date.now().toString(36)+"_"+Math.random().toString(36).slice(2);
const path=location.pathname;
let visitor="",session="",source="",campaign="";
const clean=(v,n)=>String(v??"").trim().slice(0,n);
function sourceFromRef(){
 try{
  const u=new URL(document.referrer);if(u.origin===location.origin)return "internal";
  const h=u.hostname.replace(/^www\./,"").toLowerCase();
  if(/facebook\.com|fb\.com|fb\.me|messenger\.com/.test(h))return"facebook";
  if(/instagram\.com/.test(h))return"instagram";
  if(/google\./.test(h))return"google";
  if(/pinterest\./.test(h))return"pinterest";
  if(/tiktok\.com/.test(h))return"tiktok";
  return clean(h,120);
 }catch{return"direct";}
}
const qs=new URLSearchParams(location.search);
if(!blocked){
 visitor=read(localStorage,"visitor");if(!visitor){visitor=uuid();save(localStorage,"visitor",visitor);}
 session=read(sessionStorage,"session");if(!session){session=uuid();save(sessionStorage,"session",session);}
 source=clean(qs.get("utm_source"),120).toLowerCase()||read(sessionStorage,"source")||sourceFromRef();
 campaign=clean(qs.get("utm_campaign"),140)||read(sessionStorage,"campaign");
 save(sessionStorage,"source",source);if(campaign)save(sessionStorage,"campaign",campaign);
}
function send(event_name,fields={}){
 if(blocked||!visitor||!session||!allowedEvents.has(event_name)||read(localStorage,"optout")==="yes")return;
 const data={visitor_id:visitor,session_id:session,event_name,path,
  product_id:/^\d{5,18}$/.test(String(fields.product_id||""))?String(fields.product_id):null,
  category:fields.category?clean(fields.category,50):null,
  search_term:fields.search_term?clean(fields.search_term,80).toLowerCase():null,
  quantity:Number.isInteger(fields.quantity)&&fields.quantity>=1&&fields.quantity<=99?fields.quantity:null,
  traffic_source:source||"direct",utm_campaign:campaign||null};
 try{fetch(C.analyticsDbUrl+"/rest/v1/merchlab_site_events",{method:"POST",keepalive:true,
  headers:{apikey:C.analyticsAnonKey,Authorization:"Bearer "+C.analyticsAnonKey,"Content-Type":"application/json",Prefer:"return=minimal"},
  body:JSON.stringify(data)}).catch(()=>{});}catch{/* No impact on shopping. */}
}
function outbound(e){
 const a=e.target.closest?.("a[href]");if(!a)return;
 let u;try{u=new URL(a.href);}catch{return;}
 if(!["shopee.ph","www.shopee.ph"].includes(u.hostname)||u.protocol!=="https:")return;
 const id=u.pathname.match(/^\/product\/\d+\/(\d{5,18})(?:\/|$)/)?.[1];
 if(id)send("outbound_shopee",{product_id:id});
}
if(!blocked){
 if(!read(sessionStorage,"started")){save(sessionStorage,"started","1");send("session_start");}
 send("page_view");
 const id=path.match(/^\/merchlab\/p\/(\d{5,18})(?:\/|$)/)?.[1];
 if(id)send("product_view",{product_id:id});
 const category=path.match(/^\/merchlab\/c\/([a-z]{2,30})(?:\/|$)/)?.[1];
 if(category)send("category_view",{category});
 document.addEventListener("click",outbound,{capture:true});
}
window.MERCHLAB_ANALYTICS={track:send,enabled:!blocked,status:()=>({enabled:!blocked,noPurchases:true})};
})();