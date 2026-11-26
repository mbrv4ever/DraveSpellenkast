# -*- coding: utf-8 -*-
"""DraveSpellenkast - Domino (dubbel-zes, 28 stenen). Leg een steen aan met hetzelfde aantal ogen.
Kun je niet, dan pak je uit de pot. Wie het eerst al zijn stenen kwijt is, wint.
Tegen de computer of online. Copyright (C) 2026 Dravenlock (Roger & Claudio). GNU GPL v3.0."""
import random
import time

import pygame

UI = None          # wordt door main.py gezet

STEEN_W, STEEN_H = 64, 32          # op tafel (liggend)
HAND_W, HAND_H = 52, 104           # in je hand (staand)
IVOOR = (246, 240, 226)
IVOOR_D = (196, 186, 168)
OOG = (40, 32, 52)

TX = {
    "domino": ("Domino", "Dominoes"),
    "jouw_beurt": ("Jouw beurt: klik een steen die past (oplicht).", "Your turn: click a stone that fits (lit up)."),
    "kies_kant": ("Hij past aan twee kanten: klik op de gouden kant.", "It fits on both ends: click the gold end."),
    "pak": ("Pak uit de pot", "Draw from the pile"),
    "pas": ("Passen", "Pass"),
    "moet_pakken": ("Geen steen past: pak er een uit de pot.", "No stone fits: draw one from the pile."),
    "moet_passen": ("Geen steen past en de pot is leeg: je moet passen.", "No stone fits and the pile is empty: you must pass."),
    "comp_denkt": ("De computer is aan de beurt...", "The computer's turn..."),
    "comp_pakt": ("De computer pakt uit de pot.", "The computer draws from the pile."),
    "comp_past": ("De computer kan niet en past.", "The computer can't and passes."),
    "ander_pakt": ("%s pakt uit de pot.", "%s draws from the pile."),
    "ander_past": ("%s past.", "%s passes."),
    "pot": ("Pot: %d", "Pile: %d"),
    "stenen": ("%d stenen", "%d stones"),
    "wint_punten": ("%s wint! (+%d punten)", "%s wins! (+%d points)"),
    "vast": ("Niemand kan meer. Wie de minste ogen heeft, wint.", "Nobody can move. Fewest pips wins."),
    "gelijk": ("Gelijkspel!", "A draw!"),
    "punten": ("Punten: %d", "Points: %d"),
    "gewonnen": ("Gewonnen: %d", "Won: %d"),
    "tip_kop": ("Tip: leg de gouden steen.", "Tip: play the gold stone."),
    "toetsen_domino": ("Klik een steen  ·  P = pakken  ·  T = tip  ·  Esc = menu", "Click a stone  ·  P = draw  ·  T = tip  ·  Esc = menu"),
}


def T(k):
    if k in TX:
        v = TX[k]
        return v[0] if UI.TAAL == "nl" else v[1]
    return UI.T(k)


def alle_stenen():
    return [(a, b) for a in range(7) for b in range(a, 7)]


def ogen(steen):
    return steen[0] + steen[1]


# ------------------------------------------------------------------ het spel
class Domino:
    def __init__(self, app, niveau):
        self.app = app
        self.niveau = niveau
        self.knoppen = []
        self.punten = [0, 0]
        self.begint = 0
        self.nieuw_potje()

    def naam(self, sp):
        return UI.T("jij") if sp == 0 else UI.T("computer")

    def schud(self, zaad=None):
        stenen = alle_stenen()
        random.Random(zaad).shuffle(stenen)
        return stenen

    def nieuw_potje(self, zaad=None, begint=None):
        stenen = self.schud(zaad)
        self.hand = [sorted(stenen[:7], key=ogen), sorted(stenen[7:14], key=ogen)]
        self.pot = stenen[14:]
        self.rij = []                       # de stenen op tafel, van links naar rechts, als (links, rechts)
        self.beurt = self.begint if begint is None else begint
        self.begint = 1 - self.begint
        self.klaar = False
        self.uitslag = ""
        self.melding = ""
        self.kies = None                    # index in mijn hand
        self.tip = None
        self.comp_t = time.time() + 1.0
        self.passen = 0                     # hoeveel keer achter elkaar gepast (2 = vast)
        self.nieuw_t = {}                   # steen -> tijd (om hem even te laten oplichten)
        self.mist = [set(), set()]          # getallen die een speler niet had (hij moest pakken of passen)

    # ---------- regels
    def einden(self):
        if not self.rij:
            return None, None
        return self.rij[0][0], self.rij[-1][1]

    def past_waar(self, steen):
        """Lijst van kanten waar de steen past: 'L' en/of 'R'."""
        if not self.rij:
            return ["R"]
        l, r = self.einden()
        uit = []
        if l in steen:
            uit.append("L")
        if r in steen:
            uit.append("R")
        return uit

    def kan_leggen(self, sp):
        return any(self.past_waar(s) for s in self.hand[sp])

    def leg(self, sp, steen, kant):
        self.hand[sp].remove(steen)
        a, b = steen
        if not self.rij:
            self.rij.append((a, b))
        elif kant == "L":
            l = self.rij[0][0]
            self.rij.insert(0, (b, a) if a == l else (a, b))      # het passende getal raakt het linker einde
        else:
            r = self.rij[-1][1]
            self.rij.append((a, b) if a == r else (b, a))
        self.nieuw_t[tuple(sorted(steen))] = time.time()
        self.passen = 0
        self.app.geluid.speel("zet")
        if not self.hand[sp]:
            self.einde(sp)
            return
        self.beurt = 1 - sp

    def pak(self, sp):
        if self.rij:
            self.mist[sp].update(self.einden())
        if not self.pot:
            return False
        s = self.pot.pop()
        self.hand[sp].append(s)
        self.hand[sp].sort(key=ogen)
        self.app.geluid.speel("klik")
        return True

    def pas(self, sp):
        self.passen += 1
        self.beurt = 1 - sp
        if self.passen >= 2:                    # niemand kan meer: minste ogen wint
            o = [sum(map(ogen, self.hand[0])), sum(map(ogen, self.hand[1]))]
            self.melding = T("vast")
            if o[0] == o[1]:
                self.klaar = True
                self.uitslag = T("gelijk")
            else:
                self.einde(0 if o[0] < o[1] else 1)

    def einde(self, w):
        self.klaar = True
        winst = sum(map(ogen, self.hand[1 - w]))
        self.punten[w] += winst
        self.uitslag = T("wint_punten") % (self.naam(w), winst)
        self.app.geluid.speel("win" if w == self.mijn_idx() else "verlies")

    def mijn_idx(self):
        return 0

    # ---------- de computer
    def comp_kies(self, sp):
        mog = [(s, k) for s in self.hand[sp] for k in self.past_waar(s)]
        if not mog:
            return None
        if self.niveau == 1:
            return random.choice(mog)
        if self.niveau == 2:
            return max(mog, key=lambda m: ogen(m[0]) + random.random())
        # moeilijk: dubbele en zware stenen eerst, en houd zoveel mogelijk verschillende getallen over
        tegen = self.mist[1 - sp]
        def score(m):
            s, k = m
            rest = [x for x in self.hand[sp] if x != s]
            soorten = len(set(n for x in rest for n in x))
            l, r = self.einden()
            if l is None:
                nieuw = set(s)
            elif k == "L":
                nieuw = {s[0] if s[1] == l else s[1], r}
            else:
                nieuw = {l, s[0] if s[1] == r else s[1]}
            blok = sum(6 for n in nieuw if n in tegen)            # de ander had die getallen niet: houd hem vast
            kan_verder = sum(2 for x in rest for n in nieuw if n in x)
            return ogen(s) * 2 + (8 if s[0] == s[1] else 0) + soorten * 3 + blok + kan_verder
        return max(mog, key=score)

    def comp_beurt(self, sp):
        keuze = self.comp_kies(sp)
        if keuze:
            self.leg(sp, keuze[0], keuze[1])
            self.melding = ""
            return
        if self.pak(sp):
            self.melding = T("comp_pakt")
            self.comp_t = time.time() + 0.7
            return
        self.melding = T("comp_past")
        self.pas(sp)

    def update(self):
        if self.klaar or self.beurt != 1:
            return
        if time.time() >= self.comp_t:
            self.comp_beurt(1)
            self.comp_t = time.time() + 1.0

    def geef_tip(self):
        if self.klaar or self.beurt != self.mijn_idx():
            return
        oud = self.niveau
        self.niveau = 3
        keuze = self.comp_kies(self.mijn_idx())
        self.niveau = oud
        if keuze:
            self.tip = keuze[0]
            self.melding = T("tip_kop")
            self.app.geluid.speel("goed")

    # ---------- mijn zetten
    def ik_leg(self, steen, kant):
        self.leg(self.mijn_idx(), steen, kant)

    def ik_pak(self):
        ik = self.mijn_idx()
        if self.klaar or self.beurt != ik or self.kan_leggen(ik):
            return
        if not self.pak(ik):
            self.ik_pas()

    def ik_pas(self):
        ik = self.mijn_idx()
        if self.klaar or self.beurt != ik or self.kan_leggen(ik) or self.pot:
            return
        self.pas(ik)

    def hand_rects(self):
        hand = self.hand[self.mijn_idx()]
        n = len(hand)
        stap = min(HAND_W + 12, (UI.W - 120) // max(1, n))
        x0 = (UI.W - (stap * (n - 1) + HAND_W)) // 2
        return [pygame.Rect(x0 + i * stap, UI.H - HAND_H - 110, HAND_W, HAND_H) for i in range(n)]

    def klik(self, pos):
        ik = self.mijn_idx()
        if self.klaar or self.beurt != ik:
            return
        if self.kies is not None and self.kies < len(self.hand[ik]):          # kant kiezen
            for kant, r in self.kant_rects().items():
                if r.collidepoint(pos):
                    steen = self.hand[ik][self.kies]
                    self.kies = None
                    self.tip = None
                    self.ik_leg(steen, kant)
                    return
        for i, r in enumerate(self.hand_rects()):
            if r.collidepoint(pos):
                steen = self.hand[ik][i]
                kanten = self.past_waar(steen)
                if not kanten:
                    self.app.geluid.speel("fout")
                    return
                l, rr = self.einden()
                if len(kanten) == 1 or l == rr:
                    self.kies = None
                    self.tip = None
                    self.ik_leg(steen, kanten[0])
                else:
                    self.kies = i
                    self.melding = T("kies_kant")
                    self.app.geluid.speel("klik")
                return

    def toets(self, e):
        if e.key == pygame.K_ESCAPE:
            self.app.naar_menu()
        elif self.klaar and e.key in (pygame.K_SPACE, pygame.K_RETURN):
            self.nieuw_potje()
        elif e.key == pygame.K_p:
            self.ik_pak()
        elif e.key == pygame.K_t:
            self.geef_tip()

    # ---------- tekenen
    def teken_ogen(self, d, rect, n):
        cx, cy = rect.center
        s = min(rect.w, rect.h)
        o = s * 0.27
        r = max(2, int(s * 0.09))
        plek = {1: [(0, 0)], 2: [(-1, -1), (1, 1)], 3: [(-1, -1), (0, 0), (1, 1)], 4: [(-1, -1), (1, -1), (-1, 1), (1, 1)],
                5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)], 6: [(-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]}.get(n, [])
        for dx, dy in plek:
            pygame.draw.circle(d, OOG, (int(cx + dx * o), int(cy + dy * o)), r)

    def teken_steen(self, d, rect, a, b, staand=False, rand=None, dicht=False):
        pygame.draw.rect(d, IVOOR_D, rect.move(0, 3), border_radius=7)
        pygame.draw.rect(d, (110, 96, 170) if dicht else IVOOR, rect, border_radius=7)
        pygame.draw.rect(d, (70, 60, 100), rect, 2, border_radius=7)
        if dicht:
            pygame.draw.circle(d, (140, 126, 200), rect.center, min(rect.w, rect.h) // 4, 3)
        else:
            if staand:
                h1 = pygame.Rect(rect.x, rect.y, rect.w, rect.h // 2)
                h2 = pygame.Rect(rect.x, rect.centery, rect.w, rect.h // 2)
                pygame.draw.line(d, (150, 140, 120), (rect.x + 6, rect.centery), (rect.right - 6, rect.centery), 2)
            else:
                h1 = pygame.Rect(rect.x, rect.y, rect.w // 2, rect.h)
                h2 = pygame.Rect(rect.centerx, rect.y, rect.w // 2, rect.h)
                pygame.draw.line(d, (150, 140, 120), (rect.centerx, rect.y + 4), (rect.centerx, rect.bottom - 4), 2)
            self.teken_ogen(d, h1, a)
            self.teken_ogen(d, h2, b)
        if rand:
            pygame.draw.rect(d, rand, rect.inflate(8, 8), 4, border_radius=9)

    def rij_posities(self):
        """Slang van stenen over de tafel: rijen van links naar rechts, dan terug."""
        per_rij = 15
        n = len(self.rij)
        rijen = max(1, (n + per_rij - 1) // per_rij)
        uit = []
        y0 = 300 - (rijen - 1) * 26
        for i in range(n):
            rr, k = divmod(i, per_rij)
            in_rij = min(per_rij, n - rr * per_rij)
            breed = in_rij * (STEEN_W + 4)
            x0 = (UI.W - breed) // 2
            if rr % 2 == 1:
                k = in_rij - 1 - k
            uit.append(pygame.Rect(x0 + k * (STEEN_W + 4), y0 + rr * 52, STEEN_W, STEEN_H))
        return uit

    def kant_rects(self):
        pos = self.rij_posities()
        if not pos:
            return {}
        l = pos[0].move(-STEEN_W - 10, 0) if len(pos) < 15 or True else pos[0]
        r = pos[-1].move(STEEN_W + 10, 0)
        if (len(self.rij) - 1) // 15 % 2 == 1:
            r = pos[-1].move(-STEEN_W - 10, 0)
        return {"L": l, "R": r}

    def teken(self, d, muis):
        d.fill(UI.ACHTER)
        UI.tekst(d, T("domino"), 40, UI.ACCENT, (40, 14))
        tafel = pygame.Rect(30, 150, UI.W - 60, 320)
        pygame.draw.rect(d, (34, 84, 60), tafel, border_radius=24)
        pygame.draw.rect(d, UI.RAND, tafel, 4, border_radius=24)
        nu = time.time()
        for (a, b), r in zip(self.rij, self.rij_posities()):
            licht = nu - self.nieuw_t.get(tuple(sorted((a, b))), 0) < 1.0
            self.teken_steen(d, r, a, b, rand=UI.GOUD if licht else None)
        ik = self.mijn_idx()
        mijn_beurt = not self.klaar and self.beurt == ik
        if self.kies is not None and mijn_beurt:
            for kant, r in self.kant_rects().items():
                hover = r.collidepoint(muis)
                pygame.draw.rect(d, UI.GOUD, r, 0 if hover else 4, border_radius=8)
                UI.tekst(d, "←" if kant == "L" else "→", 26, UI.ACHTER if hover else UI.GOUD, r.center, mid=True)
        # de ander: dichte stenen bovenaan
        ander = 1 - ik
        n = len(self.hand[ander])
        for i in range(n):
            self.teken_steen(d, pygame.Rect(UI.W // 2 - n * 19 + i * 38, 76, 32, 64), 0, 0, staand=True, dicht=True)
        UI.tekst(d, "%s  ·  %s" % (self.naam(ander), T("stenen") % n), 22, UI.TEKST if self.beurt == ander else UI.ZACHT, (40, 100))
        UI.tekst(d, T("pot") % len(self.pot), 22, UI.ZACHT, (UI.W - 40, 100), rechts=True)
        UI.tekst(d, T(self.punten_label()) % self.punten[ik] + "   " + self.naam(ander) + ": %d" % self.punten[ander], 22, UI.GOUD, (UI.W - 40, 24), rechts=True)
        # mijn hand
        for i, (steen, r) in enumerate(zip(self.hand[ik], self.hand_rects())):
            past = mijn_beurt and bool(self.past_waar(steen))
            rr = r.move(0, -14) if (past and r.collidepoint(muis)) or i == self.kies else r
            rand = UI.GOUD if self.tip == steen else (UI.ACCENT if i == self.kies else (UI.GROEN if past and self.app.hulp else None))
            self.teken_steen(d, rr, steen[0], steen[1], staand=True, rand=rand)
        # melding en knoppen
        if self.klaar:
            regel = self.uitslag
        elif not mijn_beurt:
            regel = self.melding or self.wacht_tekst()
        elif not self.kan_leggen(ik):
            regel = T("moet_pakken") if self.pot else T("moet_passen")
        else:
            regel = self.melding or T("jouw_beurt")
        UI.tekst(d, regel, 24, UI.GOUD if self.klaar else UI.TEKST, (UI.W // 2, 498), mid=True)
        self.knoppen = []
        y = UI.H - 80
        if self.klaar:
            self.knoppen.append(UI.Knop((40, y, 300, 64), UI.T("nog"), self.nieuw_potje, UI.GROEN, 24))
        else:
            kan = mijn_beurt and not self.kan_leggen(ik)
            if self.pot or not kan:
                self.knoppen.append(UI.Knop((40, y, 260, 64), T("pak"), self.ik_pak, UI.GROEN if kan else UI.VAK, 22, aan=kan and bool(self.pot)))
            else:
                self.knoppen.append(UI.Knop((40, y, 260, 64), T("pas"), self.ik_pas, UI.GOUD, 22, aan=kan))
            self.knoppen.append(UI.Knop((315, y, 120, 64), UI.T("tip"), self.geef_tip, UI.GOUD, 22, aan=mijn_beurt and self.tip_mag()))
            self.knoppen.append(UI.Knop((450, y, 200, 64), "%s: %s" % (UI.T("hulp"), UI.T("aan") if self.app.hulp else UI.T("uitm")),
                                        self.app.wissel_hulp, UI.VAK, 20))
        self.knoppen.append(UI.Knop((UI.W - 380, y, 160, 64), UI.T("menu"), self.app.naar_menu, UI.VAK, 24))
        self.knoppen.append(UI.Knop((UI.W - 205, y, 170, 64), UI.T("regels"), lambda: setattr(self.app, "toon_regels", True), UI.VAK, 20))
        for k in self.knoppen:
            k.teken(d, muis)

    def tip_mag(self):
        return True

    def punten_label(self):
        return "punten"

    def wacht_tekst(self):
        return T("comp_denkt")


# ------------------------------------------------------------------ online tegen elkaar
class OnlineDomino(Domino):
    """De server schudt (zaad); beide pc's kennen zo dezelfde stenen. Leggen, pakken en passen gaan via de server."""

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
        Domino.__init__(self, app, 0)
        self.beurt = -1
        self.lijn = UI.online.Lijn(adres, code, {"t": "hallo", "spel": "domino", "naam": naam, "token": token}, pad="zet/kamer")

    def mijn_idx(self):
        return self.ik if self.ik is not None else 0

    def naam(self, idx):
        if self.ik is None:
            return UI.T("speler%d" % (idx + 1))
        return UI.T("jij") if idx == self.ik else (self.ander or UI.T("tegenspeler"))

    def tip_mag(self):
        return False

    def punten_label(self):
        return "gewonnen"

    def nieuw_potje(self, zaad=None, begint=None):
        if getattr(self, "lijn", None) is not None:
            self.lijn.stuur({"t": "nieuw"})
            self.app.geluid.speel("klik")
            return
        Domino.nieuw_potje(self, zaad, begint)

    def wacht_tekst(self):
        if self.fase == "wachten":
            return UI.T("wacht_ander") % self.code
        return UI.T("ander_beurt") % self.naam(self.beurt)

    def update(self):
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

    def einde(self, w):
        self.klaar = True
        winst = sum(map(ogen, self.hand[1 - w]))
        self.uitslag = T("wint_punten") % (self.naam(w), winst)

    def stuur(self, z, nog=False):
        if self.fase != "spel" or self.beurt != self.ik:
            return False
        if self.lijn.stuur({"t": "zet", "z": z, "nog": nog, "einde": self.einde_na(z)}):
            self.n_zetten += 1
            return True
        self.status = UI.T("geen_server")
        return False

    def einde_na(self, z):
        """Wint deze zet het potje? Dan weet de server dat meteen (met de punten)."""
        ik = self.ik
        if "leg" in z and len(self.hand[ik]) == 1:
            return ik
        if z.get("pas") and self.passen >= 1:
            o = [sum(map(ogen, self.hand[0])), sum(map(ogen, self.hand[1]))]
            return -1 if o[0] == o[1] else (0 if o[0] < o[1] else 1)
        return None

    def ik_leg(self, steen, kant):
        if self.stuur({"leg": list(steen), "kant": kant}):
            Domino.leg(self, self.ik, steen, kant)

    def ik_pak(self):
        if self.klaar or self.beurt != self.ik or self.kan_leggen(self.ik):
            return
        if not self.pot:
            self.ik_pas()
            return
        if self.stuur({"pak": True}, nog=True):
            self.pak(self.ik)

    def ik_pas(self):
        if self.klaar or self.beurt != self.ik or self.kan_leggen(self.ik) or self.pot:
            return
        if self.stuur({"pas": True}):
            Domino.pas(self, self.ik)

    def pas_toe(self, st):
        self.ik = st["ik"]
        sc = st.get("score", [0, 0])
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
            Domino.nieuw_potje(self, zaad=st.get("zaad"), begint=st.get("eerste", 0))
            self.n_zetten = 0
            self.einde_gezien = False
        for d in lijst[self.n_zetten:]:
            z = d.get("z") or {}
            sp = d.get("sp", 0)
            self.n_zetten += 1
            self.beurt = sp
            if "leg" in z:
                steen = tuple(int(x) for x in z["leg"])
                if steen in self.hand[sp]:
                    Domino.leg(self, sp, steen, z.get("kant", "R"))
                    if sp != self.ik:
                        self.melding = ""
            elif z.get("pak"):
                self.pak(sp)
                if sp != self.ik:
                    self.melding = T("ander_pakt") % self.naam(sp)
            elif z.get("pas"):
                Domino.pas(self, sp)
                if sp != self.ik:
                    self.melding = T("ander_past") % self.naam(sp)
        self.punten = [sc[0], sc[1]]
        if self.fase == "einde":
            self.klaar = True
            if not self.einde_gezien:
                self.einde_gezien = True
                w = st.get("winnaar")
                if w == -1:
                    self.uitslag = T("gelijk")
                self.app.geluid.speel("win" if w == self.ik else ("klik" if w == -1 else "verlies"))
        else:
            self.klaar = False
            self.beurt = st["beurt"]

    def teken(self, d, muis):
        Domino.teken(self, d, muis)
        UI.tekst(d, UI.T("kamer") % self.code, 20, UI.ACCENT, (220, 26))
        if self.status:
            UI.tekst(d, self.status, 20, UI.ROOD, (UI.W // 2, 530), mid=True)
        elif self.ik is not None and self.ander and not self.verbonden[1 - self.ik]:
            UI.tekst(d, UI.T("ander_weg") % self.ander, 20, UI.GOUD, (UI.W // 2, 530), mid=True)
        if self.fase == "wachten":
            UI.tekst(d, self.code, 56, UI.GOUD, (UI.W // 2, 300), mid=True)

    def stop(self):
        if self.lijn:
            self.lijn.stop()
