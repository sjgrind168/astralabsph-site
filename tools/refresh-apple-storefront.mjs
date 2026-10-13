/** Public App Store presence check. Uses only the existing public Supabase anon key. */
import { readFileSync } from 'node:fs';
const cfg = readFileSync(new URL('../public/pirevo/config.js', import.meta.url),'utf8');
const match = cfg.match(/analyticsAnonKey\s*:\s*["']([^"']+)["']/);
if(!match)throw Error('Existing public analytics configuration missing');
const publicAnonKey = match[1];
const url = 'https://cscqulbludoyzsgniits.supabase.co/functions/v1/astralabs-apple-distribution';
const res = await fetch(url, {
  headers: {
    'Authorization': 'Bearer '+publicAnonKey,
    'apikey': publicAnonKey,
    'Accept':'application/json'
  }, signal: AbortSignal.timeout(22000)
});
if(!res.ok)throw Error('Apple public listing API status '+res.status);
const obj=await res.json();
if(!obj.ok||!Array.isArray(obj.apps))throw Error('Invalid Apple public listing response');
for(const [name,id] of [['keepry',6813155959],['astramate',6812828056]]){
  const row=obj.apps.find(r=>r.app_key===name&&r.track_id===id);
  if(!row||!row.available||!row.checked_at)throw Error('Apple PH listing verification missing: '+name);
  const age=Date.now()-Date.parse(row.checked_at);
  if(!Number.isFinite(age)||age>48*3600e3)throw Error('Apple PH listing check stale for '+name);
  console.log(name+': PH listing confirmed, version '+row.version+', checked '+row.checked_at);
  if(row.last_error)console.warn(name+': last refresh warning (cached last successful verification)');
}
console.log('Storefront presence verified. Private App Store Connect metrics are NOT inferred.');
