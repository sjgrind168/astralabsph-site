const PIREVO = Object.freeze({
  GA4_PROPERTY_ID: '16044108056',
  GSC_SITE_URL: 'https://www.astralabsph.com/',
  CACHE_SECONDS: 60,
  TZ: 'Asia/Manila'
});

function doGet() {
  return HtmlService.createTemplateFromFile('Index')
    .evaluate()
    .setTitle('PIREVO Analytics')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.DEFAULT);
}

function getDashboardData() {
  const cache = CacheService.getUserCache();
  const cached = cache.get('pirevo-dashboard-v2');
  if (cached) return JSON.parse(cached);

  const out = {
    ok: true,
    generatedAt: new Date().toISOString(),
    periodLabel: 'Last 7 days',
    realtime: { activeUsers: null },
    kpis: {
      users: null,
      sessions: null,
      pinterestTraffic: null,
      googleOrganic: null,
      productViews: null,
      amazonClicks: null,
      ctr: null
    },
    traffic: [],
    landingPages: [],
    products: [],
    queries: [],
    campaigns: [],
    searchConsole: {
      clicks: null,
      impressions: null,
      ctr: null,
      position: null,
      dataThrough: null
    },
    maturity: 'Initialization period — first 24–48 hours, trends are directional only.',
    errors: []
  };

  try {
    const overview = gaReport_([], ['totalUsers','sessions'], pirevoPageFilter_());
    const totals = firstMetrics_(overview, ['totalUsers','sessions']);
    out.kpis.users = totals.totalUsers;
    out.kpis.sessions = totals.sessions;
  } catch (e) { out.errors.push('GA4 overview: ' + cleanErr_(e)); }

  try {
    out.realtime.activeUsers = gaRealtimePirevoUsers_();
  } catch (e) { out.errors.push('GA4 realtime: ' + cleanErr_(e)); }

  try {
    out.kpis.pinterestTraffic = sourceSessions_('pinterest');
    out.kpis.googleOrganic = googleOrganicSessions_();
  } catch (e) { out.errors.push('GA4 acquisition: ' + cleanErr_(e)); }

  try {
    out.kpis.productViews = eventCount_('view_item', '/pirevo/products/');
    out.kpis.amazonClicks = eventCount_('affiliate_click', '/pirevo/');
    if (out.kpis.productViews !== null && out.kpis.productViews > 0 && out.kpis.amazonClicks !== null) {
      out.kpis.ctr = round1_(100 * out.kpis.amazonClicks / out.kpis.productViews);
    }
  } catch (e) { out.errors.push('GA4 funnel: ' + cleanErr_(e)); }

  try { out.traffic = trafficBreakdown_(); }
  catch (e) { out.errors.push('Traffic sources: ' + cleanErr_(e)); }

  try { out.landingPages = topLandingPages_(); }
  catch (e) { out.errors.push('Landing pages: ' + cleanErr_(e)); }

  try { out.products = topProducts_(); }
  catch (e) { out.errors.push('Product clicks: ' + cleanErr_(e)); }

  try { out.campaigns = pinterestCampaigns_(); }
  catch (e) { out.errors.push('Pinterest campaigns: ' + cleanErr_(e)); }

  try {
    const sc = searchConsole_();
    out.queries = sc.queries;
    out.searchConsole = sc.summary;
  } catch (e) { out.errors.push('Search Console: ' + cleanErr_(e)); }

  if (!out.errors.length && (out.kpis.sessions || 0) >= 100) {
    out.maturity = 'Live collection active — use trend direction with sample size in mind.';
  }

  cache.put('pirevo-dashboard-v2', JSON.stringify(out), PIREVO.CACHE_SECONDS);
  return out;
}

function authHeaders_() {
  return { Authorization: 'Bearer ' + ScriptApp.getOAuthToken() };
}

function fetchJson_(url, options) {
  options = options || {};
  options.headers = Object.assign({}, options.headers || {}, authHeaders_());
  options.muteHttpExceptions = true;
  const res = UrlFetchApp.fetch(url, options);
  const text = res.getContentText();
  if (res.getResponseCode() < 200 || res.getResponseCode() >= 300) {
    throw new Error(res.getResponseCode() + ' ' + text.slice(0, 500));
  }
  return text ? JSON.parse(text) : {};
}

function gaReport_(dimensions, metrics, dimensionFilter, extra) {
  extra = extra || {};
  const body = {
    dateRanges: [{ startDate: extra.startDate || '7daysAgo', endDate: extra.endDate || 'today' }],
    dimensions: (dimensions || []).map(name => ({ name })),
    metrics: (metrics || []).map(name => ({ name })),
    limit: String(extra.limit || 100)
  };
  if (dimensionFilter) body.dimensionFilter = dimensionFilter;
  if (extra.orderBys) body.orderBys = extra.orderBys;
  const url = 'https://analyticsdata.googleapis.com/v1beta/properties/' + PIREVO.GA4_PROPERTY_ID + ':runReport';
  return fetchJson_(url, {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(body)
  });
}

function gaRealtimePirevoUsers_() {
  const url = 'https://analyticsdata.googleapis.com/v1beta/properties/' + PIREVO.GA4_PROPERTY_ID + ':runRealtimeReport';
  const body = {
    dimensions: [{ name: 'eventName' }],
    metrics: [{ name: 'activeUsers' }],
    dimensionFilter: exactFilter_('eventName', 'pirevo_landing'),
    limit: '10'
  };
  const data = fetchJson_(url, {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(body)
  });
  return metricFromRows_(data, 'activeUsers');
}

function pirevoPageFilter_() {
  return beginsFilter_('pagePath', '/pirevo/');
}

function beginsFilter_(field, value) {
  return { filter: { fieldName: field, stringFilter: { matchType: 'BEGINS_WITH', value, caseSensitive: false } } };
}

function containsFilter_(field, value) {
  return { filter: { fieldName: field, stringFilter: { matchType: 'CONTAINS', value, caseSensitive: false } } };
}

function exactFilter_(field, value) {
  return { filter: { fieldName: field, stringFilter: { matchType: 'EXACT', value, caseSensitive: false } } };
}

function andFilter_(expressions) {
  return { andGroup: { expressions } };
}

function orFilter_(expressions) {
  return { orGroup: { expressions } };
}

function firstMetrics_(data, names) {
  const result = {};
  names.forEach(n => result[n] = 0);
  const row = (data.rows || [])[0];
  if (!row) return result;
  const headers = (data.metricHeaders || []).map(h => h.name);
  (row.metricValues || []).forEach((v, i) => {
    const name = headers[i];
    if (names.indexOf(name) >= 0) result[name] = Number(v.value || 0);
  });
  return result;
}

function metricFromRows_(data, metricName) {
  const idx = (data.metricHeaders || []).findIndex(h => h.name === metricName);
  if (idx < 0) return 0;
  return (data.rows || []).reduce((sum, r) => sum + Number((r.metricValues[idx] || {}).value || 0), 0);
}

function sourceSessions_(needle) {
  const data = gaReport_(['sessionSource'], ['sessions'],
    andFilter_([pirevoLandingFilter_(), containsFilter_('sessionSource', needle)]));
  return metricFromRows_(data, 'sessions');
}

function googleOrganicSessions_() {
  const data = gaReport_(['sessionSource','sessionMedium'], ['sessions'],
    andFilter_([
      pirevoLandingFilter_(),
      exactFilter_('sessionSource','google'),
      exactFilter_('sessionMedium','organic')
    ]));
  return metricFromRows_(data, 'sessions');
}

function pirevoLandingFilter_() {
  return beginsFilter_('landingPagePlusQueryString', '/pirevo');
}

function eventCount_(eventName, pagePrefix) {
  const filters = [exactFilter_('eventName', eventName)];
  if (pagePrefix) filters.push(beginsFilter_('pagePath', pagePrefix));
  const data = gaReport_(['eventName'], ['eventCount'], andFilter_(filters));
  return metricFromRows_(data, 'eventCount');
}

function trafficBreakdown_() {
  const data = gaReport_(['sessionSource','sessionMedium'], ['sessions'], pirevoLandingFilter_(), {
    limit: 100,
    orderBys: [{ metric: { metricName: 'sessions' }, desc: true }]
  });
  const dims = (data.dimensionHeaders || []).map(h => h.name);
  const metricIdx = (data.metricHeaders || []).findIndex(h => h.name === 'sessions');
  const buckets = { Pinterest: 0, 'Google Organic': 0, Direct: 0, Buffer: 0, Other: 0 };

  (data.rows || []).forEach(r => {
    const vals = {};
    (r.dimensionValues || []).forEach((v,i)=> vals[dims[i]] = v.value || '');
    const s = Number((r.metricValues[metricIdx] || {}).value || 0);
    const source = (vals.sessionSource || '').toLowerCase();
    const medium = (vals.sessionMedium || '').toLowerCase();
    if (source.indexOf('pinterest') >= 0) buckets.Pinterest += s;
    else if (source === 'google' && medium === 'organic') buckets['Google Organic'] += s;
    else if (source.indexOf('buffer') >= 0) buckets.Buffer += s;
    else if (source === '(direct)' || medium === '(none)' || !source) buckets.Direct += s;
    else buckets.Other += s;
  });

  const total = Object.keys(buckets).reduce((a,k)=>a+buckets[k],0);
  return Object.keys(buckets).map(name => ({
    name,
    value: buckets[name],
    pct: total ? round1_(100 * buckets[name] / total) : 0
  }));
}

function topLandingPages_() {
  const data = gaReport_(['landingPagePlusQueryString'], ['sessions'], pirevoLandingFilter_(), {
    limit: 10,
    orderBys: [{ metric: { metricName: 'sessions' }, desc: true }]
  });
  return rows_(data).map(r => ({
    path: r.landingPagePlusQueryString || '',
    name: friendlyPage_(r.landingPagePlusQueryString || ''),
    sessions: Number(r.sessions || 0)
  })).slice(0,5);
}

function topProducts_() {
  const data = gaReport_(['pagePath'], ['eventCount'],
    andFilter_([
      exactFilter_('eventName','affiliate_click'),
      beginsFilter_('pagePath','/pirevo/products/')
    ]), {
      limit: 20,
      orderBys: [{ metric: { metricName: 'eventCount' }, desc: true }]
    });
  return rows_(data).map(r => ({
    path: r.pagePath || '',
    name: friendlyProduct_(r.pagePath || ''),
    clicks: Number(r.eventCount || 0)
  })).slice(0,5);
}

function pinterestCampaigns_() {
  const sessionData = gaReport_(['sessionCampaignName'], ['sessions'],
    andFilter_([
      pirevoLandingFilter_(),
      containsFilter_('sessionSource','pinterest')
    ]), { limit: 30 });

  const eventData = gaReport_(['sessionCampaignName','eventName'], ['eventCount'],
    andFilter_([
      beginsFilter_('pagePath','/pirevo/'),
      orFilter_([
        exactFilter_('eventName','view_item'),
        exactFilter_('eventName','affiliate_click')
      ]),
      containsFilter_('sessionSource','pinterest')
    ]), { limit: 100 });

  const map = {};
  rows_(sessionData).forEach(r => {
    const name = normalizeCampaign_(r.sessionCampaignName);
    if (!name) return;
    map[name] = map[name] || { campaign:name, visits:0, productViews:0, amazonClicks:0, ctr:null };
    map[name].visits += Number(r.sessions || 0);
  });

  rows_(eventData).forEach(r => {
    const name = normalizeCampaign_(r.sessionCampaignName);
    if (!name) return;
    map[name] = map[name] || { campaign:name, visits:0, productViews:0, amazonClicks:0, ctr:null };
    if (r.eventName === 'view_item') map[name].productViews += Number(r.eventCount || 0);
    if (r.eventName === 'affiliate_click') map[name].amazonClicks += Number(r.eventCount || 0);
  });

  return Object.keys(map).map(k => {
    const x = map[k];
    x.ctr = x.productViews ? round1_(100*x.amazonClicks/x.productViews) : null;
    return x;
  }).sort((a,b)=>b.amazonClicks-a.amazonClicks || b.visits-a.visits).slice(0,6);
}

function searchConsole_() {
  const today = new Date();
  const end = new Date(today.getTime() - 2*86400000);
  const start = new Date(end.getTime() - 6*86400000);
  const startDate = Utilities.formatDate(start, PIREVO.TZ, 'yyyy-MM-dd');
  const endDate = Utilities.formatDate(end, PIREVO.TZ, 'yyyy-MM-dd');
  const encodedSite = encodeURIComponent(PIREVO.GSC_SITE_URL);
  const url = 'https://www.googleapis.com/webmasters/v3/sites/' + encodedSite + '/searchAnalytics/query';

  const summary = fetchJson_(url, {
    method:'post',
    contentType:'application/json',
    payload: JSON.stringify({ startDate, endDate, rowLimit:1 })
  });
  const srow = (summary.rows || [])[0] || {};
  const queries = fetchJson_(url, {
    method:'post',
    contentType:'application/json',
    payload: JSON.stringify({
      startDate, endDate,
      dimensions:['query'],
      rowLimit:5
    })
  });

  return {
    summary: {
      clicks: Number(srow.clicks || 0),
      impressions: Number(srow.impressions || 0),
      ctr: srow.ctr == null ? null : round1_(100*Number(srow.ctr)),
      position: srow.position == null ? null : round1_(Number(srow.position)),
      dataThrough: endDate
    },
    queries: (queries.rows || []).map(r => ({
      query: (r.keys || [''])[0],
      clicks: Number(r.clicks || 0),
      impressions: Number(r.impressions || 0),
      ctr: round1_(100*Number(r.ctr || 0)),
      position: round1_(Number(r.position || 0))
    }))
  };
}

function rows_(data) {
  const d = (data.dimensionHeaders || []).map(h=>h.name);
  const m = (data.metricHeaders || []).map(h=>h.name);
  return (data.rows || []).map(row => {
    const x = {};
    (row.dimensionValues || []).forEach((v,i)=>x[d[i]]=v.value);
    (row.metricValues || []).forEach((v,i)=>x[m[i]]=v.value);
    return x;
  });
}

function friendlyPage_(path) {
  const clean = String(path || '').split('?')[0].replace(/\/$/,'');
  if (clean === '/pirevo') return 'PIREVO Home';
  if (clean.indexOf('/pirevo/products/') === 0) return friendlyProduct_(clean);
  if (clean.indexOf('/pirevo/guides/') === 0) {
    return titleCase_(clean.split('/').filter(Boolean).pop().replace(/-/g,' '));
  }
  return clean || 'PIREVO';
}

function friendlyProduct_(path) {
  const slug = String(path || '').split('?')[0].split('/').filter(Boolean).pop() || '';
  const special = {
    'ninja-possiblecooker-pro-plus':'Ninja PossibleCooker',
    'churboro-spice-jars-25':'Churboro Spice Jars',
    'godonlif-candle-warmer-lamp':'Candle Warmer',
    'cerave-moisturizing-cream':'CeraVe Cream',
    'wrangler-satchel':'Wrangler Satchel',
    'illiyoon-ceramide-ato':'ILLIYOON Ceramide',
    'govee-tv-backlight-3-lite':'Govee TV Backlight',
    'ynylchmx-fall-wreath':'Fall Wreath'
  };
  return special[slug] || titleCase_(slug.replace(/-/g,' '));
}

function normalizeCampaign_(name) {
  name = String(name || '').trim();
  if (!name || name === '(not set)' || name === '(direct)') return '';
  return name.replace(/_/g,' ');
}

function titleCase_(s) {
  return String(s || '').replace(/\b\w/g, c => c.toUpperCase());
}

function round1_(n) { return Math.round(Number(n || 0)*10)/10; }
function cleanErr_(e) { return String(e && e.message ? e.message : e).replace(/\s+/g,' ').slice(0,260); }
