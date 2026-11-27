# -*- coding: utf-8 -*-
"""DraveBezorger - fiets door de straat en bezorg de kranten (27-11-2026, idee van pa: zijn C64-lievelingsspel).

Je fietst schuin door een straat. Huizen met een gouden vlaggetje op de brievenbus zijn abonnees:
gooi de krant in de bus of op de deurmat. Bij de andere huizen mag je best een ruitje meepikken.
Pas op voor honden, maaiers, skaters, auto's en putten. Aan het eind van de straat: het oefenparcours.
Een hele week, van maandag tot zondag. Mis je een abonnee, dan zegt hij op.

Besturing: pijltjes omhoog/omlaag = sneller/langzamer, links/rechts = sturen, spatie = krant gooien,
P = pauze, M = muziek, Esc = terug. Geen muis nodig.

Werkt in de DraveSpellenkast (UI wordt dan gezet door main.py) en ook los (python bezorger.py / DraveBezorger.exe).
Copyright (C) 2026 Dravenlock (Roger & Claudio). GNU GPL v3.0.
"""
import json
import locale
import math
import os
import random
import sys
import time
from array import array

import pygame

UI = None                    # in de Spellenkast: het main-module
VERSIE = "0.1.0"
W, H = 1280, 800
HERE = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))

ACHTER, VAK, RAND = (22, 19, 31), (36, 31, 51), (74, 61, 102)
ACCENT, PAARS, TEKST, ZACHT = (181, 156, 255), (127, 119, 221), (242, 238, 252), (169, 159, 196)
GOUD, GROEN, ROOD = (224, 184, 90), (63, 166, 107), (196, 71, 90)

TX = {
    "bez": ("DraveBezorger", "DravePaperRound"),
    "bez_sub": ("Fiets door de straat en bezorg de krant", "Ride down the street and deliver the paper"),
    "begin": ("Begin de week", "Start the week"),
    "dagen": (("Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"),
              ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")),
    "punten": ("Punten", "Score"), "kranten": ("Kranten", "Papers"), "levens": ("Levens", "Lives"),
    "abo": ("Abonnees", "Subscribers"), "dag": ("Dag", "Day"),
    "spatie_fiets": ("Spatie of Enter = fietsen!", "Space or Enter = ride!"),
    "ochtend_uitleg": ("Gouden vlaggetje = abonnee. Gooi de krant in de bus of op de mat.",
                       "Gold flag = subscriber. Throw the paper in the mailbox or on the mat."),
    "in_bus": ("In de bus!", "In the box!"), "op_mat": ("Op de mat!", "On the mat!"),
    "in_tuin": ("In de tuin", "On the lawn"), "ruit": ("Rinkel!", "Crash!"),
    "oeps_ruit": ("Oei, ruit van een abonnee!", "Oops, a subscriber's window!"),
    "pak": ("+10 kranten", "+10 papers"), "kira": ("Aai Kira!", "Pet Kira!"),
    "raak": ("Raak!", "Hit!"), "doel": ("Roos!", "Bullseye!"),
    "val": ("Au! Van je fiets...", "Ouch! You fell off..."),
    "parcours": ("Het oefenparcours! Gooi naar de schijven.", "The training course! Throw at the targets."),
    "avond": ("Einde van de %s", "End of %s"),
    "bezorgd": ("Bezorgd: %d van de %d abonnees", "Delivered: %d of %d subscribers"),
    "opgezegd": ("Opgezegd: %s", "Cancelled: %s"), "niemand_op": ("Niemand zegt op. Netjes!", "Nobody cancels. Well done!"),
    "perfect": ("Perfecte dag! Er komt een nieuwe abonnee bij.", "Perfect day! A new subscriber joins."),
    "huis": ("huis %d", "house %d"),
    "volgende": ("Volgende dag", "Next day"),
    "ontslagen": ("Geen abonnees meer... je bent ontslagen!", "No subscribers left... you're fired!"),
    "op": ("Je levens zijn op.", "You're out of lives."),
    "week_klaar": ("De hele week gefietst! Bezorger van de week!", "The whole week done! Paperboy of the week!"),
    "bonus": ("Bonus: %d per abonnee", "Bonus: %d per subscriber"),
    "beste": ("Beste score", "High score"),
    "opnieuw": ("Opnieuw", "Play again"), "scores": ("Beste scores", "High scores"),
    "pauze": ("PAUZE - druk P", "PAUSED - press P"),
    "toetsen": ("Pijl omhoog/omlaag = sneller/langzamer  ·  links/rechts = sturen  ·  spatie = krant gooien  ·  P = pauze  ·  M = muziek",
                "Up/down = faster/slower  ·  left/right = steer  ·  space = throw  ·  P = pause  ·  M = music"),
    "niveau": (("Rustig", "Normaal", "Pittig"), ("Easy", "Normal", "Hard")),
    "uitleg": ("Uitleg", "How to play"), "stoppen": ("Stoppen", "Quit"),
    "uitleg_tekst": (
        "Je bent de krantenbezorger. Je fietst vanzelf door de straat.\n"
        "Pijl omhoog = sneller, pijl omlaag = langzamer, links en rechts = sturen.\n"
        "Spatie = gooi een krant naar links, naar de huizen.\n"
        "Huizen met een GOUDEN vlaggetje op de brievenbus zijn abonnees.\n"
        "In de brievenbus = 250 punten, op de deurmat = 100. Mis je er een, dan zegt hij morgen op.\n"
        "Bij de andere huizen: een ruitje meepikken mag (50 punten). Bij een abonnee niet!\n"
        "Pas op voor honden, maaiers, skaters, auto's, putten, brandkranen en heggen.\n"
        "Een krant tegen een hond of skater: weg zijn ze (100 punten).\n"
        "Stapel kranten op de stoep? Fiets erover: +10 kranten. Kira op de stoep? Fiets langs voor een aai!\n"
        "Aan het eind: het oefenparcours. Raak de schijven voor punten.\n"
        "Een perfecte dag geeft een nieuwe abonnee. Haal de zondag!",
        "You are the paper boy. You ride down the street by yourself.\n"
        "Up = faster, down = slower, left and right = steer.\n"
        "Space = throw a paper to the left, at the houses.\n"
        "Houses with a GOLD flag on the mailbox are subscribers.\n"
        "In the mailbox = 250 points, on the doormat = 100. Miss one and he cancels tomorrow.\n"
        "Other houses: breaking a window is allowed (50 points). Not at a subscriber!\n"
        "Watch out for dogs, mowers, skaters, cars, drains, hydrants and hedges.\n"
        "A paper at a dog or skater: they're gone (100 points).\n"
        "Stack of papers on the pavement? Ride over it: +10 papers. Kira on the pavement? Ride past for a pat!\n"
        "At the end: the training course. Hit the targets for points.\n"
        "A perfect day earns a new subscriber. Make it to Sunday!"),
    "menu": ("Menu", "Menu"), "hulp": ("Hulp", "Help"), "aan": ("aan", "on"), "uitm": ("uit", "off"),
    "terug": ("Terug", "Back"), "doneer": ("Doneer via PayPal", "Donate via PayPal"),
}


def _taal():
    try:
        t = (locale.getlocale()[0] or locale.getdefaultlocale()[0] or "")
    except Exception:
        t = ""
    return "nl" if t.lower().startswith(("nl", "dutch")) else "en"


EIGEN_TAAL = _taal()


def taal():
    return UI.TAAL if UI is not None else EIGEN_TAAL


def T(k):
    v = TX.get(k)
    if v is None:
        return UI.T(k) if UI is not None else k
    return v[0] if taal() == "nl" else v[1]


_FONTS = {}


def tekst(d, t, px, kl, pos, mid=False, vet=True, rechts=False):
    if UI is not None:
        return UI.tekst(d, t, px, kl, pos, mid=mid, vet=vet, rechts=rechts)
    k = (px, vet)
    if k not in _FONTS:
        _FONTS[k] = pygame.font.SysFont("segoeui,arial,dejavusans", px, bold=vet)
    s = _FONTS[k].render(t, True, kl)
    r = s.get_rect()
    if mid:
        r.center = pos
    elif rechts:
        r.topright = pos
    else:
        r.topleft = pos
    d.blit(s, r)
    return r


class _Knop:
    """Zelfde knop als in de Spellenkast, voor als het spel los draait."""

    def __init__(self, rect, label, actie, kleur=VAK, px=26, aan=True):
        self.r = pygame.Rect(rect)
        self.label, self.actie, self.kleur, self.px, self.aan = label, actie, kleur, px, aan

    def teken(self, d, muis):
        hover = self.aan and self.r.collidepoint(muis)
        k = self.kleur if self.aan else (50, 45, 64)
        if hover:
            k = tuple(min(255, c + 25) for c in k)
        pygame.draw.rect(d, k, self.r, border_radius=14)
        pygame.draw.rect(d, ACCENT if hover else RAND, self.r, 3 if hover else 2, border_radius=14)
        donker = sum(self.kleur) > 450
        tekst(d, self.label, self.px, (30, 24, 40) if donker else (TEKST if self.aan else ZACHT), self.r.center, mid=True)

    def klik(self, pos):
        if self.aan and self.r.collidepoint(pos):
            self.actie()
            return True
        return False


def Knop(*a, **k):
    return UI.Knop(*a, **k) if UI is not None else _Knop(*a, **k)


def knip(t, px, breedte):
    """Zinnen in regels die passen."""
    if UI is not None:
        return UI.Backgammon._knip(None, t, px, breedte)
    k = (px, False)
    if k not in _FONTS:
        _FONTS[k] = pygame.font.SysFont("segoeui,arial,dejavusans", px)
    f = _FONTS[k]
    regels, nu = [], ""
    for w in t.split():
        p = (nu + " " + w).strip()
        if f.size(p)[0] > breedte and nu:
            regels.append(nu)
            nu = w
        else:
            nu = p
    if nu:
        regels.append(nu)
    return regels


# ------------------------------------------------------------------ geluid (zelf gemaakt, geen bestanden)
class Klank:
    def __init__(self, met_muziek):
        self.ok = False
        self.s = {}
        self.muziek = None
        self.muziek_aan = met_muziek
        self.kanaal = None
        try:
            ini = pygame.mixer.get_init()
            if not ini:
                pygame.mixer.init(22050, -16, 1, 512)
                ini = pygame.mixer.get_init()
            self.f, fmt, self.ch = ini
            if fmt != -16:
                return
            self.maak_effecten()
            if met_muziek:
                self.muziek = self.maak_muziek()
            self.ok = True
        except Exception:
            self.ok = False

    def _snd(self, samples):
        a = array("h")
        if self.ch == 1:
            a.extend(samples)
        else:
            for v in samples:
                for _ in range(self.ch):
                    a.append(v)
        return pygame.mixer.Sound(buffer=a.tobytes())

    def _golf(self, dur, fn, vol=0.4):
        n = int(self.f * dur)
        uit = []
        staart = max(1, int(self.f * 0.03))
        for i in range(n):
            t = i / self.f
            x = fn(t)
            env = min(1.0, (n - i) / staart, (i + 1) / 40)
            uit.append(int(max(-1.0, min(1.0, x)) * vol * 32000 * env))
        return self._snd(uit)

    def maak_effecten(self):
        rnd = random.Random(7)
        sq = lambda f, t: 1.0 if (t * f) % 1 < 0.5 else -1.0
        self.s["gooi"] = self._golf(0.18, lambda t: rnd.uniform(-1, 1) * (1 - t / 0.18) * 0.7, 0.35)
        self.s["bus"] = self._golf(0.35, lambda t: (math.sin(t * 6.283 * 1320) + 0.5 * math.sin(t * 6.283 * 1980)) * math.exp(-t * 9), 0.45)
        self.s["mat"] = self._golf(0.12, lambda t: sq(180 - t * 600, t) * math.exp(-t * 20), 0.35)
        self.s["glas"] = self._golf(0.5, lambda t: rnd.uniform(-1, 1) * math.exp(-t * 7) * (0.6 + 0.4 * math.sin(t * 6.283 * 3100)), 0.45)
        self.s["boem"] = self._golf(0.45, lambda t: (rnd.uniform(-1, 1) * 0.6 + sq(70 - t * 60, t) * 0.5) * math.exp(-t * 5), 0.55)
        self.s["blaf"] = self._golf(0.28, lambda t: sq(240 - t * 300, t) * (1 if t < 0.1 or 0.16 < t < 0.26 else 0) * 0.8, 0.35)
        self.s["kira"] = self._golf(0.3, lambda t: sq(620 + 200 * math.sin(t * 40), t) * (1 if t < 0.12 or 0.17 < t < 0.29 else 0) * 0.6, 0.25)
        self.s["pak"] = self._golf(0.3, lambda t: sq((523, 659, 784, 1046)[min(3, int(t / 0.075))], t), 0.25)
        self.s["bel"] = self._golf(0.45, lambda t: (math.sin(t * 6.283 * 2100) + math.sin(t * 6.283 * 2650)) * 0.5 * math.exp(-t * 6), 0.4)
        self.s["raak"] = self._golf(0.2, lambda t: sq(880 + t * 2000, t) * math.exp(-t * 10), 0.3)
        self.s["fanfare"] = self._golf(1.1, lambda t: sq((523, 659, 784, 659, 784, 1046)[min(5, int(t / 0.17))], t) * 0.8, 0.28)
        self.s["droef"] = self._golf(1.0, lambda t: sq((392, 370, 349, 330)[min(3, int(t / 0.25))], t) * 0.8, 0.28)

    def maak_muziek(self):
        """Een eigen vrolijk deuntje (geen bestaand nummer), 8 maten, loopt rond."""
        def n2f(n):
            return 440.0 * 2 ** ((n - 69) / 12.0) if n else 0
        C4, D4, E4, F4, G4, A4, B4 = 60, 62, 64, 65, 67, 69, 71
        C5, D5, E5, F5, G5, A5, B5, C6 = 72, 74, 76, 77, 79, 81, 83, 84
        mel = [C5, E5, G5, E5, F5, A5, G5, E5, D5, F5, E5, C5, D5, G4, B4, D5,
               C5, E5, G5, C6, A5, F5, G5, E5, D5, E5, F5, D5, C5, 0, G4, C5]
        bas = [36, 41, 38, 43, 36, 41, 43, 36]
        tel = 0.2                                  # een achtste
        uit = []
        for i, nt in enumerate(mel):
            for half in range(2):                  # elke noot = 2 achtsten
                nr = i * 2 + half
                b = bas[(nr // 8) % 8] + (12 if (nr // 2) % 2 else 0)
                fm, fb = n2f(nt), n2f(b)
                m = int(self.f * tel)
                for k in range(m):
                    t = k / self.f
                    tt = (nr * m + k) / self.f
                    v = 0.0
                    if fm and not (half == 1 and k > m * 0.8):
                        v += (0.5 if (tt * fm) % 1 < 0.25 else -0.5) * (0.85 if half == 0 else 0.7)
                    if fb:
                        ph = (tt * fb) % 1
                        v += (4 * ph - 1 if ph < 0.5 else 3 - 4 * ph) * 0.45
                    if half == 0 and k < m * 0.15 and (nr % 4 == 0):
                        v += math.sin(t * 6.283 * 90) * (1 - k / (m * 0.15)) * 0.6
                    uit.append(int(max(-1, min(1, v * 0.5)) * 0.22 * 32000))
        return self._snd(uit)

    def speel(self, naam):
        if self.ok and naam in self.s:
            try:
                self.s[naam].play()
            except Exception:
                pass

    def start_muziek(self):
        if self.ok and self.muziek and self.muziek_aan:
            try:
                if self.kanaal is None or not self.kanaal.get_busy():
                    self.kanaal = self.muziek.play(loops=-1)
            except Exception:
                pass

    def stop_muziek(self):
        if self.kanaal:
            try:
                self.kanaal.stop()
            except Exception:
                pass
            self.kanaal = None

    def wissel_muziek(self):
        self.muziek_aan = not self.muziek_aan
        if self.muziek_aan:
            self.start_muziek()
        else:
            self.stop_muziek()


# ------------------------------------------------------------------ de wereld (schuin, zoals vroeger)
X0, Y0 = 470, 470
FX, FY = 0.62, -0.40     # één stap vooruit in de straat
RX, RY = 0.62, 0.40      # één stap opzij (naar de weg toe)

HUIS_L, HUIS_D, HUIS_H = 300, 180, 120
PERIODE = 520
HUIS_V0, HUIS_V1 = -470, -290       # achterkant .. voorgevel
BUS_V = -112
STOEP_V0, STOEP_V1 = -80, -20
WEG_V0, WEG_V1 = -20, 200
MIN_V, MAX_V = -250, 210

HUIS_KLEUREN = [((196, 150, 110), (150, 70, 60)), ((170, 190, 210), (70, 80, 110)), ((215, 200, 150), (120, 90, 60)),
                ((180, 160, 200), (90, 70, 120)), ((160, 190, 160), (80, 110, 80)), ((220, 180, 170), (130, 60, 70))]


class Huis:
    def __init__(self, nr, u, abo, rng):
        self.nr = nr
        self.u = u
        self.abo = abo
        self.muur, self.dak = HUIS_KLEUREN[rng.randrange(len(HUIS_KLEUREN))]
        self.bezorgd = False
        self.schade = False
        self.ruiten = [False, False]
        self.bus = (u + HUIS_L - 30, BUS_V)
        self.mat = (u + 110, u + 150)


class Ding:
    """Iets op straat: hond, maaier, skater, auto, put, brandkraan, heg, stapel, kira, doel, kegel, finish."""

    def __init__(self, soort, u, v, **k):
        self.soort, self.u, self.v = soort, u, v
        self.weg = False
        self.actief = False
        self.t = random.random() * 10
        self.vu = k.get("vu", 0.0)
        self.vv = k.get("vv", 0.0)
        self.v0 = v
        self.raak = False
        self.r = {"hond": 26, "maaier": 30, "skater": 24, "auto": 70, "put": 24, "kraan": 16, "heg": 0,
                  "stapel": 30, "kira": 50, "doel": 30, "kegel": 16, "finish": 0, "bus": 16}.get(soort, 20)


class Bezorger:
    def __init__(self, app, niveau):
        self.app = app
        self.niveau = max(1, min(3, niveau))
        self.knoppen = []
        self.klank = Klank(met_muziek=(UI is None))
        if UI is None:
            self.klank.start_muziek()
        self.fase = "titel"
        self.toon_uitleg = False
        self.scores = self.laad_scores()
        self.tik = 0
        self.pu, self.pv, self.cam, self.kranten, self.val = 0.0, 0.0, 0.0, 10, 0
        self.nieuwe_week()
        if UI is not None:
            self.nieuw_potje()

    # ---------- bewaren
    def data_map(self):
        if UI is not None and getattr(UI, "DATA", None):
            m = UI.DATA
        else:
            m = os.path.join(HERE, "DraveBezorger-data")
        try:
            os.makedirs(m, exist_ok=True)
        except Exception:
            pass
        return m

    def laad_scores(self):
        try:
            with open(os.path.join(self.data_map(), "bezorger_scores.json"), encoding="utf-8") as f:
                return json.load(f)[:5]
        except Exception:
            return []

    def bewaar_score(self):
        self.scores.append({"punten": self.punten, "dag": self.dag + 1, "niveau": self.niveau,
                            "datum": time.strftime("%d-%m-%Y")})
        self.scores.sort(key=lambda s: -s["punten"])
        self.scores = self.scores[:5]
        try:
            with open(os.path.join(self.data_map(), "bezorger_scores.json"), "w", encoding="utf-8") as f:
                json.dump(self.scores, f)
        except Exception:
            pass

    # ---------- spelverloop
    def nieuwe_week(self):
        self.rng = random.Random()
        self.dag = 0
        self.punten = 0
        self.levens = 5 if self.niveau == 1 else 3
        n = 16
        aantal = 10 if self.niveau < 3 else 9
        abo = [True] * aantal + [False] * (n - aantal)
        self.rng.shuffle(abo)
        self.abo = abo
        self.verslag = []

    def nieuw_potje(self):
        self.nieuwe_week()
        self.fase = "ochtend"
        self.maak_straat()
        self.speel("bel")

    def speel(self, naam):
        self.klank.speel(naam)

    def maak_straat(self):
        rng = self.rng
        self.huizen = [Huis(i + 1, 400 + i * PERIODE, self.abo[i], rng) for i in range(len(self.abo))]
        self.einde_straat = 400 + len(self.abo) * PERIODE + 100
        self.dingen = []
        dicht = (0.45, 0.75, 1.0)[self.niveau - 1] * (0.65 + self.dag * 0.08)
        for h in self.huizen:
            self.dingen.append(Ding("bus", h.bus[0], h.bus[1]))
            if h.nr < len(self.huizen):
                self.dingen.append(Ding("heg", h.u + HUIS_L + 90, -200))
            if rng.random() < 0.35 * dicht:
                self.dingen.append(Ding("hond", h.u + rng.randint(40, 200), rng.randint(-240, -150)))
            if rng.random() < 0.25 * dicht:
                self.dingen.append(Ding("maaier", h.u + rng.randint(40, 220), -200, vv=1.2 + rng.random()))
            if rng.random() < 0.3 * dicht:
                self.dingen.append(Ding("skater", h.u + rng.randint(200, 500), rng.randint(20, 170), vu=-1.5 - rng.random() * 1.5 * dicht))
            if rng.random() < 0.22 * dicht and h.nr > 1:
                self.dingen.append(Ding("auto", h.u + HUIS_L + 30, -150, vv=1.6 + dicht))
            if rng.random() < 0.3 * dicht:
                self.dingen.append(Ding("put", h.u + rng.randint(0, 480), rng.choice((10, 60, 120, 170))))
            if rng.random() < 0.2 * dicht:
                self.dingen.append(Ding("kraan", h.u + rng.randint(0, 480), -30))
            if rng.random() < 0.22:
                self.dingen.append(Ding("stapel", h.u + rng.randint(0, 480), rng.randint(-70, -30)))
        # Kira, één keer per dag
        h = self.huizen[rng.randint(3, len(self.huizen) - 3)]
        self.dingen.append(Ding("kira", h.u + 200, -55))
        # oefenparcours
        u = self.einde_straat + 300
        for i in range(8):
            self.dingen.append(Ding("doel", u + i * 230, -180 + (i % 2) * 40))
            if i % 2 == 1:
                self.dingen.append(Ding("kegel", u + i * 230 + 100, rng.choice((30, 90, 150))))
        self.finish = u + 8 * 230 + 200
        self.dingen.append(Ding("finish", self.finish, 90))
        # fietser
        self.pu, self.pv = 0.0, 60.0
        self.snel = 3.6
        self.kranten = 10
        self.kranten_t = 0
        self.val = 0
        self.papieren = []
        self.liggend = []
        self.popups = []
        self.parcours = False
        self.parcours_punten = 0
        self.melding_t = 0
        self.melding = ""
        self.pauze = False

    def start_dag(self):
        self.fase = "rijden"
        self.speel("bel")

    def einde_dag(self):
        self.fase = "avond"
        bez = [h for h in self.huizen if h.abo and h.bezorgd and not h.schade]
        abo = [h for h in self.huizen if h.abo]
        weg = [h for h in abo if not (h.bezorgd and not h.schade)]
        self.verslag = [T("bezorgd") % (len(bez), len(abo))]
        if weg:
            self.verslag.append(T("opgezegd") % ", ".join(T("huis") % h.nr for h in weg))
        else:
            self.verslag.append(T("niemand_op"))
        for h in weg:
            self.abo[h.nr - 1] = False
        if not weg and abo:
            vrij = [i for i, a in enumerate(self.abo) if not a]
            if vrij:
                self.abo[self.rng.choice(vrij)] = True
                self.verslag.append(T("perfect"))
        if self.parcours_punten:
            self.verslag.append("%s: %d" % (T("parcours").split("!")[0], self.parcours_punten))
        if not any(self.abo):
            self.verslag.append(T("ontslagen"))
            self.einde_spel()
            return
        if self.dag == 6:
            n = sum(self.abo)
            self.punten += n * 250
            self.verslag.append(T("week_klaar"))
            self.verslag.append(T("bonus") % 250)
            self.einde_spel(goed=True)
            return
        self.speel("fanfare")

    def volgende_dag(self):
        self.dag += 1
        self.maak_straat()
        self.fase = "ochtend"
        self.speel("bel")

    def einde_spel(self, goed=False):
        self.fase = "einde"
        self.speel("fanfare" if goed else "droef")
        self.bewaar_score()

    # ---------- invoer
    def klik(self, pos):
        if self.toon_uitleg:
            self.toon_uitleg = False

    def toets(self, e):
        if self.toon_uitleg:
            self.toon_uitleg = False
            return
        if e.key == pygame.K_ESCAPE:
            if self.fase in ("rijden", "ochtend", "avond", "einde"):
                self.naar_titel()
            else:
                self.terug()
            return
        if e.key == pygame.K_m and UI is None:
            self.klank.wissel_muziek()
            return
        if self.fase == "titel" and e.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.nieuw_potje()
        elif self.fase == "ochtend" and e.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.start_dag()
        elif self.fase == "rijden":
            if e.key == pygame.K_p:
                self.pauze = not self.pauze
            elif e.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_LCTRL, pygame.K_RCTRL) and not self.pauze:
                self.gooi()
        elif self.fase == "avond" and e.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.volgende_dag()
        elif self.fase == "einde" and e.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.nieuw_potje()

    def naar_titel(self):
        if UI is not None:
            self.terug()
        else:
            self.fase = "titel"

    def terug(self):
        self.klank.stop_muziek()
        self.app.naar_menu()

    def gooi(self):
        if self.val or self.kranten <= 0:
            return
        self.kranten -= 1
        self.papieren.append({"u": self.pu + 10, "v": self.pv - 20, "h": 34.0, "vu": self.snel + 1.5,
                              "vv": -11.0, "vh": 5.0, "draai": 0.0})
        self.speel("gooi")

    def popup(self, u, v, t, kl=GOUD):
        self.popups.append({"u": u, "v": v, "h": 60.0, "t": t, "kl": kl, "tijd": 70})

    # ---------- elke beeldje
    def update(self):
        self.tik += 1
        if self.fase != "rijden" or self.pauze or self.toon_uitleg:
            return
        if self.melding_t:
            self.melding_t -= 1
        knop = pygame.key.get_pressed()
        basis = (3.2, 3.8, 4.4)[self.niveau - 1]
        if self.val:
            self.val -= 1
            self.snel = 0
            if self.val == 0:
                if self.levens <= 0:
                    self.einde_spel()
                    return
                self.snel = basis
                self.pv = 60
                # alles vlakbij even opzij zodat je niet meteen weer valt
                for d in self.dingen:
                    if d.soort in ("hond", "skater", "auto", "maaier") and abs(d.u - self.pu) < 300:
                        d.weg = True
                if self.parcours:
                    self.einde_dag()
            self.beweeg_rest()
            return
        doel = basis
        if knop[pygame.K_UP]:
            doel = basis + 3.2
        elif knop[pygame.K_DOWN]:
            doel = 1.6
        self.snel += (doel - self.snel) * 0.06
        zij = 4.2
        if knop[pygame.K_LEFT]:
            self.pv -= zij
        if knop[pygame.K_RIGHT]:
            self.pv += zij
        self.pv = max(MIN_V, min(MAX_V, self.pv))
        self.pu += self.snel
        if not self.parcours and self.pu > self.einde_straat:
            self.parcours = True
            self.melding, self.melding_t = T("parcours"), 180
            self.speel("bel")
            for h in self.huizen:              # niets meer bezorgd na de straat
                pass
        if self.pu > self.finish:
            self.einde_dag()
            return
        # botsingen
        for d in self.dingen:
            if d.weg:
                continue
            du, dv = d.u - self.pu, d.v - self.pv
            if d.soort == "heg":
                if -16 < du < 16 and -280 < self.pv < -120:
                    self.botsing()
                    return
                continue
            if abs(du) > 90:
                continue
            if d.soort == "auto":
                if -60 < du < 60 and -45 < dv < 45:
                    self.botsing()
                    return
                continue
            if d.soort == "finish":
                continue
            if math.hypot(du, dv) < d.r + 14:
                if d.soort == "stapel":
                    d.weg = True
                    self.kranten = min(20, self.kranten + 10)
                    self.popup(d.u, d.v, T("pak"), GROEN)
                    self.speel("pak")
                elif d.soort == "kira":
                    if not d.raak:
                        d.raak = True
                        self.punten += 100
                        self.popup(d.u, d.v, T("kira") + "  +100", (255, 190, 120))
                        self.speel("kira")
                elif d.soort == "doel":
                    pass
                else:
                    self.botsing()
                    return
        self.beweeg_rest()

    def botsing(self):
        self.val = 90
        self.levens -= 0 if self.parcours else 1
        self.speel("boem")
        self.melding, self.melding_t = T("val"), 90

    def beweeg_rest(self):
        # dingen bewegen
        for d in self.dingen:
            if d.weg:
                continue
            d.t += 1 / 60
            afstand = d.u - self.pu
            if d.soort == "hond":
                if not d.actief and -80 < afstand < 420:
                    d.actief = True
                    self.speel("blaf")
                if d.actief:
                    hs = (2.2, 3.0, 3.8)[self.niveau - 1]
                    d.v += max(-hs, min(hs, (self.pv - d.v) * 0.05))
                    d.u += max(-hs, min(hs, (self.pu + 40 - d.u) * 0.04)) + self.snel * 0.6
                    if afstand < -250:
                        d.weg = True
            elif d.soort == "maaier":
                d.v += d.vv
                if d.v < -250 or d.v > -130:
                    d.vv = -d.vv
            elif d.soort == "skater":
                if afstand < 900:
                    d.u += d.vu
            elif d.soort == "auto":
                if not d.actief and afstand < 520:
                    d.actief = True
                if d.actief and d.v < 260:
                    d.v += d.vv
        # kranten vliegen
        for p in self.papieren:
            p["u"] += p["vu"]
            p["v"] += p["vv"]
            p["h"] += p["vh"]
            p["vh"] -= 0.55
            p["vv"] *= 0.985
            p["draai"] += 0.35
            self.krant_raakt(p)
        for p in self.papieren:
            if p.get("klaar"):
                self.liggend.append((p["u"], p["v"], p["draai"]))
        self.papieren = [p for p in self.papieren if not p.get("klaar")]
        self.liggend = self.liggend[-40:]
        for pp in self.popups:
            pp["tijd"] -= 1
            pp["h"] += 0.8
        self.popups = [pp for pp in self.popups if pp["tijd"] > 0]

    def huis_bij(self, u):
        for h in self.huizen:
            if h.u - 20 <= u <= h.u + HUIS_L + 20:
                return h
        return None

    def krant_raakt(self, p):
        u, v, hh = p["u"], p["v"], p["h"]
        # tegen bewegende dingen
        for d in self.dingen:
            if d.weg or d.soort not in ("hond", "skater", "maaier", "doel"):
                continue
            if math.hypot(d.u - u, d.v - v) < d.r + 10 and hh < 80:
                if d.soort == "doel":
                    if d.raak:
                        continue
                    d.raak = True
                    self.punten += 100
                    self.parcours_punten += 100
                    self.popup(d.u, d.v, T("doel") + "  +100")
                    self.speel("raak")
                else:
                    d.weg = True
                    self.punten += 100
                    self.popup(d.u, d.v, T("raak") + "  +100")
                    self.speel("raak")
                p["klaar"] = True
                return
        h = self.huis_bij(u)
        # brievenbus
        if h is not None and not self.parcours:
            bu, bv = h.bus
            if math.hypot(bu - u, bv - v) < 26 and hh < 70:
                p["klaar"] = True
                if h.abo and not h.bezorgd:
                    h.bezorgd = True
                    self.punten += 250
                    self.popup(bu, bv, T("in_bus") + "  +250")
                else:
                    self.punten += 20
                    self.popup(bu, bv, "+20", ZACHT)
                self.speel("bus")
                return
        # tegen de gevel
        if v <= HUIS_V1 + 4:
            p["klaar"] = True
            if h is not None:
                rel = u - h.u
                raam = 0 if 30 <= rel <= 85 else 1 if 190 <= rel <= 250 else None
                if raam is not None and 45 <= hh <= 100 and not h.ruiten[raam]:
                    h.ruiten[raam] = True
                    self.speel("glas")
                    if h.abo:
                        h.schade = True
                        self.popup(u, v, T("oeps_ruit"), ROOD)
                    else:
                        self.punten += 50
                        self.popup(u, v, T("ruit") + "  +50")
                    return
                if h.abo and not h.bezorgd and h.mat[0] - 25 <= u <= h.mat[1] + 25:
                    h.bezorgd = True
                    self.punten += 100
                    self.popup(u, v, T("op_mat") + "  +100")
                    self.speel("mat")
                    return
            p["v"] = HUIS_V1 + 6
            self.speel("mat")
            return
        # op de grond
        if hh <= 0:
            p["klaar"] = True
            if h is not None and h.abo and not h.bezorgd and not self.parcours:
                if h.mat[0] - 25 <= u <= h.mat[1] + 25 and v < HUIS_V1 + 50:
                    h.bezorgd = True
                    self.punten += 100
                    self.popup(u, v, T("op_mat") + "  +100")
                    self.speel("mat")
                elif self.niveau == 1 and v < STOEP_V0:
                    h.bezorgd = True
                    self.punten += 25
                    self.popup(u, v, T("in_tuin") + "  +25", ZACHT)
                    self.speel("mat")

    # ---------- tekenen
    def P(self, u, v, h=0.0):
        du = u - self.cam
        return (X0 + du * FX + v * RX, Y0 + du * FY + v * RY - h)

    def quad(self, d, pts, kl, rand=None):
        pygame.draw.polygon(d, kl, [self.P(*p) for p in pts])
        if rand:
            pygame.draw.polygon(d, rand, [self.P(*p) for p in pts], 2)

    def teken(self, d, muis):
        self.knoppen = []
        if self.fase == "titel":
            self.teken_titel(d, muis)
        else:
            self.teken_straat(d)
            self.teken_hud(d)
            if self.fase == "ochtend":
                self.teken_ochtend(d, muis)
            elif self.fase == "avond":
                self.teken_avond(d, muis)
            elif self.fase == "einde":
                self.teken_einde(d, muis)
            elif self.pauze:
                self.donker(d)
                tekst(d, T("pauze"), 56, GOUD, (W // 2, H // 2), mid=True)
        if self.toon_uitleg:
            self.teken_uitleg(d, muis)
        for k in self.knoppen:
            k.teken(d, muis)

    def donker(d_self, d, a=150):
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        s.fill((10, 8, 16, a))
        d.blit(s, (0, 0))

    def teken_straat(self, d):
        self.cam = self.pu + 140
        d.fill((96, 150, 80))                     # gras
        u0, u1 = self.cam - 900, self.cam + 1500
        # verre kant: stoep en gras met bomen
        self.quad(d, [(u0, WEG_V1, 0), (u1, WEG_V1, 0), (u1, WEG_V1 + 50, 0), (u0, WEG_V1 + 50, 0)], (186, 180, 170))
        self.quad(d, [(u0, WEG_V0, 0), (u1, WEG_V0, 0), (u1, WEG_V1, 0), (u0, WEG_V1, 0)], (78, 78, 88))
        self.quad(d, [(u0, STOEP_V0, 0), (u1, STOEP_V0, 0), (u1, STOEP_V1, 0), (u0, STOEP_V1, 0)], (196, 190, 178))
        self.quad(d, [(u0, STOEP_V1 - 4, 0), (u1, STOEP_V1 - 4, 0), (u1, STOEP_V1 + 2, 0), (u0, STOEP_V1 + 2, 0)], (140, 136, 126))
        # stoeptegels en streepjes
        s = int(u0 // 80) * 80
        while s < u1:
            pygame.draw.line(d, (170, 164, 152), self.P(s, STOEP_V0), self.P(s, STOEP_V1), 1)
            if (s // 80) % 3 == 0:
                self.quad(d, [(s, 86, 0), (s + 120, 86, 0), (s + 120, 94, 0), (s, 94, 0)], (236, 232, 210))
            s += 80
        # bomen aan de overkant (achter alles)
        lijst = []
        b = int(u0 // 330) * 330
        while b < u1:
            lijst.append(("boom", b, 320))
            b += 330
        # einde straat: tekst op de weg
        for h in self.huizen:
            if u0 - HUIS_L < h.u < u1:
                lijst.append(("huis", h.u + HUIS_L, HUIS_V1, h))
        for x in self.dingen:
            if not x.weg and u0 < x.u < u1:
                lijst.append(("ding", x.u, x.v, x))
        for p in self.liggend:
            if u0 < p[0] < u1:
                self.teken_krantje(d, self.P(p[0], p[1]), p[2], False)
        lijst.append(("ik", self.pu, self.pv))
        lijst.sort(key=lambda e: self.P(e[1], e[2])[1])
        for e in lijst:
            if e[0] == "boom":
                self.teken_boom(d, e[1], e[2])
            elif e[0] == "huis":
                self.teken_huis(d, e[3])
            elif e[0] == "ding":
                self.teken_ding(d, e[3])
            else:
                self.teken_fietser(d)
        for p in self.papieren:
            x, y = self.P(p["u"], p["v"], 0)
            pygame.draw.ellipse(d, (40, 70, 40), (x - 8, y - 3, 16, 6))
            self.teken_krantje(d, self.P(p["u"], p["v"], p["h"]), p["draai"], True)
        for pp in self.popups:
            x, y = self.P(pp["u"], pp["v"], pp["h"])
            tekst(d, pp["t"], 24, (20, 16, 28), (x + 2, y + 2), mid=True)
            tekst(d, pp["t"], 24, pp["kl"], (x, y), mid=True)
        if self.melding_t:
            r = tekst(d, self.melding, 34, GOUD, (W // 2, 140), mid=True)

    def teken_krantje(d_self, d, pos, draai, vliegt):
        x, y = pos
        c, s = math.cos(draai), math.sin(draai)
        lang = 14
        a = (x - c * lang, y - s * lang * 0.6)
        b = (x + c * lang, y + s * lang * 0.6)
        pygame.draw.line(d, (235, 235, 225), a, b, 9)
        pygame.draw.line(d, (150, 150, 150), a, b, 2)
        pygame.draw.circle(d, (200, 60, 60), (int(x), int(y)), 3)

    def teken_boom(self, d, u, v):
        x, y = self.P(u, v)
        pygame.draw.ellipse(d, (60, 100, 55), (x - 34, y - 8, 68, 18))
        pygame.draw.rect(d, (110, 75, 45), (x - 6, y - 50, 12, 52))
        for dx, dy, r in ((0, -95, 42), (-26, -70, 32), (26, -72, 32), (0, -125, 28)):
            pygame.draw.circle(d, (50, 120, 60), (int(x + dx), int(y + dy)), r)
            pygame.draw.circle(d, (70, 145, 72), (int(x + dx - 8), int(y + dy - 8)), r // 2)

    def teken_huis(self, d, h):
        u0, u1, v0, v1, hh = h.u, h.u + HUIS_L, HUIS_V0, HUIS_V1, HUIS_H
        top = hh + 70
        vm = (v0 + v1) / 2
        donker = tuple(int(c * 0.72) for c in h.muur)
        dakd = tuple(int(c * 0.75) for c in h.dak)
        # pad naar de deur en mat
        self.quad(d, [(u0 + 110, v1, 0), (u0 + 150, v1, 0), (u0 + 150, STOEP_V0, 0), (u0 + 110, STOEP_V0, 0)], (200, 186, 160))
        self.quad(d, [(h.mat[0], v1 + 2, 0), (h.mat[1], v1 + 2, 0), (h.mat[1], v1 + 30, 0), (h.mat[0], v1 + 30, 0)],
                  (150, 90, 50) if not (h.abo and h.bezorgd) else (230, 200, 120))
        self.quad(d, [(u0, v0, hh), (u1, v0, hh), (u1, vm, top), (u0, vm, top)], dakd)                 # achterdak
        self.quad(d, [(u0, v0, 0), (u0, v1, 0), (u0, v1, hh), (u0, v0, hh)], donker, (60, 50, 50))       # zijmuur
        self.quad(d, [(u0, v1, 0), (u1, v1, 0), (u1, v1, hh), (u0, v1, hh)], h.muur, (70, 60, 60))       # voorgevel
        pygame.draw.polygon(d, donker, [self.P(u0, v0, hh), self.P(u0, v1, hh), self.P(u0, vm, top)])
        pygame.draw.polygon(d, (60, 50, 50), [self.P(u0, v0, hh), self.P(u0, v1, hh), self.P(u0, vm, top)], 2)
        self.quad(d, [(u0, v1, hh), (u1, v1, hh), (u1, vm, top), (u0, vm, top)], h.dak, (50, 40, 40))   # voordak
        # schoorsteen
        self.quad(d, [(u1 - 60, vm + 20, top - 20), (u1 - 30, vm + 20, top - 20), (u1 - 30, vm + 20, top + 22), (u1 - 60, vm + 20, top + 22)], (130, 70, 60))
        # ramen
        for i, (a, b) in enumerate(((30, 85), (190, 250))):
            kl = (90, 130, 170) if not h.ruiten[i] else (40, 40, 50)
            self.quad(d, [(u0 + a, v1, 48), (u0 + b, v1, 48), (u0 + b, v1, 100), (u0 + a, v1, 100)], kl, (240, 236, 226))
            if h.ruiten[i]:
                m = self.P(u0 + (a + b) / 2, v1, 74)
                for k in range(5):
                    ang = k * 1.25
                    pygame.draw.line(d, (220, 230, 240), m, (m[0] + math.cos(ang) * 16, m[1] + math.sin(ang) * 14), 2)
            else:
                pygame.draw.line(d, (240, 236, 226), self.P(u0 + (a + b) / 2, v1, 48), self.P(u0 + (a + b) / 2, v1, 100), 2)
        # deur
        self.quad(d, [(u0 + 112, v1, 0), (u0 + 148, v1, 0), (u0 + 148, v1, 76), (u0 + 112, v1, 76)], (110, 60, 40), (60, 30, 20))
        x, y = self.P(u0 + 142, v1, 38)
        pygame.draw.circle(d, GOUD, (int(x), int(y)), 3)
        # huisnummer
        x, y = self.P(u0 + 130, v1, 90)
        tekst(d, str(h.nr), 16, (40, 30, 30), (x, y), mid=True)
        # hulp: goud pijltje boven een abonnee die nog moet
        if h.abo and not h.bezorgd and not h.schade and self.app_hulp():
            x, y = self.P(u0 + HUIS_L / 2, v1, top + 40)
            bob = math.sin(self.tik * 0.12) * 5
            pygame.draw.polygon(d, GOUD, [(x - 14, y - 20 + bob), (x + 14, y - 20 + bob), (x, y + bob)])

    def app_hulp(self):
        return bool(getattr(self.app, "hulp", True))

    def teken_ding(self, d, x):
        X, Y = self.P(x.u, x.v)
        s = x.soort
        t = x.t
        if s == "bus":
            h = self.huis_bij(x.u)
            abo = h is not None and h.abo
            pygame.draw.ellipse(d, (60, 100, 55), (X - 12, Y - 4, 24, 9))
            pygame.draw.rect(d, (90, 70, 50), (X - 3, Y - 40, 6, 40))
            kl = (60, 60, 70) if not (h and h.bezorgd and abo) else (60, 90, 60)
            pygame.draw.rect(d, kl, (X - 14, Y - 58, 28, 20), border_radius=7)
            pygame.draw.rect(d, (20, 20, 26), (X - 14, Y - 58, 28, 20), 2, border_radius=7)
            if abo:
                if self.app_hulp():
                    g = 120 + int(60 * math.sin(self.tik * 0.15))
                    pygame.draw.circle(d, (255, 215, 90, g), (X, Y - 48), 22, 3)
                pygame.draw.line(d, (40, 30, 20), (X + 12, Y - 56), (X + 12, Y - 80), 3)
                pygame.draw.polygon(d, GOUD if not (h and h.bezorgd) else GROEN, [(X + 12, Y - 80), (X + 30, Y - 74), (X + 12, Y - 68)])
        elif s == "heg":
            a = self.P(x.u - 12, -280)
            b = self.P(x.u + 12, -280)
            c = self.P(x.u + 12, -120)
            e = self.P(x.u - 12, -120)
            hh = 34
            pygame.draw.polygon(d, (40, 95, 45), [a, b, c, e])
            pygame.draw.polygon(d, (55, 125, 58), [(a[0], a[1] - hh), (b[0], b[1] - hh), (c[0], c[1] - hh), (e[0], e[1] - hh)])
            pygame.draw.polygon(d, (45, 108, 50), [e, c, (c[0], c[1] - hh), (e[0], e[1] - hh)])
            for k in range(6):
                p = self.P(x.u, -275 + k * 30, hh + 4)
                pygame.draw.circle(d, (70, 145, 70), (int(p[0]), int(p[1])), 7)
        elif s == "hond":
            ren = math.sin(t * (18 if x.actief else 3))
            pygame.draw.ellipse(d, (40, 70, 40), (X - 22, Y - 5, 44, 12))
            pygame.draw.ellipse(d, (95, 90, 95), (X - 22, Y - 34, 40, 22))
            for k, dx in enumerate((-16, -8, 6, 14)):
                o = ren * 5 * (1 if k % 2 else -1)
                pygame.draw.line(d, (75, 70, 75), (X + dx, Y - 16), (X + dx + o, Y - 2), 5)
            pygame.draw.circle(d, (105, 100, 105), (X + 18, Y - 38), 12)
            pygame.draw.polygon(d, (70, 65, 70), [(X + 12, Y - 46), (X + 16, Y - 60), (X + 22, Y - 46)])
            pygame.draw.ellipse(d, (60, 55, 60), (X + 24, Y - 38, 12, 8))
            pygame.draw.circle(d, (250, 230, 90) if x.actief else (30, 30, 30), (X + 20, Y - 41), 3)
            pygame.draw.line(d, (95, 90, 95), (X - 20, Y - 28), (X - 32, Y - 40 + ren * 6), 4)
            if x.actief and (self.tik // 20) % 2 == 0:
                tekst(d, "WAF!", 18, (255, 240, 200), (X + 10, Y - 80), mid=True)
        elif s == "kira":
            kw = math.sin(t * 14)
            pygame.draw.ellipse(d, (90, 90, 80), (X - 24, Y - 4, 48, 12))
            pygame.draw.ellipse(d, (205, 120, 60), (X - 20, Y - 36, 36, 22))
            pygame.draw.ellipse(d, (245, 235, 220), (X + 4, Y - 30, 12, 14))
            for dx in (-14, -6, 6, 12):
                pygame.draw.line(d, (190, 110, 55), (X + dx, Y - 18), (X + dx, Y - 1), 4)
            pygame.draw.line(d, (205, 120, 60), (X + 12, Y - 30), (X + 18, Y - 50), 8)
            pygame.draw.ellipse(d, (210, 125, 62), (X + 10, Y - 62, 26, 14))
            pygame.draw.polygon(d, (205, 120, 60), [(X + 14, Y - 58), (X + 12, Y - 86), (X + 22, Y - 60)])
            pygame.draw.polygon(d, (205, 120, 60), [(X + 22, Y - 58), (X + 26, Y - 86), (X + 30, Y - 60)])
            pygame.draw.polygon(d, (240, 170, 150), [(X + 15, Y - 62), (X + 14, Y - 80), (X + 20, Y - 62)])
            pygame.draw.circle(d, (40, 30, 20), (X + 28, Y - 57), 2)
            pygame.draw.circle(d, (40, 30, 20), (X + 36, Y - 55), 3)
            pygame.draw.line(d, (205, 120, 60), (X - 18, Y - 30), (X - 30 + kw * 8, Y - 46), 4)
            tekst(d, "Kira", 16, (255, 230, 200), (X + 4, Y - 104), mid=True)
            if x.raak:
                pygame.draw.circle(d, (240, 90, 110), (X + 20, Y - 100), 6)
                pygame.draw.circle(d, (240, 90, 110), (X + 30, Y - 100), 6)
                pygame.draw.polygon(d, (240, 90, 110), [(X + 14, Y - 98), (X + 36, Y - 98), (X + 25, Y - 86)])
        elif s == "maaier":
            pygame.draw.ellipse(d, (50, 90, 45), (X - 26, Y - 6, 52, 14))
            pygame.draw.rect(d, (200, 50, 45), (X - 20, Y - 24, 36, 18), border_radius=5)
            pygame.draw.circle(d, (30, 30, 30), (X - 14, Y - 4), 6)
            pygame.draw.circle(d, (30, 30, 30), (X + 12, Y - 4), 6)
            pygame.draw.line(d, (60, 60, 60), (X + 14, Y - 22), (X + 34, Y - 52), 3)
            # meneer erachter
            pygame.draw.rect(d, (60, 120, 170), (X + 30, Y - 72, 16, 30), border_radius=5)
            pygame.draw.circle(d, (230, 195, 160), (X + 38, Y - 82), 9)
            pygame.draw.line(d, (50, 50, 80), (X + 34, Y - 44), (X + 32, Y - 22), 5)
            pygame.draw.line(d, (50, 50, 80), (X + 42, Y - 44), (X + 46, Y - 22), 5)
            if (self.tik // 6) % 2:
                for k in range(3):
                    pygame.draw.circle(d, (130, 200, 110), (X - 26 - k * 7, Y - 14 - k * 4), 2)
        elif s == "skater":
            sw = math.sin(t * 6) * 4
            pygame.draw.ellipse(d, (55, 55, 62), (X - 18, Y - 4, 36, 10))
            pygame.draw.rect(d, (230, 140, 40), (X - 18, Y - 10, 36, 6), border_radius=3)
            for dx in (-12, 12):
                pygame.draw.circle(d, (30, 30, 30), (X + dx, Y - 3), 3)
            pygame.draw.line(d, (40, 40, 90), (X - 6, Y - 10), (X - 4 + sw, Y - 34), 5)
            pygame.draw.line(d, (40, 40, 90), (X + 6, Y - 10), (X + 4 - sw, Y - 34), 5)
            pygame.draw.rect(d, (190, 60, 150), (X - 9, Y - 62, 18, 30), border_radius=5)
            pygame.draw.line(d, (190, 60, 150), (X - 8, Y - 56), (X - 24, Y - 44 + sw), 4)
            pygame.draw.line(d, (190, 60, 150), (X + 8, Y - 56), (X + 24, Y - 44 - sw), 4)
            pygame.draw.circle(d, (200, 150, 110), (X, Y - 72), 9)
            pygame.draw.arc(d, (40, 40, 40), (X - 10, Y - 84, 20, 16), 0, 3.14, 4)
        elif s == "auto":
            l, b, hh = 110, 150, 40
            u0, v0 = x.u - l / 2, x.v - b / 2
            pygame.draw.polygon(d, (40, 40, 46), [self.P(u0 - 4, v0 + 8), self.P(u0 + l + 6, v0 + 8), self.P(u0 + l + 6, v0 + b + 8), self.P(u0 - 4, v0 + b + 8)])
            kl, dk = (60, 110, 190), (40, 80, 150)
            self.quad(d, [(u0, v0, 0), (u0, v0 + b, 0), (u0, v0 + b, hh), (u0, v0, hh)], dk)
            self.quad(d, [(u0, v0 + b, 0), (u0 + l, v0 + b, 0), (u0 + l, v0 + b, hh), (u0, v0 + b, hh)], kl)
            self.quad(d, [(u0, v0, hh), (u0 + l, v0, hh), (u0 + l, v0 + b, hh), (u0, v0 + b, hh)], (80, 130, 210))
            self.quad(d, [(u0 + 10, v0 + 25, hh), (u0 + l - 10, v0 + 25, hh), (u0 + l - 10, v0 + b - 35, hh + 30), (u0 + 10, v0 + b - 35, hh + 30)], (150, 190, 230), (40, 60, 90))
            for wu, wv in ((u0 + 20, v0 + b), (u0 + l - 20, v0 + b)):
                p = self.P(wu, wv, 6)
                pygame.draw.circle(d, (25, 25, 25), (int(p[0]), int(p[1])), 10)
            p = self.P(u0, v0 + b - 10, 22)
            pygame.draw.circle(d, (250, 240, 180), (int(p[0]), int(p[1])), 5)
            if x.actief and (self.tik // 15) % 2 == 0 and x.v < 200:
                tekst(d, "TOET!", 18, (255, 240, 200), self.P(x.u, x.v, 110), mid=True)
        elif s == "put":
            pygame.draw.ellipse(d, (40, 40, 44), (X - 24, Y - 9, 48, 18))
            for k in range(-2, 3):
                pygame.draw.line(d, (90, 90, 96), (X + k * 8 - 4, Y - 6), (X + k * 8 + 4, Y + 6), 2)
        elif s == "kraan":
            pygame.draw.ellipse(d, (120, 116, 106), (X - 12, Y - 4, 24, 9))
            pygame.draw.rect(d, (210, 45, 45), (X - 8, Y - 38, 16, 36), border_radius=4)
            pygame.draw.rect(d, (230, 70, 60), (X - 13, Y - 28, 26, 8), border_radius=3)
            pygame.draw.circle(d, (230, 70, 60), (X, Y - 40), 9)
        elif s == "stapel":
            pygame.draw.ellipse(d, (120, 116, 106), (X - 22, Y - 5, 44, 12))
            for k in range(4):
                pygame.draw.rect(d, (240, 240, 232), (X - 18, Y - 10 - k * 7, 36, 8), border_radius=2)
                pygame.draw.line(d, (150, 150, 150), (X - 14, Y - 6 - k * 7), (X + 14, Y - 6 - k * 7), 1)
            pygame.draw.line(d, (200, 60, 60), (X, Y - 38), (X, Y - 2), 2)
        elif s == "doel":
            pygame.draw.ellipse(d, (60, 100, 55), (X - 14, Y - 4, 28, 9))
            pygame.draw.rect(d, (110, 90, 60), (X - 3, Y - 50, 6, 50))
            for r, kl in ((24, (240, 240, 240)), (18, (210, 50, 50)), (12, (240, 240, 240)), (6, (210, 50, 50))):
                pygame.draw.circle(d, kl if not x.raak else (90, 160, 90), (X, Y - 74), r)
        elif s == "kegel":
            pygame.draw.polygon(d, (240, 130, 30), [(X - 14, Y), (X + 14, Y), (X, Y - 36)])
            pygame.draw.line(d, (250, 250, 250), (X - 8, Y - 14), (X + 8, Y - 14), 4)
        elif s == "finish":
            a, b = self.P(x.u, WEG_V0), self.P(x.u, WEG_V1)
            for p in (a, b):
                pygame.draw.rect(d, (90, 80, 70), (p[0] - 4, p[1] - 110, 8, 110))
            pygame.draw.polygon(d, (250, 250, 250), [(a[0], a[1] - 110), (b[0], b[1] - 110), (b[0], b[1] - 80), (a[0], a[1] - 80)])
            m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 95)
            tekst(d, "FINISH", 22, (40, 30, 30), m, mid=True)

    def teken_fietser(self, d):
        X, Y = self.P(self.pu, self.pv)
        fx, fy = 0.84, -0.54
        trap = self.pu * 0.08
        if self.val:
            # gevallen: fiets op zijn kant, bezorger ernaast
            pygame.draw.ellipse(d, (40, 70, 40), (X - 30, Y - 6, 60, 14))
            pygame.draw.ellipse(d, (30, 30, 30), (X - 34, Y - 10, 26, 12), 3)
            pygame.draw.ellipse(d, (30, 30, 30), (X + 6, Y - 10, 26, 12), 3)
            pygame.draw.line(d, (200, 60, 70), (X - 20, Y - 4), (X + 20, Y - 4), 4)
            pygame.draw.rect(d, (70, 110, 200), (X + 24, Y - 18, 30, 14), border_radius=5)
            pygame.draw.circle(d, (235, 195, 160), (X + 60, Y - 12), 9)
            for k in range(3):
                a = self.tik * 0.15 + k * 2.1
                pygame.draw.circle(d, GOUD, (int(X + 50 + math.cos(a) * 18), int(Y - 36 + math.sin(a) * 6)), 4)
            return
        pygame.draw.ellipse(d, (40, 40, 40, 90), (X - 30, Y - 6, 60, 14))
        wa = (X - fx * 22, Y - fy * 22 - 14)
        wb = (X + fx * 22, Y + fy * 22 - 14)
        for w in (wa, wb):
            pygame.draw.ellipse(d, (25, 25, 25), (w[0] - 13, w[1] - 13, 26, 26), 4)
            pygame.draw.circle(d, (170, 170, 175), (int(w[0]), int(w[1])), 3)
        zadel = (X - fx * 6, Y - fy * 6 - 36)
        stuur = (X + fx * 18, Y + fy * 18 - 44)
        trapas = (X, Y - 16)
        kl = (200, 60, 70)
        pygame.draw.line(d, kl, wa, trapas, 4)
        pygame.draw.line(d, kl, trapas, zadel, 4)
        pygame.draw.line(d, kl, zadel, stuur, 4)
        pygame.draw.line(d, kl, stuur, wb, 4)
        pygame.draw.line(d, kl, wa, zadel, 3)
        # benen die trappen
        for k in (0, math.pi):
            vx, vy = trapas[0] + math.cos(trap + k) * 8, trapas[1] + math.sin(trap + k) * 8
            knie = ((zadel[0] + vx) / 2 + fx * 10, (zadel[1] + vy) / 2 - 4)
            pygame.draw.line(d, (50, 60, 110), zadel, knie, 6)
            pygame.draw.line(d, (50, 60, 110), knie, (vx, vy), 5)
            pygame.draw.circle(d, (30, 30, 30), (int(vx), int(vy)), 4)
        # lijf, tas met kranten, hoofd en pet
        rug = (zadel[0] + fx * 6, zadel[1] - 30)
        pygame.draw.line(d, (70, 110, 200), zadel, rug, 12)
        pygame.draw.line(d, (70, 110, 200), rug, stuur, 5)
        tas = pygame.Rect(0, 0, 22, 18)
        tas.center = (zadel[0] - 10, zadel[1] - 10)
        pygame.draw.rect(d, (150, 100, 50), tas, border_radius=4)
        for k in range(min(3, self.kranten)):
            pygame.draw.rect(d, (240, 240, 230), (tas.x + 3 + k * 6, tas.y - 6, 5, 8))
        hoofd = (int(rug[0] + fx * 4), int(rug[1] - 12))
        pygame.draw.circle(d, (235, 195, 160), hoofd, 10)
        pygame.draw.circle(d, (200, 50, 60), (hoofd[0], hoofd[1] - 4), 10, draw_top_left=True, draw_top_right=True)
        pygame.draw.line(d, (200, 50, 60), (hoofd[0], hoofd[1] - 4), (hoofd[0] + 14, hoofd[1] - 8), 4)
        pygame.draw.circle(d, (30, 30, 30), (hoofd[0] + 5, hoofd[1]), 2)

    def teken_hud(self, d):
        pygame.draw.rect(d, (22, 19, 31), (0, 0, W, 62))
        pygame.draw.line(d, RAND, (0, 62), (W, 62), 2)
        dag = T("dagen")[min(6, self.dag)]
        tekst(d, dag, 30, ACCENT, (20, 12))
        tekst(d, "%s %d" % (T("punten"), self.punten), 30, GOUD, (240, 12))
        # kranten
        tekst(d, T("kranten"), 22, ZACHT, (520, 18), vet=False)
        for k in range(min(20, self.kranten)):
            x = 618 + (k % 10) * 15
            y = 14 + (k // 10) * 18
            pygame.draw.rect(d, (240, 240, 230), (x, y, 11, 15), border_radius=2)
            pygame.draw.line(d, (200, 60, 60), (x, y + 7), (x + 11, y + 7), 2)
        # levens
        tekst(d, T("levens"), 22, ZACHT, (790, 18), vet=False)
        for k in range(self.levens):
            x, y = 895 + k * 28, 31
            pygame.draw.circle(d, ROOD, (x - 5, y - 4), 7)
            pygame.draw.circle(d, ROOD, (x + 5, y - 4), 7)
            pygame.draw.polygon(d, ROOD, [(x - 12, y - 1), (x + 12, y - 1), (x, y + 12)])
        tekst(d, "%s %d" % (T("abo"), sum(self.abo)), 26, TEKST, (W - 20, 15), rechts=True)
        if self.fase == "rijden":
            tekst(d, T("toetsen"), 15, (235, 240, 225), (W // 2 + 1, H - 15), mid=True, vet=False)

    def teken_ochtend(self, d, muis):
        self.donker(d, 170)
        dag = T("dagen")[self.dag]
        tekst(d, dag.upper(), 72, GOUD, (W // 2, 150), mid=True)
        tekst(d, T("ochtend_uitleg"), 26, TEKST, (W // 2, 230), mid=True, vet=False)
        # straatkaartje
        n = len(self.huizen)
        bw = 60
        x0 = W // 2 - (n * (bw + 8)) // 2
        for i, h in enumerate(self.huizen):
            r = pygame.Rect(x0 + i * (bw + 8), 300, bw, 64)
            pygame.draw.rect(d, h.muur if h.abo else (70, 66, 80), r, border_radius=6)
            pygame.draw.polygon(d, h.dak if h.abo else (50, 46, 60), [(r.x - 4, r.y), (r.right + 4, r.y), (r.centerx, r.y - 26)])
            if h.abo:
                pygame.draw.polygon(d, GOUD, [(r.right - 14, r.bottom - 30), (r.right - 2, r.bottom - 25), (r.right - 14, r.bottom - 20)])
            tekst(d, str(h.nr), 20, (30, 24, 36), r.center, mid=True)
        tekst(d, "%s: %d  ·  %s: %d  ·  %s: %s" % (T("abo"), sum(self.abo), T("levens"), self.levens,
                                                  "Niveau" if taal() == "nl" else "Level", T("niveau")[self.niveau - 1]),
              26, ZACHT, (W // 2, 410), mid=True)
        self.knoppen.append(Knop((W // 2 - 200, 470, 400, 80), T("spatie_fiets").split("=")[1].strip().rstrip("!").capitalize() + "!",
                                 self.start_dag, GROEN, 32))
        tekst(d, T("spatie_fiets"), 22, ZACHT, (W // 2, 575), mid=True, vet=False)
        self.knoppen.append(Knop((40, H - 90, 200, 60), T("menu"), self.naar_titel, VAK, 24))

    def teken_avond(self, d, muis):
        self.donker(d, 190)
        dag = T("dagen")[self.dag].lower() if taal() == "nl" else T("dagen")[self.dag]
        tekst(d, T("avond") % dag, 56, GOUD, (W // 2, 150), mid=True)
        y = 240
        for regel in self.verslag:
            for stuk in knip(regel, 30, 1000):
                tekst(d, stuk, 30, TEKST, (W // 2, y), mid=True)
                y += 42
        tekst(d, "%s: %d" % (T("punten"), self.punten), 40, GOUD, (W // 2, y + 30), mid=True)
        self.knoppen.append(Knop((W // 2 - 200, 560, 400, 80), T("volgende"), self.volgende_dag, GROEN, 32))

    def teken_einde(self, d, muis):
        self.donker(d, 200)
        y = 120
        for regel in self.verslag[-3:] if self.verslag else []:
            for stuk in knip(regel, 30, 1000):
                tekst(d, stuk, 30, TEKST, (W // 2, y), mid=True)
                y += 40
        if self.levens <= 0:
            tekst(d, T("op"), 34, ROOD, (W // 2, y + 10), mid=True)
            y += 50
        tekst(d, "%s: %d" % (T("punten"), self.punten), 54, GOUD, (W // 2, y + 40), mid=True)
        self.teken_scores(d, y + 110)
        self.knoppen.append(Knop((W // 2 - 320, 640, 300, 76), T("opnieuw"), self.nieuw_potje, GROEN, 30))
        self.knoppen.append(Knop((W // 2 + 20, 640, 300, 76), T("menu"), self.naar_titel, VAK, 30))

    def teken_scores(self, d, y):
        tekst(d, T("scores"), 28, ACCENT, (W // 2, y), mid=True)
        for i, s in enumerate(self.scores[:5]):
            t = "%d.  %d  -  %s  (%s)" % (i + 1, s["punten"], s.get("datum", ""), T("niveau")[max(0, min(2, s.get("niveau", 2) - 1))])
            tekst(d, t, 24, TEKST, (W // 2, y + 40 + i * 32), mid=True, vet=False)

    def teken_titel(self, d, muis):
        d.fill(ACHTER)
        # een stukje straat als plaatje
        tekst(d, T("bez"), 64, ACCENT, (W // 2, 70), mid=True)
        tekst(d, T("bez_sub"), 28, ZACHT, (W // 2, 128), mid=True, vet=False)
        self.teken_logo(d, W // 2, 330)
        for i in range(3):
            kl = GOUD if self.niveau == i + 1 else VAK
            self.knoppen.append(Knop((W // 2 - 330 + i * 225, 440, 210, 60), T("niveau")[i],
                                     lambda n=i + 1: setattr(self, "niveau", n), kl, 26))
        self.knoppen.append(Knop((W // 2 - 220, 520, 440, 80), T("begin"), self.nieuw_potje, GROEN, 34))
        self.knoppen.append(Knop((W // 2 - 330, 620, 210, 60), T("uitleg"), self.wil_uitleg, VAK, 24))
        hulp = self.app_hulp()
        self.knoppen.append(Knop((W // 2 - 105, 620, 210, 60), "%s: %s" % (T("hulp"), T("aan") if hulp else T("uitm")),
                                 self.wissel_hulp, GOUD if hulp else VAK, 22))
        self.knoppen.append(Knop((W // 2 + 120, 620, 210, 60), T("menu") if UI is not None else T("stoppen"), self.terug, VAK, 24))
        if self.scores:
            tekst(d, "%s: %d" % (T("beste"), self.scores[0]["punten"]), 24, GOUD, (W // 2, 712), mid=True)
        if UI is None:
            self.knoppen.append(Knop((W - 300, H - 70, 270, 50), T("doneer"), self.doneer, GOUD, 20))
            tekst(d, "v" + VERSIE + "  ·  M = muziek" if taal() == "nl" else "v" + VERSIE + "  ·  M = music", 16, ZACHT, (30, H - 30), vet=False)

    def teken_logo(self, d, cx, cy):
        """Bezorger op de fiets met een vliegende krant (groot, voor het titelscherm)."""
        pygame.draw.ellipse(d, VAK, (cx - 240, cy + 40, 480, 50))
        oud = (self.pu, self.pv, getattr(self, "cam", 0))
        self.pu, self.pv = 0, 0
        self.cam = 0
        s = pygame.Surface((200, 140), pygame.SRCALPHA)
        global X0, Y0
        x0, y0 = X0, Y0
        X0, Y0 = 100, 120
        self.teken_fietser(s)
        X0, Y0 = x0, y0
        s = pygame.transform.smoothscale(s, (400, 280))
        d.blit(s, (cx - 210, cy - 210))
        self.pu, self.pv, self.cam = oud
        a = self.tik * 0.08
        self.teken_krantje(d, (cx + 200 + math.cos(a) * 20, cy - 120 + math.sin(a * 2) * 10), a * 3, True)
        self.teken_krantje(d, (cx - 230, cy - 60 + math.sin(a) * 8), a * 2 + 1, True)

    def wissel_hulp(self):
        if hasattr(self.app, "wissel_hulp"):
            self.app.wissel_hulp()

    def wil_uitleg(self):
        if UI is not None and hasattr(self.app, "toon_regels"):
            self.app.toon_regels = True
        else:
            self.toon_uitleg = True

    def doneer(self):
        try:
            import webbrowser
            webbrowser.open("https://paypal.me/roger076")
        except Exception:
            pass

    def teken_uitleg(self, d, muis):
        self.donker(d, 200)
        r = pygame.Rect(110, 50, W - 220, H - 100)
        pygame.draw.rect(d, VAK, r, border_radius=18)
        pygame.draw.rect(d, ACCENT, r, 3, border_radius=18)
        tekst(d, T("uitleg"), 40, ACCENT, (r.x + 40, r.y + 24))
        y = r.y + 90
        for regel in T("uitleg_tekst").split("\n"):
            for stuk in knip(regel, 22, r.w - 80):
                tekst(d, stuk, 22, TEKST, (r.x + 40, y), vet=False)
                y += 30
            y += 6
        self.knoppen.append(Knop((r.centerx - 100, r.bottom - 80, 200, 60), "OK", lambda: setattr(self, "toon_uitleg", False), GROEN, 26))

    def stop(self):
        self.klank.stop_muziek()


def menu_plaatje(d, cx, cy, aan=True):
    """Tegel in het menu van de Spellenkast: huisje, brievenbus met gouden vlag en een vliegende krant."""
    muur, dak = ((196, 150, 110), (150, 70, 60)) if aan else ((110, 104, 120), (80, 74, 92))
    pygame.draw.polygon(d, (96, 150, 80) if aan else (70, 80, 70), [(cx - 150, cy + 70), (cx + 150, cy + 70), (cx + 150, cy + 90), (cx - 150, cy + 90)])
    pygame.draw.rect(d, muur, (cx - 120, cy - 20, 120, 90))
    pygame.draw.polygon(d, dak, [(cx - 135, cy - 20), (cx + 15, cy - 20), (cx - 60, cy - 75)])
    pygame.draw.rect(d, (90, 130, 170), (cx - 105, cy + 2, 30, 26))
    pygame.draw.rect(d, (110, 60, 40), (cx - 55, cy + 20, 26, 50))
    pygame.draw.rect(d, (90, 70, 50), (cx + 50, cy + 20, 6, 50))
    pygame.draw.rect(d, (60, 60, 70), (cx + 38, cy + 4, 30, 20), border_radius=7)
    pygame.draw.line(d, (40, 30, 20), (cx + 64, cy + 6), (cx + 64, cy - 20), 3)
    pygame.draw.polygon(d, GOUD, [(cx + 64, cy - 20), (cx + 84, cy - 14), (cx + 64, cy - 8)])
    for k, (x, y, a) in enumerate(((cx + 115, cy - 40, 0.5), (cx + 85, cy - 62, 2.2))):
        c, s = math.cos(a), math.sin(a)
        pygame.draw.line(d, (240, 240, 230), (x - c * 16, y - s * 10), (x + c * 16, y + s * 10), 10)
        pygame.draw.circle(d, (200, 60, 60), (x, y), 3)


# ------------------------------------------------------------------ los spelen (DraveBezorger.exe)
class LosApp:
    def __init__(self):
        pygame.mixer.pre_init(22050, -16, 1, 512)
        pygame.init()
        pygame.display.set_caption("DraveBezorger")
        try:
            pygame.display.set_icon(pygame.image.load(os.path.join(HERE, "assets", "icon.png")))
        except Exception:
            pass
        info = pygame.display.Info()
        sw, sh = info.current_w, info.current_h
        schaal = min(1.0, (sw - 80) / W, (sh - 120) / H)
        self.venster = pygame.display.set_mode((int(W * schaal), int(H * schaal)), pygame.RESIZABLE)
        self.d = pygame.Surface((W, H))
        self.klok = pygame.time.Clock()
        self.hulp = self.laad_hulp()
        self.weg = False
        self.spel = Bezorger(self, 2)

    def laad_hulp(self):
        try:
            with open(os.path.join(HERE, "DraveBezorger-data", "instellingen.json"), encoding="utf-8") as f:
                return bool(json.load(f).get("hulp", True))
        except Exception:
            return True

    def wissel_hulp(self):
        self.hulp = not self.hulp
        try:
            os.makedirs(os.path.join(HERE, "DraveBezorger-data"), exist_ok=True)
            with open(os.path.join(HERE, "DraveBezorger-data", "instellingen.json"), "w", encoding="utf-8") as f:
                json.dump({"hulp": self.hulp}, f)
        except Exception:
            pass

    def naar_menu(self):
        if self.spel.fase != "titel":
            self.spel.fase = "titel"
        else:
            self.weg = True

    def muis(self):
        mx, my = pygame.mouse.get_pos()
        vw, vh = self.venster.get_size()
        return int(mx * W / max(1, vw)), int(my * H / max(1, vh))

    def loop(self):
        while not self.weg:
            muis = self.muis()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                if e.type == pygame.VIDEORESIZE:
                    self.venster = pygame.display.set_mode((max(640, e.w), max(400, e.h)), pygame.RESIZABLE)
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE and self.spel.fase == "titel" and not self.spel.toon_uitleg:
                        return
                    self.spel.toets(e)
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    pos = self.muis()
                    if any(k.klik(pos) for k in list(self.spel.knoppen)):
                        continue
                    self.spel.klik(pos)
            self.spel.update()
            self.spel.teken(self.d, muis)
            pygame.transform.smoothscale(self.d, self.venster.get_size(), self.venster)
            pygame.display.flip()
            self.klok.tick(60)


def log_fout(t):
    try:
        m = os.path.join(HERE, "DraveBezorger-data")
        os.makedirs(m, exist_ok=True)
        with open(os.path.join(m, "error.log"), "a", encoding="utf-8") as f:
            f.write(time.strftime("%d-%m-%Y %H:%M:%S") + "\n" + t + "\n")
    except Exception:
        pass


if __name__ == "__main__":
    import traceback
    try:
        LosApp().loop()
    except Exception:
        log_fout(traceback.format_exc())
        raise
    finally:
        pygame.quit()
