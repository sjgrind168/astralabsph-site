(()=>{
  "use strict";
  const $=id=>document.getElementById(id);
  const status=$("amzReportStatus");
  if(!status)return;
  const C=window.PIREVO_CONFIG||{};
  let token="";
  try{token=localStorage.getItem("pirevo_analytics_access")||""}catch{}
  if(!token||!C.analyticsDbUrl||!C.analyticsAnonKey){
    status.textContent="Verified Amazon report unavailable: unlock the private PIREVO dashboard.";
    return;
  }
  const number=n=>(n===null||n===undefined)?"—":Number(n).toLocaleString("en-US");
  const money=n=>(n===null||n===undefined)?"—":new Intl.NumberFormat("en-US",{style:"currency",currency:"USD"}).format(Number(n));
  const prettyDate=s=>{
    if(!s)return"Unknown";
    const p=String(s).split("-");
    if(p.length!==3)return s;
    const d=new Date(Date.UTC(Number(p[0]),Number(p[1])-1,Number(p[2])));
    return d.toLocaleDateString("en-US",{month:"short",day:"numeric",year:"numeric",timeZone:"UTC"});
  };
  async function refresh(){
    try{
      const resp=await fetch(C.analyticsDbUrl+"/rest/v1/rpc/pirevo_amazon_earnings_snapshot",{
        method:"POST",cache:"no-store",
        headers:{apikey:C.analyticsAnonKey,Authorization:"Bearer "+C.analyticsAnonKey,"Content-Type":"application/json"},
        body:JSON.stringify({p_token:token})
      });
      if(!resp.ok)throw new Error("private report unavailable");
      const data=await resp.json(),month=data?.month_to_date,days=data?.last_30_days;
      if(!month&&!days){status.textContent="No verified Amazon report imported yet.";return}
      $("amzEarnMonth").textContent=money(month?.earnings_usd);
      $("amzEarn30").textContent=money(days?.earnings_usd);
      $("amzClicksMonth").textContent=number(month?.clicks);
      $("amzClicks30").textContent=number(days?.clicks);
      $("amzOrdersMonth").textContent=number(month?.ordered_items);
      const latest=month?.reported_through||days?.reported_through;
      status.textContent="Amazon Associates Central · last verified report: "+prettyDate(latest)+" · manual snapshot (not auto-synced)";
    }catch{
      status.textContent="Amazon report sync unavailable. Other PIREVO analytics are unaffected.";
    }
  }
  refresh();
})();
