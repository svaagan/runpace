# -*- coding: utf-8 -*-
"""Kontrollerer det ferdig bygde nettstedet.

    python3 _src/check.py

Sjekker interne lenker, hreflang-par, schema-gyldighet, at hver side har
nøyaktig én h1, og at ingen ressurs mangler.
"""
import io, json, os, re, sys, html.parser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://runpace.no"
problems = []
pages = []

SKIP_DIRS = {".git", "_src", "node_modules"}

for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for fn in filenames:
        if fn.endswith(".html"):
            pages.append(os.path.join(dirpath, fn))
pages.sort()


def url_of(path):
    rel = os.path.relpath(path, ROOT)
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


def exists(url):
    """Svarer en lokal URL med en fil?"""
    u = url.split("#")[0].split("?")[0]
    if not u.startswith("/"):
        return True
    p = os.path.join(ROOT, u.lstrip("/"))
    if u.endswith("/") or u == "/":
        return os.path.isfile(os.path.join(p, "index.html"))
    return os.path.isfile(p) or os.path.isfile(os.path.join(p, "index.html"))


class Nest(html.parser.HTMLParser):
    VOID = {"meta", "link", "br", "img", "hr", "input", "source", "path", "rect",
            "stop", "circle", "area", "col", "embed", "param", "track", "wbr", "use"}

    def __init__(self):
        super().__init__()
        self.stack, self.errors = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if not self.stack:
            self.errors.append("ekstra </%s>" % tag)
        elif self.stack[-1] != tag:
            self.errors.append("</%s> lukker <%s>" % (tag, self.stack[-1]))
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass
        else:
            self.stack.pop()


alts = {}
for path in pages:
    url = url_of(path)
    s = io.open(path, encoding="utf-8").read()
    tag = lambda p: (re.search(p, s) or [None, None])[1] if re.search(p, s) else None

    # 1) Én h1
    n_h1 = len(re.findall(r"<h1[ >]", s))
    if n_h1 != 1:
        problems.append("%s: %d <h1> (skal være 1)" % (url, n_h1))

    # 2) Tittel og beskrivelse
    if not re.search(r"<title>.+?</title>", s, re.S):
        problems.append("%s: mangler <title>" % url)
    if not re.search(r'name="description" content=".{40,}?"', s):
        problems.append("%s: mangler eller for kort description" % url)

    # 3) Canonical
    can = re.search(r'rel="canonical" href="([^"]+)"', s)
    if url != "/404.html":
        if not can:
            problems.append("%s: mangler canonical" % url)
        elif can.group(1) != SITE + url:
            problems.append("%s: canonical peker på %s" % (url, can.group(1)))

    # 4) Interne lenker og ressurser
    for m in re.finditer(r'(?:href|src)="(/[^"]*)"', s):
        target = m.group(1)
        if not exists(target):
            problems.append("%s: død lenke -> %s" % (url, target))

    # 5) hreflang
    for m in re.finditer(r'rel="alternate" hreflang="(nb|en)" href="([^"]+)"', s):
        alts.setdefault(url, {})[m.group(1)] = m.group(2)

    # 6) Schema
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try:
            json.loads(m.group(1))
        except ValueError as e:
            problems.append("%s: ugyldig JSON-LD (%s)" % (url, e))

    # 7) HTML-nøsting
    n = Nest()
    n.feed(s)
    if n.errors:
        problems.append("%s: nøstingsfeil %s" % (url, n.errors[:3]))
    if n.stack:
        problems.append("%s: ulukkede tagger %s" % (url, n.stack[:3]))

    # 8) Plassholdere som ikke ble erstattet
    left = re.findall(r"\{\{[^}]+\}\}", s)
    if left:
        problems.append("%s: uerstattet plassholder %s" % (url, left[:2]))

# 9) hreflang skal peke begge veier
for url, pair in alts.items():
    for lang, target in pair.items():
        t = target.replace(SITE, "")
        back = alts.get(t)
        if back is None:
            problems.append("%s: hreflang %s -> %s, men den sida har ingen alternativer" % (url, lang, t))
        elif SITE + url not in back.values():
            problems.append("%s: hreflang %s -> %s peker ikke tilbake" % (url, lang, t))

print("Kontrollerte %d sider." % len(pages))
if problems:
    print("\n%d problem:" % len(problems))
    for p in problems:
        print("  ✗ " + p)
    sys.exit(1)
print("Ingen problemer funnet.")
