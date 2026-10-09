(()=>{
"use strict";
const root=document.getElementById("platformReportStatus");
if(!root)return;
const C=window.PIREVO_CONFIG||{};
let token="";
try{token=localStorage.getItem("pirevo_analytics_access")||""}catch{}
if(!token||!C.analyticsDbUrl||!C.analyticsAnonKey){root.textContent="Private dashboard access required.";return;}
const amount=(r)=>{
 if(!r||r.metric_value===null||r.metric_value===undefined)return"—";
 const n=Number(r.metric_value);
 if(!Number.isFinite(n))return"—";
 if(r.metric_unit==="USD")return new Intl.NumberFormat("en-US",{style:"currency",currency:"USD"}).format(n);
 if(r.metric_unit==="PHP")return new Intl.NumberFormat("en-PH",{style:"currency",currency:"PHP"}).format(n);
 if(r.metric_unit==="percent")return n.toFixed(1)+"%";
 if(r.metric_unit==="USD_per_1000")return "$"+n.toFixed(2);
 return new Intl.NumberFormat("en-US",{maximumFractionDigits:0}).format(n);
};
async function load(){
 try{
  const res=await fetch(C.analyticsDbUrl+"/rest/v1/rpc/pirevo_platform_report_snapshot",{
   method:"POST",cache:"no-store",
   headers:{apikey:C.analyticsAnonKey,Authorization:"Bearer "+C.analyticsAnonKey,"Content-Type":"application/json"},
   body:JSON.stringify({p_token:token})
  });
  if(!res.ok)throw Error("Private report unavailable");
  const data=await res.json();
  const status=new Map((data.sources||[]).map(s=>[s.provider,s.status]));
  const metrics=data.metrics||[];
  for(const card of document.querySelectorAll(".platform-card")){
   const provider=card.dataset.provider,s=status.get(provider)||"not_connected";
   const badge=card.querySelector(".platform-status");
   badge.textContent=s==="not_connected"?"Awaiting access":"Report imported";
   badge.classList.toggle("live",s!=="not_connected");
   for(const m of card.querySelectorAll("[data-metric]")){
    const chosen=metrics.find(x=>x.provider===provider&&x.metric===m.dataset.metric&&
      (x.app_key==="all"||x.app_key===null));
    m.textContent=amount(chosen);
   }
   const available=metrics.filter(x=>x.provider===provider);
   if(available.length){
    const latest=available.reduce((a,b)=>!a||b.period_end>a.period_end?b:a,null);
    card.querySelector("[data-source-note]").textContent=
     "Latest imported report through "+latest.period_end+" · "+latest.source_name+
     " · "+latest.report_status+" · not live";
   }
  }
  root.textContent="Provider values are read from private verified imports. Not connected means no authorized report source. Reload after a confirmed import.";
 }catch{
  root.textContent="Private provider reporting is unavailable. No earnings have been inferred.";
 }
}
load();
})();

