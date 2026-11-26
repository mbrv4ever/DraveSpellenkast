# -*- coding: utf-8 -*-
"""DraveSpellenkast - Memory: draai twee kaartjes om en zoek de paren. Tegen de computer of online.
De plaatjes zijn zelf getekend. Copyright (C) 2026 Dravenlock (Roger & Claudio). GNU GPL v3.0."""
import math
import random
import time

import pygame

UI = None          # wordt door main.py gezet

NIVEAUS = {1: (4, 3), 2: (4, 4), 3: (6, 4)}      # kolommen x rijen: 6, 8 of 12 paren
ONLINE_NIVEAU = 2
TX = {
    "memo": ("Memory", "Memory"),
    "jouw_beurt": ("Jouw beurt: draai twee kaartjes om.", "Your turn: turn over two cards."),
    "nog_een": ("Nog één kaartje.", "One more card."),
    "paar": ("Een paar! Je mag nog een keer.", "A pair! Go again."),
    "geen_paar": ("Geen paar. Onthoud waar ze liggen!", "No pair. Remember where they are!"),
    "comp_beurt": ("De computer draait kaartjes om...", "The computer turns cards..."),
    "comp_paar": ("De computer vond een paar en mag nog een keer.", "The computer found a pair and goes again."),
    "gelijk": ("Gelijkspel! Evenveel paren.", "A draw! Same number of pairs."),
    "paren": ("Paren: %d", "Pairs: %d"),
    "potjes": ("Gewonnen potjes: %d - %d", "Games won: %d - %d"),
    "tip_memo": ("Tip: de twee gouden kaartjes zijn een paar!", "Tip: the two gold cards are a pair!"),
    "tip_niets": ("Tip: je weet nog geen paar. Draai een nieuw kaartje om.", "Tip: you know no pair yet. Turn a new card."),
    "toetsen_memo": ("Klik op een kaartje  ·  T = tip  ·  Esc = menu", "Click a card  ·  T = tip  ·  Esc = menu"),
}


def T(k):
    if k in TX:
        v = TX[k]
        return v[0] if UI.TAAL == "nl" else v[1]
    return UI.T(k)


# ------------------------------------------------------------------ de plaatjes (zelf getekend)
GEEL, ORANJE, ROOD, ROZE = (246, 206, 70), (240, 150, 60), (214, 72, 96), (236, 130, 170)
GROEN, DONKERGROEN, BLAUW, LICHTBLAUW = (90, 180, 100), (40, 120, 70), (70, 120, 220), (130, 190, 240)
BRUIN, WIT, ZWART, PAARS = (150, 100, 60), (245, 242, 235), (40, 32, 50), (150, 110, 220)


def ster(cx, cy, r1, r2, n=5, draai=-math.pi / 2):
    pts = []
    for i in range(n * 2):
        r = r1 if i % 2 == 0 else r2
        a = draai + i * math.pi / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def teken_plaatje(d, nr, r):
    """Teken plaatje nr midden in rechthoek r."""
    cx, cy = r.center
    s = min(r.w, r.h) / 100.0
    def P(x, y):
        return (cx + x * s, cy + y * s)
    def S(v):
        return max(1, int(v * s))
    if nr == 0:                                    # zon
        for i in range(12):
            a = i * math.pi / 6
            pygame.draw.line(d, ORANJE, P(26 * math.cos(a), 26 * math.sin(a)), P(40 * math.cos(a), 40 * math.sin(a)), S(5))
        pygame.draw.circle(d, GEEL, P(0, 0), S(22))
    elif nr == 1:                                  # maan
        pygame.draw.circle(d, GEEL, P(0, 0), S(32))
        pygame.draw.circle(d, (44, 38, 70), P(14, -8), S(28))
    elif nr == 2:                                  # ster
        pygame.draw.polygon(d, GEEL, [P(x, y) for x, y in ster(0, 2, 38, 16)])
    elif nr == 3:                                  # hart
        pygame.draw.circle(d, ROOD, P(-15, -10), S(18))
        pygame.draw.circle(d, ROOD, P(15, -10), S(18))
        pygame.draw.polygon(d, ROOD, [P(-32, -4), P(32, -4), P(0, 34)])
    elif nr == 4:                                  # boom
        pygame.draw.rect(d, BRUIN, (*P(-7, 10), S(14), S(28)))
        pygame.draw.circle(d, GROEN, P(0, -8), S(26))
        pygame.draw.circle(d, DONKERGROEN, P(-14, 0), S(14))
        pygame.draw.circle(d, DONKERGROEN, P(12, -18), S(10))
    elif nr == 5:                                  # bloem
        pygame.draw.line(d, GROEN, P(0, 6), P(0, 40), S(5))
        for i in range(6):
            a = i * math.pi / 3
            pygame.draw.circle(d, ROZE, P(16 * math.cos(a), -10 + 16 * math.sin(a)), S(11))
        pygame.draw.circle(d, GEEL, P(0, -10), S(10))
    elif nr == 6:                                  # huisje
        pygame.draw.rect(d, WIT, (*P(-26, -4), S(52), S(40)))
        pygame.draw.polygon(d, ROOD, [P(-34, -2), P(34, -2), P(0, -36)])
        pygame.draw.rect(d, BRUIN, (*P(-7, 14), S(14), S(22)))
        pygame.draw.rect(d, LICHTBLAUW, (*P(10, 4), S(10), S(10)))
    elif nr == 7:                                  # vis
        pygame.draw.ellipse(d, ORANJE, (*P(-30, -16), S(48), S(32)))
        pygame.draw.polygon(d, ORANJE, [P(14, 0), P(36, -18), P(36, 18)])
        pygame.draw.circle(d, ZWART, P(-16, -4), S(4))
    elif nr == 8:                                  # kat
        pygame.draw.polygon(d, (160, 160, 170), [P(-28, -10), P(-24, -38), P(-6, -22)])
        pygame.draw.polygon(d, (160, 160, 170), [P(28, -10), P(24, -38), P(6, -22)])
        pygame.draw.circle(d, (160, 160, 170), P(0, 4), S(30))
        pygame.draw.circle(d, GROEN, P(-11, -2), S(5))
        pygame.draw.circle(d, GROEN, P(11, -2), S(5))
        pygame.draw.polygon(d, ROZE, [P(-4, 8), P(4, 8), P(0, 13)])
        for k in (-1, 1):
            pygame.draw.line(d, ZWART, P(8 * k, 14), P(30 * k, 10), S(2))
            pygame.draw.line(d, ZWART, P(8 * k, 16), P(30 * k, 20), S(2))
    elif nr == 9:                                  # hond
        pygame.draw.ellipse(d, BRUIN, (*P(-36, -24), S(16), S(40)))
        pygame.draw.ellipse(d, BRUIN, (*P(20, -24), S(16), S(40)))
        pygame.draw.circle(d, (214, 170, 110), P(0, 0), S(28))
        pygame.draw.circle(d, ZWART, P(-10, -6), S(4))
        pygame.draw.circle(d, ZWART, P(10, -6), S(4))
        pygame.draw.ellipse(d, ZWART, (*P(-7, 6), S(14), S(10)))
        pygame.draw.arc(d, ZWART, (*P(-10, 8), S(20), S(14)), math.pi * 1.1, math.pi * 1.9, S(2))
    elif nr == 10:                                 # bootje
        pygame.draw.polygon(d, BRUIN, [P(-36, 12), P(36, 12), P(24, 30), P(-24, 30)])
        pygame.draw.line(d, BRUIN, P(0, 12), P(0, -36), S(4))
        pygame.draw.polygon(d, WIT, [P(3, -34), P(3, 6), P(30, 6)])
        pygame.draw.polygon(d, ROOD, [P(-3, -28), P(-3, 6), P(-24, 6)])
    elif nr == 11:                                 # paddenstoel
        pygame.draw.rect(d, WIT, (*P(-10, 0), S(20), S(32)))
        pygame.draw.ellipse(d, ROOD, (*P(-36, -30), S(72), S(40)))
        pygame.draw.rect(d, (44, 38, 70), (*P(-38, -4), S(76), S(8)))
        for x, y in ((-18, -16), (6, -22), (18, -10)):
            pygame.draw.circle(d, WIT, P(x, y), S(5))
    elif nr == 12:                                 # appel
        pygame.draw.circle(d, ROOD, P(-9, 6), S(24))
        pygame.draw.circle(d, ROOD, P(9, 6), S(24))
        pygame.draw.line(d, BRUIN, P(0, -14), P(4, -30), S(4))
        pygame.draw.ellipse(d, GROEN, (*P(5, -32), S(18), S(10)))
    elif nr == 13:                                 # draakje (Dravenlock!)
        pygame.draw.ellipse(d, PAARS, (*P(-24, -10), S(46), S(34)))
        pygame.draw.circle(d, PAARS, P(18, -20), S(14))
        pygame.draw.polygon(d, (190, 160, 255), [P(-10, -6), P(-30, -36), P(4, -14)])
        pygame.draw.polygon(d, PAARS, [P(-22, 10), P(-40, 24), P(-20, 18)])
        pygame.draw.circle(d, GEEL, P(22, -24), S(4))
        pygame.draw.polygon(d, ORANJE, [P(30, -16), P(42, -20), P(42, -10)])
    else:                                          # regenboog
        for i, kl in enumerate((ROOD, ORANJE, GEEL, GROEN, BLAUW, PAARS)):
            rr = 36 - i * 5
            pygame.draw.arc(d, kl, (*P(-rr, 10 - rr), S(2 * rr), S(2 * rr)), 0, math.pi, S(5))


# ------------------------------------------------------------------ het spel
class Memory:
    def __init__(self, app, niveau):
        self.app = app
        self.niveau = niveau
        self.knoppen = []
        self.score_potjes = [0, 0]
        self.nieuw_potje()

    def naam(self, sp):
        return UI.T("jij") if sp == 0 else UI.T("computer")

    def schud(self, zaad=None):
        kol, rij = NIVEAUS[self.niveau]
        paren = kol * rij // 2
        rnd = random.Random(zaad)
        soorten = list(range(15))
        rnd.shuffle(soorten)
        kaarten = soorten[:paren] * 2
        rnd.shuffle(kaarten)
        return kaarten

    def nieuw_potje(self, zaad=None):
        self.kol, self.rij = NIVEAUS[self.niveau]
        self.kaarten = self.schud(zaad)
        self.open = []                              # omgedraaide kaartjes deze beurt
        self.weg = {}                               # index -> wie het paar vond
        self.paren = [0, 0]
        self.beurt = 0
        self.klaar = False
        self.uitslag = ""
        self.melding = ""
        self.dicht_om = None                        # tijdstip waarop de twee kaartjes weer dichtgaan
        self.geheugen = {}                          # wat de computer heeft gezien: index -> plaatje
        self.comp_t = time.time() + 0.8
        self.tip = None
        self.draai = {}                             # index -> starttijd van het omdraaien (animatie)

    # ---------- spelregels
    def kan_draaien(self, i):
        return (not self.klaar and self.dicht_om is None and i not in self.weg and i not in self.open and len(self.open) < 2)

    def draai_om(self, i):
        if not self.kan_draaien(i):
            return False
        self.open.append(i)
        self.draai[i] = time.time()
        self.tip = None
        self.geheugen[i] = self.kaarten[i]
        self.app.geluid.speel("klik")
        if len(self.open) == 2:
            a, b = self.open
            if self.kaarten[a] == self.kaarten[b]:
                self.weg[a] = self.weg[b] = self.beurt
                self.paren[self.beurt] += 1
                self.open = []
                self.app.geluid.speel("goed")
                self.melding = T("paar") if self.beurt == self.mijn_idx() else (T("comp_paar") if self.niveau_comp() else "")
                self.comp_t = time.time() + 1.0
                self.controleer_einde()
            else:
                self.dicht_om = time.time() + 1.3
                self.melding = T("geen_paar") if self.beurt == self.mijn_idx() else ""
        else:
            self.melding = T("nog_een") if self.beurt == self.mijn_idx() else ""
        return True

    def controleer_einde(self):
        if len(self.weg) < len(self.kaarten):
            return
        self.klaar = True
        if self.paren[0] == self.paren[1]:
            self.uitslag = T("gelijk")
            self.app.geluid.speel("klik")
        else:
            w = 0 if self.paren[0] > self.paren[1] else 1
            self.score_potjes[w] += 1
            self.uitslag = UI.T("wint") % self.naam(w)
            self.app.geluid.speel("win" if w == 0 else "verlies")

    def beurt_klaar(self):
        """Na een fout paar: kaartjes dicht, de ander is aan de beurt."""
        for i in self.open:
            self.draai[i] = time.time()
        self.open = []
        self.dicht_om = None
        self.beurt = 1 - self.beurt
        self.comp_t = time.time() + 0.9
        self.melding = ""

    # ---------- de computer (onthoudt goed, of minder goed)
    def comp_kies(self):
        vergeet = {1: 0.6, 2: 0.25, 3: 0.0}[self.niveau]
        gezien = {i: k for i, k in self.geheugen.items() if i not in self.weg and random.random() >= vergeet}
        dicht = [i for i in range(len(self.kaarten)) if i not in self.weg and i not in self.open]
        if not self.open:
            per = {}
            for i, k in gezien.items():
                per.setdefault(k, []).append(i)
            for k, lijst in per.items():
                if len(lijst) >= 2:
                    return lijst[0]
            onbekend = [i for i in dicht if i not in self.geheugen]
            return random.choice(onbekend or dicht)
        eerste = self.open[0]
        for i, k in gezien.items():
            if i != eerste and k == self.kaarten[eerste] and i in dicht:
                return i
        onbekend = [i for i in dicht if i not in self.geheugen]
        return random.choice(onbekend or dicht)

    def update(self):
        nu = time.time()
        if self.dicht_om is not None and nu >= self.dicht_om:
            self.beurt_klaar()
            return
        if self.klaar or self.beurt != 1 or self.dicht_om is not None:
            return
        if nu >= self.comp_t:
            self.draai_om(self.comp_kies())
            self.comp_t = nu + 0.9

    def geef_tip(self):
        if self.klaar or self.beurt != 0 or self.dicht_om is not None:
            return
        per = {}
        for i, k in self.geheugen.items():
            if i not in self.weg:
                per.setdefault(k, []).append(i)
        if self.open:
            eerste = self.open[0]
            for i in per.get(self.kaarten[eerste], []):
                if i != eerste:
                    self.tip = (i,)
                    self.melding = T("tip_memo")
                    self.app.geluid.speel("goed")
                    return
        else:
            for k, lijst in per.items():
                if len(lijst) >= 2:
                    self.tip = tuple(lijst[:2])
                    self.melding = T("tip_memo")
                    self.app.geluid.speel("goed")
                    return
        self.melding = T("tip_niets")

    # ---------- invoer
    def kaart_rect(self, i):
        kol, rij = self.kol, self.rij
        bw, bh = 900, 650
        gap = 14
        cw = min((bw - (kol - 1) * gap) // kol, 150)
        ch = min((bh - (rij - 1) * gap) // rij, 150)
        x0 = 40 + (bw - (kol * cw + (kol - 1) * gap)) // 2
        y0 = 100 + (bh - (rij * ch + (rij - 1) * gap)) // 2
        c, r = i % kol, i // kol
        return pygame.Rect(x0 + c * (cw + gap), y0 + r * (ch + gap), cw, ch)

    def klik(self, pos):
        if self.beurt != self.mijn_idx():
            return
        for i in range(len(self.kaarten)):
            if self.kaart_rect(i).collidepoint(pos):
                self.speler_draait(i)
                return

    def mijn_idx(self):
        return 0

    def speler_draait(self, i):
        self.draai_om(i)

    def toets(self, e):
        if e.key == pygame.K_ESCAPE:
            self.app.naar_menu()
        elif self.klaar and e.key in (pygame.K_SPACE, pygame.K_RETURN):
            self.nieuw_potje()
        elif e.key == pygame.K_t:
            self.geef_tip()

    # ---------- tekenen
    def teken_kaart(self, d, i, muis):
        r = self.kaart_rect(i)
        zichtbaar = i in self.open or i in self.weg
        t0 = self.draai.get(i)
        f = 1.0
        if t0 is not None:
            f = min(1.0, (time.time() - t0) / 0.25)
        breed = abs(math.cos(f * math.pi)) if f < 1 else 1.0
        voorkant = zichtbaar if f >= 0.5 else not zichtbaar
        rr = pygame.Rect(0, 0, max(2, int(r.w * breed)), r.h)
        rr.center = r.center
        if voorkant:
            kl = (44, 38, 70)
            if i in self.weg:
                kl = (40, 70, 56) if self.weg[i] == self.mijn_idx() else (70, 44, 56)
            pygame.draw.rect(d, kl, rr, border_radius=14)
            pygame.draw.rect(d, UI.GOUD if i in self.open else UI.RAND, rr, 4, border_radius=14)
            if breed > 0.6:
                teken_plaatje(d, self.kaarten[i], r.inflate(-24, -24))
        else:
            hover = rr.collidepoint(muis) and self.kan_draaien(i) and self.beurt == self.mijn_idx()
            pygame.draw.rect(d, (96, 84, 150) if hover else UI.PAARS, rr, border_radius=14)
            pygame.draw.rect(d, UI.ACCENT if hover else UI.RAND, rr, 4, border_radius=14)
            if breed > 0.6:                        # achterkant: een draakje-stempel
                pygame.draw.circle(d, (110, 100, 190), rr.center, min(rr.w, rr.h) // 3, 4)
                UI.tekst(d, "D", int(min(rr.w, rr.h) * 0.34), (110, 100, 190), rr.center, mid=True)
        if self.tip and i in self.tip:
            pygame.draw.rect(d, UI.GOUD, r.inflate(8, 8), 5, border_radius=16)

    def teken(self, d, muis):
        d.fill(UI.ACHTER)
        UI.tekst(d, T("memo"), 40, UI.ACCENT, (40, 14))
        for i in range(len(self.kaarten)):
            self.teken_kaart(d, i, muis)
        px = 980
        for idx in (self.mijn_idx(), 1 - self.mijn_idx()):
            y = 110 if idx == self.mijn_idx() else 200
            UI.tekst(d, self.naam(idx), 28, UI.TEKST, (px, y))
            UI.tekst(d, T("paren") % self.paren[idx], 22, UI.GOUD, (px, y + 38))
            if not self.klaar and self.beurt == idx:
                pygame.draw.rect(d, UI.ACCENT, (px - 14, y - 8, UI.W - px - 10, 80), 3, border_radius=12)
        UI.tekst(d, T("potjes") % (self.score_potjes[self.mijn_idx()], self.score_potjes[1 - self.mijn_idx()]), 22, UI.ZACHT, (px, 290), vet=False)
        y = 330
        if self.klaar:
            regels = [self.uitslag]
        elif self.beurt != self.mijn_idx():
            regels = [self.wacht_tekst()]
        else:
            regels = [self.melding or T("jouw_beurt")]
        for regel in regels:
            for stuk in UI.Backgammon._knip(None, regel, 22, UI.W - px - 20):
                UI.tekst(d, stuk, 22, UI.GOUD if self.klaar else UI.TEKST, (px, y))
                y += 30
        self.knoppen = []
        if self.klaar:
            self.knoppen.append(UI.Knop((px, 540, 270, 64), UI.T("nog"), self.nieuw_potje, UI.GROEN, 24))
        else:
            self.knoppen.append(UI.Knop((px, 540, 120, 64), UI.T("tip"), self.geef_tip, UI.GOUD, 24,
                                        aan=self.beurt == self.mijn_idx() and self.dicht_om is None and self.tip_mag()))
        self.knoppen.append(UI.Knop((px, 620, 270, 60), UI.T("menu"), self.app.naar_menu, UI.VAK, 24))
        self.knoppen.append(UI.Knop((px, 690, 270, 60), UI.T("regels"), lambda: setattr(self.app, "toon_regels", True), UI.VAK, 22))
        for k in self.knoppen:
            k.teken(d, muis)
        UI.tekst(d, T("toetsen_memo"), 16, UI.ZACHT, (40, UI.H - 30), vet=False)

    def tip_mag(self):
        return self.app.hulp

    def niveau_comp(self):
        return True

    def wacht_tekst(self):
        return T("comp_beurt")


# ------------------------------------------------------------------ online tegen elkaar
class OnlineMemory(Memory):
    """Memory op twee pc's: de server schudt (zaad), elke omgedraaide kaart gaat via de server."""

    def __init__(self, app, adres, code, naam, token):
        self.lijn = None
        self.code = code
        self.ik = None
        self.ander = None
        self.verbonden = [False, False]
        self.status = UI.T("verbinden")
        self.fase = "wachten"
        self.potje = None
        self.n_zetten = 0
        self.einde_gezien = False
        Memory.__init__(self, app, ONLINE_NIVEAU)
        self.lijn = UI.online.Lijn(adres, code, {"t": "hallo", "spel": "memo", "naam": naam, "token": token}, pad="zet/kamer")

    def mijn_idx(self):
        return self.ik if self.ik is not None else 0

    def naam(self, idx):
        if self.ik is None:
            return UI.T("speler%d" % (idx + 1))
        return UI.T("jij") if idx == self.ik else (self.ander or UI.T("tegenspeler"))

    def tip_mag(self):
        return False                               # online geen tip

    def niveau_comp(self):
        return False

    def nieuw_potje(self, zaad=None):
        if getattr(self, "lijn", None) is not None:
            self.lijn.stuur({"t": "nieuw"})
            self.app.geluid.speel("klik")
            return
        Memory.nieuw_potje(self, zaad)

    def wacht_tekst(self):
        if self.fase == "wachten":
            return UI.T("wacht_ander") % self.code
        return UI.T("ander_beurt") % self.naam(self.beurt)

    def update(self):
        nu = time.time()
        if self.dicht_om is not None and nu >= self.dicht_om:
            self.beurt_klaar()
        if self.lijn is None:
            return
        for b in self.lijn.haal():
            t = b.get("t")
            if t == "_verbonden":
                self.status = ""
            elif t in ("_fout", "_weg"):
                self.status = UI.T("geen_server")
            elif t == "fout":
                self.status = UI.T("kamer_vol") if b.get("fout") == "kamer vol" else str(b.get("fout"))[:60]
            if t == "stand":
                try:
                    self.pas_toe(b)
                except Exception:
                    import traceback
                    UI.log_fout(traceback.format_exc())

    def speler_draait(self, i):
        if self.fase != "spel" or not self.kan_draaien(i):
            return
        tweede = len(self.open) == 1
        paar = tweede and self.kaarten[i] == self.kaarten[self.open[0]]
        einde = None
        if paar and len(self.weg) + 2 >= len(self.kaarten):
            p = list(self.paren)
            p[self.ik] += 1
            einde = -1 if p[0] == p[1] else (0 if p[0] > p[1] else 1)
        if self.lijn.stuur({"t": "zet", "z": {"kaart": i}, "nog": (not tweede) or paar, "einde": einde}):
            self.n_zetten += 1
            self.draai_om(i)

    def controleer_einde(self):
        if len(self.weg) >= len(self.kaarten):
            self.klaar = True

    def beurt_klaar(self):
        for i in self.open:
            self.draai[i] = time.time()
        self.open = []
        self.dicht_om = None
        self.beurt = 1 - self.beurt
        self.melding = ""

    def pas_toe(self, st):
        self.ik = st["ik"]
        self.score_potjes = list(st.get("score", [0, 0]))
        self.ander = (st.get("ander") or {}).get("naam")
        self.verbonden = st.get("verbonden", [True, True])
        self.fase = st["fase"]
        if self.fase == "wachten":
            return
        lijst = st.get("zetten") or []
        if st.get("potje") == self.potje and len(lijst) < self.n_zetten:
            return
        if st.get("potje") != self.potje:
            self.potje = st.get("potje")
            Memory.nieuw_potje(self, zaad=st.get("zaad"))
            self.beurt = st.get("eerste", 0)
            self.n_zetten = 0
            self.einde_gezien = False
            for d in lijst[:-1] if len(lijst) > 1 else []:      # opnieuw verbonden: snel naspelen
                self.speel_na(d, snel=True)
        for d in lijst[self.n_zetten:]:
            self.speel_na(d)
        if self.fase == "einde":
            self.klaar = True
            w = st.get("winnaar")
            self.uitslag = T("gelijk") if w == -1 else UI.T("wint") % self.naam(w)
            if not self.einde_gezien:
                self.einde_gezien = True
                self.app.geluid.speel("win" if w == self.ik else ("klik" if w == -1 else "verlies"))
        elif self.dicht_om is None and not self.open:
            self.beurt = st["beurt"]

    def speel_na(self, d, snel=False):
        i = int((d.get("z") or {}).get("kaart", -1))
        self.n_zetten += 1
        if not (0 <= i < len(self.kaarten)):
            return
        if self.dicht_om is not None:               # de vorige twee eerst dicht
            self.beurt_klaar()
        self.beurt = d.get("sp", self.beurt)
        self.draai_om(i)
        if snel:
            self.draai.pop(i, None)
            if self.dicht_om is not None:
                self.beurt_klaar()

    def teken(self, d, muis):
        Memory.teken(self, d, muis)
        px = 980
        UI.tekst(d, UI.T("kamer") % self.code, 20, UI.ACCENT, (240, 30))
        if self.status:
            UI.tekst(d, self.status, 20, UI.ROOD, (px, 480))
        elif self.ik is not None and self.ander and not self.verbonden[1 - self.ik]:
            UI.tekst(d, UI.T("ander_weg") % self.ander, 20, UI.GOUD, (px, 480))
        if self.fase == "wachten":
            UI.tekst(d, self.code, 56, UI.GOUD, (px, 420))

    def stop(self):
        if self.lijn:
            self.lijn.stop()
