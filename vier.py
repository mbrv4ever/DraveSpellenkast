# -*- coding: utf-8 -*-
"""DraveSpellenkast - Vier op een rij (tegen de computer, of online tegen elkaar).
Grote schijven, klik op een kolom (of toets 1-7 / pijltjes + spatie). Tip-knop en hulp (waarschuwt als de ander bijna wint).
Copyright (C) 2026 Dravenlock (Roger & Claudio). GNU GPL v3.0."""
import random
import threading
import time

import pygame

UI = None          # wordt door main.py gezet

KOL, RIJ = 7, 6
CEL = 90
BX, BY = 70, 160                       # linksboven van het bord
SCHIJF = 38
KLEUR = [(232, 190, 80), (214, 72, 96)]  # goud (speler 1) en rood (speler 2): goed uit elkaar te houden
VOLGORDE = [3, 2, 4, 1, 5, 0, 6]       # midden eerst = sterker en sneller zoeken

TX = {
    "vier": ("Vier op een rij", "Connect four"),
    "vier_sub": ("Laat je schijf vallen: wie heeft er eerst vier op een rij?", "Drop your disc: who gets four in a row first?"),
    "jouw_beurt": ("Jouw beurt: klik op een kolom", "Your turn: click a column"),
    "comp_denkt": ("De computer denkt...", "The computer is thinking..."),
    "gelijk": ("Gelijkspel! Het bord is vol.", "A draw! The board is full."),
    "tip_win": ("Tip: hier win je!", "Tip: you win here!"),
    "tip_blok": ("Tip: blokkeer hier, anders wint de computer!", "Tip: block here, or the computer wins!"),
    "tip_midden": ("Tip: het midden is sterk, daar kun je de meeste rijen maken.", "Tip: the middle is strong, it gives the most rows."),
    "tip_goed": ("Tip: dit is de beste zet die ik zie.", "Tip: this is the best move I can see."),
    "tip_val": ("Tip: niet hier! Dan kan de computer er bovenop winnen.", "Tip: not here! Then the computer can win on top."),
    "let_op": ("Let op! De computer kan bijna vier op een rij maken (rood randje).", "Watch out! The computer almost has four in a row (red ring)."),
    "vol": ("Die kolom is vol.", "That column is full."),
    "toetsen_vier": ("Klik een kolom  ·  1-7 of pijltjes + spatie  ·  T = tip  ·  Esc = menu",
                     "Click a column  ·  1-7 or arrows + space  ·  T = tip  ·  Esc = menu"),
    "comp_moeilijk": ("Computer - moeilijk", "Computer - hard"),
}


def T(k):
    if k in TX:
        v = TX[k]
        return v[0] if UI.TAAL == "nl" else v[1]
    return UI.T(k)


# ------------------------------------------------------------------ spelregels en computer
def nieuw_bord():
    return [[-1] * RIJ for _ in range(KOL)]          # bord[kolom][rij], rij 0 = onderaan


def vrije_rij(b, k):
    for r in range(RIJ):
        if b[k][r] < 0:
            return r
    return -1


def vier_van(b, k, r):
    """De vier (of meer) vakjes op een rij door (k, r), of None."""
    sp = b[k][r]
    for dk, dr in ((1, 0), (0, 1), (1, 1), (1, -1)):
        lijn = [(k, r)]
        for s in (1, -1):
            x, y = k + dk * s, r + dr * s
            while 0 <= x < KOL and 0 <= y < RIJ and b[x][y] == sp:
                lijn.append((x, y))
                x, y = x + dk * s, y + dr * s
        if len(lijn) >= 4:
            return lijn
    return None


def wint_met(b, k, sp):
    r = vrije_rij(b, k)
    if r < 0:
        return False
    b[k][r] = sp
    w = vier_van(b, k, r) is not None
    b[k][r] = -1
    return w


def waarde(b, sp):
    """Hoe goed staat sp ervoor: open rijtjes van 2 en 3, en het midden."""
    s = 0
    for r in range(RIJ):
        if b[3][r] == sp:
            s += 4
        elif b[3][r] == 1 - sp:
            s -= 4
    for k in range(KOL):
        for r in range(RIJ):
            for dk, dr in ((1, 0), (0, 1), (1, 1), (1, -1)):
                ek, er = k + 3 * dk, r + 3 * dr
                if not (0 <= ek < KOL and 0 <= er < RIJ):
                    continue
                cel = [b[k + i * dk][r + i * dr] for i in range(4)]
                mijn, zijn, leeg = cel.count(sp), cel.count(1 - sp), cel.count(-1)
                if zijn == 0:
                    s += (0, 1, 4, 20, 0)[mijn] if mijn < 4 else 0
                elif mijn == 0:
                    s -= (0, 1, 5, 25, 0)[zijn] if zijn < 4 else 0
    return s


def zoek(b, diepte, sp, alfa, beta, wie):
    """Minimax met alfa-beta. Geeft (score, kolom). wie = de speler waarvoor we rekenen."""
    vrij = [k for k in VOLGORDE if vrije_rij(b, k) >= 0]
    if not vrij:
        return 0, None
    for k in vrij:                                   # direct winnen?
        if wint_met(b, k, sp):
            return (100000 + diepte if sp == wie else -100000 - diepte), k
    if diepte == 0:
        return waarde(b, wie), None
    beste_k = vrij[0]
    if sp == wie:
        beste = -10 ** 9
        for k in vrij:
            r = vrije_rij(b, k)
            b[k][r] = sp
            v, _ = zoek(b, diepte - 1, 1 - sp, alfa, beta, wie)
            b[k][r] = -1
            if v > beste:
                beste, beste_k = v, k
            alfa = max(alfa, v)
            if alfa >= beta:
                break
    else:
        beste = 10 ** 9
        for k in vrij:
            r = vrije_rij(b, k)
            b[k][r] = sp
            v, _ = zoek(b, diepte - 1, 1 - sp, alfa, beta, wie)
            b[k][r] = -1
            if v < beste:
                beste, beste_k = v, k
            beta = min(beta, v)
            if alfa >= beta:
                break
    return beste, beste_k


def kies_zet(b, sp, niveau):
    """niveau 1 = makkelijk, 2 = normaal, 3 = moeilijk."""
    vrij = [k for k in range(KOL) if vrije_rij(b, k) >= 0]
    for k in vrij:
        if wint_met(b, k, sp):
            return k
    if niveau == 1:
        if random.random() < 0.6:                    # meestal blokkeren, soms vergeten
            for k in vrij:
                if wint_met(b, k, 1 - sp):
                    return k
        return random.choice(vrij + [3, 3] if 3 in vrij else vrij)
    diepte = 4 if niveau == 2 else 6
    kopie = [kol[:] for kol in b]
    _, k = zoek(kopie, diepte, sp, -10 ** 9, 10 ** 9, sp)
    if niveau == 2 and random.random() < 0.12:       # normaal: af en toe een menselijke zet
        k = random.choice(vrij)
    return k if k is not None else random.choice(vrij)


# ------------------------------------------------------------------ het spel
class VierOpEenRij:
    def __init__(self, app, niveau):
        self.app = app
        self.niveau = niveau                         # 1, 2, 3 (tegen de computer)
        self.mij = 0                                 # mijn kleur (0 = goud); online kan dat 1 zijn
        self.knoppen = []
        self.score = [0, 0]
        self.begint = 0
        self.nieuw_potje()

    def naam(self, sp):
        return UI.T("jij") if sp == 0 else UI.T("computer")

    def nieuw_potje(self):
        self.b = nieuw_bord()
        self.beurt = self.begint
        self.begint = 1 - self.begint                # volgende keer begint de ander
        self.winlijn = None
        self.klaar = False
        self.uitslag = ""
        self.val = None                              # [kolom, rij, y, snelheid, speler] = vallende schijf
        self.tip_k = None
        self.melding = ""
        self.denk = None
        self.cursor = 3
        self.zetten = 0

    # ---------- zetten
    def doe_zet(self, k):
        if self.klaar or self.val or k is None:
            return
        r = vrije_rij(self.b, k)
        if r < 0:
            self.melding = T("vol")
            self.app.geluid.speel("fout")
            return
        self.tip_k = None
        self.melding = ""
        self.val = [k, r, BY - CEL * 0.6, 0.0, self.beurt]
        self.app.geluid.speel("klik")

    def geland(self):
        k, r, _, _, sp = self.val
        self.val = None
        self.b[k][r] = sp
        self.zetten += 1
        self.app.geluid.speel("zet")
        lijn = vier_van(self.b, k, r)
        if lijn:
            self.winlijn = lijn
            self.klaar = True
            self.score[sp] += 1
            self.uitslag = UI.T("wint") % self.naam(sp)
            self.app.geluid.speel("win" if sp == self.mij else "verlies")
            return
        if self.zetten >= KOL * RIJ:
            self.klaar = True
            self.uitslag = T("gelijk")
            return
        self.beurt = 1 - self.beurt

    def update(self):
        if self.val:
            self.val[3] += 2.2
            self.val[2] += self.val[3]
            doel_y = BY + (RIJ - 1 - self.val[1]) * CEL + CEL / 2
            if self.val[2] >= doel_y:
                if self.val[3] > 9:                  # klein stuitertje
                    self.val[2] = doel_y
                    self.val[3] = -self.val[3] * 0.25
                else:
                    self.geland()
            return
        if self.klaar or self.beurt == self.mij:
            return
        if self.denk is None:                        # de computer gaat nadenken (in de achtergrond)
            self.denk = {"k": None, "start": time.time()}
            bord = [kol[:] for kol in self.b]
            def denk(d=self.denk, bord=bord):
                d["k"] = kies_zet(bord, 1, self.niveau)
            threading.Thread(target=denk, daemon=True).start()
        elif self.denk["k"] is not None and time.time() - self.denk["start"] > 0.6:
            k = self.denk["k"]
            self.denk = None
            self.doe_zet(k)

    def wacht_tekst(self):
        return T("comp_denkt")

    # ---------- hulp
    def dreiging(self):
        """Kolommen waar de computer de volgende beurt kan winnen."""
        return [k for k in range(KOL) if wint_met(self.b, k, 1 - self.mij)]

    def geef_tip(self):
        if self.klaar or self.beurt != self.mij or self.val:
            return
        vrij = [k for k in range(KOL) if vrije_rij(self.b, k) >= 0]
        for k in vrij:
            if wint_met(self.b, k, self.mij):
                self.tip_k, self.melding = k, T("tip_win")
                break
        else:
            dr = self.dreiging()
            if dr:
                self.tip_k, self.melding = dr[0], T("tip_blok")
            else:
                kopie = [kol[:] for kol in self.b]
                _, k = zoek(kopie, 5, self.mij, -10 ** 9, 10 ** 9, self.mij)
                self.tip_k = k if k is not None else 3
                self.melding = T("tip_midden") if self.tip_k == 3 and self.zetten < 4 else T("tip_goed")
        self.app.geluid.speel("goed")

    def gevaarlijk(self, k):
        """Zet ik hier, kan de computer er dan bovenop winnen?"""
        r = vrije_rij(self.b, k)
        if r < 0 or r + 1 >= RIJ:
            return False
        self.b[k][r] = self.mij
        bovenop = wint_met(self.b, k, 1 - self.mij)
        self.b[k][r] = -1
        return bovenop

    # ---------- invoer
    def kolom_op(self, pos):
        x, y = pos
        if BX <= x < BX + KOL * CEL and BY - CEL <= y < BY + RIJ * CEL:
            return int((x - BX) // CEL)
        return None

    def klik(self, pos):
        if self.klaar or self.beurt != self.mij:
            return
        k = self.kolom_op(pos)
        if k is not None:
            self.cursor = k
            self.doe_zet(k)

    def toets(self, e):
        if e.key == pygame.K_ESCAPE:
            self.app.naar_menu()
        elif self.klaar and e.key in (pygame.K_SPACE, pygame.K_RETURN):
            self.nieuw_potje()
        elif e.key == pygame.K_t:
            self.geef_tip()
        elif self.beurt == self.mij and not self.klaar:
            if pygame.K_1 <= e.key <= pygame.K_7:
                self.cursor = e.key - pygame.K_1
                self.doe_zet(self.cursor)
            elif e.key == pygame.K_LEFT:
                self.cursor = max(0, self.cursor - 1)
            elif e.key == pygame.K_RIGHT:
                self.cursor = min(KOL - 1, self.cursor + 1)
            elif e.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_DOWN):
                self.doe_zet(self.cursor)

    # ---------- tekenen
    def teken_schijf(self, d, x, y, sp, alfa=255, rand=None):
        x, y = int(x), int(y)
        kl = KLEUR[sp]
        if alfa < 255:
            s = pygame.Surface((SCHIJF * 2 + 4, SCHIJF * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(s, kl + (alfa,), (SCHIJF + 2, SCHIJF + 2), SCHIJF)
            d.blit(s, (x - SCHIJF - 2, y - SCHIJF - 2))
            return
        pygame.draw.circle(d, tuple(max(0, c - 60) for c in kl), (x, y + 3), SCHIJF)
        pygame.draw.circle(d, kl, (x, y), SCHIJF)
        pygame.draw.circle(d, tuple(min(255, c + 30) for c in kl), (x, y), SCHIJF - 10, 4)
        pygame.draw.circle(d, (255, 255, 255), (x - 14, y - 14), 6)
        if rand:
            pygame.draw.circle(d, rand, (x, y), SCHIJF + 4, 5)

    def teken(self, d, muis):
        d.fill(UI.ACHTER)
        UI.tekst(d, T("vier"), 40, UI.ACCENT, (BX, 14))
        # bord met gaten
        bord = pygame.Rect(BX - 12, BY - 12, KOL * CEL + 24, RIJ * CEL + 24)
        mk = None
        if not self.klaar and self.beurt == self.mij:
            mk = self.kolom_op(muis)
            if mk is None:
                mk = self.cursor                     # toetsenbord: pijltjes kiezen de kolom
            else:
                self.cursor = mk
        # schijven achter het bord
        for k in range(KOL):
            for r in range(RIJ):
                if self.b[k][r] >= 0:
                    self.teken_schijf(d, BX + k * CEL + CEL / 2, BY + (RIJ - 1 - r) * CEL + CEL / 2, self.b[k][r])
        if self.val:
            self.teken_schijf(d, BX + self.val[0] * CEL + CEL / 2, self.val[2], self.val[4])
        # het bord zelf (met gaten)
        laag = pygame.Surface(bord.size, pygame.SRCALPHA)
        pygame.draw.rect(laag, (70, 58, 120, 255), laag.get_rect(), border_radius=22)
        for k in range(KOL):
            for r in range(RIJ):
                pygame.draw.circle(laag, (0, 0, 0, 0), (12 + k * CEL + CEL // 2, 12 + r * CEL + CEL // 2), SCHIJF + 2)
        d.blit(laag, bord.topleft)
        for k in range(KOL):                          # randjes om de gaten
            for r in range(RIJ):
                pygame.draw.circle(d, (110, 96, 170), (BX + k * CEL + CEL // 2, BY + r * CEL + CEL // 2), SCHIJF + 2, 3)
        pygame.draw.rect(d, UI.RAND, bord, 4, border_radius=22)
        if self.winlijn:                              # de vier op een rij laten knipperen (boven op het bord)
            kl = (255, 255, 255) if int(time.time() * 4) % 2 else UI.GOUD
            for k, r in self.winlijn:
                pygame.draw.circle(d, kl, (BX + k * CEL + CEL // 2, BY + (RIJ - 1 - r) * CEL + CEL // 2), SCHIJF + 3, 7)
        # hulp: waar kan de computer winnen?
        if self.app.hulp and not self.klaar and self.beurt == self.mij and not self.val:
            for k in self.dreiging():
                r = vrije_rij(self.b, k)
                pygame.draw.circle(d, UI.ROOD, (BX + k * CEL + CEL // 2, BY + (RIJ - 1 - r) * CEL + CEL // 2), SCHIJF - 4, 6)
        # waar valt hij? (spookschijf boven de kolom)
        if mk is not None and vrije_rij(self.b, mk) >= 0 and not self.val:
            self.teken_schijf(d, BX + mk * CEL + CEL / 2, BY - CEL * 0.55, self.mij, alfa=170)
            if self.app.hulp and self.gevaarlijk(mk):
                UI.tekst(d, "!", 40, UI.ROOD, (BX + mk * CEL + CEL // 2, BY - CEL * 0.55), mid=True)
        if self.tip_k is not None:
            x = BX + self.tip_k * CEL + CEL // 2
            pygame.draw.polygon(d, UI.GOUD, [(x - 22, BY - 92), (x + 22, BY - 92), (x, BY - 62)])
        for k in range(KOL):                          # kolomnummers
            UI.tekst(d, str(k + 1), 22, UI.ZACHT, (BX + k * CEL + CEL // 2, BY + RIJ * CEL + 30), mid=True)
        # rechts: wie, score, meldingen, knoppen
        px = BX + KOL * CEL + 60
        for sp in (0, 1):
            y = 160 + sp * 90
            self.teken_schijf(d, px + 30, y + 30, sp)
            UI.tekst(d, self.naam(sp), 30, UI.TEKST, (px + 80, y + 4))
            UI.tekst(d, str(self.score[sp]), 30, UI.GOUD, (UI.W - 60, y + 4), rechts=True)
            if not self.klaar and self.beurt == sp:
                pygame.draw.rect(d, UI.ACCENT, (px - 12, y - 6, UI.W - px - 36, 74), 3, border_radius=12)
        y = 360
        if self.klaar:
            regels = [self.uitslag]
        elif self.beurt != self.mij:
            regels = [self.wacht_tekst()]
        else:
            regels = [T("jouw_beurt")]
            if self.app.hulp and self.dreiging() and not self.melding:
                regels.append(T("let_op"))
        if self.melding:
            regels.append(self.melding)
        for regel in regels:
            for stuk in UI.Backgammon._knip(None, regel, 24, UI.W - px - 40):
                UI.tekst(d, stuk, 24, UI.GOUD if regel in (self.melding, self.uitslag) else UI.TEKST, (px, y), vet=regel != T("let_op"))
                y += 34
            y += 8
        self.knoppen = []
        if self.klaar:
            self.knoppen.append(UI.Knop((px, 560, 300, 70), UI.T("nog"), self.nieuw_potje, UI.GROEN, 26))
        else:
            self.knoppen.append(UI.Knop((px, 560, 140, 70), UI.T("tip"), self.geef_tip, UI.GOUD, 26,
                                        aan=self.beurt == self.mij and not self.val))
            self.knoppen.append(UI.Knop((px + 160, 560, 210, 70), "%s: %s" % (UI.T("hulp"), UI.T("aan") if self.app.hulp else UI.T("uitm")),
                                        self.app.wissel_hulp, UI.VAK, 22))
        self.knoppen.append(UI.Knop((px, 650, 200, 60), UI.T("menu"), self.app.naar_menu, UI.VAK, 24))
        self.knoppen.append(UI.Knop((px + 220, 650, 200, 60), UI.T("regels"), lambda: setattr(self.app, "toon_regels", True), UI.VAK, 22))
        for k in self.knoppen:
            k.teken(d, muis)
        UI.tekst(d, T("toetsen_vier"), 18, UI.ZACHT, (BX, UI.H - 30), vet=False)


# ------------------------------------------------------------------ online tegen elkaar
class OnlineVier(VierOpEenRij):
    """Vier op een rij op twee pc's. De server houdt het bord bij en controleert elke zet."""

    def __init__(self, app, adres, code, naam, token):
        self.lijn = None
        self.code = code
        self.ik = None
        self.ander = None
        self.verbonden = [False, False]
        self.status = UI.T("verbinden")
        self.zetnr = None
        self.fase = "wachten"
        self.einde_gezien = False
        VierOpEenRij.__init__(self, app, 0)
        self.lijn = UI.online.Lijn(adres, code, {"t": "hallo", "naam": naam, "token": token}, pad="vier/kamer")

    def naam(self, sp):
        if self.ik is None:
            return UI.T("speler%d" % (sp + 1))
        return UI.T("jij") if sp == self.ik else (self.ander or UI.T("tegenspeler"))

    def nieuw_potje(self):
        if self.lijn is not None:                    # knop "Nog een potje"
            self.lijn.stuur({"t": "nieuw"})
            self.app.geluid.speel("klik")
            return
        VierOpEenRij.nieuw_potje(self)
        self.beurt = -1                              # nog niemand: wachten op de server

    def wacht_tekst(self):
        if self.fase == "wachten":
            return UI.T("wacht_ander") % self.code
        return UI.T("ander_beurt") % self.naam(self.beurt)

    def doe_zet(self, k):
        if self.klaar or self.val or k is None or self.beurt != self.mij or self.fase != "spel":
            return
        if vrije_rij(self.b, k) < 0:
            self.melding = T("vol")
            self.app.geluid.speel("fout")
            return
        if self.lijn.stuur({"t": "zet", "k": int(k)}):
            self.tip_k = None
            self.melding = UI.T("versturen")
            self.beurt = -1                          # tot de server antwoordt
            self.app.geluid.speel("klik")
        else:
            self.status = UI.T("geen_server")

    def geland(self):
        k, r, _, _, sp = self.val
        self.val = None
        self.b[k][r] = sp
        self.app.geluid.speel("zet")

    def update(self):
        if self.val:                                 # vallende schijf (zelfde als offline)
            self.val[3] += 2.2
            self.val[2] += self.val[3]
            doel_y = BY + (RIJ - 1 - self.val[1]) * CEL + CEL / 2
            if self.val[2] >= doel_y:
                if self.val[3] > 9:
                    self.val[2] = doel_y
                    self.val[3] = -self.val[3] * 0.25
                else:
                    self.geland()
            return
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
            elif t == "stand":
                try:
                    self.pas_toe(b)
                except Exception:
                    import traceback
                    UI.log_fout(traceback.format_exc())
            if self.val:                             # eerst de schijf laten vallen, dan de rest
                break

    def pas_toe(self, st):
        self.ik = self.mij = st["ik"]
        self.score = list(st.get("score", [0, 0]))
        self.ander = (st.get("ander") or {}).get("naam")
        self.verbonden = st.get("verbonden", [True, True])
        self.fase = st["fase"]
        if self.fase == "wachten":
            self.beurt = -1
            return
        if st["zetnr"] != self.zetnr:
            self.zetnr = st["zetnr"]
            nieuw = [list(kol) for kol in st["bord"]]
            l = st.get("laatste")
            if l and self.b[l["k"]][l["r"]] < 0 and nieuw[l["k"]][l["r"]] == l["sp"]:
                nieuw[l["k"]][l["r"]] = -1           # deze laten we eerst vallen
                self.b = nieuw
                self.val = [l["k"], l["r"], BY - CEL * 0.6, 0.0, l["sp"]]
            else:
                self.b = nieuw
            if self.melding == UI.T("versturen"):
                self.melding = ""
        self.zetten = sum(1 for kol in self.b for c in kol if c >= 0)
        self.beurt = st["beurt"]
        if self.fase == "einde":
            self.klaar = True
            w = st.get("winnaar")
            self.winlijn = [tuple(x) for x in st.get("winlijn") or []] or None
            self.uitslag = T("gelijk") if w == -1 else UI.T("wint") % self.naam(w)
            if not self.einde_gezien:
                self.einde_gezien = True
                self.app.geluid.speel("win" if w == self.ik else ("klik" if w == -1 else "verlies"))
        else:
            if self.klaar:                            # nieuw potje begonnen
                self.tip_k = None
                self.melding = ""
            self.klaar = False
            self.winlijn = None
            self.einde_gezien = False

    def teken(self, d, muis):
        VierOpEenRij.teken(self, d, muis)
        px = BX + KOL * CEL + 60
        if self.status:
            UI.tekst(d, self.status, 20, UI.ROOD, (px, 520))
        elif self.ik is not None and self.ander and not self.verbonden[1 - self.ik]:
            UI.tekst(d, UI.T("ander_weg") % self.ander, 20, UI.GOUD, (px, 520))
        UI.tekst(d, UI.T("kamer") % self.code, 20, UI.ACCENT, (px, 108))
        if self.fase == "wachten":
            UI.tekst(d, self.code, 56, UI.GOUD, (px, 440))

    def stop(self):
        if self.lijn:
            self.lijn.stop()
