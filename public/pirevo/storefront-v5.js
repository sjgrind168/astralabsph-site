/* PIREVO v5, accessible carousels and catalog filters. */
(()=>{"use strict";
const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>Array.from(r.querySelectorAll(s));
const menu=$(".pv-menu-toggle"),nav=$(".pv-header-nav");
if(menu&&nav){menu.addEventListener("click",()=>{const open=nav.classList.toggle("pv-open");menu.setAttribute("aria-expanded",String(open));menu.textContent=open?"Close ×":"Menu ☰"});nav.addEventListener("click",e=>{if(e.target.closest("a")&&nav.classList.contains("pv-open")){nav.classList.remove("pv-open");menu.setAttribute("aria-expanded","false");menu.textContent="Menu ☰";}});}
$$("[data-pv-carousel]").forEach(shell=>{
 const track=$(".pv-carousel-track",shell),prev=$('[data-dir="prev"]',shell),next=$('[data-dir="next"]',shell),status=$(".pv-car-status",shell);
 if(!track||!prev||!next)return;
 const cards=$$(":scope > *",track);
 const update=()=>{const max=Math.max(0,track.scrollWidth-track.clientWidth);prev.disabled=track.scrollLeft<5;next.disabled=track.scrollLeft>=max-5;
 const first=cards.findIndex(c=>c.getBoundingClientRect().right>=track.getBoundingClientRect().left+15);
 const width=cards[0]?.getBoundingClientRect().width||300;
 const visible=Math.max(1,Math.floor((track.clientWidth+13)/(width+13)));
 if(status)status.textContent=cards.length?(Math.max(1,first+1)+"–"+Math.min(cards.length,Math.max(0,first)+visible)+" of "+cards.length):"";
 };
 for(const [btn,dir] of [[prev,-1],[next,1]])btn.addEventListener("click",()=>{const c=cards[0],gap=parseFloat(getComputedStyle(track).columnGap)||15;const step=(c?.getBoundingClientRect().width||track.clientWidth)+gap;track.scrollBy({left:step*Math.max(1,Math.floor(track.clientWidth/step))*dir,behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth"});});
 track.addEventListener("scroll",update,{passive:true});addEventListener("resize",update,{passive:true});requestAnimationFrame(update);
});
const reveal=$("#pv-all-cats");
if(reveal)reveal.addEventListener("click",()=>{const opened=reveal.getAttribute("aria-expanded")==="true";$$(".pv-extra-cat").forEach(x=>x.hidden=opened);reveal.setAttribute("aria-expanded",String(!opened));reveal.textContent=opened?"View all 20 categories ↓":"Show fewer categories ↑";});
const input=$("#pv-search"),cat=$("#pv-cat-select"),cards=$$("#pv-products-grid .pv-card"),more=$("#pv-more"),count=$("#pv-count"),empty=$("#pv-no-matches"),clear=$("#pv-clear");
if(input&&cat&&cards.length){
 let limit=24,filtered=[];
 const initial=new URLSearchParams(location.search);
 input.value=(initial.get("q")||"").slice(0,90);
 if(Array.from(cat.options).some(x=>x.value===initial.get("category")))cat.value=initial.get("category")||"";
 function apply(writeUrl){
 const q=input.value.trim().toLocaleLowerCase(),category=cat.value;
 filtered=cards.filter(c=>(!category||c.dataset.cat===category)&&(!q||(c.dataset.search||"").includes(q)));
 let shown=0;cards.forEach(c=>{const match=filtered.includes(c);c.hidden=!match||shown>=limit;if(match)shown++;});
 if(count)count.textContent="Showing "+Math.min(limit,filtered.length)+" of "+filtered.length+" matching products";
 if(more){more.hidden=filtered.length<=limit;more.textContent="Show more products ("+(filtered.length-limit)+" remaining) ↓";}
 if(empty)empty.hidden=filtered.length!==0;
 if(writeUrl){const u=new URL(location.href);if(q)u.searchParams.set("q",input.value.trim());else u.searchParams.delete("q");if(category)u.searchParams.set("category",category);else u.searchParams.delete("category");history.replaceState(null,"",u.pathname+u.search+u.hash);}
 }
 input.addEventListener("input",()=>{limit=24;apply(true)});
 cat.addEventListener("change",()=>{limit=24;apply(true)});
 if(clear)clear.addEventListener("click",()=>{input.value="";cat.value="";limit=24;apply(true);input.focus()});
 if(more)more.addEventListener("click",()=>{limit+=24;apply(false)});
 $$("[data-quick-category]").forEach(link=>link.addEventListener("click",e=>{e.preventDefault();cat.value=link.dataset.quickCategory||"";limit=24;apply(true);$("#discover")?.scrollIntoView({behavior:"smooth",block:"start"});}));
 apply(false);
}
})();
