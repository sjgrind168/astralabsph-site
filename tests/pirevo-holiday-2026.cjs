"use strict";
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const base=path.resolve(__dirname,"../public/pirevo");
const read=p=>fs.readFileSync(path.join(base,p),"utf8");
const store=JSON.parse(read("store-data.js").replace(/^window.PIREVO_STORE\s*=\s*/,"").replace(/;\s*$/,""));
const all=store.products,archived=all.filter(p=>p.archivedSeason==="halloween-2026");
const visible=all.filter(p=>!p.archivedSeason);
assert.equal(all.length,142);
assert.equal(archived.length,15);
assert.equal(visible.length,127);
const home=read("index.html"),cat=read("catalog/index.html"),seasonal=read("categories/seasonal/index.html");
assert.match(home,/CHRISTMAS 2026/);
assert.match(home,/Easier Christmas shopping/);
assert.match(home,/B0HPK81GPN/);
assert.match(home,/animal-coloring-cover.jpg/);
assert.ok(fs.statSync(path.join(base,"animal-coloring-cover.jpg")).size>50000);
assert.doesNotMatch(home,/Halloween Shop \+ Holiday Preview/);
assert.doesNotMatch(home,/Things That Go Coloring Book/);
assert.match(seasonal,/Christmas Decorations/);
assert.doesNotMatch(home,/enabled Amazon earning markets/);
for(const p of archived) {
  const link="/pirevo/products/"+p.slug+"/index.html";
  assert.ok(fs.existsSync(path.join(base,"products",p.slug,"index.html")), "preserve old indexed URL "+p.slug);
  assert.ok(!home.includes('href="'+link+'"'),"archived product in homepage: "+p.slug);
  assert.ok(!cat.includes('href="'+link+'"'),"archived product in catalog: "+p.slug);
  assert.ok(!seasonal.includes('href="'+link+'"'),"archived product in holiday category: "+p.slug);
}
for(const slug of ["homemory-christmas-tree-candles","shareconn-48-prelit-christmas-wreath","lego-botanicals-tiny-plants"]) {
  assert.match(home,new RegExp(slug));
}
console.log("PASS: PIREVO Christmas site, 127 visible products, 15 archived Halloween SKUs with preserved URLs, official KDP book, corrected international copy.");
