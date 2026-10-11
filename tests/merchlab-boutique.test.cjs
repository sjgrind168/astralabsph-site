const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=path.resolve(__dirname,'..');
const publicDir=path.join(base,'public','merchlab');
const dist=path.join(base,'dist','merchlab');
const all=Array.from({length:8},(_,i)=>JSON.parse(fs.readFileSync(path.join(publicDir,'products-'+(i+1)+'.json'),'utf8'))).flat();

test('MerchLab retains all 305 unique source catalog IDs from seller export',()=>{
  assert.equal(all.length,305);
  assert.equal(new Set(all.map(p=>String(p.id))).size,305);
});
test('every catalog item retains a product-specific Shopee PH URL',()=>{
  for(const p of all){
    const u=new URL(p.url);
    assert.equal(u.hostname,'shopee.ph');
    assert.match(u.pathname,/^\/product\/\d+\/\d+$/);
    assert.equal(u.pathname.split('/').at(-1),String(p.id));
    assert.ok(p.cover||p.images?.length);
  }
});
test('redesigned homepage loads all eight existing catalog files',()=>{
  const html=fs.readFileSync(path.join(publicDir,'index.html'),'utf8');
  const js=fs.readFileSync(path.join(publicDir,'merchlab.js'),'utf8');
  for(const id of ['catalog','productDialog','mobileMenu','searchInput','how-to-order','contact'])assert.match(html,new RegExp('id="'+id+'"'));
  assert.match(js,/Array\.from\(\{length:8\}/);
  assert.match(html,/merchlab\.css/);
  assert.match(html,/merchlab\.js/);
  assert.doesNotMatch(html,/data:image\/webp;base64/);
});
test('postbuild generates exact-item canonical pages and preserves existing sitemap entries',()=>{
  const sitemap=fs.readFileSync(path.join(base,'dist','sitemap.xml'),'utf8');
  const merchlabSitemap=fs.readFileSync(path.join(dist,'sitemap.xml'),'utf8');
  assert.match(sitemap,/https:\/\/www\.astralabsph\.com\/pirevo\//);
  assert.equal((merchlabSitemap.match(/<loc>/g)||[]).length,310);
  for(const p of all){
    const page=fs.readFileSync(path.join(dist,'p',String(p.id),'index.html'),'utf8');
    assert.ok(page.includes(p.url.replaceAll('&','&amp;')),'Shopee link missing on '+p.id);
    assert.ok(page.includes('rel="canonical"'));
    assert.ok(page.includes('application/ld+json'));
    assert.ok(page.includes('Recorded catalog price')||page.includes('View current price on Shopee'));
  }
  for(const cat of ['fashion','bags','jewelry','accessories'])
    assert.ok(fs.existsSync(path.join(dist,'c',cat,'index.html')));
});

test('official icon, safe external Shopee links and return path are shipped',()=>{
  const logo=path.join(publicDir,'merchlab-official-icon.webp');
  assert.ok(fs.existsSync(logo));
  assert.ok(fs.statSync(logo).size>1500);
  const html=fs.readFileSync(path.join(publicDir,'index.html'),'utf8');
  assert.match(html,/merchlab-official-icon\.webp/);
  assert.match(html,/id="backToMerchlab"/);
  assert.match(html,/id="shopeeReturn"/);
  const js=fs.readFileSync(path.join(publicDir,'merchlab.js'),'utf8');
  assert.match(js,/\$\('detailShopee'\)\.addEventListener/);
  assert.equal(all.find(p=>p.id==='57918501585').priceMin,899);
  assert.ok(all.find(p=>p.id==='52218718352'));
  assert.ok(!all.find(p=>p.id==='28244693035'));
  const generated=fs.readFileSync(path.join(dist,'p','57918501585','index.html'),'utf8');
  assert.match(generated,/target="_blank" rel="noopener noreferrer"/);
  assert.match(generated,/Return to MerchLab products/);
});

test('slashless /merchlab URL resolves storefront assets, catalog and item links to correct absolute paths',()=>{
  const html=fs.readFileSync(path.join(publicDir,'index.html'),'utf8');
  const js=fs.readFileSync(path.join(publicDir,'merchlab.js'),'utf8');
  const base='https://www.astralabsph.com/merchlab';
  assert.match(html,/<base href="\/merchlab\/">/);
  for(const expected of ['/merchlab/merchlab.css','/merchlab/merchlab.js','/merchlab/merchlab-official-icon.webp']){
    assert.ok(html.includes(expected),'Missing absolute resource '+expected);
    assert.equal(new URL(expected,base).pathname,expected);
  }
  assert.match(js, /'\/merchlab\/products-'/);
  assert.match(js, /action\.href='\/merchlab\/p\/'/);
  for(const loc of ['p/57918501585','c/fashion']){
    const generated=fs.readFileSync(path.join(dist,...loc.split('/'),'index.html'),'utf8');
    assert.match(generated,/href="\/merchlab\/merchlab.css\?/);
    assert.match(generated,/src="\/merchlab\/merchlab-official-icon.webp"/);
    assert.match(generated,/href="\/merchlab\/"/);
  }
});
