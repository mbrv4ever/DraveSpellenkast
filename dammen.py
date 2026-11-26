# -*- coding: utf-8 -*-
"""DraveSpellenkast - Dammen (internationaal, 10x10), tegen de computer of online tegen elkaar.
Slaan is verplicht, en je moet de meeste stukken slaan. Een dam vliegt over de lijn.
Copyright (C) 2026 Dravenlock (Roger & Claudio). GNU GPL v3.0."""
import random
import threading
import time

import pygame

UI = None          # wordt door main.py gezet

N = 10
VAK = 70
BX, BY = 60, 70
WIT, ZWART = 1, -1
LICHT_VAK = (226, 214, 236)
DONKER_VAK = (98, 82, 138)
STUK = {WIT: ((244, 240, 230), (196, 186, 170)), ZWART: ((52, 42, 72), (24, 18, 36))}
RICHT = ((-1, -1), (-1, 1), (1, -1), (1, 1))

TX = {
    "dam": ("Dammen", "Draughts"),
    "dam_sub": ("Het echte Hollandse dambord: 10 bij 10", "The real Dutch board: 10 by 10"),
    "jouw_beurt": ("Jouw beurt: klik een stuk, dan waar het heen moet", "Your turn: click a piece, then where it goes"),
    "moet_slaan": ("Je moet slaan! (gouden randje = deze stukken kunnen slaan)", "You must capture! (gold ring = these pieces can capture)"),
    "meeste": ("Je moet de meeste stukken slaan: %d.", "You must capture the most pieces: %d."),
    "comp_denkt": ("De computer denkt...", "The computer is thinking..."),
    "gelijk": ("Remise! Niemand kan nog winnen.", "A draw! Nobody can win any more."),
    "dam_erbij": ("Een dam! Die mag ver over de lijn vliegen.", "A king! It may fly far along the line."),
    "tip_kop": ("Tip: het gouden stuk naar het gouden vakje.", "Tip: the gold piece to the gold square."),
    "geen_zet": ("Geen zet meer mogelijk.", "No move possible any more."),
    "toetsen_dam": ("Klik een stuk en dan een vakje  ·  T = tip  ·  Backspace = ander stuk  ·  Esc = menu",
                    "Click a piece, then a square  ·  T = tip  ·  Backspace = other piece  ·  Esc = menu"),
    "geslagen": ("Geslagen: %d", "Captured: %d"),
    "stukken": ("Stukken: %d", "Pieces: %d"),
}


def T(k):
    if k in TX:
        v = TX[k]
        return v[0] if UI.TAAL == "nl" else v[1]
    return UI.T(k)


# ------------------------------------------------------------------ spelregels
def beginbord():
    b = [[0] * N for _ in range(N)]
    for r in range(N):
        for c in range(N):
            if (r + c) % 2 == 1:
                if r < 4:
                    b[r][c] = ZWART
                elif r > 5:
                    b[r][c] = WIT
    return b


def kleur(x):
    return 1 if x > 0 else (-1 if x < 0 else 0)


def binnen(r, c):
    return 0 <= r < N and 0 <= c < N


def slagen_van(b, r, c):
    """Alle slagreeksen van het stuk op (r, c): lijst van (pad, geslagen). Pad begint op (r, c)."""
    stuk = b[r][c]
    sp = kleur(stuk)
    dam = abs(stuk) == 2
    uit = []

    def leeg(x, y):
        return binnen(x, y) and (b[x][y] == 0 or (x, y) == (r, c))     # het eigen beginvakje is nu leeg

    def zoek(pr, pc, pad, weg):
        verder = False
        for dr, dc in RICHT:
            if dam:
                x, y = pr + dr, pc + dc
                while leeg(x, y):
                    x, y = x + dr, y + dc
                if not binnen(x, y) or kleur(b[x][y]) != -sp or (x, y) in weg:
                    continue
                lx, ly = x + dr, y + dc
                while leeg(lx, ly):
                    verder = True
                    zoek(lx, ly, pad + [(lx, ly)], weg + [(x, y)])
                    lx, ly = lx + dr, ly + dc
            else:
                x, y = pr + dr, pc + dc
                lx, ly = pr + 2 * dr, pc + 2 * dc
                if leeg(lx, ly) and kleur(b[x][y]) == -sp and (x, y) not in weg:
                    verder = True
                    zoek(lx, ly, pad + [(lx, ly)], weg + [(x, y)])
        if not verder and weg:
            uit.append((pad, weg))

    zoek(r, c, [(r, c)], [])
    return uit


def zetten(b, sp):
    """Alle geldige zetten voor sp: lijst van (pad, geslagen). Slaan is verplicht, de meeste stukken."""
    slagen = []
    for r in range(N):
        for c in range(N):
            if kleur(b[r][c]) == sp:
                slagen += slagen_van(b, r, c)
    if slagen:
        m = max(len(w) for _, w in slagen)
        uniek, gezien = [], set()
        for pad, w in slagen:
            if len(w) == m:
                sleutel = (pad[0], pad[-1], tuple(sorted(w)))
                if sleutel not in gezien:
                    gezien.add(sleutel)
                    uniek.append((pad, w))
        return uniek
    uit = []
    vooruit = -1 if sp == WIT else 1
    for r in range(N):
        for c in range(N):
            if kleur(b[r][c]) != sp:
                continue
            if abs(b[r][c]) == 2:
                for dr, dc in RICHT:
                    x, y = r + dr, c + dc
                    while binnen(x, y) and b[x][y] == 0:
                        uit.append(([(r, c), (x, y)], []))
                        x, y = x + dr, y + dc
            else:
                for dc in (-1, 1):
                    x, y = r + vooruit, c + dc
                    if binnen(x, y) and b[x][y] == 0:
                        uit.append(([(r, c), (x, y)], []))
    return uit


def doe(b, zet):
    """Voer een zet uit op een kopie. Geeft (nieuw bord, werd_dam)."""
    pad, weg = zet
    n = [rij[:] for rij in b]
    r, c = pad[0]
    stuk = n[r][c]
    n[r][c] = 0
    for x, y in weg:
        n[x][y] = 0
    er, ec = pad[-1]
    dam = False
    if abs(stuk) == 1 and ((stuk == WIT and er == 0) or (stuk == ZWART and er == N - 1)):
        stuk *= 2
        dam = True
    n[er][ec] = stuk
    return n, dam


def tel(b):
    s = {WIT: [0, 0], ZWART: [0, 0]}
    for rij in b:
        for x in rij:
            if x:
                s[kleur(x)][abs(x) - 1] += 1
    return s


def waarde(b, sp):
    s = 0
    for r in range(N):
        for c in range(N):
            x = b[r][c]
            if not x:
                continue
            k = kleur(x)
            if abs(x) == 2:
                v = 330
            else:
                vooruit = (N - 1 - r) if k == WIT else r
                v = 100 + vooruit * 4 + (6 if 3 <= c <= 6 else 0)
                if (k == WIT and r == N - 1) or (k == ZWART and r == 0):
                    v += 8                                       # achterste rij bewaken
            s += v if k == sp else -v
    return s


class TeLaat(Exception):
    pass


GRENS = [None]                                                   # tijdslimiet voor het nadenken


def zoek(b, diepte, sp, alfa, beta, wie):
    if GRENS[0] and time.time() > GRENS[0]:
        raise TeLaat()
    lijst = zetten(b, sp)
    if not lijst:
        return (-100000 - diepte if sp == wie else 100000 + diepte), None
    if diepte <= 0 and not lijst[0][1]:
        return waarde(b, wie), None
    if diepte <= -4:                                             # slagen doorrekenen, maar niet eindeloos
        return waarde(b, wie), None
    lijst.sort(key=lambda z: -len(z[1]))
    beste_z = lijst[0]
    if sp == wie:
        beste = -10 ** 9
        for z in lijst:
            v, _ = zoek(doe(b, z)[0], diepte - 1, -sp, alfa, beta, wie)
            if v > beste:
                beste, beste_z = v, z
            alfa = max(alfa, v)
            if alfa >= beta:
                break
    else:
        beste = 10 ** 9
        for z in lijst:
            v, _ = zoek(doe(b, z)[0], diepte - 1, -sp, alfa, beta, wie)
            if v < beste:
                beste, beste_z = v, z
            beta = min(beta, v)
            if alfa >= beta:
                break
    return beste, beste_z


def kies_zet(b, sp, niveau):
    lijst = zetten(b, sp)
    if not lijst:
        return None
    if len(lijst) == 1:
        return lijst[0]
    if niveau == 1:
        if random.random() < 0.5:
            _, z = zoek(b, 1, sp, -10 ** 9, 10 ** 9, sp)
            return z
        return random.choice(lijst)
    z = None
    GRENS[0] = time.time() + (1.5 if niveau == 2 else 3.0)      # nooit lang laten wachten
    try:
        for diepte in range(1, (3 if niveau == 2 else 6) + 1):  # steeds een stapje dieper, zolang er tijd is
            _, z = zoek(b, diepte, sp, -10 ** 9, 10 ** 9, sp)
    except TeLaat:
        pass
    finally:
        GRENS[0] = None
    if niveau == 2 and random.random() < 0.1:
        z = random.choice(lijst)
    return z or random.choice(lijst)


def zet_naar_lijst(z):
    return {"pad": [list(p) for p in z[0]], "weg": [list(p) for p in z[1]]}


def zet_van_lijst(d):
    return ([tuple(p) for p in d["pad"]], [tuple(p) for p in d["weg"]])


# ------------------------------------------------------------------ het spel
class Dammen:
    def __init__(self, app, niveau):
        self.app = app
        self.niveau = niveau
        self.mij = WIT
        self.knoppen = []
        self.score = {WIT: 0, ZWART: 0}
        self.begint = WIT
        self.nieuw_potje()

    def naam(self, sp):
        return UI.T("jij") if sp == self.mij else UI.T("computer")

    def nieuw_potje(self):
        self.b = beginbord()
        self.beurt = WIT                       # wit begint altijd (dammen)
        self.klaar = False
        self.uitslag = ""
        self.kies = None                       # gekozen stuk (r, c)
        self.anim = None                       # {"zet", "t", "stuk"}
        self.tip = None
        self.melding = ""
        self.denk = None
        self.stil = 0                          # zetten met alleen dammen, zonder slaan (remise-regel)
        self.laatste = None
        self.geslagen = {WIT: 0, ZWART: 0}
        self.lijst = zetten(self.b, self.beurt)

    # ---------- zetten
    def start_anim(self, z):
        r, c = z[0][0]
        if not self.b[r][c]:                   # mag niet gebeuren: bord loopt niet gelijk
            UI.log_fout("dammen: zet vanaf een leeg vakje %r" % (z,))
            return
        self.anim = {"zet": z, "t": 0.0, "stuk": self.b[r][c], "sp": kleur(self.b[r][c])}
        self.kies = None
        self.tip = None
        self.app.geluid.speel("klik")

    def doe_zet(self, z):
        if self.klaar or self.anim or z is None:
            return
        self.melding = ""
        self.start_anim(z)

    def klaar_met_zet(self):
        z, sp = self.anim["zet"], self.anim["sp"]
        self.anim = None
        oud_dam = abs(self.b[z[0][0][0]][z[0][0][1]]) == 2
        self.b, dam = doe(self.b, z)
        self.laatste = z
        self.geslagen[sp] += len(z[1])
        self.app.geluid.speel("goed" if z[1] else "zet")
        if dam and sp == self.mij:
            self.melding = T("dam_erbij")
        self.stil = self.stil + 1 if (oud_dam and not z[1]) else 0
        self.beurt = -sp
        self.lijst = zetten(self.b, self.beurt)
        self.controleer_einde(sp)

    def controleer_einde(self, sp):
        if not self.lijst:
            self.klaar = True
            self.score[sp] += 1
            self.uitslag = UI.T("wint") % self.naam(sp)
            self.app.geluid.speel("win" if sp == self.mij else "verlies")
        elif self.stil >= 50:
            self.klaar = True
            self.uitslag = T("gelijk")

    def update(self):
        if self.anim:
            z = self.anim["zet"]
            self.anim["t"] += 0.11 if len(z[0]) <= 2 else 0.07
            if self.anim["t"] >= len(z[0]) - 1:
                self.klaar_met_zet()
            return
        if self.klaar or self.beurt == self.mij:
            return
        if self.denk is None:
            self.denk = {"z": None, "klaar": False, "start": time.time()}
            bord = [rij[:] for rij in self.b]
            def denk(d=self.denk, bord=bord, sp=self.beurt):
                d["z"] = kies_zet(bord, sp, self.niveau)
                d["klaar"] = True
            threading.Thread(target=denk, daemon=True).start()
        elif self.denk["klaar"] and time.time() - self.denk["start"] > 0.6:
            z = self.denk["z"]
            self.denk = None
            self.doe_zet(z)

    def wacht_tekst(self):
        return T("comp_denkt")

    # ---------- hulp
    def geef_tip(self):
        if self.klaar or self.beurt != self.mij or self.anim:
            return
        _, z = zoek(self.b, 3, self.mij, -10 ** 9, 10 ** 9, self.mij)
        if z:
            self.tip = z
            self.kies = None
            self.melding = T("tip_kop")
            self.app.geluid.speel("goed")

    def stukken_die_kunnen(self):
        return {z[0][0] for z in self.lijst}

    # ---------- invoer
    def vak_op(self, pos):
        x, y = pos
        c, r = (x - BX) // VAK, (y - BY) // VAK
        if self.mij == ZWART:                  # zwart speelt van onderen: bord omdraaien
            r, c = N - 1 - r, N - 1 - c
        return (int(r), int(c)) if binnen(r, c) and BX <= x and BY <= y else None

    def scherm_xy(self, r, c):
        if self.mij == ZWART:
            r, c = N - 1 - r, N - 1 - c
        return BX + c * VAK + VAK // 2, BY + r * VAK + VAK // 2

    def klik(self, pos):
        if self.klaar or self.beurt != self.mij or self.anim:
            return
        v = self.vak_op(pos)
        if v is None:
            return
        if v in self.stukken_die_kunnen():
            self.kies = v
            self.app.geluid.speel("klik")
            return
        if self.kies:
            for z in self.lijst:
                if z[0][0] == self.kies and z[0][-1] == v:
                    self.doe_zet(z)
                    return
        if self.b[v[0]][v[1]] and kleur(self.b[v[0]][v[1]]) == self.mij and self.lijst and self.lijst[0][1]:
            self.melding = T("moet_slaan")
            self.app.geluid.speel("fout")

    def toets(self, e):
        if e.key == pygame.K_ESCAPE:
            self.app.naar_menu()
        elif self.klaar and e.key in (pygame.K_SPACE, pygame.K_RETURN):
            self.nieuw_potje()
        elif e.key == pygame.K_t:
            self.geef_tip()
        elif e.key == pygame.K_BACKSPACE:
            self.kies = None

    # ---------- tekenen
    def teken_stuk(self, d, x, y, stuk, rand=None, alfa=255):
        x, y = int(x), int(y)
        boven, onder = STUK[kleur(stuk)]
        rr = VAK // 2 - 7
        if alfa < 255:
            s = pygame.Surface((VAK, VAK), pygame.SRCALPHA)
            pygame.draw.circle(s, boven + (alfa,), (VAK // 2, VAK // 2), rr)
            d.blit(s, (x - VAK // 2, y - VAK // 2))
            return
        pygame.draw.circle(d, onder, (x, y + 5), rr)
        pygame.draw.circle(d, boven, (x, y), rr)
        pygame.draw.circle(d, onder, (x, y), rr - 9, 3)
        pygame.draw.circle(d, onder, (x, y), rr - 18, 2)
        if abs(stuk) == 2:                     # dam: kroontje
            kl = UI.GOUD
            pts = [(x - 16, y + 8), (x - 16, y - 6), (x - 8, y + 1), (x, y - 12), (x + 8, y + 1), (x + 16, y - 6), (x + 16, y + 8)]
            pygame.draw.polygon(d, kl, pts)
            pygame.draw.polygon(d, (90, 64, 20), pts, 2)
        if rand:
            pygame.draw.circle(d, rand, (x, y), rr + 4, 5)

    def teken(self, d, muis):
        d.fill(UI.ACHTER)
        UI.tekst(d, T("dam"), 40, UI.ACCENT, (BX, 14))
        bord = pygame.Rect(BX - 10, BY - 10, N * VAK + 20, N * VAK + 20)
        pygame.draw.rect(d, (60, 48, 90), bord, border_radius=14)
        pygame.draw.rect(d, UI.RAND, bord, 4, border_radius=14)
        for r in range(N):
            for c in range(N):
                x, y = self.scherm_xy(r, c)
                pygame.draw.rect(d, DONKER_VAK if (r + c) % 2 else LICHT_VAK, (x - VAK // 2, y - VAK // 2, VAK, VAK))
        if self.laatste and not self.anim:     # vorige zet zacht laten zien
            for (r, c) in (self.laatste[0][0], self.laatste[0][-1]):
                x, y = self.scherm_xy(r, c)
                pygame.draw.rect(d, (150, 130, 200), (x - VAK // 2, y - VAK // 2, VAK, VAK), 4)
        mijn_beurt = not self.klaar and self.beurt == self.mij and not self.anim
        kunnen = self.stukken_die_kunnen() if mijn_beurt else set()
        slaan = mijn_beurt and self.lijst and self.lijst[0][1]
        anim_van = self.anim["zet"][0][0] if self.anim else None
        weg_nu = set()
        if self.anim:
            z = self.anim["zet"]
            stap = int(self.anim["t"])
            weg_nu = set(z[1][:stap])          # zie de stukken verdwijnen tijdens de slag
        for r in range(N):
            for c in range(N):
                st = self.b[r][c]
                if not st or (r, c) == anim_van or (r, c) in weg_nu:
                    continue
                x, y = self.scherm_xy(r, c)
                rand = None
                if (r, c) == self.kies:
                    rand = UI.ACCENT
                elif self.tip and (r, c) == self.tip[0][0]:
                    rand = UI.GOUD
                elif slaan and (r, c) in kunnen and self.app.hulp:
                    rand = UI.GOUD
                self.teken_stuk(d, x, y, st, rand)
        # doelen van het gekozen stuk
        if self.kies and mijn_beurt:
            for z in self.lijst:
                if z[0][0] == self.kies:
                    x, y = self.scherm_xy(*z[0][-1])
                    pygame.draw.circle(d, UI.ACCENT, (x, y), 14)
                    if self.app.hulp:
                        for (wr, wc) in z[1]:
                            wx, wy = self.scherm_xy(wr, wc)
                            pygame.draw.line(d, UI.ROOD, (wx - 14, wy - 14), (wx + 14, wy + 14), 5)
                            pygame.draw.line(d, UI.ROOD, (wx - 14, wy + 14), (wx + 14, wy - 14), 5)
        if self.tip and mijn_beurt:
            x, y = self.scherm_xy(*self.tip[0][-1])
            pygame.draw.circle(d, UI.GOUD, (x, y), 16)
        # bewegend stuk
        if self.anim:
            z, t = self.anim["zet"], self.anim["t"]
            i = min(int(t), len(z[0]) - 2)
            f = t - i
            (r1, c1), (r2, c2) = z[0][i], z[0][i + 1]
            x1, y1 = self.scherm_xy(r1, c1)
            x2, y2 = self.scherm_xy(r2, c2)
            hop = -18 * (1 - (2 * f - 1) ** 2) if z[1] else 0
            self.teken_stuk(d, x1 + (x2 - x1) * f, y1 + (y2 - y1) * f + hop, self.anim["stuk"])
        # rechts: spelers, score, meldingen, knoppen
        px = BX + N * VAK + 50
        tel_ = tel(self.b)
        for i, sp in enumerate((self.mij, -self.mij)):
            y = 130 + i * 92
            self.teken_stuk(d, px + 30, y + 32, sp)
            UI.tekst(d, self.naam(sp), 28, UI.TEKST, (px + 76, y + 4))
            UI.tekst(d, "%s  ·  %s" % (T("stukken") % sum(tel_[sp]), T("geslagen") % self.geslagen[sp]), 18, UI.ZACHT, (px + 76, y + 40), vet=False)
            UI.tekst(d, str(self.score[sp]), 30, UI.GOUD, (UI.W - 50, y + 4), rechts=True)
            if not self.klaar and self.beurt == sp:
                pygame.draw.rect(d, UI.ACCENT, (px - 12, y - 6, UI.W - px - 26, 82), 3, border_radius=12)
        y = 330
        if self.klaar:
            regels = [self.uitslag]
        elif self.beurt != self.mij:
            regels = [self.wacht_tekst()]
        else:
            regels = [T("jouw_beurt")]
            if slaan and not self.melding:
                regels.append(T("moet_slaan"))
                if len(self.lijst[0][1]) > 1:
                    regels.append(T("meeste") % len(self.lijst[0][1]))
        if self.melding:
            regels.append(self.melding)
        for regel in regels:
            for stuk in UI.Backgammon._knip(None, regel, 22, UI.W - px - 30):
                UI.tekst(d, stuk, 22, UI.GOUD if regel in (self.melding, self.uitslag) else UI.TEKST, (px, y), vet=True)
                y += 30
            y += 8
        self.knoppen = []
        if self.klaar:
            self.knoppen.append(UI.Knop((px, 560, 300, 70), UI.T("nog"), self.nieuw_potje, UI.GROEN, 26))
        else:
            self.knoppen.append(UI.Knop((px, 560, 130, 70), UI.T("tip"), self.geef_tip, UI.GOUD, 26, aan=mijn_beurt))
            self.knoppen.append(UI.Knop((px + 145, 560, 260, 70), "%s: %s" % (UI.T("hulp"), UI.T("aan") if self.app.hulp else UI.T("uitm")),
                                        self.app.wissel_hulp, UI.VAK, 22))
        self.knoppen.append(UI.Knop((px, 650, 190, 60), UI.T("menu"), self.app.naar_menu, UI.VAK, 24))
        self.knoppen.append(UI.Knop((px + 205, 650, 200, 60), UI.T("regels"), lambda: setattr(self.app, "toon_regels", True), UI.VAK, 22))
        for k in self.knoppen:
            k.teken(d, muis)
        UI.tekst(d, T("toetsen_dam"), 16, UI.ZACHT, (px, UI.H - 34), vet=False)


# ------------------------------------------------------------------ online tegen elkaar
class OnlineDammen(Dammen):
    """Dammen op twee pc's. De server geeft de zetten door; beide pc's rekenen met dezelfde regels."""

    def __init__(self, app, adres, code, naam, token):
        self.lijn = None
        self.code = code
        self.ik = None
        self.ander = None
        self.verbonden = [False, False]
        self.status = UI.T("verbinden")
        self.fase = "wachten"
        self.n_zetten = 0                      # hoeveel zetten van de server al verwerkt
        self.potje = None
        self.eerste = 0
        self.einde_gezien = False
        Dammen.__init__(self, app, 0)
        self.beurt = 0
        self.lijn = UI.online.Lijn(adres, code, {"t": "hallo", "spel": "dam", "naam": naam, "token": token}, pad="zet/kamer")

    def kleur_van(self, idx):
        return WIT if idx == self.eerste else ZWART

    def naam(self, sp):
        if self.ik is None:
            return UI.T("speler1" if sp == WIT else "speler2")
        return UI.T("jij") if sp == self.mij else (self.ander or UI.T("tegenspeler"))

    def nieuw_potje(self):
        if self.lijn is not None:
            self.lijn.stuur({"t": "nieuw"})
            self.app.geluid.speel("klik")
            return
        Dammen.nieuw_potje(self)

    def wacht_tekst(self):
        if self.fase == "wachten":
            return UI.T("wacht_ander") % self.code
        return UI.T("ander_beurt") % self.naam(self.beurt)

    def doe_zet(self, z):
        if self.klaar or self.anim or z is None or self.beurt != self.mij or self.fase != "spel":
            return
        nb, _ = doe(self.b, z)
        oud_dam = abs(self.b[z[0][0][0]][z[0][0][1]]) == 2
        stil = self.stil + 1 if (oud_dam and not z[1]) else 0
        einde = None
        if not zetten(nb, -self.mij):
            einde = self.ik
        elif stil >= 50:
            einde = -1
        if self.lijn.stuur({"t": "zet", "z": zet_naar_lijst(z), "einde": einde}):
            self.melding = ""
            self.n_zetten += 1
            self.start_anim(z)
            self.herzien = True
        else:
            self.status = UI.T("geen_server")

    def controleer_einde(self, sp):
        pass                                   # de server zegt wanneer het potje klaar is

    def update(self):
        if self.anim:
            Dammen.update(self)
            return
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
                self.stand = b
                try:
                    self.pas_toe(b)
                except Exception:
                    import traceback
                    UI.log_fout(traceback.format_exc())
        if not self.anim and getattr(self, "stand", None) and getattr(self, "herzien", False):
            self.herzien = False
            self.pas_toe(self.stand)           # na het schuiven: nog een zet, of is het potje klaar?

    def pas_toe(self, st):
        self.ik = st["ik"]
        self.eerste = st.get("eerste", 0)
        self.mij = self.kleur_van(self.ik)
        sc = st.get("score", [0, 0])
        self.score = {self.kleur_van(0): sc[0], self.kleur_van(1): sc[1]}
        self.ander = (st.get("ander") or {}).get("naam")
        self.verbonden = st.get("verbonden", [True, True])
        self.fase = st["fase"]
        if self.fase == "wachten":
            self.beurt = 0
            return
        lijst = st.get("zetten") or []
        if st.get("potje") == self.potje and len(lijst) < self.n_zetten:
            return                             # oud bericht (mijn eigen zet is nog onderweg): overslaan
        if st.get("potje") != self.potje or (self.n_zetten == 0 and len(lijst) > 1):
            self.potje = st.get("potje")      # nieuw potje, of opnieuw verbonden: alles naspelen
            Dammen.nieuw_potje(self)
            self.n_zetten = 0
            for d in lijst[:-1]:
                z = zet_van_lijst(d["z"])
                oud_dam = abs(self.b[z[0][0][0]][z[0][0][1]]) == 2
                self.b, _ = doe(self.b, z)
                self.stil = self.stil + 1 if (oud_dam and not z[1]) else 0
                self.geslagen[self.kleur_van(d["sp"])] += len(z[1])
                self.laatste = z
                self.n_zetten += 1
            self.beurt = self.kleur_van(lijst[-1]["sp"]) if lijst else WIT
            self.lijst = zetten(self.b, self.beurt)
            self.einde_gezien = False
        if self.anim:
            self.herzien = True
            return
        if len(lijst) > self.n_zetten:         # nieuwe zet van de ander: laten zien
            d = lijst[self.n_zetten]
            z = zet_van_lijst(d["z"])
            self.beurt = self.kleur_van(d["sp"])
            self.lijst = zetten(self.b, self.beurt)
            if not any(z[0] == x[0] and sorted(z[1]) == sorted(x[1]) for x in self.lijst):
                UI.log_fout("dammen online: onbekende zet %r" % (d,))
            self.n_zetten += 1
            self.start_anim(z)
            self.herzien = True
            return
        self.beurt = self.kleur_van(st["beurt"]) if st["fase"] == "spel" else self.beurt
        self.lijst = zetten(self.b, self.beurt)
        if st["fase"] == "einde":
            self.klaar = True
            w = st.get("winnaar")
            self.uitslag = T("gelijk") if w == -1 else (UI.T("wint") % self.naam(self.kleur_van(w)))
            if not self.einde_gezien:
                self.einde_gezien = True
                self.app.geluid.speel("win" if w == self.ik else ("klik" if w == -1 else "verlies"))
        else:
            self.klaar = False

    def teken(self, d, muis):
        Dammen.teken(self, d, muis)
        px = BX + N * VAK + 50
        if self.status:
            UI.tekst(d, self.status, 20, UI.ROOD, (px, 520))
        elif self.ik is not None and self.ander and not self.verbonden[1 - self.ik]:
            UI.tekst(d, UI.T("ander_weg") % self.ander, 20, UI.GOUD, (px, 520))
        UI.tekst(d, UI.T("kamer") % self.code, 20, UI.ACCENT, (px, 80))
        if self.fase == "wachten":
            UI.tekst(d, self.code, 56, UI.GOUD, (px, 440))

    def stop(self):
        if self.lijn:
            self.lijn.stop()
