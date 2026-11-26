# -*- coding: utf-8 -*-
"""DraveSpellenkast - Pesten: het bekende kaartspel. Gooi een kaart op met dezelfde kleur of hetzelfde getal.
2 = de volgende pakt er 2, joker = 5, 7 en heer = nog een keer, 8 = de volgende slaat over, boer = kleur kiezen,
aas = andersom. Wie het eerst geen kaarten meer heeft, wint.
Tegen 1 tot 3 computers of online. Copyright (C) 2026 Dravenlock (Roger & Claudio). GNU GPL v3.0."""
import math
import random
import time

import pygame

UI = None          # wordt door main.py gezet

KLEUREN = "hrks"   # harten, ruiten, klaveren, schoppen
WAARDEN = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "B", "V", "H", "A"]
ROOD_K = (204, 50, 70)
ZWART_K = (34, 30, 44)
KAART_W, KAART_H = 92, 132

TX = {
    "pest": ("Pesten", "Crazy Eights"),
    "jouw_beurt": ("Jouw beurt: gooi een kaart op die past (oplicht), of pak er een.", "Your turn: play a card that fits (lit), or draw one."),
    "straf": ("Je moet %d kaarten pakken! (of leg zelf een 2 of joker)", "You must draw %d cards! (or play a 2 or joker yourself)"),
    "pak": ("Pak", "Draw"),
    "klaar": ("Klaar", "Done"),
    "kies_kleur": ("Je boer: kies een kleur.", "Your jack: choose a suit."),
    "na_pak": ("Je pakte een kaart. Past hij? Gooi hem op. Anders: Klaar.", "You drew a card. Does it fit? Play it. Otherwise: Done."),
    "laatste": ("%s: laatste kaart!", "%s: last card!"),
    "wint": ("%s is alle kaarten kwijt en wint!", "%s has no cards left and wins!"),
    "speelt": ("%s gooit %s", "%s plays %s"),
    "pakt": ("%s pakt %d", "%s draws %d"),
    "nog_keer": ("%s mag nog een keer.", "%s goes again."),
    "slaat_over": ("%s slaat een beurt over.", "%s misses a turn."),
    "draait": ("Andersom!", "Reverse!"),
    "kleur_nu": ("Gevraagde kleur: ", "Asked suit: "),
    "computer_n": ("Computer %d", "Computer %d"),
    "kaarten": ("%d kaarten", "%d cards"),
    "tip_kop": ("Tip: gooi de gouden kaart op.", "Tip: play the gold card."),
    "toetsen_pest": ("Klik een kaart  ·  P = pakken  ·  K = klaar  ·  T = tip  ·  Esc = menu",
                     "Click a card  ·  P = draw  ·  K = done  ·  T = tip  ·  Esc = menu"),
}


def T(k):
    if k in TX:
        v = TX[k]
        return v[0] if UI.TAAL == "nl" else v[1]
    return UI.T(k)


def nieuw_stok():
    return [(w, k) for k in KLEUREN for w in WAARDEN] + [("X", "*"), ("X", "*")]


def naam_kaart(c):
    if c[0] == "X":
        return "Joker"
    teken = {"h": "♥", "r": "♦", "k": "♣", "s": "♠"}[c[1]]
    w = {"B": "Boer" if UI.TAAL == "nl" else "J", "V": "Vrouw" if UI.TAAL == "nl" else "Q",
         "H": "Heer" if UI.TAAL == "nl" else "K", "A": "Aas" if UI.TAAL == "nl" else "A"}.get(c[0], c[0])
    return "%s %s" % (teken, w)


# ------------------------------------------------------------------ het spel
class Pesten:
    def __init__(self, app, aantal):
        self.app = app
        self.aantal = aantal              # aantal computerspelers
        self.knoppen = []
        self.gewonnen = [0] * 4
        self.begint = 0
        self.nieuw_potje()

    def spelers(self):
        return 1 + self.aantal

    def naam(self, i):
        return UI.T("jij") if i == 0 else T("computer_n") % i

    def mijn_idx(self):
        return 0

    def is_mens(self, i):
        return i == 0

    def nieuw_potje(self, zaad=None, begint=None):
        self.rnd = random.Random(zaad)
        stok = nieuw_stok()
        self.rnd.shuffle(stok)
        n = self.spelers()
        self.hand = [stok[i * 7:(i + 1) * 7] for i in range(n)]
        self.pot = stok[n * 7:]
        # begin met een gewone kaart op tafel
        while self.pot[-1][0] in ("2", "7", "8", "B", "H", "A", "X"):
            self.pot.insert(0, self.pot.pop())
        self.afleg = [self.pot.pop()]
        self.gevraagd = None              # kleur na een boer
        self.straf = 0                    # hoeveel kaarten de volgende moet pakken
        self.richting = 1
        self.beurt = self.begint if begint is None else begint
        self.begint = (self.begint + 1) % n
        self.gepakt = False               # deze beurt al een kaart gepakt
        self.klaar = False
        self.uitslag = ""
        self.melding = ""
        self.boer_wacht = None            # kaart-index als ik een kleur moet kiezen
        self.tip = None
        self.comp_t = time.time() + 1.2
        self.log = []
        for h in self.hand:
            self.sorteer(h)

    def sorteer(self, h):
        h.sort(key=lambda c: (KLEUREN.index(c[1]) if c[1] in KLEUREN else 9, WAARDEN.index(c[0]) if c[0] in WAARDEN else 99))

    def zeg(self, t):
        self.melding = t
        self.log.append(t)
        self.log = self.log[-4:]

    # ---------- regels
    def boven(self):
        return self.afleg[-1]

    def mag(self, c):
        b = self.boven()
        if self.straf:
            return c[0] in ("2", "X")
        if c[0] in ("X", "B"):
            return True
        if b[0] == "X":
            return True
        kleur = self.gevraagd or b[1]
        return c[1] == kleur or c[0] == b[0]

    def volgende_van(self, sp, stappen=1):
        return (sp + self.richting * stappen) % self.spelers()

    def trek(self, sp, n):
        for _ in range(n):
            if not self.pot:
                if len(self.afleg) <= 1:
                    break
                boven = self.afleg.pop()
                self.pot = self.afleg
                self.rnd.shuffle(self.pot)
                self.afleg = [boven]
            self.hand[sp].append(self.pot.pop())
        self.sorteer(self.hand[sp])

    def speel(self, sp, c, kleur=None):
        """Speel kaart c. Geeft True als dezelfde speler nog een keer mag."""
        self.hand[sp].remove(c)
        self.afleg.append(c)
        self.gevraagd = None
        self.zeg(T("speelt") % (self.naam(sp), naam_kaart(c)))
        self.app.geluid.speel("zet")
        if len(self.hand[sp]) == 1:
            self.zeg(T("laatste") % self.naam(sp))
        if not self.hand[sp]:
            self.klaar = True
            self.gewonnen[sp] += 1
            self.uitslag = T("wint") % self.naam(sp)
            self.app.geluid.speel("win" if sp == self.mijn_idx() else "verlies")
            return False
        w = c[0]
        nog = False
        stap = 1
        if w == "2":
            self.straf += 2
        elif w == "X":
            self.straf += 5
        elif w in ("7", "H"):
            nog = True
            self.zeg(T("nog_keer") % self.naam(sp))
        elif w == "8":
            stap = 2
            self.zeg(T("slaat_over") % self.naam(self.volgende_van(sp)))
        elif w == "A":
            self.richting *= -1
            self.zeg(T("draait"))
            if self.spelers() == 2:
                nog = True
        elif w == "B":
            self.gevraagd = kleur or "h"
        self.gepakt = False
        if nog:
            self.beurt = sp
        else:
            self.beurt = self.volgende_van(sp, stap)
        if stap == 2 and self.spelers() == 2:
            nog = True
        return nog

    def pak(self, sp):
        """Pak strafkaarten (beurt voorbij) of één kaart (dan mag je hem misschien nog opgooien)."""
        if self.straf:
            n = self.straf
            self.straf = 0
            self.trek(sp, n)
            self.zeg(T("pakt") % (self.naam(sp), n))
            self.beurt = self.volgende_van(sp)
            self.gepakt = False
            return False
        self.trek(sp, 1)
        self.gepakt = True
        self.zeg(T("pakt") % (self.naam(sp), 1))
        self.app.geluid.speel("klik")
        return True

    def klaar_beurt(self, sp):
        self.gepakt = False
        self.beurt = self.volgende_van(sp)

    # ---------- de computer
    def comp_keuze(self, sp):
        h = self.hand[sp]
        mog = [c for c in h if self.mag(c)]
        if not mog:
            return None, None
        volgende = self.volgende_van(sp)
        weinig = len(self.hand[volgende]) <= 2
        def score(c):
            s = 0
            if c[0] in ("2", "X"):
                s += 6 if weinig or self.straf else -3
            if c[0] == "B":
                s -= 5                                     # boer bewaren
            if c[0] in ("7", "H"):
                s += 3
            if c[0] == "8" and weinig:
                s += 5
            s += sum(1 for x in h if x[1] == c[1])         # kleur waar je veel van hebt
            return s + random.random()
        c = max(mog, key=score)
        kleur = None
        if c[0] == "B":
            tel = {k: sum(1 for x in h if x[1] == k and x != c) for k in KLEUREN}
            kleur = max(tel, key=tel.get)
        return c, kleur

    def comp_beurt(self, sp):
        c, kleur = self.comp_keuze(sp)
        if c:
            self.speel(sp, c, kleur)
            return
        if self.gepakt:
            self.klaar_beurt(sp)
            return
        self.pak(sp)

    def update(self):
        if self.klaar or self.is_mens(self.beurt) or not self.computer_mag():
            return
        if time.time() >= self.comp_t:
            self.comp_beurt(self.beurt)
            self.comp_t = time.time() + 1.0

    def computer_mag(self):
        return True

    def geef_tip(self):
        ik = self.mijn_idx()
        if self.klaar or self.beurt != ik:
            return
        c, _ = self.comp_keuze(ik)
        if c:
            self.tip = c
            self.melding = T("tip_kop")
            self.app.geluid.speel("goed")

    # ---------- mijn zetten
    def ik_speel(self, c, kleur=None):
        self.tip = None
        self.speel(self.mijn_idx(), c, kleur)
        self.comp_t = time.time() + 1.0

    def ik_pak(self):
        ik = self.mijn_idx()
        if self.klaar or self.beurt != ik or self.gepakt or self.boer_wacht is not None:
            return
        self.pak(ik)
        self.comp_t = time.time() + 1.0

    def ik_klaar(self):
        ik = self.mijn_idx()
        if self.klaar or self.beurt != ik or not self.gepakt:
            return
        self.klaar_beurt(ik)
        self.comp_t = time.time() + 1.0

    def hand_rects(self):
        h = self.hand[self.mijn_idx()]
        n = len(h)
        stap = min(KAART_W + 8, (UI.W - 140 - KAART_W) // max(1, n - 1)) if n > 1 else 0
        x0 = (UI.W - (stap * (n - 1) + KAART_W)) // 2
        return [pygame.Rect(x0 + i * stap, UI.H - KAART_H - 100, KAART_W, KAART_H) for i in range(n)]

    def kleur_rects(self):
        return {k: pygame.Rect(UI.W // 2 - 220 + i * 112, 300, 100, 100) for i, k in enumerate(KLEUREN)}

    def klik(self, pos):
        ik = self.mijn_idx()
        if self.klaar or self.beurt != ik:
            return
        if self.boer_wacht is not None:
            for k, r in self.kleur_rects().items():
                if r.collidepoint(pos):
                    c = self.boer_wacht
                    self.boer_wacht = None
                    self.ik_speel(c, k)
                    return
            return
        rects = self.hand_rects()
        for i in range(len(rects) - 1, -1, -1):           # de bovenste (rechtse) kaart eerst
            if rects[i].collidepoint(pos):
                c = self.hand[ik][i]
                if not self.mag(c):
                    self.app.geluid.speel("fout")
                    return
                if c[0] == "B" and len(self.hand[ik]) > 1:
                    self.boer_wacht = c
                    self.melding = T("kies_kleur")
                    return
                self.ik_speel(c)
                return
        if self.pot_rect().collidepoint(pos):
            self.ik_pak()

    def pot_rect(self):
        return pygame.Rect(UI.W // 2 - 150, 240, KAART_W, KAART_H)

    def toets(self, e):
        if e.key == pygame.K_ESCAPE:
            if self.boer_wacht is not None:
                self.boer_wacht = None
            else:
                self.app.naar_menu()
        elif self.klaar and e.key in (pygame.K_SPACE, pygame.K_RETURN):
            self.nieuw_potje()
        elif e.key == pygame.K_p:
            self.ik_pak()
        elif e.key == pygame.K_k:
            self.ik_klaar()
        elif e.key == pygame.K_t:
            self.geef_tip()

    # ---------- tekenen
    def teken_kaart(self, d, r, c, dicht=False, rand=None):
        pygame.draw.rect(d, (20, 16, 30), r.move(0, 4), border_radius=10)
        if dicht:
            pygame.draw.rect(d, (110, 96, 180), r, border_radius=10)
            pygame.draw.rect(d, (240, 236, 250), r, 3, border_radius=10)
            pygame.draw.rect(d, (140, 126, 210), r.inflate(-18, -18), 2, border_radius=8)
            UI.tekst(d, "D", int(r.h * 0.3), (150, 136, 220), r.center, mid=True)
            return
        pygame.draw.rect(d, (250, 248, 242), r, border_radius=10)
        pygame.draw.rect(d, (120, 110, 140), r, 2, border_radius=10)
        if c[0] == "X":
            UI.tekst(d, "JOKER", int(r.h * 0.14), (150, 80, 200), (r.centerx, r.y + 18), mid=True)
            # een clownsgezichtje
            cx, cy = r.centerx, r.centery + 8
            pygame.draw.circle(d, (250, 210, 170), (cx, cy), int(r.w * 0.28))
            pygame.draw.polygon(d, (214, 72, 96), [(cx - 26, cy - 20), (cx, cy - 50), (cx + 26, cy - 20)])
            pygame.draw.circle(d, (240, 200, 60), (cx, cy - 52), 6)
            pygame.draw.circle(d, (214, 72, 96), (cx, cy + 4), 6)
            pygame.draw.circle(d, (40, 32, 52), (cx - 9, cy - 6), 3)
            pygame.draw.circle(d, (40, 32, 52), (cx + 9, cy - 6), 3)
            pygame.draw.arc(d, (40, 32, 52), (cx - 12, cy, 24, 16), 3.4, 6.0, 3)
        else:
            kl = ROOD_K if c[1] in "hr" else ZWART_K
            teken = {"h": "♥", "r": "♦", "k": "♣", "s": "♠"}[c[1]]
            UI.tekst(d, c[0], int(r.h * 0.2), kl, (r.x + 8, r.y + 4))
            teken_symbool(d, c[1], r.x + 20, r.y + int(r.h * 0.33), int(r.h * 0.09))
            teken_symbool(d, c[1], r.centerx + 6, r.centery + 10, int(r.h * 0.2))
            if c[0] in ("B", "V", "H"):
                UI.tekst(d, c[0], int(r.h * 0.26), kl, (r.centerx + 6, r.centery + 10), mid=True)
        if rand:
            pygame.draw.rect(d, rand, r.inflate(8, 8), 4, border_radius=12)

    def teken(self, d, muis):
        d.fill(UI.ACHTER)
        UI.tekst(d, T("pest"), 40, UI.ACCENT, (40, 14))
        tafel = pygame.Rect(30, 150, UI.W - 60, 300)
        pygame.draw.ellipse(d, (34, 84, 60), tafel)
        pygame.draw.ellipse(d, UI.RAND, tafel, 4)
        ik = self.mijn_idx()
        n = self.spelers()
        # de anderen bovenaan
        anderen = [(ik + i) % n for i in range(1, n)]
        breed = (UI.W - 80) // max(1, len(anderen))
        for j, sp in enumerate(anderen):
            x0 = 40 + j * breed
            k = len(self.hand[sp])
            for i in range(min(k, 12)):
                self.teken_kaart(d, pygame.Rect(x0 + i * 14, 70, 44, 64), None, dicht=True)
            kl = UI.GOUD if self.beurt == sp and not self.klaar else UI.ZACHT
            UI.tekst(d, "%s  ·  %s" % (self.naam(sp), T("kaarten") % k), 20, kl, (x0 + min(k, 12) * 14 + 56, 86))
            if k == 1:
                UI.tekst(d, "!", 30, UI.ROOD, (x0 + min(k, 12) * 14 + 56, 108))
        # pot en aflegstapel
        pr = self.pot_rect()
        if self.pot:
            for i in range(min(4, len(self.pot))):
                self.teken_kaart(d, pr.move(-i * 2, -i * 2), None, dicht=True)
            mag_pakken = self.beurt == ik and not self.klaar and not self.gepakt
            if mag_pakken and pr.collidepoint(muis):
                pygame.draw.rect(d, UI.GOUD, pr.inflate(10, 10), 4, border_radius=12)
        UI.tekst(d, str(len(self.pot)), 18, UI.ZACHT, (pr.centerx, pr.bottom + 16), mid=True)
        ar = pygame.Rect(UI.W // 2 + 40, 240, KAART_W, KAART_H)
        for i, c in enumerate(self.afleg[-3:]):
            self.teken_kaart(d, ar.move((i - 2) * 6, (i - 2) * 3), c)
        if self.gevraagd:
            UI.tekst(d, T("kleur_nu"), 20, UI.TEKST, (ar.right + 30, ar.y + 30))
            teken_symbool(d, self.gevraagd, ar.right + 60, ar.y + 80, 26)
        if self.straf:
            UI.tekst(d, "+%d" % self.straf, 40, UI.ROOD, (ar.right + 40, ar.bottom - 30))
        # richting: een gebogen pijl (zelf getekend)
        cx, cy = UI.W // 2 - 230, 300
        pygame.draw.arc(d, UI.ZACHT, (cx - 26, cy - 26, 52, 52), 0.6, 5.4, 5)
        hoek = 0.6 if self.richting == 1 else 5.4
        px_, py_ = cx + 26 * math.cos(hoek), cy - 26 * math.sin(hoek)
        z = -1 if self.richting == 1 else 1
        pygame.draw.polygon(d, UI.ZACHT, [(px_ - 10, py_ + 2 * z), (px_ + 10, py_ + 2 * z), (px_, py_ + 14 * z)])
        # mijn hand
        mijn = not self.klaar and self.beurt == ik and self.boer_wacht is None
        rects = self.hand_rects()
        for i, (c, r) in enumerate(zip(self.hand[ik], rects)):
            past = mijn and self.mag(c)
            hover = r.collidepoint(muis) and (i == len(rects) - 1 or not rects[i + 1].collidepoint(muis))
            rr = r.move(0, -20) if past and hover else r
            rand = UI.GOUD if self.tip == c else (UI.GROEN if past and self.app.hulp else None)
            self.teken_kaart(d, rr, c, rand=rand)
        # kleur kiezen bij een boer
        if self.boer_wacht is not None:
            laag = pygame.Surface((UI.W, 200), pygame.SRCALPHA)
            laag.fill((10, 8, 16, 220))
            d.blit(laag, (0, 260))
            UI.tekst(d, T("kies_kleur"), 26, UI.GOUD, (UI.W // 2, 274), mid=True)
            for k, r in self.kleur_rects().items():
                pygame.draw.rect(d, (250, 248, 242), r, border_radius=14)
                pygame.draw.rect(d, UI.ACCENT if r.collidepoint(muis) else UI.RAND, r, 4, border_radius=14)
                teken_symbool(d, k, r.centerx, r.centery, 32)
        # meldingen
        if self.klaar:
            regel, kl = self.uitslag, UI.GOUD
        elif self.beurt == ik:
            if self.straf:
                regel = T("straf") % self.straf
            elif self.gepakt:
                regel = T("na_pak")
            else:
                regel = T("jouw_beurt")
            kl = UI.TEKST
        else:
            regel, kl = (self.log[-1] if self.log else self.wacht_tekst()), UI.ZACHT
        UI.tekst(d, regel, 22, kl, (UI.W // 2, 470), mid=True)
        self.knoppen = []
        y = UI.H - 82
        if self.klaar:
            self.knoppen.append(UI.Knop((40, y, 300, 64), UI.T("nog"), self.nieuw_potje, UI.GROEN, 24))
        else:
            if self.gepakt and mijn:
                self.knoppen.append(UI.Knop((40, y, 170, 64), T("klaar"), self.ik_klaar, UI.GOUD, 24))
            else:
                self.knoppen.append(UI.Knop((40, y, 170, 64), T("pak"), self.ik_pak, UI.GROEN if mijn else UI.VAK, 24, aan=mijn))
            self.knoppen.append(UI.Knop((225, y, 120, 64), UI.T("tip"), self.geef_tip, UI.GOUD, 22, aan=mijn and self.tip_mag()))
            self.knoppen.append(UI.Knop((360, y, 200, 64), "%s: %s" % (UI.T("hulp"), UI.T("aan") if self.app.hulp else UI.T("uitm")),
                                        self.app.wissel_hulp, UI.VAK, 20))
        self.knoppen.append(UI.Knop((UI.W - 380, y, 160, 64), UI.T("menu"), self.app.naar_menu, UI.VAK, 24))
        self.knoppen.append(UI.Knop((UI.W - 205, y, 170, 64), UI.T("regels"), lambda: setattr(self.app, "toon_regels", True), UI.VAK, 20))
        for k in self.knoppen:
            k.teken(d, muis)
        sc = "  ·  ".join("%s %d" % (self.naam(i), self.gewonnen[i]) for i in range(n))
        UI.tekst(d, sc, 18, UI.GOUD, (UI.W - 30, 22), rechts=True)

    def tip_mag(self):
        return True

    def wacht_tekst(self):
        return T("beurt_van") % self.naam(self.beurt) if "beurt_van" in TX else ""


def teken_symbool(d, k, cx, cy, s):
    """Harten, ruiten, klaveren en schoppen, zelf getekend (geen lettertype nodig)."""
    kl = ROOD_K if k in "hr" else ZWART_K
    if k == "h":
        pygame.draw.circle(d, kl, (int(cx - s * 0.45), int(cy - s * 0.25)), int(s * 0.5))
        pygame.draw.circle(d, kl, (int(cx + s * 0.45), int(cy - s * 0.25)), int(s * 0.5))
        pygame.draw.polygon(d, kl, [(cx - s * 0.95, cy - s * 0.1), (cx + s * 0.95, cy - s * 0.1), (cx, cy + s)])
    elif k == "r":
        pygame.draw.polygon(d, kl, [(cx, cy - s), (cx + s * 0.75, cy), (cx, cy + s), (cx - s * 0.75, cy)])
    elif k == "k":
        pygame.draw.circle(d, kl, (int(cx), int(cy - s * 0.5)), int(s * 0.45))
        pygame.draw.circle(d, kl, (int(cx - s * 0.5), int(cy + s * 0.1)), int(s * 0.45))
        pygame.draw.circle(d, kl, (int(cx + s * 0.5), int(cy + s * 0.1)), int(s * 0.45))
        pygame.draw.polygon(d, kl, [(cx - s * 0.15, cy), (cx + s * 0.15, cy), (cx + s * 0.35, cy + s), (cx - s * 0.35, cy + s)])
    else:
        pygame.draw.circle(d, kl, (int(cx - s * 0.45), int(cy + s * 0.15)), int(s * 0.48))
        pygame.draw.circle(d, kl, (int(cx + s * 0.45), int(cy + s * 0.15)), int(s * 0.48))
        pygame.draw.polygon(d, kl, [(cx - s * 0.92, cy + s * 0.05), (cx + s * 0.92, cy + s * 0.05), (cx, cy - s)])
        pygame.draw.polygon(d, kl, [(cx - s * 0.15, cy + s * 0.2), (cx + s * 0.15, cy + s * 0.2), (cx + s * 0.35, cy + s), (cx - s * 0.35, cy + s)])


TX["beurt_van"] = ("%s is aan de beurt.", "%s's turn.")


# ------------------------------------------------------------------ online: met z'n tweeën
class OnlinePesten(Pesten):
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
        Pesten.__init__(self, app, 1)
        self.beurt = -1
        self.lijn = UI.online.Lijn(adres, code, {"t": "hallo", "spel": "pest", "naam": naam, "token": token}, pad="zet/kamer")

    def mijn_idx(self):
        return self.ik if self.ik is not None else 0

    def is_mens(self, i):
        return True

    def computer_mag(self):
        return False

    def tip_mag(self):
        return False

    def naam(self, i):
        if self.ik is None:
            return UI.T("speler%d" % (i + 1))
        return UI.T("jij") if i == self.ik else (self.ander or UI.T("tegenspeler"))

    def nieuw_potje(self, zaad=None, begint=None):
        if getattr(self, "lijn", None) is not None:
            self.lijn.stuur({"t": "nieuw"})
            self.app.geluid.speel("klik")
            return
        Pesten.nieuw_potje(self, zaad, begint)

    def stuur(self, z, nog, einde=None):
        if self.fase != "spel" or self.beurt != self.ik:
            return False
        if self.lijn.stuur({"t": "zet", "z": z, "nog": nog, "einde": einde}):
            self.n_zetten += 1
            return True
        self.status = UI.T("geen_server")
        return False

    def ik_speel(self, c, kleur=None):
        laatste = len(self.hand[self.ik]) == 1
        nog = c[0] in ("7", "H") or (c[0] in ("A", "8") and self.spelers() == 2)
        if self.stuur({"speel": list(c), "kleur": kleur}, nog=nog and not laatste, einde=self.ik if laatste else None):
            self.tip = None
            self.speel(self.ik, c, kleur)

    def ik_pak(self):
        if self.klaar or self.beurt != self.ik or self.gepakt or self.boer_wacht is not None:
            return
        straf = self.straf > 0
        if self.stuur({"pak": True}, nog=not straf):
            self.pak(self.ik)

    def ik_klaar(self):
        if self.klaar or self.beurt != self.ik or not self.gepakt:
            return
        if self.stuur({"klaar": True}, nog=False):
            self.klaar_beurt(self.ik)

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
            Pesten.nieuw_potje(self, zaad=st.get("zaad"), begint=st.get("eerste", 0))
            self.n_zetten = 0
            self.einde_gezien = False
        for d in lijst[self.n_zetten:]:
            z = d.get("z") or {}
            sp = d.get("sp", 0)
            self.n_zetten += 1
            self.beurt = sp
            if "speel" in z:
                c = tuple(z["speel"])
                if c in self.hand[sp]:
                    self.speel(sp, c, z.get("kleur"))
            elif z.get("pak"):
                self.pak(sp)
            elif z.get("klaar"):
                self.klaar_beurt(sp)
        self.gewonnen = list(st.get("score", [0, 0])) + [0, 0]
        if self.fase == "einde":
            self.klaar = True
            if not self.einde_gezien:
                self.einde_gezien = True
                if st.get("winnaar") != self.ik:
                    self.app.geluid.speel("verlies")
        else:
            self.klaar = False
            self.beurt = st["beurt"]

    def teken(self, d, muis):
        Pesten.teken(self, d, muis)
        UI.tekst(d, UI.T("kamer") % self.code, 20, UI.ACCENT, (220, 26))
        if self.status:
            UI.tekst(d, self.status, 20, UI.ROOD, (UI.W // 2, 500), mid=True)
        elif self.ik is not None and self.ander and not self.verbonden[1 - self.ik]:
            UI.tekst(d, UI.T("ander_weg") % self.ander, 20, UI.GOUD, (UI.W // 2, 500), mid=True)
        if self.fase == "wachten":
            UI.tekst(d, UI.T("wacht_ander") % self.code, 22, UI.TEKST, (UI.W // 2, 180), mid=True)
            UI.tekst(d, self.code, 56, UI.GOUD, (UI.W // 2, 215), mid=True)

    def stop(self):
        if self.lijn:
            self.lijn.stop()
