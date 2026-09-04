# RunPace — runpace.no

Løpekalkulator for tempo, fart og mellomtider. Publisert på
**[runpace.no](https://runpace.no)** via GitHub Pages.

Sida finnes på norsk (i rota) og engelsk (under `/en/`), koblet med `hreflang`.

---

## ⚠️ Rediger aldri HTML-filene direkte

Alle `index.html`-filene er **generert**. Redigerer du dem, blir endringen
borte neste gang noen kjører byggeren.

| Skal du endre …            | Rediger da …                        |
|----------------------------|-------------------------------------|
| Brødtekst på en side       | `_src/body/<nb\|en>/<navn>.html`    |
| Tittel, meta, URL, schema  | `_src/build.py` (`PAGES`-registeret) |
| Meny, bunn, topplinje      | `_src/chrome.py`                    |
| Tabellene                  | `_src/tables.py`                    |
| Formlene                   | `_src/pacemath.py`                  |
| Design                     | `assets/site.css`                   |
| Kalkulatoren               | `assets/calc.js`, `assets/calc.css` |

Etterpå:

```bash
python3 _src/build.py     # skriver alle HTML-filene, sitemap, robots, llms.txt, 404
python3 _src/check.py     # døde lenker, hreflang, schema, HTML-nøsting, én h1 per side
git add -A && git commit -m "..." && git push
```

**Publiseringen har ikke noe byggsteg.** GitHub Pages serverer rå filer fra
`main`. Byggeren kjøres lokalt og resultatet committes, så en feil i Python
kan aldri ta ned nettsida. Push er live etter et par minutter.

---

## Struktur

```
/                             Løpekalkulator (forside)      ← index.html
/mellomtider/                 Mellomtider: måltid → splitter
/app/                         Produktside for iOS-appen
/tabeller/…                   Seks tempotabeller + hub
/guider/…                     Sju guider + hub
/om/  /faq/  /personvern/     Info
/support/                     Støtte (Support-URL i App Store Connect)
/en/…                         Engelsk utvalg (12 sider)

assets/     site.css, site.js (alle sider) · calc.css, calc.js (verktøysidene)
            appstore-no.svg, appstore-en.svg — Apples offisielle merker
icons/      PWA-ikoner, hentet fra iOS-appens appikon
og/         Delebilder 1200×630, laget av _src/make_og.py
img/app/    Skjermbilder fra iOS-appen
_src/       Byggeren. Publiseres ikke (`Disallow` i robots.txt)
```

**Rør ikke:** `CNAME` (domenet), `app-ads.txt` (må ligge i rota for AdMob),
og adressen `/support/` (registrert i App Store Connect).

---

## Slik henger tallene sammen

Ingen tall på nettsida er skrevet for hånd. Alle tabeller genereres fra
`_src/pacemath.py`, som speiler `assets/calc.js`:

- fart = 60 ÷ tempo i minutter
- sluttid = tempo × distanse, avrundet **halve oppover** som `Math.round` i JS
  (Pythons `round()` runder til partall og gir maraton 3:30:58 i stedet for 3:30:59)
- løpstidsanslag: Riegels formel, T₂ = T₁ × (D₂ ÷ D₁)^1,06

Et oppslag i en tabell og et drag på hjulet gir dermed alltid samme svar.

---

## SEO og AI

- Unik `title`, `description`, `canonical` og `og:image` per side
- `hreflang`-par begge veier, `x-default` → engelsk
- `schema.org`: Organization på alle sider, pluss WebApplication,
  SoftwareApplication, Article, BreadcrumbList og FAQPage der de hører hjemme
- `llms.txt` i rota: innholdsfortegnelse for AI-crawlere
- `robots.txt` slipper eksplisitt inn GPTBot, ClaudeBot, PerplexityBot,
  Google-Extended, Applebot-Extended med flere
- CSS og JS får `?v=<innholdssum>`, så en endring slår igjennom med én gang
  i stedet for etter GitHub Pages' ti minutter med caching

---

## App Store

Appen er `RunPace – Pace Calculator`, App-ID **6789667868**. I markup brukes
`https://apps.apple.com/app/id6789667868`, som sender brukeren til riktig land.

- `<meta name="apple-itunes-app">` gir Apples egen nedlastingsbanner i Safari på iPhone
- Klikk mot App Store logges som `appstore-click:<plassering>` i analytikken
- Android får «Legg til på hjemskjermen» i stedet, siden appen ikke finnes der ennå

---

## Personvern

Ingen informasjonskapsler og ingen tredjepartsskript. Besøk registreres med en
egen løsning på en server i Norge: tidspunkt, hashet IP (16 tegn), user-agent
og referrer. Sporingen kjører bare når vertsnavnet er `runpace.no`, så lokale
kopier og forhåndsvisninger registreres ikke.
