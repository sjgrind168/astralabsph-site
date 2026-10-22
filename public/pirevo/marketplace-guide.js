/* PIREVO shopper-selected marketplace. Never alters affiliate destinations. */
(function () {
 "use strict";
 if(document.body.classList.contains("pv-home")) return; // Home has dedicated global shopping guidance.
 if(document.querySelector(".pirevo-region-widget")) return;
 var countries=[["US","United States"],["CA","Canada"],["UK","United Kingdom"],["DE","Germany"],["FR","France"],["IT","Italy"],["ES","Spain"],["NL","Netherlands"],["PL","Poland"],["SE","Sweden"],["OTHER","Other country"]];
 var names=Object.fromEntries(countries);
 var found=location.pathname.match(/^\/pirevo\/products\/([a-z0-9-]+)(?:\/|\/index\.html)?$/);
 var slug=found ? found[1] : null;
 // Product pages use the country tool next to the retailer link. Catalog pages put it below browsing cards.
 if(!slug && !/^\/pirevo\/catalog\/?(?:index\.html)?$/.test(location.pathname)) return;
 var widget=document.createElement("section");
 widget.className="pirevo-region-widget";
 widget.setAttribute("aria-label","Amazon international shopping guidance");
 var options=countries.map(function(c){return '<option value="'+c[0]+'">'+c[1]+'</option>';}).join("");
 widget.innerHTML='<div class="pirevo-region-head"><div><span class="pirevo-region-eyebrow">Global shopping</span><strong>Where are you shopping from?</strong></div><a href="/pirevo/international/">International shopping guide ↗</a></div><label class="pirevo-region-select-wrap"><span>Your Amazon marketplace</span><select class="pirevo-region-select" aria-label="Choose shopping country"><option value="">Choose your country</option>'+options+'</select></label><p class="pirevo-region-explainer" aria-live="polite">Choose a marketplace to see OneLink coverage guidance. Product stock and shipping are not guaranteed.</p><p class="pirevo-region-proof" hidden></p>';
 var buy=document.querySelector(".pdp-amazon,a.cta[href*='amazon.com/dp']");
 if(slug && buy){ buy.insertAdjacentElement("afterend",widget); }
 else if(slug){
  var place=document.querySelector(".details,.pdp-buy,main");
  if(!place)return;
  place.append(widget);
 } else {
  var main=document.querySelector("main") || document.body;
  var catalogEnd=main.querySelector("#items");
  if(catalogEnd)catalogEnd.insertAdjacentElement("afterend",widget);
  else main.append(widget);
 }
 var select=widget.querySelector("select"),explain=widget.querySelector(".pirevo-region-explainer"),proof=widget.querySelector(".pirevo-region-proof");
 var evidence=null,storageKey="pirevo_selected_marketplace_v1";
 function restore(){try{return localStorage.getItem(storageKey)||"";}catch(e){return "";}}
 function save(code){try{if(code)localStorage.setItem(storageKey,code);else localStorage.removeItem(storageKey);}catch(e){}}
 function render(){
   var code=select.value;proof.hidden=true;proof.textContent="";
   if(!code){explain.textContent="Choose a marketplace to see OneLink coverage guidance. Product stock and shipping are not guaranteed.";return;}
   if(code==="OTHER"){explain.textContent="Your country is outside the ten currently enabled earning preferences. A regional redirect, product shipping and affiliate coverage cannot be guaranteed. Confirm the destination at Amazon.";return;}
   var country=names[code];
   explain.textContent=country+" is included in PIREVO's currently enabled Global Earning Preferences. Amazon may show an exact or comparable local item after a US-tagged affiliate link. Availability, delivery and the exact referral attribution for this product are not guaranteed.";
   if(slug && evidence && evidence[slug] && evidence[slug][code]){
     var info=evidence[slug][code];
     if(info.model==="checked"){
       proof.hidden=false;
       proof.textContent="Product research note: the corresponding model was observed on Amazon "+country+(info.asin?" (ASIN "+info.asin+")":"")+" on "+info.checked+". This is a dated model-identity check, not a live stock, delivery, or redirect check.";
     }
   }
 }
 select.addEventListener("change",function(){save(select.value);render();});
 var saved=restore();
 if(countries.some(function(c){return c[0]===saved;}))select.value=saved;
 render();
 if(slug)fetch("/pirevo/regional-evidence.json",{credentials:"omit",cache:"no-store"})
   .then(function(r){return r.ok?r.json():null;})
   .then(function(d){if(d && d.products){evidence=d.products;render();}})
   .catch(function(){});
})();
