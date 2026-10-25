const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const ROOT = path.resolve(__dirname, '..');

function storage() {
  const data = new Map();
  return {
    getItem: key => data.get(key) ?? null,
    setItem: (key, value) => data.set(key, String(value)),
    removeItem: key => data.delete(key)
  };
}
function run(file, opts = {}) {
  const requests = [];
  const sessionStorage = opts.sessionStorage ?? storage();
  const localStorage = storage();
  const location = {
    pathname: opts.pathname ?? '/pirevo/products/example/',
    search: opts.search ?? '',
    hostname: 'www.astralabsph.com',
    origin: 'https://www.astralabsph.com'
  };
  const context = {
    location, sessionStorage, localStorage,
    navigator: { globalPrivacyControl: !!opts.gpc, doNotTrack: opts.dnt ?? null, webdriver: !!opts.webdriver },
    document: {
      readyState: 'complete', referrer: '',
      querySelector: () => null,
      addEventListener: () => {}
    },
    URL, URLSearchParams,
    crypto: { randomUUID: () => 'unique-id' },
    fetch: (url, request) => { requests.push({ url, ...request }); return Promise.resolve({ ok: true }); },
    addEventListener: () => {},
    removeEventListener: () => {}
  };
  context.window = context;
  context.PIREVO_CONFIG = { analyticsDbUrl: 'https://example.supabase.co', analyticsAnonKey: 'test-anon-key' };
  vm.runInNewContext(fs.readFileSync(path.join(ROOT, file), 'utf8'), context, { filename: file });
  return { requests, sessionStorage, context };
}
const pirevo = 'public/pirevo/business-analytics.js';
const site = 'public/astralabs-site-analytics.js';

test('PIREVO explicitly marked QA tab sends no DB or GA events', () => {
  const x = run(pirevo, { search: '?__astra_qa=1' });
  assert.equal(x.requests.length, 0);
  assert.equal(x.sessionStorage.getItem('__astralabs_qa_no_track'), '1');
  assert.equal(x.context.PIREVO_ANALYTICS.status().enabled, false);
});
test('PIREVO QA exclusion persists within same tab on later unmarked page', () => {
  const first = run(pirevo, { search: '?__astra_qa=1' });
  const next = run(pirevo, { sessionStorage: first.sessionStorage, search: '' });
  assert.equal(next.requests.length, 0);
});
test('PIREVO ordinary visitors still emit session, page and product events', () => {
  const x = run(pirevo);
  const names = x.requests.map(r => JSON.parse(r.body).event_name);
  assert.deepEqual(names, ['session_start', 'page_view', 'view_item']);
});
test('PIREVO existing privacy opt-outs remain respected', () => {
  assert.equal(run(pirevo, { gpc: true }).requests.length, 0);
  assert.equal(run(pirevo, { dnt: '1' }).requests.length, 0);
});
test('AstraLabs site QA tab sends no events', () => {
  const x = run(site, { pathname: '/', search: '?__astra_qa=1' });
  assert.equal(x.requests.length, 0);
  assert.equal(x.sessionStorage.getItem('__astralabs_qa_no_track'), '1');
});
test('AstraLabs site QA exclusion persists within same tab', () => {
  const first = run(site, { pathname: '/', search: '?__astra_qa=1' });
  const next = run(site, { pathname: '/keepry/', sessionStorage: first.sessionStorage });
  assert.equal(next.requests.length, 0);
});
test('AstraLabs ordinary homepage still emits session and page events', () => {
  const x = run(site, { pathname: '/' });
  assert.deepEqual(x.requests.map(r => JSON.parse(r.body).event_name), ['session_start', 'page_view']);
});
test('AstraLabs existing privacy and webdriver exclusions remain respected', () => {
  assert.equal(run(site, { pathname: '/', gpc: true }).requests.length, 0);
  assert.equal(run(site, { pathname: '/', dnt: '1' }).requests.length, 0);
  assert.equal(run(site, { pathname: '/', webdriver: true }).requests.length, 0);
});

function runHomepageGA(opts = {}) {
  const html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
  const inline = html.match(/<script>([\s\S]*?)<\/script>/);
  assert.ok(inline, 'homepage inline GA4 bootstrap exists');
  const scripts = [];
  const sessionStorage = opts.sessionStorage ?? storage();
  const window = {};
  const context = {
    window, sessionStorage,
    URLSearchParams, Date,
    location: { search: opts.search ?? '' },
    navigator: {
      globalPrivacyControl: !!opts.gpc,
      doNotTrack: opts.dnt ?? null,
      webdriver: !!opts.webdriver
    },
    document: {
      createElement: tag => ({ tag }),
      head: { appendChild: script => scripts.push(script) }
    }
  };
  vm.runInNewContext(inline[1], context, { filename: 'index.html:GA4' });
  return { scripts, window, sessionStorage };
}
test('homepage marked QA tab loads no GA4 tag and sends no config', () => {
  const x = runHomepageGA({ search: '?__astra_qa=1' });
  assert.equal(x.scripts.length, 0);
  assert.equal(x.window.dataLayer, undefined);
  assert.equal(x.sessionStorage.getItem('__astralabs_qa_no_track'), '1');
});
test('homepage QA exclusion persists through same-tab navigation', () => {
  const first = runHomepageGA({ search: '?__astra_qa=1' });
  const second = runHomepageGA({ sessionStorage: first.sessionStorage });
  assert.equal(second.scripts.length, 0);
  assert.equal(second.window.gtag, undefined);
});
test('homepage normal visitor still initializes one GA4 tag and config', () => {
  const x = runHomepageGA();
  assert.equal(x.scripts.length, 1);
  assert.match(x.scripts[0].src, /^https:\/\/www\.googletagmanager\.com\/gtag\/js\?id=G-16044108056$/);
  assert.equal(x.window.dataLayer.length, 2);
  assert.equal(x.window.dataLayer[0][0], 'js');
  assert.equal(x.window.dataLayer[1][0], 'config');
  assert.equal(x.window.dataLayer[1][1], 'G-16044108056');
});
test('homepage GA4 respects GPC, DNT and webdriver opt-outs', () => {
  for (const opts of [{ gpc: true }, { dnt: '1' }, { webdriver: true }]) {
    const x = runHomepageGA(opts);
    assert.equal(x.scripts.length, 0);
    assert.equal(x.window.dataLayer, undefined);
  }
});
test('homepage explicitly marked QA suppresses GA4 even when sessionStorage is blocked', () => {
  const blocked = {
    getItem: () => { throw Error('storage blocked'); },
    setItem: () => { throw Error('storage blocked'); }
  };
  const x = runHomepageGA({ search: '?__astra_qa=1', sessionStorage: blocked });
  assert.equal(x.scripts.length, 0);
});
