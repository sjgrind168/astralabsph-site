'use strict';
/**
 * MerchLab PH boutique storefront.
 * Catalog is read-only: IDs, photo URLs, prices and Shopee links are never altered.
 * All checkout links are product-specific destinations from the existing data.
 */
const PRODUCT_FILES = Array.from({length:8},(_,i)=>'./products-'+(i+1)+'.json');
const state = {products:[],featured:[],category:'All',sub:'All',search:'',sort:'default',availableOnly:true,visible:24,active:null,photo:0,returnFocus:null,menuFocus:null};
const $ = id=>document.getElementById(id);
const fmt = new Intl.NumberFormat('en-PH',{style:'currency',currency:'PHP',maximumFractionDigits:0});
const detailDialog=$('productDialog');
const scrim=$('dialogScrim');
const label = x=>String(x??'').replace(/\s+/g,' ').trim();
const text = (el,str)=>{if(el)el.textContent=str;};
const safeImage = raw=>{try{const u=new URL(raw);return u.protocol==='https:'?u.href:null;}catch{return null;}};
const safeShopee = raw=>{try{const u=new URL(raw);return u.protocol==='https:' && (u.hostname==='shopee.ph'||u.hostname==='www.shopee.ph') && /^\/product\/\d+\/\d+/.test(u.pathname)?u.href:null;}catch{return null;}};
const isBag = title=>/\b(bag|tote|pouch|sling|backpack|wallet|handbag|crossbody)\b/i.test(title);
const isJewelry = title=>/\b(earrings?|bracelets?|rings?|necklaces?|pendants?|rosary|anklets?|scapular|bangle|charms?)\b/i.test(title);
function groupOf(p){
  const c=label(p.category).toLowerCase(),t=label(p.title);
  if(isBag(t))return 'Bags';
  if(c==='fashion' && isJewelry(t))return 'Jewelry';
  if(c==='fashion' && /\b(lip tint|makeup|beauty|cosmetic)\b/i.test(t))return 'Accessories';
  if(['rings','necklaces','earrings','bracelets','jewelry'].includes(c))return 'Jewelry';
  if(c==='fashion')return 'Fashion';
  return 'Accessories';
}
function catalogPrice(p){
  if(!Number.isFinite(p.priceMin)||p.priceMin<=0)return null;
  if(Number.isFinite(p.priceMax)&&p.priceMax>p.priceMin)return fmt.format(p.priceMin)+' – '+fmt.format(p.priceMax);
  return fmt.format(p.priceMin);
}
function makeImage(src,alt,{eager=false}={}){
  const img=document.createElement('img');img.alt=alt;img.loading=eager?'eager':'lazy';img.decoding='async';
  const valid=safeImage(src);
  if(valid)img.src=valid;
  img.addEventListener('error',()=>{
    const fallback=document.createElement('span');
    fallback.className='product-image-fallback';
    fallback.textContent='Photo available on Shopee';
    img.replaceWith(fallback);
  },{once:true});
  return img;
}
function makeCard(p){
  const card=document.createElement('article');card.className='product-card';
  const button=document.createElement('button');button.type='button';button.className='product-image-button';
  button.setAttribute('aria-label','View '+label(p.title));
  const img=makeImage(p.cover||p.images?.[0],label(p.title));
  button.append(img);
  const hover=document.createElement('span');hover.className='image-cta';hover.textContent='VIEW DETAILS ↗';button.append(hover);
  button.addEventListener('click',()=>openProduct(p.id));
  const meta=document.createElement('div');meta.className='product-meta';
  const kind=document.createElement('span');kind.textContent=groupOf(p);
  const tag=document.createElement('span');tag.textContent='MERCHLAB EDIT';
  meta.append(kind,tag);
  const h=document.createElement('h3');h.textContent=label(p.title);
  const price=document.createElement('p');price.className='product-price';
  const stored=catalogPrice(p);
  if(stored){price.textContent=stored+' ';const note=document.createElement('span');note.textContent='· catalog price';price.append(note);}
  else price.textContent='See current price on Shopee';
  const action=document.createElement('a');action.href='./p/'+encodeURIComponent(String(p.id))+'/';action.className='product-view';action.textContent='View full details ';
  const arrow=document.createElement('span');arrow.textContent='↗';action.append(arrow);
  card.append(button,meta,h,price,action);
  return card;
}
function displayOrder(products){
  const groups={Fashion:[],Bags:[],Jewelry:[],Accessories:[]};
  products.forEach(p=>groups[groupOf(p)].push(p));
  const sequence=['Fashion','Jewelry','Bags','Jewelry','Fashion','Accessories','Jewelry','Bags'];
  const out=[];let remaining=products.length;
  while(remaining>0){for(const g of sequence){const p=groups[g]?.shift();if(p){out.push(p);remaining--;}}}
  return out;
}
function filteredProducts(){
  let list=(state.category==='All' && state.sort==='default' ?state.featured:state.products).filter(p=>{
    const g=groupOf(p);
    if(state.category!=='All' && g!==state.category)return false;
    if(state.category==='Jewelry' && state.sub!=='All' && p.category!==state.sub && !new RegExp('\\b'+state.sub.slice(0,-1)+'s?\\b','i').test(p.title))return false;
    if(state.availableOnly && !(Number(p.stock)>0))return false;
    const q=state.search.trim().toLowerCase();
    return !q || [p.title,p.category,p.description].some(v=>String(v||'').toLowerCase().includes(q));
  });
  if(state.sort==='title')list.sort((a,b)=>label(a.title).localeCompare(label(b.title)));
  if(state.sort==='price-asc')list.sort((a,b)=>(a.priceMin??Infinity)-(b.priceMin??Infinity));
  if(state.sort==='price-desc')list.sort((a,b)=>(b.priceMin??-Infinity)-(a.priceMin??-Infinity));
  return list;
}
function renderCatalog(){
  const list=filteredProducts(),page=list.slice(0,state.visible),grid=$('productGrid');
  const fragment=document.createDocumentFragment();
  page.forEach(p=>fragment.appendChild(makeCard(p)));
  grid.replaceChildren(fragment);
  text($('resultsStatus'),list.length+' matching items · Showing '+page.length);
  $('emptyState').hidden=list.length>0;
  $('loadMoreWrap').hidden=page.length>=list.length;
  document.querySelectorAll('[data-filter]').forEach(btn=>{
    const on=btn.dataset.filter===state.category;btn.classList.toggle('is-selected',on);btn.setAttribute('aria-pressed',String(on));
  });
  document.querySelectorAll('[data-nav]').forEach(btn=>btn.classList.toggle('is-active',btn.dataset.nav===state.category));
  $('jewelryChips').hidden=state.category!=='Jewelry';
  document.querySelectorAll('[data-sub]').forEach(btn=>{
    const on=btn.dataset.sub===state.sub;btn.classList.toggle('is-selected',on);btn.setAttribute('aria-pressed',String(on));
  });
}
function selectCategory(category,{scroll=true}={}){
  if(!['All','Fashion','Bags','Jewelry','Accessories'].includes(category))category='All';
  state.category=category;state.sub='All';state.visible=24;
  renderCatalog();closeMenu();
  if(scroll)$('catalog').scrollIntoView({behavior:'smooth',block:'start'});
}
function setHeroImage(imgId,buttonId,p){
  if(!p)return;
  const img=$(imgId),url=safeImage(p.cover||p.images?.[0]);
  if(url){img.src=url;img.alt=label(p.title);img.addEventListener('error',()=>{img.alt='Product photo unavailable';},{once:true});}
  const button=$(buttonId);button.setAttribute('aria-label','View '+label(p.title));
  button.addEventListener('click',()=>openProduct(p.id));
}
function sampleBy(group,terms){
  const pool=state.products.filter(p=>groupOf(p)===group&&Number(p.stock)>0&&safeImage(p.cover));
  for(const term of terms){const found=pool.find(p=>label(p.title).toLowerCase().includes(term.toLowerCase()));if(found)return found;}
  return pool[0]||null;
}
function placeCategoryImage(imgId,p){
  if(!p)return;
  const img=$(imgId);const url=safeImage(p.cover||p.images?.[0]);
  if(url){img.src=url;img.alt='';}
}
function setupFeatureImages(){
  const dress=sampleBy('Fashion',['mustard & ivory pleated dress','wide-leg pants','hoodie','jeans']);
  const bag=sampleBy('Bags',['mini l','3-way','leather']);
  const jewelry=sampleBy('Jewelry',['paperclip necklace','mesh bracelet','ring']);
  setHeroImage('heroPrimaryImage','heroPrimary',dress||jewelry);
  setHeroImage('heroSecondaryImage','heroSecondary',bag||jewelry);
  placeCategoryImage('tileFashion',dress);
  placeCategoryImage('tileBags',bag);
  placeCategoryImage('tileJewelry',jewelry);
}
function mediaList(p){
  const list=[p.cover,...(Array.isArray(p.images)?p.images:[])].map(safeImage).filter(Boolean);
  return [...new Set(list)].slice(0,15);
}
function showPhoto(){
  const p=state.active;if(!p)return;
  const images=mediaList(p),url=images[state.photo],target=$('detailImage');
  if(url){target.src=url;target.alt=label(p.title)+' — photo '+(state.photo+1);}
  const buttons=document.createDocumentFragment();
  images.forEach((src,i)=>{
    const b=document.createElement('button');b.type='button';b.className=i===state.photo?'is-active':'';b.setAttribute('aria-label','View photo '+(i+1));
    b.setAttribute('aria-pressed',String(i===state.photo));
    b.append(makeImage(src,label(p.title)+' thumbnail '+(i+1)));
    b.addEventListener('click',()=>{state.photo=i;showPhoto()});buttons.append(b);
  });
  $('detailThumbs').replaceChildren(buttons);
  $('prevImage').hidden=images.length<2;
  $('nextImage').hidden=images.length<2;
}
function updateShareUrl(id){
  const u=new URL(location.href);
  if(id)u.searchParams.set('item',String(id));
  else u.searchParams.delete('item');
  history.pushState({item:id||null},'',u.pathname+u.search+u.hash);
}
function openProduct(id,{push=true}={}){
  const p=state.products.find(x=>String(x.id)===String(id));
  if(!p)return;
  if(!state.active)state.returnFocus=document.activeElement;
  state.active=p;state.photo=0;
  text($('detailCategory'),groupOf(p).toUpperCase()+' / MERCHLAB PH');
  text($('detailTitle'),label(p.title));
  text($('detailPrice'),catalogPrice(p)||'See current price on Shopee');
  text($('detailDescription'),String(p.description||'Check the full product listing for current details and options.'));
  const link=safeShopee(p.url);
  $('detailShopee').href=link||'#';
  $('detailShopee').hidden=!link;
  text($('detailVariants'),'');
  scrim.hidden=false;detailDialog.hidden=false;document.body.classList.add('locked');
  showPhoto();detailDialog.scrollTop=0;
  if(push)updateShareUrl(p.id);
  document.title=label(p.title)+' | MerchLab PH';
  $('detailTitle').focus?.();
  detailDialog.focus();
}
function closeProduct({push=true}={}){
  if(detailDialog.hidden)return;
  detailDialog.hidden=true;scrim.hidden=true;document.body.classList.remove('locked');
  state.active=null;document.title='MerchLab PH | Fashion, Bags & Jewelry | Everyday Style, Elevated';
  if(push)updateShareUrl(null);
  if(state.returnFocus?.isConnected)state.returnFocus.focus();state.returnFocus=null;
}
function changePhoto(delta){
  if(!state.active)return;
  const count=mediaList(state.active).length;
  if(count){state.photo=(state.photo+delta+count)%count;showPhoto();}
}
function openMenu(){
  const menu=$('mobileMenu');state.menuFocus=document.activeElement;
  $('menuBackdrop').hidden=false;menu.classList.add('is-open');menu.setAttribute('aria-hidden','false');menu.inert=false;
  $('menuToggle').setAttribute('aria-expanded','true');$('menuToggle').setAttribute('aria-label','Close menu');
  document.body.classList.add('locked');$('menuClose').focus();
}
function closeMenu(){
  const menu=$('mobileMenu');if(!menu.classList.contains('is-open'))return;
  menu.classList.remove('is-open');menu.setAttribute('aria-hidden','true');menu.inert=true;
  $('menuBackdrop').hidden=true;$('menuToggle').setAttribute('aria-expanded','false');
  $('menuToggle').setAttribute('aria-label','Open menu');
  if(detailDialog.hidden)document.body.classList.remove('locked');
  if(state.menuFocus?.isConnected)state.menuFocus.focus();state.menuFocus=null;
}
function bind(){
  document.querySelectorAll('[data-nav]').forEach(b=>b.addEventListener('click',()=>selectCategory(b.dataset.nav)));
  document.querySelectorAll('[data-filter]').forEach(b=>b.addEventListener('click',()=>selectCategory(b.dataset.filter,{scroll:false})));
  document.querySelectorAll('[data-sub]').forEach(b=>b.addEventListener('click',()=>{
    state.sub=b.dataset.sub;state.visible=24;renderCatalog();
  }));
  document.querySelectorAll('[data-category-card]').forEach(b=>b.addEventListener('click',()=>selectCategory(b.dataset.categoryCard)));
  document.querySelectorAll('[data-scroll-category]').forEach(b=>b.addEventListener('click',()=>selectCategory(b.dataset.scrollCategory,{scroll:false})));
  $('searchTrigger').addEventListener('click',()=>{$('catalog').scrollIntoView({behavior:'smooth'});setTimeout(()=>$('searchInput').focus(),250);});
  $('shopTrigger').addEventListener('click',()=>selectCategory('All'));
  $('searchInput').addEventListener('input',e=>{state.search=e.target.value;state.visible=24;renderCatalog()});
  $('sortSelect').addEventListener('change',e=>{state.sort=e.target.value;state.visible=24;renderCatalog()});
  $('availableOnly').addEventListener('change',e=>{state.availableOnly=e.target.checked;state.visible=24;renderCatalog()});
  $('clearFilters').addEventListener('click',()=>{state.search='';$('searchInput').value='';state.sort='default';$('sortSelect').value='default';state.availableOnly=true;$('availableOnly').checked=true;selectCategory('All',{scroll:false})});
  $('loadMore').addEventListener('click',()=>{state.visible+=24;renderCatalog()});
  $('menuToggle').addEventListener('click',()=>{$('mobileMenu').classList.contains('is-open')?closeMenu():openMenu()});
  $('menuClose').addEventListener('click',closeMenu);$('menuBackdrop').addEventListener('click',closeMenu);
  $('mobileMenu').querySelectorAll('a').forEach(a=>a.addEventListener('click',closeMenu));
  $('closeDialog').addEventListener('click',()=>closeProduct());scrim.addEventListener('click',()=>closeProduct());
  $('prevImage').addEventListener('click',()=>changePhoto(-1));$('nextImage').addEventListener('click',()=>changePhoto(1));
  document.addEventListener('keydown',e=>{
    if(e.key==='Escape'){if(!detailDialog.hidden)closeProduct();else closeMenu();return;}
    if(!detailDialog.hidden){
      if(e.key==='ArrowRight')changePhoto(1);
      if(e.key==='ArrowLeft')changePhoto(-1);
      if(e.key==='Tab')trapFocus(e,detailDialog);
    }else if($('mobileMenu').classList.contains('is-open') && e.key==='Tab')trapFocus(e,$('mobileMenu'));
  });
  addEventListener('popstate',()=>{const id=new URL(location.href).searchParams.get('item');if(id)openProduct(id,{push:false});else closeProduct({push:false})});
}
function trapFocus(e,root){
  const focusable=[...root.querySelectorAll('a[href],button:not([disabled]):not([hidden]),input:not([disabled]),select:not([disabled])')].filter(el=>el.getClientRects().length);
  if(!focusable.length)return;
  const first=focusable[0],last=focusable[focusable.length-1];
  if(e.shiftKey&&document.activeElement===first){last.focus();e.preventDefault();}
  else if(!e.shiftKey&&document.activeElement===last){first.focus();e.preventDefault();}
}
async function init(){
  bind();text($('year'),new Date().getFullYear());
  try{
    const parts=await Promise.all(PRODUCT_FILES.map(async path=>{
      const res=await fetch(path,{cache:'no-cache'});
      if(!res.ok)throw Error('Catalog request failed: '+path+' ('+res.status+')');
      const data=await res.json();if(!Array.isArray(data))throw Error('Invalid catalog data in '+path);
      return data;
    }));
    const seen=new Set();
    state.products=parts.flat().filter(p=>{
      if(!p||!p.id||seen.has(String(p.id)))return false;
      seen.add(String(p.id));return true;
    });
    state.featured=displayOrder(state.products);
    setupFeatureImages();renderCatalog();
    const deepLink=new URL(location.href).searchParams.get('item');
    if(deepLink)openProduct(deepLink,{push:false});
  }catch(error){
    console.error('[MerchLab] Catalog unavailable:',error);
    text($('resultsStatus'),'Unable to load the product catalog right now.');
    const empty=$('emptyState');empty.hidden=false;
    text(empty.querySelector('h3'),'Product listings are temporarily unavailable.');
    text(empty.querySelector('p'),'Please refresh the page to try again.');
    $('clearFilters').textContent='Retry loading';
    $('clearFilters').onclick=()=>location.reload();
  }
}
init();
