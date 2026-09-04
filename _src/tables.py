# -*- coding: utf-8 -*-
"""Tabellene på runpace.no.

Alt regnes ut fra pacemath, som igjen speiler kalkulatoren i assets/calc.js.
Ingen tall skrives for hånd — da kan de ikke komme i utakt med appen.
"""
import pacemath as P

TXT = {
    "nb": {"pace": "Tempo", "speed": "Fart", "time": "Sluttid", "dist": "Distanse",
           "goal": "Måltid", "need": "Nødvendig tempo", "km": "km/t",
           "level": "Nivå", "split": "Halvveis", "incline": "Stigning",
           "screen": "På skjermen", "real": "Tilsvarer ute"},
    "en": {"pace": "Pace", "speed": "Speed", "time": "Finish time", "dist": "Distance",
           "goal": "Goal time", "need": "Required pace", "km": "km/h",
           "level": "Level", "split": "Halfway", "incline": "Incline",
           "screen": "On the display", "real": "Equivalent outdoors"},
}


def _table(headers, rows, caption=None, classes=""):
    h = "".join("<th%s>%s</th>" % (' class="num"' if c else "", t) for t, c in headers)
    body = []
    for r in rows:
        tds = "".join('<td%s>%s</td>' % (cls and ' class="%s"' % cls or "", val)
                      for val, cls in r)
        body.append("        <tr>%s</tr>" % tds)
    cap = "\n      <caption>%s</caption>" % caption if caption else ""
    return ('<div class="table-scroll">\n    <table%s>%s\n      <thead><tr>%s</tr></thead>\n'
            '      <tbody>\n%s\n      </tbody>\n    </table>\n  </div>'
            % (' class="%s"' % classes if classes else "", cap, h, "\n".join(body)))


def pace_to_time(dist_key, lang, start="3:00", end="7:30", step=5):
    """Tempo -> sluttid for én distanse. Svarer på «hva blir tiden på X min/km»."""
    t = TXT[lang]
    km = P.DISTANCES[dist_key]
    rows = []
    for p in P.pace_range(start, end, step):
        rows.append([
            (P.fmt_pace(p) + " min/km", ""),
            (P.fmt_kmh(P.pace_to_kmh(p), lang), "num"),
            (P.fmt_time(P.finish_seconds(p, km)), "num hi"),
        ])
    return _table([(t["pace"], False), (t["km"], True), (t["time"], True)], rows)


def time_to_pace(dist_key, lang, goals):
    """Måltid -> nødvendig tempo. Svarer på «hvilket tempo for 4 timer».

    goals er en liste med sluttider i sekunder.
    """
    t = TXT[lang]
    km = P.DISTANCES[dist_key]
    rows = []
    for g in goals:
        pace = g / km
        rows.append([
            (P.fmt_time(g), ""),
            (P.fmt_pace(pace) + " min/km", "num hi"),
            (P.fmt_kmh(P.pace_to_kmh(pace), lang), "num"),
            (P.fmt_time(g / 2.0), "num"),
        ])
    return _table([(t["goal"], False), (t["need"], True), (t["km"], True),
                   (t["split"], True)], rows)


def conversion(lang, start="3:00", end="8:00", step=5):
    """min/km <-> km/t, med sluttid på 5 km og 10 km som kontekst."""
    t = TXT[lang]
    rows = []
    for p in P.pace_range(start, end, step):
        rows.append([
            (P.fmt_pace(p) + " min/km", ""),
            (P.fmt_kmh(P.pace_to_kmh(p), lang), "num hi"),
            (P.fmt_time(P.finish_seconds(p, 5)), "num"),
            (P.fmt_time(P.finish_seconds(p, 10)), "num"),
        ])
    return _table([(t["pace"], False), (t["km"], True), ("5 km", True), ("10 km", True)], rows)


def treadmill(lang):
    """km/t -> min/km. Tredemøller er merket i km/t, løpere tenker i min/km."""
    t = TXT[lang]
    rows = []
    v = 6.0
    while v <= 20.001:
        pace = P.kmh_to_pace(v)
        rows.append([
            (P.fmt_kmh(v, lang) + " " + t["km"], ""),
            (P.fmt_pace(pace) + " min/km", "num hi"),
            (P.fmt_time(P.finish_seconds(pace, 5)), "num"),
            (P.fmt_time(P.finish_seconds(pace, P.DISTANCES["half"])), "num"),
        ])
        v += 0.5
    return _table([(t["speed"], False), (t["pace"], True), ("5 km", True),
                   ("21,1 km" if lang == "nb" else "21.1 km", True)], rows)


def all_distances(lang, start="3:30", end="7:00", step=15):
    """Ett tempo, alle distansene. Den kompakte oversikten på forsida."""
    t = TXT[lang]
    keys = ["5k", "10k", "half", "marathon"]
    heads = [(t["pace"], False), (t["km"], True)] + [(P.NAMES[lang][k], True) for k in keys]
    rows = []
    for p in P.pace_range(start, end, step):
        r = [(P.fmt_pace(p) + " min/km", ""), (P.fmt_kmh(P.pace_to_kmh(p), lang), "num")]
        r += [(P.fmt_time(P.finish_seconds(p, P.DISTANCES[k])), "num") for k in keys]
        rows.append(r)
    return _table(heads, rows)


def riegel_examples(lang):
    """Riegel: kjent tid på én distanse -> anslag på de andre."""
    t = TXT[lang]
    seeds = [("5k", 20 * 60), ("5k", 25 * 60), ("5k", 30 * 60),
             ("10k", 45 * 60), ("10k", 55 * 60), ("half", 105 * 60), ("half", 120 * 60)]
    targets = ["5k", "10k", "half", "marathon"]
    heads = [(t["dist"], False), (t["time"], True)] + \
            [(P.NAMES[lang][k], True) for k in targets]
    rows = []
    for key, secs in seeds:
        r = [(P.NAMES[lang][key], ""), (P.fmt_time(secs), "num")]
        for tgt in targets:
            if tgt == key:
                r.append(("—", "num"))
            else:
                r.append((P.fmt_time(P.riegel(secs, P.DISTANCES[key], P.DISTANCES[tgt])), "num hi"))
        rows.append(r)
    return _table(heads, rows)


def negative_split(lang, dist_key, goal_s, back_s=10):
    """Mellomtidsplan med negativ split: start rolig, avslutt raskt."""
    t = TXT[lang]
    km = P.DISTANCES[dist_key]
    avg = goal_s / km
    first, second = avg + back_s, avg - back_s
    rows = []
    marks = [(1, "1 km"), (int(km // 2), None), (int(km), None)]
    step = 5 if km > 20 else 1
    d = step
    elapsed = 0.0
    prev = 0.0
    while d <= km + 0.001:
        seg = min(d, km) - prev
        pace = first if prev < km / 2 else second
        elapsed += seg * pace
        rows.append([
            ("%g km" % min(d, km), ""),
            (P.fmt_pace(pace) + " min/km", "num"),
            (P.fmt_time(elapsed), "num hi"),
        ])
        prev = min(d, km)
        d += step
    if prev < km:
        elapsed += (km - prev) * second
        rows.append([("%.3f km" % km if km % 1 else "%g km" % km, ""),
                     (P.fmt_pace(second) + " min/km", "num"),
                     (P.fmt_time(elapsed), "num hi")])
    return _table([(t["dist"], False), (t["pace"], True), (t["time"], True)], rows)


# ── Måltider som brukes i time_to_pace ─────────────────────────────
def goals(dist_key):
    m = lambda x: int(x * 60)
    if dist_key == "marathon":
        return [m(x) for x in range(150, 361, 10)]          # 2:30 – 6:00, hvert 10. min
    if dist_key == "half":
        return [m(x) for x in range(75, 181, 5)]            # 1:15 – 3:00, hvert 5. min
    if dist_key == "10k":
        return [m(x) for x in range(32, 91, 2)]             # 32 – 90 min
    if dist_key == "5k":
        return [m(x) for x in range(15, 46)]                # 15 – 45 min
    return []
