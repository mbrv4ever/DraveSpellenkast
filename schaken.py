# -*- coding: utf-8 -*-
"""DraveSpellenkast - Schaken, tegen de computer of online tegen elkaar.
Alle regels: rokeren, en passant, promotie, schaak, mat, pat en remise.
Copyright (C) 2026 Dravenlock (Roger & Claudio). GNU GPL v3.0."""
import random
import threading
import time

import pygame

UI = None          # wordt door main.py gezet

VAK = 88
BX, BY = 60, 62
WIT, ZWART = 1, -1
LICHT_VAK = (226, 214, 236)
DONKER_VAK = (122, 104, 168)
WAARDE = {"p": 100, "n": 320, "b": 330, "r": 500, "q": 900, "k": 0}
TEKEN = {"k": "♚", "q": "♛", "r": "♜", "b": "♝", "n": "♞", "p": "♟"}
PAARD = (-17, -15, -10, -6, 6, 10, 15, 17)
KONING = (-9, -8, -7, -1, 1, 7, 8, 9)
LOPER = (-9, -7, 7, 9)
TOREN = (-8, -1, 1, 8)

TX = {
    "schaak": ("Schaken", "Chess"),
    "jouw_beurt": ("Jouw beurt: klik een stuk, dan waar het heen moet", "Your turn: click a piece, then where it goes"),
    "comp_denkt": ("De computer denkt...", "The computer is thinking..."),
    "schaak_staat": ("Schaak! Je koning staat aangevallen.", "Check! Your king is under attack."),
    "mat": ("Schaakmat! %s wint.", "Checkmate! %s wins."),
    "pat": ("Pat! Niemand kan zetten: remise.", "Stalemate! A draw."),
    "remise_50": ("Remise: 50 zetten zonder slaan of pionzet.", "Draw: 50 moves without a capture or pawn move."),
    "remise_3": ("Remise: dezelfde stand voor de derde keer.", "Draw: the same position for the third time."),
    "remise_mat": ("Remise: niemand kan nog mat zetten.", "Draw: nobody can checkmate any more."),
    "promo": ("Waar wordt je pion in? Klik er één.", "What does your pawn become? Click one."),
    "tip_kop": ("Tip: het gouden stuk naar het gouden vakje.", "Tip: the gold piece to the gold square."),
    "geslagen": ("Geslagen:", "Captured:"),
    "toetsen_schaak": ("Klik een stuk en dan een vakje  ·  T = tip  ·  Backspace = ander stuk  ·  Esc = menu",
                       "Click a piece, then a square  ·  T = tip  ·  Backspace = other piece  ·  Esc = menu"),
    "opgeven": ("Opgeven", "Resign"),
    "opgegeven": ("%s gaf op. %s wint.", "%s resigned. %s wins."),
}


def T(k):
    if k in TX:
        v = TX[k]
        return v[0] if UI.TAAL == "nl" else v[1]
    return UI.T(k)


# ------------------------------------------------------------------ stukken-tabellen (voor de computer)
PST = {
    "p": [0, 0, 0, 0, 0, 0, 0, 0, 50, 50, 50, 50, 50, 50, 50, 50, 10, 10, 20, 30, 30, 20, 10, 10, 5, 5, 10, 25, 25, 10, 5, 5,
          0, 0, 0, 20, 20, 0, 0, 0, 5, -5, -10, 0, 0, -10, -5, 5, 5, 10, 10, -20, -20, 10, 10, 5, 0, 0, 0, 0, 0, 0, 0, 0],
    "n": [-50, -40, -30, -30, -30, -30, -40, -50, -40, -20, 0, 0, 0, 0, -20, -40, -30, 0, 10, 15, 15, 10, 0, -30, -30, 5, 15, 20, 20, 15, 5, -30,
          -30, 0, 15, 20, 20, 15, 0, -30, -30, 5, 10, 15, 15, 10, 5, -30, -40, -20, 0, 5, 5, 0, -20, -40, -50, -40, -30, -30, -30, -30, -40, -50],
    "b": [-20, -10, -10, -10, -10, -10, -10, -20, -10, 0, 0, 0, 0, 0, 0, -10, -10, 0, 5, 10, 10, 5, 0, -10, -10, 5, 5, 10, 10, 5, 5, -10,
          -10, 0, 10, 10, 10, 10, 0, -10, -10, 10, 10, 10, 10, 10, 10, -10, -10, 5, 0, 0, 0, 0, 5, -10, -20, -10, -10, -10, -10, -10, -10, -20],
    "r": [0, 0, 0, 0, 0, 0, 0, 0, 5, 10, 10, 10, 10, 10, 10, 5, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5,
          -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 5, 5, 0, 0, 0],
    "q": [-20, -10, -10, -5, -5, -10, -10, -20, -10, 0, 0, 0, 0, 0, 0, -10, -10, 0, 5, 5, 5, 5, 0, -10, -5, 0, 5, 5, 5, 5, 0, -5,
          0, 0, 5, 5, 5, 5, 0, -5, -10, 5, 5, 5, 5, 5, 0, -10, -10, 0, 5, 0, 0, 0, 0, -10, -20, -10, -10, -5, -5, -10, -10, -20],
    "k": [-30, -40, -40, -50, -50, -40, -40, -30, -30, -40, -40, -50, -50, -40, -40, -30, -30, -40, -40, -50, -50, -40, -40, -30,
          -30, -40, -40, -50, -50, -40, -40, -30, -20, -30, -30, -40, -40, -30, -30, -20, -10, -20, -20, -20, -20, -20, -20, -10,
          20, 20, 0, 0, 0, 0, 20, 20, 20, 30, 10, 0, 0, 10, 30, 20],
}


# ------------------------------------------------------------------ spelregels
def kleur(st):
    if st == ".":
        return 0
    return WIT if st.isupper() else ZWART


class Stand:
    """Het bord (64 vakjes, 0 = a8 linksboven), wie aan zet is, rokade, en passant en de 50-zetten-teller."""

    def __init__(self):
        self.b = list("rnbqkbnr" + "pppppppp" + "." * 32 + "PPPPPPPP" + "RNBQKBNR")
        self.zet = WIT
        self.rok = "KQkq"
        self.ep = None
        self.halve = 0
        self.historie = [self.sleutel()]

    def kopie(self):
        n = Stand.__new__(Stand)
        n.b = self.b[:]
        n.zet, n.rok, n.ep, n.halve = self.zet, self.rok, self.ep, self.halve
        n.historie = self.historie[:]
        return n

    def sleutel(self):
        return "".join(self.b) + str(self.zet) + self.rok + str(self.ep)

    def koning(self, sp):
        return self.b.index("K" if sp == WIT else "k")


def aangevallen(b, vak, door):
    """Wordt vak aangevallen door kleur 'door'?"""
    r, c = divmod(vak, 8)
    # pionnen
    pr = r + 1 if door == WIT else r - 1
    pion = "P" if door == WIT else "p"
    for dc in (-1, 1):
        if 0 <= pr < 8 and 0 <= c + dc < 8 and b[pr * 8 + c + dc] == pion:
            return True
    paard, koning = ("N", "K") if door == WIT else ("n", "k")
    for d in PAARD:
        v = vak + d
        if 0 <= v < 64 and abs((v % 8) - c) <= 2 and b[v] == paard:
            return True
    for d in KONING:
        v = vak + d
        if 0 <= v < 64 and abs((v % 8) - c) <= 1 and b[v] == koning:
            return True
    rechte = ("R", "Q") if door == WIT else ("r", "q")
    schuin = ("B", "Q") if door == WIT else ("b", "q")
    for ds, stukken in ((TOREN, rechte), (LOPER, schuin)):
        for d in ds:
            v, vorige = vak, c
            while True:
                v += d
                if not (0 <= v < 64) or abs((v % 8) - vorige) > 1:
                    break
                vorige = v % 8
                if b[v] != ".":
                    if b[v] in stukken:
                        return True
                    break
    return False


def schaak(s, sp):
    return aangevallen(s.b, s.koning(sp), -sp)


def pseudo(s):
    """Alle zetten zonder te kijken of je koning schaak komt te staan: (van, naar, promo)."""
    b, sp = s.b, s.zet
    uit = []
    for v in range(64):
        st = b[v]
        if st == "." or kleur(st) != sp:
            continue
        r, c = divmod(v, 8)
        t = st.lower()
        if t == "p":
            stap = -8 if sp == WIT else 8
            start = 6 if sp == WIT else 1
            laatst = 0 if sp == WIT else 7
            n = v + stap
            if 0 <= n < 64 and b[n] == ".":
                if n // 8 == laatst:
                    uit += [(v, n, p) for p in "qrbn"]
                else:
                    uit.append((v, n, ""))
                    if r == start and b[n + stap] == ".":
                        uit.append((v, n + stap, ""))
            for dc in (-1, 1):
                if 0 <= c + dc < 8:
                    n = v + stap + dc
                    if 0 <= n < 64 and (kleur(b[n]) == -sp or n == s.ep):
                        if n // 8 == laatst:
                            uit += [(v, n, p) for p in "qrbn"]
                        else:
                            uit.append((v, n, ""))
        elif t == "n":
            for d in PAARD:
                n = v + d
                if 0 <= n < 64 and abs((n % 8) - c) <= 2 and kleur(b[n]) != sp:
                    uit.append((v, n, ""))
        elif t == "k":
            for d in KONING:
                n = v + d
                if 0 <= n < 64 and abs((n % 8) - c) <= 1 and kleur(b[n]) != sp:
                    uit.append((v, n, ""))
            # rokeren
            if sp == WIT and v == 60:
                if "K" in s.rok and b[61] == b[62] == "." and b[63] == "R" and not any(aangevallen(b, x, ZWART) for x in (60, 61, 62)):
                    uit.append((60, 62, ""))
                if "Q" in s.rok and b[59] == b[58] == b[57] == "." and b[56] == "R" and not any(aangevallen(b, x, ZWART) for x in (60, 59, 58)):
                    uit.append((60, 58, ""))
            if sp == ZWART and v == 4:
                if "k" in s.rok and b[5] == b[6] == "." and b[7] == "r" and not any(aangevallen(b, x, WIT) for x in (4, 5, 6)):
                    uit.append((4, 6, ""))
                if "q" in s.rok and b[3] == b[2] == b[1] == "." and b[0] == "r" and not any(aangevallen(b, x, WIT) for x in (4, 3, 2)):
                    uit.append((4, 2, ""))
        else:
            richtingen = LOPER if t == "b" else TOREN if t == "r" else LOPER + TOREN
            for d in richtingen:
                n, vorige = v, c
                while True:
                    n += d
                    if not (0 <= n < 64) or abs((n % 8) - vorige) > 1:
                        break
                    vorige = n % 8
                    if b[n] == ".":
                        uit.append((v, n, ""))
                    else:
                        if kleur(b[n]) == -sp:
                            uit.append((v, n, ""))
                        break
    return uit


def doe(s, z):
    """Voer zet z uit op een kopie van stand s."""
    van, naar, promo = z
    n = s.kopie()
    b = n.b
    st = b[van]
    t = st.lower()
    sp = s.zet
    slag = b[naar] != "."
    if t == "p" and naar == s.ep:                     # en passant: de pion naast je verdwijnt
        b[naar + (8 if sp == WIT else -8)] = "."
        slag = True
    b[naar] = st
    b[van] = "."
    if promo:
        b[naar] = promo.upper() if sp == WIT else promo
    if t == "k" and abs(naar - van) == 2:             # rokeren: de toren springt over
        if naar == 62:
            b[61], b[63] = "R", "."
        elif naar == 58:
            b[59], b[56] = "R", "."
        elif naar == 6:
            b[5], b[7] = "r", "."
        elif naar == 2:
            b[3], b[0] = "r", "."
    rok = n.rok
    for vak, weg in ((60, "KQ"), (4, "kq"), (63, "K"), (56, "Q"), (7, "k"), (0, "q")):
        if van == vak or naar == vak:
            for x in weg:
                rok = rok.replace(x, "")
    n.rok = rok
    n.ep = (van + naar) // 2 if t == "p" and abs(naar - van) == 16 else None
    n.halve = 0 if (t == "p" or slag) else s.halve + 1
    n.zet = -sp
    n.historie = s.historie + [n.sleutel()]
    return n


def zetten(s):
    """Alle geldige zetten."""
    uit = []
    for z in pseudo(s):
        n = doe(s, z)
        if not aangevallen(n.b, n.koning(s.zet), -s.zet):
            uit.append(z)
    return uit


def te_weinig(b):
    stukken = [x for x in b if x not in ".Kk"]
    if not stukken:
        return True
    return len(stukken) == 1 and stukken[0].lower() in "nb"


def uitslag(s, lijst=None):
    """None = verder spelen. Anders ('mat', winnaar) of ('remise', reden)."""
    if lijst is None:
        lijst = zetten(s)
    if not lijst:
        return ("mat", -s.zet) if schaak(s, s.zet) else ("remise", "pat")
    if s.halve >= 100:
        return ("remise", "remise_50")
    if s.historie.count(s.historie[-1]) >= 3:
        return ("remise", "remise_3")
    if te_weinig(s.b):
        return ("remise", "remise_mat")
    return None


# ------------------------------------------------------------------ de computer
def waarde(s):
    """Hoe goed staat wit ervoor (in honderdsten van een pion)."""
    w = 0
    for v, st in enumerate(s.b):
        if st == ".":
            continue
        t = st.lower()
        if st.isupper():
            w += WAARDE[t] + PST[t][v]
        else:
            w -= WAARDE[t] + PST[t][(7 - v // 8) * 8 + v % 8]
    return w


class TeLaat(Exception):
    pass


GRENS = [None]


def orden(s, lijst):
    b = s.b
    def k(z):
        if b[z[1]] != ".":
            return -(10 * WAARDE[b[z[1]].lower()] - WAARDE[b[z[0]].lower()]) - 1000
        return -(900 if z[2] == "q" else 0)
    return sorted(lijst, key=k)


def rustig(s, alfa, beta, diepte=0):
    """Na de gewone zoekdiepte nog even slagen doorrekenen (zodat hij geen dame weggeeft)."""
    staand = waarde(s) * s.zet
    if staand >= beta:
        return beta
    alfa = max(alfa, staand)
    if diepte > 4:
        return alfa
    for z in orden(s, [z for z in pseudo(s) if s.b[z[1]] != "."]):
        n = doe(s, z)
        if aangevallen(n.b, n.koning(s.zet), -s.zet):
            continue
        v = -rustig(n, -beta, -alfa, diepte + 1)
        if v >= beta:
            return beta
        alfa = max(alfa, v)
    return alfa


def negamax(s, diepte, alfa, beta, ply=0):
    if GRENS[0] and time.time() > GRENS[0]:
        raise TeLaat()
    lijst = zetten(s)
    u = uitslag(s, lijst)
    if u:
        return (-100000 + ply) if u[0] == "mat" else 0, None
    if diepte <= 0:
        return rustig(s, alfa, beta), None
    beste, beste_z = -10 ** 9, None
    for z in orden(s, lijst):
        v, _ = negamax(doe(s, z), diepte - 1, -beta, -alfa, ply + 1)
        v = -v
        if v > beste:
            beste, beste_z = v, z
        alfa = max(alfa, v)
        if alfa >= beta:
            break
    return beste, beste_z


def kies_zet(s, niveau):
    lijst = zetten(s)
    if not lijst:
        return None
    if niveau == 1:                                   # makkelijk: pakt wat hij ziet, maar kijkt niet vooruit
        if random.random() < 0.35:
            return random.choice(lijst)
        best = max(lijst, key=lambda z: (WAARDE[s.b[z[1]].lower()] if s.b[z[1]] != "." else 0) + random.random() * 60)
        return best
    z_best = None
    GRENS[0] = time.time() + (1.5 if niveau == 2 else 3.5)
    try:
        for diepte in range(1, (3 if niveau == 2 else 6) + 1):
            _, z = negamax(s, diepte, -10 ** 9, 10 ** 9)
            if z:
                z_best = z
    except TeLaat:
        pass
    finally:
        GRENS[0] = None
    if niveau == 2 and random.random() < 0.08:
        z_best = random.choice(lijst)
    return z_best or random.choice(lijst)


def zet_naar_lijst(z):
    return {"van": z[0], "naar": z[1], "promo": z[2]}


def zet_van_lijst(d):
    return (int(d["van"]), int(d["naar"]), str(d.get("promo") or "")[:1])


# ------------------------------------------------------------------ het spel
class Schaken:
    def __init__(self, app, niveau):
        self.app = app
        self.niveau = niveau
        self.mij = WIT
        self.knoppen = []
        self.score = {WIT: 0, ZWART: 0}
        self.volgende_kleur = WIT
        self.nieuw_potje()

    def naam(self, sp):
        return UI.T("jij") if sp == self.mij else UI.T("computer")

    def nieuw_potje(self, wissel=True):
        if wissel and self.niveau:                     # tegen de computer: om de beurt wit
            self.mij = self.volgende_kleur
            self.volgende_kleur = -self.volgende_kleur
        self.s = Stand()
        self.lijst = zetten(self.s)
        self.klaar = False
        self.uitslag = ""
        self.kies = None
        self.anim = None
        self.tip = None
        self.melding = ""
        self.denk = None
        self.laatste = None
        self.promo_wacht = None                        # (van, naar) als je nog moet kiezen waar je pion in wordt
        self.weg = {WIT: [], ZWART: []}                # geslagen stukken (per kleur die ze sloeg)

    @property
    def beurt(self):
        return self.s.zet

    # ---------- zetten
    def start_anim(self, z):
        if self.s.b[z[0]] == ".":
            UI.log_fout("schaken: zet vanaf een leeg vakje %r" % (z,))
            return
        self.anim = {"zet": z, "t": 0.0, "stuk": self.s.b[z[0]]}
        self.kies = None
        self.tip = None
        self.app.geluid.speel("klik")

    def doe_zet(self, z):
        if self.klaar or self.anim or z is None:
            return
        self.melding = ""
        self.start_anim(z)

    def klaar_met_zet(self):
        z = self.anim["zet"]
        self.anim = None
        s = self.s
        sp = s.zet
        geslagen = s.b[z[1]]
        if geslagen == "." and s.b[z[0]].lower() == "p" and z[1] == s.ep:
            geslagen = "p" if sp == WIT else "P"
        if geslagen != ".":
            self.weg[sp].append(geslagen)
        self.s = doe(s, z)
        self.laatste = z
        self.lijst = zetten(self.s)
        self.app.geluid.speel("goed" if geslagen != "." else "zet")
        self.controleer_einde()

    def controleer_einde(self):
        u = uitslag(self.s, self.lijst)
        if not u:
            if schaak(self.s, self.s.zet):
                self.app.geluid.speel("fout")
            return
        self.klaar = True
        if u[0] == "mat":
            self.score[u[1]] += 1
            self.uitslag = T("mat") % self.naam(u[1])
            self.app.geluid.speel("win" if u[1] == self.mij else "verlies")
        else:
            self.uitslag = T(u[1]) if u[1] != "pat" else T("pat")

    def update(self):
        if self.anim:
            self.anim["t"] += 0.09
            if self.anim["t"] >= 1:
                self.klaar_met_zet()
            return
        if self.klaar or self.beurt == self.mij:
            return
        if self.denk is None:
            self.denk = {"z": None, "klaar": False, "start": time.time()}
            stand = self.s.kopie()
            def denk(d=self.denk, stand=stand):
                d["z"] = kies_zet(stand, self.niveau)
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
        GRENS[0] = time.time() + 1.5
        z = None
        try:
            for d in (1, 2, 3):
                _, zz = negamax(self.s, d, -10 ** 9, 10 ** 9)
                z = zz or z
        except TeLaat:
            pass
        finally:
            GRENS[0] = None
        if z:
            self.tip = z
            self.kies = None
            self.melding = T("tip_kop")
            self.app.geluid.speel("goed")

    def in_gevaar(self):
        """Eigen stukken die geslagen kunnen worden en niet (goed genoeg) gedekt zijn."""
        uit = []
        b = self.s.b
        for v, st in enumerate(b):
            if kleur(st) == self.mij and st.lower() != "k" and aangevallen(b, v, -self.mij) and not aangevallen(b, v, self.mij):
                uit.append(v)
        return uit

    # ---------- invoer
    def vak_op(self, pos):
        x, y = pos
        if not (BX <= x < BX + 8 * VAK and BY <= y < BY + 8 * VAK):
            return None
        c, r = (x - BX) // VAK, (y - BY) // VAK
        if self.mij == ZWART:                          # zwart speelt van onderen: bord omdraaien
            r, c = 7 - r, 7 - c
        return int(r * 8 + c)

    def scherm_xy(self, v):
        r, c = divmod(v, 8)
        if self.mij == ZWART:
            r, c = 7 - r, 7 - c
        return BX + c * VAK + VAK // 2, BY + r * VAK + VAK // 2

    def klik(self, pos):
        if self.promo_wacht:
            for k in self.knoppen:
                if k.klik(pos):
                    return
            return
        if self.klaar or self.beurt != self.mij or self.anim:
            return
        v = self.vak_op(pos)
        if v is None:
            return
        if kleur(self.s.b[v]) == self.mij:
            self.kies = v
            self.app.geluid.speel("klik")
            return
        if self.kies is not None:
            mog = [z for z in self.lijst if z[0] == self.kies and z[1] == v]
            if len(mog) > 1:                           # promotie: laat kiezen
                self.promo_wacht = (self.kies, v)
                self.melding = T("promo")
                return
            if mog:
                self.doe_zet(mog[0])
                return
            self.app.geluid.speel("fout")

    def kies_promo(self, p):
        van, naar = self.promo_wacht
        self.promo_wacht = None
        self.doe_zet((van, naar, p))

    def toets(self, e):
        if e.key == pygame.K_ESCAPE:
            if self.promo_wacht:
                self.promo_wacht = None
                self.melding = ""
            else:
                self.app.naar_menu()
        elif self.klaar and e.key in (pygame.K_SPACE, pygame.K_RETURN):
            self.nieuw_potje()
        elif e.key == pygame.K_t:
            self.geef_tip()
        elif e.key == pygame.K_BACKSPACE:
            self.kies = None

    def opgeven(self):
        if self.klaar:
            return
        self.klaar = True
        self.score[-self.mij] += 1
        self.uitslag = T("opgegeven") % (self.naam(self.mij), self.naam(-self.mij))
        self.app.geluid.speel("verlies")

    # ---------- tekenen
    def teken_stuk(self, d, x, y, st, maat=None, rand=None):
        maat = maat or int(VAK * 0.82)
        plaatje = stuk_plaatje(st, maat)
        d.blit(plaatje, plaatje.get_rect(center=(int(x), int(y))))
        if rand:
            pygame.draw.circle(d, rand, (int(x), int(y)), VAK // 2 - 4, 4)

    def teken(self, d, muis):
        d.fill(UI.ACHTER)
        UI.tekst(d, T("schaak"), 40, UI.ACCENT, (BX, 8))
        bord = pygame.Rect(BX - 10, BY - 10, 8 * VAK + 20, 8 * VAK + 20)
        pygame.draw.rect(d, (60, 48, 90), bord, border_radius=14)
        pygame.draw.rect(d, UI.RAND, bord, 4, border_radius=14)
        s = self.s
        mijn_beurt = not self.klaar and self.beurt == self.mij and not self.anim and not self.promo_wacht
        gevaar = set(self.in_gevaar()) if (self.app.hulp and mijn_beurt) else set()
        koning_schaak = s.koning(s.zet) if schaak(s, s.zet) else None
        for v in range(64):
            x, y = self.scherm_xy(v)
            r, c = divmod(v, 8)
            kl = LICHT_VAK if (r + c) % 2 == 0 else DONKER_VAK
            if self.laatste and v in self.laatste[:2] and not self.anim:
                kl = (214, 196, 120) if (r + c) % 2 == 0 else (170, 150, 90)
            if v == koning_schaak:
                kl = (220, 90, 100)
            pygame.draw.rect(d, kl, (x - VAK // 2, y - VAK // 2, VAK, VAK))
        # letters en cijfers langs het bord
        for i in range(8):
            c = i if self.mij == WIT else 7 - i
            UI.tekst(d, "abcdefgh"[c], 16, UI.ZACHT, (BX + i * VAK + VAK // 2, BY + 8 * VAK + 14), mid=True, vet=False)
            r = i if self.mij == WIT else 7 - i
            UI.tekst(d, str(8 - r), 16, UI.ZACHT, (BX - 24, BY + i * VAK + VAK // 2), mid=True, vet=False)
        anim_van = self.anim["zet"][0] if self.anim else None
        for v, st in enumerate(s.b):
            if st == "." or v == anim_van:
                continue
            x, y = self.scherm_xy(v)
            rand = None
            if v == self.kies:
                rand = UI.ACCENT
            elif self.tip and v == self.tip[0]:
                rand = UI.GOUD
            elif v in gevaar:
                rand = UI.ROOD
            self.teken_stuk(d, x, y, st, rand=rand)
        if self.kies is not None and mijn_beurt:
            for z in self.lijst:
                if z[0] == self.kies:
                    x, y = self.scherm_xy(z[1])
                    if s.b[z[1]] != ".":
                        pygame.draw.circle(d, UI.ACCENT, (x, y), VAK // 2 - 4, 5)
                    else:
                        pygame.draw.circle(d, UI.ACCENT, (x, y), 13)
        if self.tip and mijn_beurt:
            x, y = self.scherm_xy(self.tip[1])
            pygame.draw.circle(d, UI.GOUD, (x, y), 15)
        if self.anim:
            z, t = self.anim["zet"], self.anim["t"]
            x1, y1 = self.scherm_xy(z[0])
            x2, y2 = self.scherm_xy(z[1])
            f = t * t * (3 - 2 * t)
            self.teken_stuk(d, x1 + (x2 - x1) * f, y1 + (y2 - y1) * f, self.anim["stuk"])
        # rechts
        px = BX + 8 * VAK + 50
        for i, sp in enumerate((-self.mij, self.mij)):
            y = 100 + i * 110
            self.teken_stuk(d, px + 28, y + 30, "K" if sp == WIT else "k", maat=52)
            UI.tekst(d, self.naam(sp), 28, UI.TEKST, (px + 70, y + 2))
            UI.tekst(d, str(self.score[sp]), 30, UI.GOUD, (UI.W - 50, y + 2), rechts=True)
            for j, g in enumerate(sorted(self.weg[sp], key=lambda q: -WAARDE[q.lower()])[:15]):
                self.teken_stuk(d, px + 82 + j * 26, y + 58, g, maat=28)
            if not self.klaar and self.beurt == sp:
                pygame.draw.rect(d, UI.ACCENT, (px - 12, y - 8, UI.W - px - 26, 92), 3, border_radius=12)
        y = 330
        if self.klaar:
            regels = [self.uitslag]
        elif self.beurt != self.mij:
            regels = [self.wacht_tekst()]
        else:
            regels = [T("jouw_beurt")]
            if koning_schaak is not None:
                regels.append(T("schaak_staat"))
        if self.melding:
            regels.append(self.melding)
        for regel in regels:
            for stuk in UI.Backgammon._knip(None, regel, 22, UI.W - px - 30):
                rood = regel == T("schaak_staat")
                UI.tekst(d, stuk, 22, UI.ROOD if rood else (UI.GOUD if regel in (self.melding, self.uitslag) else UI.TEKST), (px, y))
                y += 30
            y += 8
        self.knoppen = []
        if self.promo_wacht:
            for i, p in enumerate("qrbn"):
                r = pygame.Rect(px + i * 98, 470, 88, 88)
                k = UI.Knop(r, "", lambda p=p: self.kies_promo(p), UI.VAK)
                self.knoppen.append(k)
        if self.klaar:
            self.knoppen.append(UI.Knop((px, 580, 300, 70), UI.T("nog"), self.nieuw_potje, UI.GROEN, 26))
        else:
            self.knoppen.append(UI.Knop((px, 580, 120, 64), UI.T("tip"), self.geef_tip, UI.GOUD, 24, aan=mijn_beurt))
            self.knoppen.append(UI.Knop((px + 132, 580, 150, 64), "%s: %s" % (UI.T("hulp"), UI.T("aan") if self.app.hulp else UI.T("uitm")),
                                        self.app.wissel_hulp, UI.VAK, 20))
            self.knoppen.append(UI.Knop((px + 294, 580, 120, 64), T("opgeven"), self.opgeven, UI.VAK, 20))
        self.knoppen.append(UI.Knop((px, 660, 190, 60), UI.T("menu"), self.app.naar_menu, UI.VAK, 24))
        self.knoppen.append(UI.Knop((px + 205, 660, 200, 60), UI.T("regels"), lambda: setattr(self.app, "toon_regels", True), UI.VAK, 22))
        for k in self.knoppen:
            k.teken(d, muis)
        if self.promo_wacht:
            for i, p in enumerate("qrbn"):
                self.teken_stuk(d, px + i * 98 + 44, 514, p.upper() if self.mij == WIT else p, maat=70)
        UI.tekst(d, T("toetsen_schaak"), 15, UI.ZACHT, (px, UI.H - 34), vet=False)


_FONTS = {}
_PLAATJES = {}
OPEN = {"k": "\u2654", "q": "\u2655", "r": "\u2656", "b": "\u2657", "n": "\u2658", "p": "\u2659"}


VOET = [(18, 92), (82, 92), (80, 84), (72, 80), (28, 80), (20, 84)]


def _vormen(t):
    """De vormen van een stuk in een vak van 100x100: lijst van ('poly', punten) of ('rond', (x, y, r))."""
    if t == "p":
        return [("poly", VOET), ("poly", [(34, 80), (66, 80), (60, 56), (40, 56)]),
                ("poly", [(36, 58), (64, 58), (58, 48), (42, 48)]), ("rond", (50, 36, 14))]
    if t == "r":
        return [("poly", VOET), ("poly", [(32, 80), (68, 80), (64, 42), (36, 42)]),
                ("poly", [(26, 44), (74, 44), (74, 18), (64, 18), (64, 28), (56, 28), (56, 18), (44, 18), (44, 28),
                          (36, 28), (36, 18), (26, 18)])]
    if t == "b":
        return [("poly", VOET), ("poly", [(36, 80), (64, 80), (58, 62), (42, 62)]),
                ("poly", [(34, 66), (66, 66), (66, 60), (34, 60)]),
                ("poly", [(50, 14), (64, 30), (66, 44), (58, 60), (42, 60), (34, 44), (36, 30)]), ("rond", (50, 12, 6))]
    if t == "n":
        return [("poly", VOET), ("poly", [(30, 80), (72, 80), (74, 58), (70, 34), (58, 18), (54, 10), (48, 18), (38, 22),
                                         (24, 40), (18, 54), (24, 60), (34, 54), (44, 50), (34, 66)])]
    if t == "q":
        return [("poly", VOET), ("poly", [(32, 80), (68, 80), (64, 56), (36, 56)]),
                ("poly", [(30, 58), (70, 58), (80, 22), (64, 42), (58, 18), (50, 40), (42, 18), (36, 42), (20, 22)]),
                ("rond", (20, 20, 6)), ("rond", (42, 16, 6)), ("rond", (58, 16, 6)), ("rond", (80, 20, 6))]
    # koning
    return [("poly", VOET), ("poly", [(32, 80), (68, 80), (64, 56), (36, 56)]),
            ("poly", [(28, 58), (72, 58), (76, 40), (64, 30), (50, 36), (36, 30), (24, 40)]),
            ("poly", [(46, 32), (54, 32), (54, 22), (62, 22), (62, 15), (54, 15), (54, 6), (46, 6), (46, 15), (38, 15), (38, 22), (46, 22)])]


def stuk_plaatje(st, maat):
    """Een zelf getekend schaakstuk (geen lettertype nodig): wit of donker, met een duidelijke rand."""
    sleutel = (st, maat)
    if sleutel in _PLAATJES:
        return _PLAATJES[sleutel]
    t = st.lower()
    wit = st.isupper()
    vul = (250, 246, 236) if wit else (52, 40, 76)
    rand_kl = (36, 28, 52) if wit else (214, 204, 240)
    k = 4                                               # eerst groot tekenen, dan netjes verkleinen
    n = maat * k
    groot = pygame.Surface((n, n), pygame.SRCALPHA)
    sch = n / 100.0
    dik = max(2, int(3.2 * sch))
    vormen = _vormen(t)
    for laag in (0, 1):                                 # eerst alle randen, dan alle vullingen
        for soort, data in vormen:
            if soort == "poly":
                pts = [(x * sch, y * sch) for x, y in data]
                if laag == 0:
                    pygame.draw.polygon(groot, rand_kl, pts, 0)
                    pygame.draw.polygon(groot, rand_kl, pts, dik * 2)
                    for p in pts:
                        pygame.draw.circle(groot, rand_kl, (int(p[0]), int(p[1])), dik)
                else:
                    pygame.draw.polygon(groot, vul, pts, 0)
            else:
                x, y, r = data
                if laag == 0:
                    pygame.draw.circle(groot, rand_kl, (int(x * sch), int(y * sch)), int(r * sch) + dik)
                else:
                    pygame.draw.circle(groot, vul, (int(x * sch), int(y * sch)), int(r * sch))
    # lijntjes tussen de delen, zodat je de vorm goed ziet
    for soort, data in vormen[1:]:
        if soort == "poly":
            pts = [(x * sch, y * sch) for x, y in data]
            pygame.draw.polygon(groot, rand_kl, pts, max(1, dik // 2))
    if t == "n":                                        # oog en manen van het paard
        pygame.draw.circle(groot, rand_kl, (int(44 * sch), int(30 * sch)), int(3.5 * sch))
        pygame.draw.line(groot, rand_kl, (int(60 * sch), int(26 * sch)), (int(68 * sch), int(56 * sch)), max(1, dik // 2))
    if t == "b":                                        # sneetje in de mijter
        pygame.draw.line(groot, rand_kl, (int(54 * sch), int(30 * sch)), (int(46 * sch), int(42 * sch)), dik)
    uit = pygame.transform.smoothscale(groot, (maat, maat))
    _PLAATJES[sleutel] = uit
    return uit


def stuk_font(px):
    if px not in _FONTS:
        _FONTS[px] = pygame.font.SysFont("segoeuisymbol,dejavusans,arialunicodems,freeserif", px)
    return _FONTS[px]


# ------------------------------------------------------------------ online tegen elkaar
class OnlineSchaken(Schaken):
    """Schaken op twee pc's. De server geeft de zetten door; beide pc's rekenen met dezelfde regels."""

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
        self.herzien = False
        self.stand = None
        Schaken.__init__(self, app, 0)
        self.lijn = UI.online.Lijn(adres, code, {"t": "hallo", "spel": "schaak", "naam": naam, "token": token}, pad="zet/kamer")

    def kleur_van(self, idx):
        return WIT if idx == self.eerste else ZWART

    def naam(self, sp):
        if self.ik is None:
            return UI.T("speler1" if sp == WIT else "speler2")
        return UI.T("jij") if sp == self.mij else (self.ander or UI.T("tegenspeler"))

    def nieuw_potje(self, wissel=False):
        if self.lijn is not None:
            self.lijn.stuur({"t": "nieuw"})
            self.app.geluid.speel("klik")
            return
        Schaken.nieuw_potje(self, wissel=False)

    def wacht_tekst(self):
        if self.fase == "wachten":
            return UI.T("wacht_ander") % self.code
        return UI.T("ander_beurt") % self.naam(self.beurt)

    def doe_zet(self, z):
        if self.klaar or self.anim or z is None or self.beurt != self.mij or self.fase != "spel":
            return
        n = doe(self.s, z)
        u = uitslag(n)
        einde = None
        if u:
            einde = self.ik if u[0] == "mat" else -1
        if self.lijn.stuur({"t": "zet", "z": zet_naar_lijst(z), "einde": einde}):
            self.melding = ""
            self.n_zetten += 1
            self.start_anim(z)
            self.herzien = True
        else:
            self.status = UI.T("geen_server")

    def opgeven(self):
        if self.klaar or self.fase != "spel":
            return
        self.lijn.stuur({"t": "opgeven"})

    def controleer_einde(self):
        if not uitslag(self.s, self.lijst) and schaak(self.s, self.s.zet):
            self.app.geluid.speel("fout")

    def update(self):
        if self.anim:
            Schaken.update(self)
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
        if not self.anim and self.stand and self.herzien:
            self.herzien = False
            self.pas_toe(self.stand)

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
            return                                     # oud bericht: overslaan
        if st.get("potje") != self.potje or (self.n_zetten == 0 and len(lijst) > 1):
            self.potje = st.get("potje")
            Schaken.nieuw_potje(self, wissel=False)
            self.n_zetten = 0
            for d in lijst[:-1]:
                z = zet_van_lijst(d["z"])
                if self.s.b[z[1]] != ".":
                    self.weg[self.s.zet].append(self.s.b[z[1]])
                self.s = doe(self.s, z)
                self.laatste = z
                self.n_zetten += 1
            self.lijst = zetten(self.s)
            self.einde_gezien = False
        if self.anim:
            self.herzien = True
            return
        if len(lijst) > self.n_zetten:
            d = lijst[self.n_zetten]
            z = zet_van_lijst(d["z"])
            if z not in self.lijst:
                UI.log_fout("schaken online: onbekende zet %r" % (d,))
            self.n_zetten += 1
            self.start_anim(z)
            self.herzien = True
            return
        if st["fase"] == "einde":
            self.klaar = True
            w = st.get("winnaar")
            if st.get("reden") == "opgegeven":
                self.uitslag = T("opgegeven") % (self.naam(self.kleur_van(1 - w)), self.naam(self.kleur_van(w)))
            elif w == -1:
                u = uitslag(self.s, self.lijst)
                self.uitslag = T(u[1]) if u and u[0] == "remise" else T("pat")
            else:
                self.uitslag = T("mat") % self.naam(self.kleur_van(w))
            if not self.einde_gezien:
                self.einde_gezien = True
                self.app.geluid.speel("win" if w == self.ik else ("klik" if w == -1 else "verlies"))
        else:
            self.klaar = False

    def teken(self, d, muis):
        Schaken.teken(self, d, muis)
        px = BX + 8 * VAK + 50
        if self.status:
            UI.tekst(d, self.status, 20, UI.ROOD, (px, 540))
        elif self.ik is not None and self.ander and not self.verbonden[1 - self.ik]:
            UI.tekst(d, UI.T("ander_weg") % self.ander, 20, UI.GOUD, (px, 540))
        UI.tekst(d, UI.T("kamer") % self.code, 20, UI.ACCENT, (px, 60))
        if self.fase == "wachten":
            UI.tekst(d, self.code, 56, UI.GOUD, (px, 440))

    def stop(self):
        if self.lijn:
            self.lijn.stop()


# ------------------------------------------------------------------ oefen-lessen: stap voor stap leren schaken
def vak(naam):
    return (8 - int(naam[1])) * 8 + "abcdefgh".index(naam[0])


LESSEN = [
    {"titel": ("1. De toren", "1. The rook"),
     "uitleg": ("De toren (het kasteeltje) loopt zo ver als je wilt, maar alleen RECHT: omhoog, omlaag, links of rechts. "
                "Opdracht: sla de zwarte pion met je toren. Klik eerst op de toren, dan op de pion.",
                "The rook (the little castle) moves as far as you like, but only STRAIGHT: up, down, left or right. "
                "Task: capture the black pawn with your rook. Click the rook first, then the pawn."),
     "stukken": {"a1": "R", "e1": "K", "h8": "k", "a6": "p"}, "doel": "sla"},
    {"titel": ("2. De loper", "2. The bishop"),
     "uitleg": ("De loper (met het punthoedje) loopt zo ver als je wilt, maar alleen SCHUIN. Hij blijft dus altijd op dezelfde kleur. "
                "Opdracht: sla de zwarte pion met je loper.",
                "The bishop (with the pointed hat) moves as far as you like, but only DIAGONALLY. So it always stays on the same colour. "
                "Task: capture the black pawn with your bishop."),
     "stukken": {"c1": "B", "e1": "K", "h8": "k", "g5": "p"}, "doel": "sla"},
    {"titel": ("3. De dame", "3. The queen"),
     "uitleg": ("De dame (kroon met bolletjes) is je sterkste stuk: ze loopt recht én schuin, zo ver als je wilt. "
                "Opdracht: sla alle drie de zwarte pionnen met je dame. Zwart zet niet terug, neem rustig de tijd.",
                "The queen (crown with balls) is your strongest piece: she moves straight and diagonally, as far as you like. "
                "Task: capture all three black pawns with your queen. Black does not move, take your time."),
     "stukken": {"d1": "Q", "e1": "K", "h8": "k", "d6": "p", "h2": "p", "a4": "p"}, "doel": "sla"},
    {"titel": ("4. Het paard", "4. The knight"),
     "uitleg": ("Het paard springt in een L: twee vakjes de ene kant op en dan één opzij. Het mag als enige OVER andere stukken springen. "
                "Opdracht: sla de twee zwarte pionnen met je paard. Kijk naar de paarse stippen: daar mag hij heen.",
                "The knight jumps in an L: two squares one way and then one to the side. It is the only piece that may jump OVER others. "
                "Task: capture the two black pawns with your knight. Watch the purple dots: there it may go."),
     "stukken": {"b1": "N", "a2": "P", "b2": "P", "c2": "P", "e1": "K", "h8": "k", "c3": "p", "e4": "p"}, "doel": "sla"},
    {"titel": ("5. De pion", "5. The pawn"),
     "uitleg": ("De pion loopt één vakje vooruit (de eerste keer mag hij er twee). SLAAN doet hij schuin vooruit. "
                "Haalt hij de overkant, dan mag je kiezen wat hij wordt: meestal een dame! "
                "Opdracht: sla de zwarte pion en loop dan door tot de overkant.",
                "The pawn moves one square forward (the first time it may move two). It CAPTURES diagonally forward. "
                "If it reaches the far side, you choose what it becomes: usually a queen! "
                "Task: capture the black pawn and then walk on to the far side."),
     "stukken": {"e2": "P", "e1": "K", "a8": "k", "d3": "p"}, "doel": "promo"},
    {"titel": ("6. De koning", "6. The king"),
     "uitleg": ("De koning (met het kruisje) loopt maar één stapje, maar wel elke kant op. Hij is het belangrijkste stuk: "
                "als hij gevangen wordt, ben je af. Hij mag nooit op een vakje gaan staan dat de ander aanvalt. "
                "Opdracht: sla de zwarte pion met je koning.",
                "The king (with the cross) moves just one step, but in every direction. He is the most important piece: "
                "if he is caught, you lose. He may never step onto a square the other attacks. "
                "Task: capture the black pawn with your king."),
     "stukken": {"e1": "K", "h8": "k", "e2": "p"}, "doel": "sla"},
    {"titel": ("7. Schaak!", "7. Check!"),
     "uitleg": ("Val je de koning van de ander aan, dan staat hij SCHAAK. Hij moet dan meteen weg, of iets ertussen zetten. "
                "Opdracht: zet de zwarte koning schaak met je toren (in één zet).",
                "If you attack the other king, he is in CHECK. He must get away at once, or put something in between. "
                "Task: put the black king in check with your rook (in one move)."),
     "stukken": {"a1": "R", "g1": "K", "e8": "k"}, "doel": "schaak"},
    {"titel": ("8. Schaakmat!", "8. Checkmate!"),
     "uitleg": ("Staat de koning schaak en kan hij NERGENS meer heen, dan is het SCHAAKMAT: dan win je! "
                "Opdracht: de zwarte koning zit klem achter zijn eigen pionnen. Zet hem mat in één zet.",
                "Is the king in check and can he go NOWHERE, then it is CHECKMATE: you win! "
                "Task: the black king is stuck behind his own pawns. Checkmate him in one move."),
     "stukken": {"a1": "R", "g1": "K", "g8": "k", "f7": "p", "g7": "p", "h7": "p"}, "doel": "mat"},
    {"titel": ("9. Rokeren", "9. Castling"),
     "uitleg": ("Rokeren is een speciale zet om je koning veilig te zetten. Klik op de koning en zet hem TWEE vakjes naar de toren. "
                "De toren springt dan vanzelf over hem heen. Dat mag alleen als koning en toren nog niet bewogen hebben. "
                "Opdracht: rokeer naar rechts.",
                "Castling is a special move to put your king in safety. Click the king and move it TWO squares towards the rook. "
                "The rook then jumps over him by itself. Only allowed if king and rook have not moved yet. "
                "Task: castle to the right."),
     "stukken": {"e1": "K", "h1": "R", "f2": "P", "g2": "P", "h2": "P", "e8": "k"}, "rok": "K", "doel": "rokade"},
    {"titel": ("10. Je eerste partij", "10. Your first game"),
     "uitleg": ("Je kent nu alle stukken! Speel een echte partij tegen de computer op makkelijk. "
                "Klik op een stuk: de paarse stippen laten zien waar het heen mag. Hulp staat aan, en Tip helpt je altijd.",
                "You now know all the pieces! Play a real game against the computer on easy. "
                "Click a piece: the purple dots show where it may go. Help is on, and Tip always helps you."),
     "stukken": None, "doel": "partij"},
]

LES_TX = {
    "les_titel": ("Leer schaken", "Learn chess"),
    "goed": ("Goed zo! Opdracht gelukt.", "Well done! Task complete."),
    "bijna": ("Bijna! Dat was nog niet de opdracht. Probeer het nog eens.", "Almost! That wasn't the task yet. Try again."),
    "volgende": ("Volgende les", "Next lesson"),
    "opnieuw": ("Opnieuw", "Again"),
    "vorige": ("Vorige", "Previous"),
    "alles_klaar": ("Alle lessen gedaan! Speel nu zelf: kies Computer - makkelijk.", "All lessons done! Now play: choose Computer - easy."),
    "les_van": ("Les %d van %d", "Lesson %d of %d"),
}


def LT(k):
    v = LES_TX[k]
    return v[0] if UI.TAAL == "nl" else v[1]


class SchaakLes(Schaken):
    """Oefen-lessen: elk stuk apart, met een kleine opdracht. Zwart zet niet terug (behalve in de laatste les)."""

    def __init__(self, app, nr=0):
        self.nr = nr
        self.gelukt = False
        Schaken.__init__(self, app, 0)

    def naam(self, sp):
        return UI.T("jij") if sp == self.mij else UI.T("computer")

    def les(self):
        return LESSEN[self.nr]

    def nieuw_potje(self, wissel=False):
        Schaken.nieuw_potje(self, wissel=False)
        self.mij = WIT
        self.gelukt = False
        les = self.les()
        if les["stukken"] is None:                     # laatste les: een echte partij op makkelijk
            self.niveau = 1
            return
        self.niveau = 0
        b = ["."] * 64
        for naam, st in les["stukken"].items():
            b[vak(naam)] = st
        self.s.b = b
        self.s.rok = les.get("rok", "")
        self.s.ep = None
        self.s.historie = [self.s.sleutel()]
        self.lijst = zetten(self.s)

    def ga_naar(self, nr):
        self.nr = max(0, min(len(LESSEN) - 1, nr))
        self.app.geluid.speel("klik")
        self.nieuw_potje()

    def doelen(self):
        """De zwarte stukken die je moet slaan (gouden ring)."""
        if self.les()["doel"] not in ("sla", "promo"):
            return []
        return [v for v, st in enumerate(self.s.b) if st != "." and kleur(st) == ZWART and st != "k"]

    def klaar_met_zet(self):
        les = self.les()
        if les["doel"] == "partij":
            Schaken.klaar_met_zet(self)
            return
        z = self.anim["zet"]
        self.anim = None
        oud = self.s
        self.s = doe(oud, z)
        self.laatste = z
        doel = les["doel"]
        b = self.s.b
        if oud.b[z[1]] != ".":
            self.app.geluid.speel("goed")
        else:
            self.app.geluid.speel("zet")
        if doel == "sla":
            klaar = not self.doelen()
        elif doel == "promo":
            klaar = "Q" in b[0:8] or "R" in b[0:8] or "B" in b[0:8] or "N" in b[0:8]
        elif doel == "schaak":
            klaar = schaak(self.s, ZWART)
        elif doel == "mat":
            u = uitslag(self.s)
            klaar = bool(u and u[0] == "mat")
        else:                                          # rokade
            klaar = b[vak("g1")] == "K" and b[vak("f1")] == "R"
        if klaar:
            self.gelukt = True
            self.klaar = True
            self.melding = LT("goed")
            self.app.geluid.speel("win")
            return
        if doel in ("schaak", "mat", "rokade"):        # niet gelukt: terug naar het begin van de opdracht
            self.melding = LT("bijna")
            self.app.geluid.speel("fout")
            self.nieuw_potje()
            self.melding = LT("bijna")
            return
        self.s.zet = WIT                               # zwart zet niet terug: jij weer
        self.s.ep = None
        self.lijst = zetten(self.s)

    def geef_tip(self):
        if self.les()["doel"] == "partij":
            Schaken.geef_tip(self)
            return
        if self.klaar or self.anim:
            return
        doel = self.les()["doel"]
        kandidaten = []
        for z in self.lijst:
            n = doe(self.s, z)
            if doel == "mat":
                u = uitslag(n)
                if u and u[0] == "mat":
                    kandidaten.insert(0, z)
            elif doel == "schaak" and schaak(n, ZWART):
                kandidaten.insert(0, z)
            elif doel == "rokade" and self.s.b[z[0]] == "K" and z[1] - z[0] == 2:
                kandidaten.insert(0, z)
            elif doel in ("sla", "promo") and self.s.b[z[1]] != ".":
                kandidaten.insert(0, z)
            elif doel == "promo" and self.s.b[z[0]] == "P":
                kandidaten.append(z)
            elif doel == "sla" and self.s.b[z[0]] != "K" or (doel == "sla" and len(self.les()["stukken"]) == 3):
                kandidaten.append(z)
        if not kandidaten:
            return
        z = kandidaten[0]
        if self.les()["doel"] == "sla" and self.s.b[z[1]] == ".":
            # nog niets te slaan: kies een zet die dichter bij een pion komt (voor het paard)
            doelen = self.doelen()
            def afstand(zz):
                return min(abs(zz[1] // 8 - d // 8) + abs(zz[1] % 8 - d % 8) for d in doelen) if doelen else 0
            z = min((zz for zz in self.lijst if self.s.b[zz[0]] != "K"), key=afstand, default=z)
        self.tip = z
        self.kies = None
        self.melding = T("tip_kop")
        self.app.geluid.speel("goed")

    def teken(self, d, muis):
        les = self.les()
        Schaken.teken(self, d, muis)
        if les["doel"] == "partij":
            return
        # gouden ring om de pionnen die je moet slaan
        for v in self.doelen():
            x, y = self.scherm_xy(v)
            pygame.draw.circle(d, UI.GOUD, (x, y), VAK // 2 - 4, 4)
        # rechts: de les in plaats van de scores
        px = BX + 8 * VAK + 50
        pygame.draw.rect(d, UI.ACHTER, (px - 20, 40, UI.W - px + 20, 685))
        self.teken_les_kop(d, muis)

    def teken_les_kop(self, d, muis, partij=False):
        les = self.les()
        px = BX + 8 * VAK + 50
        taal = 0 if UI.TAAL == "nl" else 1
        if not partij:
            UI.tekst(d, LT("les_van") % (self.nr + 1, len(LESSEN)), 18, UI.ZACHT, (px, 50), vet=False)
            UI.tekst(d, les["titel"][taal], 32, UI.GOUD, (px, 76))
            y = 128
            for stuk in UI.Backgammon._knip(None, les["uitleg"][taal], 22, UI.W - px - 30):
                UI.tekst(d, stuk, 22, UI.TEKST, (px, y), vet=False)
                y += 30
            y += 14
            if self.melding:
                for stuk in UI.Backgammon._knip(None, self.melding, 24, UI.W - px - 30):
                    UI.tekst(d, stuk, 24, UI.GROEN if self.gelukt else UI.GOUD, (px, y))
                    y += 32
            if self.gelukt and self.nr == len(LESSEN) - 2:
                pass
        self.knoppen = []
        if partij:
            self.knoppen.append(UI.Knop((px, 580, 120, 64), UI.T("tip"), self.geef_tip, UI.GOUD, 24,
                                        aan=not self.klaar and self.beurt == self.mij and not self.anim))
            if self.klaar:
                self.knoppen.append(UI.Knop((px + 132, 580, 280, 64), UI.T("nog"), self.nieuw_potje, UI.GROEN, 24))
        else:
            if self.gelukt and self.nr < len(LESSEN) - 1:
                self.knoppen.append(UI.Knop((px, 580, 260, 64), LT("volgende"), lambda: self.ga_naar(self.nr + 1), UI.GROEN, 24))
            else:
                self.knoppen.append(UI.Knop((px, 580, 120, 64), UI.T("tip"), self.geef_tip, UI.GOUD, 24, aan=not self.klaar and not self.anim))
            self.knoppen.append(UI.Knop((px + 272, 580, 140, 64), LT("opnieuw"), self.nieuw_potje, UI.VAK, 22))
        self.knoppen.append(UI.Knop((px, 660, 190, 60), UI.T("menu"), self.app.naar_menu, UI.VAK, 24))
        self.knoppen.append(UI.Knop((px + 205, 660, 100, 60), "<", lambda: self.ga_naar(self.nr - 1), UI.VAK, 26, aan=self.nr > 0))
        self.knoppen.append(UI.Knop((px + 315, 660, 100, 60), ">", lambda: self.ga_naar(self.nr + 1), UI.VAK, 26, aan=self.nr < len(LESSEN) - 1))
        for k in self.knoppen:
            k.teken(d, muis)
