import logo from './assets/app-icons/astralabs.png';
const astramate = 'data:image/webp;base64,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';

const PLAY_URL = 'https://play.google.com/store/apps/details?id=com.astralabs.astramate';
const KEEPRY_URL = 'https://play.google.com/store/apps/details?id=com.astralabs.keepry';
const PIREVO_URL = 'https://pirevo.astralabsph.com/';
const KEEPRY_ICON = '/keepry-icon.webp';

const products = [
  { name: 'Astramate', label: 'Maritime toolkit · Android', icon: astramate, live: true, url: PLAY_URL,
    lead: 'Practical offline-first maritime calculations and operational tools for seafarers, maritime students, cadets and training communities worldwide.',
    points: ['For seafarers, deck officers, maritime students and maritime groups worldwide', 'Cargo, stability and operational calculators', 'Visible formulas and calculation steps', 'Offline-first core tools · optional one-time Premium'] },
  { name: 'Keepry', label: 'Everyday organization · Worldwide · Android', icon: KEEPRY_ICON, live: true, url: KEEPRY_URL,
    lead: 'For everyday life, anywhere in the world: organize important documents, expiry dates and reminders in one private, local-first place.',
    points: ['For everyone managing important dates and records worldwide', 'Private document vault and optional device biometrics', 'Life Admin, expiry tracking and reminders', 'Free essentials · optional one-time Keepry Plus'] },
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
          <a href="#updates">App updates</a>
          <a href="#studio">Studio</a>
          <a href={PIREVO_URL} target="_blank" rel="noopener noreferrer">PIREVO</a>
          <a href="mailto:contact@astralabsph.com">Contact</a>
        </nav>
      </header>

      <main id="top">
        <section className="hero">
          <div className="hero-copy">
            <div className="status-chip">TWO LIVE ANDROID APPS · BUILT FOR A WORLDWIDE AUDIENCE</div>
            <h1>Practical apps for <span>life on land and work at sea.</span></h1>
            <p>Discover Astramate, the practical maritime toolkit for seafarers and maritime students worldwide, and Keepry, the personal organizer for anyone who wants important documents and reminders in one place. Download free on Android.</p>
            <div className="hero-actions">
              <a className="primary-cta" href={PLAY_URL} target="_blank" rel="noopener noreferrer">Get Astramate free ↗</a>
              <a className="primary-cta" href={KEEPRY_URL} target="_blank" rel="noopener noreferrer">Get Keepry free ↗</a>
              <button onClick={goToApps}>Explore both apps</button>
            </div>
            <div className="trust-row">
              <span>Verified store distribution</span>
              <span>Privacy-first product direction</span>
              <span>Worldwide audiences · Android available now</span>
            </div>
          </div>

          <div className="hero-panel">
            <div className="orbit-card primary">
              <img src={astramate} alt="Astramate app icon" />
              <span>Astramate</span>
              <b>LIVE ON GOOGLE PLAY · TOOLS + CALCULATIONS</b>
            </div>
            <div className="orbit-card"><img src={KEEPRY_ICON} alt="Keepry app icon" /><span>Keepry</span><b>LIVE ON GOOGLE PLAY · PRIVATE VAULT + REMINDERS</b></div>
            <div className="panel-note">Two practical apps. More platforms on the way.</div>
          </div>
        </section>

        <section className="notice-band">
          <div>
            <strong>Astramate and Keepry are live.</strong>
            <span>Get both apps on Google Play today. Coming very soon to the App Store for iPhone and iPad, subject to review. Check this website for official app and release updates.</span>
          </div>
          <a href="#apps">EXPLORE THE APPS ↓</a>
        </section>

        <section className="apps-section" id="apps">
          <div className="section-head">
            <p>AVAILABLE NOW ON ANDROID</p>
            <h2>Made for people worldwide, on land and at sea.</h2>
            <span>Astramate supports a global maritime audience, from cadets and maritime students to working seafarers and training groups. Keepry helps anyone organize everyday documents and reminders. Choose your app and install from the official store.</span>
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
                  <a className="store-action" href={product.url} target="_blank" rel="noopener noreferrer">Get {product.name} on Google Play ↗</a>
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

        <section className="release-section" id="updates">
          <div>
            <p>RELEASE POLICY</p>
            <h2>Astramate and Keepry are live on Google Play.</h2>
            <span>Download the Android apps only from their official Google Play listings. iPhone and iPad versions are coming soon to the App Store. Their links will appear here after approval and publication. Bookmark this website for app updates, release announcements and new features.</span>
          </div>
          <div className="release-badge">
            <strong>ANDROID LIVE · iOS COMING SOON</strong>
            <small>Astramate + Keepry · official store listings · Watch this website for App Store links</small>
            <a href={PLAY_URL} target="_blank" rel="noopener noreferrer">Astramate ↗</a>
            <a href={KEEPRY_URL} target="_blank" rel="noopener noreferrer">Keepry ↗</a>
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
