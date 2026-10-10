
(()=>{
"use strict";
const P=["overview","mobile","pirevo","digital","website","admob","socials","reports"];
const SOCIAL=["all","tiktok","facebook","youtube","instagram","threads","pinterest"];
const C=window.PIREVO_CONFIG||{};
const q=s=>document.querySelector(s), qa=s=>[...document.querySelectorAll(s)], id=s=>document.getElementById(s);
const state={overviewFocus:"sessions",token:"",period:7,compare:false,tab:"overview",platform:"google_play",app:"all",social:"all",base:null,site:null,platforms:null,amazon:null,daily:null,previous:null,trendPerformance:null,kdpSync:null,seq:0};
const fm=n=>n==null||!Number.isFinite(Number(n))?"—":new Intl.NumberFormat("en-US",{maximumFractionDigits:0}).format(Number(n));
const usd=n=>n==null||!Number.isFinite(Number(n))?"—":new Intl.NumberFormat("en-US",{style:"currency",currency:"USD"}).format(Number(n));
const roundedApple=n=>n==null||!Number.isFinite(Number(n))?"—":"≈"+new Intl.NumberFormat("en-US",{style:"currency",currency:"USD",maximumFractionDigits:0}).format(Number(n));
const percent=n=>n==null||!Number.isFinite(Number(n))?"—":Number(n).toFixed(1).replace(/\.0$/,"")+"%";
const clean=s=>String(s??"");
const datePretty=s=>{if(!s)return"Not yet reported";const d=new Date(String(s).slice(0,10)+"T12:00:00Z");return Number.isNaN(d.getTime())?s:d.toLocaleDateString("en-US",{month:"short",day:"numeric",year:"numeric",timeZone:"UTC"})};
const set=(key,value)=>qa('[data-v="'+key+'"]').forEach(e=>{e.textContent=value;if(e.dataset.earning==="true")e.dataset.amountPresent=String(value)!=="—"?"true":"false"});
const note=(key,value)=>qa('[data-note="'+key+'"]').forEach(e=>e.textContent=value);
const empty=(node,message)=>{if(!node)return;node.replaceChildren();const p=document.createElement("div");p.className="empty";p.textContent=message;node.append(p)};
const cell=(tr,value,klass)=>{const td=document.createElement("td");td.textContent=value; if(klass)td.className=klass;tr.append(td)};
const rows=(table,data,columns)=>{const body=id(table);if(!body)return;body.replaceChildren();if(!data?.length){const tr=document.createElement("tr");const td=document.createElement("td");td.colSpan=columns.length;td.className="muted";td.textContent="No verified records for this period.";tr.append(td);body.append(tr);return}
 for(const r of data){const tr=document.createElement("tr");for(const c of columns){const val=typeof c==="function"?c(r):r[c];cell(tr,val==null?"—":String(val),typeof c==="function"?"number":"")}body.append(tr)}
};
async function rpc(name,args){
 if(!C.analyticsDbUrl||!C.analyticsAnonKey)throw Error("Analytics connection unavailable");
 const res=await fetch(C.analyticsDbUrl+"/rest/v1/rpc/"+name,{
  method:"POST",cache:"no-store",
  headers:{"apikey":C.analyticsAnonKey,"Authorization":"Bearer "+C.analyticsAnonKey,"Content-Type":"application/json"},
  body:JSON.stringify(args)
 });
 if(!res.ok)throw Error(res.status===401||res.status===403?"Invalid dashboard access":"Source "+name+" unavailable");
 return res.json();
}
function launch(token){
 state.token=token;
 const stored=new URL(location.href);
 stored.hash="";
 history.replaceState(null,"",stored.pathname+stored.search);
 try{localStorage.setItem("pirevo_analytics_access",token)}catch{}
 id("locked").hidden=true;id("dashboard").hidden=false;
 load();
}
async function authorize(t){
 id("lockError").textContent="Checking private dashboard access…";
 try{await rpc("pirevo_dashboard_snapshot",{p_days:7,p_token:t});
  id("lockError").textContent="";launch(t);
 }catch(e){id("lockError").textContent="Unable to verify access. Check the private dashboard code."}
}
function initialize(){
 const params=new URLSearchParams(location.hash.replace(/^#/,""));
 const fromUrl=params.get("access");
 let saved="";
 try{saved=localStorage.getItem("pirevo_analytics_access")||""}catch{}
 const qs=new URLSearchParams(location.search);
 state.tab=P.includes(qs.get("tab"))?qs.get("tab"):"overview";
 id("unlockForm").addEventListener("submit",e=>{e.preventDefault();const t=id("accessCode").value.trim();if(t)authorize(t)});
 qa("[data-tab]").forEach((btn,index,arr)=>{
  btn.addEventListener("click",()=>showTab(btn.dataset.tab,true));
  btn.addEventListener("keydown",e=>{
   const step=(e.key==="ArrowRight"||e.key==="ArrowDown")?1:(e.key==="ArrowLeft"||e.key==="ArrowUp")?-1:0;
   if(!step&&e.key!=="Home"&&e.key!=="End")return;
   e.preventDefault();
   const target=e.key==="Home"?0:e.key==="End"?arr.length-1:(index+step+arr.length)%arr.length;
   arr[target].click();arr[target].focus();
  });
 });
 id("period").addEventListener("change",e=>{state.period=Number(e.target.value)||7;load()});
 id("compare").addEventListener("change",e=>{state.compare=e.target.checked;load()});
 id("refresh").addEventListener("click",()=>load());
 qa("[data-platform]").forEach(b=>b.addEventListener("click",()=>{state.platform=b.dataset.platform;paintPlatform()}));
 qa("[data-app]").forEach(b=>b.addEventListener("click",()=>{state.app=b.dataset.app;paintPlatform()}));
 qa("[data-social]").forEach(b=>b.addEventListener("click",()=>{state.social=b.dataset.social;paintSocial()}));
 id("openReportsFromPirevo")?.addEventListener("click",()=>showTab("reports",true));
 window.ASTRA_REPORTS?.init();
 qa("[data-overview-focus], [data-overview-chart]").forEach(b=>b.addEventListener("click",()=>{
  const value=b.dataset.overviewFocus||b.dataset.overviewChart;
  if(!["sessions","views","amazon","store"].includes(value))return;
  state.overviewFocus=value;renderGAOverviewTrend();
 }));
 qa("[data-report-jump]").forEach(b=>b.addEventListener("click",e=>{
  e.preventDefault();showTab(b.dataset.reportJump,true);
 }));
 showTab(state.tab,false);
 const candidate=fromUrl||saved;
 if(candidate)authorize(candidate);else{id("locked").hidden=false;id("dashboard").hidden=true}
}
function showTab(name,historyPush){
 if(!P.includes(name))name="overview";
 state.tab=name;
 qa("[data-tab]").forEach(b=>{const selected=b.dataset.tab===name;b.setAttribute("aria-selected",String(selected));b.tabIndex=selected?0:-1});
 qa(".tabpanel").forEach(p=>p.hidden=p.dataset.panel!==name);
 const titles={overview:"Portfolio overview",mobile:"Mobile apps",pirevo:"Pirevo marketplace",digital:"Digital products",website:"AstraLabs website",admob:"AdMob advertising",socials:"Social channels",reports:"Performance reports"};
 id("pageTitle").textContent=titles[name];
 id("pageDescription").textContent={
  overview:"Your earnings, audience and business momentum in one place.",
  mobile:"Google Play and App Store performance, by application.",
  pirevo:"From marketplace discovery to Amazon affiliate activity.",
  digital:"Original books, publishing royalties and future digital products.",
  website:"Visitors, page engagement, app referrals and search visibility.",
  admob:"Advertising impressions, revenue estimates and monetization health.",
  socials:"Content performance, referral traffic and audience opportunities.",
  reports:"Cross-business performance scorecard, verified trends and measurable optimization plans."
 }[name];
 document.title=titles[name]+" | AstraLabs PH Analytics";
 if(historyPush){const u=new URL(location.href);u.searchParams.set("tab",name);history.replaceState(null,"",u.pathname+u.search)}
 window.scrollTo({top:0,behavior:"instant"});
}
function metric(provider,metricName,app="all"){
 return(state.platforms?.metrics||[]).find(x=>x.provider===provider&&x.metric===metricName&&x.app_key===app)||null;
}
function m(provider,name,app="all"){const x=metric(provider,name,app);return x&&x.metric_value!==null?Number(x.metric_value):null}
function sourcePeriod(provider,name,app="all"){
 const x=metric(provider,name,app);return x?datePretty(x.period_start)+" – "+datePretty(x.period_end)+" · imported "+datePretty(x.captured_at):"Awaiting verified source";
}
function sourceStatus(provider){const x=(state.platforms?.sources||[]).find(v=>v.provider===provider);return x?.status==="imported"?"Verified snapshot":"Awaiting report"}
function dataset(){return state.daily?.days||[]}
function total(key){return dataset().reduce((a,b)=>a+Number(b[key]||0),0)}
const COLORS=["#006241","#7BB8A2","#C8A96B","#4E8B73"];
function svgEl(type,atts,content){
 const e=document.createElementNS("http://www.w3.org/2000/svg",type);
 for(const [k,v]of Object.entries(atts||{}))e.setAttribute(k,String(v));
 if(content!=null)e.textContent=String(content);
 return e;
}
function chart(target,series,options={}){
 const root=id(target);if(!root)return;
 root.replaceChildren();
 const data=dataset(),valid=series.filter(s=>s?.key);
 const limit=Math.max(0,...data.flatMap(row=>valid.map(s=>Math.max(0,Number(row[s.key])||0))));
 if(!data.length||limit<=0){
  empty(root,options.empty||"No tracked activity in this reporting window. Bars will appear as events are recorded.");
  return;
 }
 // Grouped vertical bars: one group per actual calendar date, one colored bar per source.
 // Empty or zero-value dates are preserved, never estimated or interpolated.
 const W=720,H=265,L=45,T=17,R=16,B=36,w=W-L-R,h=H-T-B,seriesCount=valid.length;
 const svg=svgEl("svg",{viewBox:"0 0 "+W+" "+H,role:"img","aria-label":options.title||"Daily activity bar chart"});
 const daySlot=w/data.length,groupWidth=Math.min(daySlot*.82,50),innerGap=seriesCount>1?Math.min(2,groupWidth*.09):0;
 const barWidth=Math.max(.75,(groupWidth-innerGap*(seriesCount-1))/seriesCount);
 const yAxisMax=Math.max(1,Math.ceil(limit/4)*4);
 const plotY=n=>T+h-Math.min(yAxisMax,Math.max(0,Number(n)||0))/yAxisMax*h;
 for(let tick=0;tick<=4;tick++){
  const fraction=tick/4,y=T+h-fraction*h;
  svg.append(svgEl("line",{x1:L,x2:W-R,y1:y,y2:y,class:"grid-line"}));
  svg.append(svgEl("text",{x:L-7,y:y+4,"text-anchor":"end",class:"axis-label"},fm(Math.round(yAxisMax*fraction))));
 }
 data.forEach((row,index)=>{
  const groupLeft=L+index*daySlot+(daySlot-groupWidth)/2;
  valid.forEach((s,j)=>{
   const n=Math.max(0,Number(row[s.key])||0),top=plotY(n),height=T+h-top;
   if(n<=0)return;
   const x=groupLeft+j*(barWidth+innerGap);
   const rect=svgEl("rect",{x:x.toFixed(2),y:top.toFixed(2),width:barWidth.toFixed(2),height:Math.max(1,height).toFixed(2),rx:Math.min(2,barWidth/3).toFixed(2),fill:s.color||COLORS[j%COLORS.length]});
   rect.append(svgEl("title",{},clean(row.date)+" · "+s.name+": "+fm(n)));
   svg.append(rect);
  });
 });
 const mid=Math.floor((data.length-1)/2);
 const indices=data.length<=7?[...data.keys()]:[0,mid,data.length-1];
 for(const index of [...new Set(indices)]){
  const cx=L+(index+.5)*daySlot;
  svg.append(svgEl("text",{x:cx,y:H-11,"text-anchor":"middle",class:"axis-label"},clean(data[index].date).slice(5)));
 }
 root.append(svg);
 const legend=document.createElement("div");legend.className="legend";
 for(const [i,s] of valid.entries()){
  const span=document.createElement("span"),mark=document.createElement("i");
  mark.style.background=s.color||COLORS[i%COLORS.length];
  span.append(mark,document.createTextNode(s.name));legend.append(span);
 }
 root.append(legend);
}
function barList(target,data,reason){
 const root=id(target);if(!root)return;root.replaceChildren();const valid=(data||[]).filter(x=>Number(x.value)>0).slice(0,8);
 if(!valid.length){empty(root,reason||"No matching report entries yet.");return}
 const mx=Math.max(...valid.map(x=>x.value),1);
 valid.forEach(x=>{
  const row=document.createElement("div");row.className="bar-row";
  const name=document.createElement("span");name.className="bar-name";name.textContent=x.name;name.title=x.name;
  const track=document.createElement("span");track.className="bar-track";
  const fill=document.createElement("span");fill.className="bar-fill";fill.style.width=(100*x.value/mx).toFixed(2)+"%";track.append(fill);
  const val=document.createElement("b");val.className="bar-val";val.textContent=fm(x.value);
  row.append(name,track,val);root.append(row)
 })
}
function reportBadge(node,textValue,ok){
 const el=id(node);if(!el)return;el.textContent=textValue;el.className="tag "+(ok?"":"off");
}
function stamp(){
 const site=state.daily;const time=new Date(site?.generated_at||Date.now());
 id("lastSync").textContent=site?.generated_at?"Website data checked "+time.toLocaleString("en-PH",{month:"short",day:"numeric",hour:"numeric",minute:"2-digit"}):"Source check pending";
 id("dateCaption").textContent="Website events · "+(site?datePretty(site.window_start)+" to "+datePretty(site.window_end):"Not available")+" · Asia/Manila";
 const ready=["base","site","platforms","amazon","daily"].filter(k=>state[k]).length;
 id("sourceHealth").textContent=ready+"/5 reporting sources accessible";
 id("sourceHealthDot").classList.toggle("live",ready>=3);
}
function renderSummary(){
 const k=state.base?.kpis||{},s=state.site?.astralabs||{},amz=state.amazon?.month_to_date;
 const installed=m("google_play","installed_audience","astramate"),keepry=m("google_play","installed_audience","keepry");
 set("playGross",usd(m("google_play","gross_revenue_usd","keepry")));
 set("playPending",usd(m("google_play","payout_balance_usd","all")));
 set("amazonMonth",amz?usd(amz.earnings_usd):"—");
 set("admobMTD",usd(m("admob","estimated_earnings_usd")));
 set("kdpRoyalty",usd(m("kdp","royalties_usd")));
 set("appleProceeds",roundedApple(m("app_store_connect","proceeds_usd")));
 set("siteSessions",s.sessions==null?"—":fm(s.sessions));
 set("siteViews",s.page_views==null?"—":fm(s.page_views));
 set("pirevoSessions",k.sessions==null?"—":fm(k.sessions));
 set("pirevoViews",fm(total("pirevo_views")));
 set("installedTotal",installed==null||keepry==null?"—":fm(installed+keepry));
 set("storeClicks",s.store_clicks==null?"—":fm(s.store_clicks));
 note("playGross",sourcePeriod("google_play","gross_revenue_usd","keepry")+" · gross including tax");
 note("playPending",sourcePeriod("google_play","payout_balance_usd")+" · not a new sale");
 note("amazonMonth",amz?"Report through "+datePretty(amz.reported_through)+" · all tracking IDs":"Awaiting verified report");
 note("admobMTD",sourcePeriod("admob","estimated_earnings_usd")+" · estimated");
 note("installedTotal",sourcePeriod("google_play","installed_audience","astramate"));
 note("kdpRoyalty",sourcePeriod("kdp","royalties_usd"));
 note("appleProceeds",sourcePeriod("app_store_connect","proceeds_usd"));
 note("socialReferrals","First-party referral sessions, not platform impressions");
 reportBadge("playSource",sourceStatus("google_play"),!!state.platforms?.metrics?.some(x=>x.provider==="google_play"));
 reportBadge("admobSource",sourceStatus("admob"),!!metric("admob","estimated_earnings_usd"));
 reportBadge("appleSource",sourceStatus("app_store_connect"),!!metric("app_store_connect","proceeds_usd"));
 reportBadge("kdpSource",sourceStatus("kdp"),!!metric("kdp","royalties_usd"));
}
function renderOverview(){
 renderGAOverviewTrend();
 barList("overviewApps",[
  {name:"Astramate",value:m("google_play","device_acquisitions","astramate")},
  {name:"Keepry",value:m("google_play","device_acquisitions","keepry")}
 ],"Google Play device acquisition comparison will display when verified.");
 rows("revenueRows",[
 {name:"Keepry Google Play",amt:usd(m("google_play","gross_revenue_usd","keepry")),kind:"Gross customer sales (not net)",period:sourcePeriod("google_play","gross_revenue_usd","keepry")},
 {name:"Google Play payments",amt:usd(m("google_play","payout_balance_usd")),kind:"Pending payout balance (not additional revenue)",period:sourcePeriod("google_play","payout_balance_usd")},
 {name:"Amazon Associates",amt:state.amazon?.month_to_date?usd(state.amazon.month_to_date.earnings_usd):"—",kind:"Affiliate earnings, account level",period:state.amazon?.month_to_date?"Through "+datePretty(state.amazon.month_to_date.reported_through):"Awaiting report"},
 {name:"AdMob",amt:usd(m("admob","estimated_earnings_usd")),kind:"Estimated advertising earnings",period:sourcePeriod("admob","estimated_earnings_usd")},
 {name:"KDP",amt:usd(m("kdp","royalties_usd")),kind:"Royalties",period:sourcePeriod("kdp","royalties_usd")},
 {name:"App Store Connect",amt:roundedApple(m("app_store_connect","proceeds_usd")),kind:"Estimated rounded proceeds, not final payout",period:sourcePeriod("app_store_connect","proceeds_usd")}
 ],[r=>r.name,r=>r.kind,r=>r.period,r=>r.amt]);
 const curr=total("pirevo_sessions")+total("site_sessions");
 const prev=(state.previous?.days||[]).reduce((a,d)=>a+Number(d.pirevo_sessions||0)+Number(d.site_sessions||0),0);
 if(state.compare&&state.previous){
  id("comparisonText").textContent="Tracked website sessions (AstraLabs + PIREVO): "+fm(curr)+" versus "+fm(prev)+" in the preceding "+state.period+" calendar days. "+(prev>0?"Change: "+percent((curr-prev)/prev*100)+".":curr>0?"New tracked traffic versus a zero baseline.":"No sessions recorded in either window.")+" Counts describe two sites, not deduplicated people.";
 }else id("comparisonText").textContent="Select “Compare previous” to see actual website-session changes between comparable date windows. Financial imports have different source periods and are not merged into one speculative trend.";
 const clicks=Number(state.base?.kpis?.amazon_clicks||0),product=Number(state.base?.kpis?.product_views||0);
 const place=id("opportunityText");
 place.textContent=product>0?"PIREVO recorded "+fm(product)+" product views and "+fm(clicks)+" Amazon outbound clicks in the selected period. Test a stronger product-page call to action and judge the result by outbound clicks per view.":curr>0?"Traffic is being tracked, but product-view signals are sparse. Check landing-page pathways and product discovery before increasing promotional volume.":"First-party traffic history is limited. Confirm attribution links and wait for measurable engagement before ranking growth opportunities.";
 renderGAOverviewDetails();
}

function renderGAOverviewTrend(){
 const focus=state.overviewFocus||"sessions";
 const options={
  sessions:[{key:"pirevo_sessions",name:"PIREVO sessions",color:"#006241"},{key:"site_sessions",name:"AstraLabs sessions",color:"#7BB8A2"}],
  views:[{key:"pirevo_views",name:"PIREVO page views",color:"#006241"},{key:"site_views",name:"AstraLabs page views",color:"#7BB8A2"}],
  amazon:[{key:"amazon_clicks",name:"Amazon outbound clicks",color:"#006241"}],
  store:[{key:"store_clicks",name:"App store button clicks",color:"#006241"}]
 };
 const series=options[focus]||options.sessions;
 chart("overviewTraffic",series,{title:"Daily "+series.map(x=>x.name).join(" and ")});
 qa("[data-overview-focus]").forEach(btn=>{
  const active=btn.dataset.overviewFocus===focus;
  btn.setAttribute("aria-pressed",String(active));btn.classList.toggle("is-active",active)
 });
 qa("[data-overview-chart]").forEach(btn=>btn.setAttribute("aria-pressed",String(btn.dataset.overviewChart===focus)));
}
function renderGAOverviewDetails(){
 const daily=state.daily?.days||[],valid=!!state.daily;
 const sum=k=>daily.reduce((n,r)=>n+Number(r[k]||0),0);
 const value=(label,key)=>set(label,valid?fm(sum(key)):"—");
 value("overviewPirevoSessions","pirevo_sessions");value("overviewSiteSessions","site_sessions");
 set("overviewCombinedViews",valid?fm(sum("pirevo_views")+sum("site_views")):"—");
 value("overviewAmazonClicks","amazon_clicks");value("overviewStoreClicks","store_clicks");
 const merged=new Map();
 for(const list of [state.base?.traffic_sources||[],state.site?.site_sources||[]]){
  for(const row of list){
   const label=String(row.source||"direct").trim().toLowerCase()||"direct";
   const n=Number(row.sessions||0);
   if(!Number.isFinite(n)||n<0)continue;
   const key=label==="(direct)"?"direct":label;
   merged.set(key,(merged.get(key)||0)+n);
  }
 }
 barList("overviewAcquisition",[...merged].sort((a,b)=>b[1]-a[1]).map(([label,value])=>({name:label.charAt(0).toUpperCase()+label.slice(1),value})),"No recorded source sessions in the selected period.");
 const metrics=[
  ["PIREVO product views","Product page engagement",sum("product_views")],
  ["Amazon outbound clicks","Amazon links, not purchases",sum("amazon_clicks")],
  ["App interest clicks","Internal app links across both sites",sum("app_clicks")+sum("pirevo_app_clicks")],
  ["App store referrals","Outbound Play Store or Apple buttons",sum("store_clicks")],
  ["Book referrals","Clicks to book listings",sum("book_clicks")]
 ];
 const root=id("overviewEngagement");if(root){
  root.replaceChildren();
  if(!valid)empty(root,"Daily first-party event reporting is unavailable.");
  else for(const [label,caption,count] of metrics){
   const row=document.createElement("div");row.className="ga-engagement-row";
   const detail=document.createElement("div"),title=document.createElement("span"),small=document.createElement("small");
   title.textContent=label;small.textContent=caption;detail.append(title,small);
   const strong=document.createElement("strong");strong.textContent=fm(count);
   row.append(detail,strong);root.append(row);
  }
 }
 barList("overviewTopPages",(state.site?.top_pages||[]).map(x=>({name:x.path==="/"?"/ · Homepage":String(x.path),value:Number(x.views||0)})),"Top pages appear after AstraLabs website traffic is tracked.");
}

function paintPlatform(){
 qa("[data-platform]").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.platform===state.platform)));
 qa("[data-app]").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.app===state.app)));
 const play=state.platform==="google_play";id("playDetails").hidden=!play;id("appleDetails").hidden=play;
 const apps=state.app==="all"?["astramate","keepry"]:[state.app];
 const sum=key=>{const vals=apps.map(a=>m("google_play",key,a));return vals.some(v=>v===null)?null:vals.reduce((a,b)=>a+b,0)};
 set("appInstalled",fm(sum("installed_audience")));
 set("appAcquired",fm(sum("device_acquisitions")));
 set("appActive",fm(sum("monthly_active_devices")));
 set("appFirstOpens",fm(sum("device_first_opens")));
 set("appOrders",state.app==="astramate"?"—":fm(m("google_play","one_time_orders","keepry")));
 set("appGross",state.app==="astramate"?"—":usd(m("google_play","gross_revenue_usd","keepry")));
 note("appInstalled",sourcePeriod("google_play","installed_audience","keepry"));
 note("appAcquired",sourcePeriod("google_play","device_acquisitions","keepry"));
 const data=apps.map(app=>({app,installed:m("google_play","installed_audience",app),acq:m("google_play","device_acquisitions",app),active:m("google_play","monthly_active_devices",app),first:m("google_play","device_first_opens",app),gross:m("google_play","gross_revenue_usd",app)}));
 rows("appRows",data,[r=>r.app==="keepry"?"Keepry":"Astramate",r=>fm(r.installed),r=>fm(r.acq),r=>fm(r.first),r=>fm(r.active),r=>usd(r.gross)]);
 barList("appBars",data.map(x=>({name:x.app==="keepry"?"Keepry":"Astramate",value:x.acq})),"No comparable device acquisition snapshots.");
 id("appTrend").replaceChildren();empty(id("appTrend"),"Daily Play Console acquisition and revenue history is not yet imported. Only verified 28-day snapshots are displayed above.");
 const ak=state.app==="all"?"all":state.app;
 const am=(key,app=ak)=>m("app_store_connect",key,app);
 set("appleDownloads",fm(am("first_time_downloads")));
 set("appleImpressions",fm(am("app_store_impressions")));
 set("appleViews",fm(am("product_page_views")));
 set("appleCTR",am("store_conversion_rate")==null?"—":Number(am("store_conversion_rate")).toFixed(2)+"%");
 set("appleIAP",fm(am("in_app_purchases")));
 set("appleProceedsApp",usd(am("proceeds_usd")));
 note("appleDownloads",sourcePeriod("app_store_connect","first_time_downloads",ak));
 note("appleProceedsApp",sourcePeriod("app_store_connect","proceeds_usd",ak)+" · rounded Apple UI estimate");
 const source=metric("app_store_connect","first_time_downloads","astramate");
 id("applePeriod").textContent=source?"Apple snapshot · "+datePretty(source.period_start)+" to "+datePretty(source.period_end)+" · Keepry iOS awaiting review":"No imported Apple performance report";
 const appleApps=state.app==="all"?["astramate","keepry"]:[state.app];
 rows("appleRows",appleApps.map(app=>({app,down:am("first_time_downloads",app),impressions:am("app_store_impressions",app),views:am("product_page_views",app),iap:am("in_app_purchases",app),proceeds:am("proceeds_usd",app)})),[
  r=>r.app==="astramate"?"Astramate":"Keepry",
  r=>r.app==="astramate"?"Ready for Distribution":"Waiting for Review",
  r=>fm(r.down),r=>fm(r.impressions),r=>fm(r.views),r=>fm(r.iap),r=>usd(r.proceeds)
 ]);
}
function renderPirevo(){
 const k=state.base?.kpis||{},amazon=state.amazon?.month_to_date;
 set("pSessions",k.sessions==null?"—":fm(k.sessions));
 set("pVisitors",k.visitors==null?"—":fm(k.visitors));
 set("pProduct",k.product_views==null?"—":fm(k.product_views));
 set("pClicks",k.amazon_clicks==null?"—":fm(k.amazon_clicks));
 set("pCTR",k.ctr==null?"—":percent(k.ctr));
 set("pRevenue",amazon?usd(amazon.earnings_usd):"—");
 set("pOrders",amazon?.ordered_items==null?"—":fm(amazon.ordered_items));
 set("pPinterest",k.pinterest_traffic==null?"—":fm(k.pinterest_traffic));
 chart("pirevoChart",[{key:"pirevo_sessions",name:"Sessions"},{key:"product_views",name:"Product views",color:"#C8A96B"},{key:"amazon_clicks",name:"Amazon outbound",color:"#7BB8A2"}],{title:"PIREVO first-party commerce engagement"});
 barList("pSources",(state.base?.traffic_sources||[]).map(r=>({name:r.source,value:Number(r.sessions||0)})),"No recorded source sessions in this period.");
 rows("pProducts",(state.base?.top_products||[]),[r=>r.item_name||r.product_slug||"Product",r=>fm(r.clicks)]);
 rows("pCampaigns",(state.base?.campaigns||[]),[r=>r.campaign||"Campaign",r=>fm(r.visits),r=>fm(r.amazon_clicks),r=>percent(r.ctr)]);
 const funnel=id("pFunnel");funnel.replaceChildren();
 [["Sessions",k.sessions],["Product views",k.product_views],["Amazon outbound",k.amazon_clicks],["Amazon orders (account-level)",amazon?.ordered_items]].forEach(([lab,val],i)=>{
  if(i){const ar=document.createElement("span");ar.className="funnel-arrow";ar.textContent="›";funnel.append(ar)}
  const node=document.createElement("div");node.className="funnel-node";const strong=document.createElement("strong");strong.textContent=fm(val);const small=document.createElement("small");small.textContent=lab;node.append(strong,small);funnel.append(node)
 });
 const gsc=state.base?.search_console||{};set("gImpressions",gsc.captured_at?fm(gsc.impressions):"—");set("gClicks",gsc.captured_at?fm(gsc.clicks):"—");set("gCtr",gsc.captured_at?percent(gsc.ctr):"—");
 note("searchConsole",gsc.captured_at?"GSC report through "+datePretty(gsc.window_end):"Search Console report not imported");
}
function renderDigital(){
 const report=state.kdpSync?.sync||null;
 const imported=state.platforms?.metrics?.some(x=>x.provider==="kdp"&&x.metric==="book_units")||false;
 const synced=!!report?.last_success_at;
 const royalties=m("kdp","royalties_usd");
 const processed=m("kdp","book_units");
 set("digitalBookClicks",fm(total("book_clicks")));
 set("publishedTitles","1");
 set("digitalRoyalty",usd(royalties));
 set("digitalUnits",fm(processed));
 id("kdpLastSynced").textContent=synced?new Date(report.last_success_at).toLocaleString("en-PH",{dateStyle:"medium",timeStyle:"short",timeZone:"Asia/Manila"})+" PHT":"Awaiting first verified check";
 id("kdpVerifiedPeriod").textContent=report?.report_period_start&&report.report_period_end
  ?datePretty(report.report_period_start)+" – "+datePretty(report.report_period_end):"Awaiting KDP report";
 const badge=id("kdpSyncBadge");
 const status=report?.status||"pending";
 badge.textContent=status==="success"?"Synced":status==="partial"?"Orders synced · royalties pending":status==="authentication_required"?"Sign-in required":status==="source_unavailable"?"Source unavailable":"Awaiting sync";
 badge.dataset.syncStatus=status;
 const stale=report?.last_success_at&&(Date.now()-Date.parse(report.last_success_at)>36*60*60*1000);
 let message="";
 if(status==="authentication_required")message="KDP session expired. Sign back in at KDP Reports to resume authorized checks. Last verified values remain dated.";
 else if(status==="source_unavailable")message="KDP reporting could not be read. Source unavailable; previously imported figures are historical, not live.";
 else if(synced)message="Imported from authenticated KDP Reports. "+(report.data_note||"")+" "+(stale?"Last successful import is over 36 hours old. Please refresh authorization/check schedule.":"Latest import recorded. Further updates depend on scheduled browser access.");
 else message="KDP sync is prepared, but no verified sales report has been captured.";
 id("kdpSyncMessage").textContent=message;
 id("kdpSourceStatus").textContent=imported?sourcePeriod("kdp","book_units"):"Awaiting verified processed units";
 id("kdpHistoryStatus").textContent=imported?"Source-backed imports":"No imports";
 id("kdpHistoryMessage").textContent=synced
  ?"KDP processed orders are documented per report period. Estimated royalties remain unavailable until imported from a royalty-specific report."
  :"No verified KDP report imported. Book referrals are not confirmed sales.";
 const history=state.kdpSync?.recent_snapshots||[];
 rows("kdpSyncRows",history,[r=>datePretty(r.report_period_start)+" – "+datePretty(r.report_period_end),
  r=>r.report_name||"KDP report",r=>fm(r.units),r=>r.royalties_usd==null?"—":usd(r.royalties_usd),
  r=>r.checked_at?new Date(r.checked_at).toLocaleDateString("en-PH",{timeZone:"Asia/Manila"}):"—"]);
 id("kdpConnectionNote").firstChild.textContent="KDP source: authenticated report snapshots, not a live public API. Missing royalties remain —, not $0. Book referrals do not equal sales. KDP royalties are separate from Amazon Associates commissions. ";
 chart("digitalChart",[{key:"book_clicks",name:"Book referrals"}],{title:"Daily PIREVO book referrals (not KDP sales)"});
}
function renderWebsite(){
 const s=state.site?.astralabs||{};
 set("webVisitors",s.visitors==null?"—":fm(s.visitors));
 set("webSessions",s.sessions==null?"—":fm(s.sessions));
 set("webViews",s.page_views==null?"—":fm(s.page_views));
 set("webAppClicks",s.app_clicks==null?"—":fm(s.app_clicks));
 set("webStoreClicks",s.store_clicks==null?"—":fm(s.store_clicks));
 chart("webChart",[{key:"site_sessions",name:"Sessions"},{key:"site_views",name:"Page views",color:"#C8A96B"}],{title:"AstraLabs website visits and page views"});
 barList("webSources",(state.site?.site_sources||[]).map(r=>({name:r.source,value:Number(r.sessions||0)})),"No source data collected.");
 barList("webPages",(state.site?.top_pages||[]).map(r=>({name:r.path==="/"?"/ · Home":r.path,value:Number(r.views||0)})),"Website event collection starts from its deployment date.");
 rows("webApps",(state.site?.apps||[]),[r=>r.app==="keepry"?"Keepry":"Astramate",r=>fm(r.app_landing_views),r=>fm(r.google_play_clicks),r=>fm(r.app_store_clicks)]);
}
function renderAdmob(){
 set("adEst",usd(m("admob","estimated_earnings_usd")));
 const prev=m("admob","previous_month_estimated_earnings_usd");
 set("adPrev",prev==null?"—":"$"+prev.toFixed(3));
 set("adImpressions",fm(m("admob","ad_impressions")));
 set("adRequests",fm(m("admob","ad_requests")));
 note("adEst",sourcePeriod("admob","estimated_earnings_usd")+" · estimate");
 note("adPrev",sourcePeriod("admob","previous_month_estimated_earnings_usd")+" · prior month");
 id("adTrend").replaceChildren();empty(id("adTrend"),"Daily AdMob earnings data has not been imported. October month-to-date and September estimates cover different periods and are not plotted as a continuous trend.");
 rows("adBreakdown",(state.platforms?.metrics||[]).filter(x=>x.provider==="admob"),[r=>r.metric.replaceAll("_"," "),r=>r.metric_value==null?"—":r.metric_unit==="USD"?"$"+Number(r.metric_value).toFixed(3):fm(r.metric_value),r=>datePretty(r.period_start)+" – "+datePretty(r.period_end),r=>r.report_status]);
}
function paintSocial(){
 qa("[data-social]").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.social===state.social)));
 const sources=[...(state.base?.traffic_sources||[]).map(x=>({source:clean(x.source).toLowerCase(),sessions:Number(x.sessions||0),from:"Pirevo"})),...(state.site?.site_sources||[]).map(x=>({source:clean(x.source).toLowerCase(),sessions:Number(x.sessions||0),from:"AstraLabs"}))];
 const platforms=["tiktok","facebook","youtube","instagram","threads","pinterest"];
 const mapped=platforms.map(name=>({name,value:sources.filter(s=>s.source===name).reduce((a,b)=>a+b.sessions,0)}));
 const shown=state.social==="all"?mapped:mapped.filter(x=>x.name===state.social);
 set("socialVisits",fm(shown.reduce((a,b)=>a+b.value,0)));
 set("socialNative","—");
 set("socialFollowers","—");
 set("socialPosts","—");
 barList("socialSources",shown,"No attributed website sessions from the selected social channel for this period.");
 if(state.social==="all"){
  chart("socialChart",[{key:"pirevo_social_sessions",name:"PIREVO social sessions"},{key:"site_social_sessions",name:"AstraLabs social sessions",color:"#C8A96B"}],{title:"Daily tracked sessions with social referrers"});
 }else empty(id("socialChart"),"Native "+state.social+" impressions and per-platform historical activity require an authorized analytics integration. Aggregate website referrals are shown separately.");
 const socialRows=platforms.filter(p=>state.social==="all"||state.social===p).map(p=>({p,site:shown.find(x=>x.name===p)?.value||0}));
 rows("socialRows",socialRows,[r=>r.p.charAt(0).toUpperCase()+r.p.slice(1),r=>fm(r.site),r=>"Awaiting native API",r=>r.p==="pinterest"?"PIREVO Buffer posting; native metrics pending":"Not imported"]);
}
function renderAll(){
 renderSummary();stamp();renderOverview();paintPlatform();renderPirevo();renderDigital();renderWebsite();renderAdmob();paintSocial();
 chart("reportTrafficChart",[{key:"pirevo_sessions",name:"PIREVO sessions",color:"#006241"},{key:"site_sessions",name:"AstraLabs sessions",color:"#7BB8A2"}],{title:"Cross-site tracked sessions per calendar day"});
 window.ASTRA_REPORTS?.render(state);
}
async function load(){
 if(!state.token)return;
 const n=++state.seq;
 id("refresh").disabled=true;
 id("lastSync").textContent="Refreshing verified reports…";
 const token=state.token,days=state.period;
 const requests=[
 ["base",rpc("pirevo_dashboard_snapshot",{p_days:days,p_token:token})],
 ["site",rpc("pirevo_growth_counters",{p_days:days,p_token:token})],
 ["platforms",rpc("pirevo_platform_report_snapshot",{p_token:token})],
 ["amazon",rpc("pirevo_amazon_earnings_snapshot",{p_token:token})],
 ["daily",rpc("astralabs_portfolio_daily_v2",{p_days:days,p_token:token})],
 ["trendPerformance",rpc("pirevo_trend_product_performance",{p_days:days,p_token:token})],
 ["kdpSync",rpc("pirevo_kdp_sync_snapshot",{p_token:token})],
 ["previous",state.compare?rpc("astralabs_portfolio_daily_range_v2",{p_days:days,p_token:token,p_shift_days:days}):Promise.resolve(null)]
 ];
 const settled=await Promise.allSettled(requests.map(x=>x[1]));
 if(n!==state.seq)return;
 let successful=0;
 settled.forEach((r,i)=>{const key=requests[i][0];state[key]=r.status==="fulfilled"?r.value:null;if(r.status==="fulfilled"&&r.value&&key!=="previous"&&key!=="trendPerformance"&&key!=="kdpSync")successful++});
 renderAll();
 id("refresh").disabled=false;
 id("sourceHealth").textContent=successful+"/5 reporting sources accessible";
 if(successful<5)id("sourceHealthDot").classList.remove("live");
}
document.addEventListener("DOMContentLoaded",initialize);
setInterval(()=>{if(!document.hidden&&state.token)load()},60000);
document.addEventListener("visibilitychange",()=>{if(!document.hidden&&state.token)load()});
})();
