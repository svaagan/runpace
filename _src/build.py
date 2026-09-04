# -*- coding: utf-8 -*-
"""Bygger runpace.no.

Leser sideregisteret under, henter brødteksten fra _src/body/<lang>/<navn>.html
og skriver ferdige, statiske HTML-filer. GitHub Pages serverer rå filer —
det finnes ikke noe byggsteg ved publisering, og en feil her kan derfor
aldri ta ned nettsida.

    python3 _src/build.py

Rediger ALDRI de genererte HTML-filene direkte; endringene blir overskrevet.
Rediger brødteksten i _src/body/ eller rammeverket i _src/chrome.py.
"""
import io, os, re, sys, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chrome as C
import tables as T
import pacemath as P

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "_src")
TODAY = "2026-09-04"

# ── Sideregister ────────────────────────────────────────────────────
# url, kind, nav, tittel, beskrivelse, h1, og fila i _src/body/<lang>/
def P_(url, kind, nav, title, desc, h1, body, lang="nb", alt=None, crumbs=None,
       calc=False, og=None, faq=None, updated=TODAY, hero=None):
    return dict(url=url, kind=kind, nav=nav, title=title, desc=desc, h1=h1,
                body=body, lang=lang, alt=alt, crumbs=crumbs or [], calc=calc,
                og=og or "/og/default.png", faq=faq, updated=updated, hero=hero)

TAB_NB = ("Tabeller", "/tabeller/")
GUI_NB = ("Guider", "/guider/")
TAB_EN = ("Charts", "/en/charts/")

PAGES = [
 # ── Norsk ──────────────────────────────────────────────────────────
 P_("/", "home", "calc",
    "Løpekalkulator – regn ut tempo i min/km og km/t | RunPace",
    "Gratis løpekalkulator. Regn om mellom min/km og km/t, se sluttider for 5 km, "
    "10 km, halvmaraton og maraton, og lag mellomtidstabell for måltiden din.",
    "Løpekalkulator", "index", alt="/en/", calc=True, og="/og/home.png",
    faq=[("Hvordan regner jeg om min/km til km/t?",
          "Del 60 på tempoet i minutter. 5:00 min/km blir 60 ÷ 5 = 12 km/t. "
          "Løpekalkulatoren på runpace.no gjør omregningen mens du drar på hjulet."),
         ("Hva er et normalt løpetempo?",
          "For de fleste mosjonister ligger et rolig tempo på 6:00–7:00 min/km "
          "(8,6–10 km/t). Trente mosjonister holder 5:00–5:30 min/km på en rolig tur."),
         ("Hvilket tempo må jeg holde for å løpe maraton på 4 timer?",
          "5:41 min/km, altså 10,5 km/t, hele veien i 42,195 km. Halvveis skal klokka "
          "vise 2:00:00."),
         ("Er løpekalkulatoren gratis?",
          "Ja. Kalkulatoren på runpace.no er gratis, krever ingen innlogging og setter "
          "ingen informasjonskapsler.")]),

 P_("/mellomtider/", "tool", "splits",
    "Mellomtider – lag en tempoplan for måltiden din | RunPace",
    "Sett en distanse og en måltid, så får du tempoet du må holde og en "
    "mellomtidstabell med klokkeslett for hver kilometer.",
    "Mellomtider", "mellomtider", alt="/en/splits/", calc=True,
    crumbs=[("Mellomtider", None)]),

 P_("/app/", "app", "app",
    "RunPace til iPhone – løpekalkulator i lomma | RunPace",
    "RunPace er en gratis løpekalkulator for iPhone. Tempo, fart, løpstider og "
    "mellomtider — uten innlogging, og den virker uten nett.",
    "RunPace til iPhone", "app", alt="/en/app/", og="/og/app.png",
    crumbs=[("Appen", None)]),

 P_("/tabeller/", "hub", "tables",
    "Tempotabeller for løping – maraton, halvmaraton, 10 km og 5 km | RunPace",
    "Ferdige tempotabeller: hvilket tempo som gir hvilken sluttid, og hvilket tempo "
    "måltiden din krever. For maraton, halvmaraton, 10 km, 5 km og tredemølle.",
    "Tempotabeller", "tabeller", alt="/en/charts/", crumbs=[("Tabeller", None)]),

 P_("/tabeller/maraton/", "table", "tables",
    "Maratontempo-tabell – tempo, fart og sluttid for 42,195 km | RunPace",
    "Full maratontabell: hvilken sluttid hvert tempo gir, og hvilket tempo du må "
    "holde for 3, 3:30, 4, 4:30 eller 5 timer. Med halvveismerke.",
    "Maratontempo: tabell over tempo og sluttid", "tab-maraton",
    alt="/en/charts/marathon/", crumbs=[TAB_NB, ("Maraton", None)],
    faq=[("Hvilket tempo må jeg holde for maraton på 4 timer?",
          "5:41 min/km, som er 10,5 km/t. Halvveis, etter 21,1 km, skal klokka vise 2:00:00."),
         ("Hvilket tempo gir maraton på 3:30?",
          "4:59 min/km, altså 12,1 km/t. Halvveis skal klokka vise 1:45:00."),
         ("Hvor fort er maraton på 5:00 min/km?",
          "5:00 min/km i 42,195 km gir 3:30:59.")]),

 P_("/tabeller/halvmaraton/", "table", "tables",
    "Halvmaraton-tempotabell – tempo, fart og sluttid for 21,1 km | RunPace",
    "Tempotabell for halvmaraton: sluttid for hvert tempo, og nødvendig tempo for "
    "1:30, 1:45, 2:00 og 2:30. Med mellomtid halvveis.",
    "Halvmaraton: tabell over tempo og sluttid", "tab-halvmaraton",
    alt="/en/charts/half-marathon/", crumbs=[TAB_NB, ("Halvmaraton", None)],
    faq=[("Hvilket tempo må jeg holde for halvmaraton på 2 timer?",
          "5:41 min/km, som er 10,5 km/t, gjennom hele 21,0975 km."),
         ("Hva kreves for halvmaraton under 1:30?",
          "4:16 min/km, altså 14,1 km/t.")]),

 P_("/tabeller/10km/", "table", "tables",
    "10 km-tempotabell – tempo, fart og sluttid | RunPace",
    "Tempotabell for 10 km: hvilken sluttid hvert tempo gir, og hvilket tempo du "
    "trenger for 40, 45, 50 eller 60 minutter.",
    "10 km: tabell over tempo og sluttid", "tab-10km",
    alt="/en/charts/10k/", crumbs=[TAB_NB, ("10 km", None)],
    faq=[("Hvilket tempo gir 10 km på 50 minutter?", "5:00 min/km, altså 12,0 km/t."),
         ("Hva må til for 10 km under 45 minutter?", "4:30 min/km, som er 13,3 km/t.")]),

 P_("/tabeller/5km/", "table", "tables",
    "5 km-tempotabell – tempo, fart og sluttid | RunPace",
    "Tempotabell for 5 km: sluttid for hvert tempo fra 3:00 til 7:30 min/km, og "
    "nødvendig tempo for 20, 22, 25 eller 30 minutter.",
    "5 km: tabell over tempo og sluttid", "tab-5km",
    alt="/en/charts/5k/", crumbs=[TAB_NB, ("5 km", None)],
    faq=[("Hvilket tempo gir 5 km på 25 minutter?", "5:00 min/km, altså 12,0 km/t."),
         ("Hva må til for 5 km under 20 minutter?", "4:00 min/km, som er 15,0 km/t.")]),

 P_("/tabeller/min-km-til-km-t/", "table", "tables",
    "min/km til km/t – omregningstabell for løpetempo | RunPace",
    "Full omregningstabell mellom min/km og km/t, fra 3:00 til 8:00 min/km. "
    "Med formelen, og sluttider på 5 km og 10 km for hvert tempo.",
    "min/km til km/t: omregningstabell", "tab-omregning",
    alt="/en/charts/min-km-to-km-h/", crumbs=[TAB_NB, ("min/km til km/t", None)],
    faq=[("Hvordan regner jeg min/km om til km/t?",
          "Del 60 på tempoet i minutter. 5:00 min/km blir 60 ÷ 5 = 12 km/t. "
          "Sekunder må gjøres om til desimaler først: 5:30 er 5,5 minutter, og 60 ÷ 5,5 = 10,9 km/t."),
         ("Hvor mange km/t er 5:30 min/km?", "10,9 km/t."),
         ("Hvor mange min/km er 12 km/t?", "5:00 min/km.")]),

 P_("/tabeller/tredemolle/", "table", "tables",
    "Tredemølle: km/t til min/km – omregningstabell | RunPace",
    "Tredemøllen viser km/t, men du tenker i min/km. Full tabell fra 6 til 20 km/t, "
    "med sluttider og hva stigning gjør med tempoet.",
    "Tredemølle: km/t til min/km", "tab-tredemolle",
    alt="/en/charts/treadmill/", crumbs=[TAB_NB, ("Tredemølle", None)],
    faq=[("Hvor fort er 12 km/t på tredemølle?", "12 km/t er 5:00 min/km."),
         ("Hvilken stigning bør jeg bruke på tredemølle?",
          "1 % er den vanligste anbefalingen. Uten motvind og med et belte som drar "
          "føttene bakover, blir samme fart litt lettere inne enn ute.")]),

 P_("/guider/", "hub", "guides",
    "Guider om løpetempo og pacing | RunPace",
    "Korte, konkrete guider om tempo: hva min/km betyr, hvordan du legger opp "
    "farten i et løp, og hva som er realistisk å sikte mot.",
    "Guider", "guider", crumbs=[("Guider", None)]),

 P_("/guider/hva-er-min-km/", "guide", "guides",
    "Hva betyr min/km? Slik leser du løpetempo | RunPace",
    "min/km er minutter per kilometer — tiden du bruker på én kilometer. "
    "Lavere tall betyr raskere løping. Her er hva tallene betyr i praksis.",
    "Hva betyr min/km?", "hva-er-min-km", crumbs=[GUI_NB, ("Hva er min/km?", None)],
    faq=[("Hva betyr min/km?",
          "min/km er minutter per kilometer — hvor lang tid du bruker på én kilometer. "
          "5:00 min/km betyr fem minutter per kilometer."),
         ("Er lavt eller høyt min/km best?",
          "Lavt. 4:00 min/km er raskere enn 6:00 min/km, fordi du bruker kortere tid "
          "på hver kilometer.")]),

 P_("/guider/5km-under-25-minutter/", "guide", "guides",
    "5 km under 25 minutter: tempo og treningsopplegg | RunPace",
    "5 km på 25 minutter krever 5:00 min/km hele veien. Her er hva det innebærer, "
    "hvordan du legger opp løpet, og et treningsopplegg på åtte uker.",
    "5 km under 25 minutter", "5km-under-25",
    crumbs=[GUI_NB, ("5 km under 25 minutter", None)],
    faq=[("Hvilket tempo trengs for 5 km på 25 minutter?",
          "5:00 min/km, altså 12,0 km/t, jevnt gjennom hele løpet."),
         ("Er 25 minutter på 5 km bra?",
          "Det er en solid mosjonisttid. De fleste som løper jevnt et par ganger i uka "
          "kan nå den på noen måneder.")]),

 P_("/guider/maratontempo/", "guide", "guides",
    "Maratontempo: hva er realistisk for deg? | RunPace",
    "Ganger du halvmaratontiden din med 2,1, får du et realistisk maratonmål. "
    "Her er hvorfor, og hvordan du unngår å gå på veggen etter 30 km.",
    "Maratontempo: hva er realistisk?", "maratontempo",
    crumbs=[GUI_NB, ("Maratontempo", None)],
    faq=[("Hvordan anslår jeg maratontiden min?",
          "Gang halvmaratontiden med 2,1. Løper du halvmaraton på 2:00, er 4:12 et "
          "realistisk maratonmål."),
         ("Hvorfor går folk på veggen?",
          "Nesten alltid fordi de startet for fort. Glykogenlagrene tømmes, og de "
          "sekundene du sparte de første ti kilometerne, taper du mangedobbelt igjen "
          "på de siste ti.")]),

 P_("/guider/tempo-vs-fart/", "guide", "guides",
    "Tempo eller fart? Forskjellen på min/km og km/t | RunPace",
    "min/km og km/t beskriver det samme, sett fra hver sin kant. Her er formelen, "
    "og hvorfor løpere bruker det ene og tredemøller det andre.",
    "Tempo eller fart: min/km eller km/t?", "tempo-vs-fart",
    crumbs=[GUI_NB, ("Tempo eller fart?", None)]),

 P_("/guider/god-tid-pa-5km/", "guide", "guides",
    "Hva er en god tid på 5 km? | RunPace",
    "Det finnes ikke ett svar, men det finnes noen holdepunkter. Her er hva "
    "ulike 5 km-tider tilsvarer i tempo, og hva de krever av trening.",
    "Hva er en god tid på 5 km?", "god-tid-5km",
    crumbs=[GUI_NB, ("Hva er en god 5 km-tid?", None)],
    faq=[("Hva er en god tid på 5 km?",
          "For en som har løpt jevnt en stund, er 25–30 minutter en god tid. Under 25 "
          "minutter regnes som godt trent, og under 20 minutter er konkurransenivå for "
          "mosjonister. Men den beste målestokken er din egen forrige tid."),
         ("Er 30 minutter på 5 km bra?",
          "Ja. 30 minutter er 6:00 min/km, et jevnt og kontrollert mosjonstempo, og en "
          "helt vanlig tid for noen som løper regelmessig.")]),

 P_("/guider/riegel-formelen/", "guide", "guides",
    "Riegels formel: anslå løpstiden din på en ny distanse | RunPace",
    "Har du en tid på 5 km, kan du anslå hva du klarer på 10 km, halvmaraton og "
    "maraton. Riegels formel forklart, med ferdig tabell.",
    "Riegels formel: fra én distanse til en annen", "riegel",
    crumbs=[GUI_NB, ("Riegels formel", None)],
    faq=[("Hva er Riegels formel?",
          "T₂ = T₁ × (D₂ ÷ D₁)^1,06. Den anslår tiden din på en ny distanse ut fra en "
          "tid du allerede har løpt. Eksponenten 1,06 er det som gjør at tempoet faller "
          "litt for hver kilometer distansen øker."),
         ("Hvor treffsikker er Riegels formel?",
          "Godt innenfor en dobling eller halvering av distansen. Fra 5 km til maraton "
          "er spranget for stort, og formelen gir gjerne et for optimistisk anslag hvis "
          "du ikke har lang tur i beina.")]),

 P_("/guider/negativ-split/", "guide", "guides",
    "Negativ split: løp andre halvdel raskere | RunPace",
    "Nesten alle personlige rekorder settes med negativ split — andre halvdel "
    "raskere enn første. Her er hvorfor det virker, og hvordan du planlegger det.",
    "Negativ split: slik legger du opp løpet", "negativ-split",
    crumbs=[GUI_NB, ("Negativ split", None)],
    faq=[("Hva er negativ split?",
          "Å løpe andre halvdel av løpet raskere enn første. Motsatt av positiv split, "
          "der du starter hardt og bremser."),
         ("Hvor mye saktere bør jeg starte?",
          "10–15 sekunder per kilometer under måltempoet de første kilometerne holder "
          "for de fleste. På maraton er 10 sekunder nok.")]),

 P_("/om/", "info", None, "Om RunPace",
    "RunPace er en løpekalkulator laget i Norge. Ingen innlogging, ingen "
    "informasjonskapsler, og all utregning skjer i nettleseren din.",
    "Om RunPace", "om", alt="/en/about/", crumbs=[("Om RunPace", None)]),

 P_("/faq/", "info", None, "Vanlige spørsmål om løpetempo | RunPace",
    "Svar på de vanligste spørsmålene om tempo, fart, mellomtider og RunPace-appen.",
    "Vanlige spørsmål", "faq", crumbs=[("Vanlige spørsmål", None)],
    faq=[("Hvordan regner jeg min/km om til km/t?",
          "Del 60 på tempoet i minutter. 5:00 min/km blir 60 ÷ 5 = 12,0 km/t. Har tempoet "
          "sekunder, gjør du dem om til desimaler først: 5:30 er 5,5 minutter, og "
          "60 ÷ 5,5 = 10,9 km/t."),
         ("Er lavt eller høyt min/km best?",
          "Lavt. 4:00 min/km er raskere enn 6:00 min/km, fordi du bruker kortere tid på "
          "hver kilometer."),
         ("Hva er et normalt løpetempo?",
          "For de fleste mosjonister ligger et rolig tempo på 6:00–7:00 min/km, altså "
          "8,6–10 km/t. Trente mosjonister holder gjerne 5:00–5:30 min/km på en rolig tur."),
         ("Hvilket tempo må jeg holde for maraton på 4 timer?",
          "5:41 min/km, altså 10,5 km/t, hele veien i 42,195 km. Halvveis skal klokka "
          "vise 2:00:00."),
         ("Hva kreves for halvmaraton på 2 timer?",
          "5:41 min/km — samme tempo som en maraton på 4 timer, bare halve distansen."),
         ("Kan jeg legge RunPace på hjemskjermen?",
          "Ja. Sida virker som en app når den er installert — full skjerm, egen ikon og "
          "uten nettleseren rundt."),
         ("Hva koster RunPace-appen?",
          "Ingenting. Den er gratis med et lite reklamebanner nederst, og ett engangskjøp "
          "fjerner banneret for godt. Ingen funksjoner er låst bak betaling."),
         ("Finnes RunPace på Android?",
          "Ikke ennå. På Android kan du legge nettsida på hjemskjermen, så oppfører den "
          "seg som en app med egen ikon og full skjerm.")]),

 P_("/personvern/", "info", None, "Personvernerklæring | RunPace",
    "Hva RunPace samler inn, hva vi ikke samler inn, og hvordan reklamen i "
    "iOS-appen fungerer.",
    "Personvernerklæring", "personvern", alt="/en/privacy/",
    crumbs=[("Personvern", None)]),

 # ── Engelsk ────────────────────────────────────────────────────────
 P_("/en/", "home", "calc",
    "Running Pace Calculator – min/km, km/h and race times | RunPace",
    "Free running pace calculator. Convert between min/km and km/h, see finish times "
    "for 5K, 10K, half marathon and marathon, and build a split table for your goal.",
    "Running Pace Calculator", "index", lang="en", alt="/", calc=True, og="/og/home.png",
    faq=[("How do I convert min/km to km/h?",
          "Divide 60 by your pace in minutes. 5:00 min/km gives 60 ÷ 5 = 12 km/h."),
         ("What pace do I need for a 4 hour marathon?",
          "5:41 min/km, or 10.5 km/h, for the full 42.195 km. At halfway the clock "
          "should read 2:00:00."),
         ("Is the pace calculator free?",
          "Yes. It is free, needs no sign-in and sets no cookies.")]),

 P_("/en/splits/", "tool", "splits",
    "Split Calculator – build a pacing plan for your goal time | RunPace",
    "Set a distance and a goal time, and get the pace you need plus a split table "
    "showing what the clock should read at every kilometre.",
    "Split Calculator", "mellomtider", lang="en", alt="/mellomtider/", calc=True,
    crumbs=[("Splits", None)]),

 P_("/en/app/", "app", "app",
    "RunPace for iPhone – a pace calculator in your pocket | RunPace",
    "RunPace is a free running pace calculator for iPhone. Pace, speed, race times "
    "and splits — no sign-in, and it works offline.",
    "RunPace for iPhone", "app", lang="en", alt="/app/", og="/og/app.png",
    crumbs=[("iOS app", None)]),

 P_("/en/charts/", "hub", "tables",
    "Running pace charts – marathon, half marathon, 10K and 5K | RunPace",
    "Ready-made pace charts: what finish time each pace gives, and what pace your "
    "goal time needs. For marathon, half marathon, 10K, 5K and the treadmill.",
    "Pace charts", "tabeller", lang="en", alt="/tabeller/", crumbs=[("Charts", None)]),

 P_("/en/charts/marathon/", "table", "tables",
    "Marathon pace chart – pace, speed and finish time | RunPace",
    "Full marathon pace chart: the finish time each pace gives, and the pace needed "
    "for a 3, 3:30, 4, 4:30 or 5 hour marathon. With halfway splits.",
    "Marathon pace chart", "tab-maraton", lang="en", alt="/tabeller/maraton/",
    crumbs=[TAB_EN, ("Marathon", None)],
    faq=[("What pace is needed for a 4 hour marathon?",
          "5:41 min/km, which is 10.5 km/h. At halfway the clock should read 2:00:00."),
         ("What pace gives a 3:30 marathon?", "4:59 min/km, or 12.1 km/h.")]),

 P_("/en/charts/half-marathon/", "table", "tables",
    "Half marathon pace chart – pace, speed and finish time | RunPace",
    "Half marathon pace chart: finish time for every pace, and the pace needed for "
    "1:30, 1:45, 2:00 and 2:30. With halfway splits.",
    "Half marathon pace chart", "tab-halvmaraton", lang="en",
    alt="/tabeller/halvmaraton/", crumbs=[TAB_EN, ("Half marathon", None)],
    faq=[("What pace is needed for a 2 hour half marathon?",
          "5:41 min/km, or 10.5 km/h, for the full 21.0975 km.")]),

 P_("/en/charts/10k/", "table", "tables",
    "10K pace chart – pace, speed and finish time | RunPace",
    "10K pace chart: the finish time each pace gives, and the pace needed for 40, "
    "45, 50 or 60 minutes.",
    "10K pace chart", "tab-10km", lang="en", alt="/tabeller/10km/",
    crumbs=[TAB_EN, ("10K", None)],
    faq=[("What pace gives a 50 minute 10K?", "5:00 min/km, or 12.0 km/h.")]),

 P_("/en/charts/5k/", "table", "tables",
    "5K pace chart – pace, speed and finish time | RunPace",
    "5K pace chart: finish time for every pace from 3:00 to 7:30 min/km, and the "
    "pace needed for 20, 22, 25 or 30 minutes.",
    "5K pace chart", "tab-5km", lang="en", alt="/tabeller/5km/",
    crumbs=[TAB_EN, ("5K", None)],
    faq=[("What pace gives a 25 minute 5K?", "5:00 min/km, or 12.0 km/h.")]),

 P_("/en/charts/min-km-to-km-h/", "table", "tables",
    "min/km to km/h – running pace conversion chart | RunPace",
    "Full conversion chart between min/km and km/h, from 3:00 to 8:00 min/km, with "
    "the formula and 5K and 10K finish times for every pace.",
    "min/km to km/h conversion chart", "tab-omregning", lang="en",
    alt="/tabeller/min-km-til-km-t/", crumbs=[TAB_EN, ("min/km to km/h", None)],
    faq=[("How do I convert min/km to km/h?",
          "Divide 60 by your pace in minutes. 5:00 min/km gives 60 ÷ 5 = 12 km/h. "
          "Convert seconds to decimals first: 5:30 is 5.5 minutes, and 60 ÷ 5.5 = 10.9 km/h."),
         ("How many km/h is 5:30 min/km?", "10.9 km/h.")]),

 P_("/en/charts/treadmill/", "table", "tables",
    "Treadmill pace chart – km/h to min/km | RunPace",
    "The treadmill shows km/h but you think in min/km. Full chart from 6 to 20 km/h, "
    "with finish times and what incline does to your effort.",
    "Treadmill pace chart: km/h to min/km", "tab-tredemolle", lang="en",
    alt="/tabeller/tredemolle/", crumbs=[TAB_EN, ("Treadmill", None)],
    faq=[("How fast is 12 km/h on a treadmill?", "12 km/h is 5:00 min/km.")]),

 P_("/en/about/", "info", None, "About RunPace",
    "RunPace is a running pace calculator made in Norway. No sign-in, no cookies, "
    "and every calculation happens in your browser.",
    "About RunPace", "om", lang="en", alt="/om/", crumbs=[("About", None)]),

 # Støttesida er Support-URL-en registrert i App Store Connect. Adressen
 # /support/ må derfor ikke endres.
 P_("/support/", "info", None, "Support &amp; Help | RunPace",
    "Support for the RunPace pace calculator and iOS app: how to reach us, answers to "
    "common questions, and how the Apple Health feature works.",
    "Support &amp; Help", "support", lang="en", crumbs=[("Support", None)],
    faq=[("How do I use the pace calculator?",
          "Scroll the wheels to set a pace (min/km) or a speed (km/h) — both update "
          "automatically. Below the wheels you will see estimated finish times for standard "
          "distances from 1 km up to a marathon."),
         ("How do I build a pacing or split plan?",
          "Open the Race plan screen in the app, pick a distance or enter a custom one, and "
          "scroll in your target finish time. RunPace shows the required pace and a split "
          "table so you know what the clock should read at each interval."),
         ("What does the Apple Health feature do?",
          "In the iOS app you can optionally allow RunPace to read your latest VO2max value "
          "from Apple Health, to suggest training zones and a starting point for race "
          "predictions. This is fully optional — every feature works without it."),
         ("Does RunPace collect my data?",
          "The iOS app has no account and every calculation happens locally on your device. "
          "From version 1.5 it shows a small banner ad delivered by Google AdMob. Apart from "
          "that banner the app sends nothing about you anywhere, and Health data is never "
          "used for advertising.")]),

 P_("/en/privacy/", "info", None, "Privacy Policy | RunPace",
    "What RunPace collects, what it does not, and how the ads in the iOS app work.",
    "Privacy Policy", "personvern", lang="en", alt="/personvern/",
    crumbs=[("Privacy", None)]),
]

BY_URL = {p["url"]: p for p in PAGES}


# ── Innsetting av genererte tabeller ────────────────────────────────
def expand(html, page):
    lang = page["lang"]

    def repl(m):
        name = m.group(1)
        a = name.split("|")
        if a[0] == "cta":
            return C.store_cta(page, a[1], a[2], a[3])
        if a[0] == "pace2time":
            # a[4] er skrittlengde i sekunder og må være et tall
            return T.pace_to_time(a[1], lang, a[2], a[3], int(a[4]))
        if a[0] == "time2pace":
            return T.time_to_pace(a[1], lang, T.goals(a[1]))
        if a[0] == "conversion":
            return T.conversion(lang)
        if a[0] == "treadmill":
            return T.treadmill(lang)
        if a[0] == "alldist":
            return T.all_distances(lang)
        if a[0] == "riegel":
            return T.riegel_examples(lang)
        if a[0] == "negsplit":
            return T.negative_split(lang, a[1], int(a[2]), int(a[3]))
        raise SystemExit("Ukjent plassholder: {{%s}} i %s" % (name, page["url"]))

    return re.sub(r"\{\{([^}]+)\}\}", repl, html)


# ── Rendering ───────────────────────────────────────────────────────
def render(page):
    lang = page["lang"]
    body_path = os.path.join(SRC, "body", lang, page["body"] + ".html")
    if not os.path.exists(body_path):
        raise SystemExit("Mangler brødtekst: %s" % body_path)
    body = expand(io.open(body_path, encoding="utf-8").read().rstrip(), page)

    alt = page.get("alt")
    updated = ""
    if page["kind"] in ("guide", "table"):
        updated = ('  <p class="page-meta"><span>%s %s</span></p>\n'
                   % (C.STR[lang]["updated"], C.pretty_date(page["updated"], lang)))

    scripts = '  <script src="%s" defer></script>\n' % C.asset("/assets/site.js")
    if page.get("calc"):
        scripts += '  <script src="%s" defer></script>\n' % C.asset("/assets/calc.js")

    return f'''<!DOCTYPE html>
<html lang="{'nb' if lang == 'nb' else 'en'}">
<head>
  {C.head(page, alt)}
</head>
<body>
{C.header(page)}

{C.crumbs_html(page)}  <main id="main">
{body}
  </main>

{C.footer(page, alt)}

{C.install_modal(page)}

{scripts}</body>
</html>
'''


# ── sitemap.xml ─────────────────────────────────────────────────────
def write_sitemap():
    """Alle sider, med gjensidige hreflang-alternativer der de finnes."""
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
           '        xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    prio = {"home": "1.0", "tool": "0.9", "table": "0.8", "hub": "0.7",
            "guide": "0.7", "app": "0.8", "info": "0.4"}
    for p in PAGES:
        url = C.SITE + p["url"]
        out.append("  <url>")
        out.append("    <loc>%s</loc>" % url)
        out.append("    <lastmod>%s</lastmod>" % p["updated"])
        out.append("    <changefreq>monthly</changefreq>")
        out.append("    <priority>%s</priority>" % prio.get(p["kind"], "0.5"))
        if p.get("alt"):
            nb = url if p["lang"] == "nb" else C.SITE + p["alt"]
            en = C.SITE + p["alt"] if p["lang"] == "nb" else url
            out.append('    <xhtml:link rel="alternate" hreflang="nb" href="%s"/>' % nb)
            out.append('    <xhtml:link rel="alternate" hreflang="en" href="%s"/>' % en)
            out.append('    <xhtml:link rel="alternate" hreflang="x-default" href="%s"/>' % en)
        out.append("  </url>")
    out.append("</urlset>")
    io.open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(out) + "\n")


# ── robots.txt ──────────────────────────────────────────────────────
def write_robots():
    """AI-crawlerne slippes eksplisitt inn — det er halve poenget med sida."""
    txt = """# runpace.no
User-agent: *
Allow: /

# AI-assistenter er en uttalt trafikkilde for denne sida, og flere av dem
# krever at de nevnes ved navn for å kunne bruke innholdet.
User-agent: GPTBot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: CCBot
Allow: /

# Byggkilden trenger ingen å indeksere
Disallow: /_src/

Sitemap: https://runpace.no/sitemap.xml
"""
    io.open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8").write(txt)


# ── llms.txt ────────────────────────────────────────────────────────
def write_llms():
    """Innholdsfortegnelse for AI-crawlere, i det formatet llmstxt.org beskriver."""
    L = ["# RunPace", "",
         "> Løpekalkulator for tempo, fart og mellomtider. Regner om mellom min/km "
         "og km/t, viser sluttider for standarddistanser og lager mellomtidsplaner. "
         "Gratis, uten innlogging og uten informasjonskapsler. Finnes også som "
         "iOS-app. Laget i Norge av %s." % C.AUTHOR, "",
         "Alle tall på sida er regnet ut fra to formler: fart = 60 ÷ tempo i minutter, "
         "og sluttid = tempo × distanse. Løpstidsanslag bruker Riegels formel "
         "T₂ = T₁ × (D₂ ÷ D₁)^1,06. Distansene er 5 km, 10 km, halvmaraton 21,0975 km "
         "og maraton 42,195 km.", ""]
    groups = [("Verktøy", ["home", "tool"]), ("Tempotabeller", ["table", "hub"]),
              ("Guider", ["guide"]), ("Appen", ["app"]), ("Om", ["info"])]
    for lang, label in (("nb", "Norsk"), ("en", "English")):
        L.append("## %s" % label)
        L.append("")
        for title, kinds in groups:
            rows = [p for p in PAGES if p["lang"] == lang and p["kind"] in kinds]
            for p in rows:
                L.append("- [%s](%s%s): %s" % (p["h1"], C.SITE, p["url"], p["desc"]))
        L.append("")
    L.append("## Kontakt")
    L.append("")
    L.append("- E-post: %s" % C.CONTACT)
    L.append("- iOS-app: %s" % C.APP_URL)
    L.append("")
    io.open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8").write("\n".join(L))


# ── 404 ─────────────────────────────────────────────────────────────
def write_404():
    page = P_("/404.html", "info", None, "Fant ikke sida | RunPace",
              "Sida finnes ikke. Her er veien tilbake til løpekalkulatoren.",
              "Fant ikke sida", "_404")
    body = """  <article class="narrow">
    <h1>Fant ikke sida</h1>
    <div class="answer">
      <p>Adressen finnes ikke — eller den har flyttet. Nettsida ble bygget om i
        september 2026, og noen sider fikk nye adresser.</p>
    </div>
    <p>Her er de mest brukte:</p>
    <ul>
      <li><a href="/">Løpekalkulator</a> — tempo, fart og sluttider</li>
      <li><a href="/mellomtider/">Mellomtider</a> — tempoplan for måltiden din</li>
      <li><a href="/tabeller/">Tempotabeller</a> — maraton, halvmaraton, 10 km, 5 km</li>
      <li><a href="/guider/">Guider</a> — om tempo, pacing og målsetting</li>
      <li><a href="/app/">RunPace til iPhone</a></li>
    </ul>
    <p>Kom du hit fra en lenke som burde virke, si gjerne fra til
      <a href="mailto:kontakt@runpace.no">kontakt@runpace.no</a>.</p>
  </article>"""
    d = os.path.join(SRC, "body", "nb")
    io.open(os.path.join(d, "_404.html"), "w", encoding="utf-8").write(body)
    html = render(page).replace('<link rel="canonical" href="https://runpace.no/404.html">',
                                '<meta name="robots" content="noindex">')
    io.open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8").write(html)


def main():
    written = []
    for page in PAGES:
        out = page["url"].strip("/")
        path = os.path.join(ROOT, out, "index.html") if out else os.path.join(ROOT, "index.html")
        d = os.path.dirname(path)
        if d and not os.path.isdir(d):
            os.makedirs(d)
        html = render(page)
        io.open(path, "w", encoding="utf-8").write(html)
        written.append((page["url"], len(html)))
    write_sitemap()
    write_robots()
    write_llms()
    write_404()
    for url, n in written:
        print("  %-34s %6d B" % (url, n))
    print("\n%d sider skrevet, pluss sitemap.xml, robots.txt, llms.txt og 404.html."
          % len(written))


if __name__ == "__main__":
    main()
