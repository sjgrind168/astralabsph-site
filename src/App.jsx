import logo from './assets/app-icons/astralabs.png';
const astramate = '/astramate-icon.webp';

const PLAY_URL = 'https://play.google.com/store/apps/details?id=com.astralabs.astramate&utm_source=astralabsph&utm_medium=website&utm_campaign=global_android_launch&utm_content=homepage';
const KEEPRY_URL = 'https://play.google.com/store/apps/details?id=com.astralabs.keepry&utm_source=astralabsph&utm_medium=website&utm_campaign=global_android_launch&utm_content=homepage';
const APP_STORE_URL = 'https://apps.apple.com/us/app/astramate/id6812828056';
const APP_STORE_BADGE_ART = 'https://developer.apple.com/assets/elements/badges/download-on-the-app-store.svg';
const GOOGLE_PLAY_BADGE_ART = 'https://play.google.com/intl/en_us/badges/static/images/badges/en_badge_web_generic.png';
const PIREVO_URL = 'https://pirevo.astralabsph.com/';
const KEEPRY_ICON = '/keepry-icon.webp';

const products = [
  { name: 'Astramate', label: 'Maritime toolkit · Android + iPhone', icon: astramate, live: true, url: PLAY_URL, iosUrl: APP_STORE_URL,
    lead: 'Checking cargo weight against hold volume? Astramate brings supported cargo, stowage-factor and draft/trim calculations together, with visible working for reviewing your own figures.',
    points: ['For deck officers, cadets and seafarers worldwide', 'Cargo weight, volume, stowage-factor and draft/trim calculation aids', 'Visible working for independent review against approved vessel information', 'Start free · optional one-time lifetime Premium unlocks more supported tools'] },
  { name: 'Keepry', label: 'Everyday organization · Worldwide · Android', icon: KEEPRY_ICON, live: true, url: KEEPRY_URL,
    lead: 'Your important document is in one folder and its renewal date is somewhere else. Keepry brings imported files, user-entered expiry dates and reminders into one local-first organizer.',
    points: ['For adults managing documents, household records and important dates worldwide', 'Local-first Vault for images and PDFs with searchable details', 'Validity dates, Life Admin and supported reminders', 'Start free · optional one-time Keepry Plus expands capacity and recurring reminders'] },
];

function App() {
  // Existing social campaigns already land on the canonical root with ?app=astramate/keepry.
  // Show the matching app FIRST without a redirect, preserving all UTM parameters.
  const requestedApp = (() => {
    try {
      const value = new URLSearchParams(window.location.search).get('app');
      return value === 'astramate' || value === 'keepry' ? value : null;
    } catch {
      return null;
    }
  })();
  const campaignProduct = products.find((product) => product.name.toLowerCase() === requestedApp);
  const alternateProduct = products.find((product) => product.name.toLowerCase() !== requestedApp);

  // Keep unique external campaign attribution when a visitor selects either app on the main storefront.
  const trackedPlay = (originalUrl, app) => {
    try {
      const source = new URLSearchParams(window.location.search);
      const destination = new URL(originalUrl);
      for (const key of ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content']) {
        const value = source.get(key);
        if (value && /^[A-Za-z0-9_-]{1,80}$/.test(value)) destination.searchParams.set(key, value);
      }
      const campaign = source.get('utm_content');
      if (campaign && /^[A-Za-z0-9_-]{1,65}$/.test(campaign)) {
        destination.searchParams.set('utm_content', campaign + '_' + app);
      }
      return destination.toString();
    } catch {
      return originalUrl;
    }
  };
  const goToApps = () => document.getElementById('apps')?.scrollIntoView({ behavior: 'smooth' });

  return (
    <div className="site">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="AstraLabs PH home">
          <img src={logo} alt="AstraLabs PH" />
          <span>
            <strong>AstraLabs PH</strong>
            <small>Software Development Studio</small>
          </span>
        </a>
        <nav>
          <a href="#apps">Apps</a>
          <a href="#updates">App updates</a>
          <a href="#studio">Studio</a>
          <a href={PIREVO_URL} target="_blank" rel="noopener noreferrer">PIREVO</a>
          <a href="mailto:contact@astralabsph.com">Contact</a>
        </nav>
      </header>

      <main id="top">
        <section className="hero">
          <div className="hero-copy">
            <div className="status-chip">ASTRAMATE LIVE ON iOS + ANDROID · KEEPRY LIVE ON ANDROID</div>
            {campaignProduct ? (
              <>
                <h1>{campaignProduct.name === 'Astramate' ? 'Cargo figures deserve a second look.' : 'Important documents. Important dates.'}
                  <span> {campaignProduct.name === 'Astramate' ? 'Meet Astramate.' : 'Keep them together with Keepry.'}</span>
                </h1>
                <p>{campaignProduct.lead} {campaignProduct.name === 'Astramate' ? 'Astramate is available now on iPhone and Android.' : 'Start with the free Android app.'} Optional one-time upgrades are available when you need more supported tools or capacity.</p>
                <div className="hero-actions">
                  <a className="official-store-badge google-play-official" href={trackedPlay(campaignProduct.url, requestedApp)} target="_blank" rel="noopener noreferrer" aria-label={`Get ${campaignProduct.name} on Google Play`}><img src={GOOGLE_PLAY_BADGE_ART} alt="Get it on Google Play" /></a>
                  {campaignProduct.name === 'Astramate' && <a className="official-store-badge app-store-official" href={APP_STORE_URL} target="_blank" rel="noopener noreferrer" aria-label="Download Astramate on the App Store"><img src={APP_STORE_BADGE_ART} alt="Download on the App Store" /></a>}
                  <a className="secondary-cta" href={`#${requestedApp}`}>See what {campaignProduct.name} helps you do ↓</a>
                  <a className="secondary-cta" href={trackedPlay(alternateProduct.url, alternateProduct.name.toLowerCase())} target="_blank" rel="noopener noreferrer">Explore {alternateProduct.name} ↗</a>
                </div>
              </>
            ) : (
              <>
                <h1>One studio. <span>Practical apps for life on land and work at sea.</span></h1>
                <p>Review cargo, stowage-factor and draft calculations with Astramate. Keep important documents, expiry dates and Life Admin together with Keepry. Astramate is now on iPhone and Android; Keepry is available on Android while its iOS release progresses through App Store review.</p>
                <div className="hero-actions">
                  <a className="official-store-badge app-store-official" href={APP_STORE_URL} target="_blank" rel="noopener noreferrer" aria-label="Download Astramate on the App Store"><img src={APP_STORE_BADGE_ART} alt="Download on the App Store" /></a>
                  <a className="official-store-badge google-play-official" href={trackedPlay(PLAY_URL, 'astramate')} target="_blank" rel="noopener noreferrer" aria-label="Get Astramate on Google Play"><img src={GOOGLE_PLAY_BADGE_ART} alt="Get it on Google Play" /></a>
                  <button onClick={goToApps}>Explore both apps</button>
                </div>
              </>
            )}
            <div className="trust-row">
              <span>Verified store distribution</span>
              <span>Privacy-first product direction</span>
              <span>Astramate on iOS + Android · Keepry on Android</span>
            </div>
          </div>

          <div className="hero-panel">
            <div className="orbit-card primary">
              <img src={astramate} alt="Astramate app icon" />
              <span>Astramate</span>
              <b>LIVE ON APP STORE + GOOGLE PLAY · TOOLS + CALCULATIONS</b>
            </div>
            <div className="orbit-card"><img src={KEEPRY_ICON} alt="Keepry app icon" /><span>Keepry</span><b>LIVE ON GOOGLE PLAY · PRIVATE VAULT + REMINDERS</b></div>
            <div className="panel-note">Two practical apps. More platforms on the way.</div>
          </div>
        </section>

        <section className="notice-band">
          <div>
            <strong>Astramate and Keepry are live.</strong>
            <span>Astramate is now live on the App Store for iPhone and on Google Play. Keepry is live on Google Play, with iOS still in App Store review. Use only the official store links on this website.</span>
          </div>
          <a href="#apps">EXPLORE THE APPS ↓</a>
        </section>

        <section className="apps-section" id="apps">
          <div className="section-head">
            <p>ASTRAMATE: iOS + ANDROID · KEEPRY: ANDROID</p>
            <h2>Made for people worldwide, on land and at sea.</h2>
            <span>Astramate supports a global maritime audience, from cadets and maritime students to working seafarers and training groups, and is now available on iPhone and Android. Keepry helps anyone organize everyday documents and reminders and is currently available on Android.</span>
          </div>

          <div className="product-grid">
            {products.map((product) => (
              <article id={product.name.toLowerCase()} className={product.live ? 'product-card featured' : 'product-card'} key={product.name}>
                <div className="card-top">
                  {product.icon ? <img className="product-icon-image" src={product.icon} alt="" /> : <span className="product-mark">{product.mark}</span>}
                  <span className={product.live ? 'launch-pill live' : 'launch-pill'}>{product.live ? (product.name === 'Astramate' ? 'Available on iOS + Android' : 'Available on Google Play') : 'Launching Soon'}</span>
                </div>
                <small>{product.label}</small>
                <h3>{product.name}</h3>
                <p>{product.lead}</p>
                <ul>{product.points.map((point) => <li key={point}>{point}</li>)}</ul>
                {product.live ? (
                  <div className="store-action-row">
                    {product.name === 'Astramate' && (
                      <a className="official-store-badge app-store-official" href={APP_STORE_URL} target="_blank" rel="noopener noreferrer" aria-label="Download Astramate on the App Store"><img src={APP_STORE_BADGE_ART} alt="Download on the App Store" /></a>
                    )}
                    <a className="official-store-badge google-play-official" href={trackedPlay(product.url, product.name.toLowerCase())} target="_blank" rel="noopener noreferrer" aria-label={`Get ${product.name} on Google Play`}><img src={GOOGLE_PLAY_BADGE_ART} alt="Get it on Google Play" /></a>
                    {product.name !== 'Astramate' ? (
                      <span className="store-action ios-soon-action" aria-disabled="true" title="Keepry for iPhone is still in App Store review">iOS Coming Soon</span>
                    ) : null}
                  </div>
                ) : (
                  <div className="disabled-action" aria-disabled="true">Release page coming soon</div>
                )}
              </article>
            ))}
          </div>
        </section>

        <section className="global-guides" aria-label="Free educational guides for international audiences">
          <p className="guides-kicker">FREE PRACTICAL GUIDES · WORLDWIDE</p>
          <h2>Start with a useful question. Discover a practical tool.</h2>
          <div className="global-guide-grid">
            <article>
              <small>FOR SEAFARERS AND MARITIME STUDENTS</small>
              <h3>Cargo weight fits. Does the parcel fit the hold?</h3>
              <p>Five practical checks covering stowage factor, usable volume and approved vessel information.</p>
              <a href="/guides/cargo-weight-hold-volume-checklist/">Read the cargo-space checklist ↗</a>
            </article>
            <article>
              <small>FOR PEOPLE ORGANIZING IMPORTANT DOCUMENTS</small>
              <h3>Document photo saved. Expiry reminder set?</h3>
              <p>A simple routine for verifying dates, organizing records and reviewing renewal reminders.</p>
              <a href="/guides/document-expiry-reminder-checklist/">Read the document reminder checklist ↗</a>
            </article>
          </div>
        </section>

        <section className="studio-section" id="studio">
          <div className="studio-copy">
            <p>ABOUT THE STUDIO</p>
            <h2>Small studio. Useful software.</h2>
            <span>AstraLabs PH develops mobile and web applications, digital utility tools and practical software for everyday use. Our products are designed to simplify tasks, organize information, perform useful calculations and reduce avoidable friction.</span>
          </div>
          <div className="studio-grid">
            <article><b>Independent software studio</b><span>Lean product development with focused, maintainable apps.</span></article>
            <article><b>Useful automation</b><span>Automation and AI-assisted workflows where they genuinely save time.</span></article>
            <article><b>Calculation integrity</b><span>Technical calculators are specified and tested before release.</span></article>
            <article><b>International direction</b><span>New consumer apps are designed beyond a Philippines-only scope.</span></article>
          </div>
        </section>

        <section className="release-section" id="updates">
          <div>
            <p>RELEASE POLICY</p>
            <h2>Astramate is live on iPhone and Android. Keepry is live on Android.</h2>
            <span>Download Astramate from its official App Store or Google Play listing. Keepry is available from its official Google Play listing while its iOS release remains in review. Bookmark this website for verified store links, app updates and new releases.</span>
          </div>
          <div className="release-badge">
            <strong>ASTRAMATE LIVE ON iOS + ANDROID</strong>
            <small>Keepry is live on Android · official store links only</small>
            <div className="release-store-group"><span>Astramate</span><div className="release-store-badges"><a className="official-store-badge app-store-official" href={APP_STORE_URL} target="_blank" rel="noopener noreferrer" aria-label="Download Astramate on the App Store"><img src={APP_STORE_BADGE_ART} alt="Download on the App Store" /></a><a className="official-store-badge google-play-official" href={trackedPlay(PLAY_URL, 'astramate')} target="_blank" rel="noopener noreferrer" aria-label="Get Astramate on Google Play"><img src={GOOGLE_PLAY_BADGE_ART} alt="Get it on Google Play" /></a></div></div>
            <div className="release-store-group"><span>Keepry</span><div className="release-store-badges"><a className="official-store-badge google-play-official" href={trackedPlay(KEEPRY_URL, 'keepry')} target="_blank" rel="noopener noreferrer" aria-label="Get Keepry on Google Play"><img src={GOOGLE_PLAY_BADGE_ART} alt="Get it on Google Play" /></a></div></div>
          </div>
        </section>
      </main>

      <footer>
        <div>
          <strong>AstraLabs PH</strong>
          <span>AstraLabs Software Development Services</span>
        </div>
        <div className="footer-links">
          <a href="/privacy-policy/">AstraLabs PH Privacy Policy</a>
          <a href="/astramate-privacy-policy/">Astramate Privacy Policy</a>
          <a href="/keepry-privacy-policy/">Keepry Privacy Policy</a>
          <a href={PIREVO_URL} target="_blank" rel="noopener noreferrer">PIREVO shopping guides ↗</a>
          <a href="/astramate/">Astramate product guide</a>
          <a href="/keepry/">Keepry product guide</a>
          <a href="#updates">App releases & updates</a>
          <a href="mailto:contact@astralabsph.com">contact@astralabsph.com</a>
          <span>© 2026 AstraLabs PH</span>
        </div>
      </footer>
    </div>
  );
}

export default App;
