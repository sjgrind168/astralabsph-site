// Automated regression invariants for AstraLabs Socials pipeline.
// Run: node tests/social-analytics-invariants.cjs
const assert=require("node:assert/strict"), fs=require("node:fs");
const dash=fs.readFileSync("public/analytics/dashboard-v2.js","utf8");
const module=fs.readFileSync("public/analytics/social-native.js","utf8");
const html=fs.readFileSync("public/analytics/index.html","utf8");
assert.equal((dash.match(/function paintSocial\(\)/g)||[]).length,1);
assert.match(dash,/function paintSocial\(\)\{\s*window\.ASTRA_SOCIAL_NATIVE\?\.render/);
assert.equal((dash.match(/ASTRA_SOCIAL_NATIVE\?\.render/g)||[]).length,1);
assert.match(dash,/b\.addEventListener\("click",\(\)=>\{state\.social=b\.dataset\.social;paintSocial\(\)\}\)/);
assert.match(dash,/renderAll\(\)\{[^}]*paintSocial\(\)/);
assert.doesNotMatch(module,/window\.location\.reload/);
assert.match(module,/state\.socialMetrics\?\.daily/);
assert.match(module,/visible_video_views_total/);
assert.match(module,/board_pin_inventory/);
assert.match(module,/metric_unit/);
assert.match(module,/NOT last 30 days/);
assert.match(module,/dataset\.social===n/);
assert.match(module,/chart\.replaceChildren\(build\("div","empty"/);
assert.match(html,/social-native\.js\?v=2/);
assert.match(html,/dashboard-v2\.js\?v=14/);
console.log("PASS: 14 unified rendering and reporting-scope invariants");
