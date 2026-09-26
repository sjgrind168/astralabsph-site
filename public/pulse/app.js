const API = 'https://cscqulbludoyzsgniits.supabase.co/functions/v1/pulse-api';
const PROVIDERS = {
  google: { title: 'Google', subtitle: 'Play statistics · optional AdMob / GA4 / YouTube', children: ['google_play','admob','ga4','youtube'] },
  meta: { title: 'Meta', subtitle: 'Facebook · Instagram', children: ['facebook','instagram'] },
  threads: { title: 'Threads', subtitle: 'Profile & account insights', children: ['threads'] },
  tiktok: { title: 'TikTok', subtitle: 'Profile & recent video stats', children: ['tiktok'] },
  pinterest: { title: 'Pinterest', subtitle: 'Organic account analytics', children: ['pinterest'] },
};
const SOCIAL = ['facebook','instagram','threads','tiktok','pinterest','youtube'];
const state = { key: localStorage.getItem('astra_pulse_key') || '', period: 30, data: null, view: 'overview' };

const $ = (s, root=document) => root.querySelector(s);
const $$ = (s, root=document) => [...root.querySelectorAll(s)];
const fmt = n => {
  const x = Number(n || 0);
  if (Math.abs(x) >= 1e6) return `${(x/1e6).toFixed(x>=1e7?0:1)}M`;
  if (Math.abs(x) >= 1e3) return `${(x/1e3).toFixed(x>=1e4?0:1)}K`;
  return new Intl.NumberFormat('en-US',{maximumFractionDigits:1}).format(x);
};
const money = (n,c='PHP') => {
  try { return new Intl.NumberFormat('en-PH',{style:'currency',currency:c,maximumFractionDigits:2}).format(Number(n||0)); }
  catch { return `${c||''} ${Number(n||0).toFixed(2)}`; }
};
const timeAgo = iso => {
  if (!iso) return 'Never';
  const min = Math.max(0, Math.floor((Date.now()-new Date(iso).getTime())/60000));
  if (min < 1) return 'Just now';
  if (min < 60) return `${min}m ago`;
  if (min < 1440) return `${Math.floor(min/60)}h ago`;
  return `${Math.floor(min/1440)}d ago`;
};
const niceMetric = s => s.replaceAll('_',' ').replace(/\b\w/g,c=>c.toUpperCase());
function toast(msg){ const t=$('#toast'); t.textContent=msg; t.classList.remove('hidden'); clearTimeout(toast.t); toast.t=setTimeout(()=>t.classList.add('hidden'),3500); }
function notice(msg,type=''){ const n=$('#notice'); if(!msg){n.classList.add('hidden');return} n.textContent=msg;n.className=`notice ${type}`; }
async function api(path, opts={}) {
  const res = await fetch(`${API}${path}`, {
    ...opts,
    headers: { 'Content-Type':'application/json', 'x-pulse-key':state.key, ...(opts.headers||{}) },
  });
  const text = await res.text();
  let data={}; try{data=text?JSON.parse(text):{}}catch{data={error:text}}
  if(!res.ok) throw new Error(data.error||`HTTP ${res.status}`);
  return data;
}
function metricRows(provider=null, metric=null){
  return (state.data?.metrics||[]).filter(x=>(!provider||x.provider===provider)&&(!metric||x.metric===metric));
}
function latestRows(provider=null, metric=null){
  const rows=metricRows(provider,metric), map=new Map();
  for(const r of rows){const k=`${r.provider}|${r.account_id}|${r.entity_type}|${r.entity_id}|${r.metric}`; const old=map.get(k); if(!old||r.day>old.day)map.set(k,r)}
  return [...map.values()];
}
function sumLatest(provider, metric){ return latestRows(provider,metric).reduce((a,r)=>a+Number(r.value||0),0); }
function sumAll(provider, metric){ return metricRows(provider,metric).reduce((a,r)=>a+Number(r.value||0),0); }
function connector(id){ return (state.data?.connectors||[]).find(x=>x.provider===id)||{provider:id,label:id,status:'not_configured'}; }

async function load(period=state.period){
  state.period=Number(period);
  try{
    const data=await api(`/dashboard?period=${state.period}`);
    state.data=data;
    $('#lock').classList.add('hidden'); $('#app').classList.remove('hidden');
    render();
    const p=new URLSearchParams(location.search);
    if(p.get('connected')){toast(`${p.get('connected')} authorization received. Run Sync now.`); history.replaceState({},'',location.pathname);}
    if(p.get('oauth_error')){notice(decodeURIComponent(p.get('oauth_error')),'error'); history.replaceState({},'',location.pathname);}
  }catch(e){
    if(String(e.message).includes('unauthorized')){localStorage.removeItem('astra_pulse_key'); state.key=''; $('#lock').classList.remove('hidden');$('#app').classList.add('hidden');$('#lockError').textContent='That key did not unlock Astra Pulse.';}
    else toast(e.message);
  }
}
function render(){
  $('#lastUpdated').textContent=`Dashboard generated ${timeAgo(state.data?.generated_at)} · ${state.period}-day window`;
  $('#trendLabel').textContent=`${state.period} DAYS`;
  renderKpis(); renderTrend(); renderConnectorMini(); renderPlay(); renderSocialSummary(); renderApps(); renderSocialCards(); renderSources();
}
function renderKpis(){
  const gaUsers=sumAll('ga4','active_users');
  const installs=sumAll('google_play','installs');
  const socialViews =
    sumAll('youtube','views') + sumLatest('threads','views') + sumLatest('tiktok','video_views_recent') + sumLatest('pinterest','impressions');
  const followers=SOCIAL.reduce((a,p)=>a+sumLatest(p,'followers_total')+sumLatest(p,'subscribers_total'),0);
  const revRows=metricRows(null,'revenue');
  const byCurrency={}; revRows.forEach(r=>{const c=r.currency||'PHP';byCurrency[c]=(byCurrency[c]||0)+Number(r.value||0)});
  const revEntries=Object.entries(byCurrency);
  const revenue=revEntries.length===1?money(revEntries[0][1],revEntries[0][0]):revEntries.length?`${revEntries.length} currencies`:'—';
  const cards=[
    ['Revenue',revenue,revEntries.length?'Connected revenue sources':'Connect AdMob / sales sources'],
    ['App installs',fmt(installs),'Google Play reports'],
    ['Website users',fmt(gaUsers),'GA4 active users'],
    ['Social views',fmt(socialViews),'Available official metrics'],
    ['Audience',fmt(followers),'Latest followers / subscribers'],
  ];
  $('#kpis').innerHTML=cards.map(([l,v,s])=>`<article class="kpi"><span>${l}</span><strong>${v}</strong><small>${s}</small></article>`).join('');
}
function dailySeries(metricFn){
  const days=[]; for(let i=state.period-1;i>=0;i--){const d=new Date();d.setUTCDate(d.getUTCDate()-i);days.push(d.toISOString().slice(0,10))}
  return days.map(day=>({day,value:metricFn(day)}));
}
function svgLine(series, cls, max, w=700,h=190){
  if(!series.length) return '';
  const pts=series.map((p,i)=>`${(i/(Math.max(1,series.length-1)))*w},${h-(Number(p.value||0)/Math.max(1,max))*h}`).join(' ');
  return `<polyline class="chart-line ${cls}" points="${pts}"/>`;
}
function renderTrend(){
  const by=(provider,metric,day)=>metricRows(provider,metric).filter(r=>r.day===day).reduce((a,r)=>a+Number(r.value||0),0);
  const web=dailySeries(d=>by('ga4','active_users',d));
  const apps=dailySeries(d=>by('google_play','installs',d));
  const social=dailySeries(d=>by('youtube','views',d)+by('threads','views',d)+by('pinterest','impressions',d)+by('tiktok','video_views_recent',d));
  const all=[...web,...apps,...social], max=Math.max(1,...all.map(x=>x.value));
  if(all.every(x=>!x.value)){ $('#trendChart').innerHTML='<div class="empty">Trend lines appear after the first successful data sync.</div>';return; }
  $('#trendChart').innerHTML=`<svg viewBox="0 0 700 190" preserveAspectRatio="none">
    <line class="axis-line" x1="0" y1="189" x2="700" y2="189"/><line class="axis-line" x1="0" y1="95" x2="700" y2="95"/>
    ${svgLine(web,'line-web',max)}${svgLine(social,'line-social',max)}${svgLine(apps,'line-apps',max)}
  </svg>`;
}
function renderConnectorMini(){
  $('#connectorMini').innerHTML=(state.data?.connectors||[]).map(c=>`<div class="connector-row">
    <i class="status-dot ${c.status}"></i><div><b>${c.label}</b><br><small>${c.account_label||c.status.replaceAll('_',' ')}</small></div><small>${timeAgo(c.last_sync_at)}</small>
  </div>`).join('');
}
function table(headers,rows){
  if(!rows.length) return '<div class="empty">No synced data yet.</div>';
  return `<table class="data-table"><thead><tr>${headers.map(h=>`<th>${h}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr>${r.map(v=>`<td>${v??'—'}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
}
function renderPlay(){
  const apps=[...new Set(metricRows('google_play').map(r=>r.entity_id).filter(Boolean))];
  const rows=apps.map(id=>[id,fmt(sumLatestEntity('google_play',id,'installs')),fmt(sumLatestEntity('google_play',id,'uninstalls')),fmt(sumLatestEntity('google_play',id,'crashes')),fmt(sumLatestEntity('google_play',id,'anrs'))]);
  $('#playSummary').innerHTML=table(['App','Installs','Uninstalls','Crashes','ANRs'],rows);
}
function sumLatestEntity(provider,id,metric){
  const rows=metricRows(provider,metric).filter(r=>r.entity_id===id).sort((a,b)=>b.day.localeCompare(a.day));
  return Number(rows[0]?.value||0);
}
function renderSocialSummary(){
  const rows=SOCIAL.map(p=>{
    const c=connector(p);
    const audience=sumLatest(p,'followers_total')+sumLatest(p,'subscribers_total');
    let activity=0;
    if(p==='youtube')activity=sumAll(p,'views');
    if(p==='tiktok')activity=sumLatest(p,'video_views_recent');
    if(p==='threads')activity=sumLatest(p,'views');
    if(p==='pinterest')activity=sumLatest(p,'impressions');
    return [c.label,audience?fmt(audience):'—',activity?fmt(activity):'—',c.status.replaceAll('_',' ')];
  });
  $('#socialSummary').innerHTML=table(['Channel','Audience','Views','Status'],rows);
}
function renderApps(){
  const ids=[...new Set(metricRows('google_play').map(r=>r.entity_id).filter(Boolean))];
  $('#appCards').innerHTML=ids.length?ids.map(id=>`<article class="metric-card"><div class="card-title"><div><h3>${id.includes('astramate')?'Astramate':id.includes('keepry')?'Keepry':id}</h3><p>${id}</p></div><span class="status-pill ${connector('google_play').status}">${connector('google_play').status.replaceAll('_',' ')}</span></div><div class="metric-pairs">
    <div class="metric-pair"><span>Installs</span><b>${fmt(sumLatestEntity('google_play',id,'installs'))}</b></div>
    <div class="metric-pair"><span>Uninstalls</span><b>${fmt(sumLatestEntity('google_play',id,'uninstalls'))}</b></div>
    <div class="metric-pair"><span>Crashes</span><b>${fmt(sumLatestEntity('google_play',id,'crashes'))}</b></div>
    <div class="metric-pair"><span>ANRs</span><b>${fmt(sumLatestEntity('google_play',id,'anrs'))}</b></div>
  </div></article>`).join(''):'<article class="panel"><div class="empty">Connect Google and enter the Play developer bucket to populate app statistics.</div></article>';
  const adApps=[...new Set(metricRows('admob').map(r=>r.entity_id).filter(Boolean))];
  const rows=adApps.map(id=>{
    const any=metricRows('admob','revenue').find(r=>r.entity_id===id); const label=any?.dimensions?.label||id; const currency=any?.currency||'USD';
    return [label,money(metricRows('admob','revenue').filter(r=>r.entity_id===id).reduce((a,r)=>a+Number(r.value||0),0),currency),fmt(metricRows('admob','impressions').filter(r=>r.entity_id===id).reduce((a,r)=>a+Number(r.value||0),0)),fmt(metricRows('admob','clicks').filter(r=>r.entity_id===id).reduce((a,r)=>a+Number(r.value||0),0))];
  });
  $('#admobTable').innerHTML=table(['App','Revenue','Impressions','Clicks'],rows);
}
function renderSocialCards(){
  const cards=SOCIAL.map(p=>{
    const c=connector(p), metrics=latestRows(p).filter(r=>r.entity_type==='account').slice(0,8);
    const preferred=['followers_total','subscribers_total','views','video_views_recent','impressions','likes','saves','media_total','videos_total'];
    metrics.sort((a,b)=>preferred.indexOf(a.metric)-preferred.indexOf(b.metric));
    return `<article class="metric-card"><div class="card-title"><div><h3>${c.label}</h3><p>${c.account_label||'Not linked yet'}</p></div><span class="status-pill ${c.status}">${c.status.replaceAll('_',' ')}</span></div><div class="metric-pairs">${metrics.slice(0,4).map(r=>`<div class="metric-pair"><span>${niceMetric(r.metric)}</span><b>${fmt(r.value)}</b></div>`).join('')||'<div class="empty">No metrics yet.</div>'}</div></article>`;
  });
  $('#socialCards').innerHTML=cards.join('');
}
function groupStatus(children){
  const cs=children.map(connector);
  if(cs.some(c=>c.status==='connected'))return 'connected';
  if(cs.some(c=>c.status==='error'))return 'error';
  if(cs.some(c=>c.status==='authorized'))return 'authorized';
  if(cs.some(c=>c.status==='configured'||c.status==='needs_config'))return 'configured';
  return 'not_configured';
}
function renderSources(){
  $('#sourceCards').innerHTML=Object.entries(PROVIDERS).map(([id,p])=>{
    const status=groupStatus(p.children), child=p.children.map(connector), errors=child.map(c=>c.last_error).filter(Boolean);
    return `<article class="source-card"><div class="source-top"><div><h3>${p.title}</h3><p>${p.subtitle}</p></div><span class="status-pill ${status}">${status.replaceAll('_',' ')}</span></div>
      <p>${child.map(c=>`${c.label}: ${c.account_label||c.status.replaceAll('_',' ')}`).join('<br>')}</p>
      ${errors.length?`<div class="source-error">${errors[0]}</div>`:''}
      <div class="source-actions"><button class="secondary" data-config="${id}">Settings</button><button class="primary" data-connect="${id}">Connect</button></div>
    </article>`;
  }).join('');
}
function showView(view){
  state.view=view;
  $$('.view').forEach(v=>v.classList.add('hidden'));
  $(`#${view}View`)?.classList.remove('hidden');
  $$('.nav-item').forEach(b=>b.classList.toggle('active',b.dataset.view===view));
  const titles={overview:'Performance Overview',apps:'Apps & Revenue',social:'Social Performance',sources:'Sources & Authorization'};
  $('#viewTitle').textContent=titles[view]||'Astra Pulse';
}
async function syncAll(){
  const b=$('#syncBtn'); b.disabled=true;b.textContent='Syncing…';
  try{
    const r=await api('/sync-all',{method:'POST',body:'{}'});
    const ok=r.results?.filter(x=>x.ok).length||0, fail=r.results?.filter(x=>!x.ok).length||0;
    toast(`Sync finished: ${ok} sources updated${fail?`, ${fail} need attention`:''}.`);
    await load();
  }catch(e){toast(e.message)}finally{b.disabled=false;b.textContent='↻ Sync now'}
}
const formDefs={
  google:[
    ['play_service_account_json','Play service account JSON','secret'],
    ['play_bucket_id','Play developer bucket ID','config'],
    ['play_packages','Play package names (comma separated)','config'],
    ['client_id','Google OAuth Client ID (optional: AdMob / GA4 / YouTube)','secret'],
    ['client_secret','Google OAuth Client Secret (optional)','secret'],
    ['ga4_property_id','GA4 Property ID (optional)','config'],
  ],
  meta:[['client_id','Meta App ID','secret'],['client_secret','Meta App Secret','secret'],['page_id','Preferred Facebook Page ID (optional)','config']],
  threads:[['client_id','Threads App ID','secret'],['client_secret','Threads App Secret','secret']],
  tiktok:[['client_id','TikTok Client Key','secret'],['client_secret','TikTok Client Secret','secret']],
  pinterest:[['client_id','Pinterest App ID','secret'],['client_secret','Pinterest App Secret','secret']],
};
async function openConfig(provider){
  let cfg={provider,config:{},has_client_id:false,has_client_secret:false,redirect_uri:state.data?.redirects?.[provider]};
  try{cfg=await api(`/config?provider=${provider}`)}catch(e){}
  const p=PROVIDERS[provider];
  $('#modalContent').innerHTML=`<p class="eyebrow">SOURCE SETUP</p><h2>${p.title}</h2><p class="muted small">${p.subtitle}</p>
    <div class="form-grid">${formDefs[provider].map(([key,label,type])=>{
      const wide = key==='play_packages'||key==='play_service_account_json';
      const saved = (key==='client_id'&&cfg.has_client_id)||(key==='client_secret'&&cfg.has_client_secret)||(key==='play_service_account_json'&&cfg.has_play_service_account);
      if(key==='play_service_account_json') return `<label class="span2">${label}<textarea class="form-input" rows="4" data-field="${key}" data-kind="${type}" placeholder="${saved?'Saved securely · leave blank to keep':'Paste the complete service-account JSON here'}"></textarea></label>`;
      return `<label class="${wide?'span2':''}">${label}<input class="form-input" data-field="${key}" data-kind="${type}" type="${type==='secret'?'password':'text'}" value="${type==='config'?(cfg.config?.[key]??(key==='play_packages'?'com.astralabs.astramate,com.astralabs.keepry':'')):''}" placeholder="${saved?'Saved securely · leave blank to keep':'Enter value'}"></label>`;
    }).join('')}</div>
    <p class="helper">Register this exact OAuth redirect URI in the provider's developer console:</p>
    <div class="redirect-box"><code>${cfg.redirect_uri||state.data?.redirects?.[provider]||''}</code><button class="text-btn" id="copyRedirect">Copy</button></div>
    ${provider==='google'?'<p class="helper"><b>For Google Play statistics only:</b> paste a service-account JSON, enter the Play developer bucket ID, and keep the two package names. OAuth Client ID, Client Secret, and GA4 Property ID are optional and only needed later for AdMob/GA4/YouTube direct integrations.</p>':''}
    <div class="modal-actions"><button class="secondary" data-close-modal>Cancel</button><button class="primary" id="saveSource">Save settings</button></div>`;
  $('#sourceModal').classList.remove('hidden'); $('#sourceModal').setAttribute('aria-hidden','false');
  $('#copyRedirect').onclick=async()=>{await navigator.clipboard.writeText(cfg.redirect_uri||state.data?.redirects?.[provider]||'');toast('Redirect URI copied.')};
  $('#saveSource').onclick=()=>saveSource(provider);
}
function closeModal(){ $('#sourceModal').classList.add('hidden');$('#sourceModal').setAttribute('aria-hidden','true'); }
async function saveSource(provider){
  const config={},secrets={};
  $$('#modalContent [data-field]').forEach(el=>{const v=el.value.trim(); if(el.dataset.kind==='config')config[el.dataset.field]=v;else if(v)secrets[el.dataset.field]=v});
  if(provider==='google'&&config.play_packages)config.play_packages=config.play_packages.split(/[\s,]+/).filter(Boolean);
  try{await api('/config',{method:'POST',body:JSON.stringify({provider,config,secrets})});toast(`${PROVIDERS[provider].title} settings saved.`);closeModal();await load();}catch(e){toast(e.message)}
}
async function connect(provider){
  try{
    const r=await api(`/oauth/${provider}/start`,{method:'POST',body:'{}'});
    location.href=r.url;
  }catch(e){toast(e.message);openConfig(provider);}
}

$('#unlockForm').addEventListener('submit',async e=>{e.preventDefault();state.key=$('#accessKey').value.trim();if(!state.key)return;localStorage.setItem('astra_pulse_key',state.key);$('#lockError').textContent='';await load()});
$('#lockBtn').onclick=()=>{localStorage.removeItem('astra_pulse_key');state.key='';location.reload()};
$('#syncBtn').onclick=syncAll; $('#syncSourcesBtn').onclick=syncAll; $('#sourcesBtn').onclick=()=>showView('sources');
$('#periodSwitch').addEventListener('click',e=>{const b=e.target.closest('[data-period]');if(!b)return;$$('#periodSwitch button').forEach(x=>x.classList.remove('active'));b.classList.add('active');load(Number(b.dataset.period))});
document.addEventListener('click',e=>{
  const nav=e.target.closest('.nav-item'); if(nav)showView(nav.dataset.view);
  const go=e.target.closest('[data-go]'); if(go)showView(go.dataset.go);
  const cfg=e.target.closest('[data-config]'); if(cfg)openConfig(cfg.dataset.config);
  const con=e.target.closest('[data-connect]'); if(con)connect(con.dataset.connect);
  if(e.target.closest('[data-close-modal]'))closeModal();
});
setInterval(()=>{$('#clock').textContent=new Intl.DateTimeFormat('en-PH',{timeZone:'Asia/Manila',dateStyle:'medium',timeStyle:'short'}).format(new Date())},1000);

if(state.key){$('#accessKey').value=state.key;load()}