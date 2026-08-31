# RunPace

Løpekalkulator for mobil. Beregner tempo i min/km og km/h, estimerer løpstider for standarddistanser, og genererer mellomtidstabeller for et målsatt sluttid.

Tilgjengelig på **[runpace.no](https://runpace.no)**

---

## Hva appen gjør

### Kalkulator
To sammenkoblede scrollehjul viser min/km og km/h side om side. Justerer du det ene, oppdateres det andre automatisk. Under hjulene vises estimert løpstid for sju standarddistanser (1k, 1 mile, 3k, 5k, 10k, halvmaraton, maraton).

### Pacing
Velg en distanse (forhåndsinnstilt eller egendefinert i meter eller km) og et tidsmål. Appen beregner nødvendig tempo og viser en mellomtidstabell. Du velger intervall for mellomtidene (100 m, 200 m, 400 m, 1k, 2k, 5k eller 10k).

### Guider
Fire artikler om løpeteknikk og pacing:
- **Hva er min/km?** — forklarer tempoenheten og omregning til km/h
- **5k under 25 min** — pacing-guide med treningsopplegg
- **Maraton-tempo** — oversikt over tempoer og sluttider
- **Tempo vs. fart** — forskjellen på min/km og km/h, tredemølle-tabell

### Om oss / Personvern
Informasjonsside og GDPR-erklæring. Kontakt: kontakt@runpace.no

---

## Teknisk

- **Én fil:** Hele appen er `index.html` — ingen avhengigheter, ingen byggsteg, ingen backend
- **PWA-klar:** Kan installeres på hjemskjermen og åpnes i fullskjerm uten nettlesergrensesnitt
- **Ingen cookies:** Appen setter ingen informasjonskapsler
- **Språk:** Norsk (bokmål)
- **Design:** Mørkt tema med gul aksent (`#F2C800`), iOS-inspirerte scrollehjul

---

## Hosting


Publisert med **GitHub Pages** fra `main`-branchen i dette repoet, med eget domene via `CNAME`-fila og automatisk HTTPS.

For å oppdatere siden: rediger `index.html`, commit og push. GitHub bygger og publiserer automatisk, vanligvis i løpet av ett minutt.

---

## Analytikk

Egenutviklet, selvdriftet analytikkløsning. Ingen tredjepartstjenester, ingen cookies.

### Hva som samles inn per besøk
- Tidspunkt
- Anonymisert IP (SHA-256, kun 16 tegn lagres — kan ikke rekonstrueres)
- Nettleser/enhet (user-agent)
- Trafikkilde (referrer)

Data lagres på en privat server i Norge, deles ikke med tredjeparter og selges ikke.
Sporingen kjører kun når siden lastes fra `runpace.no` — lokale kopier og forhåndsvisninger registreres ikke.

---

## Filstruktur

```
runpace/
├── index.html         # Hele appen (kalkulator, pacing, guider, om oss, personvern)
├── support/
│   └── index.html     # Støtteside (Support URL for App Store)
├── robots.txt         # Instruksjoner til søkemotorer
├── sitemap.xml        # Sidekart for søkemotorer
├── CNAME              # Eget domene for GitHub Pages (runpace.no)
├── .gitignore
└── README.md          # Denne filen
```

---

## Git / versjonskontroll

```bash
# Oppdater og push endringer
git add index.html
git commit -m "Beskriv hva du endret"
git push
```

Push til `main` utløser en ny publisering til runpace.no automatisk.
