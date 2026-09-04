/* ─────────────────────────────────────────────────────────────
   runpace.no — sidelogikk
   Meny, installeringsdialog, App Store-knapper og analytikk.
   Lastes av hver side. Ingen avhengigheter.
   ───────────────────────────────────────────────────────────── */
(function () {
  'use strict';

  var APP_STORE_URL = 'https://apps.apple.com/app/id6789667868';
  var UA = navigator.userAgent;
  var IS_IOS = /iPad|iPhone|iPod/.test(UA) ||
               (UA.indexOf('Macintosh') > -1 && navigator.maxTouchPoints > 1);
  var IS_ANDROID = /Android/.test(UA);
  var LANG = (document.documentElement.lang || 'nb').slice(0, 2);

  var T = {
    nb: {
      androidTitle: 'Legg RunPace på hjemskjermen',
      androidText:  'RunPace installeres rett fra nettleseren på Android — full skjerm, ' +
                    'på hjemskjermen, og den virker uten nett.',
      androidBtn:   'Legg til på hjemskjermen'
    },
    en: {
      androidTitle: 'Add RunPace to your home screen',
      androidText:  'RunPace installs straight from the browser on Android — full screen, ' +
                    'on your home screen, and it works offline.',
      androidBtn:   'Add to Home Screen'
    }
  };
  var t = T[LANG] || T.nb;

  /* ── Meny ───────────────────────────────────────────────── */
  var burger = document.querySelector('.hamburger');
  if (burger) {
    burger.addEventListener('click', function () {
      var open = document.body.classList.toggle('nav-open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }
  // Escape lukker det som er åpent
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    document.body.classList.remove('nav-open');
    if (burger) burger.setAttribute('aria-expanded', 'false');
    hideInstallModal();
  });

  /* ── Installeringsdialog ────────────────────────────────── */
  function showInstallModal() {
    // Chrome på Android kan installere direkte når manifestet er godkjent.
    // Da hoppes bruksanvisningen over.
    if (deferredPrompt) {
      deferredPrompt.prompt();
      deferredPrompt.userChoice.then(function () { deferredPrompt = null; });
      return;
    }
    document.body.classList.remove('nav-open');
    var m = document.getElementById('installModal');
    if (m) m.classList.remove('hidden');
  }
  function hideInstallModal(e) {
    var m = document.getElementById('installModal');
    if (!m) return;
    if (!e || e.target === m) m.classList.add('hidden');
  }
  var modal = document.getElementById('installModal');
  if (modal) {
    modal.addEventListener('click', hideInstallModal);
    var closeBtn = modal.querySelector('.modal-close');
    if (closeBtn) closeBtn.addEventListener('click', function () { modal.classList.add('hidden'); });
  }

  // Chrome tilbyr installering gjennom denne hendelsen; vi tar vare på
  // den og bruker den når brukeren faktisk trykker.
  var deferredPrompt = null;
  window.addEventListener('beforeinstallprompt', function (e) {
    e.preventDefault();
    deferredPrompt = e;
  });

  /* ── Analytikk ──────────────────────────────────────────── */
  var LIVE = location.hostname === 'runpace.no';

  function ping(params) {
    if (!LIVE) return;
    var q = Object.keys(params).map(function (k) {
      return encodeURIComponent(k) + '=' + encodeURIComponent(params[k]);
    }).join('&');
    fetch('https://svaagan-ubuntuserver.duckdns.org/track?' + q,
          { keepalive: true })['catch'](function () {});
  }

  // Klikk mot App Store logges som en referrer-verdi, slik at det dukker
  // opp i den analytikken som allerede finnes uten endring på serveren.
  function trackStore(placement) {
    ping({ ref: 'appstore-click:' + placement, ev: 'appstore',
           placement: placement, path: location.pathname });
  }

  function openStore(placement) {
    if (IS_ANDROID) { showInstallModal(); return; }
    trackStore(placement);
    window.open(APP_STORE_URL, '_blank', 'noopener');
  }

  /* ── App Store-knapper ──────────────────────────────────── */
  // Android har ingen App Store å sende folk til, så merket byttes ut
  // med installering på hjemskjermen.
  function applyDeviceCta() {
    document.querySelectorAll('[data-store-link]').forEach(function (a) {
      a.addEventListener('click', function () {
        trackStore(a.getAttribute('data-store-link') || 'link');
      });
    });
    document.querySelectorAll('[data-open-store]').forEach(function (b) {
      b.addEventListener('click', function () {
        openStore(b.getAttribute('data-open-store') || 'button');
      });
    });
    document.querySelectorAll('[data-install]').forEach(function (b) {
      b.addEventListener('click', showInstallModal);
    });

    if (!IS_ANDROID) return;

    document.querySelectorAll('[data-store-cta]').forEach(function (box) {
      var title = box.querySelector('.store-cta-title');
      var text  = box.querySelector('.store-cta-text');
      var badge = box.querySelector('.store-badge');
      if (title) title.textContent = t.androidTitle;
      if (text)  text.textContent  = t.androidText;
      if (badge) {
        var btn = document.createElement('button');
        btn.className = 'install-btn';
        btn.type = 'button';
        btn.textContent = t.androidBtn;
        btn.addEventListener('click', showInstallModal);
        badge.replaceWith(btn);
      }
    });
    // Merker utenfor CTA-kortene (topplinja, bunnen) skjules helt
    document.querySelectorAll('[data-ios-only]').forEach(function (el) {
      el.classList.add('hidden');
    });
    var ios = document.getElementById('stepsIos');
    var and = document.getElementById('stepsAndroid');
    if (ios && and) { ios.classList.add('hidden'); and.classList.remove('hidden'); }
  }

  applyDeviceCta();
  ping(document.referrer ? { ref: document.referrer, path: location.pathname }
                         : { path: location.pathname });

  /* ── Last på nytt etter lang tid i bakgrunnen ───────────── */
  var hiddenAt = 0;
  document.addEventListener('visibilitychange', function () {
    if (document.visibilityState === 'hidden') {
      hiddenAt = Date.now();
    } else if (navigator.onLine && hiddenAt && Date.now() - hiddenAt > 5 * 60 * 1000) {
      location.reload();
    }
  });

  // Brukes av markup og av kalkulatorsidene
  window.showInstallModal = showInstallModal;
  window.openStore = openStore;
  window.RunPace = { isIOS: IS_IOS, isAndroid: IS_ANDROID, storeUrl: APP_STORE_URL };
})();
