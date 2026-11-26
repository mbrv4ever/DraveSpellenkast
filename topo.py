# -*- coding: utf-8 -*-
"""Topografie voor de DraveSpellenkast - naar het oude C64-spel, maar dan met grote knoppen.
Waar ligt het? Provincies, hoofdsteden, steden en alle 342 gemeentes van Nederland (2026).
Alleen of met z'n tweeën (om de beurt). Kaart: CBS 2026 (open data), plaatsen: GeoNames (CC-BY 4.0)."""
import json
import math
import os
import random

import pygame

UI = None          # wordt door main.py gezet (tekst, Knop, kleuren, T, ...)

AANTAL = 10        # vragen per speler
KM_PX = 111.0 / 266.0

ONDERWERPEN = ["prov", "hoofd", "groot", "steden", "alle", "gem"]
TXT = {
    "t_wat": ("Wat wil je oefenen?", "What do you want to practise?"),
    "t_hoe": ("Hoe?", "How?"), "t_wie": ("Wie speelt?", "Who plays?"),
    "o_prov": ("Provincies (12)", "Provinces (12)"), "o_hoofd": ("Hoofdsteden (12)", "Capitals (12)"),
    "o_groot": ("Grote steden", "Big cities"), "o_steden": ("Steden", "Cities"),
    "o_alle": ("Alle plaatsen (moeilijk)", "All towns (hard)"), "o_gem": ("Alle 342 gemeentes", "All 342 municipalities"),
    "h_klik": ("Klik op de kaart", "Click on the map"), "h_kies": ("Kies uit 4 namen", "Choose from 4 names"),
    "w_een": ("Alleen", "Alone"), "w_twee": ("Met z'n tweeën", "Two players"),
    "start": ("Start!", "Start!"), "beste": ("Beste score: %d van %d", "Best score: %d of %d"),
    "waar": ("Waar ligt", "Where is"), "welke": ("Wat is dit?", "What is this?"),
    "welke_sub": ("Kijk naar het gouden stuk op de kaart.", "Look at the gold part of the map."),
    "klik_uitleg": ("Klik op de kaart.", "Click on the map."),
    "goed": ("Goed! +%d", "Right! +%d"), "bijna": ("Bijna! +%d", "Almost! +%d"), "mis": ("Mis...", "Missed..."),
    "ernaast": ("%d km ernaast", "%d km off"), "het_is": ("Het was: %s", "It was: %s"),
    "volgende": ("Volgende", "Next"), "uitslag": ("Uitslag", "Result"),
    "vraag": ("Vraag %d van %d", "Question %d of %d"), "punten": ("%d punten", "%d points"),
    "in_prov": ("Tip: het ligt in %s", "Tip: it is in %s"), "tip_kost": ("Tip (-5)", "Tip (-5)"),
    "nieuw_rec": ("Nieuw record!", "New record!"), "gelijkspel": ("Gelijkspel!", "A tie!"),
    "wint": ("%s wint!", "%s wins!"), "klaar": ("Klaar!", "Done!"),
    "lof3": ("Topograaf! Je kent Nederland op je duimpje.", "Topographer! You know the Netherlands by heart."),
    "lof2": ("Goed gedaan! Nog even oefenen en je kent ze allemaal.", "Well done! A bit more practice and you know them all."),
    "lof1": ("Leuk geprobeerd! Speel nog eens, dan leer je ze vanzelf.", "Nice try! Play again and you'll learn them."),
    "toetsen_t": ("Spatie = volgende   ·   1-4 = naam kiezen   ·   M = muziek   ·   Esc = menu",
                  "Space = next   ·   1-4 = choose name   ·   M = music   ·   Esc = menu"),
    "of_spatie": ("(of druk op de spatiebalk)", "(or press the space bar)"),
    "h_vlieg": ("Vlieg erheen (helikopter)", "Fly there (helicopter)"),
    "vlieg_naar": ("Vlieg naar", "Fly to"),
    "vlieg_uitleg": ("Pijltjes = vliegen, spatie = landen. Of klik op de kaart: dan vliegt hij zelf.",
                     "Arrows = fly, space = land. Or click on the map: it flies by itself."),
    "landen": ("Landen", "Land"), "brandstof": ("Brandstof", "Fuel"),
    "bonus": ("Zuinig gevlogen: +%d bonus", "Fuel saved: +%d bonus"),
    "nood": ("Brandstof op! Noodlanding.", "Out of fuel! Emergency landing."),
    "beurt_van": ("Beurt: %s", "Turn: %s"),
}


def T(k):
    if k in TXT:
        v = TXT[k]
        return v[0] if UI.TAAL == "nl" else v[1]
    return UI.T(k)


# ------------------------------------------------------------------ kaart
_DATA = None


def data():
    global _DATA
    if _DATA is None:
        with open(os.path.join(UI.HERE, "assets", "topo_nl.json"), encoding="utf-8") as f:
            _DATA = json.load(f)
        for p in _DATA["prov"]:
            p["k"] = "prov"
        for g in _DATA["gem"]:
            g["k"] = "gem"
    return _DATA


def items_voor(onderwerp):
    d = data()
    pl = d["plaats"]
    if onderwerp == "prov":
        return d["prov"]
    if onderwerp == "hoofd":
        naam = {p["n"]: p for p in pl}
        return [naam[p["h"]] for p in d["prov"]]
    if onderwerp == "groot":
        return [p for p in pl if p["i"] >= 95000]
    if onderwerp == "steden":
        return [p for p in pl if p["i"] >= 40000]
    if onderwerp == "alle":
        return list(pl)
    return d["gem"]


def is_vlak(it):
    return "r" in it


def binnen(pt, r):
    x, y = pt
    c = False
    n = len(r)
    for i in range(n):
        x1, y1 = r[i]
        x2, y2 = r[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def raak_vlak(pt, it):
    return any(binnen(pt, r) for r in it["r"])


def afstand_vlak(pt, it):
    """kortste afstand (px) van punt tot de rand van een vlak; 0 als het erin ligt"""
    if raak_vlak(pt, it):
        return 0.0
    best = 1e9
    px, py = pt
    for r in it["r"]:
        n = len(r)
        for i in range(n):
            (x1, y1), (x2, y2) = r[i], r[(i + 1) % n]
            dx, dy = x2 - x1, y2 - y1
            L = dx * dx + dy * dy
            t = 0 if L == 0 else max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / L))
            qx, qy = x1 + t * dx, y1 + t * dy
            best = min(best, math.hypot(px - qx, py - qy))
    return best


ZEE = (26, 34, 58)
LAND = (58, 50, 84)
LAND2 = (66, 57, 95)


def maak_kaart(met_gemeentes):
    d = data()
    s = pygame.Surface((UI.W, UI.H), pygame.SRCALPHA)
    for i, p in enumerate(d["prov"]):
        for r in p["r"]:
            pygame.draw.polygon(s, LAND if i % 2 else LAND2, r)
    if met_gemeentes:
        for g in d["gem"]:
            for r in g["r"]:
                pygame.draw.lines(s, (92, 82, 128), True, r, 1)
    for p in d["prov"]:
        for r in p["r"]:
            pygame.draw.lines(s, UI.ACCENT if not met_gemeentes else (150, 132, 210), True, r, 2)
    return s


# ------------------------------------------------------------------ het spel
class Topografie:
    def __init__(self, app, onderwerp, vorm, spelers):
        self.app, self.onderwerp, self.vorm, self.spelers = app, onderwerp, vorm, spelers
        self.items = items_voor(onderwerp)
        self.kaart = maak_kaart(onderwerp == "gem")
        self.knoppen = []
        self.nieuw()

    def nieuw(self):
        n = AANTAL * self.spelers
        pool = list(self.items)
        random.shuffle(pool)
        while len(pool) < n:                       # 12 provincies, 2 spelers: dan komen er een paar terug
            extra = list(self.items)
            random.shuffle(extra)
            pool += extra
        self.vragen = pool[:n]
        self.nr = 0
        self.score = [0] * self.spelers
        self.goed = [0] * self.spelers
        self.fase = "vraag"                        # vraag, antwoord, einde
        self.uitslag = None
        self.tip_gezien = False
        self.record = False
        self.heli_pos = [[470.0, 430.0] for _ in range(self.spelers)]
        self.maak_keuzes()
        self.start_vlucht()

    # ---- hulpjes
    @property
    def sp(self):
        return self.nr % self.spelers

    @property
    def doel(self):
        return self.vragen[self.nr]

    def naam_sp(self, i):
        return UI.T("jij") if self.spelers == 1 else UI.T("speler%d" % (i + 1))

    def maak_keuzes(self):
        self.keuze_fout = None
        if self.vorm != "kies":
            self.keuzes = []
            return
        doel = self.doel
        anderen = [it for it in self.items if it["n"] != doel["n"]]
        if self.onderwerp in ("alle", "gem", "steden"):
            # moeilijker: namen uit de buurt
            dx, dy = doel["m"]
            anderen.sort(key=lambda it: (it["m"][0] - dx) ** 2 + (it["m"][1] - dy) ** 2)
            anderen = anderen[:9]
        k = random.sample(anderen, 3) + [doel]
        random.shuffle(k)
        self.keuzes = k

    def punten_voor_klik(self, pt):
        doel = self.doel
        if is_vlak(doel):
            km = afstand_vlak(pt, doel) * KM_PX
            if km == 0:
                return 10, 0
            return (5 if km <= 8 else 0), km
        km = math.hypot(pt[0] - doel["m"][0], pt[1] - doel["m"][1]) * KM_PX
        if self.app.hulp and self.onderwerp != "alle":
            # met hulp staan er bolletjes: klik je het juiste bolletje, dan is het goed
            dichtst = min(self.items, key=lambda it: (it["m"][0] - pt[0]) ** 2 + (it["m"][1] - pt[1]) ** 2)
            if dichtst is doel and km <= 14:
                return 10, km
        if km <= 7:
            return 10, km
        if km <= 20:
            return 5, km
        return 0, km

    # ---- helikopter
    def start_vlucht(self):
        self.vlucht = None
        if self.vorm != "vlieg":
            return
        x, y = self.heli_pos[self.sp]
        dx, dy = self.doel["m"]
        km = math.hypot(dx - x, dy - y) * KM_PX
        tank = max(70.0, km * 1.5 + 30.0)
        self.vlucht = {"vx": 0.0, "vy": 0.0, "hoek": getattr(self, "_laatste_hoek", 0.0), "doel": None,
                       "tank": tank, "rest": tank, "t0": pygame.time.get_ticks()}
        self.heli_geluid(True)

    def heli_geluid(self, aan):
        g = self.app.geluid
        if not getattr(g, "ok", False) or not hasattr(g, "heli"):
            return
        try:
            if aan and not getattr(self, "_rotor", False):
                g.heli.play(loops=-1)
            elif not aan:
                g.heli.stop()
            self._rotor = aan
        except Exception:
            pass

    def update(self):
        v = self.vlucht
        if self.vorm != "vlieg" or self.fase != "vraag" or v is None:
            return
        k = pygame.key.get_pressed()
        ax = (k[pygame.K_RIGHT] - k[pygame.K_LEFT]) * 1.0
        ay = (k[pygame.K_DOWN] - k[pygame.K_UP]) * 1.0
        pos = self.heli_pos[self.sp]
        if ax or ay:
            v["doel"] = None
            v["vx"] += ax * 0.22
            v["vy"] += ay * 0.22
        elif v["doel"]:
            tx, ty = v["doel"]
            dx, dy = tx - pos[0], ty - pos[1]
            afst = math.hypot(dx, dy)
            if afst < 2:
                v["doel"] = None
                v["vx"] = v["vy"] = 0.0
            else:
                snel = min(3.0, afst / 12.0 + 0.4)
                v["vx"] += (dx / afst * snel - v["vx"]) * 0.15
                v["vy"] += (dy / afst * snel - v["vy"]) * 0.15
        v["vx"] *= 0.95
        v["vy"] *= 0.95
        sp = math.hypot(v["vx"], v["vy"])
        if sp > 3.2:
            v["vx"], v["vy"] = v["vx"] * 3.2 / sp, v["vy"] * 3.2 / sp
            sp = 3.2
        nx = min(880.0, max(30.0, pos[0] + v["vx"]))
        ny = min(UI.H - 30.0, max(30.0, pos[1] + v["vy"]))
        gevlogen = math.hypot(nx - pos[0], ny - pos[1]) * KM_PX
        pos[0], pos[1] = nx, ny
        if sp > 0.3:
            doelhoek = math.atan2(v["vy"], v["vx"])
            verschil = (doelhoek - v["hoek"] + math.pi) % (2 * math.pi) - math.pi
            v["hoek"] += verschil * 0.12
            self._laatste_hoek = v["hoek"]
        v["rest"] -= gevlogen + 0.01             # ook stilhangen kost een beetje
        if v["rest"] <= 0:
            v["rest"] = 0
            self.landen(nood=True)

    def landen(self, nood=False):
        if self.fase != "vraag" or self.vlucht is None:
            return
        v = self.vlucht
        pt = (self.heli_pos[self.sp][0], self.heli_pos[self.sp][1])
        p, km = self.punten_voor_klik(pt)
        bonus = int(round(5 * v["rest"] / v["tank"])) if p > 0 else 0
        self.heli_geluid(False)
        self.geef(p, km, pt, bonus=bonus, nood=nood)

    def geef(self, punten, km=None, klik=None, bonus=0, nood=False):
        if self.tip_gezien:
            punten = max(0, punten - 5) if punten else 0
        basis = punten
        punten += bonus
        self.score[self.sp] += punten
        if punten >= 5:
            self.goed[self.sp] += 1
        soort = "goed" if basis >= 10 or (self.tip_gezien and basis >= 5) else ("bijna" if basis > 0 else "mis")
        self.uitslag = {"soort": soort, "p": punten, "km": km, "klik": klik, "bonus": bonus, "nood": nood}
        self.fase = "antwoord"
        self.app.geluid.speel({"goed": "goed", "bijna": "klik", "mis": "fout"}[soort])

    def volgende(self):
        if self.fase != "antwoord":
            return
        self.nr += 1
        self.tip_gezien = False
        if self.nr >= len(self.vragen):
            self.fase = "einde"
            self.sla_record_op()
            if self.spelers == 1:
                self.app.geluid.speel("win" if self.score[0] >= self.max_punten() * 0.6 else "uit")
            else:
                self.app.geluid.speel("win")
            return
        self.fase = "vraag"
        self.uitslag = None
        self.maak_keuzes()
        self.start_vlucht()
        self.app.geluid.speel("klik")

    def max_punten(self):
        return AANTAL * (15 if self.vorm == "vlieg" else 10)

    def kies(self, it):
        if self.fase != "vraag":
            return
        if it is self.doel:
            self.geef(10)
        else:
            self.keuze_fout = it
            self.geef(0)

    def tip(self):
        if self.fase == "vraag" and not self.tip_gezien:
            self.tip_gezien = True
            self.app.geluid.speel("klik")

    def klik(self, pos):
        if self.fase == "vraag" and self.vorm == "klik" and pos[0] < 900:
            p, km = self.punten_voor_klik(pos)
            self.geef(p, km, pos)
        elif self.fase == "vraag" and self.vorm == "vlieg" and pos[0] < 900 and self.vlucht:
            self.vlucht["doel"] = (float(pos[0]), float(pos[1]))

    def toets(self, e):
        if e.key == pygame.K_ESCAPE:
            self.app.naar_menu()
        elif e.key in (pygame.K_SPACE, pygame.K_RETURN):
            if self.fase == "antwoord":
                self.volgende()
            elif self.fase == "vraag" and self.vorm == "vlieg":
                self.landen()
            elif self.fase == "einde":
                self.nieuw()
        elif self.fase == "vraag" and self.vorm == "kies" and e.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
            self.kies(self.keuzes[e.key - pygame.K_1])

    # ---- records
    def sla_record_op(self):
        if self.spelers != 1:
            return
        sleutel = "%s_%s" % (self.onderwerp, self.vorm)
        rec = laad_records()
        if self.score[0] > rec.get(sleutel, -1):
            self.record = rec.get(sleutel, -1) >= 0 or self.score[0] > 0
            rec[sleutel] = self.score[0]
            try:
                with open(os.path.join(UI.DATA, "topo_records.json"), "w", encoding="utf-8") as f:
                    json.dump(rec, f)
            except Exception:
                pass

    # ---- tekenen
    def teken_doel(self, d, it, kleur, dik=False):
        t = pygame.time.get_ticks() / 1000.0
        if is_vlak(it):
            laag = pygame.Surface((UI.W, UI.H), pygame.SRCALPHA)
            for r in it["r"]:
                pygame.draw.polygon(laag, kleur + (170,), r)
            d.blit(laag, (0, 0))
            for r in it["r"]:
                pygame.draw.lines(d, kleur, True, r, 3)
            if it["k"] == "gem" or dik:
                cx, cy = it["m"]
                straal = int(22 + 6 * math.sin(t * 4))
                pygame.draw.circle(d, kleur, (int(cx), int(cy)), straal, 4)
        else:
            cx, cy = int(it["m"][0]), int(it["m"][1])
            straal = int(16 + 5 * math.sin(t * 4))
            pygame.draw.circle(d, kleur, (cx, cy), straal, 4)
            pygame.draw.circle(d, kleur, (cx, cy), 8)
            pygame.draw.circle(d, (30, 24, 40), (cx, cy), 8, 2)

    def teken(self, d, muis):
        d.fill(UI.ACHTER)
        pygame.draw.rect(d, ZEE, (10, 10, 890, UI.H - 20), border_radius=18)
        d.blit(self.kaart, (0, 0))
        doel = self.doel if self.fase != "einde" else None
        # tip: provincie oplichten
        if doel is not None and self.tip_gezien and self.fase == "vraag":
            pr = next(p for p in data()["prov"] if p["n"] == doel.get("p"))
            laag = pygame.Surface((UI.W, UI.H), pygame.SRCALPHA)
            for r in pr["r"]:
                pygame.draw.polygon(laag, (127, 119, 221, 110), r)
            d.blit(laag, (0, 0))
        # hulp-bolletjes bij plaatsen
        if self.app.hulp and doel is not None and not is_vlak(doel) and self.onderwerp != "alle":
            for it in self.items:
                pygame.draw.circle(d, (200, 190, 235), (int(it["m"][0]), int(it["m"][1])), 5)
                pygame.draw.circle(d, (40, 32, 60), (int(it["m"][0]), int(it["m"][1])), 5, 1)
        # helikopter
        if self.vorm == "vlieg" and doel is not None:
            if self.fase == "vraag" and self.app.hulp:
                knip = (pygame.time.get_ticks() // 400) % 2 == 0
                if is_vlak(doel):
                    if knip:
                        for r in doel["r"]:
                            pygame.draw.lines(d, UI.GOUD, True, r, 3)
                elif knip:
                    pygame.draw.circle(d, UI.GOUD, (int(doel["m"][0]), int(doel["m"][1])), 9)
                    pygame.draw.circle(d, (30, 24, 40), (int(doel["m"][0]), int(doel["m"][1])), 9, 2)
            if self.fase == "vraag" and self.vlucht and self.vlucht["doel"]:
                tx, ty = int(self.vlucht["doel"][0]), int(self.vlucht["doel"][1])
                pygame.draw.circle(d, UI.ACCENT, (tx, ty), 12, 2)
                pygame.draw.circle(d, UI.ACCENT, (tx, ty), 3)
            for i in range(self.spelers):
                if i != self.sp:
                    x, y = self.heli_pos[i]
                    teken_heli(d, x, y, 0, 0, i, vliegt=False, vaag=True)
            x, y = self.heli_pos[self.sp]
            hoek = self.vlucht["hoek"] if self.vlucht else getattr(self, "_laatste_hoek", 0.0)
            teken_heli(d, x, y, hoek, pygame.time.get_ticks() / 1000.0, self.sp, vliegt=self.fase == "vraag")
        # muis-wijzer op de kaart
        if self.fase == "vraag" and self.vorm == "klik" and muis[0] < 900:
            pygame.draw.circle(d, UI.GOUD, muis, 10, 2)
            pygame.draw.line(d, UI.GOUD, (muis[0] - 16, muis[1]), (muis[0] - 6, muis[1]), 2)
            pygame.draw.line(d, UI.GOUD, (muis[0] + 6, muis[1]), (muis[0] + 16, muis[1]), 2)
            pygame.draw.line(d, UI.GOUD, (muis[0], muis[1] - 16), (muis[0], muis[1] - 6), 2)
            pygame.draw.line(d, UI.GOUD, (muis[0], muis[1] + 6), (muis[0], muis[1] + 16), 2)
        if doel is not None:
            if self.fase == "vraag" and self.vorm == "kies":
                self.teken_doel(d, doel, UI.GOUD, dik=True)
            elif self.fase == "antwoord":
                u = self.uitslag
                kl = UI.GROEN
                if self.keuze_fout is not None:
                    self.teken_doel(d, self.keuze_fout, UI.ROOD)
                    fx, fy = int(self.keuze_fout["m"][0]), int(self.keuze_fout["m"][1])
                    fl = UI.font(18).render(self.keuze_fout["n"], True, UI.TEKST)
                    fr = fl.get_rect(midright=(fx - 24, fy))
                    fr.clamp_ip(pygame.Rect(16, 16, 880, UI.H - 32))
                    pygame.draw.rect(d, (22, 19, 31), fr.inflate(12, 6), border_radius=8)
                    pygame.draw.rect(d, UI.ROOD, fr.inflate(12, 6), 2, border_radius=8)
                    d.blit(fl, fr)
                self.teken_doel(d, doel, kl, dik=True)
                if u["klik"]:
                    kx, ky = u["klik"]
                    if u["soort"] != "goed":
                        pygame.draw.line(d, UI.ROOD, (kx, ky), (int(doel["m"][0]), int(doel["m"][1])), 2)
                    kk = UI.GROEN if u["soort"] == "goed" else UI.ROOD
                    pygame.draw.line(d, kk, (kx - 9, ky - 9), (kx + 9, ky + 9), 4)
                    pygame.draw.line(d, kk, (kx - 9, ky + 9), (kx + 9, ky - 9), 4)
                # naam bij de plek
                cx, cy = int(doel["m"][0]), int(doel["m"][1])
                lab = UI.font(22).render(doel["n"], True, UI.TEKST)
                r = lab.get_rect(midbottom=(cx, cy - 28))
                r.clamp_ip(pygame.Rect(16, 16, 880, UI.H - 32))
                pygame.draw.rect(d, (22, 19, 31), r.inflate(14, 8), border_radius=8)
                pygame.draw.rect(d, kl, r.inflate(14, 8), 2, border_radius=8)
                d.blit(lab, r)
        tekst = UI.tekst
        px = 925
        tekst(d, UI.T("topo"), 32, UI.ACCENT, (px, 24))
        tekst(d, T("o_" + self.onderwerp), 18, UI.ZACHT, (px, 66), vet=False)
        self.knoppen = []
        if self.fase == "einde":
            self.teken_einde(d, muis, px)
        else:
            # spelers
            y = 100
            for i in range(self.spelers):
                aan = i == self.sp
                if aan and self.spelers > 1:
                    pygame.draw.rect(d, (50, 44, 72), (px - 10, y - 6, UI.W - px - 6, 40), border_radius=10)
                kl = (UI.STEEN_W if i == 0 else UI.GOUD)
                pygame.draw.circle(d, kl, (px + 10, y + 14), 10)
                tekst(d, "%s: %s" % (self.naam_sp(i), T("punten") % self.score[i]), 22, UI.TEKST, (px + 30, y))
                y += 44
            vn = self.nr // self.spelers + 1
            tekst(d, T("vraag") % (vn, AANTAL), 20, UI.ZACHT, (px, y + 6), vet=False)
            y += 44
            if self.fase == "vraag":
                if self.spelers > 1:
                    tekst(d, T("beurt_van") % self.naam_sp(self.sp), 22, UI.GOUD, (px, y)); y += 36
                if self.vorm == "vlieg":
                    tekst(d, T("vlieg_naar") + "...", 26, UI.TEKST, (px, y)); y += 40
                    for regel in UI.Backgammon._knip(None, self.doel["n"] + "!", 34, UI.W - px - 20):
                        tekst(d, regel, 34, UI.GOUD, (px, y)); y += 44
                    v = self.vlucht
                    tekst(d, T("brandstof"), 20, UI.ZACHT, (px, y + 2), vet=False); y += 30
                    bw = UI.W - px - 30
                    deel = v["rest"] / v["tank"]
                    kl = UI.GROEN if deel > 0.5 else (UI.GOUD if deel > 0.2 else UI.ROOD)
                    pygame.draw.rect(d, (40, 34, 58), (px, y, bw, 30), border_radius=8)
                    pygame.draw.rect(d, kl, (px, y, int(bw * deel), 30), border_radius=8)
                    pygame.draw.rect(d, UI.RAND, (px, y, bw, 30), 2, border_radius=8)
                    y += 44
                    for regel in UI.Backgammon._knip(None, T("vlieg_uitleg"), 17, UI.W - px - 20):
                        tekst(d, regel, 17, UI.ZACHT, (px, y), vet=False); y += 23
                    y += 10
                    self.knoppen.append(UI.Knop((px, y, 220, 66), T("landen"), self.landen, UI.GROEN, 28))
                    y += 80
                    if self.app.hulp and self.onderwerp != "prov":
                        if self.tip_gezien:
                            for regel in UI.Backgammon._knip(None, T("in_prov") % self.doel.get("p", ""), 20, UI.W - px - 20):
                                tekst(d, regel, 20, UI.ACCENT, (px, y)); y += 28
                        else:
                            self.knoppen.append(UI.Knop((px, y, 200, 52), T("tip_kost"), self.tip, UI.GOUD, 22))
                elif self.vorm == "klik":
                    tekst(d, T("waar") + "...", 26, UI.TEKST, (px, y)); y += 40
                    for regel in UI.Backgammon._knip(None, self.doel["n"] + "?", 34, UI.W - px - 20):
                        tekst(d, regel, 34, UI.GOUD, (px, y)); y += 44
                    tekst(d, T("klik_uitleg"), 20, UI.ZACHT, (px, y + 4), vet=False); y += 40
                    if self.app.hulp and self.onderwerp != "prov":
                        if self.tip_gezien:
                            for regel in UI.Backgammon._knip(None, T("in_prov") % self.doel.get("p", ""), 20, UI.W - px - 20):
                                tekst(d, regel, 20, UI.ACCENT, (px, y)); y += 28
                        else:
                            self.knoppen.append(UI.Knop((px, y, 200, 52), T("tip_kost"), self.tip, UI.GOUD, 22))
                else:
                    tekst(d, T("welke"), 28, UI.TEKST, (px, y)); y += 40
                    tekst(d, T("welke_sub"), 17, UI.ZACHT, (px, y), vet=False); y += 34
                    for i, it in enumerate(self.keuzes):
                        naam = it["n"]
                        grootte = 22 if len(naam) < 20 else (18 if len(naam) < 27 else 15)
                        self.knoppen.append(UI.Knop((px, y, UI.W - px - 20, 62), "%d. %s" % (i + 1, naam),
                                                    (lambda it=it: self.kies(it)), UI.VAK, grootte))
                        y += 72
            elif self.fase == "antwoord":
                u = self.uitslag
                kop = {"goed": T("goed") % u["p"], "bijna": T("bijna") % u["p"], "mis": T("mis")}[u["soort"]]
                tekst(d, kop, 36, UI.GROEN if u["soort"] == "goed" else (UI.GOUD if u["soort"] == "bijna" else UI.ROOD), (px, y)); y += 52
                if u.get("nood"):
                    tekst(d, T("nood"), 20, UI.ROOD, (px, y)); y += 32
                if u.get("bonus"):
                    tekst(d, T("bonus") % u["bonus"], 20, UI.GROEN, (px, y)); y += 32
                if u["km"] is not None and u["km"] >= 1 and u["soort"] != "goed":
                    tekst(d, T("ernaast") % round(u["km"]), 22, UI.TEKST, (px, y)); y += 36
                for regel in UI.Backgammon._knip(None, T("het_is") % self.doel["n"], 22, UI.W - px - 20):
                    tekst(d, regel, 22, UI.TEKST, (px, y)); y += 30
                if self.doel.get("p") and self.onderwerp != "prov":
                    tekst(d, "(%s)" % self.doel["p"], 20, UI.ZACHT, (px, y), vet=False); y += 30
                self.knoppen.append(UI.Knop((px, max(y + 16, 470), 220, 66), T("volgende"), self.volgende, UI.GROEN, 28))
                tekst(d, T("of_spatie"), 17, UI.ZACHT, (px, max(y + 16, 470) + 74), vet=False)
        self.knoppen.append(UI.Knop((px, UI.H - 70, 150, 54), UI.T("menu"), self.app.naar_menu, UI.VAK, 22))
        if self.onderwerp not in ("prov",):
            self.knoppen.append(UI.Knop((px + 160, UI.H - 70, UI.W - px - 180, 54),
                                        "%s: %s" % (UI.T("hulp"), UI.T("aan") if self.app.hulp else UI.T("uitm")),
                                        self.app.wissel_hulp, UI.GOUD if self.app.hulp else UI.VAK, 18))
        for k in self.knoppen:
            k.teken(d, muis)


    def teken_einde(self, d, muis, px):
        tekst = UI.tekst
        y = 110
        tekst(d, T("klaar"), 40, UI.GOUD, (px, y)); y += 60
        maxp = self.max_punten()
        for i in range(self.spelers):
            tekst(d, "%s: %d / %d" % (self.naam_sp(i), self.score[i], maxp), 26, UI.TEKST, (px, y)); y += 40
        y += 10
        if self.spelers > 1:
            if self.score[0] == self.score[1]:
                kop = T("gelijkspel")
            else:
                kop = T("wint") % self.naam_sp(0 if self.score[0] > self.score[1] else 1)
            tekst(d, kop, 30, UI.ACCENT, (px, y)); y += 50
        else:
            s = self.score[0]
            sterren = 3 if s >= maxp * 0.8 else (2 if s >= maxp * 0.5 else 1)
            for k in range(3):
                teken_ster(d, px + 30 + k * 64, y + 30, 26, UI.GOUD if k < sterren else (70, 62, 96))
            y += 74
            for regel in UI.Backgammon._knip(None, T("lof%d" % sterren), 21, UI.W - px - 20):
                tekst(d, regel, 21, UI.TEKST, (px, y), vet=False); y += 30
            if self.record:
                tekst(d, T("nieuw_rec"), 24, UI.GROEN, (px, y + 6)); y += 40
        self.knoppen.append(UI.Knop((px, max(y + 20, 520), 300, 66), UI.T("nog"), self.nieuw, UI.GROEN, 26))


def teken_heli(d, x, y, hoek, t, speler, vliegt=True, vaag=False):
    """Getekende helikopter van bovenaf: romp, staart, schaatsen en draaiende wieken."""
    s = pygame.Surface((110, 110), pygame.SRCALPHA)
    c = 55
    romp = (236, 232, 222) if speler == 0 else (224, 184, 90)
    donker = (60, 50, 86)
    # wiekenschijf en schaduw eerst (anders wissen ze de romp uit)
    if vliegt:
        pygame.draw.circle(s, (220, 220, 240, 45), (c, c), 46)
    pygame.draw.ellipse(s, (0, 0, 0, 70), (c - 20, c - 9 + 10, 46, 22))
    # schaatsen
    pygame.draw.line(s, donker, (c - 16, c - 12), (c + 16, c - 12), 3)
    pygame.draw.line(s, donker, (c - 16, c + 12), (c + 16, c + 12), 3)
    # staart
    pygame.draw.polygon(s, romp, [(c - 10, c - 4), (c - 44, c - 2), (c - 44, c + 2), (c - 10, c + 4)])
    pygame.draw.polygon(s, donker, [(c - 10, c - 4), (c - 44, c - 2), (c - 44, c + 2), (c - 10, c + 4)], 2)
    # staartrotor
    hs = math.sin(t * 40) * 9 if vliegt else 9
    pygame.draw.line(s, donker, (c - 44, c - hs), (c - 44, c + hs), 3)
    # romp + raam
    pygame.draw.ellipse(s, romp, (c - 18, c - 13, 40, 26))
    pygame.draw.ellipse(s, donker, (c - 18, c - 13, 40, 26), 2)
    pygame.draw.ellipse(s, (127, 180, 230), (c + 4, c - 9, 16, 18))
    pygame.draw.ellipse(s, donker, (c + 4, c - 9, 16, 18), 2)
    # wieken
    a = t * 18 if vliegt else 0.6
    for k in range(2):
        aa = a + k * math.pi / 2
        dx, dy = math.cos(aa) * 46, math.sin(aa) * 46
        pygame.draw.line(s, (40, 34, 56), (c - dx, c - dy), (c + dx, c + dy), 4)
    pygame.draw.circle(s, donker, (c, c), 5)
    if vaag:
        s.set_alpha(110)
    r = pygame.transform.rotozoom(s, -math.degrees(hoek), 1.3)
    d.blit(r, r.get_rect(center=(int(x), int(y))))


def teken_ster(d, cx, cy, r, kl):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    pygame.draw.polygon(d, kl, pts)


def laad_records():
    try:
        with open(os.path.join(UI.DATA, "topo_records.json"), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


# ------------------------------------------------------------------ keuzescherm
class Keuze:
    def __init__(self, app):
        self.app = app
        self.onderwerp = getattr(app, "topo_onderwerp", "hoofd")
        self.vorm = getattr(app, "topo_vorm", "kies")
        self.spelers = getattr(app, "topo_spelers", 1)
        self.knoppen = []

    def zet(self, naam, waarde):
        setattr(self, naam, waarde)
        setattr(self.app, "topo_" + naam, waarde)
        self.app.geluid.speel("klik")

    def teken(self, d, muis):
        tekst = UI.tekst
        d.fill(UI.ACHTER)
        tekst(d, UI.T("topo"), 46, UI.ACCENT, (UI.W // 2, 50), mid=True)
        self.knoppen = []
        tekst(d, T("t_wat"), 26, UI.TEKST, (80, 100))
        for i, o in enumerate(ONDERWERPEN):
            x = 80 + (i % 3) * 380
            y = 140 + (i // 3) * 82
            aan = self.onderwerp == o
            self.knoppen.append(UI.Knop((x, y, 360, 70), T("o_" + o), (lambda o=o: self.zet("onderwerp", o)),
                                        UI.GOUD if aan else UI.VAK, 24))
        tekst(d, T("t_hoe"), 26, UI.TEKST, (80, 320))
        for i, v in enumerate(("kies", "klik", "vlieg")):
            aan = self.vorm == v
            self.knoppen.append(UI.Knop((80 + i * 380, 360, 360, 70), T("h_" + v), (lambda v=v: self.zet("vorm", v)),
                                        UI.GOUD if aan else UI.VAK, 24))
        tekst(d, T("t_wie"), 26, UI.TEKST, (80, 460))
        for i, (w, n) in enumerate((("w_een", 1), ("w_twee", 2))):
            aan = self.spelers == n
            self.knoppen.append(UI.Knop((80 + i * 380, 500, 360, 70), T(w), (lambda n=n: self.zet("spelers", n)),
                                        UI.GOUD if aan else UI.VAK, 24))
        self.knoppen.append(UI.Knop((80 + 760, 500, 360, 70), "%s: %s" % (UI.T("hulp"), UI.T("aan") if self.app.hulp else UI.T("uitm")),
                                    self.app.wissel_hulp, UI.GOUD if self.app.hulp else UI.VAK, 22))
        rec = laad_records().get("%s_%s" % (self.onderwerp, self.vorm))
        if rec is not None:
            tekst(d, T("beste") % (rec, AANTAL * (15 if self.vorm == "vlieg" else 10)), 22, UI.GOUD, (UI.W // 2, 615), mid=True)
        self.knoppen.append(UI.Knop((UI.W // 2 - 160, 650, 320, 90), T("start"),
                                    lambda: self.app.start_topo(self.onderwerp, self.vorm, self.spelers), UI.GROEN, 36))
        self.knoppen.append(UI.Knop((40, UI.H - 90, 200, 60), UI.T("terug"), self.app.naar_menu, UI.VAK, 24))
        for k in self.knoppen:
            k.teken(d, muis)
