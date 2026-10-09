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
  const referrals=document.getElementById("kdpBookReferrals");
  if(referrals)referrals.textContent=Number.isFinite(Number(data.book_referrals_7d))?
    new Intl.NumberFormat("en-US").format(Number(data.book_referrals_7d)):"—";
  const status=new Map((data.sources||[]).map(s=>[s.provider,s.status]));
  const metrics=data.metrics||[];
  const specific=(provider,metric,app)=>
    metrics.find(x=>x.provider===provider&&x.metric===metric&&x.app_key===app);
  const bothApps=(metric)=>{
    const a=specific("google_play",metric,"astramate");
    const k=specific("google_play",metric,"keepry");
    if(!a||!k)return null;
    return {...a,metric_value:Number(a.metric_value)+Number(k.metric_value)};
  };
  for(const card of document.querySelectorAll(".platform-card")){
   const provider=card.dataset.provider,s=status.get(provider)||"not_connected";
   const badge=card.querySelector(".platform-status");
   badge.textContent=s==="not_connected"?"Awaiting report":"Verified snapshot";
   badge.classList.toggle("live",s!=="not_connected");
   for(const m of card.querySelectorAll("[data-metric]")){
    let chosen=null;
    if(provider==="google_play"&&(m.dataset.metric==="installed_audience"||m.dataset.metric==="device_acquisitions")){
      chosen=bothApps(m.dataset.metric);
    }else if(provider==="google_play"&&(m.dataset.metric==="gross_revenue_usd"||m.dataset.metric==="one_time_orders")){
      chosen=specific(provider,m.dataset.metric,"keepry");
    }else{
      chosen=specific(provider,m.dataset.metric,"all");
    }
    m.textContent=amount(chosen);
   }
   const available=metrics.filter(x=>x.provider===provider);
   if(available.length){
    const latest=available.reduce((a,b)=>!a||b.captured_at>a.captured_at?b:a,null);
    card.querySelector("[data-source-note]").textContent=
      provider==="google_play"?
      "Verified Oct 9: $3.98 September earnings balance, pending scheduled payout (Google normally initiates around Oct 15). Keepry gross $4.79 includes tax, less $0.72 fees and $0.09 VAT. Astramate: 7 installed, 10 acquisitions; Keepry: 8 installed, 16 acquisitions. Manual snapshots only.":
      provider==="admob"?
      "Estimates: Oct month-to-date $0.00; Sept ~$0.01 (unrounded $0.008). Impressions are for last 7 days. Not finalized payouts.":
      "Imported snapshot dated "+latest.period_end+" · "+latest.source_name+" · not automatically synced.";
   }
  }
  root.textContent="Last reviewed Oct 9, 2026 · Google Play & AdMob are verified manual snapshots, not continuous API connections. Apple & KDP financial imports are still pending.";
 }catch{
  root.textContent="Private provider reporting is unavailable. No earnings have been inferred.";
 }
}
load();
})();

