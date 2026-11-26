# -*- coding: utf-8 -*-
"""DraveSpellenkast - Puzzel met de kunst van Roger (gemaakt met NightCafe).
Wissel-puzzel: klik twee stukjes om ze te verwisselen. Schuifpuzzel: schuif de stukjes naar het lege vakje.
Copyright (C) 2026 Dravenlock (Roger & Claudio). GNU GPL v3.0. De plaatjes: (C) Roger, Dravenlock."""
import json
import os
import random
import time

import pygame

UI = None          # wordt door main.py gezet

NIVEAUS = {1: (3, "wissel"), 2: (4, "wissel"), 3: (6, "wissel"), 4: (4, "schuif")}
GROOT = 640                          # het puzzelvlak
BX, BY = 40, 110

TX = {
    "puzzel": ("Puzzel", "Puzzle"),
    "kies_plaat": ("Kies een plaatje van Roger", "Choose one of Roger's pictures"),
    "willekeurig": ("Verras me!", "Surprise me!"),
    "wissel_uitleg": ("Klik op twee stukjes om ze te verwisselen. Een stukje op de goede plek zit vast.", "Click two pieces to swap them. A piece in the right place locks."),
    "schuif_uitleg": ("Klik op een stukje naast het lege vakje om het te schuiven.", "Click a piece next to the empty square to slide it."),
    "klaar_p": ("Klaar! In %d zetten en %s.", "Done! In %d moves and %s."),
    "record": ("Nieuw record!", "New record!"),
    "zetten": ("Zetten: %d", "Moves: %d"),
    "tijd": ("Tijd: %s", "Time: %s"),
    "beste": ("Beste: %s", "Best: %s"),
    "goed_n": ("Goed: %d van %d", "Right: %d of %d"),
    "voorbeeld": ("Voorbeeld", "Example"),
    "ander_plaatje": ("Ander plaatje", "Other picture"),
    "tip_p": ("Tip: het gouden stukje hoort op de gouden plek.", "Tip: the gold piece belongs in the gold spot."),
    "kunst_door": ("Kunst: Roger (Dravenlock), gemaakt met NightCafe", "Art: Roger (Dravenlock), made with NightCafe"),
    "toetsen_puzzel": ("Klik de stukjes  ·  T = tip  ·  Esc = menu", "Click the pieces  ·  T = tip  ·  Esc = menu"),
}


def T(k):
    if k in TX:
        v = TX[k]
        return v[0] if UI.TAAL == "nl" else v[1]
    return UI.T(k)


def kunst_map():
    return os.path.join(UI.HERE, "assets", "kunst")


def plaatjes():
    try:
        return sorted(f for f in os.listdir(kunst_map()) if f.lower().endswith((".jpg", ".png")))
    except Exception:
        return []


def tijd_tekst(s):
    s = int(s)
    return "%d:%02d" % (s // 60, s % 60)


def oplosbaar(volgorde, n):
    """Een schuifpuzzel is alleen op te lossen bij de goede 'pariteit'."""
    rij = [x for x in volgorde if x != n * n - 1]
    inversies = sum(1 for i in range(len(rij)) for j in range(i + 1, len(rij)) if rij[i] > rij[j])
    if n % 2 == 1:
        return inversies % 2 == 0
    leeg_rij_van_onder = n - volgorde.index(n * n - 1) // n
    return (inversies + leeg_rij_van_onder) % 2 == 1


class Puzzel:
    def __init__(self, app, niveau):
        self.app = app
        self.niveau = niveau
        self.n, self.soort = NIVEAUS[niveau]
        self.knoppen = []
        self.lijst = plaatjes()
        self.cache_thumb = {}
        self.kiezen = True                 # eerst een plaatje kiezen
        self.beste = self.laad_beste()
        self.plaat = None

    # ---------- records
    def beste_pad(self):
        return os.path.join(UI.DATA, "puzzel_records.json")

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

    def sleutel(self):
        return "%s_%d" % (self.soort, self.n)

    # ---------- beginnen
    def kies(self, naam):
        try:
            beeld = pygame.image.load(os.path.join(kunst_map(), naam)).convert()
        except Exception:
            UI.log_fout("puzzel: kan %s niet laden" % naam)
            return
        self.plaat = pygame.transform.smoothscale(beeld, (GROOT, GROOT))
        self.plaat_naam = naam
        self.kiezen = False
        self.nieuw_potje()
        self.app.geluid.speel("klik")

    def nieuw_potje(self):
        n = self.n
        stuk = GROOT // n
        self.stuk = stuk
        self.stukken = [self.plaat.subsurface((i % n * stuk, i // n * stuk, stuk, stuk)) for i in range(n * n)]
        while True:
            volgorde = list(range(n * n))
            random.shuffle(volgorde)
            if self.soort == "schuif" and not oplosbaar(volgorde, n):
                continue
            if sum(1 for i, x in enumerate(volgorde) if i == x) <= n // 2:
                break
        self.plek = volgorde                # plek[vak] = welk stukje daar ligt
        self.zetten = 0
        self.start = time.time()
        self.eind = None
        self.klaar = False
        self.gekozen = None
        self.tip = None
        self.melding = ""
        self.record = False
        self.anim = {}                       # vak -> (van_xy, starttijd)

    def ander_plaatje(self):
        self.kiezen = True
        self.app.geluid.speel("klik")

    # ---------- zetten
    def vak_rect(self, v):
        return pygame.Rect(BX + v % self.n * self.stuk, BY + v // self.n * self.stuk, self.stuk, self.stuk)

    def vak_op(self, pos):
        x, y = pos
        if BX <= x < BX + self.n * self.stuk and BY <= y < BY + self.n * self.stuk:
            return (y - BY) // self.stuk * self.n + (x - BX) // self.stuk
        return None

    def vast(self, v):
        return self.soort == "wissel" and self.plek[v] == v

    def wissel(self, a, b):
        self.anim[a] = (self.vak_rect(b).topleft, time.time())
        self.anim[b] = (self.vak_rect(a).topleft, time.time())
        self.plek[a], self.plek[b] = self.plek[b], self.plek[a]
        self.zetten += 1
        self.tip = None
        self.app.geluid.speel("goed" if self.plek[a] == a or self.plek[b] == b else "zet")
        self.controleer()

    def controleer(self):
        if all(self.plek[i] == i for i in range(self.n * self.n)):
            self.klaar = True
            self.eind = time.time()
            duur = self.eind - self.start
            oud = self.beste.get(self.sleutel())
            if oud is None or duur < oud:
                self.beste[self.sleutel()] = duur
                self.bewaar_beste()
                self.record = True
            self.app.geluid.speel("win")

    def klik(self, pos):
        if self.kiezen:
            for naam, r in self.thumb_rects():
                if r.collidepoint(pos):
                    self.kies(naam)
                    return
            return
        if self.klaar:
            return
        v = self.vak_op(pos)
        if v is None:
            return
        if self.soort == "schuif":
            leeg = self.plek.index(self.n * self.n - 1)
            r1, c1 = divmod(v, self.n)
            r2, c2 = divmod(leeg, self.n)
            if abs(r1 - r2) + abs(c1 - c2) == 1:
                self.wissel(v, leeg)
            else:
                self.app.geluid.speel("fout")
            return
        if self.vast(v):
            self.app.geluid.speel("fout")
            return
        if self.gekozen is None:
            self.gekozen = v
            self.app.geluid.speel("klik")
        elif self.gekozen == v:
            self.gekozen = None
        else:
            a, self.gekozen = self.gekozen, None
            self.wissel(a, v)

    def geef_tip(self):
        if self.kiezen or self.klaar:
            return
        if self.soort == "schuif":
            leeg = self.plek.index(self.n * self.n - 1)
            buren = [x for x in range(self.n * self.n)
                     if abs(x // self.n - leeg // self.n) + abs(x % self.n - leeg % self.n) == 1]
            # het buurstukje dat het dichtst bij zijn eigen plek komt
            def afstand(v):
                s = self.plek[v]
                return abs(s // self.n - leeg // self.n) + abs(s % self.n - leeg % self.n)
            v = min(buren, key=afstand)
            self.tip = (v, leeg)
        else:
            fout = [v for v in range(self.n * self.n) if self.plek[v] != v]
            if not fout:
                return
            doel = random.choice(fout)               # de plek...
            waar = self.plek.index(doel)             # ...en waar zijn stukje nu ligt
            self.tip = (waar, doel)
        self.melding = T("tip_p")
        self.app.geluid.speel("goed")

    def update(self):
        pass

    def toets(self, e):
        if e.key == pygame.K_ESCAPE:
            if not self.kiezen:
                self.kiezen = True
            else:
                self.app.naar_menu()
        elif e.key == pygame.K_t:
            self.geef_tip()
        elif self.klaar and e.key in (pygame.K_SPACE, pygame.K_RETURN):
            self.nieuw_potje()

    # ---------- tekenen
    def thumb_rects(self):
        uit = []
        kol, maat, gap = 8, 132, 12
        x0 = (UI.W - (kol * maat + (kol - 1) * gap)) // 2
        for i, naam in enumerate(self.lijst):
            uit.append((naam, pygame.Rect(x0 + i % kol * (maat + gap), 110 + i // kol * (maat + gap), maat, maat)))
        return uit

    def teken_kiezen(self, d, muis):
        UI.tekst(d, T("kies_plaat"), 30, UI.TEKST, (UI.W // 2, 66), mid=True)
        for naam, r in self.thumb_rects():
            if naam not in self.cache_thumb:
                try:
                    im = pygame.image.load(os.path.join(kunst_map(), naam)).convert()
                    self.cache_thumb[naam] = pygame.transform.smoothscale(im, (r.w, r.h))
                except Exception:
                    self.cache_thumb[naam] = None
            th = self.cache_thumb[naam]
            if th:
                d.blit(th, r)
            hover = r.collidepoint(muis)
            pygame.draw.rect(d, UI.GOUD if hover else UI.RAND, r.inflate(6, 6), 4 if hover else 2, border_radius=8)
        self.knoppen = [UI.Knop((UI.W // 2 - 150, UI.H - 90, 300, 64), T("willekeurig"),
                                lambda: self.kies(random.choice(self.lijst)) if self.lijst else None, UI.GOUD, 24),
                        UI.Knop((40, UI.H - 90, 180, 64), UI.T("menu"), self.app.naar_menu, UI.VAK, 24)]
        UI.tekst(d, T("kunst_door"), 16, UI.ZACHT, (UI.W - 40, UI.H - 40), rechts=True, vet=False)

    def teken(self, d, muis):
        d.fill(UI.ACHTER)
        UI.tekst(d, T("puzzel"), 40, UI.ACCENT, (40, 14))
        if self.kiezen:
            self.teken_kiezen(d, muis)
            for k in self.knoppen:
                k.teken(d, muis)
            return
        bord = pygame.Rect(BX - 8, BY - 8, self.n * self.stuk + 16, self.n * self.stuk + 16)
        pygame.draw.rect(d, (44, 38, 64), bord, border_radius=12)
        nu = time.time()
        leeg = self.n * self.n - 1 if self.soort == "schuif" and not self.klaar else None
        for v in range(self.n * self.n):
            s = self.plek[v]
            r = self.vak_rect(v)
            if s == leeg:
                pygame.draw.rect(d, (28, 24, 40), r)
                continue
            x, y = r.topleft
            if v in self.anim:
                (vx, vy), t0 = self.anim[v]
                f = min(1.0, (nu - t0) / 0.18)
                if f >= 1:
                    del self.anim[v]
                f = f * f * (3 - 2 * f)
                x, y = vx + (x - vx) * f, vy + (y - vy) * f
            d.blit(self.stukken[s], (x, y))
            if not self.klaar:
                pygame.draw.rect(d, (20, 16, 30), (x, y, self.stuk, self.stuk), 1)
                if self.vast(v) and self.app.hulp:
                    pygame.draw.rect(d, UI.GROEN, (x + 2, y + 2, self.stuk - 4, self.stuk - 4), 2)
        if self.gekozen is not None:
            pygame.draw.rect(d, UI.ACCENT, self.vak_rect(self.gekozen), 5)
        if self.tip:
            pygame.draw.rect(d, UI.GOUD, self.vak_rect(self.tip[0]), 5)
            pygame.draw.rect(d, UI.GOUD, self.vak_rect(self.tip[1]).inflate(-14, -14), 3)
        # rechts
        px = BX + GROOT + 50
        if self.app.hulp:
            UI.tekst(d, T("voorbeeld"), 18, UI.ZACHT, (px, BY - 4), vet=False)
            klein = pygame.transform.smoothscale(self.plaat, (240, 240))
            d.blit(klein, (px, BY + 20))
            pygame.draw.rect(d, UI.RAND, (px, BY + 20, 240, 240), 2)
        y = BY + 280
        duur = (self.eind or time.time()) - self.start
        UI.tekst(d, T("zetten") % self.zetten, 24, UI.TEKST, (px, y))
        UI.tekst(d, T("tijd") % tijd_tekst(duur), 24, UI.TEKST, (px + 200, y))
        oud = self.beste.get(self.sleutel())
        if oud is not None:
            UI.tekst(d, T("beste") % tijd_tekst(oud), 20, UI.GOUD, (px, y + 36))
        goed = sum(1 for i in range(self.n * self.n) if self.plek[i] == i)
        UI.tekst(d, T("goed_n") % (goed, self.n * self.n), 20, UI.ZACHT, (px + 200, y + 36), vet=False)
        y += 80
        if self.klaar:
            regel = T("klaar_p") % (self.zetten, tijd_tekst(duur)) + ("  " + T("record") if self.record else "")
            kl = UI.GROEN
        else:
            regel = self.melding or (T("schuif_uitleg") if self.soort == "schuif" else T("wissel_uitleg"))
            kl = UI.GOUD if self.melding else UI.TEKST
        for stuk in UI.Backgammon._knip(None, regel, 20, UI.W - px - 30)[:3]:
            UI.tekst(d, stuk, 20, kl, (px, y))
            y += 28
        self.knoppen = []
        if self.klaar:
            self.knoppen.append(UI.Knop((px, 570, 250, 60), UI.T("nog"), self.nieuw_potje, UI.GROEN, 22))
        else:
            self.knoppen.append(UI.Knop((px, 570, 120, 60), UI.T("tip"), self.geef_tip, UI.GOUD, 22))
            self.knoppen.append(UI.Knop((px + 130, 570, 200, 60), "%s: %s" % (UI.T("hulp"), UI.T("aan") if self.app.hulp else UI.T("uitm")),
                                        self.app.wissel_hulp, UI.VAK, 20))
        self.knoppen.append(UI.Knop((px, 640, 250, 56), T("ander_plaatje"), self.ander_plaatje, UI.VAK, 20))
        self.knoppen.append(UI.Knop((px, 706, 120, 56), UI.T("menu"), self.app.naar_menu, UI.VAK, 20))
        self.knoppen.append(UI.Knop((px + 130, 706, 200, 56), UI.T("regels"), lambda: setattr(self.app, "toon_regels", True), UI.VAK, 20))
        for k in self.knoppen:
            k.teken(d, muis)
        UI.tekst(d, T("kunst_door"), 15, UI.ZACHT, (BX, UI.H - 30), vet=False)
