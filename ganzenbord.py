# -*- coding: utf-8 -*-
"""DraveSpellenkast - Ganzenbord: het oude Hollandse dobbelspel, met de gans, de brug, de herberg, de put,
het doolhof, de gevangenis en de dood. Wie precies op 63 komt, wint.
Tegen 1 tot 3 computerspelers of online. Copyright (C) 2026 Dravenlock (Roger & Claudio). GNU GPL v3.0."""
import math
import random
import time

import pygame

UI = None          # wordt door main.py gezet

GANZEN = {5, 9, 14, 18, 23, 27, 32, 36, 41, 45, 50, 54, 59}
BRUG, HERBERG, PUT, DOOLHOF, GEVANGENIS, DOOD, EIND = 6, 19, 31, 42, 52, 58, 63
PION = [(127, 119, 221), (224, 184, 90), (214, 72, 96), (63, 166, 107)]
KOL, RIJ = 9, 7
VAK_W, VAK_H = 78, 74
BX, BY = 40, 92

TX = {
    "gans": ("Ganzenbord", "Game of the Goose"),
    "gooi": ("Gooi!", "Roll!"),
    "jouw_beurt": ("Jouw beurt: gooi de dobbelstenen.", "Your turn: roll the dice."),
    "beurt_van": ("%s is aan de beurt.", "%s's turn."),
    "gooit": ("%s gooit %d en %d.", "%s rolls %d and %d."),
    "gans_v": ("Een gans! Nog een keer zo ver.", "A goose! Again the same distance."),
    "brug_v": ("De brug: je mag door naar 12.", "The bridge: go on to 12."),
    "herberg_v": ("De herberg: een beurt overslaan.", "The inn: miss a turn."),
    "put_v": ("In de put! Wacht tot iemand anders erin valt.", "In the well! Wait until someone else falls in."),
    "doolhof_v": ("Het doolhof: terug naar 39.", "The maze: back to 39."),
    "gevangenis_v": ("De gevangenis! Wacht tot iemand anders er komt.", "Prison! Wait until someone else comes."),
    "dood_v": ("De dood: helemaal terug naar het begin!", "Death: all the way back to the start!"),
    "terug_v": ("Te ver! Terug lopen vanaf 63.", "Too far! Walk back from 63."),
    "start_63": ("6 en 3 bij de eerste worp: door naar 26!", "6 and 3 on the first roll: on to 26!"),
    "start_54": ("5 en 4 bij de eerste worp: door naar 53!", "5 and 4 on the first roll: on to 53!"),
    "vrij": ("%s is vrij!", "%s is free!"),
    "slaat_over": ("%s slaat een beurt over.", "%s misses a turn."),
    "zit_vast": ("%s zit nog vast.", "%s is still stuck."),
    "wint": ("%s staat op 63 en wint!", "%s reaches 63 and wins!"),
    "computer_n": ("Computer %d", "Computer %d"),
    "toetsen_gans": ("Spatie of klik Gooi!  ·  Esc = menu", "Space or click Roll!  ·  Esc = menu"),
}


def T(k):
    if k in TX:
        v = TX[k]
        return v[0] if UI.TAAL == "nl" else v[1]
    return UI.T(k)


def vak_plek():
    """Een spiraal van buiten naar binnen: vak 1 linksonder, vak 63 in het midden."""
    plek = {}
    top, onder, links, rechts = 0, RIJ - 1, 0, KOL - 1
    n = 1
    r, c = onder, links
    richting = 0
    gezien = set()
    while n <= 63:
        plek[n] = (r, c)
        gezien.add((r, c))
        n += 1
        for _ in range(4):
            dr, dc = [(0, 1), (-1, 0), (0, -1), (1, 0)][richting]
            nr, nc = r + dr, c + dc
            if 0 <= nr < RIJ and 0 <= nc < KOL and (nr, nc) not in gezien:
                r, c = nr, nc
                break
            richting = (richting + 1) % 4
    return plek


PLEK = vak_plek()


def vak_rect(n):
    if n == 0:
        return pygame.Rect(BX - 6, BY + RIJ * VAK_H + 8, VAK_W, 40)
    r, c = PLEK[n]
    return pygame.Rect(BX + c * VAK_W, BY + r * VAK_H, VAK_W - 4, VAK_H - 4)


def teken_ster(d, cx, cy, r, kl):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    pygame.draw.polygon(d, kl, pts)


class Ganzenbord:
    def __init__(self, app, aantal):
        self.app = app
        self.aantal = aantal              # aantal computerspelers (1-3)
        self.knoppen = []
        self.gewonnen = [0] * 4
        self.nieuw_potje()

    def spelers(self):
        return 1 + self.aantal

    def naam(self, i):
        return UI.T("jij") if i == 0 else T("computer_n") % i

    def nieuw_potje(self):
        n = self.spelers()
        self.pos = [0] * n
        self.overslaan = [0] * n
        self.vast = [None] * n             # "put" of "gevangenis"
        self.eerste = [True] * n
        self.beurt = 0
        self.klaar = False
        self.uitslag = ""
        self.melding = ""
        self.stenen = (0, 0)
        self.loop = None                   # [speler, lijst van vakjes nog te lopen, daarna-functie]
        self.rol_t = 0.0
        self.comp_t = time.time() + 1.0
        self.log = []

    def mijn_idx(self):
        return 0

    def is_mens(self, i):
        return i == 0

    # ---------- regels
    def gooi(self, a=None, b=None):
        if self.klaar or self.loop or time.time() < self.rol_t:
            return None
        a = a or random.randint(1, 6)
        b = b or random.randint(1, 6)
        self.stenen = (a, b)
        self.rol_t = time.time() + 0.5
        self.app.geluid.speel("klik")
        self.zeg(T("gooit") % (self.naam(self.beurt), a, b))
        self.zet(self.beurt, a, b)
        return a, b

    def zeg(self, tekst):
        self.melding = tekst
        self.log.append(tekst)
        self.log = self.log[-6:]

    def zet(self, sp, a, b):
        som = a + b
        if self.eerste[sp] and self.pos[sp] == 0 and {a, b} in ({6, 3}, {5, 4}):
            self.eerste[sp] = False
            doel = 26 if {a, b} == {6, 3} else 53
            self.zeg(T("start_63") if doel == 26 else T("start_54"))
            self.loop = [sp, list(range(self.pos[sp] + 1, doel + 1)), lambda: self.aangekomen(sp, som)]
            return
        self.eerste[sp] = False
        self.loop_stappen(sp, som)

    def loop_stappen(self, sp, som):
        p, richting, stappen = self.pos[sp], 1, []
        for _ in range(som):
            if p >= EIND:
                richting = -1                    # te ver: vanaf 63 terug lopen
            p += richting
            stappen.append(p)
        if richting == -1:
            self.zeg(T("terug_v"))
        self.loop = [sp, stappen, lambda: self.aangekomen(sp, som)]

    def aangekomen(self, sp, som):
        p = self.pos[sp]
        if p == EIND:
            self.klaar = True
            self.gewonnen[sp] += 1
            self.uitslag = T("wint") % self.naam(sp)
            self.app.geluid.speel("win" if sp == self.mijn_idx() else "verlies")
            self.einde_gemeld(sp)
            return
        if p in GANZEN:
            self.zeg(T("gans_v"))
            self.app.geluid.speel("goed")
            self.loop_stappen(sp, som)
            return
        if p == BRUG:
            self.zeg(T("brug_v"))
            self.loop = [sp, list(range(7, 13)), lambda: self.volgende()]
            return
        if p == DOOLHOF:
            self.zeg(T("doolhof_v"))
            self.loop = [sp, [41, 40, 39], lambda: self.volgende()]
            return
        if p == DOOD:
            self.zeg(T("dood_v"))
            self.app.geluid.speel("verlies")
            self.pos[sp] = 0
            self.volgende()
            return
        if p == HERBERG:
            self.zeg(T("herberg_v"))
            self.overslaan[sp] = 1
        if p in (PUT, GEVANGENIS):
            self.zeg(T("put_v") if p == PUT else T("gevangenis_v"))
            for i in range(self.spelers()):            # wie er al zat, is nu vrij
                if i != sp and self.pos[i] == p and self.vast[i]:
                    self.vast[i] = None
                    self.zeg(T("vrij") % self.naam(i))
            self.vast[sp] = "put" if p == PUT else "gevangenis"
        self.volgende()

    def einde_gemeld(self, sp):
        pass

    def volgende(self):
        n = self.spelers()
        sp = self.beurt
        for _ in range(n * 3):
            sp = (sp + 1) % n
            if self.vast[sp]:
                continue
            if self.overslaan[sp]:
                self.overslaan[sp] -= 1
                continue
            break
        self.beurt = sp
        self.comp_t = time.time() + 1.0

    def update(self):
        if self.loop:
            if time.time() < self.rol_t:
                return
            sp, stappen, daarna = self.loop
            if stappen:
                self.pos[sp] = stappen.pop(0)
                self.rol_t = time.time() + 0.16
                self.app.geluid.speel("zet") if not stappen else None
                return
            self.loop = None
            daarna()
            return
        if self.klaar:
            return
        if all(self.vast[i] for i in range(self.spelers())):     # iedereen vast: de put/gevangenis gaat open
            for i in range(self.spelers()):
                self.vast[i] = None
        if not self.is_mens(self.beurt) and self.computer_mag() and time.time() >= self.comp_t:
            self.gooi()

    def computer_mag(self):
        return True

    # ---------- invoer
    def klik(self, pos):
        pass

    def toets(self, e):
        if e.key == pygame.K_ESCAPE:
            self.app.naar_menu()
        elif self.klaar and e.key in (pygame.K_SPACE, pygame.K_RETURN):
            self.nieuw_potje()
        elif e.key in (pygame.K_SPACE, pygame.K_RETURN):
            self.ik_gooi()

    def ik_gooi(self):
        if self.beurt == self.mijn_idx():
            self.gooi()

    # ---------- tekenen
    def teken_gans(self, d, cx, cy, s=1.0, kl=(250, 250, 250)):
        pygame.draw.ellipse(d, kl, (cx - 18 * s, cy - 6 * s, 30 * s, 18 * s))
        pygame.draw.line(d, kl, (cx + 8 * s, cy), (cx + 12 * s, cy - 16 * s), max(2, int(5 * s)))
        pygame.draw.circle(d, kl, (int(cx + 13 * s), int(cy - 18 * s)), max(2, int(5 * s)))
        pygame.draw.polygon(d, (240, 150, 60), [(cx + 17 * s, cy - 19 * s), (cx + 25 * s, cy - 17 * s), (cx + 17 * s, cy - 15 * s)])

    def teken_vak(self, d, n):
        r = vak_rect(n)
        kl = (60, 52, 92)
        if n in GANZEN:
            kl = (70, 110, 170)
        elif n in (BRUG, HERBERG, PUT, DOOLHOF, GEVANGENIS):
            kl = (150, 104, 60)
        elif n == DOOD:
            kl = (110, 40, 56)
        elif n == EIND:
            kl = (190, 150, 60)
        pygame.draw.rect(d, kl, r, border_radius=10)
        pygame.draw.rect(d, UI.RAND, r, 2, border_radius=10)
        UI.tekst(d, str(n), 16, (230, 224, 245), (r.x + 6, r.y + 3), vet=True)
        cx, cy = r.centerx, r.centery + 8
        if n in GANZEN:
            self.teken_gans(d, cx, cy + 4, 0.9)
        elif n == BRUG:
            pygame.draw.arc(d, (240, 230, 210), (cx - 22, cy - 12, 44, 30), 0, math.pi, 4)
            pygame.draw.line(d, (240, 230, 210), (cx - 26, cy + 3), (cx + 26, cy + 3), 4)
        elif n == HERBERG:
            pygame.draw.rect(d, (240, 230, 210), (cx - 14, cy - 6, 28, 20))
            pygame.draw.polygon(d, (200, 80, 70), [(cx - 18, cy - 6), (cx + 18, cy - 6), (cx, cy - 20)])
        elif n == PUT:
            pygame.draw.ellipse(d, (30, 24, 40), (cx - 18, cy - 8, 36, 18))
            pygame.draw.ellipse(d, (200, 190, 170), (cx - 18, cy - 8, 36, 18), 3)
        elif n == DOOLHOF:
            for i in range(3):
                pygame.draw.rect(d, (240, 230, 210), (cx - 16 + i * 5, cy - 14 + i * 5, 32 - i * 10, 28 - i * 10), 2)
        elif n == GEVANGENIS:
            for i in range(4):
                pygame.draw.line(d, (240, 230, 210), (cx - 15 + i * 10, cy - 16), (cx - 15 + i * 10, cy + 14), 3)
        elif n == DOOD:
            pygame.draw.circle(d, (240, 236, 230), (cx, cy - 2), 14)
            pygame.draw.circle(d, (40, 20, 30), (cx - 5, cy - 4), 4)
            pygame.draw.circle(d, (40, 20, 30), (cx + 5, cy - 4), 4)
            pygame.draw.rect(d, (240, 236, 230), (cx - 8, cy + 8, 16, 7))
        elif n == EIND:
            self.teken_gans(d, cx, cy + 4, 1.1, (255, 240, 200))
            teken_ster(d, cx - 22, cy - 16, 8, (255, 255, 255))

    def teken(self, d, muis):
        d.fill(UI.ACHTER)
        UI.tekst(d, T("gans"), 40, UI.ACCENT, (40, 14))
        bord = pygame.Rect(BX - 12, BY - 12, KOL * VAK_W + 20, RIJ * VAK_H + 20)
        pygame.draw.rect(d, (40, 34, 60), bord, border_radius=18)
        for n in range(1, 64):
            self.teken_vak(d, n)
        UI.tekst(d, "Start", 18, UI.ZACHT, (BX - 4, BY + RIJ * VAK_H + 14))
        # pionnen
        n = self.spelers()
        for i in range(n):
            r = vak_rect(self.pos[i]) if self.pos[i] else pygame.Rect(BX + 60 + i * 36, BY + RIJ * VAK_H + 10, 30, 30)
            dx, dy = [(-16, -10), (16, -10), (-16, 14), (16, 14)][i] if self.pos[i] else (0, 0)
            x, y = r.centerx + dx, r.centery + dy
            pygame.draw.circle(d, (20, 16, 30), (x, y + 3), 13)
            pygame.draw.circle(d, PION[i], (x, y), 13)
            pygame.draw.circle(d, (255, 255, 255), (x - 4, y - 4), 3)
            if i == self.beurt and not self.klaar:
                pygame.draw.circle(d, (255, 255, 255), (x, y), 16, 3)
        # rechts
        px = BX + KOL * VAK_W + 40
        for i in range(n):
            y = 96 + i * 58
            pygame.draw.circle(d, PION[i], (px + 14, y + 16), 13)
            kl = UI.TEKST if i == self.beurt else UI.ZACHT
            extra = ""
            if self.vast[i]:
                extra = "  (put)" if self.vast[i] == "put" else "  (gevangenis)" if UI.TAAL == "nl" else "  (prison)"
            elif self.overslaan[i]:
                extra = "  (herberg)" if UI.TAAL == "nl" else "  (inn)"
            UI.tekst(d, "%s  %d%s" % (self.naam(i), self.pos[i], extra), 22, kl, (px + 36, y + 3))
            teken_ster(d, UI.W - 62, y + 16, 9, UI.GOUD)
            UI.tekst(d, "%d" % self.gewonnen[i], 18, UI.GOUD, (UI.W - 30, y + 6), rechts=True)
            if i == self.beurt and not self.klaar:
                pygame.draw.rect(d, UI.ACCENT, (px - 6, y - 4, UI.W - px - 20, 44), 2, border_radius=10)
        # dobbelstenen
        y = 96 + n * 58 + 10
        if self.stenen[0]:
            UI.teken_dobbel(d, px, y, self.stenen[0], 60)
            UI.teken_dobbel(d, px + 74, y, self.stenen[1], 60)
        y += 80
        regels = [self.uitslag] if self.klaar else self.log[-3:] or [T("jouw_beurt")]
        for regel in regels:
            for stuk in UI.Backgammon._knip(None, regel, 19, UI.W - px - 24)[:2]:
                UI.tekst(d, stuk, 19, UI.GOUD if self.klaar else UI.TEKST, (px, y), vet=regel == regels[-1])
                y += 24
        self.knoppen = []
        mijn = not self.klaar and self.beurt == self.mijn_idx() and not self.loop
        if self.klaar:
            self.knoppen.append(UI.Knop((px, 590, UI.W - px - 30, 64), UI.T("nog"), self.nieuw_potje, UI.GROEN, 24))
        else:
            self.knoppen.append(UI.Knop((px, 590, UI.W - px - 30, 64), T("gooi"), self.ik_gooi, UI.GOUD if mijn else UI.VAK, 28, aan=mijn))
        self.knoppen.append(UI.Knop((px, 670, 150, 56), UI.T("menu"), self.app.naar_menu, UI.VAK, 22))
        self.knoppen.append(UI.Knop((px + 160, 670, UI.W - px - 190, 56), UI.T("regels"), lambda: setattr(self.app, "toon_regels", True), UI.VAK, 20))
        for k in self.knoppen:
            k.teken(d, muis)
        UI.tekst(d, T("toetsen_gans"), 16, UI.ZACHT, (px, UI.H - 30), vet=False)


# ------------------------------------------------------------------ online: met z'n tweeën
class OnlineGanzenbord(Ganzenbord):
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
        Ganzenbord.__init__(self, app, 1)
        self.lijn = UI.online.Lijn(adres, code, {"t": "hallo", "spel": "gans", "naam": naam, "token": token}, pad="zet/kamer")

    def mijn_idx(self):
        return self.ik if self.ik is not None else 0

    def is_mens(self, i):
        return True

    def naam(self, i):
        if self.ik is None:
            return UI.T("speler%d" % (i + 1))
        return UI.T("jij") if i == self.ik else (self.ander or UI.T("tegenspeler"))

    def nieuw_potje(self):
        if getattr(self, "lijn", None) is not None:
            self.lijn.stuur({"t": "nieuw"})
            self.app.geluid.speel("klik")
            return
        Ganzenbord.nieuw_potje(self)

    def ik_gooi(self):
        if self.fase != "spel" or self.beurt != self.ik or self.loop or self.klaar:
            return
        a, b = random.randint(1, 6), random.randint(1, 6)
        # eerst kijken waar het eindigt (op een kopie), zodat de server de beurt goed doorgeeft
        kopie = self.na_worp(a, b)
        if self.lijn.stuur({"t": "zet", "z": {"a": a, "b": b}, "nog": kopie["beurt"] == self.ik,
                            "einde": self.ik if kopie["klaar"] else None}):
            self.n_zetten += 1
            self.gooi(a, b)
        else:
            self.status = UI.T("geen_server")

    def na_worp(self, a, b):
        """Speel de worp na op een stille kopie om te weten wie er daarna aan de beurt is."""
        k = OnlineGanzenbord.__new__(OnlineGanzenbord)
        k.__dict__.update({x: (v[:] if isinstance(v, list) else v) for x, v in self.__dict__.items()})
        k.app = _Stil()
        k.lijn = None
        k.log = []
        k.stenen = (a, b)
        k.rol_t = 0
        k.zet(k.beurt, a, b)
        while k.loop:
            sp, stappen, daarna = k.loop
            if stappen:
                k.pos[sp] = stappen.pop(0)
                continue
            k.loop = None
            daarna()
        return {"beurt": k.beurt, "klaar": k.klaar}

    def computer_mag(self):
        return False

    def update(self):
        Ganzenbord.update(self)
        if self.lijn is None or self.loop:
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
                self.stand = b
        st = getattr(self, "stand", None)
        if st and not self.loop:
            try:
                self.pas_toe(st)
            except Exception:
                import traceback
                UI.log_fout(traceback.format_exc())

    def pas_toe(self, st):
        self.ik = st["ik"]
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
            Ganzenbord.nieuw_potje(self)
            self.beurt = st.get("eerste", 0)
            self.n_zetten = 0
            self.einde_gezien = False
        if len(lijst) > self.n_zetten:                       # één worp tegelijk, met de animatie
            d = lijst[self.n_zetten]
            z = d.get("z") or {}
            self.n_zetten += 1
            self.beurt = d.get("sp", self.beurt)
            self.rol_t = 0
            self.gooi(int(z.get("a", 1)), int(z.get("b", 1)))
            return
        self.gewonnen = list(st.get("score", [0, 0])) + [0, 0]
        if self.fase == "einde":
            self.klaar = True
            if not self.einde_gezien:
                self.einde_gezien = True
        elif not self.loop:
            self.klaar = False
            self.beurt = st["beurt"]

    def teken(self, d, muis):
        Ganzenbord.teken(self, d, muis)
        UI.tekst(d, UI.T("kamer") % self.code, 20, UI.ACCENT, (330, 30))
        px = BX + KOL * VAK_W + 40
        if self.status:
            UI.tekst(d, self.status, 18, UI.ROOD, (px, 560))
        elif self.ik is not None and self.ander and not self.verbonden[1 - self.ik]:
            UI.tekst(d, UI.T("ander_weg") % self.ander, 18, UI.GOUD, (px, 560))
        if self.fase == "wachten":
            UI.tekst(d, UI.T("wacht_ander") % self.code, 18, UI.TEKST, (px, 430))
            UI.tekst(d, self.code, 44, UI.GOUD, (px, 470))

    def stop(self):
        if self.lijn:
            self.lijn.stop()


class _Stil:
    """Een app zonder geluid, voor het stil narekenen van een worp."""
    class _G:
        def speel(self, *a):
            pass
    geluid = _G()
