/**
 * PIREVO Amazon Associates static attribution guard.
 *
 * This verifies site-owned link formatting and catalog completeness.
 * It does NOT send traffic to Amazon, click affiliate links, test a purchase,
 * prove individual referral commissions, or call Amazon's Link Checker API.
 *
 * Current Associates Central Store ID / registered destination checked
 * in the authenticated account on 2026-10-10: pirevo-20,
 * https://www.astralabsph.com/pirevo
 */
"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const ROOT=path.resolve(__dirname,"..");
const PUBLIC=path.join(ROOT,"public","pirevo");
const EXPECTED_TAG="pirevo-20";
const OWN_KDP_BOOK_IDS=new Set(["B0FX95D9LL","B0FXDNX4DV"]);
let checked=0, failures=[];
const fail=(reason)=>failures.push(reason);
const file=(rel)=>fs.readFileSync(path.join(PUBLIC,rel),"utf8");
const source=file("store-data.js");
let store;
try{store=JSON.parse(source.slice(source.indexOf("{"),source.lastIndexOf(";")))}
catch(err){console.error("Failed to parse catalog:",err);process.exit(1)}
const cfg=file("config.js");
if(!cfg.includes('affiliateEnabled:true'))fail("Affiliate program disabled in storefront config");
if(!cfg.includes('amazonAssociateTag:"'+EXPECTED_TAG+'"'))fail("Store config tag no longer matches Associates Central");
if(store.associateTag!==EXPECTED_TAG)fail("Catalog affiliate tag no longer matches Associates Central");
if(!Array.isArray(store.products)||store.products.length<134)fail("Missing or incomplete product catalog (expected >=134)");
const slugs=new Set(),asins=new Set();
for(const p of store.products||[]){
 checked++;
 if(!p.slug||slugs.has(p.slug))fail("Invalid/duplicate slug: "+String(p.slug));
 slugs.add(p.slug);
 if(!/^[A-Z0-9]{10}$/.test(p.asin||""))fail("Invalid ASIN: "+p.slug);
 if(asins.has(p.asin))fail("Duplicate ASIN: "+p.slug);
 asins.add(p.asin);
 let url;
 try{url=new URL(p.amazon)}
 catch {fail("Malformed Amazon URL: "+p.slug);continue}
 if(url.protocol!=="https:"||url.hostname!=="www.amazon.com")
   fail("Unexpected Amazon marketplace/domain: "+p.slug);
 if(url.pathname!=="/dp/"+p.asin)
   fail("Product link ASIN mismatch: "+p.slug);
 if(url.searchParams.getAll("tag").length!==1||url.searchParams.get("tag")!==EXPECTED_TAG)
   fail("Amazon tag missing/incorrect/duplicated: "+p.slug);
 if(url.hash)fail("Unexpected fragment in product affiliate link: "+p.slug);
}
// The buying guides construct URLs through the config and must set the tag.
const guide=file("guide.js");
if(!guide.includes('u.searchParams.set("tag",C.amazonAssociateTag)'))
 fail("Buying guide no longer applies Associates tag to links");
if(!guide.includes("data-shortlist")||!guide.includes("amazonUrl(p.search"))
 fail("Buying guide checkout link construction changed; inspect before shipping");
// Product detail link must use stored product URL directly, not a rewriting intermediary.
const product=file("product.js");
if(!product.includes('href="\${esc(p.amazon)}"'))
 fail("Product detail is no longer using stored affiliate product URL directly");
const shop=file("shop.js");
if(!shop.includes("window.PIREVO_STORE"))
 fail("Catalog rendering disconnected from audited product links");
// Audit any hardcoded external Amazon anchor in PIREVO HTML.
function walk(dir){
 for(const f of fs.readdirSync(dir,{withFileTypes:true})){
  const full=path.join(dir,f.name);
  if(f.isDirectory())walk(full);
  else if(f.name.endsWith(".html")){
   const text=fs.readFileSync(full,"utf8"),rel=path.relative(PUBLIC,full);
   const regex=/<a\b[^>]*\bhref\s*=\s*(["'])(https?:\/\/(?:www\.)?amazon\.com[^"'<>]*)\1/gi;
   for(const match of text.matchAll(regex)){
    let u;try{u=new URL(match[2])}catch{fail("Invalid Amazon anchor: "+rel);continue}
    const m=u.pathname.match(/^\/dp\/([A-Z0-9]{10})$/i);
    // Our own KDP book detail links are not affiliate products.
    if(m&&OWN_KDP_BOOK_IDS.has(m[1])&&
       (rel.startsWith("books/")||rel==="index.html"))continue;
    if(u.searchParams.getAll("tag").length!==1||
      u.searchParams.get("tag")!==EXPECTED_TAG)
      fail("Non-tagged Amazon anchor: "+rel+" / "+u.pathname);
   }
  }
 }
}
walk(PUBLIC);
if(failures.length){
 console.error("PIREVO Amazon affiliate LINK AUDIT FAILED ("+checked+" catalog items checked):");
 failures.forEach((x,i)=>console.error((i+1)+". "+x));
 process.exit(1);
}
console.log("PASS: "+checked+" catalog URLs tagged for "+EXPECTED_TAG+"; ASIN matches, duplicate guard, guide builder and PIREVO static Amazon anchors checked.");
console.log("NOTE: Valid links do not guarantee attributed orders, commissions, item availability, or marketplace compliance.");
