# -*- coding: utf-8 -*-
"""DraveSpellenkast - Lingo: raad het woord van 5 letters. De eerste letter krijg je.
Groen = goede letter op de goede plek, geel = zit erin maar op een andere plek.
Alleen oefenen, om de beurt tegen de computer, of online tegen elkaar (om de beurt raden op hetzelfde woord).
Copyright (C) 2026 Dravenlock (Roger & Claudio). GNU GPL v3.0."""
import random
import time

import pygame

UI = None          # wordt door main.py gezet

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
POGINGEN = 6
GROEN_L = (63, 166, 107)
GEEL_L = (226, 180, 60)
GRIJS_L = (70, 64, 92)

WOORDEN_NL = """
AARDE ADRES AGENT ALARM APPEL AVOND BAKEN BALIE BANAAN BEKER BEURS BLAAS BLOED BLOEM BOCHT BOMEN BOORD BOTER BRAND
BREED BRIEF BROEK BROOD BRUID BUREN BURGER CAMPER DAKEN DALEN DAMES DEKEN DELEN DIEET DIKTE DORST DRAAK DRAAI DROOM
DRUIF EGELS EIKEN ENKEL FABEL FEEST FIETS FLUIT FRUIT GANZEN GEBED GEDOE GEITEN GELUK GEVEL GLANS GRAAN GROEN GROND
HAKEN HAMER HAVEN HEKEL HEMEL HOOFD HOTEL HUMOR JAREN JONGE KAART KABEL KAMER KAARS KASTEN KEVER KLEUR KLOMP KNOOP
KOFFIE KOKEN KOMMA KONIJN KOORD KRAAI KRANT KROON KRUIK KUSSEN LAARS LACHT LADEN LAMPEN LEPEL LEVEN LICHT LIJST LINKS
LUCHT MAAND MAKER MANEN MEREL METER MODEL MOLEN MUREN NACHT NAMEN NEVEL OCEAAN OGEN ONWEER OOGST OPERA ORGEL OUDER
PAARD PADEN PAKJE PALEN PAREL PASTA PEKEL PIANO PLAAT PLANT PLEIN POORT POTEN PRIJS PRINS RADIO RAMEN REGEN REIGER
RIDDER RIVIER ROBOT ROMAN RONDE ROZEN SALON SCHAT SCHIP SCHOT SLANG SLOOT SMAAK SNEEUW SPOOR STAAF STEEN STERK STOEL
STORM STRAND SUIKER TAFEL TAKEN TANTE TAART TEGEL TENEN TIJGER TOREN TRAAN TREIN TROMP TULPEN VADER VAREN VELDEN VEREN
VIOOL VISSEN VLAAG VLOER VOGEL VONDST WAGEN WAKEN WATER WEKER WERELD WOLKEN WORST ZADEL ZAKEN ZEBRA ZEGEL ZEKER ZOMER
ZONEN ZUSTER BEVER BLIND BOKAAL BRUIN DADEL DUNNE FAKIR GRAPPA HEKEL HOMMEL JUWEEL KABAAL KAMEEL KASSA KETEL KIKKER
KOGEL KOPJE KORST KREEFT LAKEN LATTE LEEUW LOKET LOTUS MAGIE MANGO MANTEL METAAL MOTOR MUNTEN NOOIT ORANJE PAKKET
PALET PANDA PLOEG POLKA POSTER PUREE RACKET RAKET RAMSJ ROGGE ROLLEN SABEL SALSA SAUNA SCHAAL SFEER SIGAAR SNOEP
SOKKEN SPEER SPIEGEL STAAL STAND STOEP STOOM STOUT STRIK SUPER TAKJE TAPIJT TEDER TENTEN TONEEL TOVER TROTS TUINEN
UITJE VAATJE VAZEN VEZEL VILLA VISIE VLIEG VLOED VOETEN VOORN VRUCHT WALVIS WAPEN WINTER WOEDE ZALM ZWAAN ZWART ZWEET
ZEEUW BOVEN ONDER ACHTER BINNEN BUITEN KLEIN GROOT LANGE KORTE WITTE
"""

WOORDEN_EN = """
APPLE BEACH BREAD BRICK CANDY CHAIR CHALK CHEST CLOUD CLOCK CROWN DANCE DREAM DRINK EAGLE EARTH FEAST FIELD FLAME FLOOR
FRUIT GHOST GIANT GLASS GRAPE GRASS HEART HORSE HOUSE JUICE KNIFE LEMON LIGHT MAGIC MONEY MOUSE MUSIC NIGHT OCEAN PAINT
PAPER PEACH PIANO PLANT PLATE QUEEN RADIO RIVER ROBOT ROUND SCARF SHEEP SHELL SHIRT SMILE SNAKE SPOON STONE STORM SUGAR
TABLE TIGER TOAST TOWER TRAIN TRUCK WATER WHALE WHEEL WORLD YACHT ZEBRA BRAVE CLEAN DREAD FAIRY FROST GLOVE HONEY
JELLY KNOCK LEMON MAPLE NOBLE OLIVE PEARL QUILT RAVEN SALAD SPICE TULIP UNCLE VOICE WAGON YOUTH CABIN DRAKE EMBER
FORGE GLADE HAVEN IVORY JEWEL KNELT LUNAR MOTOR NERVE ORBIT PRISM QUEST RIDGE SPARK THORN UNITY VAPOR WOVEN
"""


def lijst(tekst):
    gezien, uit = set(), []
    for w in tekst.split():
        w = w.strip().upper()
        if len(w) == 5 and all(c in LETTERS for c in w) and w not in gezien:
            gezien.add(w)
            uit.append(w)
    return uit


TX = {
    "lingo": ("Lingo", "Lingo"),
    "typ": ("Typ een woord van 5 letters en druk Enter.", "Type a 5-letter word and press Enter."),
    "kort": ("Het woord moet 5 letters hebben.", "The word must have 5 letters."),
    "begin_met": ("Het woord moet met een %s beginnen.", "The word must start with %s."),
    "goed_woord": ("Goed! Het woord was %s.", "Right! The word was %s."),
    "niet_geraden": ("Niet geraden. Het woord was %s.", "Not guessed. The word was %s."),
    "comp_raadt": ("De computer raadt...", "The computer is guessing..."),
    "jouw_beurt_l": ("Jouw beurt om te raden.", "Your turn to guess."),
    "uitleg_kleur": ("Groen = goede plek  ·  Geel = zit erin, andere plek  ·  Grijs = zit er niet in",
                     "Green = right place  ·  Yellow = in the word, other place  ·  Grey = not in it"),
    "punten": ("Punten: %d", "Points: %d"),
    "reeks": ("Op rij goed: %d  ·  Beste: %d", "In a row: %d  ·  Best: %d"),
    "tip_lingo": ("Tip: probeer %s", "Tip: try %s"),
    "toetsen_lingo": ("Typ letters  ·  Enter = raden  ·  Backspace = wissen  ·  Ctrl+T = tip  ·  Esc = menu",
                      "Type letters  ·  Enter = guess  ·  Backspace = delete  ·  Ctrl+T = tip  ·  Esc = menu"),
}


def T(k):
    if k in TX:
        v = TX[k]
        return v[0] if UI.TAAL == "nl" else v[1]
    return UI.T(k)


def woorden():
    return lijst(WOORDEN_NL if UI.TAAL == "nl" else WOORDEN_EN)


def kleuren(gok, woord):
    """Per letter: 2 = groen (goede plek), 1 = geel (zit erin), 0 = grijs. Dubbele letters netjes geteld."""
    uit = [0] * 5
    over = {}
    for i in range(5):
        if gok[i] == woord[i]:
            uit[i] = 2
        else:
            over[woord[i]] = over.get(woord[i], 0) + 1
    for i in range(5):
        if uit[i] == 0 and over.get(gok[i], 0) > 0:
            uit[i] = 1
            over[gok[i]] -= 1
    return uit


def past(kandidaat, rijen):
    return all(kleuren(g, kandidaat) == k for g, k in rijen)


def comp_gok(lijst_, eerste, rijen, niveau):
    """De computer kiest een woord dat past bij wat er al op het bord staat (makkelijk: let niet altijd op)."""
    goed = [w for w in lijst_ if w[0] == eerste and past(w, rijen)]
    if niveau == 1 and random.random() < 0.5 or not goed:
        alle = [w for w in lijst_ if w[0] == eerste and w not in [g for g, _ in rijen]]
        return random.choice(alle or goed or lijst_)
    if niveau == 2 and random.random() < 0.2:
        half = [w for w in lijst_ if w[0] == eerste and sum(1 for g, k in rijen if kleuren(g, w) == k) >= len(rijen) - 1]
        return random.choice(half or goed)
    return random.choice(goed)


# ------------------------------------------------------------------ het spel
class Lingo:
    def __init__(self, app, niveau):
        self.app = app
        self.niveau = niveau            # 0 = alleen oefenen, 1-3 = om de beurt tegen de computer
        self.knoppen = []
        self.score = [0, 0]
        self.reeks = 0
        self.beste = 0
        self.lijst = woorden()
        self.begint = 0
        self.nieuw_potje()

    def naam(self, sp):
        return UI.T("jij") if sp == 0 else UI.T("computer")

    def nieuw_potje(self, woord=None):
        self.woord = woord or random.choice(self.lijst)
        self.rijen = []                 # [(gok, kleuren, wie)]
        self.invoer = self.woord[0]
        self.klaar = False
        self.gewonnen_door = None
        self.melding = ""
        self.beurt = self.begint if self.niveau else 0
        self.begint = 1 - self.begint
        self.comp_t = time.time() + 1.2
        self.onthul = None              # (rij, starttijd) voor het omdraai-effect
        self.schud = 0.0

    def mijn_beurt(self):
        return not self.klaar and self.beurt == 0

    def letter_staat(self):
        staat = {}
        for g, k, _ in self.rijen:
            for c, s in zip(g, k):
                staat[c] = max(staat.get(c, -1), s)
        return staat

    def typ(self, c):
        if not self.mijn_beurt():
            return
        if len(self.invoer) < 5:
            self.invoer += c
            self.app.geluid.speel("klik")

    def wis(self):
        if self.mijn_beurt() and len(self.invoer) > 1:
            self.invoer = self.invoer[:-1]

    def raad(self):
        if not self.mijn_beurt():
            return
        gok = self.invoer
        if len(gok) != 5:
            self.melding = T("kort")
            self.schud = 1.0
            self.app.geluid.speel("fout")
            return
        if gok[0] != self.woord[0]:
            self.melding = T("begin_met") % self.woord[0]
            self.schud = 1.0
            self.app.geluid.speel("fout")
            return
        self.leg_neer(gok, 0)

    def leg_neer(self, gok, wie):
        k = kleuren(gok, self.woord)
        self.rijen.append((gok, k, wie))
        self.onthul = (len(self.rijen) - 1, time.time())
        self.melding = ""
        self.invoer = self.woord[0]
        if k == [2] * 5:
            self.klaar = True
            self.gewonnen_door = wie
            self.melding = T("goed_woord") % self.woord
            if self.niveau:
                self.score[wie] += 1
            else:
                self.score[0] += 10 * (POGINGEN + 1 - len(self.rijen))
                self.reeks += 1
                self.beste = max(self.beste, self.reeks)
            self.app.geluid.speel("win" if wie == 0 else "verlies")
            return
        self.app.geluid.speel("zet")
        if len(self.rijen) >= POGINGEN:
            self.klaar = True
            self.melding = T("niet_geraden") % self.woord
            if not self.niveau:
                self.reeks = 0
            self.app.geluid.speel("verlies")
            return
        if self.niveau:
            self.beurt = 1 - self.beurt
            self.comp_t = time.time() + 1.6

    def update(self):
        self.schud = max(0.0, self.schud - 0.05)
        if self.klaar or not self.niveau or self.beurt != 1:
            return
        if time.time() >= self.comp_t:
            gok = comp_gok(self.lijst, self.woord[0], [(g, k) for g, k, _ in self.rijen], self.niveau)
            self.leg_neer(gok, 1)

    def geef_tip(self):
        if not self.mijn_beurt():
            return
        goed = [w for w in self.lijst if w[0] == self.woord[0] and past(w, [(g, k) for g, k, _ in self.rijen])]
        if goed:
            w = random.choice(goed)
            self.melding = T("tip_lingo") % w
            self.app.geluid.speel("goed")

    # ---------- invoer
    def klik(self, pos):
        pass

    def toets(self, e):
        if e.key == pygame.K_ESCAPE:
            self.app.naar_menu()
        elif self.klaar and e.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
            self.nieuw_potje()
        elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.raad()
        elif e.key == pygame.K_BACKSPACE:
            self.wis()
        elif e.key == pygame.K_t and e.mod & pygame.KMOD_CTRL:
            self.geef_tip()
        elif e.unicode and len(e.unicode) == 1 and e.unicode.upper() in LETTERS:
            self.typ(e.unicode.upper())

    # ---------- tekenen
    def teken_rooster(self, d):
        vak, gap = 78, 10
        x0 = 150
        y0 = 100
        for r in range(POGINGEN):
            for c in range(5):
                x = x0 + c * (vak + gap)
                y = y0 + r * (vak + gap)
                if r < len(self.rijen):
                    g, k, wie = self.rijen[r]
                    vertraging = 0
                    if self.onthul and self.onthul[0] == r:
                        vertraging = (time.time() - self.onthul[1]) - c * 0.12
                        if vertraging < 0:
                            pygame.draw.rect(d, UI.VAK, (x, y, vak, vak), border_radius=10)
                            pygame.draw.rect(d, UI.RAND, (x, y, vak, vak), 3, border_radius=10)
                            UI.tekst(d, g[c], 44, UI.TEKST, (x + vak // 2, y + vak // 2), mid=True)
                            continue
                    kl = (GRIJS_L, GEEL_L, GROEN_L)[k[c]]
                    if k[c] == 1:
                        pygame.draw.rect(d, UI.VAK, (x, y, vak, vak), border_radius=10)
                        pygame.draw.circle(d, kl, (x + vak // 2, y + vak // 2), vak // 2 - 4)
                    else:
                        pygame.draw.rect(d, kl, (x, y, vak, vak), border_radius=10)
                    UI.tekst(d, g[c], 44, (255, 255, 255), (x + vak // 2, y + vak // 2), mid=True)
                    if self.niveau and c == 0:
                        kl_w = UI.ACCENT if wie == 0 else UI.ZACHT
                        UI.tekst(d, self.naam(wie), 16, kl_w, (x - 8, y + vak // 2), mid=False, rechts=True)
                elif r == len(self.rijen) and not self.klaar:
                    dx = int(10 * self.schud * (1 if int(self.schud * 20) % 2 else -1))
                    pygame.draw.rect(d, (44, 38, 64), (x + dx, y, vak, vak), border_radius=10)
                    pygame.draw.rect(d, UI.GOUD if self.mijn_beurt() else UI.RAND, (x + dx, y, vak, vak), 3, border_radius=10)
                    tekst = self.invoer if self.mijn_beurt() else self.woord[0]
                    if c < len(tekst):
                        UI.tekst(d, tekst[c], 44, UI.TEKST, (x + dx + vak // 2, y + vak // 2), mid=True)
                    elif c == len(tekst) and self.mijn_beurt() and (pygame.time.get_ticks() // 500) % 2 == 0:
                        pygame.draw.line(d, UI.GOUD, (x + 20, y + vak - 16), (x + vak - 20, y + vak - 16), 4)
                else:
                    pygame.draw.rect(d, UI.VAK, (x, y, vak, vak), border_radius=10)
                    pygame.draw.rect(d, UI.RAND, (x, y, vak, vak), 2, border_radius=10)
        if self.klaar:
            for c in range(5):                                      # het goede woord eronder
                x = x0 + c * (vak + gap)
                y = y0 + POGINGEN * (vak + gap) + 6
                UI.tekst(d, self.woord[c], 30, UI.GOUD, (x + vak // 2, y + 14), mid=True)

    def teken_toetsen(self, d, muis):
        staat = self.letter_staat()
        knoppen = []
        rijen = ("QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM")
        for r, rij in enumerate(rijen):
            for i, c in enumerate(rij):
                x = 640 + i * 58 + r * 26
                y = 330 + r * 72
                s = staat.get(c, -1)
                kl = {2: GROEN_L, 1: GEEL_L, 0: (50, 44, 66)}.get(s, UI.VAK)
                knoppen.append(UI.Knop((x, y, 52, 64), c, lambda c=c: self.typ(c), kl, 26, aan=True))
        knoppen.append(UI.Knop((640, 546, 170, 64), "Enter", self.raad, UI.GROEN, 24, aan=self.mijn_beurt()))
        knoppen.append(UI.Knop((825, 546, 150, 64), "←", self.wis, UI.VAK, 30, aan=self.mijn_beurt()))
        return knoppen

    def teken(self, d, muis):
        d.fill(UI.ACHTER)
        UI.tekst(d, T("lingo"), 40, UI.ACCENT, (60, 20))
        self.teken_rooster(d)
        px = 640
        if self.niveau:
            for i, sp in enumerate((0, 1)):
                UI.tekst(d, "%s: %d" % (self.naam(sp), self.score[sp]), 28, UI.GOUD if sp == 0 else UI.TEKST, (px + i * 310, 100))
                if not self.klaar and self.beurt == sp:
                    pygame.draw.rect(d, UI.ACCENT, (px - 12 + i * 310, 90, 290, 52), 3, border_radius=12)
        else:
            UI.tekst(d, T("punten") % self.score[0], 28, UI.GOUD, (px, 100))
            UI.tekst(d, T("reeks") % (self.reeks, self.beste), 22, UI.ZACHT, (px, 140), vet=False)
        if self.klaar:
            regel = self.melding
            kl = UI.GROEN if self.gewonnen_door == 0 else UI.ROOD if self.gewonnen_door is None else UI.GOUD
        elif self.niveau and self.beurt == 1:
            regel, kl = T("comp_raadt"), UI.TEKST
        else:
            regel = self.melding or (T("jouw_beurt_l") + " " + T("typ") if self.niveau else T("typ"))
            kl = UI.GOUD if self.melding else UI.TEKST
        for i, stuk in enumerate(UI.Backgammon._knip(None, regel, 22, UI.W - px - 40)[:3]):
            UI.tekst(d, stuk, 22, kl, (px, 190 + i * 30))
        if self.app.hulp:
            for i, stuk in enumerate(UI.Backgammon._knip(None, T("uitleg_kleur"), 17, UI.W - px - 40)[:2]):
                UI.tekst(d, stuk, 17, UI.ZACHT, (px, 286 + i * 22), vet=False)
        self.knoppen = self.teken_toetsen(d, muis)
        y = 640
        if self.klaar:
            self.knoppen.append(UI.Knop((px, y, 300, 64), UI.T("nog"), self.nieuw_potje, UI.GROEN, 24))
        else:
            self.knoppen.append(UI.Knop((px, y, 120, 64), UI.T("tip"), self.geef_tip, UI.GOUD, 24, aan=self.mijn_beurt() and self.tip_mag()))
            self.knoppen.append(UI.Knop((px + 130, y, 180, 64), "%s: %s" % (UI.T("hulp"), UI.T("aan") if self.app.hulp else UI.T("uitm")),
                                        self.app.wissel_hulp, UI.VAK, 20))
        self.knoppen.append(UI.Knop((px + 320, y, 140, 64), UI.T("menu"), self.app.naar_menu, UI.VAK, 24))
        self.knoppen.append(UI.Knop((px + 470, y, 150, 64), UI.T("regels"), lambda: setattr(self.app, "toon_regels", True), UI.VAK, 20))
        for k in self.knoppen:
            k.teken(d, muis)
        UI.tekst(d, T("toetsen_lingo"), 16, UI.ZACHT, (60, UI.H - 30), vet=False)

    def tip_mag(self):
        return True


# ------------------------------------------------------------------ online: om de beurt raden op hetzelfde woord
class OnlineLingo(Lingo):
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
        Lingo.__init__(self, app, 2)
        self.woord = "....."
        self.lijn = UI.online.Lijn(adres, code, {"t": "hallo", "spel": "lingo", "naam": naam, "token": token}, pad="zet/kamer")

    def naam(self, sp):
        """sp: 0 = ik, 1 = de ander (zo werkt het tekenen van Lingo)."""
        if sp == 0:
            return UI.T("jij")
        return self.ander or UI.T("tegenspeler")

    def tip_mag(self):
        return False

    def nieuw_potje(self, woord=None):
        if getattr(self, "lijn", None) is not None:
            self.lijn.stuur({"t": "nieuw"})
            self.app.geluid.speel("klik")
            return
        Lingo.nieuw_potje(self, woord)

    def mijn_beurt(self):
        return self.fase == "spel" and not self.klaar and self.beurt == 0

    def leg_neer(self, gok, wie):
        if wie == 0:                                  # mijn eigen gok: eerst naar de server
            k = kleuren(gok, self.woord)
            einde = None
            if k == [2] * 5:
                einde = self.ik
            elif len(self.rijen) + 1 >= POGINGEN:
                einde = -1
            if not self.lijn.stuur({"t": "zet", "z": {"gok": gok}, "einde": einde}):
                self.status = UI.T("geen_server")
                return
            self.n_zetten += 1
        Lingo.leg_neer(self, gok, wie)
        if not self.klaar:
            self.beurt = 1 - wie

    def update(self):
        self.schud = max(0.0, self.schud - 0.05)
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
        sc = st.get("score", [0, 0])
        self.score = [sc[self.ik], sc[1 - self.ik]]
        self.ander = (st.get("ander") or {}).get("naam")
        self.verbonden = st.get("verbonden", [True, True])
        self.fase = st["fase"]
        if self.fase == "wachten":
            return
        lijst_z = st.get("zetten") or []
        if st.get("potje") == self.potje and len(lijst_z) < self.n_zetten:
            return
        if st.get("potje") != self.potje:
            self.potje = st.get("potje")
            woorden_ = self.lijst
            woord = woorden_[int(st.get("zaad") or 0) % len(woorden_)]
            Lingo.nieuw_potje(self, woord)
            self.n_zetten = 0
            self.einde_gezien = False
            self.beurt = 0 if st.get("eerste", 0) == self.ik else 1
        for d in lijst_z[self.n_zetten:]:
            gok = str((d.get("z") or {}).get("gok", ""))[:5].upper()
            self.n_zetten += 1
            if len(gok) == 5:
                Lingo.leg_neer(self, gok, 0 if d.get("sp") == self.ik else 1)
                if not self.klaar:
                    self.beurt = 0 if d.get("sp") != self.ik else 1
        self.score = [sc[self.ik], sc[1 - self.ik]]       # de server telt de punten (na het naspelen)
        if self.fase == "einde":
            self.klaar = True
            w = st.get("winnaar")
            self.gewonnen_door = None if w == -1 else (0 if w == self.ik else 1)
            if not self.einde_gezien:
                self.einde_gezien = True
                self.melding = (T("goed_woord") if w != -1 else T("niet_geraden")) % self.woord
        else:
            self.beurt = 0 if st["beurt"] == self.ik else 1

    def teken(self, d, muis):
        Lingo.teken(self, d, muis)
        UI.tekst(d, UI.T("kamer") % self.code, 20, UI.ACCENT, (240, 34))
        if self.status:
            UI.tekst(d, self.status, 20, UI.ROOD, (640, 160))
        elif self.ik is not None and self.ander and not self.verbonden[1 - self.ik]:
            UI.tekst(d, UI.T("ander_weg") % self.ander, 20, UI.GOUD, (640, 160))
        if self.fase == "wachten":
            pygame.draw.rect(d, UI.ACHTER, (630, 180, 640, 100))
            UI.tekst(d, UI.T("wacht_ander") % self.code, 22, UI.TEKST, (640, 190))
            UI.tekst(d, self.code, 48, UI.GOUD, (640, 224))

    def stop(self):
        if self.lijn:
            self.lijn.stop()
