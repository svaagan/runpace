/* ─────────────────────────────────────────────────────────────
   runpace.no — kalkulatormotoren
   Hjulene, tempo-/fartomregningen, løpstidene og mellomtidstabellen.
   Lastes bare av forsida og /mellomtider/.

   Delene bygges bare hvis elementene de trenger finnes på sida, så
   den samme fila driver begge verktøyene.
   ───────────────────────────────────────────────────────────── */
(function () {
  'use strict';

  // Sida finnes på norsk og engelsk. Alt brukeren ser hentes herfra.
  var LANG = (document.documentElement.lang || 'nb').slice(0, 2) === 'en' ? 'en' : 'nb';
  var L = {
    nb: { dist: 'Distanse', total: 'Total tid', target: 'Måltid', kmh: 'km/t',
          interval: 'Mellomtid hver', splitCol: 'Mellomtid',
          empty: 'Velg distanse og måltid', custom: 'Egendefinert',
          finish: 'Mål', thousands: '\u00a0',
          mile: '1 engelsk mil', half: 'Halvmaraton', full: 'Maraton',
          d: function (k) { return k + ' km'; },
          dec: ',' },
    en: { dist: 'Distance', total: 'Total time', target: 'Target time', kmh: 'km/h',
          interval: 'Split frequency', splitCol: 'Split',
          empty: 'Choose distance and target time', custom: 'Custom',
          finish: 'Finish', thousands: ',',
          mile: '1 mile', half: 'Half marathon', full: 'Marathon',
          d: function (k) { return k + 'K'; },
          dec: '.' }
  }[LANG];

  // Desimaltall: norsk bruker komma, engelsk punktum.
  function num(x, decimals) {
    return x.toFixed(decimals).replace('.', L.dec);
  }

  // Tusenskille: hardt mellomrom på norsk, komma på engelsk
  function fmtMeters(km) {
    return String(Math.round(km * 1000)).replace(/\B(?=(\d{3})+(?!\d))/g, L.thousands);
  }

  const ITEM_H = 40;

  const DISTANCES = [
    { id: 'd1k',    name: L.d('1'),            km: 1,        hasHours: false },
    { id: 'mile',   name: L.mile,         km: 1.60934,  hasHours: false },
    { id: 'd3k',    name: L.d('3'),           km: 3,        hasHours: false },
    { id: 'd5k',    name: L.d('5'),           km: 5,        hasHours: false },
    { id: 'd10k',   name: L.d('10'),          km: 10,       hasHours: true  },
    { id: 'half',   name: L.half,         km: 21.0975,  hasHours: true  },
    { id: 'full',   name: L.full,         km: 42.195,   hasHours: true  },
    { id: 'custom', name: L.custom,       km: null,     hasHours: true  },
  ];

  const INTERVAL_KMS = [0.1, 0.2, 0.4, 1, 2, 5, 10];
  const fmtIntervalDist = km => km < 1 ? `${Math.round(km * 1000)} m` : L.d(km);

  let maalCustomUnit = 'km';

  function buildMaalCustomWheel() {
    const wrap = document.getElementById('maalCustomWheelWrap');
    wrap.innerHTML = '';
    let items;
    if (maalCustomUnit === 'm') {
      items = [...Array(99).keys()].map(i => `${fmtMeters((i + 1) * 0.1)} m`);
    } else {
      items = [...Array(100).keys()].map(i => `${i + 1} km`);
    }
    wrap.appendChild(makeWheel('maal-custom', 'val', items, 'w-maal w-maal-custom', updateMaalResult, null));
  }

  function setMaalUnit(unit) {
    const prevKm = getMaalCustomKm() || 0;
    maalCustomUnit = unit;
    document.getElementById('maalUnitM').classList.toggle('active',  unit === 'm');
    document.getElementById('maalUnitKm').classList.toggle('active', unit === 'km');
    buildMaalCustomWheel();
    requestAnimationFrame(() => {
      if (prevKm > 0) {
        const idx = unit === 'm'
          ? Math.max(0, Math.min(98,  Math.round(prevKm / 0.1) - 1))
          : Math.max(0, Math.min(99, Math.round(prevKm)        - 1));
        setWheelValue('maal-custom', 'val', idx);
      }
      updateMaalResult();
    });
  }

  function getMaalCustomKm() {
    const idx = getWheelValue('maal-custom', 'val');
    return maalCustomUnit === 'm' ? (idx + 1) * 0.1 : idx + 1;
  }

  // ── Calculator ──
  const CALC_SPACER_H = ITEM_H; // 40 — 3-item wheel (1 above + selected + 1 below)

  function makeCalcSep(char) {
    const s = document.createElement('span');
    s.className = 'calc-sep'; s.textContent = char; return s;
  }

  function buildCalcPicker() {
    const container = document.getElementById('calcCombined');
    container.innerHTML = '';

    // ── Pace group ──
    const paceGroup = document.createElement('div');
    paceGroup.className = 'calc-group';
    const paceLabel = document.createElement('div');
    paceLabel.className = 'calc-group-label';
    paceLabel.textContent = 'min/km';
    const paceWrap = document.createElement('div');
    paceWrap.className = 'calc-picker-wrap';
    paceWrap.appendChild(makeWheel('calc', 'min', [...Array(16).keys()].map(String),                            'w-calc w-calc-narrow', onPaceWheelChange, CALC_SPACER_H));
    paceWrap.appendChild(makeCalcSep(':'));
    paceWrap.appendChild(makeWheel('calc', 'sec', [...Array(60).keys()].map(i => String(i).padStart(2,'0')), 'w-calc w-calc-wide',   onPaceWheelChange, CALC_SPACER_H));
    paceGroup.appendChild(paceLabel);
    paceGroup.appendChild(paceWrap);
    container.appendChild(paceGroup);

    // ── Divider ──
    const divider = document.createElement('div');
    divider.className = 'calc-divider';
    container.appendChild(divider);

    // ── Speed group ──
    const speedGroup = document.createElement('div');
    speedGroup.className = 'calc-group';
    const speedLabel = document.createElement('div');
    speedLabel.className = 'calc-group-label';
    speedLabel.textContent = L.kmh;
    const speedWrap = document.createElement('div');
    speedWrap.className = 'calc-picker-wrap';
    speedWrap.appendChild(makeWheel('calc', 'int', [...Array(41).keys()].map(String),    'w-calc w-calc-wide',   onSpeedWheelChange, CALC_SPACER_H));
    speedWrap.appendChild(makeCalcSep('.'));
    speedWrap.appendChild(makeWheel('calc', 'dec', [...Array(10).keys()].map(String),    'w-calc w-calc-narrow', onSpeedWheelChange, CALC_SPACER_H));
    speedGroup.appendChild(speedLabel);
    speedGroup.appendChild(speedWrap);
    container.appendChild(speedGroup);

    setCalcDefaults();
    // Layout kan mangle når skriften ennå ikke er lastet; kjør en gang til.
    window.addEventListener('load', setCalcDefaults);
  }

  // Standard: 5:00 min/km = 12,0 km/t
  function setCalcDefaults() {
    setWheelValue('calc', 'min', 5);
    setWheelValue('calc', 'sec', 0);
    setWheelValue('calc', 'int', 12);
    setWheelValue('calc', 'dec', 0);
    updateCalcDist();
  }

  // Prevent ping-pong between the two groups
  let ignoreSpeedUntil = 0;
  let ignorePaceUntil  = 0;

  function onPaceWheelChange() {
    if (Date.now() < ignorePaceUntil) return;
    const mins = getWheelValue('calc', 'min');
    const secs = getWheelValue('calc', 'sec');
    const totalMin = mins + secs/60;
    if (totalMin <= 0) return;
    const speed = 60 / totalMin;
    let intPart = Math.floor(speed);
    let decPart = Math.round((speed - intPart) * 10);
    if (decPart === 10) { intPart++; decPart = 0; }
    ignoreSpeedUntil = Date.now() + 300;
    setWheelValue('calc', 'int', Math.min(intPart, 40));
    setWheelValue('calc', 'dec', decPart);
    updateCalcDist();
  }

  function onSpeedWheelChange() {
    if (Date.now() < ignoreSpeedUntil) return;
    const speed = getWheelValue('calc', 'int') + getWheelValue('calc', 'dec') / 10;
    if (speed <= 0) return;
    const pace = 60 / speed;
    let mins = Math.floor(pace);
    let secs = Math.round((pace - mins) * 60);
    if (secs === 60) { mins++; secs = 0; }
    ignorePaceUntil = Date.now() + 300;
    setWheelValue('calc', 'min', Math.min(mins, 15));
    setWheelValue('calc', 'sec', secs);
    updateCalcDist();
  }

  function buildCalcDist() {
    const section = document.getElementById('calcDistSection');
    section.innerHTML = '';
    const header = document.createElement('div');
    header.className = 'calc-dist-header';
    header.innerHTML = '<span>' + L.dist + '</span><span>' + L.total + '</span>';
    section.appendChild(header);
    DISTANCES.filter(d => d.km).forEach(d => {
      const row = document.createElement('div');
      row.className = 'calc-dist-row';
      row.innerHTML = `
        <div><span class="calc-dist-name">${d.name}</span></div>
        <span class="calc-dist-time empty" id="cdist-${d.id}">–</span>`;
      section.appendChild(row);
    });
  }

  function updateCalcDist() {
    const pace = getCurrentPace();
    DISTANCES.forEach(d => {
      const el = document.getElementById(`cdist-${d.id}`);
      if (!el) return;
      if (pace) { el.textContent = fmtRaceTime(pace * d.km); el.className = 'calc-dist-time'; }
      else       { el.textContent = '–';                      el.className = 'calc-dist-time empty'; }
    });
  }

  function getCurrentPace() {
    const mins = getWheelValue('calc', 'min');
    const secs = getWheelValue('calc', 'sec');
    const t = mins + secs/60;
    return t > 0 ? t : null;
  }

  // ── Shared formatters ──
  function fmtPace(totalMin) {
    const m = Math.floor(totalMin);
    const s = Math.round((totalMin - m) * 60);
    if (s === 60) return `${m+1}:00`;
    return `${m}:${String(s).padStart(2,'0')}`;
  }
  function fmtRaceTime(totalMin) {
    const ts = Math.round(totalMin * 60);
    const h  = Math.floor(ts / 3600);
    const m  = Math.floor((ts % 3600) / 60);
    const s  = ts % 60;
    if (h > 0) return `${h}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
    return `${m}:${String(s).padStart(2,'0')}`;
  }

  // ── Picker builder ──
  function makeWheel(distId, col, items, widthClass, callback, spacerH) {
    const wheel = document.createElement('div');
    wheel.className = `picker-wheel ${widthClass}`;
    wheel.dataset.distId = distId;
    wheel.dataset.col    = col;
    const ts = document.createElement('div'); ts.className = 'picker-spacer';
    if (spacerH) ts.style.height = spacerH + 'px';
    wheel.appendChild(ts);
    items.forEach(item => {
      const el = document.createElement('div');
      el.className = 'picker-item'; el.textContent = item; wheel.appendChild(el);
    });
    const bs = document.createElement('div'); bs.className = 'picker-spacer';
    if (spacerH) bs.style.height = spacerH + 'px';
    wheel.appendChild(bs);
    let timer;
    wheel.addEventListener('scroll', () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        const idx = Math.round(wheel.scrollTop / ITEM_H);
        wheel.scrollTo({ top: idx * ITEM_H, behavior: 'smooth' });
        if (callback) callback();
      }, 120);
    }, { passive: true });
    return wheel;
  }

  function getWheelValue(distId, col) {
    const w = document.querySelector(`.picker-wheel[data-dist-id="${distId}"][data-col="${col}"]`);
    if (!w) return 0;
    return Math.round(w.scrollTop / ITEM_H);
  }
  function setWheelValue(distId, col, val) {
    const w = document.querySelector(`.picker-wheel[data-dist-id="${distId}"][data-col="${col}"]`);
    if (!w) return;
    w.scrollTop = val * ITEM_H;
  }

  // ── Distansefart ──
  function buildMaalPicker() {
    const container = document.getElementById('maalCombined');
    container.innerHTML = '';

    const distGroup = document.createElement('div');
    distGroup.className = 'calc-group';
    const distLabel = document.createElement('div');
    distLabel.className = 'calc-group-label';
    distLabel.textContent = L.dist;
    const distWrap = document.createElement('div');
    distWrap.className = 'calc-picker-wrap';
    distWrap.appendChild(makeWheel('maal', 'dist', DISTANCES.map(d => d.name), 'w-maal w-maal-dist', updateMaalResult, null));
    distGroup.appendChild(distLabel);
    distGroup.appendChild(distWrap);
    container.appendChild(distGroup);

    const divider = document.createElement('div');
    divider.className = 'calc-divider';
    container.appendChild(divider);

    const timeGroup = document.createElement('div');
    timeGroup.className = 'calc-group';
    const timeLabel = document.createElement('div');
    timeLabel.className = 'calc-group-label';
    timeLabel.textContent = L.target;
    const timeWrap = document.createElement('div');
    timeWrap.className = 'calc-picker-wrap';
    timeWrap.appendChild(makeWheel('maal', 'h', [...Array(10).keys()].map(String),                            'w-maal w-maal-h',  updateMaalResult, null));
    timeWrap.appendChild(makeCalcSep(':'));
    timeWrap.appendChild(makeWheel('maal', 'm', [...Array(60).keys()].map(i => String(i).padStart(2,'0')), 'w-maal w-maal-ms', updateMaalResult, null));
    timeWrap.appendChild(makeCalcSep(':'));
    timeWrap.appendChild(makeWheel('maal', 's', [...Array(60).keys()].map(i => String(i).padStart(2,'0')), 'w-maal w-maal-ms', updateMaalResult, null));
    timeGroup.appendChild(timeLabel);
    timeGroup.appendChild(timeWrap);
    container.appendChild(timeGroup);

    // Standard: 5 km på 25:00, som gir 5:00 min/km.
    // Indeks 3 er 5 km — indeks 2 er 3 km, og var feil her fra før.
    setMaalDefaults();
  }

  function setMaalDefaults() {
    setWheelValue('maal', 'dist', 3);      // 5 km
    setWheelValue('maal', 'h', 0);
    setWheelValue('maal', 'm', 25);        // 25:00
    setWheelValue('maal', 's', 0);
    setWheelValue('maal', 'interval', 3);  // mellomtid hver kilometer
    updateMaalResult();
  }

  function updateMaalResult() {
    const paceEl  = document.getElementById('maalPaceVal');
    const speedEl = document.getElementById('maalSpeedVal');
    const tbody   = document.getElementById('maal-pacing-tbody');
    const distIdx = getWheelValue('maal', 'dist');
    const h = getWheelValue('maal', 'h');
    const m = getWheelValue('maal', 'm');
    const s = getWheelValue('maal', 's');
    const totalMin = h*60 + m + s/60;
    const dist = DISTANCES[distIdx];

    const isCustom = dist && dist.id === 'custom';
    document.getElementById('maalCustomInput').classList.toggle('hidden', !isCustom);

    const km = isCustom ? getMaalCustomKm() : (dist ? dist.km : null);

    if (!km || km <= 0 || totalMin <= 0) {
      paceEl.textContent = '–';
      speedEl.textContent = '';
      tbody.innerHTML = '<tr><td colspan="2" class="pacing-placeholder">' + L.empty + '</td></tr>';
      return;
    }

    const pace  = totalMin / km;
    const speed = 60 / pace;
    paceEl.textContent = fmtPace(pace);
    speedEl.innerHTML  = '<span>' + num(speed, 2) + '</span> ' + L.kmh;

    // Build pacing table with selected interval
    const interval = INTERVAL_KMS[Math.min(getWheelValue('maal', 'interval'), INTERVAL_KMS.length - 1)];
    const rows = [];
    let ckm = interval;
    while (ckm < km - 0.001) {
      rows.push({ km: ckm, label: fmtIntervalDist(ckm), isFinish: false });
      ckm = Math.round((ckm + interval) * 1000) / 1000;
    }
    const lastCkm = rows.length > 0 ? rows[rows.length - 1].km : 0;
    if (Math.abs(lastCkm - km) < 0.001) {
      rows[rows.length - 1].isFinish = true;
    } else {
      let finLabel;
      if (isCustom) {
        finLabel = maalCustomUnit === 'm'
          ? L.finish + ' · ' + fmtMeters(km) + ' m'
          : L.finish + ' · ' + km + ' km';
      } else {
        finLabel = L.finish + ' · ' + dist.name;
      }
      rows.push({ km, label: finLabel, isFinish: true });
    }

    tbody.innerHTML = rows.map(r => `
      <tr class="${r.isFinish ? 'finish' : ''}">
        <td>${r.label}</td>
        <td>${fmtRaceTime(pace * r.km)}</td>
      </tr>`).join('');
  }

  // ── Oppstart ──
  // Forsida har bare kalkulatoren, /mellomtider/ har bare pacing-verktøyet.
  if (document.getElementById('calcCombined')) {
    buildCalcDist();
    buildCalcPicker();
  }
  if (document.getElementById('maalCombined')) {
    buildMaalPicker();
    buildMaalCustomWheel();
    document.getElementById('maalIntervalWrap').appendChild(
      makeWheel('maal', 'interval', INTERVAL_KMS.map(fmtIntervalDist),
                'w-maal w-maal-interval', updateMaalResult, null)
    );
    setMaalDefaults();
    // Layout kan mangle når skriften ennå ikke er lastet; kjør en gang til.
    window.addEventListener('load', setMaalDefaults);
  }

  // setMaalUnit kalles fra onclick i markup
  window.setMaalUnit = setMaalUnit;
})();
