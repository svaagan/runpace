# -*- coding: utf-8 -*-
"""Felles ramme rundt hver side på runpace.no.

Topplinje, meny, brødsmuler, bunn og strukturerte data. Alt skrives som
ekte HTML inn i hver fil — ikke injisert med JavaScript — slik at
søkemotorer ser de interne lenkene i rå kildekode.
"""
import hashlib
import json
import os

SITE = "https://runpace.no"
APP_ID = "6789667868"
APP_URL = "https://apps.apple.com/app/id" + APP_ID
CONTACT = "kontakt@runpace.no"

# Ressursene merkes med innholdssummen sin. GitHub Pages setter max-age=600,
# så uten dette ser besøkende gammel CSS i inntil ti minutter etter en endring.
def _rev(path):
    full = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), path.lstrip("/"))
    try:
        with open(full, "rb") as f:
            return hashlib.sha1(f.read()).hexdigest()[:8]
    except IOError:
        return "0"


def asset(path):
    return "%s?v=%s" % (path, _rev(path))
AUTHOR = "Stian Gaare Vaagan"

# ── Meny ────────────────────────────────────────────────────────────
NAV = {
    "nb": [
        ("calc",   "Kalkulator",  "/"),
        ("splits", "Mellomtider", "/mellomtider/"),
        ("tables", "Tabeller",    "/tabeller/"),
        ("guides", "Guider",      "/guider/"),
        ("app",    "Appen",       "/app/"),
    ],
    "en": [
        ("calc",   "Calculator", "/en/"),
        ("splits", "Splits",     "/en/splits/"),
        ("tables", "Charts",     "/en/charts/"),
        ("app",    "iOS app",    "/en/app/"),
    ],
}

FOOTER = {
    "nb": [
        ("Verktøy", [("Løpekalkulator", "/"), ("Mellomtider", "/mellomtider/"),
                     ("RunPace til iPhone", "/app/")]),
        ("Tempotabeller", [("Maraton", "/tabeller/maraton/"),
                           ("Halvmaraton", "/tabeller/halvmaraton/"),
                           ("10 km", "/tabeller/10km/"), ("5 km", "/tabeller/5km/"),
                           ("min/km til km/t", "/tabeller/min-km-til-km-t/"),
                           ("Tredemølle", "/tabeller/tredemolle/")]),
        ("Guider", [("Hva er min/km?", "/guider/hva-er-min-km/"),
                    ("5 km under 25 minutter", "/guider/5km-under-25-minutter/"),
                    ("Maratontempo", "/guider/maratontempo/"),
                    ("Tempo eller fart?", "/guider/tempo-vs-fart/"),
                    ("Hva er en god 5 km-tid?", "/guider/god-tid-pa-5km/"),
                    ("Riegels formel", "/guider/riegel-formelen/"),
                    ("Negativ split", "/guider/negativ-split/")]),
        ("Om", [("Om RunPace", "/om/"), ("Vanlige spørsmål", "/faq/"),
                ("Personvern", "/personvern/"), ("Støtte", "/support/"),
                (CONTACT, "mailto:" + CONTACT)]),
    ],
    "en": [
        ("Tools", [("Pace calculator", "/en/"), ("Splits", "/en/splits/"),
                   ("RunPace for iPhone", "/en/app/")]),
        ("Pace charts", [("Marathon", "/en/charts/marathon/"),
                         ("Half marathon", "/en/charts/half-marathon/"),
                         ("10K", "/en/charts/10k/"), ("5K", "/en/charts/5k/"),
                         ("min/km to km/h", "/en/charts/min-km-to-km-h/"),
                         ("Treadmill", "/en/charts/treadmill/")]),
        ("About", [("About RunPace", "/en/about/"), ("Privacy", "/en/privacy/"),
                   ("Support", "/support/"), (CONTACT, "mailto:" + CONTACT)]),
    ],
}

STR = {
    "nb": {
        "skip": "Hopp til innhold", "menu": "Meny", "home": "Hjem",
        "get": "Få appen", "updated": "Sist oppdatert",
        "footer_note": "Løpekalkulator for tempo, fart og mellomtider. "
                       "Laget i Norge av %s." % AUTHOR,
        "badge": "/assets/appstore-no.svg", "badge_alt": "Last ned RunPace i App Store",
        "lang_other": ("English", "en"),
    },
    "en": {
        "skip": "Skip to content", "menu": "Menu", "home": "Home",
        "get": "Get the app", "updated": "Last updated",
        "footer_note": "Running pace calculator for pace, speed and splits. "
                       "Made in Norway by %s." % AUTHOR,
        "badge": "/assets/appstore-en.svg", "badge_alt": "Download RunPace on the App Store",
        "lang_other": ("Norsk", "nb"),
    },
}

MONTHS_NB = ["januar", "februar", "mars", "april", "mai", "juni", "juli",
             "august", "september", "oktober", "november", "desember"]


def pretty_date(iso, lang):
    y, m, d = (int(x) for x in iso.split("-"))
    if lang == "nb":
        return "%d. %s %d" % (d, MONTHS_NB[m - 1], y)
    return "%d %s %d" % (d, MONTHS_NB[m - 1].capitalize()[:3] if False else
                         ["January", "February", "March", "April", "May", "June", "July",
                          "August", "September", "October", "November", "December"][m - 1], y)


def head(page, alt_url=None):
    """<head> for én side: meta, hreflang, Open Graph og schema."""
    lang = page["lang"]
    s = STR[lang]
    url = SITE + page["url"]
    og = page.get("og", "/og/default.png")

    L = []
    L.append('<meta charset="utf-8">')
    L.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    L.append('<title>%s</title>' % esc(page["title"]))
    L.append('<meta name="description" content="%s">' % esc(page["desc"]))
    L.append('<link rel="canonical" href="%s">' % url)

    # Språkpar. x-default peker på engelsk — det er versjonen resten av
    # verden skal få når Google ikke vet bedre.
    if alt_url:
        nb_url = url if lang == "nb" else SITE + alt_url
        en_url = SITE + alt_url if lang == "nb" else url
        L.append('<link rel="alternate" hreflang="nb" href="%s">' % nb_url)
        L.append('<link rel="alternate" hreflang="en" href="%s">' % en_url)
        L.append('<link rel="alternate" hreflang="x-default" href="%s">' % en_url)

    L.append('<meta property="og:type" content="%s">' %
             ("article" if page["kind"] in ("guide", "table") else "website"))
    L.append('<meta property="og:site_name" content="RunPace">')
    L.append('<meta property="og:url" content="%s">' % url)
    L.append('<meta property="og:title" content="%s">' % esc(page.get("og_title", page["title"])))
    L.append('<meta property="og:description" content="%s">' % esc(page["desc"]))
    L.append('<meta property="og:image" content="%s%s">' % (SITE, og))
    L.append('<meta property="og:image:width" content="1200">')
    L.append('<meta property="og:image:height" content="630">')
    L.append('<meta property="og:locale" content="%s">' % ("nb_NO" if lang == "nb" else "en_US"))
    L.append('<meta name="twitter:card" content="summary_large_image">')
    L.append('<meta name="twitter:title" content="%s">' % esc(page.get("og_title", page["title"])))
    L.append('<meta name="twitter:description" content="%s">' % esc(page["desc"]))
    L.append('<meta name="twitter:image" content="%s%s">' % (SITE, og))

    L.append('<meta name="theme-color" content="#000000">')
    L.append('<meta name="apple-mobile-web-app-capable" content="yes">')
    L.append('<meta name="apple-mobile-web-app-status-bar-style" content="black">')
    L.append('<meta name="apple-mobile-web-app-title" content="RunPace">')
    L.append('<!-- Safari på iPhone viser Apples egen nedlastingsbanner av denne -->')
    L.append('<meta name="apple-itunes-app" content="app-id=%s">' % APP_ID)
    L.append('<link rel="manifest" href="%s">'
             % ("/manifest.json" if lang == "nb" else "/en/manifest.json"))
    L.append('<link rel="icon" href="/favicon.svg" type="image/svg+xml">')
    L.append('<link rel="icon" href="/favicon.ico" sizes="32x32">')
    L.append('<link rel="apple-touch-icon" href="/icons/icon-180.png">')
    L.append('<link rel="stylesheet" href="%s">' % asset("/assets/site.css"))
    if page.get("calc"):
        L.append('<link rel="stylesheet" href="%s">' % asset("/assets/calc.css"))
    L.append('<script type="application/ld+json">%s</script>' % schema(page))
    return "\n  ".join(L)


def esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def schema(page):
    """Strukturerte data. Dette er det Google og AI-assistenter leser først."""
    lang = page["lang"]
    url = SITE + page["url"]
    graph = []

    org = {"@type": "Organization", "@id": SITE + "/#org", "name": "RunPace",
           "url": SITE, "email": CONTACT,
           "founder": {"@type": "Person", "name": AUTHOR},
           "logo": {"@type": "ImageObject", "url": SITE + "/icons/icon-512.png"}}
    site = {"@type": "WebSite", "@id": SITE + "/#site", "name": "RunPace",
            "url": SITE, "publisher": {"@id": SITE + "/#org"},
            "inLanguage": "nb-NO" if lang == "nb" else "en"}

    # Organisasjonen refereres med @id fra alle sider, så noden må ligge på
    # alle sidene — ikke bare på forsida og appsida.
    if page["kind"] not in ("home", "app"):
        graph.append(org)

    if page["kind"] == "home":
        graph += [org, site, {
            "@type": "WebApplication", "@id": url + "#app",
            "name": "RunPace", "url": url,
            "description": page["desc"],
            "applicationCategory": "HealthApplication",
            "operatingSystem": "Web, iOS",
            "browserRequirements": "Krever JavaScript" if lang == "nb" else "Requires JavaScript",
            "isAccessibleForFree": True,
            "inLanguage": "nb-NO" if lang == "nb" else "en",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "NOK"},
            "publisher": {"@id": SITE + "/#org"},
        }]
    elif page["kind"] == "app":
        graph += [org, {
            "@type": "SoftwareApplication", "@id": url + "#ios",
            "name": "RunPace – Pace Calculator", "url": url,
            "installUrl": APP_URL, "downloadUrl": APP_URL,
            "description": page["desc"],
            "applicationCategory": "HealthApplication",
            "operatingSystem": "iOS 17.0 or later",
            "author": {"@type": "Person", "name": AUTHOR},
            "publisher": {"@id": SITE + "/#org"},
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "NOK",
                       "availability": "https://schema.org/InStock"},
        }]
    else:
        graph.append(site)
        if page["kind"] in ("guide", "table"):
            graph.append({
                "@type": "Article", "@id": url + "#article",
                "headline": page["h1"], "description": page["desc"],
                "url": url, "mainEntityOfPage": url,
                "datePublished": page.get("published", page["updated"]),
                "dateModified": page["updated"],
                "author": {"@type": "Person", "name": AUTHOR, "url": SITE + ("/om/" if lang == "nb" else "/en/about/")},
                "publisher": {"@id": SITE + "/#org"},
                "inLanguage": "nb-NO" if lang == "nb" else "en",
                "image": SITE + page.get("og", "/og/default.png"),
            })

    crumbs = page.get("crumbs") or []
    if crumbs:
        items = [{"@type": "ListItem", "position": 1,
                  "name": STR[lang]["home"], "item": SITE + ("/" if lang == "nb" else "/en/")}]
        for i, (name, href) in enumerate(crumbs, start=2):
            it = {"@type": "ListItem", "position": i, "name": name}
            if href:
                it["item"] = SITE + href
            items.append(it)
        graph.append({"@type": "BreadcrumbList", "@id": url + "#crumbs", "itemListElement": items})

    if page.get("faq"):
        graph.append({
            "@type": "FAQPage", "@id": url + "#faq",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}}
                           for q, a in page["faq"]],
        })

    return json.dumps({"@context": "https://schema.org", "@graph": graph},
                      ensure_ascii=False, indent=2)


def header(page):
    lang = page["lang"]
    s = STR[lang]
    home = "/" if lang == "nb" else "/en/"
    items = "".join(
        '\n        <a href="%s"%s>%s</a>' % (href, ' aria-current="page"' if key == page.get("nav") else "", label)
        for key, label, href in NAV[lang])
    drawer = drawer_html(page)
    return f'''  <a class="sr-only skip-link" href="#main">{s["skip"]}</a>

  <header class="site-header">
    <div class="wrap">
      <button class="hamburger" type="button" aria-label="{s["menu"]}" aria-expanded="false" aria-controls="navDrawer">
        <span></span><span></span><span></span>
      </button>
      <a class="brand" href="{home}"><b>Run</b>Pace</a>
      <nav class="nav-main" aria-label="{s["menu"]}">{items}
      </nav>
      <div class="header-spacer"></div>
      <a class="header-cta" href="{APP_URL}" data-store-link="header" target="_blank" rel="noopener">
        <svg width="14" height="14" viewBox="0 0 19 19" fill="none" aria-hidden="true">
          <path d="M9.5 2v9M5.5 7.5l4 4 4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M2.5 13v1.5A2.5 2.5 0 005 17h9a2.5 2.5 0 002.5-2.5V13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg><span>{s["get"]}</span>
      </a>
    </div>
  </header>

{drawer}'''


def drawer_html(page):
    lang = page["lang"]
    out = ['  <div class="nav-drawer" id="navDrawer">', '    <div class="wrap">']
    for title, links in FOOTER[lang]:
        out.append('      <div class="nav-group">')
        out.append('        <div class="nav-group-title">%s</div>' % title)
        for label, href in links:
            cur = ' aria-current="page"' if href == page["url"] else ""
            out.append('        <a href="%s"%s>%s</a>' % (href, cur, label))
        out.append('      </div>')
    out.append('    </div>')
    out.append('  </div>')
    return "\n".join(out)


def crumbs_html(page):
    if not page.get("crumbs"):
        return ""
    lang = page["lang"]
    home = "/" if lang == "nb" else "/en/"
    parts = ['<a href="%s">%s</a>' % (home, STR[lang]["home"])]
    for name, href in page["crumbs"]:
        parts.append('<span aria-hidden="true">/</span>')
        parts.append('<a href="%s">%s</a>' % (href, name) if href
                     else '<span aria-current="page">%s</span>' % name)
    return ('  <nav class="crumbs narrow" aria-label="%s">\n    %s\n  </nav>\n'
            % ("Brødsmuler" if lang == "nb" else "Breadcrumb", "\n    ".join(parts)))


def store_cta(page, title, text, placement):
    s = STR[page["lang"]]
    return f'''<aside class="store-cta" data-store-cta>
  <p class="store-cta-title">{title}</p>
  <p class="store-cta-text">{text}</p>
  <a class="store-badge" href="{APP_URL}" data-store-link="{placement}" target="_blank" rel="noopener">
    <img src="{s["badge"]}" alt="{s["badge_alt"]}" width="138" height="46" loading="lazy">
  </a>
</aside>'''


def install_modal(page):
    lang = page["lang"]
    if lang == "nb":
        title, close = "Legg RunPace på hjemskjermen", "Lukk"
        ios = [("Trykk <strong>Del</strong>-ikonet i Safari, nederst på skjermen. "
                "I Chrome: <strong>⋯</strong> nederst til høyre, så <strong>Del</strong>"),
               ("Bla ned og trykk <strong>Legg til på Hjem-skjerm</strong>"),
               ("Trykk <strong>Legg til</strong> — RunPace åpnes nå i full skjerm, uten nettleseren rundt")]
        andr = [("Trykk <strong>tre-prikk-menyen</strong> øverst til høyre i Chrome"),
                ("Velg <strong>Legg til på startsiden</strong>"),
                ("Trykk <strong>Installer</strong> — RunPace åpnes nå i full skjerm, uten nettleseren rundt")]
    else:
        title, close = "Add RunPace to your home screen", "Close"
        ios = [("In Safari, tap the <strong>Share</strong> icon in the bottom bar. "
                "In Chrome, tap <strong>⋯</strong> at the bottom right, then <strong>Share</strong>"),
               ("Scroll down and tap <strong>Add to Home Screen</strong>"),
               ("Tap <strong>Add</strong> — RunPace then opens full screen, without the browser interface")]
        andr = [("Tap the <strong>three-dot menu</strong> at the top right of Chrome"),
                ("Choose <strong>Add to Home screen</strong>"),
                ("Tap <strong>Install</strong> — RunPace then opens full screen, without the browser interface")]

    def steps(items, sid, hidden):
        rows = "".join(
            '\n        <div class="modal-step"><div class="step-num">%d</div>'
            '<p class="step-text">%s</p></div>' % (i, txt)
            for i, txt in enumerate(items, 1))
        return ('      <div class="modal-steps%s" id="%s">%s\n      </div>'
                % (" hidden" if hidden else "", sid, rows))

    return f'''  <div class="modal-backdrop hidden" id="installModal">
    <div class="modal-sheet">
      <p class="modal-title">{title}</p>
{steps(ios, "stepsIos", False)}
{steps(andr, "stepsAndroid", True)}
      <button class="modal-close" type="button">{close}</button>
    </div>
  </div>'''


def footer(page, alt_url=None):
    lang = page["lang"]
    s = STR[lang]
    cols = []
    for title, links in FOOTER[lang]:
        li = "".join('\n            <li><a href="%s">%s</a></li>' % (h, l) for l, h in links)
        cols.append('        <div class="footer-col">\n          <h3>%s</h3>\n'
                    '          <ul>%s\n          </ul>\n        </div>' % (title, li))
    other_label, other_lang = s["lang_other"]
    if alt_url:
        lang_html = ('<span class="lang-switch"><a aria-current="true" href="%s">%s</a>'
                     '<span aria-hidden="true">·</span><a href="%s" hreflang="%s">%s</a></span>'
                     % (page["url"], "Norsk" if lang == "nb" else "English",
                        alt_url, other_lang, other_label))
    else:
        lang_html = ('<span class="lang-switch"><a href="%s" hreflang="%s">%s</a></span>'
                     % ("/en/" if lang == "nb" else "/", other_lang, other_label))

    return f'''  <footer class="site-footer">
    <div class="wrap">
      <div class="footer-cols">
{chr(10).join(cols)}
      </div>
      <div class="footer-bottom">
        <span>{s["footer_note"]}</span>
        {lang_html}
      </div>
    </div>
  </footer>'''
