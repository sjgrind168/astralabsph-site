import logo from './assets/app-icons/astralabs.png';
import astramate from './assets/app-icons/astramate.png';

const PLAY_URL = 'https://play.google.com/store/apps/details?id=com.astralabs.astramate';

const products = [
  {
    name: 'Astramate',
    label: 'New version',
    icon: astramate,
    live: true,
    lead: 'A practical maritime toolkit focused on useful onboard calculations and day-to-day seafarer tools.',
    points: ['Compass error tools', 'Navigation and voyage calculations', 'Operational utility calculators', 'No exam reviewer or bulky reference library'],
  },
  {
    name: 'Maritime Calculators',
    label: 'Working title',
    mark: '∑',
    lead: 'A focused standalone calculator app for day-to-day maritime computations.',
    points: ['Speed, distance and time', 'ETA and voyage calculations', 'Unit and operational conversions', 'Formula-first design with validation'],
  },
  {
    name: 'Cargo & Stability Tools',
    label: 'Working title',
    mark: '⚓',
    lead: 'Dedicated cargo-planning and stability utilities without crowding Astramate.',
    points: ['Cargo calculation tools', 'Stability-focused utilities', 'Clear inputs and traceable outputs', 'Built around verified formulas'],
  },
  {
    name: 'Keepry',
    label: 'Personal Admin + Private Vault',
    mark: 'K',
    lead: 'A focused personal-admin app for reminders, important records, documents, expiries and renewals.',
    points: ['Life-admin reminders', 'Private document vault', 'Smart capture and extraction', 'Expiry and renewal tracking'],
  },
  {
    name: 'Travel Buddy',
    label: 'Travel Companion',
    mark: '✈',
    lead: 'A dedicated trip companion so travel features stay separate from general life-admin.',
    points: ['Flight and trip reminders', 'Travel document checklist', 'Itinerary organization', 'Pre-departure alerts'],
  },
];

function App() {
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
          <a href="#studio">Studio</a>
          <a href="mailto:contact@astralabsph.com">Contact</a>
        </nav>
      </header>

      <main id="top">
        <section className="hero">
          <div className="hero-copy">
            <div className="status-chip">ASTRAMATE · NOW LIVE ON GOOGLE PLAY</div>
            <h1>Practical software for <span>real life, real work</span> and the journeys between.</h1>
            <p>AstraLabs PH builds focused software that solves one job well. Astramate is now live on Google Play, while the rest of the lineup continues through development and verified app-store preparation.</p>
            <div className="hero-actions">
              <a className="primary-cta" href={PLAY_URL} target="_blank" rel="noreferrer">Get Astramate on Google Play ↗</a>
              <button onClick={goToApps}>Explore the lineup</button>
            </div>
            <div className="trust-row">
              <span>Verified store distribution</span>
              <span>Privacy-first product direction</span>
              <span>Built for a global audience</span>
            </div>
          </div>

          <div className="hero-panel">
            <div className="orbit-card primary">
              <img src={astramate} alt="Astramate app icon" />
              <span>Astramate</span>
              <b>LIVE ON GOOGLE PLAY · TOOLS + CALCULATIONS</b>
            </div>
            <div className="orbit-card"><span className="orbit-mark">K</span><span>Keepry</span><b>PERSONAL ADMIN + PRIVATE VAULT</b></div>
            <div className="orbit-card"><span className="orbit-mark">✈</span><span>Travel Buddy</span><b>TRAVEL COMPANION</b></div>
            <div className="panel-note">Focused apps. Cleaner boundaries. Less bloat.</div>
          </div>
        </section>

        <section className="notice-band">
          <div>
            <strong>Astramate is live.</strong>
            <span>Get the new version through Google Play. Legacy direct-download links remain intentionally disabled.</span>
          </div>
          <a href={PLAY_URL} target="_blank" rel="noreferrer">OPEN GOOGLE PLAY ↗</a>
        </section>

        <section className="apps-section" id="apps">
          <div className="section-head">
            <p>THE ASTRA LABS LINEUP</p>
            <h2>One ecosystem, separate territories.</h2>
            <span>We are deliberately not pouring every feature into one app. Each product gets a tighter purpose, cleaner interface and its own development track.</span>
          </div>

          <div className="product-grid">
            {products.map((product) => (
              <article className={product.live ? 'product-card featured' : 'product-card'} key={product.name}>
                <div className="card-top">
                  {product.icon ? <img className="product-icon-image" src={product.icon} alt="" /> : <span className="product-mark">{product.mark}</span>}
                  <span className={product.live ? 'launch-pill live' : 'launch-pill'}>{product.live ? 'Available on Google Play' : 'Launching Soon'}</span>
                </div>
                <small>{product.label}</small>
                <h3>{product.name}</h3>
                <p>{product.lead}</p>
                <ul>{product.points.map((point) => <li key={point}>{point}</li>)}</ul>
                {product.live ? (
                  <a className="store-action" href={PLAY_URL} target="_blank" rel="noreferrer">Get Astramate on Google Play ↗</a>
                ) : (
                  <div className="disabled-action" aria-disabled="true">Release page coming soon</div>
                )}
              </article>
            ))}
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

        <section className="release-section">
          <div>
            <p>RELEASE POLICY</p>
            <h2>Astramate is live. Upcoming apps follow when ready.</h2>
            <span>Astramate is now distributed through Google Play. Direct APK links and legacy download buttons stay offline; future releases will continue through verified distribution channels and official AstraLabs pages.</span>
          </div>
          <div className="release-badge">
            <strong>ASTRAMATE · AVAILABLE ON GOOGLE PLAY</strong>
            <small>Verified store release · legacy APK downloads remain disabled</small>
            <a href={PLAY_URL} target="_blank" rel="noreferrer">Open listing ↗</a>
          </div>
        </section>
      </main>

      <footer>
        <div>
          <strong>AstraLabs PH</strong>
          <span>AstraLabs Software Development Services</span>
        </div>
        <div className="footer-links">
          <a href="/astramate-privacy-policy/">Astramate Privacy Policy</a>
          <a href="mailto:contact@astralabsph.com">contact@astralabsph.com</a>
          <span>© 2026 AstraLabs PH</span>
        </div>
      </footer>
    </div>
  );
}

export default App;
