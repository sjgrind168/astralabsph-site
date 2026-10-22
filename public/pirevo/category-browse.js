/* Category shop: progressive browsing supports 50 researched items without fabricating rankings. */
(()=>{"use strict";const grid=document.querySelector("main .grid"),panel=document.querySelector(".pv-category-tools");if(!grid||!panel)return;
const search=panel.querySelector('input[type="search"]'),clear=panel.querySelector('[data-clear]'),status=panel.querySelector('[data-count]'),more=panel.querySelector('[data-more]'),cards=Array.from(grid.querySelectorAll('a.card'));let limit=12;const base=location.pathname;
function refresh(writeUrl=false){
 const query=search.value.trim().toLowerCase();let eligible=0,visible=0;
 cards.forEach(card=>{const match=!query||card.textContent.toLowerCase().includes(query);if(match)eligible++;card.hidden=!match||visible>=limit;if(match)visible++;});
 const countShown=Math.min(limit,eligible);status.textContent=countShown+" of "+eligible+" researched products shown";more.hidden=eligible<=limit;
 if(!more.hidden)more.textContent="Show more products ("+(eligible-limit)+" remaining) ↓";
 if(writeUrl){const u=new URL(location.href);if(query)u.searchParams.set("q",search.value.trim());else u.searchParams.delete("q");history.replaceState(null,"",u.pathname+u.search+u.hash);}
}
const q=new URLSearchParams(location.search).get("q")||"";search.value=q.slice(0,95);
search.addEventListener("input",()=>{limit=12;refresh(true)});clear.addEventListener("click",()=>{search.value="";limit=12;refresh(true);search.focus()});more.addEventListener("click",()=>{limit+=12;refresh()});
if(cards.length<12)panel.querySelector(".pv-category-search-row").hidden=true;
refresh(false);
})();
