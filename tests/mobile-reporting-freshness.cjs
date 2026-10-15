const assert=require('node:assert/strict'),fs=require('node:fs');
const dash=fs.readFileSync('public/analytics/dashboard-v2.js','utf8');
const report=fs.readFileSync('public/analytics/reports.js','utf8');
assert.match(dash,/daysOld>=2/);
assert.match(report,/daysOld>=2/);
assert.match(dash,/app==="all"&&!keepryReported\?null/);
assert.match(dash,/playSourcePeriod=key/);
assert.doesNotMatch(dash,/note\("appInstalled",sourcePeriod\("google_play","installed_audience","keepry"\)\)/);
console.log('PASS: freshness and incomplete Apple coverage');
