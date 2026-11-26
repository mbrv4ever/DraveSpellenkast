# -*- coding: utf-8 -*-
"""DraveSpellenkast - Sudoku: vul het rooster zo dat elke rij, kolom en elk blok van 3x3 de cijfers 1 tot 9 heeft.
Elke puzzel wordt zelf gemaakt en heeft precies één oplossing. Copyright (C) 2026 Dravenlock (Roger & Claudio). GNU GPL v3.0."""
import json
import os
import random
import time

import pygame

UI = None          # wordt door main.py gezet

VAK = 70
BX, BY = 60, 96
GEGEVEN = {1: 40, 2: 32, 3: 26}      # hoeveel cijfers je cadeau krijgt

TX = {
    "sudoku": ("Sudoku", "Sudoku"),
    "maken": ("Even een nieuwe puzzel maken...", "Making a new puzzle..."),
    "uitleg_s": ("Klik een vakje en typ een cijfer (of klik een cijfer hieronder).", "Click a square and type a number (or click a number below)."),
    "potlood": ("Potlood", "Pencil"),
    "gum": ("Gum", "Erase"),
    "klaar_s": ("Opgelost in %s! Knap gedaan.", "Solved in %s! Well done."),
    "record": ("Nieuw record!", "New record!"),
    "fouten_s": ("Fouten: %d", "Mistakes: %d"),
    "tijd": ("Tijd: %s", "Time: %s"),
    "beste": ("Beste: %s", "Best: %s"),
    "tip_s": ("Tip: in het gouden vakje hoort een %d.", "Tip: the gold square needs a %d."),
    "tip_vak": ("Klik eerst een leeg vakje, dan Tip.", "Click an empty square first, then Tip."),
    "toetsen_sudoku": ("Klik + 1-9  ·  pijltjes  ·  Delete = gum  ·  P = potlood  ·  T = tip  ·  Esc = menu",
                       "Click + 1-9  ·  arrows  ·  Delete = erase  ·  P = pencil  ·  T = tip  ·  Esc = menu"),
}


def T(k):
    if k in TX:
        v = TX[k]
        return v[0] if UI.TAAL == "nl" else v[1]
    return UI.T(k)


def tijd_tekst(s):
    s = int(s)
    return "%d:%02d" % (s // 60, s % 60)


# ------------------------------------------------------------------ puzzels maken
def kandidaten(g, i):
    r, c = divmod(i, 9)
    gezien = set(g[r * 9:r * 9 + 9]) | set(g[c::9])
    br, bc = r // 3 * 3, c // 3 * 3
    for rr in range(br, br + 3):
        gezien.update(g[rr * 9 + bc:rr * 9 + bc + 3])
    return [n for n in range(1, 10) if n not in gezien]


def los_op(g, tel=False, limiet=2, rnd=None):
    """Backtracking met 'minst aantal keuzes eerst'. tel=True: tel oplossingen (tot limiet)."""
    g = g[:]
    aantal = [0]
    oplossing = [None]

    def stap():
        beste, beste_k = None, None
        for i in range(81):
            if g[i] == 0:
                k = kandidaten(g, i)
                if not k:
                    return False
                if beste is None or len(k) < len(beste_k):
                    beste, beste_k = i, k
                    if len(k) == 1:
                        break
        if beste is None:
            aantal[0] += 1
            if oplossing[0] is None:
                oplossing[0] = g[:]
            return aantal[0] >= limiet if tel else True
        if rnd:
            rnd.shuffle(beste_k)
        for n in beste_k:
            g[beste] = n
            if stap():
                return True
            g[beste] = 0
        return False

    stap()
    return aantal[0] if tel else oplossing[0]


def maak_puzzel(niveau, rnd=None):
    rnd = rnd or random.Random()
    vol = los_op([0] * 81, rnd=rnd)
    puzzel = vol[:]
    plekken = list(range(81))
    rnd.shuffle(plekken)
    over = 81
    for i in plekken:
        if over <= GEGEVEN[niveau]:
            break
        oud = puzzel[i]
        puzzel[i] = 0
        if los_op(puzzel, tel=True) != 1:
            puzzel[i] = oud                     # dan zou er meer dan één oplossing zijn
        else:
            over -= 1
    return puzzel, vol


# ------------------------------------------------------------------ het spel
class Sudoku:
    def __init__(self, app, niveau):
        self.app = app
        self.niveau = niveau
        self.knoppen = []
        self.beste = self.laad_beste()
        self.nieuw_potje()

    def beste_pad(self):
        return os.path.join(UI.DATA, "sudoku_records.json")

    def laad_beste(self):
        try:
            with open(self.beste_pad(), encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def bewaar_beste(self):
        try:
            with open(self.beste_pad(), "w", encoding="utf-8") as f:
                json.dump(self.beste, f)
        except Exception:
            pass

    def nieuw_potje(self):
        self.puzzel, self.oplossing = maak_puzzel(self.niveau)
        self.g = self.puzzel[:]
        self.noten = [set() for _ in range(81)]
        self.gekozen = 40
        self.potlood = False
        self.fouten = 0
        self.start = time.time()
        self.eind = None
        self.klaar = False
        self.record = False
        self.melding = ""
        self.tip = None
        self.flits = {}                         # vak -> tijd (goed ingevuld: even oplichten)

    # ---------- invullen
    def zet(self, n):
        i = self.gekozen
        if self.klaar or i is None or self.puzzel[i]:
            return
        if self.potlood and n:
            if self.g[i]:
                return
            self.noten[i] ^= {n}
            self.app.geluid.speel("klik")
            return
        self.g[i] = n
        self.noten[i] = set()
        self.tip = None
        self.melding = ""
        if n == 0:
            return
        if n != self.oplossing[i]:
            self.fouten += 1
            self.app.geluid.speel("fout")
        else:
            self.flits[i] = time.time()
            self.app.geluid.speel("zet")
            r, c = divmod(i, 9)                  # het cijfer mag uit de potlood-notities van de buren
            for j in range(81):
                rr, cc = divmod(j, 9)
                if rr == r or cc == c or (rr // 3 == r // 3 and cc // 3 == c // 3):
                    self.noten[j].discard(n)
        if self.g == self.oplossing:
            self.klaar = True
            self.eind = time.time()
            duur = self.eind - self.start
            k = str(self.niveau)
            if self.beste.get(k) is None or duur < self.beste[k]:
                self.beste[k] = duur
                self.bewaar_beste()
                self.record = True
            self.app.geluid.speel("win")

    def geef_tip(self):
        if self.klaar:
            return
        i = self.gekozen
        if i is None or self.puzzel[i] or self.g[i] == self.oplossing[i]:
            leeg = [j for j in range(81) if self.g[j] != self.oplossing[j]]
            if not leeg:
                return
            # het vakje met de minste mogelijkheden: daar kun je het makkelijkst verder
            i = min(leeg, key=lambda j: len(kandidaten([x if x == self.oplossing[k] else 0 for k, x in enumerate(self.g)], j)))
            self.gekozen = i
        self.tip = i
        self.melding = T("tip_s") % self.oplossing[i]
        self.app.geluid.speel("goed")

    def update(self):
        pass

    # ---------- invoer
    def vak_op(self, pos):
        x, y = pos
        if BX <= x < BX + 9 * VAK and BY <= y < BY + 9 * VAK:
            return (y - BY) // VAK * 9 + (x - BX) // VAK
        return None

    def klik(self, pos):
        v = self.vak_op(pos)
        if v is not None:
            self.gekozen = v
            self.app.geluid.speel("klik")

    def toets(self, e):
        if e.key == pygame.K_ESCAPE:
            self.app.naar_menu()
            return
        if self.klaar and e.key in (pygame.K_SPACE, pygame.K_RETURN):
            self.nieuw_potje()
            return
        i = self.gekozen if self.gekozen is not None else 40
        r, c = divmod(i, 9)
        if e.key == pygame.K_UP:
            self.gekozen = (r - 1) % 9 * 9 + c
        elif e.key == pygame.K_DOWN:
            self.gekozen = (r + 1) % 9 * 9 + c
        elif e.key == pygame.K_LEFT:
            self.gekozen = r * 9 + (c - 1) % 9
        elif e.key == pygame.K_RIGHT:
            self.gekozen = r * 9 + (c + 1) % 9
        elif e.key in (pygame.K_DELETE, pygame.K_BACKSPACE, pygame.K_0, pygame.K_KP0):
            self.zet(0)
        elif e.key == pygame.K_p:
            self.potlood = not self.potlood
        elif e.key == pygame.K_t:
            self.geef_tip()
        elif e.unicode and e.unicode in "123456789" and len(e.unicode) == 1:
            self.zet(int(e.unicode))

    # ---------- tekenen
    def teken(self, d, muis):
        d.fill(UI.ACHTER)
        UI.tekst(d, T("sudoku"), 40, UI.ACCENT, (BX, 14))
        bord = pygame.Rect(BX - 6, BY - 6, 9 * VAK + 12, 9 * VAK + 12)
        pygame.draw.rect(d, (240, 236, 248), bord, border_radius=10)
        sel = self.gekozen
        sel_n = self.g[sel] if sel is not None else 0
        nu = time.time()
        for i in range(81):
            r, c = divmod(i, 9)
            rect = pygame.Rect(BX + c * VAK, BY + r * VAK, VAK, VAK)
            kl = (250, 248, 252)
            if sel is not None and self.app.hulp:
                sr, sc = divmod(sel, 9)
                if r == sr or c == sc or (r // 3 == sr // 3 and c // 3 == sc // 3):
                    kl = (228, 222, 244)
                if sel_n and self.g[i] == sel_n:
                    kl = (206, 196, 240)
            if i == sel:
                kl = (186, 170, 250)
            if self.tip == i:
                kl = (250, 222, 140)
            if i in self.flits and nu - self.flits[i] < 0.6:
                kl = (180, 230, 190)
            pygame.draw.rect(d, kl, rect)
            pygame.draw.rect(d, (190, 182, 210), rect, 1)
            n = self.g[i]
            if n:
                if self.puzzel[i]:
                    tkl = (34, 28, 50)
                elif n != self.oplossing[i] and self.app.hulp:
                    tkl = (200, 50, 70)
                else:
                    tkl = (90, 70, 190)
                UI.tekst(d, str(n), 40, tkl, rect.center, mid=True, vet=bool(self.puzzel[i]))
            elif self.noten[i]:
                for m in self.noten[i]:
                    mx = rect.x + 12 + (m - 1) % 3 * 23
                    my = rect.y + 12 + (m - 1) // 3 * 23
                    UI.tekst(d, str(m), 16, (120, 110, 150), (mx, my), mid=True, vet=False)
        for k in range(10):                      # dikke lijnen om de blokken
            w = 4 if k % 3 == 0 else 0
            if w:
                pygame.draw.line(d, (40, 32, 60), (BX + k * VAK, BY), (BX + k * VAK, BY + 9 * VAK), w)
                pygame.draw.line(d, (40, 32, 60), (BX, BY + k * VAK), (BX + 9 * VAK, BY + k * VAK), w)
        # rechts
        px = BX + 9 * VAK + 50
        duur = (self.eind or nu) - self.start
        UI.tekst(d, T("tijd") % tijd_tekst(duur), 26, UI.TEKST, (px, BY))
        UI.tekst(d, T("fouten_s") % self.fouten, 22, UI.ROOD if self.fouten else UI.ZACHT, (px, BY + 40))
        oud = self.beste.get(str(self.niveau))
        if oud is not None:
            UI.tekst(d, T("beste") % tijd_tekst(oud), 22, UI.GOUD, (px + 200, BY + 40))
        # cijferknoppen
        self.knoppen = []
        tel = {n: sum(1 for i in range(81) if self.g[i] == n and self.g[i] == self.oplossing[i]) for n in range(1, 10)}
        for n in range(1, 10):
            x = px + (n - 1) % 3 * 92
            y = BY + 100 + (n - 1) // 3 * 82
            vol = tel[n] >= 9
            self.knoppen.append(UI.Knop((x, y, 84, 74), str(n), lambda n=n: self.zet(n), UI.VAK if not vol else (40, 70, 56), 34, aan=not self.klaar))
        y = BY + 352
        self.knoppen.append(UI.Knop((px, y, 136, 60), T("potlood"), lambda: setattr(self, "potlood", not self.potlood),
                                    UI.GOUD if self.potlood else UI.VAK, 22))
        self.knoppen.append(UI.Knop((px + 144, y, 132, 60), T("gum"), lambda: self.zet(0), UI.VAK, 22))
        y += 76
        if self.klaar:
            regel = T("klaar_s") % tijd_tekst(duur) + ("  " + T("record") if self.record else "")
            kl = UI.GROEN
        else:
            regel = self.melding or T("uitleg_s")
            kl = UI.GOUD if self.melding else UI.TEKST
        for stuk in UI.Backgammon._knip(None, regel, 20, UI.W - px - 30)[:3]:
            UI.tekst(d, stuk, 20, kl, (px, y))
            y += 28
        if self.klaar:
            self.knoppen.append(UI.Knop((px, 620, 276, 60), UI.T("nog"), self.nieuw_potje, UI.GROEN, 22))
        else:
            self.knoppen.append(UI.Knop((px, 620, 120, 60), UI.T("tip"), self.geef_tip, UI.GOUD, 22))
            self.knoppen.append(UI.Knop((px + 130, 620, 146, 60), "%s: %s" % (UI.T("hulp"), UI.T("aan") if self.app.hulp else UI.T("uitm")),
                                        self.app.wissel_hulp, UI.VAK, 18))
        self.knoppen.append(UI.Knop((px, 690, 120, 56), UI.T("menu"), self.app.naar_menu, UI.VAK, 20))
        self.knoppen.append(UI.Knop((px + 130, 690, 146, 56), UI.T("regels"), lambda: setattr(self.app, "toon_regels", True), UI.VAK, 18))
        for k in self.knoppen:
            k.teken(d, muis)
        UI.tekst(d, T("toetsen_sudoku"), 15, UI.ZACHT, (BX, UI.H - 30), vet=False)
