# -*- coding: utf-8 -*-
"""DraveSpellenkast - Wie ben ik? (tegen de computer; online volgt).
24 zelfgetekende figuurtjes. Kies een ja/nee-vraag uit de lijst, klap om wie het niet kan zijn, en raad wie de ander heeft.
Copyright (C) 2026 Dravenlock (Roger & Claudio). GNU GPL v3.0."""
import random
import time

import pygame

UI = None          # wordt door main.py gezet

# ------------------------------------------------------------------ de figuurtjes
HAAR = {"zwart": (40, 34, 40), "bruin": (110, 70, 40), "blond": (232, 196, 110), "rood": (200, 90, 40), "grijs": (180, 180, 186)}
TRUI = {"rood": (200, 60, 70), "blauw": (60, 110, 210), "groen": (60, 160, 90), "geel": (236, 196, 60), "paars": (140, 90, 200)}
HUID = [(250, 214, 180), (236, 190, 150), (200, 150, 110), (150, 100, 70), (110, 74, 52)]
JONGENS = ["Bram", "Cor", "Daan", "Gijs", "Joop", "Kees", "Olaf", "Piet", "Ruud", "Tim", "Wim", "Bas", "Henk", "Jan", "Sem", "Luuk"]
MEISJES = ["Anna", "Eva", "Fenna", "Hanna", "Ilse", "Lotte", "Mila", "Noor", "Sanne", "Uma", "Vera", "Yara", "Zoë", "Lisa", "Roos", "Fleur"]

# vragen: (sleutel, tekst NL, tekst EN, test)
VRAGEN = [
    ("bril", "Heeft je figuur een bril?", "Does your person wear glasses?", lambda f: f["bril"]),
    ("hoed", "Draagt je figuur een hoed of pet?", "Does your person wear a hat or cap?", lambda f: f["hoed"] is not None),
    ("baard", "Heeft je figuur een baard?", "Does your person have a beard?", lambda f: f["baard"]),
    ("snor", "Heeft je figuur een snor?", "Does your person have a moustache?", lambda f: f["snor"]),
    ("kaal", "Is je figuur kaal?", "Is your person bald?", lambda f: f["haar"] == "kaal"),
    ("lang", "Heeft je figuur lang haar?", "Does your person have long hair?", lambda f: f["haar"] == "lang"),
    ("krul", "Heeft je figuur krullen?", "Does your person have curly hair?", lambda f: f["haar"] == "krul"),
    ("h_zwart", "Is het haar zwart?", "Is the hair black?", lambda f: f["haar"] != "kaal" and f["haarkleur"] == "zwart"),
    ("h_bruin", "Is het haar bruin?", "Is the hair brown?", lambda f: f["haar"] != "kaal" and f["haarkleur"] == "bruin"),
    ("h_blond", "Is het haar blond?", "Is the hair blond?", lambda f: f["haar"] != "kaal" and f["haarkleur"] == "blond"),
    ("h_rood", "Is het haar rood?", "Is the hair red?", lambda f: f["haar"] != "kaal" and f["haarkleur"] == "rood"),
    ("h_grijs", "Is het haar grijs?", "Is the hair grey?", lambda f: f["haar"] != "kaal" and f["haarkleur"] == "grijs"),
    ("oorbel", "Draagt je figuur oorbellen?", "Does your person wear earrings?", lambda f: f["oorbel"]),
    ("sjaal", "Draagt je figuur een sjaal?", "Does your person wear a scarf?", lambda f: f["sjaal"]),
    ("lach", "Lacht je figuur met open mond?", "Is your person laughing (mouth open)?", lambda f: f["lach"]),
    ("t_rood", "Is de trui rood?", "Is the sweater red?", lambda f: f["trui"] == "rood"),
    ("t_blauw", "Is de trui blauw?", "Is the sweater blue?", lambda f: f["trui"] == "blauw"),
    ("t_groen", "Is de trui groen?", "Is the sweater green?", lambda f: f["trui"] == "groen"),
    ("t_geel", "Is de trui geel?", "Is the sweater yellow?", lambda f: f["trui"] == "geel"),
    ("t_paars", "Is de trui paars?", "Is the sweater purple?", lambda f: f["trui"] == "paars"),
]


def maak_figuren():
    """24 vaste figuurtjes (altijd dezelfde), elk net anders."""
    rnd = random.Random(2411)
    figs = []
    gezien = set()
    i = 0
    while len(figs) < 24:
        f = {
            "naam": "",
            "huid": HUID[rnd.randrange(len(HUID))],
            "haar": rnd.choice(["kort", "kort", "lang", "lang", "krul", "kaal"]),
            "haarkleur": rnd.choice(list(HAAR)),
            "bril": rnd.random() < 0.3,
            "hoed": rnd.choice([None, None, None, "hoed", "pet"]),
            "baard": rnd.random() < 0.2,
            "snor": rnd.random() < 0.2,
            "oorbel": rnd.random() < 0.25,
            "sjaal": rnd.random() < 0.25,
            "lach": rnd.random() < 0.4,
            "trui": rnd.choice(list(TRUI)),
        }
        if f["haar"] == "kaal":
            f["hoed"] = None if rnd.random() < 0.6 else f["hoed"]
        sleutel = tuple(v(f) for _, _, _, v in VRAGEN)
        i += 1
        if sleutel in gezien:
            continue
        gezien.add(sleutel)
        figs.append(f)
    # namen die passen: met baard of snor een jongensnaam, lang haar of oorbellen een meisjesnaam
    jongens, meisjes = list(JONGENS), list(MEISJES)
    rnd.shuffle(jongens)
    rnd.shuffle(meisjes)
    for n, f in enumerate(figs):
        if f["baard"] or f["snor"] or f["haar"] == "kaal":
            f["naam"] = jongens.pop()
        elif f["haar"] == "lang" or f["oorbel"]:
            f["naam"] = meisjes.pop()
        else:
            f["naam"] = (jongens if n % 2 else meisjes).pop()
    figs.sort(key=lambda f: f["naam"])                       # op alfabet, makkelijk zoeken
    return figs


FIGUREN = maak_figuren()

TX = {
    "wie": ("Wie ben ik?", "Guess who?"),
    "jouw_fig": ("Jouw figuur", "Your person"),
    "stel": ("Jouw beurt: kies een vraag", "Your turn: pick a question"),
    "comp_vraagt": ("De computer vraagt:", "The computer asks:"),
    "ja": ("Ja", "Yes"), "nee": ("Nee", "No"),
    "antwoord": ("%s  ->  %s", "%s  ->  %s"),
    "klap": ("Klap om wie het niet kan zijn (klik op de kaartjes). Klaar? Klik 'Klaar'.", "Flip down who it can't be (click the cards). Done? Click 'Done'."),
    "raad": ("Raden!", "Guess!"), "raad_uitleg": ("Klik op wie je denkt dat het is.", "Click who you think it is."),
    "annuleer": ("Toch niet", "Cancel"),
    "comp_raadt": ("De computer raadt: is het %s?", "The computer guesses: is it %s?"),
    "goed_geraden": ("Goed geraden! Het was %s.", "Correct! It was %s."),
    "fout_geraden": ("Helaas, het was %s.", "Sorry, it was %s."),
    "comp_over": ("De computer twijfelt nog tussen %d figuren.", "The computer still has %d people left."),
    "vragen": ("Vragen", "Questions"),
    "toetsen_wie": ("Klik een vraag  ·  klik kaartjes om om te klappen  ·  Raden! om te raden  ·  Esc = menu",
                    "Click a question  ·  click cards to flip  ·  Guess! to guess  ·  Esc = menu"),
}


def T(k):
    if k in TX:
        v = TX[k]
        return v[0] if UI.TAAL == "nl" else v[1]
    return UI.T(k)


def vraag_tekst(i):
    return VRAGEN[i][1] if UI.TAAL == "nl" else VRAGEN[i][2]


def beste_vraag(kandidaten, gesteld, niveau):
    """Niveau 3: de vraag die de groep het eerlijkst in tweeën deelt. 2: een goede uit de top. 1: zomaar een vraag."""
    opties = []
    for i, (_, _, _, test) in enumerate(VRAGEN):
        if i in gesteld:
            continue
        ja = sum(1 for f in kandidaten if test(FIGUREN[f]))
        if 0 < ja < len(kandidaten):
            opties.append((abs(len(kandidaten) / 2 - ja), i))
    if not opties:
        return None
    opties.sort()
    if niveau == 1:
        return random.choice(opties)[1]
    if niveau == 2:
        return random.choice(opties[:4])[1]
    return opties[0][1]


# ------------------------------------------------------------------ tekenen van een figuurtje
def teken_figuur(d, f, r, dicht=False, licht=False):
    """Kaartje met een getekend figuurtje in rechthoek r."""
    pygame.draw.rect(d, (236, 230, 246) if not dicht else (70, 62, 96), r, border_radius=12)
    pygame.draw.rect(d, UI.GOUD if licht else UI.RAND, r, 4 if licht else 3, border_radius=12)
    if dicht:
        pygame.draw.line(d, (110, 100, 140), (r.x + 16, r.y + 16), (r.right - 16, r.bottom - 40), 4)
        pygame.draw.line(d, (110, 100, 140), (r.right - 16, r.y + 16), (r.x + 16, r.bottom - 40), 4)
        UI.tekst(d, f["naam"], max(14, r.w // 7), (150, 140, 180), (r.centerx, r.bottom - 18), mid=True)
        return
    s = r.w / 120.0
    cx, cy = r.centerx, r.y + int(62 * s)
    z = lambda v: int(v * s)
    # trui
    pygame.draw.ellipse(d, TRUI[f["trui"]], (cx - z(44), cy + z(36), z(88), z(60)))
    if f["sjaal"]:
        pygame.draw.rect(d, (230, 80, 80) if f["trui"] != "rood" else (240, 240, 240), (cx - z(26), cy + z(30), z(52), z(12)), border_radius=z(6))
        for k in range(3):
            pygame.draw.line(d, (255, 255, 255), (cx - z(18) + k * z(16), cy + z(31)), (cx - z(18) + k * z(16), cy + z(41)), 2)
    # haar achter (lang)
    hk = HAAR[f["haarkleur"]]
    if f["haar"] == "lang":                                  # lang haar: bovenop en langs de zijkanten tot de schouders
        pygame.draw.ellipse(d, hk, (cx - z(35), cy - z(40), z(70), z(56)))
        pygame.draw.rect(d, hk, (cx - z(37), cy - z(14), z(16), z(54)), border_radius=z(7))
        pygame.draw.rect(d, hk, (cx + z(21), cy - z(14), z(16), z(54)), border_radius=z(7))
    # hoofd
    pygame.draw.ellipse(d, f["huid"], (cx - z(28), cy - z(32), z(56), z(66)))
    # haar voor
    if f["haar"] in ("kort", "lang"):
        pygame.draw.arc(d, hk, (cx - z(30), cy - z(36), z(60), z(50)), 0.1, 3.05, z(14))
    elif f["haar"] == "krul":
        for k in range(7):
            pygame.draw.circle(d, hk, (cx - z(27) + k * z(9), cy - z(26) + (k % 2) * z(4)), z(10))
    # oren + oorbellen
    for kant in (-1, 1):
        pygame.draw.circle(d, f["huid"], (cx + kant * z(28), cy + z(2)), z(7))
        if f["oorbel"]:
            pygame.draw.circle(d, UI.GOUD, (cx + kant * z(29), cy + z(12)), z(4))
    # ogen
    for kant in (-1, 1):
        pygame.draw.circle(d, (255, 255, 255), (cx + kant * z(11), cy - z(2)), z(6))
        pygame.draw.circle(d, (40, 40, 60), (cx + kant * z(11), cy - z(1)), z(3))
    if f["bril"]:
        for kant in (-1, 1):
            pygame.draw.circle(d, (30, 30, 40), (cx + kant * z(11), cy - z(2)), z(10), 3)
        pygame.draw.line(d, (30, 30, 40), (cx - z(2), cy - z(3)), (cx + z(2), cy - z(3)), 3)
    # baard en snor
    if f["baard"]:
        pygame.draw.ellipse(d, HAAR[f["haarkleur"]] if f["haar"] != "kaal" else (110, 90, 80), (cx - z(24), cy + z(10), z(48), z(28)))
    if f["snor"]:
        pygame.draw.ellipse(d, HAAR[f["haarkleur"]] if f["haar"] != "kaal" else (90, 70, 60), (cx - z(13), cy + z(10), z(26), z(8)))
    # mond
    if f["lach"]:
        pygame.draw.ellipse(d, (150, 40, 50), (cx - z(9), cy + z(16), z(18), z(12)))
        pygame.draw.rect(d, (255, 255, 255), (cx - z(7), cy + z(16), z(14), z(4)))
    else:
        pygame.draw.arc(d, (150, 60, 60), (cx - z(10), cy + z(10), z(20), z(12)), 3.4, 6.0, 3)
    # hoed of pet
    if f["hoed"] == "hoed":
        pygame.draw.rect(d, (60, 50, 70), (cx - z(36), cy - z(30), z(72), z(8)), border_radius=z(4))
        pygame.draw.rect(d, (60, 50, 70), (cx - z(22), cy - z(56), z(44), z(30)), border_radius=z(6))
        pygame.draw.rect(d, UI.ROOD, (cx - z(22), cy - z(36), z(44), z(6)))
    elif f["hoed"] == "pet":
        pygame.draw.ellipse(d, (70, 120, 200), (cx - z(30), cy - z(46), z(60), z(32)))
        pygame.draw.rect(d, (70, 120, 200), (cx - z(4), cy - z(26), z(40), z(8)), border_radius=z(4))
    UI.tekst(d, f["naam"], max(14, r.w // 7), (40, 30, 60), (r.centerx, r.bottom - 18), mid=True)


# ------------------------------------------------------------------ het spel
KAART_W, KAART_H = 118, 148
ZICHT = 8                                    # zoveel vragen tegelijk in beeld (pijltjes of muiswiel voor meer)
BX, BY = 28, 96


class WieBenIk:
    def __init__(self, app, niveau):
        self.app = app
        self.niveau = niveau
        self.mij = 0
        self.knoppen = []
        self.score = [0, 0]
        self.begint = 0
        self.nieuw_potje()

    def naam(self, sp):
        return UI.T("jij") if sp == self.mij else UI.T("computer")

    def nieuw_potje(self):
        self.mijn_fig = random.randrange(24)                 # wie ik ben (de ander raadt dit)
        self.zijn_fig = random.randrange(24)                 # wie hij is (ik raad dit)
        self.dicht = set()                                   # mijn omgeklapte kaartjes
        self.gesteld = set()                                 # vragen die ik al stelde
        self.comp_kand = set(range(24))                      # wie de computer nog mogelijk vindt
        self.comp_gesteld = set()
        self.beurt = self.begint
        self.begint = 1 - self.begint
        self.fase = "vragen"                                 # vragen / klappen / raden / wacht
        self.laatste = None                                  # (vraag, antwoord) die ik kreeg
        self.comp_bericht = ""
        self.klaar = False
        self.uitslag = ""
        self.melding = ""
        self.wacht_tot = time.time() + 0.8
        self.scroll = 0

    # ---------- ik
    def stel(self, i):
        if self.klaar or self.beurt != self.mij or self.fase != "vragen":
            return
        ja = VRAGEN[i][3](FIGUREN[self.zijn_fig])
        self.gesteld.add(i)
        self.laatste = (i, ja)
        self.app.geluid.speel("goed" if ja else "klik")
        if self.app.hulp:                                    # hulp: vanzelf omklappen
            for k in range(24):
                if VRAGEN[i][3](FIGUREN[k]) != ja:
                    self.dicht.add(k)
        self.fase = "klappen"

    def klaar_met_klappen(self):
        if self.fase != "klappen":
            return
        self.fase = "vragen"
        self.beurt = 1 - self.mij
        self.wacht_tot = time.time() + 0.9

    def raad_modus(self):
        if self.klaar or self.beurt != self.mij:
            return
        self.fase = "raden" if self.fase != "raden" else "vragen"

    def raad(self, k):
        goed = k == self.zijn_fig
        self.klaar = True
        sp = self.mij if goed else 1 - self.mij
        self.score[sp] += 1
        self.uitslag = (T("goed_geraden") if goed else T("fout_geraden")) % FIGUREN[self.zijn_fig]["naam"]
        self.app.geluid.speel("win" if goed else "verlies")

    # ---------- de computer
    def update(self):
        if self.klaar or self.beurt == self.mij or time.time() < self.wacht_tot:
            return
        if len(self.comp_kand) == 1 or (self.niveau == 1 and len(self.comp_kand) <= 2 and random.random() < 0.5):
            k = random.choice(sorted(self.comp_kand))
            self.comp_bericht = T("comp_raadt") % FIGUREN[k]["naam"]
            self.klaar = True
            goed = k == self.mijn_fig
            sp = 1 - self.mij if goed else self.mij
            self.score[sp] += 1
            self.uitslag = (UI.T("wint") % self.naam(sp))
            self.app.geluid.speel("verlies" if goed else "win")
            return
        i = beste_vraag(self.comp_kand, self.comp_gesteld, self.niveau)
        if i is None:
            self.comp_kand = {self.mijn_fig}
            return
        self.comp_gesteld.add(i)
        ja = VRAGEN[i][3](FIGUREN[self.mijn_fig])           # eerlijk antwoord voor jou
        self.comp_kand = {k for k in self.comp_kand if VRAGEN[i][3](FIGUREN[k]) == ja}
        self.comp_bericht = "%s %s  ->  %s" % (T("comp_vraagt"), vraag_tekst(i), T("ja") if ja else T("nee"))
        self.app.geluid.speel("klik")
        self.beurt = self.mij
        self.fase = "vragen"

    # ---------- invoer
    def kaart_rect(self, k):
        return pygame.Rect(BX + (k % 6) * (KAART_W + 8), BY + (k // 6) * (KAART_H + 8), KAART_W, KAART_H)

    def klik(self, pos):
        if self.klaar:
            return
        for k in range(24):
            if self.kaart_rect(k).collidepoint(pos):
                if self.fase == "raden":
                    self.raad(k)
                elif self.beurt == self.mij:
                    self.dicht ^= {k}                         # omklappen (of terug)
                    self.app.geluid.speel("zet")
                return

    def toets(self, e):
        if e.key == pygame.K_ESCAPE:
            if self.fase == "raden":
                self.fase = "vragen"
            else:
                self.app.naar_menu()
        elif self.klaar and e.key in (pygame.K_SPACE, pygame.K_RETURN):
            self.nieuw_potje()
        elif self.fase == "klappen" and e.key in (pygame.K_SPACE, pygame.K_RETURN):
            self.klaar_met_klappen()

    def wiel(self, dy):
        self.scroll = max(0, min(len(VRAGEN) - ZICHT, self.scroll - dy))

    # ---------- tekenen
    def teken(self, d, muis):
        d.fill(UI.ACHTER)
        UI.tekst(d, T("wie"), 40, UI.ACCENT, (BX, 18))
        open_ = 24 - len(self.dicht)
        UI.tekst(d, "%d / 24" % open_, 22, UI.ZACHT, (BX + 6 * (KAART_W + 8) - 8, 34), rechts=True)
        for k in range(24):
            r = self.kaart_rect(k)
            licht = (self.fase == "raden" and r.collidepoint(muis) and k not in self.dicht) or (self.klaar and k == self.zijn_fig)
            teken_figuur(d, FIGUREN[k], r, dicht=k in self.dicht and not (self.klaar and k == self.zijn_fig), licht=licht)
        px = BX + 6 * (KAART_W + 8) + 16
        bw = UI.W - px - 20
        # mijn figuur
        r = pygame.Rect(px, 20, 96, 120)
        teken_figuur(d, FIGUREN[self.mijn_fig], r)
        UI.tekst(d, T("jouw_fig"), 22, UI.TEKST, (px + 110, 24))
        UI.tekst(d, FIGUREN[self.mijn_fig]["naam"], 30, UI.GOUD, (px + 110, 54))
        for sp in (0, 1):
            UI.tekst(d, "%s  %d" % (self.naam(sp), self.score[sp]), 18, UI.ZACHT, (px + 110, 96 + sp * 22), vet=False)
        self.knoppen = []
        y = 156
        regels = []
        if self.klaar:
            regels.append((self.uitslag, UI.GOUD))
        if self.comp_bericht:
            regels.append((self.comp_bericht, UI.TEKST))
        if self.laatste and not self.klaar:
            i, ja = self.laatste
            regels.append((T("antwoord") % (vraag_tekst(i), T("ja") if ja else T("nee")), UI.GOUD))
        for t, kl in regels:
            for stuk in UI.Backgammon._knip(None, t, 19, bw):
                UI.tekst(d, stuk, 19, kl, (px, y))
                y += 25
            y += 4
        y = max(y + 6, 250)
        if self.klaar:
            self.knoppen.append(UI.Knop((px, y + 10, bw, 64), UI.T("nog"), self.nieuw_potje, UI.GROEN, 24))
        elif self.beurt != self.mij and self.fase != "klappen":
            if hasattr(self, "lijn"):
                UI.tekst(d, T("hij_denkt") % self.naam(1 - self.mij), 22, UI.TEKST, (px, y))
            else:
                UI.tekst(d, UI.T("denkt"), 22, UI.TEKST, (px, y))
                UI.tekst(d, T("comp_over") % len(self.comp_kand), 18, UI.ZACHT, (px, y + 32), vet=False)
        elif self.fase == "klappen":
            for stuk in UI.Backgammon._knip(None, T("klap"), 19, bw):
                UI.tekst(d, stuk, 19, UI.TEKST, (px, y), vet=False)
                y += 25
            self.knoppen.append(UI.Knop((px, y + 10, bw, 64), UI.T("klaar"), self.klaar_met_klappen, UI.GROEN, 26))
        elif self.fase == "raden":
            for stuk in UI.Backgammon._knip(None, T("raad_uitleg"), 22, bw):
                UI.tekst(d, stuk, 22, UI.GOUD, (px, y))
                y += 30
            self.knoppen.append(UI.Knop((px, y + 10, bw, 60), T("annuleer"), self.raad_modus, UI.VAK, 22))
        else:
            UI.tekst(d, T("stel"), 20, UI.TEKST, (px, y))
            y += 32
            zicht = list(range(len(VRAGEN)))[self.scroll:self.scroll + ZICHT]
            for i in zicht:
                gedaan = i in self.gesteld
                tekstje = vraag_tekst(i)
                self.knoppen.append(UI.Knop((px, y, bw, 40), tekstje, lambda i=i: self.stel(i), UI.VAK, 18, aan=not gedaan))
                y += 44
            if len(VRAGEN) > ZICHT:
                self.knoppen.append(UI.Knop((px, y + 2, bw // 2 - 4, 34), "▲", lambda: self.wiel(3), UI.VAK, 18, aan=self.scroll > 0))
                self.knoppen.append(UI.Knop((px + bw // 2 + 4, y + 2, bw // 2 - 4, 34), "▼", lambda: self.wiel(-3), UI.VAK, 18,
                                            aan=self.scroll < len(VRAGEN) - ZICHT))
            self.knoppen.append(UI.Knop((px, 700, bw // 2 - 4, 56), T("raad"), self.raad_modus, UI.GOUD, 24))
        self.knoppen.append(UI.Knop((px + (bw // 2 + 4 if not self.klaar and self.beurt == self.mij and self.fase == "vragen" else 0), 700,
                                     bw // 2 - 4, 56), UI.T("menu"), self.app.naar_menu, UI.VAK, 20))
        for k in self.knoppen:
            k.teken(d, muis)
        UI.tekst(d, T("toetsen_wie"), 16, UI.ZACHT, (BX, UI.H - 24), vet=False)


# ------------------------------------------------------------------ online tegen elkaar
TX.update({
    "hij_vraagt": ("%s vraagt:", "%s asks:"),
    "hij_denkt": ("%s is aan de beurt...", "%s's turn..."),
    "hij_raadde": ("%s raadde: %s", "%s guessed: %s"),
})


class OnlineWie(WieBenIk):
    """Wie ben ik? op twee pc's. De server kiest de figuurtjes en beantwoordt de vragen eerlijk."""

    def __init__(self, app, adres, code, naam, token):
        self.lijn = None
        self.code = code
        self.ik = None
        self.ander = None
        self.verbonden = [False, False]
        self.status = UI.T("verbinden")
        self.zetnr = None
        self.server_fase = "wachten"
        self.log_gezien = 0
        self.einde_gezien = False
        WieBenIk.__init__(self, app, 0)
        self.lijn = UI.online.Lijn(adres, code, {"t": "hallo", "naam": naam, "token": token}, pad="wie/kamer")

    def naam(self, sp):
        if self.ik is None:
            return UI.T("speler%d" % (sp + 1))
        return UI.T("jij") if sp == self.ik else (self.ander or UI.T("tegenspeler"))

    def nieuw_potje(self):
        if self.lijn is not None:
            self.lijn.stuur({"t": "nieuw"})
            self.app.geluid.speel("klik")
            return
        WieBenIk.nieuw_potje(self)
        self.beurt = -1
        self.zijn_fig = None

    def stel(self, i):
        if self.klaar or self.beurt != self.mij or self.fase != "vragen" or i in self.gesteld:
            return
        if self.lijn.stuur({"t": "vraag", "i": int(i)}):
            self.gesteld.add(i)
            self.beurt = -1                              # tot de server antwoordt
        else:
            self.status = UI.T("geen_server")

    def klaar_met_klappen(self):
        if self.fase == "klappen":
            self.fase = "vragen"

    def raad(self, k):
        if self.lijn.stuur({"t": "raad", "k": int(k)}):
            self.fase = "vragen"
            self.beurt = -1
        else:
            self.status = UI.T("geen_server")

    def update(self):
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

    def pas_toe(self, st):
        self.ik = self.mij = st["ik"]
        self.score = list(st.get("score", [0, 0]))
        self.ander = (st.get("ander") or {}).get("naam")
        self.verbonden = st.get("verbonden", [True, True])
        f = st["fase"]
        nieuw = self.server_fase == "einde" and f == "spel"
        self.server_fase = f
        if f == "wachten":
            self.beurt = -1
            return
        if nieuw:                                        # volgend potje: alles terug
            WieBenIk.nieuw_potje(self)
            self.log_gezien = 0
            self.einde_gezien = False
        if st.get("mijn_geheim") is not None:
            self.mijn_fig = st["mijn_geheim"]
        log = st.get("log") or []
        for x in log[self.log_gezien:]:
            i, ja = x["i"], x["ja"]
            if x["door"] == self.ik:
                self.gesteld.add(i)
                self.laatste = (i, ja)
                self.app.geluid.speel("goed" if ja else "klik")
                if self.app.hulp:
                    for k in range(24):
                        if VRAGEN[i][3](FIGUREN[k]) != ja:
                            self.dicht.add(k)
                self.fase = "klappen"
            else:
                self.comp_bericht = "%s %s  ->  %s" % (T("hij_vraagt") % self.naam(1 - self.ik), vraag_tekst(i),
                                                       T("ja") if ja else T("nee"))
                self.app.geluid.speel("klik")
        self.log_gezien = len(log)
        self.beurt = st["beurt"]
        if f == "einde":
            self.klaar = True
            self.zijn_fig = st.get("zijn_geheim")
            g = st.get("geraden") or {}
            w = st.get("winnaar")
            wie = FIGUREN[g["k"]]["naam"] if "k" in g else "?"
            self.comp_bericht = T("hij_raadde") % (self.naam(g.get("door", 0)), wie)
            self.uitslag = UI.T("wint") % self.naam(w)
            if not self.einde_gezien:
                self.einde_gezien = True
                self.app.geluid.speel("win" if w == self.ik else "verlies")
        else:
            self.klaar = False

    def teken(self, d, muis):
        if self.zijn_fig is None:
            self.zijn_fig = -1                           # nog onbekend (pas aan het eind)
        WieBenIk.teken(self, d, muis)
        px = BX + 6 * (KAART_W + 8) + 16
        UI.tekst(d, UI.T("kamer") % self.code, 18, UI.ACCENT, (px + 260, 54))
        if self.status:
            UI.tekst(d, self.status, 18, UI.ROOD, (px, 668))
        elif self.ik is not None and self.ander and not self.verbonden[1 - self.ik]:
            UI.tekst(d, UI.T("ander_weg") % self.ander, 18, UI.GOUD, (px, 668))
        if self.server_fase == "wachten":
            UI.tekst(d, UI.T("wacht_ander") % self.code, 22, UI.GOUD, (px, 250))

    def stop(self):
        if self.lijn:
            self.lijn.stop()
