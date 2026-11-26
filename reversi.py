# -*- coding: utf-8 -*-
"""DraveSpellenkast - Reversi: sluit schijven van de ander in, dan draaien ze om naar jouw kleur.
Tegen de computer of online tegen elkaar. Copyright (C) 2026 Dravenlock (Roger & Claudio). GNU GPL v3.0."""
import random
import threading
import time

import pygame

UI = None          # wordt door main.py gezet

N = 8
VAK = 84
BX, BY = 60, 62
ZWART, WIT = 1, -1                     # zwart begint
KLEUR = {ZWART: ((40, 32, 56), (20, 16, 30)), WIT: ((246, 242, 234), (190, 182, 170))}
RICHT = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
GEWICHT = [
    [120, -20, 20, 5, 5, 20, -20, 120],
    [-20, -40, -5, -5, -5, -5, -40, -20],
    [20, -5, 15, 3, 3, 15, -5, 20],
    [5, -5, 3, 3, 3, 3, -5, 5],
    [5, -5, 3, 3, 3, 3, -5, 5],
    [20, -5, 15, 3, 3, 15, -5, 20],
    [-20, -40, -5, -5, -5, -5, -40, -20],
    [120, -20, 20, 5, 5, 20, -20, 120],
]

TX = {
    "rev": ("Reversi", "Reversi"),
    "jouw_beurt": ("Jouw beurt: klik op een vakje met een stipje.", "Your turn: click a square with a dot."),
    "comp_denkt": ("De computer denkt...", "The computer is thinking..."),
    "pas_jij": ("Jij kunt niet zetten: je moet passen.", "You cannot move: you must pass."),
    "pas_ander": ("%s kan niet zetten en past.", "%s cannot move and passes."),
    "gelijk": ("Gelijkspel!", "A draw!"),
    "uitslag": ("%s wint met %d tegen %d!", "%s wins %d to %d!"),
    "tip_kop": ("Tip: zet op het gouden vakje.", "Tip: play the gold square."),
    "hoekje": ("Hoeken zijn goud waard: die kan de ander nooit meer omdraaien!", "Corners are gold: the other can never flip them back!"),
    "toetsen_rev": ("Klik een vakje met een stipje  ·  T = tip  ·  Esc = menu", "Click a square with a dot  ·  T = tip  ·  Esc = menu"),
}


def T(k):
    if k in TX:
        v = TX[k]
        return v[0] if UI.TAAL == "nl" else v[1]
    return UI.T(k)


def beginbord():
    b = [[0] * N for _ in range(N)]
    b[3][3] = b[4][4] = WIT
    b[3][4] = b[4][3] = ZWART
    return b


def omdraai(b, r, c, sp):
    """Welke schijven draaien om als sp op (r, c) zet."""
    if b[r][c]:
        return []
    uit = []
    for dr, dc in RICHT:
        x, y = r + dr, c + dc
        lijn = []
        while 0 <= x < N and 0 <= y < N and b[x][y] == -sp:
            lijn.append((x, y))
            x, y = x + dr, y + dc
        if lijn and 0 <= x < N and 0 <= y < N and b[x][y] == sp:
            uit += lijn
    return uit


def zetten(b, sp):
    return [(r, c) for r in range(N) for c in range(N) if not b[r][c] and omdraai(b, r, c, sp)]


def doe(b, zet, sp):
    n = [rij[:] for rij in b]
    if zet is None:
        return n
    r, c = zet
    for x, y in omdraai(b, r, c, sp):
        n[x][y] = sp
    n[r][c] = sp
    return n


def tel(b):
    z = sum(1 for rij in b for x in rij if x == ZWART)
    w = sum(1 for rij in b for x in rij if x == WIT)
    return {ZWART: z, WIT: w}


def waarde(b, sp):
    s = 0
    for r in range(N):
        for c in range(N):
            if b[r][c]:
                s += GEWICHT[r][c] * (1 if b[r][c] == sp else -1)
    s += 5 * (len(zetten(b, sp)) - len(zetten(b, -sp)))
    return s


def zoek(b, diepte, sp, alfa, beta, wie, grens):
    if time.time() > grens:
        raise TimeoutError
    mijn = zetten(b, sp)
    if not mijn and not zetten(b, -sp):
        t = tel(b)
        verschil = t[wie] - t[-wie]
        return (10000 + verschil if verschil > 0 else -10000 + verschil if verschil < 0 else 0), None
    if diepte == 0:
        return waarde(b, wie), None
    if not mijn:
        v, _ = zoek(b, diepte - 1, -sp, alfa, beta, wie, grens)
        return v, None
    mijn.sort(key=lambda z: -GEWICHT[z[0]][z[1]])
    beste_z = mijn[0]
    if sp == wie:
        beste = -10 ** 9
        for z in mijn:
            v, _ = zoek(doe(b, z, sp), diepte - 1, -sp, alfa, beta, wie, grens)
            if v > beste:
                beste, beste_z = v, z
            alfa = max(alfa, v)
            if alfa >= beta:
                break
    else:
        beste = 10 ** 9
        for z in mijn:
            v, _ = zoek(doe(b, z, sp), diepte - 1, -sp, alfa, beta, wie, grens)
            if v < beste:
                beste, beste_z = v, z
            beta = min(beta, v)
            if alfa >= beta:
                break
    return beste, beste_z


def kies_zet(b, sp, niveau):
    mijn = zetten(b, sp)
    if not mijn:
        return None
    if niveau == 1:                                  # makkelijk: pakt meestal gewoon de meeste schijven
        if random.random() < 0.4:
            return random.choice(mijn)
        return max(mijn, key=lambda z: len(omdraai(b, z[0], z[1], sp)) + random.random())
    grens = time.time() + (1.2 if niveau == 2 else 2.5)
    beste = mijn[0]
    try:
        for diepte in range(1, (3 if niveau == 2 else 8) + 1):
            _, z = zoek(b, diepte, sp, -10 ** 9, 10 ** 9, sp, grens)
            if z:
                beste = z
    except TimeoutError:
        pass
    return beste


# ------------------------------------------------------------------ het spel
class Reversi:
    def __init__(self, app, niveau):
        self.app = app
        self.niveau = niveau
        self.knoppen = []
        self.score = {ZWART: 0, WIT: 0}
        self.volgende = ZWART
        self.mij = ZWART
        self.nieuw_potje()

    def naam(self, sp):
        return UI.T("jij") if sp == self.mij else UI.T("computer")

    def nieuw_potje(self):
        if self.niveau:
            self.mij = self.volgende
            self.volgende = -self.volgende
        self.b = beginbord()
        self.beurt = ZWART
        self.klaar = False
        self.uitslag = ""
        self.melding = ""
        self.anim = None                # {"zet", "draai", "sp", "t"}
        self.denk = None
        self.laatste = None
        self.tip = None
        self.pas_t = 0.0

    # ---------- zetten
    def doe_zet(self, zet):
        if self.klaar or self.anim:
            return
        sp = self.beurt
        if zet is None:
            self.melding = T("pas_jij") if sp == self.mij else T("pas_ander") % self.naam(sp)
            self.beurt = -sp
            self.na_zet()
            return
        draai = omdraai(self.b, zet[0], zet[1], sp)
        if not draai:
            return
        self.b[zet[0]][zet[1]] = sp
        self.anim = {"zet": zet, "draai": draai, "sp": sp, "t": time.time()}
        self.laatste = zet
        self.tip = None
        self.melding = T("hoekje") if sp == self.mij and zet in ((0, 0), (0, 7), (7, 0), (7, 7)) and self.app.hulp else ""
        self.app.geluid.speel("zet")

    def klaar_anim(self):
        a = self.anim
        for x, y in a["draai"]:
            self.b[x][y] = a["sp"]
        self.anim = None
        self.beurt = -a["sp"]
        self.na_zet()

    def na_zet(self):
        if not zetten(self.b, ZWART) and not zetten(self.b, WIT):
            self.klaar = True
            t = tel(self.b)
            if t[ZWART] == t[WIT]:
                self.uitslag = T("gelijk")
                self.app.geluid.speel("klik")
            else:
                w = ZWART if t[ZWART] > t[WIT] else WIT
                self.score[w] += 1
                self.uitslag = T("uitslag") % (self.naam(w), t[w], t[-w])
                self.app.geluid.speel("win" if w == self.mij else "verlies")

    def update(self):
        if self.anim:
            if time.time() - self.anim["t"] > 0.15 + 0.05 * len(self.anim["draai"]):
                self.klaar_anim()
            return
        if self.klaar:
            return
        if not zetten(self.b, self.beurt):           # niemand hoeft op een knop te drukken om te passen
            if self.pas_t == 0:
                self.pas_t = time.time()
            elif time.time() - self.pas_t > 1.2:
                self.pas_t = 0
                self.pas()
            return
        if self.beurt == self.mij:
            return
        self.computer()

    def pas(self):
        self.doe_zet(None)

    def computer(self):
        if self.denk is None:
            self.denk = {"z": None, "klaar": False, "start": time.time()}
            bord = [rij[:] for rij in self.b]
            def denk(d=self.denk, bord=bord, sp=self.beurt):
                d["z"] = kies_zet(bord, sp, self.niveau)
                d["klaar"] = True
            threading.Thread(target=denk, daemon=True).start()
        elif self.denk["klaar"] and time.time() - self.denk["start"] > 0.7:
            z = self.denk["z"]
            self.denk = None
            self.doe_zet(z)

    def wacht_tekst(self):
        return T("comp_denkt")

    def geef_tip(self):
        if self.klaar or self.beurt != self.mij or self.anim:
            return
        z = kies_zet(self.b, self.mij, 2)
        if z:
            self.tip = z
            self.melding = T("tip_kop")
            self.app.geluid.speel("goed")

    # ---------- invoer
    def vak_op(self, pos):
        x, y = pos
        c, r = (x - BX) // VAK, (y - BY) // VAK
        if 0 <= r < N and 0 <= c < N and x >= BX and y >= BY:
            return int(r), int(c)
        return None

    def klik(self, pos):
        if self.klaar or self.beurt != self.mij or self.anim:
            return
        v = self.vak_op(pos)
        if v and omdraai(self.b, v[0], v[1], self.mij):
            self.doe_zet(v)
        elif v:
            self.app.geluid.speel("fout")

    def toets(self, e):
        if e.key == pygame.K_ESCAPE:
            self.app.naar_menu()
        elif self.klaar and e.key in (pygame.K_SPACE, pygame.K_RETURN):
            self.nieuw_potje()
        elif e.key == pygame.K_t:
            self.geef_tip()

    # ---------- tekenen
    def teken_schijf(self, d, x, y, sp, breed=1.0):
        boven, onder = KLEUR[sp]
        rr = VAK // 2 - 8
        w = max(3, int(2 * rr * breed))
        pygame.draw.ellipse(d, onder, (x - w // 2, y - rr + 4, w, 2 * rr))
        pygame.draw.ellipse(d, boven, (x - w // 2, y - rr, w, 2 * rr))
        if breed > 0.6:
            pygame.draw.ellipse(d, onder, (x - w // 2 + 10, y - rr + 10, w - 20, 2 * rr - 20), 3)

    def teken(self, d, muis):
        d.fill(UI.ACHTER)
        UI.tekst(d, T("rev"), 40, UI.ACCENT, (BX, 8))
        bord = pygame.Rect(BX - 10, BY - 10, N * VAK + 20, N * VAK + 20)
        pygame.draw.rect(d, (34, 84, 60), bord, border_radius=14)
        pygame.draw.rect(d, UI.RAND, bord, 4, border_radius=14)
        mijn_beurt = not self.klaar and self.beurt == self.mij and not self.anim
        mog = set(zetten(self.b, self.mij)) if mijn_beurt else set()
        for r in range(N):
            for c in range(N):
                x, y = BX + c * VAK, BY + r * VAK
                pygame.draw.rect(d, (46, 120, 82) if (r + c) % 2 else (42, 110, 76), (x, y, VAK, VAK))
                pygame.draw.rect(d, (28, 70, 50), (x, y, VAK, VAK), 2)
        for (r, c) in ((2, 2), (2, 6), (6, 2), (6, 6)):
            pygame.draw.circle(d, (28, 70, 50), (BX + c * VAK, BY + r * VAK), 6)
        draai = set(map(tuple, self.anim["draai"])) if self.anim else set()
        f = 0.0
        if self.anim:
            f = min(1.0, (time.time() - self.anim["t"]) / (0.15 + 0.05 * len(self.anim["draai"])))
        for r in range(N):
            for c in range(N):
                x, y = BX + c * VAK + VAK // 2, BY + r * VAK + VAK // 2
                sp = self.b[r][c]
                if sp:
                    if (r, c) in draai:                 # omdraaien: smal worden en dan de andere kleur
                        breed = abs(1 - 2 * f)
                        self.teken_schijf(d, x, y, sp if f < 0.5 else self.anim["sp"], max(0.05, breed))
                    else:
                        self.teken_schijf(d, x, y, sp)
                    if self.laatste == (r, c) and not self.anim:
                        pygame.draw.circle(d, UI.ROOD, (x, y), 6)
                elif (r, c) in mog and self.app.hulp:
                    hover = self.vak_op(muis) == (r, c)
                    pygame.draw.circle(d, UI.GOUD if self.tip == (r, c) else (UI.ACCENT if hover else (120, 200, 150)), (x, y), 12 if hover else 8)
                    if hover:                           # laat zien hoeveel er omdraaien
                        n = len(omdraai(self.b, r, c, self.mij))
                        UI.tekst(d, "+%d" % n, 18, UI.GOUD, (x, y - 26), mid=True)
                elif (r, c) in mog and self.tip == (r, c):
                    pygame.draw.circle(d, UI.GOUD, (x, y), 12)
        # rechts
        px = BX + N * VAK + 50
        t = tel(self.b)
        for i, sp in enumerate((self.mij, -self.mij)):
            y = 110 + i * 100
            self.teken_schijf(d, px + 30, y + 30, sp, 0.8)
            UI.tekst(d, self.naam(sp), 28, UI.TEKST, (px + 76, y + 4))
            UI.tekst(d, "%d" % t[sp], 22, UI.GOUD, (px + 76, y + 40))
            UI.tekst(d, str(self.score[sp]), 30, UI.GOUD, (UI.W - 50, y + 4), rechts=True)
            if not self.klaar and self.beurt == sp:
                pygame.draw.rect(d, UI.ACCENT, (px - 12, y - 8, UI.W - px - 26, 84), 3, border_radius=12)
        y = 330
        if self.klaar:
            regels = [self.uitslag]
        elif self.beurt != self.mij:
            regels = [self.wacht_tekst()]
        else:
            regels = [T("jouw_beurt") if mog else T("pas_jij")]
        if self.melding:
            regels.append(self.melding)
        for regel in regels:
            for stuk in UI.Backgammon._knip(None, regel, 22, UI.W - px - 30):
                UI.tekst(d, stuk, 22, UI.GOUD if regel in (self.melding, self.uitslag) else UI.TEKST, (px, y))
                y += 30
            y += 8
        self.knoppen = []
        if self.klaar:
            self.knoppen.append(UI.Knop((px, 560, 300, 70), UI.T("nog"), self.nieuw_potje, UI.GROEN, 26))
        else:
            self.knoppen.append(UI.Knop((px, 560, 130, 70), UI.T("tip"), self.geef_tip, UI.GOUD, 26, aan=mijn_beurt and self.tip_mag()))
            self.knoppen.append(UI.Knop((px + 145, 560, 260, 70), "%s: %s" % (UI.T("hulp"), UI.T("aan") if self.app.hulp else UI.T("uitm")),
                                        self.app.wissel_hulp, UI.VAK, 22))
        self.knoppen.append(UI.Knop((px, 650, 190, 60), UI.T("menu"), self.app.naar_menu, UI.VAK, 24))
        self.knoppen.append(UI.Knop((px + 205, 650, 200, 60), UI.T("regels"), lambda: setattr(self.app, "toon_regels", True), UI.VAK, 22))
        for k in self.knoppen:
            k.teken(d, muis)
        UI.tekst(d, T("toetsen_rev"), 16, UI.ZACHT, (px, UI.H - 34), vet=False)

    def tip_mag(self):
        return True


# ------------------------------------------------------------------ online tegen elkaar
class OnlineReversi(Reversi):
    def __init__(self, app, adres, code, naam, token):
        self.lijn = None
        self.code = code
        self.ik = None
        self.ander = None
        self.verbonden = [False, False]
        self.status = UI.T("verbinden")
        self.fase = "wachten"
        self.n_zetten = 0
        self.potje = None
        self.eerste = 0
        self.einde_gezien = False
        self.stand = None
        self.herzien = False
        Reversi.__init__(self, app, 0)
        self.beurt = 0
        self.lijn = UI.online.Lijn(adres, code, {"t": "hallo", "spel": "rev", "naam": naam, "token": token}, pad="zet/kamer")

    def kleur_van(self, idx):
        return ZWART if idx == self.eerste else WIT

    def naam(self, sp):
        if self.ik is None:
            return UI.T("speler1" if sp == ZWART else "speler2")
        return UI.T("jij") if sp == self.mij else (self.ander or UI.T("tegenspeler"))

    def tip_mag(self):
        return False

    def nieuw_potje(self):
        if self.lijn is not None:
            self.lijn.stuur({"t": "nieuw"})
            self.app.geluid.speel("klik")
            return
        Reversi.nieuw_potje(self)

    def wacht_tekst(self):
        if self.fase == "wachten":
            return UI.T("wacht_ander") % self.code
        return UI.T("ander_beurt") % self.naam(self.beurt)

    def doe_zet(self, zet):
        if self.klaar or self.anim or self.beurt != self.mij or self.fase != "spel":
            return
        na = doe(self.b, zet, self.mij)
        einde = None
        if not zetten(na, ZWART) and not zetten(na, WIT):
            t = tel(na)
            einde = -1 if t[ZWART] == t[WIT] else (self.ik if t[self.mij] > t[-self.mij] else 1 - self.ik)
        z = {"pas": True} if zet is None else {"r": zet[0], "c": zet[1]}
        if self.lijn.stuur({"t": "zet", "z": z, "einde": einde}):
            self.n_zetten += 1
            Reversi.doe_zet(self, zet)
            self.herzien = True
        else:
            self.status = UI.T("geen_server")

    def pas(self):
        if self.beurt == self.mij:
            self.doe_zet(None)                     # alleen ik pas voor mezelf; de ander doet dat zelf

    def na_zet(self):
        pass                                       # de server zegt wanneer het klaar is

    def computer(self):
        pass

    def update(self):
        if self.anim:
            Reversi.update(self)
            return
        if self.lijn is not None:
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
            if not self.anim and self.stand and self.herzien:
                self.herzien = False
                self.pas_toe(self.stand)
        if self.fase == "spel" and not self.klaar and not self.anim:
            Reversi.update(self)                   # automatisch passen als ik niet kan

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
            return
        lijst = st.get("zetten") or []
        if st.get("potje") == self.potje and len(lijst) < self.n_zetten:
            return
        if st.get("potje") != self.potje:
            self.potje = st.get("potje")
            Reversi.nieuw_potje(self)
            self.mij = self.kleur_van(self.ik)
            self.n_zetten = 0
            self.einde_gezien = False
            for d in lijst[:-1] if len(lijst) > 1 else []:
                z = d.get("z") or {}
                sp = self.kleur_van(d["sp"])
                zet = None if z.get("pas") else (int(z["r"]), int(z["c"]))
                self.b = doe(self.b, zet, sp)
                self.beurt = -sp
                self.n_zetten += 1
        if self.anim:
            self.herzien = True
            return
        if len(lijst) > self.n_zetten:
            d = lijst[self.n_zetten]
            z = d.get("z") or {}
            sp = self.kleur_van(d["sp"])
            self.n_zetten += 1
            self.beurt = sp
            if z.get("pas"):
                self.melding = T("pas_ander") % self.naam(sp)
                self.beurt = -sp
            else:
                zet = (int(z["r"]), int(z["c"]))
                Reversi.doe_zet(self, zet)
            self.herzien = True
            return
        if self.fase == "einde":
            self.klaar = True
            w = st.get("winnaar")
            t = tel(self.b)
            if w == -1:
                self.uitslag = T("gelijk")
            else:
                ws = self.kleur_van(w)
                self.uitslag = T("uitslag") % (self.naam(ws), t[ws], t[-ws])
            if not self.einde_gezien:
                self.einde_gezien = True
                self.app.geluid.speel("win" if w == self.ik else ("klik" if w == -1 else "verlies"))
        else:
            self.klaar = False
            self.beurt = self.kleur_van(st["beurt"])

    def teken(self, d, muis):
        Reversi.teken(self, d, muis)
        px = BX + N * VAK + 50
        if self.status:
            UI.tekst(d, self.status, 20, UI.ROOD, (px, 520))
        elif self.ik is not None and self.ander and not self.verbonden[1 - self.ik]:
            UI.tekst(d, UI.T("ander_weg") % self.ander, 20, UI.GOUD, (px, 520))
        UI.tekst(d, UI.T("kamer") % self.code, 20, UI.ACCENT, (px, 60))
        if self.fase == "wachten":
            UI.tekst(d, self.code, 56, UI.GOUD, (px, 440))

    def stop(self):
        if self.lijn:
            self.lijn.stop()
