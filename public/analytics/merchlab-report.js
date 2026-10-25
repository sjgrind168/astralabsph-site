/* Owner-passkey-only MerchLab funnel report. Receives only the protected RPC snapshot. */
(()=>{
"use strict";
const $=id=>document.getElementById(id);
const format=n=>n==null||!Number.isFinite(Number(n))?"—":new Intl.NumberFormat("en-PH").format(Number(n));
const value=(id,n)=>{const e=$(id);if(e)e.textContent=format(n);};
const replaceRows=(id,items,cols,blank)=>{
 const target=$(id);if(!target)return;target.replaceChildren();
 if(!items?.length){const tr=document.createElement("tr"),td=document.createElement("td");td.colSpan=cols.length;td.className="muted";td.textContent=blank;tr.append(td);target.append(tr);return;}
 for(const item of items){const tr=document.createElement("tr");for(const c of cols){const td=document.createElement("td");const entry=c(item);if(entry instanceof Node)td.append(entry);else td.textContent=String(entry??"—");tr.append(td);}target.append(tr);}
};
const productLink=p=>{
 const id=String(p.product_id||"");if(!/^\d{5,18}$/.test(id))return id;
 const a=document.createElement("a");a.href="/merchlab/p/"+encodeURIComponent(id)+"/";a.target="_blank";a.rel="noopener noreferrer";a.textContent="Item "+id+" ↗";return a;
};
function render(data){
 const note=$("mlSourceStatus");
 if(!note)return;
 if(!data||typeof data!=="object"||!data.kpis){
  note.textContent="MerchLab reporting unavailable. The dashboard will not replace missing data with zero.";
  for(const name of ["Visitors","Sessions","Views","ProductViews","CartAdds","Outbounds","BagViews","Searches"])value("ml"+name,null);
  for(const key of ["mlDays","mlProducts","mlSources","mlSearches"])replaceRows(key,[],[x=>x], "Report unavailable");
  return;
 }
 const k=data.kpis;
 for(const [id,field] of [["Visitors","visitors"],["Sessions","sessions"],["Views","page_views"],["ProductViews","product_views"],["CartAdds","add_to_bag"],["Outbounds","outbound_shopee"],["BagViews","bag_views"],["Searches","searches"]])value("ml"+id,k[field]);
 note.textContent="Tracked events only · "+data.period_days+" calendar days (Asia/Manila) · First event: "+(data.first_event?new Date(data.first_event).toLocaleDateString("en-PH",{timeZone:"Asia/Manila"}):"none yet")+" · Orders and sales not available";
 const ratio=$("mlCTR");
 if(ratio){const a=Number(k.product_views)||0,o=Number(k.outbound_shopee)||0;ratio.textContent=a?((o/a)*100).toFixed(1)+"%":"—";}
 const dayRows=(data.daily||[]).slice().reverse();
 replaceRows("mlDays",dayRows,[x=>x.day,x=>format(x.visitors),x=>format(x.sessions),x=>format(x.page_views),x=>format(x.product_views),x=>format(x.add_to_bag),x=>format(x.outbound_shopee)],"No events in this window");
 replaceRows("mlProducts",data.top_products,[productLink,x=>format(x.product_views),x=>format(x.add_to_bag),x=>format(x.shopee_clicks)],"No product activity yet");
 replaceRows("mlSources",data.sources,[x=>x.source,x=>format(x.sessions),x=>format(x.page_views)],"No referrer information yet");
 replaceRows("mlSearchTerms",data.search_terms,[x=>x.search_term,x=>format(x.searches)],"No on-site searches yet");
 const chart=$("mlDailyBars");
 if(chart){
  chart.replaceChildren();
  const max=Math.max(1,...dayRows.map(x=>Number(x.page_views)||0));
  for(const d of dayRows){
   const row=document.createElement("div");row.className="ml-bar-row";
   const date=document.createElement("span");date.textContent=d.day.slice(5);
   const track=document.createElement("div");track.className="ml-bar-track";
   const fill=document.createElement("span");fill.className="ml-bar-fill";fill.style.width=(Number(d.page_views||0)/max*100)+"%";
   const count=document.createElement("strong");count.textContent=format(d.page_views);
   track.append(fill);row.append(date,track,count);chart.append(row);
  }
  if(!dayRows.length){const p=document.createElement("p");p.className="empty";p.textContent="Daily visitor activity will appear after tracking begins.";chart.append(p);}
 }
}
window.MERCHLAB_REPORT={render};
})();