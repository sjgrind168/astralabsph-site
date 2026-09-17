(() => {
  const KEEPRY_PLAY_URL = 'https://play.google.com/store/apps/details?id=com.astralabs.keepry';

  const addStyle = () => {
    if (document.getElementById('keepry-live-style')) return;
    const style = document.createElement('style');
    style.id = 'keepry-live-style';
    style.textContent = `
      @media (min-width: 901px) {
        .product-grid .product-card.featured { grid-column: auto; min-height: 390px; }
      }
    `;
    document.head.appendChild(style);
  };

  const patch = () => {
    addStyle();

    const statusChip = document.querySelector('.status-chip');
    if (statusChip) statusChip.textContent = 'ASTRAMATE + KEEPRY · LIVE ON GOOGLE PLAY';

    const heroCopy = document.querySelector('.hero-copy > p');
    if (heroCopy) {
      heroCopy.textContent = 'AstraLabs PH builds focused software that solves one job well. Astramate and Keepry are now live on Google Play, while the rest of the lineup continues through development and verified app-store preparation.';
    }

    const heroActions = document.querySelector('.hero-actions');
    if (heroActions && !heroActions.querySelector('[data-keepry-cta]')) {
      const link = document.createElement('a');
      link.dataset.keepryCta = 'true';
      link.href = KEEPRY_PLAY_URL;
      link.target = '_blank';
      link.rel = 'noreferrer';
      link.textContent = 'Get Keepry on Google Play ↗';
      const exploreButton = heroActions.querySelector('button');
      heroActions.insertBefore(link, exploreButton || null);
    }

    document.querySelectorAll('.orbit-card').forEach((card) => {
      const name = card.querySelector('span:not(.orbit-mark)');
      if (name?.textContent?.trim() !== 'Keepry') return;
      const detail = card.querySelector('b');
      if (detail) detail.textContent = 'LIVE ON GOOGLE PLAY · PERSONAL ADMIN + PRIVATE VAULT';
    });

    const notice = document.querySelector('.notice-band');
    if (notice) {
      const strong = notice.querySelector('strong');
      const span = notice.querySelector('span');
      const link = notice.querySelector('a');
      if (strong) strong.textContent = 'Astramate and Keepry are live.';
      if (span) span.textContent = 'Both apps are now available through Google Play. Legacy direct-download links remain intentionally disabled.';
      if (link) {
        link.href = '#apps';
        link.removeAttribute('target');
        link.removeAttribute('rel');
        link.textContent = 'VIEW LIVE APPS ↓';
      }
    }

    document.querySelectorAll('.product-card').forEach((card) => {
      const title = card.querySelector('h3');
      if (title?.textContent?.trim() !== 'Keepry') return;

      card.classList.add('featured');

      const pill = card.querySelector('.launch-pill');
      if (pill) {
        pill.classList.add('live');
        pill.textContent = 'Available on Google Play';
      }

      const disabled = card.querySelector('.disabled-action');
      if (disabled) {
        const link = document.createElement('a');
        link.className = 'store-action';
        link.href = KEEPRY_PLAY_URL;
        link.target = '_blank';
        link.rel = 'noreferrer';
        link.textContent = 'Get Keepry on Google Play ↗';
        disabled.replaceWith(link);
      }
    });

    const releaseSection = document.querySelector('.release-section');
    if (releaseSection) {
      const heading = releaseSection.querySelector('h2');
      const copy = releaseSection.querySelector(':scope > div:first-child > span');
      const badge = releaseSection.querySelector('.release-badge');
      if (heading) heading.textContent = 'Astramate and Keepry are live. Upcoming apps follow when ready.';
      if (copy) copy.textContent = 'Astramate and Keepry are now distributed through Google Play. Direct APK links and legacy download buttons stay offline; future releases will continue through verified distribution channels and official AstraLabs pages.';
      if (badge) {
        const strong = badge.querySelector('strong');
        const small = badge.querySelector('small');
        if (strong) strong.textContent = '2 APPS · AVAILABLE ON GOOGLE PLAY';
        if (small) small.textContent = 'Astramate + Keepry · verified store releases';
        if (!badge.querySelector('[data-keepry-release-link]')) {
          const link = document.createElement('a');
          link.dataset.keepryReleaseLink = 'true';
          link.href = KEEPRY_PLAY_URL;
          link.target = '_blank';
          link.rel = 'noreferrer';
          link.textContent = 'Open Keepry listing ↗';
          badge.appendChild(link);
        }
      }
    }

    document.documentElement.dataset.keepryLive = 'true';
  };

  const observer = new MutationObserver(() => {
    if (document.querySelector('.product-card h3')) {
      patch();
      observer.disconnect();
    }
  });

  observer.observe(document.documentElement, { childList: true, subtree: true });
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', patch, { once: true });
  } else {
    patch();
  }
  setTimeout(patch, 250);
})();
