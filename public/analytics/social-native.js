
(function(){
"use strict";
const F=n=>n==null?"—":Number(n).toLocaleString("en-US");
const pretty=d=>{if(!d)return "";const [y,m,day]=String(d).slice(0,10).split("-");return [m,day,y].join("/")};
const title=(parent,txt)=>{const e=document.createElement("strong");e.textContent=txt;parent.append(e)};
function render(state){
 const net=state.social||"all",root=document.getElementById("socialNativeDetails");
 if(!root)return;
 const metrics=state.socialMetrics?.metrics||[];
 const record=(n,k)=>metrics.find(x=>x.network===n&&x.metric===k);
 const value=(n,k)=>record(n,k)?.metric_value;
 const set=(name,v)=>{const e=document.querySelector('[data-v="'+name+'"]');if(e)e.textContent=v};
 const note=(name,v)=>{const e=document.querySelector('[data-note="'+name+'"]');if(e)e.textContent=v};
 const label=(id,v)=>{const e=document.getElementById(id);if(e)e.textContent=v};
 label("socialViewsLabel",net==="tiktok"?"Lifetime plays · visible videos":net==="pinterest"?"Pinterest impressions":net==="facebook"?"Facebook views":"Native views / impressions");
 label("socialPostsLabel",net==="tiktok"?"Visible videos":net==="pinterest"?"Pins on boards":"Published posts");
 if(net==="all"){
   set("socialNative","—");note("socialNativeStatus","Choose a platform · lifetime, 28-day and 30-day totals differ");
   set("socialPosts","—");note("socialPostsStatus","Choose a platform · published posts differ from current inventory");
 }
 if(net==="tiktok"){
   set("socialNative",F(value("tiktok","visible_video_views_total")));
   note("socialNativeStatus","Lifetime plays on 23 visible videos · NOT last 30 days");
   set("socialPosts",F(value("tiktok","visible_videos")));
   note("socialPostsStatus","Current public inventory · not posts in website date range");
 }
 if(net==="pinterest"){
   set("socialPosts",F(value("pinterest","board_pin_inventory")));
   note("socialPostsStatus","Current board inventory, not 30-day published posts");
 }
 const tr=[...document.querySelectorAll("#socialRows tr")];
 for(const row of tr){
  const cells=row.querySelectorAll("td");if(cells.length!==6)continue;
  const p=(cells[0].textContent||"").trim().toLowerCase();
  if(p==="tiktok"){
    cells[1].textContent=F(value("tiktok","visible_video_views_total"))+" (lifetime)";
    cells[3].textContent=F(value("tiktok","visible_videos"))+" visible";
    cells[5].textContent="TikTok live creator profile, Oct 10 · lifetime playback totals · Metricool prior-day history awaiting backfill";
  }
  if(p==="pinterest"){
    cells[3].textContent=F(value("pinterest","board_pin_inventory"))+" on boards";
    cells[5].textContent="Pinterest Business Analytics · impressions Sep 10–Oct 10; Pins are current board inventory";
  }
  if(p==="facebook"&&record("facebook","native_views")){
    cells[5].textContent="Meta Business Suite Sep 11–Oct 8 (views) · follower snapshot Oct 10 · post count pending period-qualified import";
  }
 }
 root.hidden=false;root.replaceChildren();
 const h=document.createElement("div");h.className="social-native-head";
 const heading=document.createElement("h3");heading.textContent=net==="all"?"Native data source coverage":net.charAt(0).toUpperCase()+net.slice(1)+" · verified detail";
 const mark=document.createElement("span");mark.textContent=net==="facebook"?"Sep 11–Oct 8, 2026":net==="pinterest"?"Sep 10–Oct 10, 2026":net==="tiktok"?"Account snapshot Oct 10, 2026":"Separate verified reporting windows";
 h.append(heading,mark);root.append(h);
 const g=document.createElement("div");g.className="social-facts";root.append(g);
 function fact(k,v,sub){
  if(v==null)return;const box=document.createElement("div");box.className="social-fact";
  const n=document.createElement("strong");n.textContent=typeof v==="number"?F(v):String(v);
  const t=document.createElement("small");t.textContent=k;
  const d=document.createElement("span");d.textContent=sub||"";
  box.append(n,t,d);g.append(box);
 }
 let disclosure="";
 if(net==="facebook"){
   fact("Viewers",value("facebook","viewers"),"People, not views");
   fact("Page visits",value("facebook","page_visits"),"Not website sessions");
   fact("Interactions",value("facebook","interactions"),"28-day content activity");
   fact("Net new follows",value("facebook","new_followers"),"28-day reporting period");
   disclosure="Current Facebook Page followers: 29 as of Oct 10. Meta daily view series is available. The period-qualified total of published posts remains unverified.";
 } else if(net==="pinterest"){
   fact("Outbound clicks",value("pinterest","outbound_clicks"),"Not Amazon orders");
   fact("Saves",value("pinterest","saves"),"Reported 30-day value");
   fact("PIREVO board Pins",value("pinterest","pirevo_board_pins"),"Board inventory");
   fact("Audience",value("pinterest","total_audience"),"Estimated 30-day people");
   disclosure="Pinterest 98 impressions (newer 30-day source). Board Pins: 37 PIREVO + 15 AstraLabs. Pinterest profile follower count is not yet reliably loaded. Pinterest outbound clicks and attributed website sessions are distinct.";
 } else if(net==="tiktok"){
   fact("Lifetime video plays",value("tiktok","visible_video_views_total"),"Sum of visible video counters");
   fact("Current followers",value("tiktok","followers"),"Profile total");
   fact("Visible videos",value("tiktok","visible_videos"),"Current inventory");
   fact("Profile likes",value("tiktok","likes"),"Not a period count");
   disclosure="2,833 plays are accumulated on 23 visible videos, NOT views gained in the last 30 days. Metricool started on Oct 10 and has not backfilled 7/30-day data.";
 } else if(net==="all"){
   fact("Facebook views",value("facebook","native_views"),"28 days ending Oct 8");
   fact("Pinterest impressions",value("pinterest","native_views"),"30 days ending Oct 10");
   fact("TikTok visible video plays",value("tiktok","visible_video_views_total"),"Lifetime counts");
   fact("Connected accounts","6 / 6","Reporting dates differ");
   disclosure="These source figures are intentionally NOT summed into one audience total. Source-tagged PIREVO traffic, retailer orders and commission records are separate.";
 }else{
   fact("Followers",value(net,"followers"),"Provider account metric");
   fact("Published posts",value(net,"published_posts"),"Provider reporting period");
   disclosure="Metricool connected. Check exact source date and period before comparing against another platform.";
 }
 const paragraph=document.createElement("p");paragraph.className="note";paragraph.textContent=disclosure;root.append(paragraph);
 if(net==="facebook"){
  const daily=(state.socialMetrics?.daily||[]).filter(x=>x.network==="facebook"&&x.metric==="views").sort((a,b)=>String(a.day).localeCompare(String(b.day)));
  if(daily.length){
   const plot=document.getElementById("socialChart");plot.replaceChildren();
   const subtitle=document.createElement("p");subtitle.className="social-plot-label";subtitle.textContent="Meta Business Suite · "+daily.length+" days · "+F(daily.reduce((a,b)=>a+Number(b.metric_value),0))+" Facebook views";
   const bars=document.createElement("div");bars.className="social-daily-bars";
   const max=Math.max(1,...daily.map(x=>Number(x.metric_value)));
   bars.setAttribute("role","img");bars.setAttribute("aria-label","Daily Facebook views from "+daily[0].day+" to "+daily.at(-1).day);
   for(const d of daily){const bar=document.createElement("div");bar.className="social-daily-bar";bar.title=d.day+": "+F(d.metric_value)+" views";bar.style.height=Math.max(2,100*Number(d.metric_value)/max)+"%";bars.append(bar)}
   const axis=document.createElement("div");axis.className="social-daily-axis";
   const s=document.createElement("span");s.textContent=pretty(daily[0].day);
   const e=document.createElement("span");e.textContent=pretty(daily.at(-1).day);
   axis.append(s,e);plot.append(subtitle,bars,axis);
  }
 }
}
window.ASTRA_SOCIAL_NATIVE={render};
})();
