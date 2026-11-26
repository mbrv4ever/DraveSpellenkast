# -*- coding: utf-8 -*-
"""DraveSpellenkast - Galgje: raad het woord letter voor letter, voordat het poppetje hangt.
Tegen de computer (die kiest een woord) of online: de een bedenkt een woord, de ander raadt.
Copyright (C) 2026 Dravenlock (Roger & Claudio). GNU GPL v3.0."""
import random

import pygame

UI = None          # wordt door main.py gezet

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MAX_FOUT = 10      # galg in 10 stappen

WOORDEN_NL = {
    "dieren": "HOND KAT PAARD KOE GEIT SCHAAP VARKEN KONIJN HAMSTER CAVIA PAPEGAAI UIL ADELAAR ZWALUW MEREL KRAAI EEND ZWAAN "
              "VOS WOLF BEER DAS EGEL OTTER BEVER HERT REE EEKHOORN MUIS RAT OLIFANT GIRAFFE LEEUW TIJGER ZEBRA AAP NEUSHOORN "
              "KROKODIL SLANG SCHILDPAD KIKKER PADDENSTOEL VLINDER BIJ WESP MIER SPIN SLAK WALVIS DOLFIJN HAAI ZEEHOND PINGUIN",
    "eten": "BROOD KAAS BOTER MELK APPEL PEER BANAAN AARDBEI KERS DRUIF CITROEN SINAASAPPEL TOMAAT KOMKOMMER WORTEL UI "
            "AARDAPPEL SPRUITJES BROCCOLI PAPRIKA RIJST PASTA PIZZA SOEP STAMPPOT PANNENKOEK POFFERTJES STROOPWAFEL HAGELSLAG "
            "DROP CHOCOLADE KOEKJE TAART SLAGROOM KOFFIE THEE LIMONADE YOGHURT HONING JAM PINDAKAAS FRIKANDEL KROKET BITTERBAL",
    "huis": "STOEL TAFEL BANK KAST BED KUSSEN DEKEN LAMP SPIEGEL DEUR RAAM TRAP ZOLDER KELDER KEUKEN BADKAMER DOUCHE "
            "OVEN KOELKAST WASMACHINE STOFZUIGER BEZEM EMMER SCHAAR HAMER SCHROEVENDRAAIER BOOR TELEFOON COMPUTER TOETSENBORD "
            "TELEVISIE KLOK SLEUTEL GORDIJN KAARS VAAS SCHILDERIJ BOEKENKAST",
    "natuur": "BOOM BOS EIK BERK DEN WILG BEUK BLAD TAK WORTEL BLOEM TULP ROOS ZONNEBLOEM MADELIEFJE GRAS MOS VAREN "
              "RIVIER BEEK MEER ZEE STRAND DUIN BERG HEUVEL VALLEI WOLK REGEN SNEEUW HAGEL ONWEER BLIKSEM REGENBOOG ZON MAAN "
              "STER PLANEET KOMEET WIND STORM MIST IJS HERFST WINTER LENTE ZOMER",
    "dingen": "FIETS AUTO TREIN BUS VLIEGTUIG BOOT RAKET TRACTOR HELIKOPTER BRUG TOREN KASTEEL MOLEN KERK SCHOOL WINKEL "
              "MUZIEK GITAAR PIANO TROMMEL FLUIT CAMERA BRIL HORLOGE PARAPLU RUGZAK KOFFER SCHOEN LAARS JAS SJAAL MUTS "
              "HANDSCHOEN BOEK KRANT POTLOOD GUM LINIAAL SCHRIFT DRAAK RIDDER TOVENAAR SCHAT KAART KOMPAS",
}
WOORDEN_EN = {
    "animals": "DOG CAT HORSE COW GOAT SHEEP PIG RABBIT HAMSTER PARROT OWL EAGLE SWALLOW CROW DUCK SWAN FOX WOLF BEAR BADGER "
               "HEDGEHOG OTTER BEAVER DEER SQUIRREL MOUSE RAT ELEPHANT GIRAFFE LION TIGER ZEBRA MONKEY RHINO CROCODILE SNAKE "
               "TURTLE FROG BUTTERFLY BEE WASP ANT SPIDER SNAIL WHALE DOLPHIN SHARK SEAL PENGUIN",
    "food": "BREAD CHEESE BUTTER MILK APPLE PEAR BANANA STRAWBERRY CHERRY GRAPE LEMON ORANGE TOMATO CUCUMBER CARROT ONION "
            "POTATO BROCCOLI PEPPER RICE PASTA PIZZA SOUP PANCAKE WAFFLE CHOCOLATE COOKIE CAKE CREAM COFFEE TEA YOGHURT HONEY "
            "JAM SANDWICH",
    "home": "CHAIR TABLE COUCH CUPBOARD BED PILLOW BLANKET LAMP MIRROR DOOR WINDOW STAIRS ATTIC CELLAR KITCHEN BATHROOM "
            "SHOWER OVEN FRIDGE BROOM BUCKET SCISSORS HAMMER SCREWDRIVER PHONE COMPUTER KEYBOARD TELEVISION CLOCK KEY CURTAIN "
            "CANDLE VASE PAINTING BOOKCASE",
    "nature": "TREE FOREST OAK BIRCH PINE WILLOW LEAF BRANCH ROOT FLOWER TULIP ROSE SUNFLOWER DAISY GRASS MOSS FERN RIVER "
              "STREAM LAKE SEA BEACH DUNE MOUNTAIN HILL VALLEY CLOUD RAIN SNOW HAIL THUNDER LIGHTNING RAINBOW SUN MOON STAR "
              "PLANET COMET WIND STORM FOG ICE AUTUMN WINTER SPRING SUMMER",
    "things": "BICYCLE CAR TRAIN BUS AIRPLANE BOAT ROCKET TRACTOR HELICOPTER BRIDGE TOWER CASTLE WINDMILL CHURCH SCHOOL SHOP "
              "MUSIC GUITAR PIANO DRUM FLUTE CAMERA GLASSES WATCH UMBRELLA BACKPACK SUITCASE SHOE BOOT COAT SCARF HAT GLOVE "
              "BOOK NEWSPAPER PENCIL ERASER RULER NOTEBOOK DRAGON KNIGHT WIZARD TREASURE MAP COMPASS",
}
CAT_NAAM = {"dieren": "Dieren", "eten": "Eten en drinken", "huis": "In huis", "natuur": "Natuur", "dingen": "Dingen",
            "animals": "Animals", "food": "Food and drink", "home": "At home", "nature": "Nature", "things": "Things"}

TX = {
    "galg": ("Galgje", "Hangman"),
    "raad": ("Raad het woord: klik op een letter (of typ hem).", "Guess the word: click a letter (or type it)."),
    "goed_l": ("Ja! De %s zit erin.", "Yes! The %s is in it."),
    "fout_l": ("Nee, geen %s.", "No, no %s."),
    "al": ("Die letter had je al.", "You already had that letter."),
    "geraden": ("Geraden! Het woord was %s.", "Guessed! The word was %s."),
    "hangt": ("Helaas, hij hangt! Het woord was %s.", "Too bad, he's hanged! The word was %s."),
    "soort": ("Soort woord: %s", "Kind of word: %s"),
    "fouten": ("Fouten: %d van %d", "Mistakes: %d of %d"),
    "tip_l": ("Tip: probeer de %s (kost wel een fout).", "Tip: try the %s (it does cost a mistake)."),
    "toetsen_galg": ("Klik een letter of typ hem  ·  Ctrl+T = tip  ·  Esc = menu", "Click a letter or type it  ·  Ctrl+T = tip  ·  Esc = menu"),
    "stand_galg": ("Geraden: %d  ·  Gehangen: %d", "Guessed: %d  ·  Hanged: %d"),
    # online
    "bedenk": ("Jij bedenkt het woord. Typ het in (alleen letters) en klik Klaar.", "You think of the word. Type it (letters only) and click Done."),
    "willekeurig": ("Willekeurig woord", "Random word"),
    "ander_bedenkt": ("%s bedenkt een woord...", "%s is thinking of a word..."),
    "ander_raadt": ("%s raadt jouw woord: %s", "%s is guessing your word: %s"),
    "jouw_woord": ("Jouw woord: %s", "Your word: %s"),
    "te_kort": ("Minstens 3 letters, alleen A tot Z.", "At least 3 letters, only A to Z."),
}


def T(k):
    if k in TX:
        v = TX[k]
        return v[0] if UI.TAAL == "nl" else v[1]
    return UI.T(k)


def woordenlijst():
    return WOORDEN_NL if UI.TAAL == "nl" else WOORDEN_EN


def kies_woord(niveau):
    """Makkelijk: korte woorden. Normaal: middel. Moeilijk: lange woorden."""
    lijst = woordenlijst()
    kandidaten = []
    for cat, tekst in lijst.items():
        for w in tekst.split():
            n = len(w)
            if (niveau == 1 and 3 <= n <= 5) or (niveau == 2 and 6 <= n <= 8) or (niveau == 3 and n >= 9):
                kandidaten.append((w, cat))
    return random.choice(kandidaten)


def schoon(woord):
    return "".join(c for c in woord.upper() if c in LETTERS)


# ------------------------------------------------------------------ het spel
class Galgje:
    def __init__(self, app, niveau):
        self.app = app
        self.niveau = niveau
        self.knoppen = []
        self.score = [0, 0]              # [geraden, gehangen]
        self.nieuw_potje()

    def nieuw_potje(self):
        self.woord, self.cat = kies_woord(self.niveau)
        self.geraden = set()
        self.fout = 0
        self.klaar = False
        self.gewonnen = False
        self.melding = ""
        self.schud = 0.0                 # het poppetje schudt even bij een fout
        self.knipper = 0.0

    def mag_raden(self):
        return not self.klaar

    def raad(self, letter):
        if not self.mag_raden():
            return
        if letter in self.geraden:
            self.melding = T("al")
            self.app.geluid.speel("klik")
            return
        self.verwerk(letter)

    def verwerk(self, letter):
        self.geraden.add(letter)
        if letter in self.woord:
            self.melding = T("goed_l") % letter
            self.knipper = 1.0
            self.app.geluid.speel("goed")
        else:
            self.fout += 1
            self.melding = T("fout_l") % letter
            self.schud = 1.0
            self.app.geluid.speel("fout")
        self.controleer()

    def controleer(self):
        if all(c in self.geraden for c in self.woord):
            self.klaar = True
            self.gewonnen = True
            self.score[0] += 1
            self.melding = T("geraden") % self.woord
            self.app.geluid.speel("win")
        elif self.fout >= MAX_FOUT:
            self.klaar = True
            self.score[1] += 1
            self.melding = T("hangt") % self.woord
            self.app.geluid.speel("verlies")

    def geef_tip(self):
        if not self.mag_raden():
            return
        over = [c for c in self.woord if c not in self.geraden]
        if over:
            letter = random.choice(over)
            self.fout += 1                 # een tip kost een fout
            self.schud = 0.6
            self.geraden.add(letter)
            self.knipper = 1.0
            self.controleer()
            if not self.klaar:
                self.melding = T("tip_l") % letter
            self.app.geluid.speel("goed")

    def update(self):
        self.schud = max(0.0, self.schud - 0.04)
        self.knipper = max(0.0, self.knipper - 0.03)

    # ---------- invoer
    def klik(self, pos):
        pass                               # de letters zijn knoppen

    def toets(self, e):
        if e.key == pygame.K_ESCAPE:
            self.app.naar_menu()
        elif self.klaar and e.key in (pygame.K_SPACE, pygame.K_RETURN):
            self.nieuw_potje()
        elif e.unicode and e.unicode.upper() in LETTERS and len(e.unicode) == 1:
            if e.unicode.upper() == "T" and e.mod & pygame.KMOD_CTRL:
                self.geef_tip()
            else:
                self.raad(e.unicode.upper())

    # ---------- tekenen
    def teken_galg(self, d, x0, y0, fout):
        hout = (150, 112, 70)
        donker = (90, 64, 40)
        dx = int(8 * self.schud * (1 if int(self.schud * 20) % 2 else -1))
        stappen = [
            lambda: pygame.draw.rect(d, donker, (x0, y0 + 380, 300, 22), border_radius=6),                 # grond
            lambda: pygame.draw.rect(d, hout, (x0 + 50, y0 + 20, 22, 370), border_radius=4),               # paal
            lambda: pygame.draw.rect(d, hout, (x0 + 50, y0 + 20, 210, 20), border_radius=4),               # balk
            lambda: pygame.draw.line(d, hout, (x0 + 72, y0 + 100), (x0 + 140, y0 + 40), 14),               # schoor
            lambda: pygame.draw.line(d, (200, 190, 160), (x0 + 220, y0 + 40), (x0 + 220 + dx, y0 + 90), 5),  # touw
        ]
        figuur_kl = UI.ACCENT if not (self.klaar and not self.gewonnen) else UI.ROOD
        cx = x0 + 220 + dx
        figuur = [
            lambda: (pygame.draw.circle(d, figuur_kl, (cx, y0 + 122), 32, 6),
                     pygame.draw.circle(d, figuur_kl, (cx - 11, y0 + 116), 4), pygame.draw.circle(d, figuur_kl, (cx + 11, y0 + 116), 4)),
            lambda: pygame.draw.line(d, figuur_kl, (cx, y0 + 154), (cx, y0 + 260), 7),                    # lijf
            lambda: pygame.draw.line(d, figuur_kl, (cx, y0 + 180), (cx - 48, y0 + 226), 7),               # arm
            lambda: pygame.draw.line(d, figuur_kl, (cx, y0 + 180), (cx + 48, y0 + 226), 7),               # arm
            lambda: (pygame.draw.line(d, figuur_kl, (cx, y0 + 258), (cx - 40, y0 + 330), 7),
                     pygame.draw.line(d, figuur_kl, (cx, y0 + 258), (cx + 40, y0 + 330), 7)),             # benen
        ]
        alles = stappen + figuur
        for i in range(min(fout, len(alles))):
            alles[i]()
        if self.klaar and self.gewonnen:                                                                  # blij poppetje ernaast
            bx, by = x0 + 330, y0 + 250
            pygame.draw.circle(d, UI.GROEN, (bx, by), 26, 5)
            pygame.draw.arc(d, UI.GROEN, (bx - 14, by - 6, 28, 20), 3.4, 6.0, 4)
            pygame.draw.line(d, UI.GROEN, (bx, by + 26), (bx, by + 100), 6)
            pygame.draw.line(d, UI.GROEN, (bx, by + 46), (bx - 40, by + 10), 6)
            pygame.draw.line(d, UI.GROEN, (bx, by + 46), (bx + 40, by + 10), 6)
            pygame.draw.line(d, UI.GROEN, (bx, by + 98), (bx - 30, by + 150), 6)
            pygame.draw.line(d, UI.GROEN, (bx, by + 98), (bx + 30, by + 150), 6)

    def teken_woord(self, d, y, laat_zien=False):
        n = len(self.woord)
        vak = min(64, (UI.W - 520) // max(1, n))
        x0 = 480 + ((UI.W - 520) - n * vak) // 2
        for i, c in enumerate(self.woord):
            x = x0 + i * vak
            pygame.draw.line(d, UI.ACCENT, (x + 6, y + vak), (x + vak - 6, y + vak), 5)
            if c in self.geraden or laat_zien or self.klaar:
                kl = UI.GOUD if c in self.geraden else UI.ROOD
                if self.knipper and c in self.geraden:
                    kl = tuple(min(255, int(a + (255 - a) * self.knipper)) for a in kl)
                UI.tekst(d, c, int(vak * 0.8), kl, (x + vak // 2, y + vak // 2), mid=True)

    def teken_toetsen(self, d, muis, aan=True):
        self.knoppen = []
        rijen = (LETTERS[:9], LETTERS[9:18], LETTERS[18:])
        for r, rij in enumerate(rijen):
            for i, c in enumerate(rij):
                x = 490 + i * 84
                y = 380 + r * 84
                if c in self.geraden:
                    kl = UI.GROEN if c in self.woord else (120, 50, 66)
                    k = UI.Knop((x, y, 74, 74), c, lambda: None, kl, 34)      # groen = goed, rood = fout
                else:
                    k = UI.Knop((x, y, 74, 74), c, lambda c=c: self.raad(c), UI.VAK, 34, aan=aan)
                self.knoppen.append(k)

    def teken(self, d, muis):
        d.fill(UI.ACHTER)
        UI.tekst(d, T("galg"), 40, UI.ACCENT, (40, 14))
        paneel = pygame.Rect(30, 90, 420, 440)
        pygame.draw.rect(d, UI.VAK, paneel, border_radius=20)
        pygame.draw.rect(d, UI.RAND, paneel, 3, border_radius=20)
        self.teken_galg(d, 60, 110, self.fout)
        self.teken_info(d)
        self.teken_woord(d, 170)
        self.teken_toetsen(d, muis, aan=self.mag_raden())
        self.teken_knoppen(d, muis)
        for k in self.knoppen:
            k.teken(d, muis)
        UI.tekst(d, T("toetsen_galg"), 16, UI.ZACHT, (40, UI.H - 34), vet=False)

    def teken_info(self, d):
        UI.tekst(d, T("fouten") % (self.fout, MAX_FOUT), 26, UI.ROOD if self.fout >= MAX_FOUT - 2 else UI.TEKST, (40, 548))
        if self.app.hulp or self.klaar:
            UI.tekst(d, T("soort") % CAT_NAAM.get(self.cat, self.cat), 22, UI.ZACHT, (40, 590), vet=False)
        UI.tekst(d, T("stand_galg") % (self.score[0], self.score[1]), 24, UI.GOUD, (UI.W - 40, 22), rechts=True)
        regel = self.melding or T("raad")
        kl = UI.GROEN if (self.klaar and self.gewonnen) else (UI.ROOD if self.klaar else UI.GOUD)
        for i, stuk in enumerate(UI.Backgammon._knip(None, regel, 24, UI.W - 520)[:2]):
            UI.tekst(d, stuk, 24, kl if self.melding else UI.TEKST, (490, 280 + i * 32))

    def teken_knoppen(self, d, muis):
        y = 650
        if self.klaar:
            self.knoppen.append(UI.Knop((490, y, 300, 70), UI.T("nog"), self.nieuw_potje, UI.GROEN, 26))
        else:
            self.knoppen.append(UI.Knop((490, y, 140, 70), UI.T("tip"), self.geef_tip, UI.GOUD, 26, aan=self.mag_raden()))
            self.knoppen.append(UI.Knop((645, y, 230, 70), "%s: %s" % (UI.T("hulp"), UI.T("aan") if self.app.hulp else UI.T("uitm")),
                                        self.app.wissel_hulp, UI.VAK, 22))
        self.knoppen.append(UI.Knop((890, y, 170, 70), UI.T("menu"), self.app.naar_menu, UI.VAK, 24))
        self.knoppen.append(UI.Knop((1075, y, 170, 70), UI.T("regels"), lambda: setattr(self.app, "toon_regels", True), UI.VAK, 22))


# ------------------------------------------------------------------ online: de een bedenkt, de ander raadt
class OnlineGalgje(Galgje):
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
        self.eerste = 0
        self.invoer = ""
        self.einde_gezien = False
        Galgje.__init__(self, app, 1)
        self.woord, self.cat = "", ""
        self.score = [0, 0]                # per speler (index)
        self.lijn = UI.online.Lijn(adres, code, {"t": "hallo", "spel": "galg", "naam": naam, "token": token}, pad="zet/kamer")

    def ik_bedenk(self):
        return self.ik is not None and self.ik == self.eerste

    def nieuw_potje(self):
        if self.lijn is not None:
            self.lijn.stuur({"t": "nieuw"})
            self.app.geluid.speel("klik")
            return
        Galgje.nieuw_potje(self)

    def mag_raden(self):
        return self.fase == "spel" and not self.klaar and self.woord and not self.ik_bedenk()

    def naam_van(self, idx):
        if idx == self.ik:
            return UI.T("jij")
        return self.ander or UI.T("tegenspeler")

    def verwerk(self, letter):
        if not self.lijn:
            return
        nieuw = self.geraden | {letter}
        fout = self.fout + (0 if letter in self.woord else 1)
        einde = None
        if all(c in nieuw for c in self.woord):
            einde = self.ik
        elif fout >= MAX_FOUT:
            einde = 1 - self.ik
        if self.lijn.stuur({"t": "zet", "z": {"letter": letter}, "nog": True, "einde": einde}):
            self.n_zetten += 1
            self.pas_letter(letter)
        else:
            self.status = UI.T("geen_server")

    def pas_letter(self, letter):
        Galgje.verwerk(self, letter)

    def controleer(self):
        if all(c in self.geraden for c in self.woord):
            self.klaar = True
            self.gewonnen = True
            self.melding = T("geraden") % self.woord
        elif self.fout >= MAX_FOUT:
            self.klaar = True
            self.gewonnen = False
            self.melding = T("hangt") % self.woord

    def geef_tip(self):
        pass                               # online: geen tip (dan zou het te makkelijk zijn)

    def kies_woord_online(self, woord=None):
        if not self.ik_bedenk() or self.woord or self.fase != "spel":
            return
        if woord is None:
            woord = schoon(self.invoer)
            if len(woord) < 3:
                self.melding = T("te_kort")
                self.app.geluid.speel("fout")
                return
            cat = ""
        else:
            woord, cat = woord
        if self.lijn.stuur({"t": "zet", "z": {"woord": woord[:20], "cat": cat}}):
            self.n_zetten += 1
            self.woord, self.cat = woord[:20], cat
            self.melding = ""
            self.app.geluid.speel("klik")

    def toets(self, e):
        if e.key == pygame.K_ESCAPE:
            self.app.naar_menu()
            return
        if self.ik_bedenk() and not self.woord and self.fase == "spel":
            if e.key == pygame.K_BACKSPACE:
                self.invoer = self.invoer[:-1]
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.kies_woord_online()
            elif e.unicode and e.unicode.upper() in LETTERS and len(self.invoer) < 20:
                self.invoer += e.unicode.upper()
            return
        if self.klaar and e.key in (pygame.K_SPACE, pygame.K_RETURN):
            self.nieuw_potje()
        elif e.unicode and len(e.unicode) == 1 and e.unicode.upper() in LETTERS:
            self.raad(e.unicode.upper())

    def update(self):
        Galgje.update(self)
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
        self.eerste = st.get("eerste", 0)
        self.score = list(st.get("score", [0, 0]))
        self.ander = (st.get("ander") or {}).get("naam")
        self.verbonden = st.get("verbonden", [True, True])
        self.fase = st["fase"]
        if self.fase == "wachten":
            return
        lijst = st.get("zetten") or []
        if st.get("potje") == self.potje and len(lijst) < self.n_zetten:
            return
        if st.get("potje") != self.potje:            # nieuw potje (of net binnen): opnieuw opbouwen
            self.potje = st.get("potje")
            self.woord, self.cat = "", ""
            self.geraden, self.fout = set(), 0
            self.klaar = self.gewonnen = False
            self.melding = ""
            self.invoer = ""
            self.n_zetten = 0
            self.einde_gezien = False
        for d in lijst[self.n_zetten:]:
            z = d.get("z") or {}
            if "woord" in z:
                self.woord, self.cat = schoon(z["woord"])[:20], str(z.get("cat") or "")
            elif "letter" in z and self.woord:
                Galgje.verwerk(self, str(z["letter"])[:1])
            self.n_zetten += 1
        if self.fase == "einde":
            self.klaar = True
            w = st.get("winnaar")
            if not self.einde_gezien:
                self.einde_gezien = True
                if st.get("reden") != "opgegeven":
                    self.gewonnen = all(c in self.geraden for c in self.woord)
                self.app.geluid.speel("win" if w == self.ik else "verlies")
        else:
            self.klaar = False

    def teken(self, d, muis):
        d.fill(UI.ACHTER)
        UI.tekst(d, T("galg"), 40, UI.ACCENT, (40, 14))
        UI.tekst(d, UI.T("kamer") % self.code, 20, UI.ACCENT, (240, 30))
        paneel = pygame.Rect(30, 90, 420, 440)
        pygame.draw.rect(d, UI.VAK, paneel, border_radius=20)
        pygame.draw.rect(d, UI.RAND, paneel, 3, border_radius=20)
        self.teken_galg(d, 60, 110, self.fout)
        self.knoppen = []
        if self.ik is not None:
            UI.tekst(d, "%s %d  ·  %s %d" % (self.naam_van(self.ik), self.score[self.ik], self.naam_van(1 - self.ik),
                                             self.score[1 - self.ik]), 24, UI.GOUD, (UI.W - 40, 22), rechts=True)
        UI.tekst(d, T("fouten") % (self.fout, MAX_FOUT), 26, UI.TEKST, (40, 548))
        if self.fase == "wachten":
            UI.tekst(d, UI.T("wacht_ander") % self.code, 24, UI.TEKST, (490, 120))
            UI.tekst(d, self.code, 64, UI.GOUD, (490, 170))
        elif self.ik_bedenk() and not self.woord:
            UI.tekst(d, T("bedenk"), 24, UI.TEKST, (490, 110))
            r = pygame.Rect(490, 160, 600, 80)
            pygame.draw.rect(d, (44, 38, 64), r, border_radius=14)
            pygame.draw.rect(d, UI.GOUD, r, 3, border_radius=14)
            knip = (pygame.time.get_ticks() // 500) % 2 == 0
            UI.tekst(d, self.invoer + ("|" if knip else ""), 44, UI.TEKST, (r.x + 20, r.y + 14))
            self.knoppen.append(UI.Knop((490, 270, 200, 70), UI.T("klaar"), self.kies_woord_online, UI.GROEN, 26))
            self.knoppen.append(UI.Knop((710, 270, 320, 70), T("willekeurig"),
                                        lambda: self.kies_woord_online(kies_woord(random.choice((1, 2, 2, 3)))), UI.VAK, 24))
            if self.melding:
                UI.tekst(d, self.melding, 22, UI.ROOD, (490, 360))
        elif not self.woord:
            UI.tekst(d, T("ander_bedenkt") % (self.ander or UI.T("tegenspeler")), 26, UI.TEKST, (490, 140))
        else:
            self.teken_woord(d, 170, laat_zien=self.ik_bedenk())
            if self.ik_bedenk():
                regel = T("ander_raadt") % (self.ander or UI.T("tegenspeler"), self.woord)
            else:
                regel = self.melding or T("raad")
            if self.klaar:
                regel = (T("geraden") if self.gewonnen else T("hangt")) % self.woord
            kl = UI.GROEN if (self.klaar and self.gewonnen) else (UI.ROOD if self.klaar else UI.GOUD)
            for i, stuk in enumerate(UI.Backgammon._knip(None, regel, 24, UI.W - 520)[:2]):
                UI.tekst(d, stuk, 24, kl, (490, 280 + i * 32))
            vorige = self.knoppen
            self.teken_toetsen(d, muis, aan=self.mag_raden())
            self.knoppen = vorige + self.knoppen
        if self.status:
            UI.tekst(d, self.status, 20, UI.ROOD, (40, 600))
        elif self.ik is not None and self.ander and not self.verbonden[1 - self.ik]:
            UI.tekst(d, UI.T("ander_weg") % self.ander, 20, UI.GOUD, (40, 600))
        y = 650
        if self.klaar:
            self.knoppen.append(UI.Knop((490, y, 300, 70), UI.T("nog"), self.nieuw_potje, UI.GROEN, 26))
        self.knoppen.append(UI.Knop((890, y, 170, 70), UI.T("menu"), self.app.naar_menu, UI.VAK, 24))
        self.knoppen.append(UI.Knop((1075, y, 170, 70), UI.T("regels"), lambda: setattr(self.app, "toon_regels", True), UI.VAK, 22))
        for k in self.knoppen:
            k.teken(d, muis)

    def stop(self):
        if self.lijn:
            self.lijn.stop()
