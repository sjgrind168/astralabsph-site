/* AstraLabs Mission Control preview v1. Protected owner UI; no embedded provider credentials. */
const API="https://cscqulbludoyzsgniits.supabase.co/functions/v1/astralabs-akashic";
const MOBILE_SUMMARY="https://cscqulbludoyzsgniits.supabase.co/functions/v1/astralabs-mobile-summary";
const $=id=>document.getElementById(id);
const NAV={home:["Business pulse","Verified earnings, active work and what needs attention."],analytics:["Analytics","Apps, KDP, advertising and growth by reporting source."],akame:["AKAME","Dedicated private business assistant chat."],missions:["Tasks","Open work, approvals and ASTRA–AKAME handoffs."],settings:["More","Security, integrations and advanced Akashic records."]};
const state={token:sessionStorage.getItem("astra-akashic-session")||"",snapshot:null,summary:null,view:"home",busy:false,historySlug:"",search:"",syncError:""};
const safe=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const text=v=>safe(v||"");
const date=v=>{if(!v)return"Unknown";const d=new Date(v);return Number.isNaN(d.getTime())?"Unknown":new Intl.DateTimeFormat("en-PH",{timeZone:"Asia/Manila",month:"short",day:"numeric",hour:"numeric",minute:"2-digit"}).format(d)};
const clip=(s,n=190)=>String(s??"").slice(0,n);
const tag=(t,kind="")=>'<span class="tag '+kind+'">'+safe(t)+'</span>';
const alert=(headline,body)=>'<div class="notice"><strong>'+safe(headline)+'</strong>'+safe(body)+'</div>';
function btn(label,action,extra="",cls="outline"){return'<button type="button" class="btn '+cls+' '+extra+'" data-action="'+safe(action)+'">'+safe(label)+'</button>'}
function card(title,inside,cls=""){return'<section class="card panel '+cls+'"><div class="card-head"><h2>'+safe(title)+'</h2></div>'+inside+'</section>'}
function listRow(name,detail="",badge=""){return'<div class="list-row"><div class="row-stack"><div class="row-title">'+safe(name)+'</div><div class="row-meta">'+safe(detail)+'</div></div>'+badge+'</div>'}
function statusTag(s){return tag(s||"unknown",["paused","blocked","failed","error"].includes(String(s).toLowerCase())?"warn":"")}
function lock(){state.token="";state.snapshot=null;state.summary=null;sessionStorage.removeItem("astra-akashic-session");$("app").hidden=true;$("login").hidden=false}
function toast(msg){const n=$("toast");n.textContent=msg;n.hidden=false;clearTimeout(toast._timer);toast._timer=setTimeout(()=>n.hidden=true,4600)}
async function api(method="GET",action="",data=null,params={}){
  if(!state.token)throw Error("Owner passkey is required");
  const u=new URL(API);u.searchParams.set("view",params.view||"dashboard");if(params.slug)u.searchParams.set("slug",params.slug);
  const opt={method,headers:{authorization:"Bearer "+state.token,accept:"application/json"}};
  if(method==="POST"){opt.headers["content-type"]="application/json";opt.body=JSON.stringify({action,data})}
  const res=await fetch(u,opt);
  const body=await res.json().catch(()=>({}));
  if(res.status===401){lock();throw Error("Session expired; unlock again with your passkey.")}
  if(!res.ok||!body.ok)throw Error(String(body.error||"Provider request failed ("+res.status+")"));
  return body;
}
function updateHeader(){
  const [title,sub]=NAV[state.view]||NAV.home;
  $("pageTitle").textContent=title;$("pageSubtitle").textContent=sub;$("viewEyebrow").textContent="OWNER WORKSPACE / "+state.view.toUpperCase();
  const when=state.snapshot?.as_of;const check=when?"Checked "+date(when):"Not yet checked";$("syncLabel").textContent=check;
  $("liveDate").textContent=new Intl.DateTimeFormat("en-PH",{timeZone:"Asia/Manila",dateStyle:"medium"}).format(new Date());
  $("sideStatus").textContent=state.snapshot?"Source: Akashic · "+date(when):"No verified source available";
  for(const b of document.querySelectorAll("[data-tab]")){b.classList.toggle("active",b.dataset.tab===state.view||(b.closest(".mobile-nav")&&b.dataset.tab==="settings"&&["settings"].includes(state.view)))}
}
function nav(view){if(!NAV[view])return;state.view=view;state.search="";state.historySlug="";updateHeader();render();window.scrollTo({top:0,behavior:"instant"})}
async function loadSummary(){
 const request=new Request(MOBILE_SUMMARY,{method:"GET",headers:{authorization:"Bearer "+state.token,accept:"application/json"},cache:"no-store"});
 const res=await fetch(request);const body=await res.json().catch(()=>({}));
 if(!res.ok||!body.ok)throw Error(body.error||"Mobile reporting importer unavailable");
 return body;
}
async function refresh(){
 if(state.busy||!state.token)return;state.busy=true;$("refreshBtn").disabled=true;
 try{
  const [ledger,reports]=await Promise.allSettled([api(),loadSummary()]);
  if(ledger.status==="fulfilled")state.snapshot=ledger.value;
  if(reports.status==="fulfilled")state.summary=reports.value;
  state.syncError=[ledger,reports].filter(x=>x.status==="rejected").map(x=>x.reason?.message||"Provider unavailable").join("; ");
  if(state.snapshot){$("login").hidden=true;$("app").hidden=false;render();if(state.syncError)toast("Some sources are unavailable: "+state.syncError)}
  else if(ledger.status==="rejected")throw ledger.reason;
 }catch(e){state.syncError=e.message;if(state.token){$("login").hidden=true;$("app").hidden=false;render();toast("Sync unavailable: "+e.message)}}
 finally{state.busy=false;$("refreshBtn").disabled=false}
}
function verifiedTasks(){const s=state.snapshot;const checks=new Map((s.checks||[]).map(c=>[c.task_id,c]));return{checks,completed:(s.tasks||[]).filter(t=>checks.get(t.id)?.done).length}}
function inboxRecords(){return(state.snapshot?.records||[]).filter(r=>r.category==="handoff"&&(r.project_slug==="akame-astra-shared-inbox"||String(r.slug).startsWith("akame-astra-")||String(r.slug).startsWith("owner-")))}
function metrics(){
 const s=state.snapshot,{completed}=verifiedTasks(),pending=(s.tasks||[]).length-completed,active=(s.projects||[]).filter(p=>p.status==="active").length,queued=inboxRecords().filter(r=>r.author==="akame"&&String(r.content).includes("Awaiting ASTRA")).length;
 return'<div class="metrics">'+[
 ["Active projects",active,"Akashic registry"],["Today's checks",completed+"/"+(s.tasks||[]).length,"Source-checked actions"],["Open task checks",pending,"Not automatically failed"],["Inbox handoffs",inboxRecords().length,"Signed record versions"]
 ].map(([k,v,h])=>'<article class="card"><div class="metric-label">'+safe(k)+'</div><div class="metric-number">'+safe(v)+'</div><div class="metric-hint">'+safe(h)+'</div></article>').join("")+'</div>';
}
function recentTasks(limit=5){const tasks=state.snapshot?.tasks||[],{checks}=verifiedTasks();if(!tasks.length)return'<div class="empty">No active tasks in the verified ledger.</div>';return tasks.slice(0,limit).map(t=>listRow(t.title,t.area+" · "+clip(t.detail,120),checks.get(t.id)?.done?tag("Checked"):tag("Needs evidence","warn"))).join("")}
function projectCards(items,limit=6){
 if(!items.length)return'<div class="note">No matching projects in the authenticated registry. No placeholders were created.</div>';
 return'<div class="cards-two">'+items.slice(0,limit).map(p=>'<article class="card project-card"><div class="project-kicker"><span class="minor-label">'+safe(p.area||"Project")+'</span>'+statusTag(p.status)+'</div><div class="project-title">'+safe(p.name)+'</div><p class="line-clamp">'+safe(clip(p.summary,260))+'</p><p class="project-next line-clamp">Next: '+safe(clip(p.next_action||"Needs owner review",180))+'</p><p class="subdued">Updated '+date(p.updated_at)+'</p></article>').join("")+'</div>';
}
function platformMetric(provider,metric,app="all"){return(state.summary?.providers||[]).find(r=>r.provider===provider&&r.metric===metric&&(r.app===app||app==="any"))}
function currency(value,unit){const n=Number(value);return Number.isFinite(n)&&unit ? new Intl.NumberFormat("en-PH",{style:"currency",currency:unit}).format(n):"Unavailable"}
function sourceMeta(r){return r?("Through "+(r.period_end||"unknown date")+" · "+(r.status||"report")):"Source not verified"}
function renderBusinessPulse(){
 const groups=state.summary?.apple?.groups||[];
 const apple=groups.length===1?currency(groups[0].proceeds,groups[0].currency):groups.length>1?"See currencies":"Unavailable";
 const applePeriod=groups.length===1?"Through "+groups[0].latest_period:"Separate currencies, never combined";
 const kdp=platformMetric("kdp","royalties_usd"),kdpValue=kdp?currency(kdp.value,kdp.unit):"Unavailable";
 const kdpPeriod=kdp?("Estimated · through "+kdp.period_end):"No dated KDP report";
 return '<div class="metrics business-metrics"><article class="card"><div class="metric-label">Apple developer proceeds</div><div class="metric-number">'+safe(apple)+'</div><div class="metric-hint">'+safe(groups.length?applePeriod:"Private import unavailable")+'</div></article><article class="card"><div class="metric-label">KDP estimated royalties</div><div class="metric-number">'+safe(kdpValue)+'</div><div class="metric-hint">'+safe(kdpPeriod)+'</div></article></div>';
}
function renderAnalytics(){
 const summary=state.summary;
 if(!summary)return alert("Private reporting unavailable",state.syncError||"Unable to fetch a dated source report. Missing is not zero.");
 const app=summary.apple?.groups||[];
 const earnings=app.length?app.map(v=>listRow(v.app+" · developer proceeds",currency(v.proceeds,v.currency)+" · through "+v.latest_period,tag("Imported"))).join(""):'<div class="empty">No Apple daily proceeds imported in the selected window.</div>';
 const payout=platformMetric("google_play","payout_balance_usd");
 const admob=platformMetric("admob","estimated_earnings_usd");
 const kdpRoyalty=platformMetric("kdp","royalties_usd"),kdpUnits=platformMetric("kdp","book_units");
 const playOther=(summary.providers||[]).filter(r=>r.provider==="google_play"&&["device_acquisitions","installed_audience","gross_revenue_usd","one_time_orders"].includes(r.metric));
 const socials=(summary.social||[]).filter(r=>["followers","impressions","views","outbound_clicks","clicks","reach"].some(k=>r.metric.includes(k))).slice(0,12);
 const appRows=playOther.length?playOther.map(r=>listRow((r.app||"all")+" · "+r.metric.replaceAll("_"," "),safe(r.value)+" "+safe(r.unit||"")+" · "+r.period_end,tag("Historical"))).join(""):'<p class="empty">Google Play direct reporting currently has no fresh verified metrics.</p>';
 const socialRows=socials.length?socials.map(r=>listRow(r.network+" · "+r.metric.replaceAll("_"," "),String(r.value)+" "+(r.unit||"")+" · period through "+r.period_end,tag("Snapshot"))).join(""):'<p class="empty">No dated social KPIs loaded.</p>';
 return '<div class="stack">'+
 card("App Store proceeds",earnings)+
 card("Google Play and AdMob",listRow("Google Play payout balance",payout?currency(payout.value,payout.unit)+" · "+sourceMeta(payout):"Unavailable",tag("Payout ≠ sales","warn"))+listRow("AdMob estimated earnings",admob?currency(admob.value,admob.unit)+" · "+sourceMeta(admob):"Unavailable",tag("Estimate","warn")))+
 card("KDP books and royalties",listRow("KDP estimated royalties",kdpRoyalty?currency(kdpRoyalty.value,kdpRoyalty.unit)+" · "+sourceMeta(kdpRoyalty):"Unavailable",tag("Estimate","warn"))+listRow("KDP processed units",kdpUnits?String(kdpUnits.value)+" units · "+sourceMeta(kdpUnits):"Unavailable",tag("Imported")))+
 card("App installs and orders",appRows)+
 card("Social growth snapshots",socialRows)+
 alert("Source integrity","Each item shows its own reporting period and metric meaning. Customer gross, developer proceeds, payout balance and estimated royalties are NEVER added into one total.")+
 '</div>';
}
function renderHome(){
 const s=state.snapshot;
 return renderBusinessPulse()+'<div class="stage-grid"><div class="stack">'+
 '<section class="hero"><div><div class="eyebrow">GOOD OPERATIONS START WITH EVIDENCE</div><h2>Everything important.<br>One clear view.</h2><p>Review the business, ask AKAME to investigate, and coordinate with ASTRA through the secured inbox.</p>'+btn("Ask AKAME ↗","new-request","","")+'</div></section>'+
 card("Today's mission ledger",recentTasks(7)+'<div class="action-row">'+btn("Open all missions","open-missions","","soft")+'</div>')+
 '</div><div class="stack">'+card("Agent availability",'<div class="agent-row"><div class="agent-mark dark">A</div><div><strong>AKAME</strong><p>Mac API observed in prior audit</p></div>'+tag("Cloud not live","warn")+'</div><div class="list-row"><div class="row-stack"><div class="row-title">ASTRA</div><div class="row-meta">On-demand authenticated review via shared Akashic records</div></div>'+tag("Not autonomous","off")+'</div><div class="subdued">No fake “online” status. Worker heartbeats and an unattended executor have not been deployed.</div><div class="action-row">'+btn("Shared inbox","open-inbox","","soft")+'</div>')+
 card("Reporting integrity",alert("No invented business figures","This preview reads Akashic operational records only. Revenue, installs, conversions and sales stay unavailable until each provider's importer passes source verification."))+
 '</div></div><div class="section-space"><div class="section-heading"><div><h2>Projects requiring attention</h2><p>Most recently updated items from the canonical registry</p></div>'+btn("All apps","open-apps","","soft")+'</div>'+projectCards((s.projects||[]).filter(p=>["active","blocked","paused","review"].includes(p.status)),4)+'</div>';
}
function renderAkame(){
 const handoffs=inboxRecords();
 return'<section class="hero"><div><div class="eyebrow">PRIVATE BUSINESS ASSISTANT</div><h2>AKAME. With you,<br>wherever you work.</h2><p>Persistent context and real business evidence come first. Mac-off AI execution requires the upcoming cloud worker.</p>'+btn("Create investigation request","new-request","","")+'</div></section>'+
 '<div class="stage-grid section-space"><div class="stack">'+
 card("AKAME workspace",'<div class="agent-chat"><div class="agent-row"><div class="agent-mark dark">A</div><div><strong>AKAME</strong><p>Mac agent + proposed cloud companion</p></div>'+tag("Bridge pending","warn")+'</div><div class="chat-bubble"><strong>AKAME</strong><br>Business chat is being connected to the shared authenticated backend. I can store an owner request now, but cannot pretend that a cloud LLM already answered.</div><div class="compose-placeholder"><div class="request-box"><strong>Send a task to our shared inbox</strong><p>Request persists under your signed owner identity. It waits for an authorized agent to check it.</p>'+btn("Compose request ↗","new-request","","solid")+'</div></div></div>')+
 '</div><div class="stack">'+card("Intelligence layers",listRow("FreeLLMAPI model router","Mac runtime; automatic fallback code exists",tag("Audited"))+listRow("Hindsight","Mac-local memory; cloud-safe sync not implemented",tag("Local"))+listRow("Coding specialist","Protected local coding tools; needs Mac",tag("Local"))+listRow("ASTRA coordination","Versioned Akashic record handoffs",tag("Manual","warn")))+card("Recent handoffs",handoffs.length?handoffs.slice(0,3).map(r=>listRow(r.title,date(r.created_at)+" · "+r.author)).join(""):'<div class="empty">No handoff records available.</div>')+'</div></div>';
}
function renderApps(){
 const proj=state.snapshot.projects||[];
 const a=proj.filter(p=>/astramate|keepry|shoku|stabilitymax|rude|wrigglegate|ruseshield|scamlens|akame/i.test([p.name,p.slug].join(" ")));
 return'<div class="notice"><strong>App pipeline status</strong>These are project registry records, not Store Connect or Google Play live sales. Missing provider reports are shown as unavailable, never zero.</div><div class="section-space">'+projectCards(a.length?a:proj,12)+'</div><div class="section-space">'+card("Release approval boundary",listRow("iOS builds & TestFlight","Mac-required build and device QA; no silent app submissions",tag("Owner approval","warn"))+listRow("Store commerce","Imports and report periods must be validated by source",tag("Not certified","off")))+'</div>';
}
function renderGrowth(){
 const projects=(state.snapshot.projects||[]).filter(p=>/marketing|growth|social|pirevo|affiliate|pinterest|youtube|tiktok|amazon|kdp|merchlab/i.test([p.area,p.name,p.slug].join(" ")));
 return'<div class="stage-grid"><div class="stack">'+card("Marketing priorities",projectCards(projects,8))+'</div><div class="stack">'+card("Publishing boundaries",listRow("Pinterest","New Pin requires native URL and independent confirmation",tag("Proof required"))+listRow("Facebook / Instagram / YouTube","Authenticated in Composio during prior audit; publish tools still need end-to-end tests",tag("Audit pending","warn"))+listRow("Threads / X / TikTok","No verified autonomous Composio publishing pipeline",tag("Unavailable","off")))+card("Growth intelligence",alert("Recommendations need data","AKAME should research conversion and demand using verified sources, then propose drafts and strategies. Auto-posting is not enabled from this preview."))+'</div></div>';
}
function renderCommerce(){
 return'<div class="notice"><strong>Financial reporting is not connected to this preview.</strong>Do not interpret unavailable provider reports as zero revenue. Provider, currency, report period and source receipts must all match before aggregation.</div><div class="section-space cards-three">'+[
 ["App Store & Play","Private sales and installs importer verification required"],
 ["PIREVO / Amazon","Affiliate commission import not certified"],
 ["KDP / PayMongo","Source-specific royalties and payment receipts required"]
 ].map(([a,b])=>'<article class="card simple-card"><span class="minor-label">NOT REPORTED</span><h3>'+safe(a)+'</h3><p>'+safe(b)+'</p></article>').join("")+'</div><div class="section-space">'+card("Source-of-truth contract",listRow("Value unavailable ≠ ₱0","Preserve null with report freshness and status")+listRow("Cash versus gross","Never combine proceeds, sales, affiliate clicks and commissions")+listRow("Importer integrity","Account, reporting dates and source ID must match"))+'</div>';
}
function renderMissions(){
 const tasks=state.snapshot.tasks||[],checks=verifiedTasks().checks;
 return'<div class="toolbar"><p class="hint">Only authenticated Akashic check entries count as completed.</p>'+btn("+ Request a mission","new-request","","solid")+'</div>'+
 card("Active task ledger",tasks.length?tasks.map(t=>listRow(t.title,clip(t.detail,155)+" · "+t.area,checks.get(t.id)?.done?tag("Checked"):tag("Open","warn"))).join(""):'<div class="empty">No tasks returned from Akashic.</div>')+
 '<div class="section-space">'+card("ASTRA ↔ AKAME inbox",inboxRecords().slice(0,5).map(inboxItem).join("")||"<p class=\"empty\">No handoff record yet.</p>")+"</div>"+'<div class="section-space">'+card("Automatic execution: not yet deployed",alert("Approval is not a worker","The full system requires mission leases, stable idempotency keys, exact-payload owner approvals, heartbeats, execution evidence and rollback policies. These controls are not present in the existing record API. Request creation is available; unattended execution is not."))+'</div>';
}
function inboxItem(r){
 const slug=safe(r.slug);
 return'<div class="list-row"><div class="row-stack" class="history-row"><div class="row-title">'+safe(r.title)+'</div><div class="row-meta">By '+safe(r.author)+' · '+date(r.created_at)+' · version '+safe(r.version)+' · '+safe(r.verification||"unverified")+'</div><p class="hint line-clamp" class="row-gap">'+safe(clip(r.content,350))+'</p><div class="action-row"><button class="btn mini outline" data-action="view-history" data-slug="'+slug+'">Version history</button><button class="btn mini soft" data-action="reply-thread" data-slug="'+slug+'">Owner follow-up</button></div></div></div>';
}
function renderInbox(){
 const inbox=inboxRecords();
 return'<div class="toolbar"><p class="hint">AKAME and ASTRA are separate authenticated actors; owner replies are signed as owner.</p>'+btn("+ New request","new-request","","solid")+'</div>'+
 '<section class="card panel"><div class="card-head"><h2>Dedicated agent handoffs</h2>'+tag(inbox.length+" current records")+'</div>'+
 (inbox.length?inbox.slice(0,60).map(inboxItem).join(""):'<div class="empty">No shared handoffs found in latest Akashic data.</div>')+'</section>'+
 '<div id="historyDetails" class="section-space"></div><div class="section-space">'+alert("Async workflow rule","ASTRA responds only when invoked through an authorized ChatGPT session or configured automation. AKAME's Mac outbox currently checks signed ASTRA versions manually; a continuous runner and push notifications are future work.")+'</div>';
}
function renderRecords(){
 const all=state.snapshot.records||[],q=state.search.toLowerCase(),rows=all.filter(r=>[r.title,r.slug,r.category,r.content].join(" ").toLowerCase().includes(q)).slice(0,100);
 return'<div class="toolbar"><input id="recordSearch" class="search" placeholder="Search source-backed records…" value="'+safe(state.search)+'" aria-label="Search records"><span class="hint">'+all.length+' current records</span></div>'+
 '<section class="card panel">'+(rows.length?rows.map(r=>'<div class="list-row"><div class="row-stack"><div class="row-title">'+safe(r.title)+'</div><div class="row-meta">'+safe(r.category)+' · '+date(r.created_at)+' · '+safe(r.author)+' · v'+safe(r.version)+'</div><p class="hint line-clamp" class="row-gap">'+safe(clip(r.content,240))+'</p><div class="action-row"><button type="button" class="btn mini outline" data-action="view-history" data-slug="'+safe(r.slug)+'">History</button></div></div></div>').join(""):'<div class="empty">No matching records.</div>')+'</section><div class="section-space" id="historyDetails"></div>';
}
function renderSettings(){
 const providers=[["Akashic","Authenticated source in this session","Verified"],["AKAME local runtime","Not queried from this remote browser","Mac only"],["ASTRA automatic runner","Not deployed","Pending"],["Cloud AI failover","Model adapters and spend caps not deployed","Pending"],["Composio provider adapters","Connected through ASTRA; not exposed to web client","Separate auth"],["AMC Telegram","Test message passed in prior audit; no event subscription","Not automated"],["Native sales feeds","Per-provider adapter audit required","Pending"]];
 return'<div class="stage-grid"><div class="stack">'+card("Connection boundaries",'<div class="table-wrap"><table class="clean-table"><thead><tr><th>System</th><th>Current state</th><th>Validation</th></tr></thead><tbody>'+providers.map(a=>'<tr><td>'+safe(a[0])+'</td><td>'+safe(a[1])+'</td><td>'+tag(a[2],a[2]==="Verified"?"":"warn")+'</td></tr>').join("")+'</tbody></table></div>')+'</div><div class="stack">'+card("Owner security",listRow("Authentication","Existing AstraLabs passkey + expiring session",tag("Active"))+listRow("Server-side permissions","Owner requests authored by server; never trust browser identity",tag("Enforced"))+listRow("Execution kill switch","To be built before automatic jobs",tag("Pending","warn"))+'<div class="action-row">'+btn("Lock workspace","lock","","solid")+'</div>')+card("Next engineering gates",listRow("1. Queue + approvals","Authenticated mission and immutable audit events")+listRow("2. One real job","Claim → execute → provider evidence")+listRow("3. Mac-off service","Scoped cloud AI and real model quota checks")+listRow("4. Native iPhone QA","Device build after storage recovery"))+'</div></div>';
}
function render(){
 updateHeader();const stage=$("stage");if(!state.snapshot){stage.innerHTML='<section class="card panel">'+alert("Source unavailable",state.syncError||"Unlock or refresh to request the current Akashic ledger.")+'</section>';return}
 stage.innerHTML=({
 home:renderHome,analytics:renderAnalytics,akame:renderAkame,missions:renderMissions,settings:renderSettings
 }[state.view]||renderHome)();
 const search=$("recordSearch");if(search)search.addEventListener("input",()=>{state.search=search.value;const pos=search.selectionStart;render();const newer=$("recordSearch");newer?.focus();try{newer?.setSelectionRange(pos,pos)}catch{}});
}
function openRequest(item=null){
 if(!state.token){toast("Passkey required");return}
 $("requestForm").reset();$("dialogTitle").textContent=item?"Owner follow-up":"New agent request";
 $("replySlug").value=item?.slug||"";
 if(item){$("requestTitle").value="Follow-up: "+clip(item.title,105);$("requestBody").placeholder="Add evidence, context or next instructions. The original record remains in version history."}
 $("requestDialog").showModal();
}
async function submitRequest(ev){
 ev.preventDefault();if(state.busy)return;
 const title=$("requestTitle").value.trim(),body=$("requestBody").value.trim(),target=$("requestTarget").value,reply=$("replySlug").value;
 if(title.length<2||!body){toast("Subject and instructions required");return}
 const slug=reply||"owner-agent-request-"+new Date().toISOString().slice(0,10).replaceAll("-","")+ "-" +crypto.randomUUID().slice(0,12);
 const payload={slug,project_slug:"akame-astra-shared-inbox",category:"handoff",title,content:"OWNER TO "+target.toUpperCase()+" | MISSION INBOX\n\n"+body+"\n\nRequested status: needs triage. No auto-execution, authorization or provider result implied.",source:"AstraLabs private Mission Control preview; signed owner session",verification:"needs-review"};
 state.busy=true;$("saveRequest").disabled=true;
 try{const updated=await api("POST","record.publish",payload);state.snapshot=updated;$("requestDialog").close();toast("Request saved to Akashic as "+updated.actor+". Awaiting manual agent review.");nav("missions")}
 catch(err){toast("Request not saved: "+err.message)}
 finally{state.busy=false;$("saveRequest").disabled=false}
}
async function showHistory(slug){
 const container=$("historyDetails");if(!container)return;container.innerHTML='<section class="card panel">Checking signed version history…</section>';
 try{
 const d=await api("GET","",null,{view:"history",slug});
 const versions=d.versions||[];container.innerHTML='<section class="card panel"><div class="card-head"><h2>Version history</h2>'+tag(versions.length+" versions")+'</div>'+versions.map(v=>listRow("v"+v.version+" · "+v.author,clip(v.content,900)+" · "+date(v.created_at),tag(v.verification||"unknown"))).join("")+'</section>';
 container.scrollIntoView({behavior:"smooth",block:"nearest"});
 }catch(e){container.textContent="History could not be verified: "+e.message}
}
document.querySelectorAll("[data-tab]").forEach(b=>b.addEventListener("click",()=>nav(b.dataset.tab)));
$("stage").addEventListener("click",ev=>{
 const b=ev.target.closest("[data-action]");if(!b)return;const a=b.dataset.action;
 if(a==="new-request")openRequest();
 else if(a==="open-missions")nav("missions");else if(a==="open-inbox")nav("missions");else if(a==="open-apps"||a==="open-analytics")nav("analytics");
 else if(a==="lock")lock();
 else if(a==="view-history")showHistory(b.dataset.slug);
 else if(a==="reply-thread"){const r=inboxRecords().find(x=>x.slug===b.dataset.slug);if(r)openRequest(r)}
});
$("requestForm").addEventListener("submit",submitRequest);$("cancelRequest").addEventListener("click",()=>$("requestDialog").close());
$("lockBtn").addEventListener("click",lock);$("refreshBtn").addEventListener("click",refresh);
document.addEventListener("akashic:authenticated",ev=>{state.token=ev.detail.token;sessionStorage.setItem("astra-akashic-session",state.token);refresh()});
if(state.token)refresh();else{updateHeader()}
