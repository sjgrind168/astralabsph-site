(()=>{
  const C=window.PIREVO_CONFIG||{};
  const store=window.PIREVO_STORE||{products:[]};
  const productMap=new Map((store.products||[]).map(p=>[p.slug,p]));
  const COLORS=["#214b32","#47743f","#79a654","#b8d36f","#c9c8bd","#84957c","#d9e7b6"];

  const $=id=>document.getElementById(id);
  const fmt=n=>new Intl.NumberFormat("en-US",{maximumFractionDigits:0}).format(Number(n||0));
  const fmtCompact=n=>new Intl.NumberFormat("en-US",{notation:"compact",maximumFractionDigits:1}).format(Number(n||0));
  const pct=n=>Number(n||0).toFixed(1).replace(".0","")+"%";
  const titleize=s=>String(s||"").replace(/[_-]+/g," ").replace(/\b\w/g,m=>m.toUpperCase());
  const slugFromPath=path=>(String(path).match(/\/products\/([^/]+)/)||[])[1]||"";
  const productForSlug=slug=>productMap.get(slug)||null;
  const prettyPath=path=>{
    if(/^\/pirevo\/?$/.test(path))return"PIREVO Home";
    const slug=slugFromPath(path);
    const p=productForSlug(slug);
    if(p)return p.shortName||p.fullName||titleize(slug);
    if(/\/guides\//.test(path))return titleize((path.match(/\/guides\/([^/]+)/)||[])[1]||"Guide");
    return path;
  };
  const imageForSlug=slug=>productForSlug(slug)?.image||"";
  const accessFromHash=()=>{
    const raw=location.hash.replace(/^#/,"");
    if(!raw)return"";
    const h=new URLSearchParams(raw);
    return h.get("access")||"";
  };
  let token=accessFromHash();
  if(token){
    try{localStorage.setItem("pirevo_analytics_access",token)}catch{}
    history.replaceState(null,"",location.pathname);
  }else{
    try{token=localStorage.getItem("pirevo_analytics_access")||""}catch{}
  }

  if(!token){
    $("dashboard").hidden=true;
    $("locked").hidden=false;
    return;
  }

  async function snapshot(){
    const res=await fetch(C.analyticsDbUrl+"/rest/v1/rpc/pirevo_dashboard_snapshot",{
      method:"POST",
      cache:"no-store",
      headers:{
        apikey:C.analyticsAnonKey,
        Authorization:"Bearer "+C.analyticsAnonKey,
        "Content-Type":"application/json"
      },
      body:JSON.stringify({p_days:7,p_token:token})
    });
    if(!res.ok)throw new Error("analytics access");
    return res.json();
  }

  function renderKpis(k={}){
    $("kVisitors").textContent=fmt(k.visitors);
    $("kSessions").textContent=fmt(k.sessions);
    $("kPinterest").textContent=fmt(k.pinterest_traffic);
    $("kGoogle").textContent=fmt(k.google_organic);
    $("kProductViews").textContent=fmt(k.product_views);
    $("kAmazon").textContent=fmt(k.amazon_clicks);
    $("kCtr").textContent=pct(k.ctr);
    $("donutSessions").textContent=fmt(k.sessions);
  }

  function renderTraffic(rows=[],sessions=0){
    const total=Math.max(1,Number(sessions||0));
    let cursor=0;
    const parts=[];
    const legend=[];
    rows.slice(0,7).forEach((r,i)=>{
      const n=Number(r.sessions||0);
      const share=(n/total)*100;
      const start=cursor;
      cursor+=share;
      parts.push(`${COLORS[i%COLORS.length]} ${start.toFixed(2)}% ${cursor.toFixed(2)}%`);
      legend.push(`<div class="traffic-row"><i class="dot" style="background:${COLORS[i%COLORS.length]}"></i><span>${titleize(r.source)}</span><b>${share.toFixed(0)}%</b></div>`);
    });
    if(cursor<100)parts.push(`#e7e4dc ${cursor.toFixed(2)}% 100%`);
    $("trafficDonut").style.background="conic-gradient("+parts.join(",")+")";
    $("trafficLegend").innerHTML=legend.length?legend.join(""):'<div class="empty">Traffic sources will appear as visitors arrive.</div>';
  }

  function rankRow(i,name,img,value){
    return `<div class="rank-row"><span class="rank-num">${i+1}</span><span class="rank-name">${name}</span>${img?`<img class="rank-thumb" src="${img}" alt="">`:'<span></span>'}<strong class="rank-value">${value??""}</strong></div>`;
  }

  function renderLanding(rows=[]){
    $("landingList").innerHTML=rows.length?rows.map((r,i)=>{
      const slug=slugFromPath(r.path);
      return rankRow(i,prettyPath(r.path),imageForSlug(slug),fmt(r.sessions));
    }).join(""):'<div class="empty">Landing-page data starts with the next new sessions.</div>';
  }

  function renderProducts(rows=[]){
    $("productList").innerHTML=rows.length?rows.map((r,i)=>{
      const p=productForSlug(r.product_slug);
      const name=p?.shortName||r.item_name||titleize(r.product_slug);
      return rankRow(i,name,p?.image||"",fmt(r.clicks));
    }).join(""):'<div class="empty">Amazon click leaders will appear after outbound clicks begin.</div>';
  }

  function renderQueries(data){
    const gsc=data.search_console||{};
    const gscQueries=Array.isArray(gsc.top_queries)?gsc.top_queries:[];
    const own=data.top_searches||[];
    const rows=gscQueries.length?gscQueries:own;
    $("querySource").textContent=gscQueries.length?"Google Search Console":"on-site search";
    $("queryList").innerHTML=rows.length?rows.slice(0,5).map((r,i)=>{
      const q=r.query||r.search_term||r.keys?.[0]||"";
      const n=r.clicks??r.searches??"";
      return `<div class="query-row"><span class="query-num">${i+1}</span><span>${q}</span><span class="query-count">${n!==""?fmt(n):""}</span></div>`;
    }).join(""):'<div class="empty">Search-query data is still initializing.</div>';
  }

  function renderCampaigns(rows=[]){
    $("campaignRows").innerHTML=rows.length?rows.map(r=>`<tr>
      <td><div class="campaign-name"><span class="campaign-chip">P</span><span>${titleize(r.campaign)}</span></div></td>
      <td>${fmt(r.visits)}</td><td>${fmt(r.product_views)}</td><td>${fmt(r.amazon_clicks)}</td><td>${pct(r.ctr)}</td>
    </tr>`).join(""):'<tr><td colspan="5"><div class="empty">Pinterest UTM campaigns will populate as tracked Pins send traffic.</div></td></tr>';
  }

  function renderGsc(g={}){
    $("gImpressions").textContent=fmtCompact(g.impressions);
    $("gClicks").textContent=fmt(g.clicks);
    $("gCtr").textContent=pct(g.ctr);
    $("gPosition").textContent=Number(g.avg_position)>0?Number(g.avg_position).toFixed(1):"—";
    if(g.captured_at){
      const d=new Date(g.captured_at);
      $("gscAge").textContent="synced "+d.toLocaleString("en-PH",{month:"short",day:"numeric",hour:"numeric",minute:"2-digit"});
    }else{
      $("gscAge").textContent="awaiting first GSC snapshot";
    }
  }

  function renderMaturity(k={}){
    const sessions=Number(k.sessions||0);
    if(!k.last_event_at){
      $("maturityText").textContent="Initialization period. Waiting for the first live business signals.";
    }else if(sessions<25){
      $("maturityText").textContent="Early sample. Live tracking is working, but trends are directional until more sessions accumulate.";
    }else if(sessions<100){
      $("maturityText").textContent="Growing sample. Use the rankings for testing, but avoid declaring winners from small differences.";
    }else{
      $("maturityText").textContent="Live sample is building. Compare traffic quality and Amazon outbound click-through before scaling campaigns.";
    }
  }

  function render(data){
    const k=data.kpis||{};
    renderKpis(k);
    renderTraffic(data.traffic_sources||[],k.sessions||0);
    renderLanding(data.top_landing_pages||[]);
    renderProducts(data.top_products||[]);
    renderQueries(data);
    renderCampaigns(data.campaigns||[]);
    renderGsc(data.search_console||{});
    renderMaturity(k);
    document.querySelector(".live-dot").classList.add("on");
    $("liveText").textContent="Live · auto-sync 15s";
    const stamp=k.last_event_at?new Date(k.last_event_at):new Date(data.generated_at||Date.now());
    $("updatedText").textContent="Last signal "+stamp.toLocaleString("en-PH",{month:"short",day:"numeric",hour:"numeric",minute:"2-digit",second:"2-digit"});
  }

  async function load(){
    try{
      const data=await snapshot();
      render(data);
    }catch(err){
      document.querySelector(".live-dot").classList.remove("on");
      $("liveText").textContent="Connection waiting";
      $("updatedText").textContent="Retrying automatically";
    }
  }

  load();
  setInterval(()=>{if(document.visibilityState==="visible")load()},15000);
  document.addEventListener("visibilitychange",()=>{if(document.visibilityState==="visible")load()});
})();