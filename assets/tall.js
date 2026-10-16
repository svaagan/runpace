/* ─────────────────────────────────────────────────────────────
   runpace.no/tall/ — tegner tallsida fra /tall/tall.json.
   Fila skrives hver natt av hjemmeserveren (runpace-analyse,
   dashboard.mjs) og pushes hit. Ingen avhengigheter.
   ───────────────────────────────────────────────────────────── */
(function () {
  'use strict';

  var NS = 'http://www.w3.org/2000/svg';
  var MND = ['januar', 'februar', 'mars', 'april', 'mai', 'juni', 'juli',
             'august', 'september', 'oktober', 'november', 'desember'];
  var KJOP = ['pro', 'supporter', 'app', 'annet'];

  var tall = function (n) { return Math.round(n).toLocaleString('nb-NO'); };
  var kr = function (n) { return tall(n) + ' kr'; };
  var dato = function (s) { return new Date(s + 'T00:00:00Z'); };
  var iso = function (d) { return d.toISOString().slice(0, 10); };
  var pen = function (s) { var d = dato(s); return d.getUTCDate() + '. ' + MND[d.getUTCMonth()] + ' ' + d.getUTCFullYear(); };
  var kort = function (s) { var d = dato(s); return d.getUTCDate() + '.' + (d.getUTCMonth() + 1) + '.'; };
  var kjop = function (x) { return KJOP.reduce(function (a, k) { return a + (x[k] || 0); }, 0); };

  function mandag(s) {
    var d = dato(s);
    d.setUTCDate(d.getUTCDate() - ((d.getUTCDay() + 6) % 7));
    return iso(d);
  }

  /** Uke for uke fra første til siste dag, med tomme uker som null. */
  function uker(data) {
    var ut = [], per = {};
    Object.keys(data.perDag).forEach(function (d) {
      var u = mandag(d), x = data.perDag[d];
      var w = per[u] || (per[u] = { nedlastinger: 0, kr: 0, pro: 0, supporter: 0, app: 0, annet: 0 });
      Object.keys(w).forEach(function (k) { w[k] += x[k] || 0; });
    });
    for (var d = dato(mandag(data.forsteDag)); iso(d) <= data.oppdatert; d.setUTCDate(d.getUTCDate() + 7)) {
      var u = iso(d);
      ut.push({ uke: u, v: per[u] || { nedlastinger: 0, kr: 0, pro: 0, supporter: 0, app: 0, annet: 0 } });
    }
    return ut;
  }

  function el(navn, attr, tekst) {
    var e = document.createElementNS(NS, navn);
    for (var k in attr) e.setAttribute(k, attr[k]);
    if (tekst != null) e.textContent = tekst;
    return e;
  }

  /** Søylediagram med én serie. Toppen er rundet, foten står på grunnlinja. */
  function soyler(boks, rader, verdi, tips) {
    boks.innerHTML = '';
    var B = Math.max(280, boks.clientWidth), H = 220;
    var venstre = 40, hoyre = 8, topp = 22, bunn = 26;
    var bredde = B - venstre - hoyre, hoyde = H - topp - bunn;
    var maks = Math.max.apply(null, rader.map(verdi).concat([1]));
    // Pene trinn på y-aksen: 1, 2 eller 5 ganger en tierpotens
    var steg = Math.pow(10, Math.floor(Math.log10(maks)));
    if (maks / steg > 5) steg *= 2; else if (maks / steg < 2) steg /= 2;
    if (steg < 1) steg = 1;
    var tak = Math.ceil(maks / steg) * steg;
    var y = function (v) { return topp + hoyde - (v / tak) * hoyde; };

    var svg = el('svg', { viewBox: '0 0 ' + B + ' ' + H, width: B, height: H });
    for (var g = 0; g <= tak; g += steg) {
      svg.appendChild(el('line', { x1: venstre, x2: B - hoyre, y1: y(g), y2: y(g), 'class': g ? 'rutenett' : 'akse' }));
      svg.appendChild(el('text', { x: venstre - 8, y: y(g) + 4, 'text-anchor': 'end' }, tall(g)));
    }

    var trinn = bredde / rader.length;
    var sb = Math.max(2, Math.min(36, trinn - 2));          // 2 px luft mellom søylene
    var etikettHver = Math.ceil(46 / trinn);
    var imaks = rader.map(verdi).indexOf(maks);
    var soylene = [];

    rader.forEach(function (r, i) {
      var v = verdi(r), x = venstre + i * trinn + (trinn - sb) / 2, h = y(0) - y(v);
      var s;
      if (v > 0) {
        var rr = Math.min(4, sb / 2, h);
        // Rundet topp, rett fot
        s = el('path', { 'class': 'soyle', d:
          'M' + x + ',' + y(0) + 'V' + (y(v) + rr) + 'Q' + x + ',' + y(v) + ' ' + (x + rr) + ',' + y(v) +
          'H' + (x + sb - rr) + 'Q' + (x + sb) + ',' + y(v) + ' ' + (x + sb) + ',' + (y(v) + rr) + 'V' + y(0) + 'Z' });
        if (h < 1) s.setAttribute('d', 'M' + x + ',' + y(0) + 'h' + sb + 'v-1h-' + sb + 'Z');
        svg.appendChild(s);
      }
      soylene.push(s);
      // Verdien skrives bare på den høyeste og den siste søyla
      if (v > 0 && (i === imaks || i === rader.length - 1)) {
        svg.appendChild(el('text', { 'class': 'verdi', x: x + sb / 2, y: y(v) - 6, 'text-anchor': 'middle' }, tall(v)));
      }
      if (i % etikettHver === 0 || i === rader.length - 1) {
        if (i === rader.length - 1 && i % etikettHver && (i % etikettHver) < etikettHver / 2) return;
        svg.appendChild(el('text', { x: x + sb / 2, y: H - 8, 'text-anchor': 'middle' }, kort(r.uke)));
      }
    });

    // Treffflater i hele kolonnas høyde — større enn søyla, så tynne søyler kan pekes på
    var lapp = document.createElement('div');
    lapp.className = 'tall-tips hidden';
    rader.forEach(function (r, i) {
      var t = el('rect', { 'class': 'treff', x: venstre + i * trinn, y: topp, width: trinn, height: hoyde });
      var vis = function () {
        soylene.forEach(function (s) { if (s) s.classList.remove('aktiv'); });
        if (soylene[i]) soylene[i].classList.add('aktiv');
        lapp.innerHTML = tips(r);
        lapp.style.left = (venstre + i * trinn + trinn / 2) / B * 100 + '%';
        lapp.style.top = Math.max(0, y(verdi(r)) - 10) + 'px';
        lapp.classList.remove('hidden');
      };
      t.addEventListener('pointerenter', vis);
      t.addEventListener('pointerdown', vis);
      svg.appendChild(t);
    });
    svg.addEventListener('pointerleave', function () {
      lapp.classList.add('hidden');
      soylene.forEach(function (s) { if (s) s.classList.remove('aktiv'); });
    });
    boks.appendChild(svg);
    boks.appendChild(lapp);
  }

  function ukeTekst(r) {
    var slutt = dato(r.uke); slutt.setUTCDate(slutt.getUTCDate() + 6);
    return '<span>Uka ' + kort(r.uke) + '–' + kort(iso(slutt)) + '</span><br>';
  }

  function maneder(data) {
    var per = {};
    Object.keys(data.perDag).forEach(function (d) {
      var m = d.slice(0, 7), x = data.perDag[d];
      var w = per[m] || (per[m] = { nedlastinger: 0, pro: 0, supporter: 0, app: 0, annet: 0, kr: 0 });
      Object.keys(w).forEach(function (k) { w[k] += x[k] || 0; });
    });
    var rader = Object.keys(per).sort().map(function (m) {
      var x = per[m], d = dato(m + '-01');
      return '<tr><td>' + MND[d.getUTCMonth()] + ' ' + d.getUTCFullYear() + '</td>' +
        '<td class="num">' + tall(x.nedlastinger) + '</td><td class="num">' + tall(x.pro) + '</td>' +
        '<td class="num">' + tall(x.supporter) + '</td><td class="num">' + tall(x.app + x.annet) + '</td>' +
        '<td class="num">' + kr(x.kr) + '</td></tr>';
    });
    var t = data.totalt, sum = function (k) {
      return Object.keys(per).reduce(function (a, m) { return a + per[m][k]; }, 0);
    };
    document.querySelector('#tall-maned tbody').innerHTML = rader.join('');
    var fot = document.createElement('tfoot');
    fot.innerHTML = '<tr><td>I alt</td><td class="num">' + tall(t.nedlastinger) + '</td>' +
      '<td class="num">' + tall(sum('pro')) + '</td><td class="num">' + tall(sum('supporter')) + '</td>' +
      '<td class="num">' + tall(sum('app') + sum('annet')) + '</td><td class="num">' + kr(t.kr) + '</td></tr>';
    document.getElementById('tall-maned').appendChild(fot);
  }

  function tegn(data) {
    var t = data.totalt;
    var grense = dato(data.oppdatert); grense.setUTCDate(grense.getUTCDate() - 29);
    var siste = { nedlastinger: 0, kjop: 0, kr: 0 };
    Object.keys(data.perDag).forEach(function (d) {
      if (d < iso(grense)) return;
      var x = data.perDag[d];
      siste.nedlastinger += x.nedlastinger; siste.kjop += kjop(x); siste.kr += x.kr;
    });

    document.getElementById('tall-oppdatert').textContent =
      'Tall til og med ' + pen(data.oppdatert) + ' · siden ' + pen(data.forsteDag);
    document.getElementById('kpi-nedlastinger').textContent = tall(t.nedlastinger);
    document.getElementById('kpi-kjop').textContent = tall(t.kjop);
    document.getElementById('kpi-kr').textContent = kr(t.kr);
    document.getElementById('kpi-nedlastinger-30').textContent = tall(siste.nedlastinger) + ' siste 30 dager';
    document.getElementById('kpi-kjop-30').textContent = tall(siste.kjop) + ' siste 30 dager';
    document.getElementById('kpi-kr-30').textContent = kr(siste.kr) + ' siste 30 dager';

    var u = uker(data);
    var tegnGrafer = function () {
      soyler(document.getElementById('graf-nedlastinger'), u,
        function (r) { return r.v.nedlastinger; },
        function (r) { var n = r.v.nedlastinger; return ukeTekst(r) + tall(n) + (n === 1 ? ' nedlasting' : ' nedlastinger'); });
      soyler(document.getElementById('graf-kr'), u,
        function (r) { return r.v.kr; },
        function (r) {
          var deler = [['Pro', r.v.pro], ['Supporter', r.v.supporter], ['Appen', r.v.app + r.v.annet]]
            .filter(function (p) { return p[1]; }).map(function (p) { return p[1] + ' ' + p[0]; });
          return ukeTekst(r) + kr(r.v.kr) + (deler.length ? ' · ' + deler.join(', ') : ' · ingen kjøp');
        });
    };
    tegnGrafer();
    var bredde = window.innerWidth, vent;
    window.addEventListener('resize', function () {
      if (window.innerWidth === bredde) return;   // iOS sender resize når adresselinja glir
      bredde = window.innerWidth;
      clearTimeout(vent); vent = setTimeout(tegnGrafer, 120);
    });
    maneder(data);
  }

  fetch('/tall/tall.json', { cache: 'no-cache' })
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(tegn)
    ['catch'](function () {
      document.getElementById('tall-oppdatert').textContent =
        'Tallene kunne ikke hentes akkurat nå. Prøv igjen senere.';
    });
})();
