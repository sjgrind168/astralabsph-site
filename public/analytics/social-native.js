/* AstraLabs PH unified Socials renderer.
 * Sole owner of cards, labels, rows, chart and details on Socials tab.
 * Every metric is source-backed, identified by its scope, and never imputed.
 */
(function(){
"use strict";
const NETWORKS=["tiktok","facebook","youtube","instagram","threads","pinterest"];
const LABELS={tiktok:"TikTok",facebook:"Facebook",youtube:"YouTube",instagram:"Instagram",threads:"Threads",pinterest:"Pinterest"};
const formatted=n=>n==null||!Number.isFinite(Number(n))?"—":Number(n).toLocaleString("en-US",{maximumFractionDigits:0});
const pretty=d=>{if(!d)return "Date unavailable";const v=String(d).slice(0,10),parts=v.split("-");return parts.length===3?parts[1]+"/"+parts[2]+"/"+parts[0]:v};
function sourceInfo(r){return r?.period_start&&r?.period_end?pretty(r.period_start)+(r.period_start===r.period_end?"":" – "+pretty(r.period_end)):"Source date not available";}
function dom(name){return document.getElementById(name)}
function build(tag,cls,text){const el=document.createElement(tag);if(cls)el.className=cls;if(text!==undefined)el.textContent=String(text);return el}
function canonical(source){
 const s=String(source||"").toLowerCase().trim();
 if(/tiktok|tiktok\.com/.test(s))return "tiktok";
 if(/facebook|(^|[^a-z])fb([^a-z]|$)|fb\.com/.test(s))return "facebook";
 if(/youtube|youtu\.be/.test(s))return "youtube";
 if(/instagram|instagr\.am/.test(s))return "instagram";
 if(/threads|threads\.net/.test(s))return "threads";
 if(/pinterest|pin\.it/.test(s))return "pinterest";
 return null;
}
function render(state,helpers){
 const h=helpers||{},n=NETWORKS.includes(state.social)?state.social:"all";
 const raw=Array.isArray(state.socialMetrics?.metrics)?state.socialMetrics.metrics:[];
 const connections=Array.isArray(state.socialMetrics?.sources)?state.socialMetrics.sources:[];
 const daily=Array.isArray(state.socialMetrics?.daily)?state.socialMetrics.daily:[];
 const rec=(net,key)=>raw.find(x=>x.network===net&&x.metric===key)||null;
 const val=(net,key)=>rec(net,key)?.metric_value;
 const put=(name,v)=>{const e=document.querySelector('[data-v="'+name+'"]');if(e)e.textContent=v};
 const note=(name,v)=>{const e=document.querySelector('[data-note="'+name+'"]');if(e)e.textContent=v};
 const label=(name,v)=>{const e=dom(name);if(e)e.textContent=v};
 const metric=(net)=>net==="tiktok"?rec(net,"visible_video_views_total"):rec(net,"native_views");
 const content=(net)=>net==="tiktok"?rec(net,"visible_videos"):net==="pinterest"?rec(net,"board_pin_inventory"):rec(net,"published_posts");
 const rangeKind=(net)=>net==="tiktok"?"Cumulative public lifetime plays":net==="pinterest"?"Native impressions":net==="facebook"?"Meta native views":"Metricool native views";
 const contentKind=(net)=>net==="tiktok"?"Visible video inventory":net==="pinterest"?"Pins on boards":"Published in provider period";
 const coverage=NETWORKS.filter(p=>rec(p,"native_views")!==null).length;
 const connected=connections.filter(x=>x.connection_status==="connected").length;
 document.querySelectorAll("[data-social]").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.social===n)));
 const sources=[...(state.base?.traffic_sources||[]),...(state.site?.site_sources||[])];
 const sessions=NETWORKS.map(p=>({name:LABELS[p],slug:p,value:sources.filter(x=>canonical(x.source)===p).reduce((sum,x)=>sum+(Number(x.sessions)||0),0)}));
 const siteAvailable=Boolean(state.base||state.site);
 const selected=n==="all"?sessions:sessions.filter(x=>x.slug===n);
 put("socialVisits",siteAvailable?formatted(selected.reduce((sum,r)=>sum+r.value,0)):"—");
 note("socialReferrals",siteAvailable?"First-party website sessions · website period selector applies":"Website referral sources unavailable");
 if(n==="all"){
  put("socialNative","—");
  note("socialNativeStatus",coverage+"/6 dated platform views sources; choose a channel to avoid mixing periods");
  const followerSources=NETWORKS.filter(p=>rec(p,"followers"));
  put("socialFollowers",followerSources.length?formatted(followerSources.reduce((sum,p)=>sum+Number(val(p,"followers")),0)):"—");
  note("socialFollowersStatus",followerSources.length+"/6 account totals summed, NOT unique audience");
  put("socialPosts","—");note("socialPostsStatus","Choose a channel · period posts and cumulative inventory differ");
 }else{
  const view=metric(n),follow=rec(n,"followers"),published=content(n);
  put("socialNative",view?formatted(view.metric_value):"—");
  note("socialNativeStatus",view?rangeKind(n)+" · "+sourceInfo(view):"No verified view metric from this platform");
  put("socialFollowers",follow?formatted(follow.metric_value):"—");
  note("socialFollowersStatus",follow?"Account total as of "+sourceInfo(follow):n==="pinterest"?"Follower count awaiting independent verification; setup-day Metricool zeros are inconclusive":"Follower data not available");
  put("socialPosts",published?formatted(published.metric_value):"—");
  note("socialPostsStatus",published?contentKind(n)+" · "+sourceInfo(published):"Period-qualified published count unavailable");
 }
 label("socialViewsLabel",n==="tiktok"?"Visible-video lifetime plays":n==="pinterest"?"Pin impressions":n==="facebook"?"Facebook views":"Native impressions / views");
 label("socialPostsLabel",n==="tiktok"?"Visible videos":n==="pinterest"?"Pins on boards":n==="facebook"?"Published posts & reels":"Published posts");
 label("socialNativeSourceBadge",state.socialMetrics?
   connected+"/6 connected · "+coverage+"/6 dated views sources · TikTok lifetime counts separate":
   "Social source unavailable · last verified data not loaded");
 if(typeof h.barList==="function")h.barList("socialSources",selected,"No attributed website sessions from the selected channel during the website date range.");
 else {
  const area=dom("socialSources");if(area)area.replaceChildren(build("div","empty","Website-referral breakdown unavailable"));
 }
 const chart=dom("socialChart");
 const points=daily.filter(x=>x.network===n&&x.metric==="views"&&Number.isFinite(Number(x.metric_value))).sort((a,b)=>String(a.day).localeCompare(String(b.day)));
 if(n!=="all"&&points.length){
  chart.replaceChildren();
  const interval=build("p","social-plot-label",LABELS[n]+" native daily views · "+pretty(points[0].day)+" – "+pretty(points[points.length-1].day)+" · historical provider dates");
  const bars=build("div","social-daily-bars");
  bars.setAttribute("role","img");
  bars.setAttribute("aria-label",LABELS[n]+" daily view counts from "+pretty(points[0].day)+" to "+pretty(points[points.length-1].day));
  const max=Math.max(1,...points.map(x=>Number(x.metric_value)));
  points.forEach(x=>{const bar=build("div","social-daily-bar");bar.style.height=Math.max(2,100*Number(x.metric_value)/max)+"%";bar.title=pretty(x.day)+": "+formatted(x.metric_value)+" views";bars.append(bar)});
  const axis=build("div","social-daily-axis");
  axis.append(build("span","",pretty(points[0].day)),build("span","",pretty(points[points.length-1].day)));
  chart.append(interval,bars,axis);
 }else if(n==="all"&&typeof h.chart==="function"){
  h.chart("socialChart",[{key:"pirevo_social_sessions",name:"PIREVO social referrals",color:"#006241"},{key:"site_social_sessions",name:"AstraLabs social referrals",color:"#7BB8A2"}],
   {title:"Verified first-party website social referrals by day (not native reach)",
   empty:"No recorded social website sessions in this website reporting period. Native platform exposure is shown separately below."});
 }else if(chart){
  const r=metric(n);
  chart.replaceChildren(build("div","empty",
   r?LABELS[n]+" "+rangeKind(n).toLowerCase()+" are recorded for "+sourceInfo(r)+
      ", but native DAILY history has not been imported. No invented bar chart.": 
     LABELS[n]+" account connected; native daily views are not yet available. Website referrals are separate."));
 }
 const tableRows=(n==="all"?NETWORKS:[n]).map(net=>({net,view:metric(net),followers:rec(net,"followers"),published:content(net),referral:sessions.find(x=>x.slug===net)?.value||0}));
 if(typeof h.rows==="function")h.rows("socialRows",tableRows,[
  r=>LABELS[r.net],
  r=>r.view?formatted(r.view.metric_value)+(r.net==="tiktok"?" (lifetime)":""):"—",
  r=>r.followers?formatted(r.followers.metric_value):"—",
  r=>r.published?formatted(r.published.metric_value)+(r.net==="pinterest"?" on boards":r.net==="tiktok"?" visible":""):"—",
  r=>siteAvailable?formatted(r.referral):"—",
  r=>r.view?rangeKind(r.net)+" · "+r.view.source_name+" · "+sourceInfo(r.view):
   r.followers?"Profile account snapshot · "+r.followers.source_name+" · "+sourceInfo(r.followers):
   connections.find(x=>x.network===r.net)?.connection_status==="connected"?"Connected; verifiable historical metrics pending":"No verified source"
 ]);
 const detail=dom("socialNativeDetails");if(!detail)return;
 detail.hidden=false;detail.replaceChildren();
 const head=build("div","social-native-head");
 head.append(build("h3","",n==="all"?"Cross-platform reporting scope":LABELS[n]+" · verified data"),
   build("span","",n==="all"?"Periods vary":sourceInfo(metric(n)||rec(n,"followers")||content(n))));
 detail.append(head);
 const grid=build("div","social-facts");
 detail.append(grid);
 const add=(name,net,key,scope)=>{const x=rec(net,key);if(!x)return;
  const box=build("div","social-fact");
  box.append(build("strong","",formatted(x.metric_value)),build("small","",name),
   build("span","",scope||sourceInfo(x)));grid.append(box)
 };
 let disclaimer="";
 if(n==="facebook"){
  add("Unique viewers","facebook","viewers","28-day Meta report");
  add("Page visits","facebook","page_visits","Not website sessions");
  add("Interactions","facebook","interactions","Not retailer orders");
  add("Net new followers","facebook","new_followers","28-day reporting period");
  add("Published posts & reels","facebook","published_posts","Meta Published list, 28-day source");
  disclaimer="Facebook views and unique viewers are separate metrics. Meta published posts and reels Sep 11–Oct 8 exclude scheduled content, drafts and Stories.";
 }else if(n==="pinterest"){
  add("Outbound clicks","pinterest","outbound_clicks","Not Amazon orders");
  add("Saves","pinterest","saves","30-day native report");
  add("PIREVO Pins","pinterest","pirevo_board_pins","Current board inventory");
  add("Audience","pinterest","total_audience","Provider estimate");
  disclaimer="Pinterest impressions cover the Created Pins report, not unique viewers. Board inventory is not the count published this month. Pinterest followers remain unverified; setup-day Metricool zeros are not conclusive.";
 }else if(n==="tiktok"){
  add("Current followers","tiktok","followers","Profile count");
  add("Profile likes","tiktok","likes","Lifetime public profile count");
  add("Visible videos","tiktok","visible_videos","Current inventory");
  add("Lifetime visible-video plays","tiktok","visible_video_views_total","Cumulative, NOT last 30 days");
  disclaimer="TikTok public video play totals are historical accumulated counters, NOT current-month gains. Metricool hasn't backfilled dated videos yet.";
 }else if(n==="all"){
  add("Facebook views","facebook","native_views","28-day period");
  add("Pinterest impressions","pinterest","native_views","30-day period");
  add("TikTok lifetime plays","tiktok","visible_video_views_total","Cumulative video counters");
  const box=build("div","social-fact");
  box.append(build("strong","",connected+"/6"),build("small","","Linked social accounts"),build("span","","Native metrics have different windows"));
  grid.append(box);
  disclaimer="Dated Facebook views, Pinterest impressions and lifetime TikTok plays are deliberately NOT summed. Clicks from the platforms, website sessions and Amazon checkouts are different funnel stages.";
 }else{
  add("Followers",n,"followers","Provider snapshot");add("Posts in reporting window",n,"published_posts","Metricool reporting period");
  disclaimer="Source-backed metrics for "+LABELS[n]+". The website period selector controls first-party referrals; it does not change native provider snapshot dates.";
 }
 detail.append(build("p","note",disclaimer));
}
window.ASTRA_SOCIAL_NATIVE=Object.freeze({render});
})();
