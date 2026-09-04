# -*- coding: utf-8 -*-
"""Lager delebildene (Open Graph, 1200x630) fra SVG.

    python3 _src/make_og.py

Krever rsvg-convert (brew install librsvg). Kjøres bare når teksten skal endres —
resultatet ligger committet i og/.
"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "og")

CARDS = {
    "default": ("Løpekalkulator", "Tempo, fart og mellomtider"),
    "home":    ("Løpekalkulator", "min/km ↔ km/t · sluttider · mellomtider"),
    "app":     ("RunPace til iPhone", "Gratis løpekalkulator i lomma"),
    "tabeller":("Tempotabeller", "Maraton · halvmaraton · 10 km · 5 km"),
    "guider":  ("Guider om løpetempo", "Kort, konkret og uten fyllstoff"),
}

FONT = "SF Pro Display, Helvetica Neue, Helvetica, Arial, sans-serif"

TPL = '''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="#000"/>
  <!-- svak gul glød oppe til høyre, så kortet ikke blir en flat sort flate -->
  <defs>
    <radialGradient id="glow" cx="0.82" cy="0.12" r="0.75">
      <stop offset="0" stop-color="#F2C800" stop-opacity="0.16"/>
      <stop offset="1" stop-color="#F2C800" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="ico" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#F5CE0A"/><stop offset="1" stop-color="#E5B400"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="630" fill="url(#glow)"/>

  <!-- Merket: samme løpebane som appikonet -->
  <g transform="translate(80,74) scale(0.203)">
    <rect width="512" height="512" rx="112" fill="url(#ico)"/>
    <rect x="71" y="154" width="368" height="205" rx="102" fill="none" stroke="#1A1A17" stroke-width="43"/>
    <rect x="132" y="209" width="248" height="97" rx="48" fill="none" stroke="#F7EFD8" stroke-width="33"/>
    <rect x="152" y="227" width="213" height="58" rx="29" fill="#E5B400"/>
  </g>
  <text x="196" y="128" font-family="{font}" font-size="42" font-weight="700" fill="#fff">
    <tspan fill="#F2C800">Run</tspan>Pace
  </text>

  <text x="80" y="330" font-family="{font}" font-size="82" font-weight="700" fill="#fff">{title}</text>
  <text x="80" y="400" font-family="{font}" font-size="38" font-weight="400" fill="#B8B8B8">{sub}</text>

  <rect x="80" y="470" width="120" height="4" rx="2" fill="#F2C800"/>
  <text x="80" y="546" font-family="{font}" font-size="32" font-weight="500" fill="#8A8A8A">runpace.no</text>
</svg>'''


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    for name, (title, sub) in CARDS.items():
        svg = TPL.format(font=FONT, title=esc(title), sub=esc(sub))
        tmp = os.path.join(OUT, name + ".svg")
        with open(tmp, "w") as f:
            f.write(svg)
        png = os.path.join(OUT, name + ".png")
        subprocess.check_call(["rsvg-convert", "-w", "1200", "-h", "630",
                               "-o", png, tmp])
        os.remove(tmp)
        print("  og/%s.png" % name)


if __name__ == "__main__":
    main()
