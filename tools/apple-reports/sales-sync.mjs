/** AstraLabs PH / Apple Sales Reports: idempotent private pipeline. Node 22; no paid SDKs. */
import {readFileSync} from 'node:fs';
import {createPrivateKey,sign,createHash} from 'node:crypto';
import {gunzipSync} from 'node:zlib';
import {execFileSync} from 'node:child_process';

const local=process.env.APPLE_SYNC_LOCAL==='1';
const home='/Users/wafu';
const fromKeychain=service=>execFileSync('/usr/bin/security',['find-generic-password','-a','wafu','-s',service,'-w'],{encoding:'utf8',stdio:['ignore','pipe','ignore']}).trim();
const issuer=local?fromKeychain('ph.astralabs.apple.asc-issuer-id'):process.env.APPLE_ASC_ISSUER_ID;
const kid=local?'D384D687YJ':process.env.APPLE_ASC_KEY_ID;
const vendor=local?process.env.APPLE_VENDOR_NUMBER:process.env.APPLE_ASC_VENDOR_NUMBER;
const key=local?readFileSync(home+'/Library/Application Support/AstraLabsPH/Secrets/AppStoreConnect/AuthKey_D384D687YJ.p8'):Buffer.from(process.env.APPLE_ASC_P8_B64||'','base64');
if(!/^[a-f0-9-]{36}$/i.test(issuer||'')||!/^[A-Z0-9]{10}$/.test(kid||'')||!/^[0-9]{6,12}$/.test(vendor||'')||key.length<100)throw Error('Apple Team reporting configuration incomplete');
const signer=createPrivateKey(key);
const enc=v=>Buffer.from(JSON.stringify(v)).toString('base64url');
const now=Math.floor(Date.now()/1000);
const msg=enc({alg:'ES256',kid,typ:'JWT'})+'.'+enc({iss:issuer,iat:now-10,exp:now+600,aud:'appstoreconnect-v1'});
const jwt=msg+'.'+sign('sha256',Buffer.from(msg),{key:signer,dsaEncoding:'ieee-p1363'}).toString('base64url');
const headers={authorization:'Bearer '+jwt,accept:'application/json'};
const sha=data=>createHash('sha256').update(data).digest('hex');
const modes=new Set(process.argv.slice(2));
const dry=modes.has('--dry-run');
const backfill=modes.has('--backfill')?40:10;
const fixed=process.env.APPLE_REPORT_TEST_DATE;
const known=new Map([['6813155959','keepry'],['6812828056','astramate']]);
const wait=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function request(url,options={}){
 for(let attempt=0;attempt<3;attempt++){
  const r=await fetch(url,{...options,signal:AbortSignal.timeout(20000)});
  if((r.status===429||r.status>=500)&&attempt<2){await wait(1200*(attempt+1));continue}
  return r;
 }
 throw Error('Apple request exhausted retries');
}
const appsResponse=await request('https://api.appstoreconnect.apple.com/v1/apps?limit=200',{headers});
if(!appsResponse.ok)throw Error('Apple app list authorization failed HTTP '+appsResponse.status);
const apps=(await appsResponse.json()).data||[];
const skuByApp=new Map();
for(const a of apps)if(known.has(a.id))skuByApp.set(String(a.attributes?.sku||''),known.get(a.id));
if(![...known.keys()].every(id=>apps.some(a=>a.id===id)))throw Error('Both expected Apple apps must be visible to this key');
console.log('APPLE_TEAM_AUTH_OK; TRACKED_APPS=Keepry,Astramate; MODE='+(dry?'DRY_RUN':'PRIVATE_IMPORT'));
const dateList=[];
for(let n=1;n<=backfill;n++){const d=new Date(Date.now()-n*86400000);dateList.push(d.toISOString().slice(0,10))}
if(fixed){dateList.splice(0,dateList.length,fixed)}
let sent=0,sourceRows=0,skipped=0,noSales=0;
for(const date of dateList){
 const url=new URL('https://api.appstoreconnect.apple.com/v1/salesReports');
 for(const [key,value]of Object.entries({'filter[frequency]':'DAILY','filter[reportDate]':date,
 'filter[reportType]':'SALES','filter[reportSubType]':'SUMMARY','filter[vendorNumber]':vendor,'filter[version]':'1_0'}))url.searchParams.set(key,value);
 const res=await request(url,{headers:{...headers,accept:'application/a-gzip'}});
 let status='available', source='',rows=[],lineCount=0,unknown=0;
 if(res.status===404){
  const error=await res.json().catch(()=>null);
  const details=(error?.errors||[]).map(x=>x.detail||'').join(' ');
  if(!/There were no sales for the date specified/i.test(details))throw Error(date+': Apple report unavailable (not a no-sales confirmation)');
  status='no_sales';noSales++;
  source=sha('Apple SALES SUMMARY '+date+' official no sales response');
 }else if(!res.ok){throw Error(date+': Apple Sales report HTTP '+res.status)}
 else{
  const compressed=Buffer.from(await res.arrayBuffer());
  if(compressed[0]!==31||compressed[1]!==139)throw Error(date+': Apple Sales report not gzip');
  source=sha(compressed);
  const lines=gunzipSync(compressed).toString('utf8').trim().split(/\r?\n/);
  const cols=lines.shift().split('\t');
  const pos=name=>cols.indexOf(name);
  for(const field of ['Product Type Identifier','Units','Apple Identifier','Customer Price','Customer Currency','Developer Proceeds','Currency of Proceeds'])if(pos(field)<0)throw Error(date+': report field missing: '+field);
  lineCount=lines.length; sourceRows+=lineCount;
  const map=new Map();
  for(const line of lines){
   const cells=line.split('\t');
   const field=name=>String(cells[pos(name)]||'').trim();
   const product=field('Product Type Identifier').toUpperCase();
   const appleId=field('Apple Identifier');
   const sku=field('Parent Identifier')||field('SKU');
   const app=known.get(appleId)||skuByApp.get(sku);
   if(!app){unknown++;continue}
   if(!/^[A-Z0-9_-]{1,15}$/.test(product))throw Error(date+': unexpected Apple product type');
   const units=Number(field('Units')),price=Number(field('Customer Price')),proceeds=Number(field('Developer Proceeds'));
   if(![units,price,proceeds].every(Number.isFinite))throw Error(date+': invalid numeric row');
   const ccy=(field('Customer Currency')||'XXX').toUpperCase(),pcy=(field('Currency of Proceeds')||'XXX').toUpperCase();
   if(!/^[A-Z]{3}$/.test(ccy)||!/^[A-Z]{3}$/.test(pcy))throw Error(date+': invalid currency code');
   if((ccy==='XXX'&&price!==0)||(pcy==='XXX'&&proceeds!==0))throw Error(date+': nonzero value without currency code');
   const id=[app,product,ccy,pcy].join('|');
   const x=map.get(id)||{app_key:app,product_type:product,customer_currency:ccy,proceeds_currency:pcy,
      units:0,gross_customer_native:0,developer_proceeds_native:0};
   x.units+=units;x.gross_customer_native+=units*price;x.developer_proceeds_native+=units*proceeds;map.set(id,x);
  }
  rows=[...map.values()].map(v=>({...v,units:Number(v.units.toFixed(2)),gross_customer_native:Number(v.gross_customer_native.toFixed(4)),developer_proceeds_native:Number(v.developer_proceeds_native.toFixed(4))}));
 }
 if(dry){console.log(date,status,'SOURCE_ROWS',lineCount,'TRACKED_GROUPS',rows.length,'UNATTRIBUTED_ROWS',unknown)}
 else{
  const req=await request('https://cscqulbludoyzsgniits.supabase.co/functions/v1/astralabs-apple-sales-ingest',{method:'POST',headers:{authorization:'Bearer '+jwt,'content-type':'application/json'},body:JSON.stringify({report_date:date,status,source_sha256:source,source_row_count:lineCount,rows})});
  if(!req.ok)throw Error(date+': secure Apple source ingest HTTP '+req.status);
  const result=await req.json();if(!result.ok)throw Error(date+': destination did not confirm import');
  console.log(date,'VERIFIED_API_IMPORT',status,'GROUPS',result.tracked_groups,'UNATTRIBUTED',unknown);
  sent++;
 }
 skipped+=unknown;
 await wait(200);
}
console.log('APPLE_SYNC_COMPLETED; DAYS='+dateList.length+'; WRITTEN='+sent+'; NO_SALES_DATES='+noSales+'; RAW_ROWS='+sourceRows+'; UNATTRIBUTED_ROWS='+skipped);
