# -*- coding: utf-8 -*-
"""DraveSpellenkast - Zeeslag (tegen de computer, of online tegen elkaar).
10 x 10 vakjes, 5 schepen (5-4-3-3-2) die elkaar niet raken. Om de beurt schieten.
Grote vakjes, klik om te schieten. Tip-knop en hulp (water rond een gezonken schip wordt vanzelf gemarkeerd).
Copyright (C) 2026 Dravenlock (Roger & Claudio). GNU GPL v3.0."""
import math
import random
import time

import pygame

UI = None          # wordt door main.py gezet

N = 10
SCHEPEN = [5, 4, 3, 3, 2]
LETTERS = "ABCDEFGHIJ"
GROOT = 56                                  # vakje op het grote bord (schieten / plaatsen)
KLEIN = 36                                  # vakje op je eigen kleine bord tijdens het spel
GX, GY = 450, 130                           # groot bord linksboven
KX, KY = 40, 210                            # klein bord linksboven
ZEE = (30, 62, 110)
ZEE2 = (36, 72, 126)
LIJN = (70, 110, 170)
ROMP = (150, 156, 170)
ROMP_D = (96, 100, 116)
VUUR = (255, 140, 40)

TX = {
    "zee": ("Zeeslag", "Battleship"),
    "plaats": ("Zet je schepen neer", "Place your ships"),
    "plaats_uitleg": ("Klik op het bord om het schip neer te leggen. R of rechts klikken = draaien.",
                      "Click on the board to place the ship. R or right click = rotate."),
    "willekeurig": ("Willekeurig", "Random"), "draai": ("Draaien (R)", "Rotate (R)"), "opnieuw": ("Opnieuw", "Reset"),
    "start": ("Start!", "Start!"),
    "jouw_vloot": ("Jouw vloot", "Your fleet"), "zijn_zee": ("Zee van %s", "%s's sea"),
    "schiet": ("Jouw beurt: klik waar je schiet", "Your turn: click where to shoot"),
    "comp_schiet": ("De computer mikt...", "The computer is aiming..."),
    "mis": ("Plons! Mis.", "Splash! Miss."), "raak": ("Raak!", "Hit!"),
    "gezonken": ("Raak en gezonken! (%d)", "Hit and sunk! (%d)"),
    "jouw_gezonken": ("Oei, de computer liet je schip van %d zinken.", "Oops, the computer sank your ship of %d."),
    "al": ("Daar heb je al geschoten.", "You already shot there."),
    "tip_zee": ("Tip: schiet naast je treffer, daar ligt de rest van het schip.", "Tip: shoot next to your hit, the rest of the ship is there."),
    "tip_kans": ("Tip: hier is de kans op een schip het grootst.", "Tip: a ship is most likely here."),
    "over": ("Nog te zinken: %s", "Left to sink: %s"),
    "toetsen_zee": ("Klik = schieten  ·  T = tip  ·  R = draaien (plaatsen)  ·  Esc = menu",
                    "Click = shoot  ·  T = tip  ·  R = rotate (placing)  ·  Esc = menu"),
    "plaats_niet": ("Daar past hij niet (schepen mogen elkaar niet raken).", "It doesn't fit there (ships may not touch)."),
}


def T(k):
    if k in TX:
        v = TX[k]
        return v[0] if UI.TAAL == "nl" else v[1]
    return UI.T(k)


# ------------------------------------------------------------------ regels
def vakken(x, y, lengte, liggend):
    return [(x + i, y) if liggend else (x, y + i) for i in range(lengte)]


def past(vloot, cellen):
    """Binnen het bord, en niet op of naast een ander schip."""
    bezet = set()
    for sch in vloot:
        for (cx, cy) in sch:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    bezet.add((cx + dx, cy + dy))
    return all(0 <= x < N and 0 <= y < N and (x, y) not in bezet for x, y in cellen)


def willekeurige_vloot():
    while True:
        vloot = []
        for lengte in SCHEPEN:
            for _ in range(300):
                liggend = random.random() < 0.5
                x = random.randint(0, N - (lengte if liggend else 1))
                y = random.randint(0, N - (1 if liggend else lengte))
                c = vakken(x, y, lengte, liggend)
                if past(vloot, c):
                    vloot.append(c)
                    break
            else:
                break
        if len(vloot) == len(SCHEPEN):
            return vloot


def rondom(schip):
    uit = set()
    for (x, y) in schip:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if 0 <= x + dx < N and 0 <= y + dy < N:
                    uit.add((x + dx, y + dy))
    return uit - set(schip)


class Schoten:
    """Wat ik weet van de zee van de ander: 0 = onbekend, 1 = mis, 2 = raak, 3 = gezonken, 4 = water (zeker leeg)."""

    def __init__(self):
        self.g = [[0] * N for _ in range(N)]
        self.over = list(SCHEPEN)               # lengtes die nog niet gezonken zijn

    def zink(self, schip):
        for (x, y) in schip:
            self.g[x][y] = 3
        for (x, y) in rondom(schip):
            if self.g[x][y] == 0:
                self.g[x][y] = 4
        if len(schip) in self.over:
            self.over.remove(len(schip))


def kansenkaart(sch):
    """Hoe vaak past een nog-niet-gezonken schip over elk vakje (treffers tellen extra)."""
    kaart = [[0] * N for _ in range(N)]
    raak = [(x, y) for x in range(N) for y in range(N) if sch.g[x][y] == 2]
    for lengte in sch.over:
        for liggend in (True, False):
            for x in range(N - (lengte - 1 if liggend else 0)):
                for y in range(N - (0 if liggend else lengte - 1)):
                    c = vakken(x, y, lengte, liggend)
                    if any(sch.g[a][b] in (1, 3, 4) for a, b in c):
                        continue
                    extra = sum(1 for p in c if sch.g[p[0]][p[1]] == 2)
                    if raak and extra == 0:
                        gewicht = 1
                    else:
                        gewicht = 1 + extra * 30
                    for a, b in c:
                        if sch.g[a][b] == 0:
                            kaart[a][b] += gewicht
    return kaart


def jaag(sch):
    """Na een treffer: probeer de buren (op een lijn als er al twee raak zijn)."""
    raak = [(x, y) for x in range(N) for y in range(N) if sch.g[x][y] == 2]
    if not raak:
        return None
    opties = []
    for (x, y) in raak:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            a, b = x + dx, y + dy
            if 0 <= a < N and 0 <= b < N and sch.g[a][b] == 0:
                lijn = (a - dx * 2, b - dy * 2) in raak or (x - dx, y - dy) in raak
                opties.append((2 if lijn else 1, (a, b)))
    if not opties:
        return None
    opties.sort(reverse=True)
    beste = [p for s, p in opties if s == opties[0][0]]
    return random.choice(beste)


def kies_schot(sch, niveau):
    vrij = [(x, y) for x in range(N) for y in range(N) if sch.g[x][y] == 0]
    if niveau == 1:
        if random.random() < 0.5:
            j = jaag(sch)
            if j:
                return j
        return random.choice(vrij)
    if niveau == 2:
        j = jaag(sch)
        if j:
            return j
        dam = [p for p in vrij if (p[0] + p[1]) % 2 == 0]      # schaakbord: slimmer zoeken
        return random.choice(dam or vrij)
    kaart = kansenkaart(sch)
    beste = max(kaart[x][y] for (x, y) in vrij)
    return random.choice([(x, y) for (x, y) in vrij if kaart[x][y] == beste])


# ------------------------------------------------------------------ geluid (zelf gemaakt)
_GEL = {}


def geluiden():
    if _GEL or not getattr(UI, "np", None):
        return _GEL
    try:
        np, toon, mix, naar = UI.np, UI.toon, UI.mix, UI.naar_geluid
        n = int(UI.SR * 0.6)
        ruis = np.random.RandomState(4).uniform(-1, 1, n)
        t = np.arange(n) / UI.SR
        plons = np.convolve(ruis, np.ones(30) / 30, mode="same") * np.exp(-t * 7) * 0.9
        _GEL["plons"] = naar(mix(plons, toon(240, 0.25, 0.15, decay=12)))
        n = int(UI.SR * 0.9)
        ruis = np.random.RandomState(9).uniform(-1, 1, n)
        t = np.arange(n) / UI.SR
        knal = np.convolve(ruis, np.ones(12) / 12, mode="same") * np.exp(-t * 4.5)
        _GEL["boem"] = naar(mix(knal * 1.1, toon(70, 0.8, 0.5, decay=4), toon(110, 0.4, 0.3, decay=6)))
        _GEL["schot"] = naar(mix(toon(0, 0.12, 0.3, "ruis", 30), toon(160, 0.12, 0.3, decay=25)))
    except Exception:
        pass
    return _GEL


def speel(app, naam):
    g = geluiden().get(naam)
    if g is not None and app.geluid.ok:
        try:
            g.play()
            return
        except Exception:
            pass
    app.geluid.speel({"plons": "zet", "boem": "sla", "schot": "klik"}.get(naam, "klik"))


# ------------------------------------------------------------------ het spel
class Zeeslag:
    def __init__(self, app, niveau):
        self.app = app
        self.niveau = niveau
        self.knoppen = []
        self.score = [0, 0]
        self.begint = 0
        self.mij = 0
        self.nieuw_potje()

    def naam(self, sp):
        return UI.T("jij") if sp == 0 else UI.T("computer")

    def nieuw_potje(self):
        self.fase = "plaatsen"
        self.vloot = []                              # mijn schepen (lijsten van vakjes)
        self.liggend = True
        self.zijn_vloot = willekeurige_vloot()
        self.mijn_schoten = Schoten()                # wat ik weet van zijn zee
        self.zijn_schoten = Schoten()                # wat hij weet van mijn zee
        self.beurt = self.begint
        self.begint = 1 - self.begint
        self.klaar = False
        self.uitslag = ""
        self.melding = ""
        self.tip = None
        self.anim = []                               # [x, y, soort, start, groot] spetters en vlammen
        self.wacht_tot = 0

    # ---------- plaatsen
    def volgend_schip(self):
        return SCHEPEN[len(self.vloot)] if len(self.vloot) < len(SCHEPEN) else None

    def plaats(self, x, y):
        lengte = self.volgend_schip()
        if lengte is None:
            return
        c = vakken(x, y, lengte, self.liggend)
        if past(self.vloot, c):
            self.vloot.append(c)
            self.app.geluid.speel("zet")
            self.melding = ""
        else:
            self.melding = T("plaats_niet")
            self.app.geluid.speel("fout")

    def willekeurig(self):
        self.vloot = willekeurige_vloot()
        self.app.geluid.speel("klik")

    def begin(self):
        if len(self.vloot) == len(SCHEPEN):
            self.fase = "spel"
            self.melding = ""
            self.app.geluid.speel("goed")

    # ---------- schieten
    def schot_op(self, schoten, vloot, x, y):
        """Geeft 'mis', 'raak' of ('gezonken', schip)."""
        for sch in vloot:
            if (x, y) in sch:
                schoten.g[x][y] = 2
                if all(schoten.g[a][b] in (2, 3) for a, b in sch):
                    schoten.zink(sch)
                    return ("gezonken", sch)
                return "raak"
        schoten.g[x][y] = 1
        return "mis"

    def schiet(self, x, y):
        if self.fase != "spel" or self.beurt != self.mij or self.klaar or time.time() < self.wacht_tot:
            return
        if self.mijn_schoten.g[x][y] != 0:
            self.melding = T("al")
            return
        self.tip = None
        uit = self.schot_op(self.mijn_schoten, self.zijn_vloot, x, y)
        self.na_schot(uit, x, y, ik=True)

    def na_schot(self, uit, x, y, ik):
        nu = time.time()
        gx, gy = (GX + x * GROOT + GROOT // 2, GY + y * GROOT + GROOT // 2) if ik else (KX + x * KLEIN + KLEIN // 2, KY + y * KLEIN + KLEIN // 2)
        speel(self.app, "schot")
        if uit == "mis":
            self.anim.append([gx, gy, "plons", nu, ik])
            speel(self.app, "plons")
            self.melding = T("mis") if ik else ""
        else:
            self.anim.append([gx, gy, "boem", nu, ik])
            speel(self.app, "boem")
            if isinstance(uit, tuple):
                self.melding = (T("gezonken") % len(uit[1])) if ik else (T("jouw_gezonken") % len(uit[1]))
            else:
                self.melding = T("raak") if ik else ""
        schoten = self.mijn_schoten if ik else self.zijn_schoten
        if not schoten.over:
            self.klaar = True
            sp = self.mij if ik else 1 - self.mij
            self.score[sp] += 1
            self.uitslag = UI.T("wint") % self.naam(sp)
            self.app.geluid.speel("win" if ik else "verlies")
            return
        self.beurt = 1 - self.beurt
        self.wacht_tot = nu + 0.9                    # even kijken wat er gebeurde

    def update(self):
        nu = time.time()
        self.anim = [a for a in self.anim if nu - a[3] < 1.6]
        if self.fase != "spel" or self.klaar or self.beurt == self.mij or nu < self.wacht_tot:
            return
        x, y = kies_schot(self.zijn_schoten, self.niveau)
        uit = self.schot_op(self.zijn_schoten, self.vloot, x, y)
        self.na_schot(uit, x, y, ik=False)

    def geef_tip(self):
        if self.fase != "spel" or self.beurt != self.mij or self.klaar:
            return
        j = jaag(self.mijn_schoten)
        if j:
            self.tip, self.melding = j, T("tip_zee")
        else:
            kaart = kansenkaart(self.mijn_schoten)
            vrij = [(x, y) for x in range(N) for y in range(N) if self.mijn_schoten.g[x][y] == 0]
            if vrij:
                self.tip = max(vrij, key=lambda p: kaart[p[0]][p[1]])
                self.melding = T("tip_kans")
        self.app.geluid.speel("goed")

    # ---------- invoer
    def vak_op(self, pos, ox, oy, maat):
        x, y = (pos[0] - ox) // maat, (pos[1] - oy) // maat
        if 0 <= x < N and 0 <= y < N:
            return int(x), int(y)
        return None

    def klik(self, pos):
        v = self.vak_op(pos, GX, GY, GROOT)
        if v is None:
            return
        if self.fase == "plaatsen":
            self.plaats(*v)
        else:
            self.schiet(*v)

    def klik_rechts(self, pos):
        if self.fase == "plaatsen":
            self.liggend = not self.liggend

    def toets(self, e):
        if e.key == pygame.K_ESCAPE:
            self.app.naar_menu()
        elif e.key == pygame.K_r and self.fase == "plaatsen":
            self.liggend = not self.liggend
        elif e.key == pygame.K_t:
            self.geef_tip()
        elif self.klaar and e.key in (pygame.K_SPACE, pygame.K_RETURN):
            self.nieuw_potje()
        elif self.fase == "plaatsen" and e.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.begin()

    # ---------- tekenen
    def teken_zee(self, d, ox, oy, maat, labels=True):
        golf = time.time() * 1.5
        for x in range(N):
            for y in range(N):
                kl = ZEE if (x + y) % 2 == 0 else ZEE2
                r = pygame.Rect(ox + x * maat, oy + y * maat, maat, maat)
                pygame.draw.rect(d, kl, r)
                if maat >= 40:                       # golfjes
                    gy = r.y + maat * 0.62 + math.sin(golf + x * 0.8 + y) * 2
                    pygame.draw.arc(d, LIJN, (r.x + 8, gy - 4, maat * 0.35, 8), 0, math.pi, 2)
                    pygame.draw.arc(d, LIJN, (r.x + maat * 0.45, gy - 4, maat * 0.35, 8), 0, math.pi, 2)
        for i in range(N + 1):
            pygame.draw.line(d, LIJN, (ox + i * maat, oy), (ox + i * maat, oy + N * maat), 1)
            pygame.draw.line(d, LIJN, (ox, oy + i * maat), (ox + N * maat, oy + i * maat), 1)
        pygame.draw.rect(d, UI.RAND, (ox - 3, oy - 3, N * maat + 6, N * maat + 6), 3, border_radius=6)
        if labels:
            px = 20 if maat >= 40 else 15
            for i in range(N):
                UI.tekst(d, LETTERS[i], px, UI.ZACHT, (ox + i * maat + maat // 2, oy - px), mid=True)
                UI.tekst(d, str(i + 1), px, UI.ZACHT, (ox - px, oy + i * maat + maat // 2), mid=True)

    def teken_schip(self, d, schip, ox, oy, maat, kleur=ROMP, alfa=255):
        xs = [c[0] for c in schip]
        ys = [c[1] for c in schip]
        liggend = len(set(ys)) == 1
        r = pygame.Rect(ox + min(xs) * maat + 4, oy + min(ys) * maat + 4,
                        (max(xs) - min(xs) + 1) * maat - 8, (max(ys) - min(ys) + 1) * maat - 8)
        s = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        w, h = r.w, r.h
        if liggend:
            punt = [(0, h * 0.5), (h * 0.45, 0), (w - 6, 0), (w, h * 0.25), (w, h * 0.75), (w - 6, h), (h * 0.45, h)]
        else:
            punt = [(w * 0.5, 0), (w, w * 0.45), (w, h - 6), (w * 0.75, h), (w * 0.25, h), (0, h - 6), (0, w * 0.45)]
        pygame.draw.polygon(s, kleur + (alfa,), punt)
        pygame.draw.polygon(s, ROMP_D + (alfa,), punt, 3)
        k = maat * 0.32                               # kajuitjes en een schoorsteen
        for i in range(len(schip)):
            if i in (1, len(schip) - 2) or len(schip) <= 2:
                cx = (i + 0.5) * maat - 4 if liggend else w / 2
                cy = h / 2 if liggend else (i + 0.5) * maat - 4
                pygame.draw.rect(s, ROMP_D + (alfa,), (cx - k / 2, cy - k / 2, k, k), border_radius=3)
        cx = (len(schip) * 0.5) * maat - 4 if liggend else w / 2
        cy = h / 2 if liggend else (len(schip) * 0.5) * maat - 4
        pygame.draw.circle(s, (60, 64, 78, alfa), (int(cx), int(cy)), max(4, int(maat * 0.16)))
        d.blit(s, r.topleft)

    def teken_markering(self, d, x, y, ox, oy, maat, soort):
        cx, cy = ox + x * maat + maat // 2, oy + y * maat + maat // 2
        if soort == 1:                                # mis: wit plonsje
            pygame.draw.circle(d, (220, 232, 250), (cx, cy), max(4, maat // 7))
            pygame.draw.circle(d, (160, 190, 230), (cx, cy), max(7, maat // 4), 2)
        elif soort in (2, 3):                         # raak: vlammetje
            f = 0.8 + 0.2 * math.sin(time.time() * 9 + x * 3 + y)
            pygame.draw.circle(d, (200, 50, 40), (cx, cy), int(maat * 0.36))
            pygame.draw.circle(d, VUUR, (cx, cy - 2), int(maat * 0.24 * f))
            pygame.draw.circle(d, (255, 230, 120), (cx, cy - 3), int(maat * 0.11 * f))
        elif soort == 4:                              # zeker water (hulp)
            pygame.draw.circle(d, (90, 120, 170), (cx, cy), max(3, maat // 10))

    def teken_anim(self, d):
        nu = time.time()
        for x, y, soort, t0, groot in self.anim:
            t = nu - t0
            if soort == "plons":
                for i in range(3):
                    r = int((10 + t * 60 - i * 12) * (1 if groot else 0.6))
                    if r > 0:
                        pygame.draw.circle(d, (210, 230, 255), (x, y), r, 2)
            else:
                for i in range(10):
                    hoek = i * 0.63
                    r = (t * 90) * (1 if groot else 0.6)
                    px, py = x + math.cos(hoek) * r, y + math.sin(hoek) * r - t * 30
                    pygame.draw.circle(d, VUUR if i % 2 else (255, 220, 90), (int(px), int(py)), max(1, int(7 - t * 4)))

    def teken(self, d, muis):
        d.fill(UI.ACHTER)
        UI.tekst(d, T("zee"), 40, UI.ACCENT, (40, 14))
        self.knoppen = []
        sx = GX + N * GROOT + 30                      # zijbalk
        if self.fase == "plaatsen":
            UI.tekst(d, T("plaats"), 30, UI.TEKST, (GX, 70))
            self.teken_zee(d, GX, GY, GROOT)
            for sch in self.vloot:
                self.teken_schip(d, sch, GX, GY, GROOT)
            lengte = self.volgend_schip()
            v = self.vak_op(muis, GX, GY, GROOT)
            if lengte and v:
                c = vakken(v[0], v[1], lengte, self.liggend)
                ok = past(self.vloot, c)
                binnen = [p for p in c if 0 <= p[0] < N and 0 <= p[1] < N]
                if ok:
                    self.teken_schip(d, c, GX, GY, GROOT, alfa=150)
                else:
                    for (a, b) in binnen:
                        pygame.draw.rect(d, UI.ROOD, (GX + a * GROOT + 3, GY + b * GROOT + 3, GROOT - 6, GROOT - 6), 3)
            # links: welke schepen nog
            y = 140
            UI.tekst(d, T("jouw_vloot"), 26, UI.TEKST, (40, y))
            y += 50
            for i, l in enumerate(SCHEPEN):
                kl = ROMP if i >= len(self.vloot) else (80, 84, 98)
                self.teken_schip(d, [(j, 0) for j in range(l)], 40, y, 44, kleur=kl)
                if i == len(self.vloot):
                    pygame.draw.polygon(d, UI.GOUD, [(20, y + 12), (34, y + 22), (20, y + 32)])
                y += 58
            for i, regel in enumerate(UI.Backgammon._knip(None, T("plaats_uitleg"), 20, 360)):
                UI.tekst(d, regel, 20, UI.ZACHT, (40, y + 20 + i * 28), vet=False)
            if self.melding:
                for i, regel in enumerate(UI.Backgammon._knip(None, self.melding, 20, 360)):
                    UI.tekst(d, regel, 20, UI.GOUD, (40, y + 110 + i * 28))
            self.knoppen.append(UI.Knop((sx, 140, 230, 66), T("draai"), lambda: setattr(self, "liggend", not self.liggend), UI.VAK, 22))
            self.knoppen.append(UI.Knop((sx, 220, 230, 66), T("willekeurig"), self.willekeurig, UI.VAK, 22))
            self.knoppen.append(UI.Knop((sx, 300, 230, 66), T("opnieuw"), lambda: setattr(self, "vloot", []), UI.VAK, 22))
            self.knoppen.append(UI.Knop((sx, 400, 230, 80), T("start"), self.begin, UI.GROEN, 30, aan=len(self.vloot) == len(SCHEPEN)))
        else:
            # groot: zijn zee
            UI.tekst(d, T("zijn_zee") % self.naam(1 - self.mij), 26, UI.TEKST, (GX, 70))
            self.teken_zee(d, GX, GY, GROOT)
            gezonken = [sch for sch in self.zijn_vloot if all(self.mijn_schoten.g[a][b] == 3 for a, b in sch)]
            for sch in gezonken:
                self.teken_schip(d, sch, GX, GY, GROOT, kleur=(110, 70, 70))
            if self.klaar:                            # na afloop: laat zien waar ze lagen
                for sch in self.zijn_vloot:
                    if sch not in gezonken:
                        self.teken_schip(d, sch, GX, GY, GROOT, alfa=120)
            for x in range(N):
                for y in range(N):
                    s = self.mijn_schoten.g[x][y]
                    if s and (s != 4 or self.app.hulp):
                        self.teken_markering(d, x, y, GX, GY, GROOT, s)
            v = self.vak_op(muis, GX, GY, GROOT)
            if v and self.beurt == self.mij and not self.klaar and self.mijn_schoten.g[v[0]][v[1]] == 0:
                cx, cy = GX + v[0] * GROOT + GROOT // 2, GY + v[1] * GROOT + GROOT // 2
                pygame.draw.circle(d, UI.GOUD, (cx, cy), GROOT // 2 - 6, 3)
                pygame.draw.line(d, UI.GOUD, (cx - 20, cy), (cx + 20, cy), 2)
                pygame.draw.line(d, UI.GOUD, (cx, cy - 20), (cx, cy + 20), 2)
            if self.tip:
                tx, ty = GX + self.tip[0] * GROOT, GY + self.tip[1] * GROOT
                kl = UI.GOUD if int(time.time() * 3) % 2 else (255, 255, 255)
                pygame.draw.rect(d, kl, (tx + 2, ty + 2, GROOT - 4, GROOT - 4), 4, border_radius=6)
            # klein: mijn vloot
            UI.tekst(d, T("jouw_vloot"), 24, UI.TEKST, (KX, KY - 70))
            self.teken_zee(d, KX, KY, KLEIN)
            for sch in self.vloot:
                zonk = all(self.zijn_schoten.g[a][b] == 3 for a, b in sch)
                self.teken_schip(d, sch, KX, KY, KLEIN, kleur=(110, 70, 70) if zonk else ROMP)
            for x in range(N):
                for y in range(N):
                    s = self.zijn_schoten.g[x][y]
                    if s in (1, 2, 3):
                        self.teken_markering(d, x, y, KX, KY, KLEIN, s)
            self.teken_anim(d)
            # wat moet er nog
            y = KY + N * KLEIN + 24
            over = ", ".join(str(l) for l in self.mijn_schoten.over) or "-"
            UI.tekst(d, T("over") % over, 20, UI.ZACHT, (KX, y), vet=False)
            # zijbalk
            for sp in (0, 1):
                yy = 140 + sp * 60
                UI.tekst(d, self.naam(sp), 24, UI.TEKST, (sx, yy))
                UI.tekst(d, str(self.score[sp]), 24, UI.GOUD, (UI.W - 30, yy), rechts=True)
                if not self.klaar and self.beurt == sp:
                    pygame.draw.rect(d, UI.ACCENT, (sx - 8, yy - 6, UI.W - sx - 14, 44), 3, border_radius=10)
            y = 280
            if self.klaar:
                regels = [self.uitslag]
            elif self.beurt == self.mij:
                regels = [T("schiet")]
            else:
                regels = [self.wacht_tekst()]
            if self.melding:
                regels.append(self.melding)
            for regel in regels:
                for stuk in UI.Backgammon._knip(None, regel, 22, UI.W - sx - 20):
                    UI.tekst(d, stuk, 22, UI.GOUD if regel in (self.melding, self.uitslag) else UI.TEKST, (sx, y))
                    y += 30
                y += 8
            if self.klaar:
                self.knoppen.append(UI.Knop((sx, 520, 230, 70), UI.T("nog"), self.nieuw_potje, UI.GROEN, 24))
            else:
                self.knoppen.append(UI.Knop((sx, 520, 230, 66), UI.T("tip"), self.geef_tip, UI.GOUD, 26,
                                            aan=self.beurt == self.mij))
                self.knoppen.append(UI.Knop((sx, 600, 230, 56), "%s: %s" % (UI.T("hulp"), UI.T("aan") if self.app.hulp else UI.T("uitm")),
                                            self.app.wissel_hulp, UI.VAK, 20))
        self.knoppen.append(UI.Knop((sx, 670, 110, 56), UI.T("menu"), self.app.naar_menu, UI.VAK, 20))
        self.knoppen.append(UI.Knop((sx + 120, 670, 110, 56), UI.T("regels"), lambda: setattr(self.app, "toon_regels", True), UI.VAK, 18))
        for k in self.knoppen:
            k.teken(d, muis)
        UI.tekst(d, T("toetsen_zee"), 17, UI.ZACHT, (40, UI.H - 28), vet=False)

    def wacht_tekst(self):
        return T("comp_schiet")


# ------------------------------------------------------------------ online tegen elkaar
TX.update({
    "wacht_vloot": ("Wacht tot %s zijn schepen heeft neergezet...", "Waiting for %s to place the ships..."),
    "hij_klaar": ("%s is al klaar met plaatsen.", "%s has already placed the ships."),
    "hij_schiet": ("%s mikt...", "%s is aiming..."),
    "hij_zonk": ("%s liet je schip van %d zinken.", "%s sank your ship of %d."),
})


class OnlineZeeslag(Zeeslag):
    """Zeeslag op twee pc's. De server houdt beide vloten geheim en zegt alleen mis, raak of gezonken."""

    def __init__(self, app, adres, code, naam, token):
        self.lijn = None
        self.code = code
        self.ik = None
        self.ander = None
        self.verbonden = [False, False]
        self.status = UI.T("verbinden")
        self.zetnr = None
        self.server_fase = "wachten"
        self.hij_klaar = False
        self.einde_gezien = False
        Zeeslag.__init__(self, app, 0)
        self.lijn = UI.online.Lijn(adres, code, {"t": "hallo", "naam": naam, "token": token}, pad="zee/kamer")

    def naam(self, sp):
        if self.ik is None:
            return UI.T("speler%d" % (sp + 1))
        return UI.T("jij") if sp == self.ik else (self.ander or UI.T("tegenspeler"))

    def nieuw_potje(self):
        if self.lijn is not None:
            self.lijn.stuur({"t": "nieuw"})
            self.app.geluid.speel("klik")
            return
        Zeeslag.nieuw_potje(self)
        self.zijn_vloot = []                         # geheim: we kennen alleen wat gezonken is
        self.beurt = -1

    def begin(self):
        if len(self.vloot) != len(SCHEPEN) or self.fase != "plaatsen":
            return
        if self.lijn.stuur({"t": "vloot", "vloot": [[list(c) for c in sch] for sch in self.vloot]}):
            self.fase = "wacht_vloot"
            self.app.geluid.speel("goed")
        else:
            self.status = UI.T("geen_server")

    def wacht_tekst(self):
        return T("hij_schiet") % self.naam(1 - self.mij)

    def schiet(self, x, y):
        if self.fase != "spel" or self.beurt != self.mij or self.klaar:
            return
        if self.mijn_schoten.g[x][y] != 0:
            self.melding = T("al")
            return
        if self.lijn.stuur({"t": "schiet", "x": int(x), "y": int(y)}):
            self.tip = None
            self.beurt = -1
            self.melding = UI.T("versturen")
        else:
            self.status = UI.T("geen_server")

    def update(self):
        nu = time.time()
        self.anim = [a for a in self.anim if nu - a[3] < 1.6]
        if self.lijn is None:
            return
        for b in self.lijn.haal():
            t = b.get("t")
            if t == "_verbonden":
                self.status = ""
            elif t in ("_fout", "_weg"):
                self.status = UI.T("geen_server")
            elif t == "welkom":
                self.ik = self.mij = b.get("speler")
            elif t == "fout":
                self.status = UI.T("kamer_vol") if b.get("fout") == "kamer vol" else str(b.get("fout"))[:60]
                if b.get("fout") == "vloot klopt niet":
                    self.fase = "plaatsen"
            elif t == "stand":
                try:
                    self.pas_toe(b)
                except Exception:
                    import traceback
                    UI.log_fout(traceback.format_exc())

    def pas_toe(self, st):
        self.ik = self.mij = st["ik"]
        self.score = list(st.get("score", [0, 0]))
        self.ander = (st.get("ander") or {}).get("naam")
        self.verbonden = st.get("verbonden", [True, True])
        self.hij_klaar = st.get("hij_klaar", False)
        f = st["fase"]
        nieuw_potje = self.server_fase == "einde" and f == "plaatsen"
        self.server_fase = f
        if f == "wachten":
            self.fase = "plaatsen" if self.fase == "plaatsen" else self.fase
            self.beurt = -1
            return
        if nieuw_potje:
            Zeeslag.nieuw_potje(self)
            self.zijn_vloot = []
            self.klaar = False
            self.einde_gezien = False
        if f == "plaatsen":
            if st.get("ik_klaar"):
                self.fase = "wacht_vloot"
                self.vloot = [[tuple(c) for c in sch] for sch in st.get("mijn_vloot") or []]
            elif self.fase not in ("plaatsen",):
                self.fase = "plaatsen"
            self.beurt = -1
            return
        # spel of einde
        self.fase = "spel"
        self.vloot = [[tuple(c) for c in sch] for sch in st.get("mijn_vloot") or []]
        self.mijn_schoten.g = [list(kol) for kol in st["kennis"]]
        gez = [[tuple(c) for c in sch] for sch in st.get("gezonken") or []]
        over = list(SCHEPEN)
        for sch in gez:
            if len(sch) in over:
                over.remove(len(sch))
        self.mijn_schoten.over = over
        self.zijn_vloot = gez
        self.zijn_schoten.g = [list(kol) for kol in st["op_mij"]]
        self.beurt = st["beurt"]
        if st["zetnr"] != self.zetnr:
            eerste = self.zetnr is None
            self.zetnr = st["zetnr"]
            l = st.get("laatste")
            if l and not eerste:
                ik = l["door"] == self.ik
                uit = ("gezonken", [None] * l["lengte"]) if l["uit"] == "gezonken" else l["uit"]
                x, y = l["x"], l["y"]
                gx, gy = (GX + x * GROOT + GROOT // 2, GY + y * GROOT + GROOT // 2) if ik else (KX + x * KLEIN + KLEIN // 2, KY + y * KLEIN + KLEIN // 2)
                speel(self.app, "schot")
                if uit == "mis":
                    self.anim.append([gx, gy, "plons", time.time(), ik])
                    speel(self.app, "plons")
                    self.melding = T("mis") if ik else ""
                else:
                    self.anim.append([gx, gy, "boem", time.time(), ik])
                    speel(self.app, "boem")
                    if isinstance(uit, tuple):
                        self.melding = (T("gezonken") % l["lengte"]) if ik else (T("hij_zonk") % (self.naam(1 - self.ik), l["lengte"]))
                    else:
                        self.melding = T("raak") if ik else ""
        if f == "einde":
            self.klaar = True
            w = st.get("winnaar")
            alles = [[tuple(c) for c in sch] for sch in st.get("zijn_vloot") or []]
            if alles:
                self.zijn_vloot = alles
            self.uitslag = UI.T("wint") % self.naam(w)
            if not self.einde_gezien:
                self.einde_gezien = True
                self.app.geluid.speel("win" if w == self.ik else "verlies")

    def teken(self, d, muis):
        if self.fase == "wacht_vloot":
            # eigen vloot staat klaar; wachten op de ander
            d.fill(UI.ACHTER)
            UI.tekst(d, T("zee"), 40, UI.ACCENT, (40, 14))
            self.teken_zee(d, GX, GY, GROOT)
            for sch in self.vloot:
                self.teken_schip(d, sch, GX, GY, GROOT)
            UI.tekst(d, T("wacht_vloot") % (self.ander or UI.T("tegenspeler")), 26, UI.GOUD, (GX, 70))
            self.knoppen = [UI.Knop((GX + N * GROOT + 30, 670, 230, 56), UI.T("menu"), self.app.naar_menu, UI.VAK, 20)]
            for k in self.knoppen:
                k.teken(d, muis)
        else:
            Zeeslag.teken(self, d, muis)
            if self.fase == "plaatsen" and self.hij_klaar:
                UI.tekst(d, T("hij_klaar") % (self.ander or UI.T("tegenspeler")), 20, UI.GOUD, (40, 700))
        sx = GX + N * GROOT + 30
        UI.tekst(d, UI.T("kamer") % self.code, 20, UI.ACCENT, (sx, 108))
        if self.status:
            UI.tekst(d, self.status, 18, UI.ROOD, (sx, 470))
        elif self.ik is not None and self.ander and not self.verbonden[1 - self.ik]:
            for i, regel in enumerate(UI.Backgammon._knip(None, UI.T("ander_weg") % self.ander, 18, 230)):
                UI.tekst(d, regel, 18, UI.GOUD, (sx, 470 + i * 24))
        if self.server_fase == "wachten":
            UI.tekst(d, UI.T("wacht_ander") % self.code, 22, UI.GOUD, (40, 700))

    def stop(self):
        if self.lijn:
            self.lijn.stop()
