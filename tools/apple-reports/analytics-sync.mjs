/** AstraLabs official App Store Connect App Analytics report-request bootstrap. */
import {createPrivateKey,sign} from 'node:crypto';
const issuer=process.env.APPLE_ASC_ISSUER_ID,kid=process.env.APPLE_ASC_KEY_ID;
const key=Buffer.from(process.env.APPLE_ASC_P8_B64||'','base64');
if(!/^[0-9a-f-]{36}$/i.test(issuer||'')||!/^([A-Z0-9]{10})$/.test(kid||'')||key.length<100)throw Error('Apple key unavailable');
const enc=o=>Buffer.from(JSON.stringify(o)).toString('base64url');
const t=Math.floor(Date.now()/1000),head=enc({alg:'ES256',kid,typ:'JWT'});
const body=enc({iss:issuer,iat:t-10,exp:t+600,aud:'appstoreconnect-v1'});
const unsigned=head+'.'+body;
const jwt=unsigned+'.'+sign('sha256',Buffer.from(unsigned),{key:createPrivateKey(key),dsaEncoding:'ieee-p1363'}).toString('base64url');
const base='https://api.appstoreconnect.apple.com/v1';
async function api(url,opts={}){
 const r=await fetch(url,{...opts,headers:{authorization:'Bearer '+jwt,accept:'application/json',...(opts.body?{'content-type':'application/json'}:{})},signal:AbortSignal.timeout(24000)});
 const b=await r.json().catch(()=>({}));
 return {status:r.status,body:b};
}
const names=new Map([['6812828056','Astramate'],['6813155959','Keepry']]);
let created=0,existing=0,blocked=0;
for(const [appId,name] of names){
 const {status,body}=await api(base+'/apps/'+appId+'/analyticsReportRequests?limit=200');
 if(status!==200){console.log('APPLE_ANALYTICS_READ_ERROR',name,status,(body.errors||[]).map(x=>x.code).join(','));blocked++;continue}
 const requests=(body.data||[]).filter(x=>x.attributes?.accessType==='ONGOING'&&x.attributes?.stoppedDueToInactivity!==true);
 if(requests.length){existing++;console.log('APPLE_ANALYTICS_ONGOING_ALREADY_ACTIVE',name,requests.length);continue}
 const input={data:{type:'analyticsReportRequests',attributes:{accessType:'ONGOING'},relationships:{app:{data:{type:'apps',id:appId}}}}};
 const result=await api(base+'/analyticsReportRequests',{method:'POST',body:JSON.stringify(input)});
 if(result.status===201||result.status===200){created++;console.log('APPLE_ANALYTICS_ONGOING_CREATED',name)}
 else{blocked++;console.log('APPLE_ANALYTICS_INITIAL_REQUEST_REQUIRES_ADMIN',name,'HTTP',result.status,'CODES',(result.body.errors||[]).map(x=>x.code).join(','))}
}
console.log('APPLE_ANALYTICS_BOOTSTRAP',JSON.stringify({created,existing,blocked}));
if(blocked)process.exitCode=2;
