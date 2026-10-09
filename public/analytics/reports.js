(()=>{
"use strict";
const $=s=>document.getElementById(s);
const fmt=n=>n==null||!Number.isFinite(Number(n))?"—":Number(n).toLocaleString("en-US",{maximumFractionDigits:0});
const usd=n=>n==null||!Number.isFinite(Number(n))?"—":new Intl.NumberFormat("en-US",{style:"currency",currency:"USD"}).format(Number(n));
const date=d=>d?String(d).slice(0,10):"not available";
const count=(days,key)=>days.reduce((a,d)=>a+Number(d[key]||0),0);
const add=(tag,text,cls)=>{const x=document.createElement(tag);if(text!=null)x.textContent=String(text);if(cls)x.className=cls;return x};
const sourceMetric=(state,provider,metric,app="all")=>(state.platforms?.metrics||[]).find(x=>x.provider===provider&&x.metric===metric&&x.app_key===app)||null;
const value=(state,p,m,app="all")=>{const r=sourceMetric(state,p,m,app);return r?.metric_value==null?null:Number(r.metric_value)};
const srcStatus=(state,provider)=>state.platforms?.sources?.find(x=>x.provider===provider)?.status==="imported"?"Verified snapshot":"Awaiting import";
let selected="all",trends=null,lastReport=null,lastTrendState=null;
const linksOnly=(p)=>{
 const x=document.createElement("a");
 if(p.slug&&/^[-a-z0-9]+$/.test(p.slug)){x.href="/pirevo/products/"+p.slug+"/index.html";x.textContent="Open PIREVO product ↗";return x}
 x.href=p.sources?.[0]?.url||"https://trends.pinterest.com/";
 x.target="_blank";x.rel="noopener noreferrer";x.textContent="Research source ↗";return x;
};
function trendPaint(){
 const summary=$("reportTrendSummary"),root=$("reportTrendCards"),mini=$("pirevoRadarMini");
 if(!root||!mini)return;
 if(!trends){summary.textContent="Trend research could not be loaded. This is not a live trend feed.";return}
 const all=trends.products||[];
 const listed=all.filter(x=>x.status==="in_catalog"),research=all.filter(x=>x.status==="research_queue");
 summary.textContent="Reviewed "+trends.reviewed_at+" · "+listed.length+" matched rated catalog products · "+research.length+" candidates awaiting Amazon validation · Threads/YouTube/Facebook product evidence not yet imported.";
 $("reportSocialMatches").textContent=fmt(listed.length);
 root.replaceChildren();
 const show=all.filter(p=>selected==="all"||p.status===selected);
 for(const item of show){
  const card=add("article",null,"report-trend-card");
  const tags=add("div",null,"report-trend-meta");
  for(const platform of item.platforms||[])tags.append(add("span",platform));
  tags.append(add("span",item.status==="in_catalog"?"Live in catalog · Amazon snapshot":"Research queue · Amazon unverified",item.status==="in_catalog"?"":"research"));
  card.append(tags,add("h3",item.name));
  if(item.status==="in_catalog")card.append(add("p","Amazon "+Number(item.rating).toFixed(1)+"★ · "+Number(item.reviews).toLocaleString("en-US")+" reviews · "+item.rating_reviewed_at+" snapshot"));
  card.append(add("p",item.signal));
  card.append(add("p","Trend evidence: "+(item.scope==="product"?"Exact product discussed":"Brand/category-level match, not exact product social sales")));
  const row=add("div");row.append(linksOnly(item));
  for(const source of (item.sources||[]).slice(0,2)){
   const link=add("a","Evidence ↗");link.href=source.url;link.target="_blank";link.rel="noopener noreferrer";link.title=source.title;row.append(link)
  }
  card.append(row);root.append(card);
 }
 mini.replaceChildren();
 for(const item of listed.slice(0,5)){
  const row=add("div",null,"report-mini-item"),name=add("strong",item.name),hint=add("span",Number(item.rating).toFixed(1)+"★ · "+item.platforms.join(" + "));
  row.append(name,hint);mini.append(row)
 }
}
function tableRow(cells){
 const tr=document.createElement("tr");
 for(const s of cells){const td=add("td",s);tr.append(td)}
 return tr
}
function block(id,text){
 const n=$(id);if(n)n.textContent=text;
}
function metrics(state){
 const days=state.daily?.days||[],hasDays=!!state.daily,k=state.base?.kpis||{},site=state.site?.astralabs||{},amz=state.amazon?.month_to_date;
 const playA=value(state,"google_play","device_acquisitions","astramate"),playK=value(state,"google_play","device_acquisitions","keepry"),gross=value(state,"google_play","gross_revenue_usd","keepry");
 const admob=value(state,"admob","estimated_earnings_usd");
 const kdp=value(state,"kdp","royalties_usd");
 const apple=value(state,"app_store_connect","proceeds_usd");
 return {
  days,hasDays,k,site,amz,playA,playK,gross,admob,kdp,apple,
  pSessions:k.sessions==null?null:Number(k.sessions),
  pViews:k.product_views==null?null:Number(k.product_views),
  pOutbound:k.amazon_clicks==null?null:Number(k.amazon_clicks),
  webSessions:site.sessions==null?null:Number(site.sessions),
  webViews:site.page_views==null?null:Number(site.page_views),
  storeClicks:site.store_clicks==null?null:Number(site.store_clicks),
  bookRef:hasDays?count(days,"book_clicks"):null,
  socialSessions:hasDays?count(days,"site_social_sessions")+count(days,"pirevo_social_sessions"):null,
  reportDate:new Date().toISOString()
 }
}
function createScorecard(state,m){
 const last=d=>d?date(d):"Not imported",status=p=>srcStatus(state,p);
 return [
  {channel:"Mobile apps · Google Play",performance:usd(m.gross)+" gross Keepry; "+(m.playA==null||m.playK==null?"—":fmt(m.playA+m.playK))+" acquired devices",source:"Play Console · gross through "+last(sourceMetric(state,"google_play","gross_revenue_usd","keepry")?.period_end)+"; acquisitions in a separate 28-day period",status:status("google_play")},
  {channel:"Mobile apps · App Store",performance:usd(m.apple)+" proceeds",source:"Apple financial report",status:status("app_store_connect")},
  {channel:"PIREVO affiliate",performance:fmt(m.pSessions)+" sessions; "+fmt(m.pOutbound)+" Amazon outbound; "+(m.amz?usd(m.amz.earnings_usd)+" commission":"— affiliate commission"),source:"First-party events for selected period; Amazon Associates account-level snapshot",status:state.base?"Website live + earnings snapshot":"Awaiting events"},
  {channel:"Digital products · KDP",performance:usd(m.kdp)+" royalties; "+fmt(m.bookRef)+" referrals",source:"KDP royalty report (not imported); PIREVO book-referral events",status:status("kdp")},
  {channel:"AstraLabs website",performance:fmt(m.webSessions)+" sessions; "+fmt(m.webViews)+" page views; "+fmt(m.storeClicks)+" store clicks",source:"First-party events · selected period",status:state.site?"Tracked":"Awaiting events"},
  {channel:"AdMob",performance:usd(m.admob)+" estimated earnings",source:"AdMob snapshot, period "+last(sourceMetric(state,"admob","estimated_earnings_usd")?.period_end),status:status("admob")},
  {channel:"Socials",performance:fmt(m.socialSessions)+" attributed web sessions; native impressions —",source:"First-party referrals; social network impressions not connected",status:"Native metrics awaiting import"}
 ];
}
function recommendations(state,m){
 const list=[],addItem=(id,area,title,evidence,test,success,urgency)=>list.push({id,area,title,evidence,test,success,urgency});
 if(m.pOutbound!=null&&m.pViews!=null){
  addItem("pirevo-conversion","PIREVO",m.pViews<20?"Build a trustworthy PIREVO conversion baseline":"Improve PIREVO product-to-Amazon clicks",
   fmt(m.pViews)+" tracked product views and "+fmt(m.pOutbound)+" Amazon outbound clicks for the chosen window. "+(m.pViews<20?"Small sample: no reliable winning product yet.":"This is an outbound-interest metric, not purchases."),
   "Improve one product-page headline, feature summary and retailer CTA, then compare a matched period.", "Amazon outbound clicks per product view; qualifying commissions separately.", "High");
 }else addItem("pirevo-attribution","PIREVO","Restore product funnel measurement","PIREVO product views or Amazon outbound metrics are unavailable.","Check event collection and QA exclusion before optimizing creative.","Accurately counted product views and Amazon outbound clicks.","High");
 if(m.playA!=null&&m.playK!=null) addItem("app-activation","Mobile apps","Review app discovery and first-launch onboarding",
  "Play acquired devices: Astramate "+fmt(m.playA)+", Keepry "+fmt(m.playK)+" in the imported reporting window. First opens and monthly active audience must be assessed separately.",
  "Review app listing screenshots and first-run setup; test one onboarding change per app.", "Device first opens, active devices, store conversion and premium purchases over comparable time windows.", "High");
 if(m.storeClicks!=null) addItem("website-app-cta","Website","Increase qualified app-store referrals",
  fmt(m.webSessions)+" AstraLabs sessions and "+fmt(m.storeClicks)+" store-button clicks in the selected period.",
  "Test a clearer app benefit headline and a more prominent Google Play / App Store CTA on the highest-traffic app page.",
  "App store button clicks per app page view; actual installs from store reports.", "Medium");
 if(m.socialSessions!=null) addItem("social-attribution","Socials","Grow measured social traffic, not vanity views",
  fmt(m.socialSessions)+" website sessions attributed to social sources in the selected period. Native TikTok, Instagram, Threads and Pinterest metrics are still unimported.",
  "Post one measured creative variation per platform with unique UTM links; connect approved social analytics where available.",
  "Native outbound clicks and correctly attributed site sessions; then retailer interest.", "High");
 addItem("trend-validation","PIREVO Trends","Validate new social products before publishing",
  trends?(trends.products||[]).filter(x=>x.status==="research_queue").length+" candidate products need exact Amazon ASIN/rating checks. "+(trends.products||[]).filter(x=>x.status==="in_catalog").length+" catalog products already match social-shopping topics.":"Social trends are in the editorial queue; verification data is loading.",
  "Prioritize 4.5★+ well-reviewed exact Amazon variants, avoid duplicates, publish only source-backed matches and compare product clicks.",
  "Number of verified new listings and qualified outbound clicks per product view.", "High");
 if(m.admob!=null) addItem("admob-quality","AdMob","Grow ad requests via real app activity",
  usd(m.admob)+" AdMob estimate in the imported month-to-date window. Limited reported impressions should not be interpreted as an eCPM or payout trend.",
  "Increase app usage and instrument ad match rate/eCPM before testing ad placement changes.",
  "Matched requests, impressions, estimated earnings and retention by app.", "Medium");
 if(m.kdp==null)addItem("kdp-reporting","Digital products","Import KDP royalty and title-level unit reports",
  fmt(m.bookRef)+" tracked book referrals, but royalty data is not imported. Referrals are not book sales.",
  "Import royalty reports and create one content test for the published Timmy ebook.", "Reported paid units and royalties by title and traffic source where supported.", "Medium");
 if(m.apple==null)addItem("apple-reporting","Mobile apps","Connect App Store sales and acquisition reporting",
  "iOS proceeds and first-time downloads cannot be verified from the current imported dataset.",
  "Authorize Apple reports, then examine listing conversion and retention before making app-store claims.",
  "Verified Apple downloads, product-page views and proceeds.", "Medium");
 return list;
}
function savedStatus(id){try{return JSON.parse(localStorage.getItem("astralabs_experiment_status_v1")||"{}")[id]||"Proposed"}catch{return"Proposed"}}
function setStatus(id,val){try{const all=JSON.parse(localStorage.getItem("astralabs_experiment_status_v1")||"{}");all[id]=val;localStorage.setItem("astralabs_experiment_status_v1",JSON.stringify(all))}catch{}}
function paintRecommendations(items){
 const root=$("reportRecommendations");if(!root)return;root.replaceChildren();
 for(const [i,x] of items.entries()){
  const article=add("article",null,"report-reco"),head=add("div",null,"report-reco-head");
  head.append(add("h3",(i+1)+". "+x.title),add("span",x.urgency+" priority","report-reco-tag"));
  article.append(head,add("p","Source: "+x.area+" · "+x.evidence),add("p","Experiment: "+x.test));
  article.append(add("div","Measure: "+x.success,"report-success"));
  const label=add("label","Experiment status (stored in this browser)");
  const select=add("select");select.setAttribute("aria-label","Status for "+x.title);
  for(const v of ["Proposed","In progress","Completed","On hold"]){const option=add("option",v);option.value=v;select.append(option)}
  select.value=savedStatus(x.id);select.addEventListener("change",()=>setStatus(x.id,select.value));label.append(select);article.append(label);root.append(article);
 }
}

function campaignUrl(item,source){
 const content=item.slug.toLowerCase().replace(/[^a-z0-9-]/g,"").slice(0,100);
 const url=new URL("/pirevo/products/"+encodeURIComponent(content)+"/","https://www.astralabsph.com");
 url.searchParams.set("utm_source",source);
 url.searchParams.set("utm_medium","organic_social");
 url.searchParams.set("utm_campaign","pirevo_trend_test_202610");
 url.searchParams.set("utm_content",content);
 return url.toString();
}
async function copyCampaign(btn,url){
 try{await navigator.clipboard.writeText(url);btn.textContent="Copied";setTimeout(()=>{btn.textContent="Copy URL"},1800)}
 catch{window.prompt("Copy this tracked PIREVO link:",url)}
}
function paintTrendFunnel(state){
 const tbody=$("rTrendFunnelRows");if(!tbody)return;
 tbody.replaceChildren();
 const report=state.trendPerformance;
 if(!report){
  block("rTrendFunnelPeriod","No authorized product-level report available. Check the private reporting connection.");
  tbody.append(tableRow(["Trend performance unavailable","—","—","—","—","—"]));
  ["rTrendProductViews","rTrendAmazonClicks","rTrendTrackedProducts"].forEach(k=>block(k,"—"));
  return;
 }
 const listed=(trends?.products||[]).filter(x=>x.status==="in_catalog");
 const matched=new Map((report.products||[]).map(x=>[x.product_slug,x]));
 const list=listed.map(item=>({...item,...(matched.get(item.slug)||{})}));
 list.sort((a,b)=>(Number(b.amazon_outbounds||0)-Number(a.amazon_outbounds||0))||(Number(b.product_views||0)-Number(a.product_views||0))||(Number(b.product_card_clicks||0)-Number(a.product_card_clicks||0))||a.name.localeCompare(b.name));
 const views=list.reduce((n,p)=>n+Number(p.product_views||0),0);
 const clicks=list.reduce((n,p)=>n+Number(p.amazon_outbounds||0),0);
 const active=list.filter(p=>Number(p.product_views||0)+Number(p.product_card_clicks||0)+Number(p.amazon_outbounds||0)>0).length;
 block("rTrendProductViews",fmt(views));block("rTrendAmazonClicks",fmt(clicks));block("rTrendTrackedProducts",fmt(active));
 block("rTrendFunnelPeriod",fmt(list.length)+" vetted Trends products · "+date(report.window_start)+" to "+date(report.window_end)+" · events tracked in Asia/Manila · source: PIREVO first-party analytics");
 if(!list.length){tbody.append(tableRow(["Trend source loading","—","—","—","—","—"]));return}
 // Rank active products first, then show a practical 15-product launch shortlist.
 for(const item of list){
  const tr=document.createElement("tr");
  const td=add("td");const a=add("a",item.name);a.href="/pirevo/products/"+encodeURIComponent(item.slug)+"/";a.target="_blank";a.rel="noopener noreferrer";td.append(a);tr.append(td);
  const v=Number(item.product_views||0),c=Number(item.amazon_outbounds||0);
  for(const value of [v,Number(item.product_card_clicks||0),c])tr.append(add("td",fmt(value)));
  tr.append(add("td",v>0?(100*c/v).toFixed(1)+"%":"—"));
  const linktd=add("td");
  const btn=add("button","Copy URL","report-copy-link");btn.type="button";
  btn.title="Copy tracked Pinterest campaign URL for this exact product page";
  btn.addEventListener("click",()=>copyCampaign(btn,campaignUrl(item,"pinterest")));
  linktd.append(btn);tr.append(linktd);tbody.append(tr);
 }
 if(lastReport)lastReport.trend_product_performance=report.products||[];
}

function render(state){
 lastTrendState={trendPerformance:state.trendPerformance};
 const m=metrics(state),score=createScorecard(state,m),next=recommendations(state,m),captured=new Date().toISOString();
 lastReport={generated_at:captured,timezone:"Asia/Manila",first_party_reporting_window:state.daily?{start:state.daily.window_start,end:state.daily.window_end,days:state.period}:null,
  definitions:{sessions:"first-party visits; not deduplicated across AstraLabs and PIREVO",outbound_clicks:"not purchases",financial:"provider reporting periods differ; do not add gross sales, pending payout and estimated revenue"},
  scorecard:score,recommendations:next.map(x=>({...x,status:savedStatus(x.id)})),
  latest_provider_metrics:(state.platforms?.metrics||[]).map(x=>({provider:x.provider,app:x.app_key,metric:x.metric,value:x.metric_value,unit:x.metric_unit,period_start:x.period_start,period_end:x.period_end,source:x.source_name,captured_at:x.captured_at})),
  amazon_verified_report:state.amazon?.month_to_date||null,
  selected_period_daily_events:(state.daily?.days||[]),trend_product_performance:state.trendPerformance?.products||null,trend_research:trends?{reviewed_at:trends.reviewed_at,products:trends.products}:null};
 block("reportPirevoSessions",fmt(m.pSessions));block("reportSiteSessions",fmt(m.webSessions));
 block("reportAmazonAcctClicks",m.amz?fmt(m.amz.clicks):"—");
 block("reportAmazonOrders",m.amz?.ordered_items==null?"—":fmt(m.amz.ordered_items));
 block("reportAmazonShipped",m.amz?.shipped_items==null?"—":fmt(m.amz.shipped_items));
 block("reportAmazonCommission",m.amz?usd(m.amz.earnings_usd):"—");
 block("reportAmazonSource",m.amz?
   "Amazon Associates account-wide report through "+date(m.amz.reported_through)+". This may include activity from other affiliate links and tracking IDs. Website click activity is separately measured and must not be treated as a checkout.":
   "Verified retailer orders unavailable. Do not infer Amazon purchases from PIREVO click events.");

 block("reportMeta","Report generated "+new Date(captured).toLocaleString("en-PH")+" · site events: "+(state.daily?date(state.daily.window_start)+" to "+date(state.daily.window_end):"unavailable")+" · separate financial source periods · no synthetic trends");
 const table=$("reportScorecard");if(table){table.replaceChildren();score.forEach(x=>table.append(tableRow([x.channel,x.performance,x.source,x.status])))}
 const source=$("reportSourceHealth");if(source){source.replaceChildren();for(const [n,s] of [
  ["PIREVO tracker",state.base?"Tracking":"Unavailable"],["AstraLabs tracker",state.site?"Tracking":"Unavailable"],["Google Play",srcStatus(state,"google_play")],
  ["AdMob",srcStatus(state,"admob")],["Amazon Associates",state.amazon?"Verified report":"Awaiting report"],
  ["Apple",srcStatus(state,"app_store_connect")],["KDP",srcStatus(state,"kdp")],["Native social insights","Awaiting authorized metrics"]
 ]){const row=add("div",null,"report-source-row");row.append(add("strong",n),add("span",s));source.append(row)}}
 paintRecommendations(next);trendPaint();paintTrendFunnel(state);
}
function download(name,type,body){
 const blob=new Blob([body],{type});const url=URL.createObjectURL(blob),a=document.createElement("a");a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);
}
function exportJSON(){
 if(!lastReport)return;
 // Explicitly omit the access token and individual visitor/session identifiers.
 lastReport.recommendations=lastReport.recommendations.map(x=>({...x,status:savedStatus(x.id)}));
 download("AstraLabs_PH_Performance_Report_"+new Date().toISOString().slice(0,10)+".json","application/json",JSON.stringify(lastReport,null,2));
}
function exportCSV(){
 if(!lastReport)return;
 const protect=v=>{let s=String(v??"");if(/^[=+\-@\t\r]/.test(s))s="'"+s;return '"'+s.replaceAll('"','""')+'"'};
 const columns=["channel","performance","source","status"];
 const data=[columns.join(","),...lastReport.scorecard.map(x=>columns.map(k=>protect(x[k])).join(","))];
 download("AstraLabs_PH_Scorecard_"+new Date().toISOString().slice(0,10)+".csv","text/csv;charset=utf-8","\ufeff"+data.join("\r\n"));
}
async function init(){
 $("reportExport")?.addEventListener("click",exportJSON);
 $("reportExportCSV")?.addEventListener("click",exportCSV);
 document.querySelectorAll("[data-report-trend]").forEach(btn=>btn.addEventListener("click",()=>{
  selected=btn.dataset.reportTrend;
  document.querySelectorAll("[data-report-trend]").forEach(other=>other.setAttribute("aria-pressed",String(other===btn)));
  trendPaint();
 }));
 try{
  const r=await fetch("/pirevo/social-trend-research.json",{cache:"no-store"});
  if(!r.ok)throw Error("research unavailable");
  trends=await r.json();
  trendPaint();
  if(lastReport){lastReport.trend_research={reviewed_at:trends.reviewed_at,products:trends.products}}
  if(lastTrendState)paintTrendFunnel(lastTrendState);
 }catch{trendPaint()}
}
window.ASTRA_REPORTS={init,render};
})();