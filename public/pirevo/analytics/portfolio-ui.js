(()=>{
"use strict";
/* Mirrors existing verified source fields. No synthetic portfolio revenue totals. */
const el=id=>document.getElementById(id);
const pairs=[
 ["sumPayout",'[data-provider="google_play"] [data-metric="payout_balance_usd"]'],
 ["sumInstalls",'[data-provider="google_play"] [data-metric="installed_audience"]'],
 ["sumPirevoSessions","#kSessions"],
 ["sumSiteViews","#growthSitePageviews"],
 ["sumAmazon","#amzEarnMonth"]
];
function sync(){
 for(const [target,selector] of pairs){
  const node=el(target),source=document.querySelector(selector);
  if(!node||!source)continue;
  const value=source.textContent.trim();
  node.textContent=(!value||value==="Loading..."||value==="0"&&source.id==="kSessions"&&!document.querySelector(".live-dot.on"))?"—":value;
 }
 const source=el("firstPartySourceStatus"),live=el("liveText");
 if(source&&live)source.textContent=live.textContent.includes("Live")?"PIREVO tracking active":"PIREVO tracking unavailable";
}
const tracked=pairs.map(x=>document.querySelector(x[1])).filter(Boolean);
const trackedNodes=[...tracked,el("liveText")].filter(Boolean);
const observer=new MutationObserver(sync);
trackedNodes.forEach(x=>observer.observe(x,{childList:true,characterData:true,subtree:true}));
const anchors=[...document.querySelectorAll('.console-sidebar nav a[href^="#"]')];
for(const a of anchors){
 a.addEventListener("click",()=>{
  anchors.forEach(n=>{n.classList.toggle("active",n===a);if(n===a)n.setAttribute("aria-current","location");else n.removeAttribute("aria-current")});
 });
}
if("IntersectionObserver" in window){
 const sections=[...document.querySelectorAll(".console-section[id],#overview")];
 const active=new IntersectionObserver(entries=>{
  const candidates=entries.filter(x=>x.isIntersecting).sort((a,b)=>b.intersectionRatio-a.intersectionRatio);
  if(!candidates.length)return;
  const found=anchors.find(x=>x.getAttribute("href")==="#"+candidates[0].target.id);
  if(found){anchors.forEach(n=>{n.classList.toggle("active",n===found);if(n===found)n.setAttribute("aria-current","location");else n.removeAttribute("aria-current")})}
 },{rootMargin:"-10% 0px -62% 0px",threshold:[0,.2,.5]});
 sections.forEach(s=>active.observe(s));
}
sync();
})();