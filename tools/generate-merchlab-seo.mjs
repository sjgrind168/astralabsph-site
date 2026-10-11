/**
 * Build-time, zero-dependency MerchLab PH static SEO pages.
 * Runs AFTER Vite copies the existing public files to dist/.
 * Never writes to PIREVO, the source catalog, or unrelated production files.
 */
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const source=path.join(repo,'public','merchlab');
const output=path.join(repo,'dist','merchlab');
const origin='https://www.astralabsph.com/merchlab/';
const parts=await Promise.all(Array.from({length:8},(_,i)=>readFile(path.join(source,'products-'+(i+1)+'.json'),'utf8').then(JSON.parse)));
const catalog=parts.flat();
const names=new Set();
for(const p of catalog){
  if(!/^\d+$/.test(String(p.id))||names.has(String(p.id)))throw Error('Invalid/duplicate MerchLab product ID: '+p.id);
  names.add(String(p.id));
}
const esc=s=>String(s??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;');
const clean=s=>String(s??'').replace(/\s+/g,' ').trim();
const image=s=>{try{const u=new URL(s);return u.protocol==='https:'?u.href:null}catch{return null}};
const shopee=s=>{try{const u=new URL(s);return u.protocol==='https:'&&['shopee.ph','www.shopee.ph'].includes(u.hostname)&&/^\/product\/\d+\/\d+/.test(u.pathname)?u.href:null}catch{return null}};
const bag=s=>/\b(bag|tote|pouch|sling|backpack|wallet|handbag|crossbody)\b/i.test(s);
const jewelry=s=>/\b(earrings?|bracelets?|rings?|necklaces?|pendants?|rosary|anklets?|scapular|bangle|charms?)\b/i.test(s);
function category(p){
  const raw=clean(p.category).toLowerCase(),t=clean(p.title);
  if(bag(t))return 'Bags';
  if(raw==='fashion' && jewelry(t))return 'Jewelry';
  if(raw==='fashion' && /\b(lip tint|makeup|beauty|cosmetic)\b/i.test(t))return 'Accessories';
  if(['rings','necklaces','earrings','bracelets','jewelry'].includes(raw)||raw==='fashion'&&jewelry(t))return 'Jewelry';
  if(raw==='fashion')return 'Fashion';
  return 'Accessories';
}
const money=new Intl.NumberFormat('en-PH',{style:'currency',currency:'PHP',maximumFractionDigits:0});
const catalogPrice=p=>Number.isFinite(p.priceMin)&&p.priceMin>0?(Number.isFinite(p.priceMax)&&p.priceMax>p.priceMin?money.format(p.priceMin)+' – '+money.format(p.priceMax):money.format(p.priceMin)):null;
function docHead(title,desc,url,photo,schema){
  return '<!doctype html><html lang="en-PH"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#f8f5ef"><title>'+esc(title)+'</title><meta name="description" content="'+esc(desc)+'"><link rel="canonical" href="'+esc(url)+'"><meta property="og:type" content="'+(schema?'product':'website')+'"><meta property="og:title" content="'+esc(title)+'"><meta property="og:description" content="'+esc(desc)+'"><meta property="og:url" content="'+esc(url)+'">'+(photo?'<meta property="og:image" content="'+esc(photo)+'">':'')+'<link rel="stylesheet" href="'+(schema?'../../merchlab.css':'../../merchlab.css')+'">'+(schema?'<script type="application/ld+json">'+JSON.stringify(schema).replace(/</g,'\\u003c')+'</script>':'')+'</head>';
}
const productUrls=[];
const categoryUrls=[];
const groups={Fashion:[],Bags:[],Jewelry:[],Accessories:[]};
for(const p of catalog){
  const id=String(p.id),name=clean(p.title),cat=category(p),link=shopee(p.url),photo=image(p.cover||p.images?.[0]);
  if(!link)throw Error('Invalid Shopee product destination for '+id);
  groups[cat].push(p);
  const uri=origin+'p/'+id+'/';
  const summary=clean(p.description).slice(0,250)||'Explore this curated MerchLab item and check current price and availability on Shopee Philippines.';
  const desc=summary.slice(0,156);
  const ld={'@context':'https://schema.org','@type':'Product',name,url:uri,sku:id,description:summary};
  if(photo)ld.image=[photo];
  const pictures=[...new Set([p.cover,...(Array.isArray(p.images)?p.images:[])].map(image).filter(Boolean))].slice(0,5);
  const thumbs=pictures.map((src,i)=>'<img src="'+esc(src)+'" alt="'+esc(name)+' product photo '+(i+1)+'" loading="'+(i?'lazy':'eager')+'">').join('');
  const price=catalogPrice(p);
  const html=docHead(name+' | MerchLab PH',desc,uri,photo,ld)+
    '<body class="product-static"><header class="site-header"><div class="container header-inner"><a class="brand" href="../../"><span class="brand-mark" aria-hidden="true">ml</span><span class="brand-word">MerchLab<span class="brand-dot">.</span></span></a><a class="text-link" href="../../#catalog">← Back to collection</a></div></header>'+
    '<main class="container static-main"><nav class="static-crumb" aria-label="Breadcrumb"><a href="../../">Home</a> / <a href="../../c/'+cat.toLowerCase()+'/">'+esc(cat)+'</a> / Product</nav><div class="static-layout"><div class="static-gallery">'+thumbs+'</div><div class="static-detail"><p class="section-kicker">THE MERCHLAB EDIT / '+esc(cat.toUpperCase())+'</p><h1>'+esc(name)+'</h1><p class="detail-price">'+(price?esc(price)+' <small>Recorded catalog price</small>':'View current price on Shopee')+'</p><p class="detail-price-note">Actual prices, variations, stock and delivery details must be confirmed on Shopee.</p><div class="static-description">'+esc(p.description||'Review the original seller listing for the latest product details.')+'</div><a class="button button-dark detail-shop" href="'+esc(link)+'" target="_blank" rel="noopener noreferrer">View exact item on Shopee ↗</a><p class="detail-note">Checkout is completed on Shopee Philippines. Item photographs are sourced from the catalog.</p></div></div></main><footer class="static-footer"><a href="../../">MerchLab PH</a> · Everyday style, elevated.</footer></body></html>';
  const file=path.join(output,'p',id,'index.html');await mkdir(path.dirname(file),{recursive:true});await writeFile(file,html);
  productUrls.push(uri);
}
for(const [cat,list] of Object.entries(groups)){
  const uri=origin+'c/'+cat.toLowerCase()+'/';
  const desc='Browse MerchLab PH '+cat.toLowerCase()+' products with original listing photos and exact-item Shopee Philippines checkout.';
  const cards=list.map(p=>'<a class="static-product-card" href="../../p/'+esc(p.id)+'/">'+(image(p.cover)?'<img src="'+esc(image(p.cover))+'" alt="'+esc(p.title)+'" loading="lazy">':'')+'<span>'+esc(p.title)+'</span></a>').join('');
  const html=docHead(cat+' | MerchLab PH Collection',desc,uri,null,null)+
    '<body class="category-static"><header class="site-header"><div class="container header-inner"><a class="brand" href="../../"><span class="brand-mark" aria-hidden="true">ml</span><span class="brand-word">MerchLab<span class="brand-dot">.</span></span></a><a class="text-link" href="../../#catalog">Shop all products ↗</a></div></header><main class="container static-main"><nav class="static-crumb" aria-label="Breadcrumb"><a href="../../">Home</a> / '+esc(cat)+'</nav><p class="section-kicker">MERCHLAB PH / COLLECTION</p><h1 class="static-category-heading">'+esc(cat)+'<em>.</em></h1><p class="static-category-desc">'+esc(desc)+'</p><div class="static-products">'+cards+'</div></main><footer class="static-footer"><a href="../../">MerchLab PH</a> · Shopping checkout via Shopee Philippines</footer></body></html>';
  const file=path.join(output,'c',cat.toLowerCase(),'index.html');await mkdir(path.dirname(file),{recursive:true});await writeFile(file,html);
  categoryUrls.push(uri);
}
const urls=[origin,...categoryUrls,...productUrls];
const locs=urls.map(url=>'  <url><loc>'+esc(url)+'</loc></url>').join('\n');
await writeFile(path.join(output,'sitemap.xml'),'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+locs+'\n</urlset>\n');
const mainSitemap=path.join(repo,'dist','sitemap.xml');
const root=await readFile(mainSitemap,'utf8');
if(!root.includes('</urlset>'))throw Error('Cannot extend root sitemap safely');
const remaining=urls.filter(uri=>!root.includes('<loc>'+esc(uri)+'</loc>'));
if(remaining.length)await writeFile(mainSitemap,root.replace('</urlset>',remaining.map(uri=>'  <url><loc>'+esc(uri)+'</loc></url>').join('\n')+'\n</urlset>'));
console.log('[MerchLab SEO] Generated '+productUrls.length+' product pages, '+categoryUrls.length+' categories and 2 sitemaps. Unrelated source files unchanged.');
