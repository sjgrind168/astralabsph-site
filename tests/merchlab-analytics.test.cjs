const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
test('MerchLab tracking scripts are confined to MerchLab and its product pages',()=>{
 const homepage=read('public/merchlab/index.html'),generator=read('tools/generate-merchlab-seo.mjs');
 assert.match(homepage,/\/merchlab\/merchlab-analytics\.js/);
 assert.match(generator,/\/merchlab\/merchlab-analytics\.js/);
 assert.match(homepage,/\/pirevo\/config\.js/);
 for(const f of ['public/merchlab/merchlab.js','public/merchlab/merchlab-cart.js'])assert.match(read(f),/MERCHLAB_ANALYTICS/);
 assert.doesNotMatch(read('public/astralabs-site-analytics.js'),/merchlab_site_events/);
});
test('private dashboard has one MerchLab reporting tab and protected report RPC',()=>{
 const html=read('public/analytics/index.html'),js=read('public/analytics/dashboard-v2.js');
 for(const id of ['tab-merchlab','pane-merchlab','mlVisitors','mlSessions','mlViews','mlCartAdds','mlOutbounds','mlDays','mlProducts','mlSources','mlSearchTerms'])assert.match(html,new RegExp('id="'+id+'"'));
 assert.match(js,/merchlab_dashboard_snapshot/);
 assert.match(js,/window\.MERCHLAB_REPORT\?\.render/);
 assert.match(html,/merchlab-report\.js/);
});
test('database schema allows anonymous inserts, blocks public reads and authenticates private reporting',()=>{
 const sql=read('tools/merchlab/firstparty_analytics.sql');
 assert.match(sql,/enable row level security/);
 assert.match(sql,/grant insert on table public\.merchlab_site_events to anon,authenticated/);
 assert.match(sql,/revoke all on table public\.merchlab_site_events from public,anon,authenticated/);
 assert.match(sql,/astra_analytics_session_is_valid\(p_token\)/);
 assert.match(sql,/grant execute on function public\.merchlab_dashboard_snapshot/);
 assert.doesNotMatch(sql,/grant select on table public\.merchlab_site_events to anon/i);
});
test('tracker sends structured events, honors DNT and skips automated browsers',()=>{
 const code=read('public/merchlab/merchlab-analytics.js');
 const store=()=>{const m=new Map();return {getItem:k=>m.get(k)||null,setItem:(k,v)=>m.set(k,v)}};
 function context(options={}){
  const requests=[],localStorage=store(),sessionStorage=store();
  const document={referrer:'https://www.facebook.com/groups/example',addEventListener:()=>{}};
  const window={PIREVO_CONFIG:{analyticsDbUrl:'https://demo.supabase.co',analyticsAnonKey:'public-placeholder'},doNotTrack:options.dnt?'1':'0'};
  const env={window,document,localStorage,sessionStorage,location:{hostname:'www.astralabsph.com',pathname:'/merchlab/',search:options.qa?'?metrics_qa=1':'?utm_source=facebook&utm_campaign=first'},navigator:{webdriver:!!options.webdriver,globalPrivacyControl:false,doNotTrack:options.dnt?'1':'0'},crypto:{randomUUID:()=>'test-'+Math.random().toString(36).slice(2).padEnd(20,'0')},URL,URLSearchParams,Math,fetch:(url,data)=>{requests.push({url,data:JSON.parse(data.body)});return Promise.resolve({ok:true})}};
  vm.runInNewContext(code,env);
  return {requests,window};
 }
 const ok=context();
 assert.deepEqual(ok.requests.map(x=>x.data.event_name),['session_start','page_view']);
 ok.window.MERCHLAB_ANALYTICS.track('add_to_bag',{product_id:'57918501585',quantity:1});
 assert.equal(ok.requests.at(-1).data.product_id,'57918501585');
 assert.equal(ok.requests.at(-1).data.traffic_source,'facebook');
 ok.window.MERCHLAB_ANALYTICS.track('purchase',{product_id:'57918501585'});
 assert.equal(ok.requests.length,3);
 assert.equal(context({dnt:true}).requests.length,0);
 assert.equal(context({webdriver:true}).requests.length,0);
 assert.equal(context({qa:true}).requests.length,0);
});
