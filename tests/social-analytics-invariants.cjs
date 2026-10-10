// Automated regression invariants for AstraLabs Socials pipeline.
// Run: node tests/social-analytics-invariants.cjs
const assert=require("node:assert/strict"), fs=require("node:fs");
const dash=fs.readFileSync("public/analytics/dashboard-v2.js","utf8");
const socialSource=fs.readFileSync("public/analytics/social-native.js","utf8");
const html=fs.readFileSync("public/analytics/index.html","utf8");
assert.equal((dash.match(/function paintSocial\(\)/g)||[]).length,1);
assert.match(dash,/function paintSocial\(\)\{\s*window\.ASTRA_SOCIAL_NATIVE\?\.render/);
assert.equal((dash.match(/ASTRA_SOCIAL_NATIVE\?\.render/g)||[]).length,1);
assert.match(dash,/b\.addEventListener\("click",\(\)=>\{state\.social=b\.dataset\.social;paintSocial\(\)\}\)/);
assert.match(dash,/renderAll\(\)\{[^}]*paintSocial\(\)/);
assert.doesNotMatch(socialSource,/window\.location\.reload/);
assert.match(socialSource,/state\.socialMetrics\?\.daily/);
assert.match(socialSource,/visible_video_views_total/);
assert.match(socialSource,/board_pin_inventory/);
assert.match(socialSource,/metric_unit/);
assert.match(socialSource,/NOT last 30 days/);
assert.match(socialSource,/dataset\.social===n/);
assert.match(socialSource,/chart\.replaceChildren\(build\("div","empty"/);
assert.match(html,/social-native\.js\?v=2/);
assert.match(html,/dashboard-v2\.js\?v=14/);
console.log("PASS: 14 unified rendering and reporting-scope invariants");
