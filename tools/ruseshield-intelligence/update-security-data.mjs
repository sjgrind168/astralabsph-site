import { createHash, createPublicKey, sign, verify } from 'node:crypto';
import { gunzipSync } from 'node:zlib';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const OUT=resolve(process.env.RUSESHIELD_SECURITY_DATA_OUT || 'security-data-out');
const PRIVATE_KEY_FILE=resolve(process.env.RUSESHIELD_INTEL_SIGNING_KEY_FILE || '');
const PUBLIC_BASE=(process.env.RUSESHIELD_SECURITY_DATA_PUBLIC_BASE || 'https://raw.githubusercontent.com/sjgrind168/astralabsph-site/ruseshield-security-data').replace(/\/$/,'');
const CURRENT_MANIFEST_URL=process.env.RUSESHIELD_CURRENT_MANIFEST_URL || `${PUBLIC_BASE}/manifest.json`;
const appKey=(process.env.PHISHTANK_APP_KEY||'').trim();
const fixturePath=(process.env.RUSESHIELD_PHISHTANK_FIXTURE||'').trim();
const userAgent='RuseShield-Intelligence-Hub/2.0 (+https://www.astralabsph.com/)';
const feedUrl=appKey ? `https://data.phishtank.com/data/${encodeURIComponent(appKey)}/online-valid.json.gz` : 'https://data.phishtank.com/data/online-valid.json.gz';
if(!PRIVATE_KEY_FILE) throw new Error('RUSESHIELD_INTEL_SIGNING_KEY_FILE is required');

const sha256=b=>createHash('sha256').update(b).digest('hex');
function canonical(raw=''){
  try{ const u=new URL(String(raw).trim()); if(!['http:','https:'].includes(u.protocol)) return null; u.hash=''; return u.href; }catch{return null;}
}
function fingerprint(raw=''){ const c=canonical(raw); return c?sha256(c):null; }
function cleanEtag(v=''){ return String(v||'').trim(); }
function etagToken(v=''){ return cleanEtag(v).replace(/[^a-z0-9]/gi,'').slice(0,12).toLowerCase()||'feed'; }
async function safeCurrentManifest(){
  try{ const res=await fetch(`${CURRENT_MANIFEST_URL}${CURRENT_MANIFEST_URL.includes('?')?'&':'?'}check=${Date.now()}`,{headers:{'User-Agent':userAgent}}); return res.ok?await res.json():null; }catch{return null;}
}
async function noUpdate(current,etag){
  await mkdir(OUT,{recursive:true});
  await writeFile(resolve(OUT,'update-status.json'),JSON.stringify({updated:false,reason:'source-etag-unchanged',sourceEtag:etag,version:current?.version||null,checkedAt:new Date().toISOString()},null,2)+'\n');
  console.log(`NO_UPDATE PhishTank ETag unchanged: ${etag}`);
}

const current=fixturePath ? null : await safeCurrentManifest();
const previousEtag=cleanEtag(current?.source?.sourceEtag||'');
let rows, etag='', sourceLastModified='';
if(fixturePath){
  rows=JSON.parse(await readFile(resolve(fixturePath),'utf8'));
  etag='fixture-etag-v1';
  sourceLastModified='fixture';
}else{
  if(appKey && previousEtag){
    try{
      const head=await fetch(feedUrl,{method:'HEAD',headers:{'User-Agent':userAgent,'If-None-Match':previousEtag}});
      const headEtag=cleanEtag(head.headers.get('etag'));
      if(head.status===304 || (head.ok && headEtag && headEtag===previousEtag)){
        await noUpdate(current,headEtag||previousEtag);
        process.exit(0);
      }
      if(!head.ok && head.status!==304) console.warn(`HEAD warning: PhishTank HTTP ${head.status}; continuing with GET.`);
    }catch(err){ console.warn(`HEAD warning: ${err.message}; continuing with GET.`); }
  }
  const res=await fetch(feedUrl,{headers:{'User-Agent':userAgent,'Accept':'application/gzip,application/json'}});
  if(!res.ok) throw new Error(`PhishTank HTTP ${res.status}. Add the free PHISHTANK_APP_KEY secret if anonymous downloads are rate-limited.`);
  const compressed=Buffer.from(await res.arrayBuffer());
  let decoded;
  try{decoded=gunzipSync(compressed);}catch{decoded=compressed;}
  rows=JSON.parse(decoded.toString('utf8'));
  etag=cleanEtag(res.headers.get('etag'));
  sourceLastModified=res.headers.get('last-modified')||'';
  if(previousEtag && etag && etag===previousEtag){ await noUpdate(current,etag); process.exit(0); }
}
if(!Array.isArray(rows)) throw new Error('Unexpected PhishTank feed: expected JSON array.');

const hashes=new Set(); let rejected=0;
for(const row of rows){
  if(String(row?.verified||'').toLowerCase()!=='yes'||String(row?.online||'').toLowerCase()!=='yes') continue;
  const fp=fingerprint(row?.url||''); if(fp) hashes.add(fp); else rejected++;
}
if(hashes.size<1000) throw new Error(`Refusing suspiciously small PhishTank pack: ${hashes.size} records.`);

const generatedAt=new Date().toISOString();
const expiresAt=new Date(Date.now()+26*60*60*1000).toISOString();
const stamp=generatedAt.replace(/[-:]/g,'').replace(/\.\d{3}Z$/,'Z').replace('T','-');
const packVersion=`phishtank-${stamp}-${etagToken(etag)}`;
const pack={
  schemaVersion:2,packVersion,generatedAt,expiresAt,scope:'global-phishing-threats',
  maliciousDomains:[],maliciousUrlHashes:[...hashes].sort(),threatUrlHashAlgorithm:'sha256-canonical-url-v1',urlShorteners:[],brandProfiles:[],recordCount:hashes.size,
  source:{name:'PhishTank',operator:'Cisco Talos Intelligence Group',feed:'online-valid.json.gz',verifiedOnly:true,onlineOnly:true,sourceEtag:etag||null,sourceLastModified:sourceLastModified||null,developerInfo:'https://www.phishtank.org/developer_info.php',terms:'https://phishtank.org/terms.php'},
  notes:'Canonical URL SHA-256 fingerprints derived only from PhishTank verified+online rows. Raw phishing URLs are not published by RuseShield.'
};
const packBytes=Buffer.from(JSON.stringify(pack,null,2)+'\n','utf8');
const privatePem=await readFile(PRIVATE_KEY_FILE,'utf8');
const publicKey=createPublicKey(privatePem);
const spki=publicKey.export({type:'spki',format:'der'});
const keyId=`rs-ed25519-${sha256(spki).slice(0,16)}`;
const signatureBytes=sign(null,packBytes,privatePem);
if(!verify(null,packBytes,publicKey,signatureBytes)) throw new Error('self-verification failed');
const packSha256=sha256(packBytes);
const signature={schemaVersion:1,algorithm:'Ed25519',keyId,packFile:'phishtank-global-v1.json',packVersion,packSha256,signatureBase64:signatureBytes.toString('base64'),signedAt:new Date().toISOString()};
const sigBytes=Buffer.from(JSON.stringify(signature,null,2)+'\n','utf8');
const manifest={
  schemaVersion:2,product:'RuseShield Security Data',channel:'global-phishing',version:packVersion,generatedAt,expiresAt,recordCount:pack.recordCount,
  threatUrlHashAlgorithm:pack.threatUrlHashAlgorithm,
  packUrl:`${PUBLIC_BASE}/phishtank-global-v1.json?v=${packSha256.slice(0,16)}`,
  signatureUrl:`${PUBLIC_BASE}/phishtank-global-v1.sig.json?v=${sha256(sigBytes).slice(0,16)}`,
  sha256:packSha256,sizeBytes:packBytes.length,signatureAlgorithm:'Ed25519',keyId,minimumAppVersion:'0.4.1',
  source:{name:'PhishTank',verifiedOnly:true,onlineOnly:true,sourceEtag:etag||null,sourceLastModified:sourceLastModified||null},
  privacy:'This manifest and pack contain public threat fingerprints only. RuseShield user scan content is never uploaded by this updater.'
};
const trusted={schemaVersion:1,keyId,algorithm:'Ed25519',spkiBase64:spki.toString('base64'),createdFor:'RuseShield Security Data verification'};
await mkdir(OUT,{recursive:true});
await Promise.all([
  writeFile(resolve(OUT,'phishtank-global-v1.json'),packBytes),
  writeFile(resolve(OUT,'phishtank-global-v1.sig.json'),sigBytes),
  writeFile(resolve(OUT,'manifest.json'),JSON.stringify(manifest,null,2)+'\n'),
  writeFile(resolve(OUT,'trusted-key.json'),JSON.stringify(trusted,null,2)+'\n'),
  writeFile(resolve(OUT,'update-status.json'),JSON.stringify({updated:true,version:packVersion,recordCount:pack.recordCount,sourceEtag:etag||null,keyId,sha256:packSha256,generatedAt},null,2)+'\n')
]);
console.log(`PASS RuseShield cloud Security Data: ${pack.recordCount.toLocaleString()} verified online URL fingerprints`);
console.log(`VERSION=${packVersion}`);
console.log(`KEY_ID=${keyId}`);
console.log(`SHA256=${packSha256}`);
console.log(`REJECTED_INVALID_URLS=${rejected}`);
