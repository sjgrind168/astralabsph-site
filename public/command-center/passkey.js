const endpoint="https://cscqulbludoyzsgniits.supabase.co/functions/v1/astralabs-akashic-passkey";
const btn=document.getElementById("passkeyButton");
const enroll=document.getElementById("enrollButton");
const info=document.getElementById("passkeyInfo");
const error=document.getElementById("loginError");
let invite=new URLSearchParams(location.hash.slice(1)).get("enroll");
if(invite){
  history.replaceState(null,"",location.pathname+location.search);
  btn.hidden=true;
  enroll.hidden=false;
  info.textContent="Your private invitation is ready. Click below to save a passkey on this device.";
}
if(!window.PublicKeyCredential){
  btn.disabled=true;
  enroll.disabled=true;
  error.textContent="This browser does not support passkeys. Open the page in Safari or a current browser.";
}
const from64=(s)=>Uint8Array.from(atob(s.replace(/-/g,"+").replace(/_/g,"/")+"=".repeat((4-s.length%4)%4)),c=>c.charCodeAt(0));
const to64=(a)=>{let b="";for(const v of new Uint8Array(a))b+=String.fromCharCode(v);return btoa(b).replace(/\+/g,"-").replace(/\//g,"_").replace(/=/g,"")};
async function request(action,values={}){
  const res=await fetch(endpoint,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({action,...values})});
  const data=await res.json().catch(()=>({error:"service_unavailable"}));
  if(!res.ok||!data.ok)throw Error(data.error||"Passkey service unavailable");
  return data;
}
function registrationJSON(c){
  return {id:c.id,rawId:to64(c.rawId),type:c.type,authenticatorAttachment:c.authenticatorAttachment,
    response:{attestationObject:to64(c.response.attestationObject),clientDataJSON:to64(c.response.clientDataJSON),transports:c.response.getTransports?.()||[]},
    clientExtensionResults:c.getClientExtensionResults()};
}
function authenticationJSON(c){
  return {id:c.id,rawId:to64(c.rawId),type:c.type,authenticatorAttachment:c.authenticatorAttachment,
    response:{authenticatorData:to64(c.response.authenticatorData),clientDataJSON:to64(c.response.clientDataJSON),signature:to64(c.response.signature),userHandle:c.response.userHandle?to64(c.response.userHandle):null},
    clientExtensionResults:c.getClientExtensionResults()};
}
async function login(){
 const start=await request("login.start");
 const options=start.options;
 const credential=await navigator.credentials.get({publicKey:{challenge:from64(options.challenge),rpId:options.rpId,timeout:options.timeout||60000,userVerification:"required",allowCredentials:(options.allowCredentials||[]).map(c=>({...c,id:from64(c.id)}))}});
 if(!credential)throw Error("No passkey was selected");
 const result=await request("login.finish",{challenge_id:start.challenge_id,credential:authenticationJSON(credential)});
 document.dispatchEvent(new CustomEvent("akashic:authenticated",{detail:{token:result.token}}));
}
async function register(){
 if(!invite)throw Error("Enrollment invitation expired. Ask Astra to reopen setup.");
 const start=await request("enroll.start",{ticket:invite});
 const o=start.options;
 const credential=await navigator.credentials.create({publicKey:{challenge:from64(o.challenge),rp:{name:o.rp.name,id:o.rp.id},
   user:{id:from64(o.user.id),name:o.user.name,displayName:o.user.displayName},pubKeyCredParams:o.pubKeyCredParams,
   timeout:o.timeout||60000,attestation:o.attestation||"none",authenticatorSelection:o.authenticatorSelection,
   excludeCredentials:(o.excludeCredentials||[]).map(c=>({...c,id:from64(c.id)}))}});
 if(!credential)throw Error("Passkey creation was cancelled");
 const result=await request("enroll.finish",{ticket:invite,challenge_id:start.challenge_id,credential:registrationJSON(credential)});
 invite=null;enroll.hidden=true;btn.hidden=false;
 info.textContent="Passkey registered successfully. You can now unlock with Touch ID / Face ID.";
 document.dispatchEvent(new CustomEvent("akashic:authenticated",{detail:{token:result.token}}));
}
async function guarded(target,task){
 error.textContent="";
 btn.disabled=true;enroll.disabled=true;
 target.textContent=target===enroll?"Setting up passkey…":"Waiting for Touch ID / Passkey…";
 try{await task()}
 catch(ex){error.textContent=(ex.name==="NotAllowedError"?"Passkey cancelled or unavailable. Try again.":ex.message||"Passkey operation failed.");}
 finally{btn.disabled=false;enroll.disabled=false;btn.textContent="Unlock with Touch ID / Passkey ↗";enroll.textContent="Set up my passkey ↗"}
}
btn.addEventListener("click",()=>guarded(btn,login));
enroll.addEventListener("click",()=>guarded(enroll,register));
