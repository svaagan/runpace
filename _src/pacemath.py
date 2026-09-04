# -*- coding: utf-8 -*-
import math
"""Tempo-regning for runpace.no.

Alle tabeller på nettsida genereres herfra, slik at de ikke kan komme i utakt
med kalkulatoren i index.html eller med iOS-appen. Avrundingen speiler
`fmtTime` i assets/calc.js: sekunder rundes til nærmeste hele sekund.
"""

# Samme liste som DISTANCES i assets/calc.js
DISTANCES = {
    "1k":       1.0,
    "mile":     1.60934,
    "3k":       3.0,
    "5k":       5.0,
    "10k":      10.0,
    "half":     21.0975,
    "marathon": 42.195,
}

NAMES = {
    "nb": {"1k": "1 km", "mile": "1 engelsk mil", "3k": "3 km", "5k": "5 km",
           "10k": "10 km", "half": "Halvmaraton", "marathon": "Maraton"},
    "en": {"1k": "1 km", "mile": "1 mile", "3k": "3 km", "5k": "5 km",
           "10k": "10 km", "half": "Half marathon", "marathon": "Marathon"},
}


def _round_half_up(x):
    """JS Math.round runder .5 oppover; Pythons round() runder til partall.

    Uten dette gir maraton på 5:00 min/km 3:30:58 her og 3:30:59 i appen.
    """
    return int(math.floor(x + 0.5))


def pace_to_kmh(pace_s):
    """Tempo i sekunder per km -> km/t."""
    return 3600.0 / pace_s


def kmh_to_pace(kmh):
    """km/t -> tempo i sekunder per km."""
    return 3600.0 / kmh


def finish_seconds(pace_s, km):
    """Sluttid i sekunder for et gitt tempo og en gitt distanse."""
    return _round_half_up(pace_s * km)


def fmt_pace(pace_s):
    """300 -> '5:00'. Tempo vises alltid som m:ss."""
    pace_s = _round_half_up(pace_s)
    return "%d:%02d" % (pace_s // 60, pace_s % 60)


def fmt_time(total_s):
    """Sluttid: 'm:ss' under en time, ellers 'h:mm:ss'."""
    total_s = _round_half_up(total_s)
    h, rest = divmod(total_s, 3600)
    m, s = divmod(rest, 60)
    return "%d:%02d:%02d" % (h, m, s) if h else "%d:%02d" % (m, s)


def fmt_kmh(kmh, lang="nb"):
    """12.0 -> '12,0' på norsk, '12.0' på engelsk."""
    txt = "%.1f" % kmh
    return txt.replace(".", ",") if lang == "nb" else txt


def riegel(t1_s, d1_km, d2_km, exponent=1.06):
    """Riegels formel: anslå tid på én distanse ut fra en kjent tid på en annen."""
    return t1_s * (d2_km / d1_km) ** exponent


def pace_range(start="3:00", end="8:00", step_s=5):
    """Tempoer fra start til end, som sekunder per km."""
    def parse(t):
        m, s = t.split(":")
        return int(m) * 60 + int(s)
    a, b = parse(start), parse(end)
    return list(range(a, b + 1, step_s))
