import logo from "./assets/app-icons/astralabs.png";
import astramate from "./assets/app-icons/astramate.png";
import lifeadminph from "./assets/app-icons/lifeadminph.png";
import comingsoon from "./assets/app-icons/coming-soon.svg";

const apps = [
  {
    name: "Astra Mate",
    icon: astramate,
    status: "LIVE",
    tagline: "Maritime Learning & Reference Assistant",
    desc: "Built for seafarers, cadets, and maritime professionals. A smart reference and learning companion onboard and on land.",
    buttons: [
      { label: "Open Astra Mate", url: "https://astramate.vercel.app/download", primary: true },
    ],
  },
  {
    name: "Life Admin PH",
    icon: lifeadminph,
    status: "EARLY ACCESS",
    tagline: "Adulting Assistant for Filipinos",
    desc: "Built for everyday life. Your organizer for reminders, documents, renewals, bills, and important deadlines.",
    buttons: [
      { label: "Soon in Play Store", url: "https://play.google.com/store/apps/details?id=com.astralabs.lifeadminph", primary: true },
      { label: "Early Access APK", url: "https://play.google.com/store/apps/details?id=com.astralabs.lifeadminph", primary: false },
    ],
  },
  {
    name: "Coming Soon",
    icon: comingsoon,
    status: "SOON",
    tagline: "More AstraLabs products",
    desc: "New apps and practical tools are currently under development.",
    buttons: [{ label: "Updates Soon", url: "#", primary: false }],
  },
];

const astraMateHelp = [
  ["🎓", "For Students & Cadets", "Review navigation topics, shipboard concepts, and maritime knowledge. Designed as a study guide, not a replacement for official learning materials."],
  ["👤", "For Aspiring Officers", "Prepare for exams and assessments with quick access to COLREGS, maritime safety, cargo basics, and navigation references."],
  ["⚙️", "For Onboard Officers", "Use as a quick reference for topics like gyro error, operational formulas, and bridge-related concepts."],
  ["📦", "Cargo & Loading Support", "Helpful for understanding loading information, cargo calculations, and related shipboard references."],
  ["🛡️", "Important Notice", "Astra Mate is for learning, guidance, and reference only. It does not replace official publications, shipboard manuals, company SMS, or professional judgment."],
];

const lapHelp = [
  ["🔔", "Smart Reminders", "Never miss important dates, bills, renewals, and deadlines. Get timely reminders for the things that matter most."],
  ["📁", "Document Tracking", "Track important documents like passport, driver's license, SSS, PhilHealth, Pag-IBIG, and more."],
  ["📅", "Renewal & Expiry Alerts", "Know when to renew your documents and licenses. Stay ahead with countdowns and expiry notifications."],
  ["💳", "Bills & Payments", "Organize bills and subscriptions. Keep track of due dates and payment status easily."],
  ["📈", "Organize Your Life", "From daily tasks to long-term goals, Life Admin PH helps you stay organized, productive, and in control."],
];

function App() {
  return (
    <main className="page">
      <div className="glow" />

      <header className="hero">
        <div className="brand">
          <img src={logo} alt="AstraLabs PH" />
          <div>
            <h3>AstraLabs PH</h3>
            <span>Digital Tools Ecosystem</span>
          </div>
        </div>

        <h1>Building tools that actually matter.</h1>
        <p>Practical digital products for productivity, learning, and modern Filipino life.</p>
      </header>

      <section className="apps">
        {apps.map((app) => (
          <article className="appCard" key={app.name}>
            <img className="appIcon" src={app.icon} alt={app.name} />

            <div className="appContent">
              <span className="status">{app.status}</span>
              <h2>{app.name}</h2>
              <h4>{app.tagline}</h4>
              <p>{app.desc}</p>

              <div className="buttonGroup">
                {app.buttons.map((button) => (
                  <a
                    key={button.label}
                    href={button.url}
                    target={button.url === "#" ? undefined : "_blank"}
                    rel="noreferrer"
                    className={button.primary ? "button primary" : "button secondary"}
                  >
                    {button.label}
                  </a>
                ))}
              </div>
            </div>
          </article>
        ))}
      </section>

      <section className="helpSection">
        <div className="helpHeader">
          <h1>How Our Apps Can Help</h1>
          <p>Two apps. One mission. Helping seafarers and Filipinos stay prepared, organized, and always ready.</p>
        </div>

        <div className="helpGrid">
          <div className="helpColumn">
            <div className="productHeader">
              <img src={astramate} alt="Astra Mate" />
              <div>
                <h2>Astra Mate</h2>
                <p>Maritime Learning & Reference Assistant</p>
              </div>
            </div>

            {astraMateHelp.map(([icon, title, text]) => (
              <div className="helpCard" key={title}>
                <div className="helpIcon blue">{icon}</div>
                <div>
                  <h3>{title}</h3>
                  <p>{text}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="helpColumn">
            <div className="productHeader">
              <img src={lifeadminph} alt="Life Admin PH" />
              <div>
                <h2>Life Admin PH</h2>
                <p className="greenText">Adulting Assistant for Filipinos</p>
              </div>
            </div>

            {lapHelp.map(([icon, title, text]) => (
              <div className="helpCard" key={title}>
                <div className="helpIcon green">{icon}</div>
                <div>
                  <h3 className="greenText">{title}</h3>
                  <p>{text}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="mission">
          <strong>Two apps. One goal.</strong>
          <span>AstraLabs PH is committed to building practical tools that help seafarers excel at sea and Filipinos thrive on land.</span>
        </div>
      </section>


      
      <section className="trustLegal">
        <div className="trustGrid">
          <div className="trustCard">
            <h3>🔒 Secure Payments</h3>
            <p>Payments must only be made through official AstraLabs PH checkout pages, verified payment partners, or links posted on official AstraLabs PH websites. Do not send payments to unofficial accounts or private messages.</p>
          </div>

          <div className="trustCard">
            <h3>⬇️ Secure Downloads</h3>
            <p>Only download AstraLabs apps from astralabsph.com, official AstraLabs PH download pages, or verified app store listings. AstraLabs PH is not responsible for modified, copied, reuploaded, or unofficial app files.</p>
          </div>

          <div className="trustCard">
            <h3>⚠️ Use at Your Own Discretion</h3>
            <p>AstraLabs apps are provided for productivity, learning, reminders, and reference support only. They do not replace official documents, professional advice, shipboard procedures, government rules, company policies, or the judgment of qualified professionals.</p>
          </div>
        </div>

        <div className="legalBox">
          <h2>Privacy Policy</h2>
          <p>AstraLabs PH respects user privacy. Information provided through our apps or support channels may be used only to operate the app, provide support, improve services, process payments, and maintain account or subscription access where applicable.</p>
          <p>Users are responsible for the accuracy of the information they enter. AstraLabs PH does not sell personal information. Third-party services such as hosting, payment processors, analytics, app stores, or authentication providers may process data according to their own policies.</p>
        </div>

        <div className="legalBox">
          <h2>Terms of Use & Disclaimer</h2>
          <p>By using AstraLabs PH apps or websites, users agree that the tools are provided “as is” for guidance, productivity, learning, and organizational purposes. AstraLabs PH does not guarantee that all information, reminders, calculations, references, or app outputs will always be complete, updated, error-free, or suitable for every situation.</p>
          <p>For maritime use, Astra Mate is not a replacement for official nautical publications, vessel procedures, company SMS, class requirements, regulatory instructions, or licensed professional judgment. For Life Admin PH, reminders and document tracking are not a replacement for official government records, agency requirements, legal advice, or financial advice.</p>
          <p>Users remain fully responsible for verifying information, meeting deadlines, complying with laws and regulations, and making final decisions. AstraLabs PH shall not be held liable for losses, penalties, missed deadlines, operational decisions, data issues, or damages arising from reliance on the apps, websites, downloads, or third-party links.</p>
        </div>

        <div className="legalLinks">
          <a href="mailto:astralabsph@gmail.com">Contact Support: astralabsph@gmail.com</a>
        </div>
      </section>


      <footer>© 2026 AstraLabs PH. All Rights Reserved.</footer>
    </main>
  );
}

export default App;
