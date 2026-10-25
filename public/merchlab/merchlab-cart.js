/* Local MerchLab shopping bag. This never adds items to Shopee automatically. */
(()=>{
'use strict';
const KEY='merchlab-ph-shopping-bag-v1',$=id=>document.getElementById(id),fmt=new Intl.NumberFormat('en-PH',{style:'currency',currency:'PHP',maximumFractionDigits:0});
const products=new Map();let saved=restore(),ready=false,visible=false,handoff=false,lastFocus=null;
function restore(){try{const r=JSON.parse(localStorage.getItem(KEY)||'[]');return Array.isArray(r)?r.filter(v=>v&&/^\d{5,18}$/.test(String(v.id))).slice(0,120).map(v=>({id:String(v.id),qty:Math.max(1,Math.min(99,Math.floor(Number(v.qty)||1)))})):[];}catch{return [];}}
function persist(){try{localStorage.setItem(KEY,JSON.stringify(saved));}catch{ /* Storage can be disabled. */ }}
function safeShopee(s){try{const u=new URL(s);return u.protocol==='https:'&&['shopee.ph','www.shopee.ph'].includes(u.hostname)&&/^\/product\/\d+\/\d+\/?$/.test(u.pathname)?u.href:null;}catch{return null;}}
function safeImage(s){try{const u=new URL(s);return u.protocol==='https:'?u.href:null;}catch{return null;}}
function stock(p){return p?Math.min(99,Math.max(0,Math.floor(Number(p.stock)||0))):0;}
function price(p){const n=Number(p?.priceMin);return Number.isFinite(n)&&n>0?n:0;}
function e(t,c,s){const x=document.createElement(t);if(c)x.className=c;if(s!==undefined)x.textContent=s;return x;}
function b(t,c,fn){const x=e('button',c,t);x.type='button';x.addEventListener('click',fn);return x;}
function a(t,url,c){const x=e('a',c,t);x.href=url;return x;}
function totalCount(){return saved.reduce((x,r)=>x+r.qty,0);}
function registerProducts(arr){if(!Array.isArray(arr))return;products.clear();arr.forEach(p=>{if(p&&p.id)products.set(String(p.id),p);});ready=true;render();}
function add(id){
 const p=products.get(String(id));
 if(!ready||!p){notice('Product still loading. Please try again.');return false;}
 if(stock(p)<1||!safeShopee(p.url)){notice('This item is not available in the catalog.');return false;}
 const it=saved.find(x=>x.id===String(id));
 if(it){if(it.qty>=stock(p)){notice('Catalog quantity limit reached.');open();return false;}it.qty++;}
 else saved.push({id:String(id),qty:1});
 handoff=false;persist();render();
 window.MERCHLAB_ANALYTICS?.track('add_to_bag',{product_id:String(id),quantity:1});
 open();return true;
}
function remove(id){saved=saved.filter(x=>x.id!==id);persist();if(!saved.length)handoff=false;render();window.MERCHLAB_ANALYTICS?.track('remove_from_bag',{product_id:String(id)});}
function changeQty(id,n){
 const it=saved.find(x=>x.id===id),p=products.get(id);if(!it)return;
 if(!stock(p))return remove(id);
 it.qty=Math.min(stock(p),Math.max(1,n));persist();handoff=false;render();window.MERCHLAB_ANALYTICS?.track('cart_qty_change',{product_id:String(id),quantity:it.qty});
}
function notice(t){const x=$('bagToast');if(!x)return;x.textContent=t;x.hidden=false;clearTimeout(notice.timer);notice.timer=setTimeout(()=>{x.hidden=true;},2400);}
function open(){
 if(visible)return;
 if($('productDialog')&&!$('productDialog').hidden)$('closeDialog')?.click();
 if($('mobileMenu')?.classList.contains('is-open'))$('menuClose')?.click();
 window.MERCHLAB_ANALYTICS?.track('bag_view');
 lastFocus=document.activeElement;visible=true;$('bagBackdrop').hidden=false;$('merchlabBag').hidden=false;document.body.classList.add('locked');render();$('bagClose').focus();
}
function close(){if(!visible)return;visible=false;$('bagBackdrop').hidden=true;$('merchlabBag').hidden=true;document.body.classList.remove('locked');if(lastFocus?.isConnected)lastFocus.focus();}
function renderItem(it){
 const p=products.get(it.id),row=e('article','bag-item');
 if(!p){row.append(e('p','bag-item-title','No longer in current catalog: '+it.id),b('Remove','bag-remove',()=>remove(it.id)));return row;}
 const imgLink=a('','/merchlab/p/'+it.id+'/','bag-item-image'),src=safeImage(p.cover||p.images?.[0]);
 if(src){const img=e('img');img.src=src;img.alt='';img.loading='lazy';imgLink.append(img);}
 const info=e('div','bag-item-info'),name=a(p.title,'/merchlab/p/'+it.id+'/','bag-item-title');
 info.append(name,e('p','bag-item-price',(Number(p.priceMax)>Number(p.priceMin)?'From ':'')+(price(p)?fmt.format(price(p)):'Check Shopee price')+' · catalog estimate'),e('p','bag-snapshot-note',stock(p)?'Catalog quantity limit: '+stock(p)+' (not live stock)':'Not currently listed as available'));
 const q=e('div','bag-quantity'),less=b('−','bag-qty-button',()=>changeQty(it.id,it.qty-1)),more=b('+','bag-qty-button',()=>changeQty(it.id,it.qty+1));
 less.disabled=it.qty<=1;more.disabled=it.qty>=stock(p);
 less.setAttribute('aria-label','Decrease '+p.title);more.setAttribute('aria-label','Increase '+p.title);
 q.append(less,e('output','bag-qty-value',String(it.qty)),more);info.append(q,b('Remove','bag-remove',()=>remove(it.id)));row.append(imgLink,info);return row;
}
function renderHandoff(it,i){
 const p=products.get(it.id),row=e('div','bag-handoff-item');if(!p){row.append(e('p','','Item unavailable in catalog.'));return row;}
 row.append(e('p','',String(i+1)+'. '+p.title),e('small','','Quantity: '+it.qty+' · choose options on Shopee'));
 const url=safeShopee(p.url);
 if(url){const l=a('Open this item on Shopee ↗',url,'bag-open-shopee');l.target='_blank';l.rel='noopener noreferrer';l.addEventListener('click',()=>{l.textContent='Open again on Shopee ↗';});row.append(l);}
 return row;
}
function render(){
 const n=totalCount(),badge=$('cartCount'),launch=$('shopTrigger');
 if(badge){badge.textContent=String(n);badge.hidden=n===0;badge.setAttribute('aria-label',n+' items in shopping bag');}
 if(launch){launch.setAttribute('aria-label','Open MerchLab shopping bag with '+n+' items');if(launch.classList.contains('bag-static-launch'))launch.textContent='Bag ('+n+')';}
 if(!$('bagItems'))return;
 const list=document.createDocumentFragment();
 if(!ready)list.append(e('p','bag-empty-text','Loading products…'));
 else if(!saved.length){const empty=e('div','bag-empty');empty.append(e('span','bag-empty-icon','♡'),e('h3','','Your bag is waiting.'),e('p','','Save your favorite pieces using Add to Bag.'));list.append(empty);}
 else saved.forEach(it=>list.append(renderItem(it)));
 $('bagItems').replaceChildren(list);
 $('bagTotalLabel').textContent='Estimated subtotal ('+n+' items)';
 $('bagTotal').textContent=ready?fmt.format(saved.reduce((s,x)=>s+price(products.get(x.id))*x.qty,0)):'…';
 $('bagProceed').disabled=!ready||!saved.some(x=>safeShopee(products.get(x.id)?.url));
 $('bagReview').hidden=!handoff||saved.length===0;
 if(handoff){const fragment=document.createDocumentFragment();saved.forEach((it,i)=>fragment.append(renderHandoff(it,i)));$('bagHandoffList').replaceChildren(fragment);$('bagProceed').textContent='Shopee links shown below ↓';}
 else $('bagProceed').textContent='Continue on Shopee ↗';
}
function init(){
 const wrap=e('div');
 wrap.innerHTML=[
 '<div class="merchlab-bag-backdrop" id="bagBackdrop" hidden></div>',
 '<aside id="merchlabBag" class="merchlab-bag" role="dialog" aria-modal="true" aria-labelledby="bagTitle" tabindex="-1" hidden>',
 '<div class="bag-head"><div><p class="bag-eyebrow">MERCHLAB PH / SAVED ON THIS DEVICE</p><h2 id="bagTitle">Your Shopping <em>Bag.</em></h2></div>',
 '<button type="button" id="bagClose" class="bag-close" aria-label="Close shopping bag">×</button></div>',
 '<div class="bag-scroll"><p class="bag-explainer">Collect favorites here. <strong>This is a MerchLab bag, not a synced Shopee cart.</strong></p><div class="bag-items" id="bagItems" aria-live="polite"></div>',
 '<section id="bagReview" class="bag-review" hidden><h3>Continue on Shopee, one item at a time</h3><p>Open each product, select your size, color and quantity, then add it to your cart <strong>on Shopee</strong>. Return here for the next product. Check out through your Shopee cart when finished.</p><div id="bagHandoffList"></div></section></div>',
 '<div class="bag-bottom"><div class="bag-total"><span id="bagTotalLabel">Estimated subtotal</span><strong id="bagTotal">₱0</strong></div>',
 '<p class="bag-total-note">Estimate uses last exported catalog prices. Shipping, final stock, variation prices and discounts are confirmed on Shopee. Nothing is transferred automatically.</p>',
 '<button id="bagProceed" type="button" class="button button-dark bag-proceed">Continue on Shopee ↗</button>',
 '<button id="bagBrowse" type="button" class="button button-outline bag-browse">← Continue shopping</button></div></aside>',
 '<div id="bagToast" class="bag-toast" role="status" aria-live="polite" hidden></div>'].join('');
 document.body.append(wrap);
 $('bagClose').addEventListener('click',close);$('bagBackdrop').addEventListener('click',close);
 $('bagProceed').addEventListener('click',()=>{window.MERCHLAB_ANALYTICS?.track('shopee_handoff_view');handoff=true;render();$('bagReview').scrollIntoView({behavior:'smooth',block:'nearest'});});
 $('bagBrowse').addEventListener('click',()=>{close();if($('catalog'))$('catalog').scrollIntoView({behavior:'smooth'});else location.href='/merchlab/#catalog';});
 document.querySelectorAll('[data-merchlab-add]').forEach(x=>x.addEventListener('click',()=>add(x.dataset.merchlabAdd)));
 if(!$('shopTrigger')){const h=document.querySelector('.site-header .header-inner');if(h){const cart=b('Bag (0)','bag-static-launch',open);cart.id='shopTrigger';cart.setAttribute('aria-controls','merchlabBag');h.append(cart);}}
 document.addEventListener('keydown',ev=>{
  if(!visible)return;
  if(ev.key==='Escape'){ev.stopPropagation();close();}
  if(ev.key==='Tab'){
   const items=[...$('merchlabBag').querySelectorAll('a[href],button:not([disabled])')].filter(x=>x.getClientRects().length);
   const first=items[0],last=items.at(-1);if(!first||!last)return;
   if(ev.shiftKey&&document.activeElement===first){last.focus();ev.preventDefault();}
   else if(!ev.shiftKey&&document.activeElement===last){first.focus();ev.preventDefault();}
  }
 });
 window.addEventListener('storage',ev=>{if(ev.key===KEY){saved=restore();handoff=false;render();}});
 render();if(new URLSearchParams(location.search).has('bag'))setTimeout(open,100);
}
async function staticCatalog(){
 if(!document.body.classList.contains('product-static')&&!document.body.classList.contains('category-static'))return;
 try{const chunks=await Promise.all(Array.from({length:8},(_,i)=>fetch('/merchlab/products-'+(i+1)+'.json').then(r=>{if(!r.ok)throw Error('Catalog not found');return r.json();})));registerProducts(chunks.flat());}
 catch(err){console.warn('[MerchLab Bag] Unable to load catalog',err);notice('Catalog could not load. Try again later.');}
}
window.MerchLabCart={add,open,close,registerProducts,getItems:()=>saved.map(x=>({...x}))};
if(Array.isArray(window.MerchLabCatalog))registerProducts(window.MerchLabCatalog);
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>{init();staticCatalog();});
else{init();staticCatalog();}
})();