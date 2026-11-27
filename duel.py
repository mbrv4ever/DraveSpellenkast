# -*- coding: utf-8 -*-
"""DraveSpellenkast - DraveMagie: een kaartspel met wezens en spreuken (27-11-2026, idee van pa).
Twee stokken: Woud en Vuur (rood-groen: wezens en aanvallen) en Licht en Water (blauw-wit: spreuken en verdediging).
Elke beurt krijg je 1 mana meer. Speel wezens en spreuken, val aan, en breng de ander van 20 naar 0 levens.
Combinaties maken het slim: wolven worden sterker in een roedel, uilen laten je kaarten trekken, enzovoort.
Tegen de computer (3 niveaus). Copyright (C) 2026 Dravenlock (Roger & Claudio). GNU GPL v3.0."""
import math
import random
import time

import pygame

UI = None          # wordt door main.py gezet

LEVENS = 20
MAX_MANA = 8
HAND_MAX = 8
VELD_MAX = 6
KW, KH = 118, 168          # kaart in de hand
VW, VH = 112, 140          # wezen op het veld

TX = {
    "duel": ("DraveMagie", "DraveMagic"),
    "kies_stok": ("Kies je stok", "Choose your deck"),
    "stok_rg": ("Woud en Vuur", "Forest and Fire"),
    "stok_rg_sub": ("Rood-groen: veel wezens, hard aanvallen, wolven in een roedel.",
                    "Red-green: many creatures, attack hard, wolves in a pack."),
    "stok_bw": ("Licht en Water", "Light and Water"),
    "stok_bw_sub": ("Blauw-wit: spreuken, schilden en kaarten trekken.",
                    "Blue-white: spells, shields and drawing cards."),
    "jouw_beurt": ("Jouw beurt. Klik een kaart om te spelen, of een wezen om aan te vallen.",
                   "Your turn. Click a card to play it, or a creature to attack."),
    "kies_doel": ("Kies een doel (of Backspace om te stoppen).", "Choose a target (or Backspace to cancel)."),
    "kies_aanval": ("Wie val je aan? Klik een wezen of de held van de ander.", "Attack whom? Click a creature or the other hero."),
    "moet_wacht": ("Eerst de Wachters! Wezens met een schild moeten eerst verslagen worden.",
                   "Guards first! Creatures with a shield must be defeated first."),
    "te_duur": ("Daar heb je niet genoeg mana voor.", "Not enough mana for that."),
    "veld_vol": ("Je veld is vol (6 wezens).", "Your field is full (6 creatures)."),
    "slaapt": ("Dit wezen is net gekomen en moet nog even wennen. Volgende beurt mag hij aanvallen.",
               "This creature just arrived. It can attack next turn."),
    "al_aangevallen": ("Dit wezen heeft deze beurt al aangevallen.", "This creature already attacked this turn."),
    "bevroren": ("Dit wezen is bevroren en slaat een beurt over.", "This creature is frozen and skips a turn."),
    "comp_denkt": ("De computer is aan de beurt...", "The computer's turn..."),
    "einde_beurt": ("Einde beurt", "End turn"),
    "jij_wint": ("Jij wint! De held van de computer is verslagen.", "You win! The computer's hero is defeated."),
    "comp_wint": ("De computer wint dit potje.", "The computer wins this round."),
    "trek_leeg": ("Je stok is leeg: elke beurt kost je dat 2 levens.", "Your deck is empty: that costs 2 life each turn."),
    "hand_vol": ("Je hand is vol: de getrokken kaart gaat verloren.", "Your hand is full: the drawn card is lost."),
    "toetsen_duel": ("Klik kaart = spelen  ·  klik wezen = aanvallen  ·  Backspace = stoppen  ·  Enter = einde beurt  ·  Esc = menu",
                     "Click card = play  ·  click creature = attack  ·  Backspace = cancel  ·  Enter = end turn  ·  Esc = menu"),
    "mana": ("Mana", "Mana"), "stok": ("Stok", "Deck"), "hand": ("Hand", "Hand"),
    "spreuk": ("SPREUK", "SPELL"),
    "tip_kop": ("Tip: de gouden kaart of het gouden wezen.", "Tip: the gold card or the gold creature."),
}


def T(k):
    if k in TX:
        v = TX[k]
        return v[0] if UI.TAAL == "nl" else v[1]
    return UI.T(k)


# ------------------------------------------------------------------ de kaarten
# soort: "wezen" of "spreuk". doel (spreuk): None, "wezen", "vijand_wezen", "eigen_wezen", "alles" (wezen of held)
KAARTEN = {
    # --- Woud en Vuur (rood-groen)
    "vonk":    dict(nl="Vonkje", en="Spark", soort="wezen", kost=1, kr=1, lv=1, haast=True, kleur="rood", tekening="vonk",
                    t_nl="Haast: valt meteen aan.", t_en="Haste: attacks at once."),
    "wolf":    dict(nl="Wolf", en="Wolf", soort="wezen", kost=2, kr=2, lv=2, roedel=True, kleur="groen", tekening="wolf",
                    t_nl="Roedel: +1 kracht per andere wolf.", t_en="Pack: +1 power per other wolf."),
    "druide":  dict(nl="Druïde", en="Druid", soort="wezen", kost=3, kr=2, lv=3, kom="druide", kleur="groen", tekening="druide",
                    t_nl="Komt: je andere wezens +1 leven.", t_en="Arrives: your other creatures +1 health."),
    "everzwijn": dict(nl="Everzwijn", en="Boar", soort="wezen", kost=3, kr=3, lv=2, haast=True, kleur="rood", tekening="zwijn",
                    t_nl="Haast: valt meteen aan.", t_en="Haste: attacks at once."),
    "beer":    dict(nl="Beer", en="Bear", soort="wezen", kost=4, kr=4, lv=5, kleur="groen", tekening="beer",
                    t_nl="Sterk en taai.", t_en="Strong and tough."),
    "draak":   dict(nl="Vuurdraak", en="Fire dragon", soort="wezen", kost=6, kr=6, lv=6, haast=True, kleur="rood", tekening="draak",
                    t_nl="Haast. Komt: 2 schade aan elk vijandig wezen.", t_en="Haste. Arrives: 2 damage to each enemy creature.", kom="draak"),
    "vuurbal": dict(nl="Vuurbal", en="Fireball", soort="spreuk", kost=2, doel="alles", kleur="rood", tekening="vuurbal",
                    t_nl="3 schade aan een wezen of een held.", t_en="3 damage to a creature or a hero."),
    "groei":   dict(nl="Groeikracht", en="Growth", soort="spreuk", kost=1, doel="eigen_wezen", kleur="groen", tekening="groei",
                    t_nl="Eigen wezen +2 kracht en +2 leven.", t_en="Your creature +2 power and +2 health."),
    "huil":    dict(nl="Huil naar de maan", en="Howl at the moon", soort="spreuk", kost=3, doel=None, kleur="groen", tekening="maan",
                    t_nl="Er komen 2 wolven bij je.", t_en="Two wolves join you."),
    # --- Licht en Water (blauw-wit)
    "ridder":  dict(nl="Ridder", en="Knight", soort="wezen", kost=2, kr=2, lv=4, wacht=True, kleur="wit", tekening="ridder",
                    t_nl="Wacht: moet eerst verslagen worden.", t_en="Guard: must be defeated first."),
    "uil":     dict(nl="Wijze uil", en="Wise owl", soort="wezen", kost=2, kr=2, lv=2, kom="uil", kleur="blauw", tekening="uil",
                    t_nl="Komt: trek 1 kaart.", t_en="Arrives: draw 1 card."),
    "golem":   dict(nl="Watergolem", en="Water golem", soort="wezen", kost=4, kr=4, lv=6, kleur="blauw", tekening="golem",
                    t_nl="Taai als een rots in de branding.", t_en="Tough as a rock in the surf."),
    "engel":   dict(nl="Engel", en="Angel", soort="wezen", kost=5, kr=4, lv=5, kom="engel", kleur="wit", tekening="engel",
                    t_nl="Komt: jij krijgt 4 levens.", t_en="Arrives: you gain 4 life."),
    "slang":   dict(nl="Zeeslang", en="Sea serpent", soort="wezen", kost=5, kr=5, lv=7, wacht=True, kleur="blauw", tekening="slang",
                    t_nl="Wacht: moet eerst verslagen worden.", t_en="Guard: must be defeated first."),
    "bevries": dict(nl="Bevriezen", en="Freeze", soort="spreuk", kost=1, doel="vijand_wezen", kleur="blauw", tekening="ijs",
                    t_nl="Vijandelijk wezen slaat een beurt over.", t_en="Enemy creature skips a turn."),
    "schild":  dict(nl="Lichtschild", en="Light shield", soort="spreuk", kost=1, doel="eigen_wezen", kleur="wit", tekening="schild",
                    t_nl="Eigen wezen +3 leven en wordt een Wacht.", t_en="Your creature +3 health and becomes a Guard."),
    "genees":  dict(nl="Genezing", en="Healing", soort="spreuk", kost=2, doel=None, kleur="wit", tekening="hart",
                    t_nl="Jij krijgt 5 levens.", t_en="You gain 5 life."),
    "wijsheid": dict(nl="Wijsheid", en="Wisdom", soort="spreuk", kost=3, doel=None, kleur="blauw", tekening="boek",
                    t_nl="Trek 2 kaarten.", t_en="Draw 2 cards."),
    "straal":  dict(nl="Lichtstraal", en="Ray of light", soort="spreuk", kost=3, doel="vijand_wezen", kleur="wit", tekening="straal",
                    t_nl="5 schade aan een vijandelijk wezen.", t_en="5 damage to an enemy creature."),
}

STOKKEN = {
    "rg": ["vonk"] * 2 + ["wolf"] * 4 + ["druide"] * 2 + ["everzwijn"] * 2 + ["beer"] * 2 + ["draak"] * 1 +
          ["vuurbal"] * 3 + ["groei"] * 2 + ["huil"] * 2,
    "bw": ["ridder"] * 3 + ["uil"] * 3 + ["golem"] * 2 + ["engel"] * 2 + ["slang"] * 1 +
          ["bevries"] * 2 + ["schild"] * 2 + ["genees"] * 2 + ["wijsheid"] * 1 + ["straal"] * 2,
}

KLEUREN = {"rood": ((150, 52, 48), (236, 120, 90)), "groen": ((46, 110, 62), (130, 210, 120)),
           "blauw": ((40, 78, 140), (120, 180, 240)), "wit": ((150, 140, 110), (250, 240, 200))}


def naam_van(sl):
    k = KAARTEN[sl]
    return k["nl"] if UI is None or UI.TAAL == "nl" else k["en"]


def tekst_van(sl):
    k = KAARTEN[sl]
    return k["t_nl"] if UI is None or UI.TAAL == "nl" else k["t_en"]


# ------------------------------------------------------------------ de regels (zonder scherm)
class Wezen:
    def __init__(self, sl, wid):
        k = KAARTEN[sl]
        self.id = wid
        self.sl = sl
        self.kr = k["kr"]
        self.lv = k["lv"]
        self.max_lv = k["lv"]
        self.wacht = k.get("wacht", False)
        self.haast = k.get("haast", False)
        self.roedel = k.get("roedel", False)
        self.slaapt = not self.haast
        self.aangevallen = False
        self.bevroren = 0
        self.flits = 0.0               # voor het tekenen: net geraakt


class Speler:
    def __init__(self, stok_sl, rng):
        self.stok = list(STOKKEN[stok_sl])
        rng.shuffle(self.stok)
        self.stok_sl = stok_sl
        self.hand = []
        self.veld = []
        self.levens = LEVENS
        self.mana = 0
        self.max_mana = 0
        self.leeg_schade = 0


def kracht(sp, w):
    if w.roedel:
        return w.kr + sum(1 for x in sp.veld if x is not w and x.roedel)
    return w.kr


class Spel:
    """Alle regels. Speler 0 en 1. 'zeg' is een functie voor meldingen (mag None)."""

    def __init__(self, stok0, stok1, zaad=None, zeg=None):
        self.rng = random.Random(zaad)
        self.sp = [Speler(stok0, self.rng), Speler(stok1, self.rng)]
        self.zeg = zeg or (lambda t: None)
        self.beurt = 0
        self.winnaar = None
        self.teller = 0
        for _ in range(4):
            self.trek(0)
            self.trek(1)
        self.trek(1)                    # wie als tweede begint krijgt een kaartje extra
        self.begin_beurt(0, eerste=True)

    # ---------- hulpjes
    def trek(self, i):
        s = self.sp[i]
        if not s.stok:
            s.leeg_schade += 2
            s.levens -= s.leeg_schade
            self.zeg(("trek_leeg", i))
            self.check()
            return
        k = s.stok.pop()
        if len(s.hand) >= HAND_MAX:
            self.zeg(("hand_vol", i))
            return
        s.hand.append(k)

    def begin_beurt(self, i, eerste=False):
        s = self.sp[i]
        self.beurt = i
        s.max_mana = min(MAX_MANA, s.max_mana + 1)
        s.mana = s.max_mana
        for w in s.veld:
            w.slaapt = False
            w.aangevallen = False
            if w.bevroren:
                w.bevroren -= 1
        if not eerste:
            self.trek(i)

    def einde_beurt(self):
        if self.winnaar is not None:
            return
        self.begin_beurt(1 - self.beurt)

    def check(self):
        for i in (0, 1):
            self.sp[i].veld = [w for w in self.sp[i].veld if w.lv > 0]
        if self.winnaar is None:
            if self.sp[0].levens <= 0 and self.sp[1].levens <= 0:
                self.winnaar = -1
            elif self.sp[0].levens <= 0:
                self.winnaar = 1
            elif self.sp[1].levens <= 0:
                self.winnaar = 0

    def heeft_wacht(self, i):
        return any(w.wacht for w in self.sp[i].veld)

    # ---------- mag het?
    def kan_spelen(self, i, h):
        s = self.sp[i]
        if self.winnaar is not None or self.beurt != i or h >= len(s.hand):
            return False
        k = KAARTEN[s.hand[h]]
        if k["kost"] > s.mana:
            return False
        if k["soort"] == "wezen" and len(s.veld) >= VELD_MAX:
            return False
        if k["soort"] == "spreuk" and k["doel"] and not self.doelen(i, k["doel"]):
            return False
        if s.hand[h] == "huil" and len(s.veld) >= VELD_MAX:
            return False
        return True

    def doelen(self, i, soort):
        """Lijst van doelen: ("wezen", speler, id) of ("held", speler)."""
        uit = []
        if soort in ("vijand_wezen", "wezen", "alles"):
            uit += [("wezen", 1 - i, w.id) for w in self.sp[1 - i].veld]
        if soort in ("eigen_wezen", "wezen", "alles"):
            uit += [("wezen", i, w.id) for w in self.sp[i].veld]
        if soort == "alles":
            uit += [("held", 1 - i), ("held", i)]
        return uit

    def aanval_doelen(self, i, wid):
        a = self.zoek(i, wid)
        if a is None or a.slaapt or a.aangevallen or a.bevroren or kracht(self.sp[i], a) <= 0:
            return []
        j = 1 - i
        if self.heeft_wacht(j):
            return [("wezen", j, w.id) for w in self.sp[j].veld if w.wacht]
        return [("wezen", j, w.id) for w in self.sp[j].veld] + [("held", j)]

    def zoek(self, i, wid):
        for w in self.sp[i].veld:
            if w.id == wid:
                return w
        return None

    # ---------- doen
    def speel(self, i, h, doel=None):
        """Speel kaart h uit de hand van speler i. Geeft True als het lukte."""
        if not self.kan_spelen(i, h):
            return False
        s = self.sp[i]
        sl = s.hand[h]
        k = KAARTEN[sl]
        if k["soort"] == "spreuk" and k["doel"] and doel not in self.doelen(i, k["doel"]):
            return False
        s.hand.pop(h)
        s.mana -= k["kost"]
        if k["soort"] == "wezen":
            self.teller += 1
            w = Wezen(sl, self.teller)
            s.veld.append(w)
            kom = k.get("kom")
            if kom == "druide":
                for x in s.veld:
                    if x is not w:
                        x.lv += 1
                        x.max_lv += 1
            elif kom == "uil":
                self.trek(i)
            elif kom == "engel":
                s.levens += 4
            elif kom == "draak":
                for x in self.sp[1 - i].veld:
                    x.lv -= 2
                    x.flits = time.time()
        else:
            self.spreuk(i, sl, doel)
        self.check()
        return True

    def raak(self, doel, schade):
        if doel[0] == "held":
            self.sp[doel[1]].levens -= schade
        else:
            w = self.zoek(doel[1], doel[2])
            if w:
                w.lv -= schade
                w.flits = time.time()

    def spreuk(self, i, sl, doel):
        s = self.sp[i]
        if sl == "vuurbal":
            self.raak(doel, 3)
        elif sl == "straal":
            self.raak(doel, 5)
        elif sl == "groei":
            w = self.zoek(doel[1], doel[2])
            w.kr += 2
            w.lv += 2
            w.max_lv += 2
        elif sl == "schild":
            w = self.zoek(doel[1], doel[2])
            w.lv += 3
            w.max_lv += 3
            w.wacht = True
        elif sl == "bevries":
            w = self.zoek(doel[1], doel[2])
            w.bevroren = 1
        elif sl == "genees":
            s.levens += 5
        elif sl == "wijsheid":
            self.trek(i)
            self.trek(i)
        elif sl == "huil":
            for _ in range(2):
                if len(s.veld) < VELD_MAX:
                    self.teller += 1
                    s.veld.append(Wezen("wolf", self.teller))

    def val_aan(self, i, wid, doel):
        if self.winnaar is not None or self.beurt != i or doel not in self.aanval_doelen(i, wid):
            return False
        a = self.zoek(i, wid)
        ka = kracht(self.sp[i], a)
        a.aangevallen = True
        if doel[0] == "held":
            self.sp[doel[1]].levens -= ka
        else:
            v = self.zoek(doel[1], doel[2])
            kv = kracht(self.sp[doel[1]], v)
            v.lv -= ka
            a.lv -= kv
            v.flits = a.flits = time.time()
        self.check()
        return True


# ------------------------------------------------------------------ de computer
def schat(spel, i):
    """Hoe goed staat speler i ervoor (hoger = beter)."""
    if spel.winnaar is not None:
        return 10 ** 6 if spel.winnaar == i else -10 ** 6
    me, hij = spel.sp[i], spel.sp[1 - i]
    w = (me.levens - hij.levens) * 2
    w += sum(kracht(me, x) * 2 + x.lv + (3 if x.wacht else 0) for x in me.veld)
    w -= sum(kracht(hij, x) * 2 + x.lv + (3 if x.wacht else 0) for x in hij.veld)
    w += len(me.hand) - len(hij.hand) * 0.5
    return w


def kloon(spel):
    import copy
    z = spel.zeg
    spel.zeg = None
    k = copy.deepcopy(spel)
    spel.zeg = z
    k.zeg = lambda t: None
    return k


def computer_zetten(spel, i, niveau):
    """Geeft een lijst acties: ("speel", h, doel) / ("val", wid, doel). Gulzig: kiest steeds de beste stap."""
    acties = []
    sim = kloon(spel)
    rng = random.Random()
    for _ in range(30):
        if sim.winnaar is not None or sim.beurt != i:
            break
        opties = []
        s = sim.sp[i]
        for h in range(len(s.hand)):
            if not sim.kan_spelen(i, h):
                continue
            k = KAARTEN[s.hand[h]]
            doelen = sim.doelen(i, k["doel"]) if k["soort"] == "spreuk" and k["doel"] else [None]
            for d in doelen:
                opties.append(("speel", h, d))
        for w in s.veld:
            for d in sim.aanval_doelen(i, w.id):
                opties.append(("val", w.id, d))
        if not opties:
            break
        basis = schat(sim, i)
        beste, beste_w = None, None
        for o in opties:
            t = kloon(sim)
            ok = t.speel(i, o[1], o[2]) if o[0] == "speel" else t.val_aan(i, o[1], o[2])
            if not ok:
                continue
            w = schat(t, i)
            if o[0] == "speel":
                w += 0.5 * KAARTEN[sim.sp[i].hand[o[1]]]["kost"]     # mana gebruiken is goed
            if niveau == 1:
                w += rng.uniform(-6, 6)
            elif niveau == 2:
                w += rng.uniform(-2, 2)
            if beste_w is None or w > beste_w:
                beste, beste_w = o, w
        if beste is None:
            break
        if beste[0] == "val" and beste_w < basis - (0 if niveau == 3 else 1):
            break                                    # een slechte ruil: liever niet
        if niveau == 1 and rng.random() < 0.15:
            break                                    # makkelijk: stopt soms te vroeg
        acties.append(beste)
        if beste[0] == "speel":
            sim.speel(i, beste[1], beste[2])
        else:
            sim.val_aan(i, beste[1], beste[2])
    return acties


# ------------------------------------------------------------------ tekenen van de plaatjes
def teken_plaatje(d, sl, rect):
    """Een klein zelfgetekend plaatje per kaart (geen kale blokjes)."""
    x, y, w, h = rect
    cx, cy = x + w // 2, y + h // 2
    s = min(w, h) / 100.0
    k = KAARTEN[sl]
    don, lic = KLEUREN[k["kleur"]]
    pygame.draw.rect(d, tuple(int(c * 0.55) for c in don), rect, border_radius=8)
    t = k["tekening"]

    def P(px, py):
        return (int(cx + px * s), int(cy + py * s))

    if t == "wolf":
        pygame.draw.polygon(d, (120, 120, 132), [P(-30, 10), P(-20, -30), P(-8, -12), P(8, -12), P(20, -30), P(30, 10), P(0, 34)])
        pygame.draw.polygon(d, (180, 180, 192), [P(-12, 14), P(0, 32), P(12, 14), P(0, 4)])
        pygame.draw.circle(d, (250, 220, 90), P(-12, 0), max(2, int(5 * s)))
        pygame.draw.circle(d, (250, 220, 90), P(12, 0), max(2, int(5 * s)))
        pygame.draw.circle(d, (30, 30, 30), P(0, 26), max(2, int(4 * s)))
    elif t == "vonk":
        for a in range(8):
            r1 = 34 if a % 2 == 0 else 16
            ang = a * math.pi / 4
            pygame.draw.line(d, (255, 210, 90), P(0, 0), P(math.cos(ang) * r1, math.sin(ang) * r1), max(2, int(4 * s)))
        pygame.draw.circle(d, (255, 140, 60), P(0, 0), int(14 * s))
        pygame.draw.circle(d, (40, 20, 10), P(-5, -3), max(1, int(3 * s)))
        pygame.draw.circle(d, (40, 20, 10), P(5, -3), max(1, int(3 * s)))
    elif t == "druide":
        pygame.draw.polygon(d, (70, 130, 70), [P(-26, 40), P(0, -10), P(26, 40)])
        pygame.draw.circle(d, (230, 200, 170), P(0, -18), int(13 * s))
        pygame.draw.polygon(d, (60, 110, 60), [P(-16, -20), P(0, -44), P(16, -20)])
        pygame.draw.line(d, (130, 90, 50), P(28, 40), P(32, -30), max(2, int(4 * s)))
        pygame.draw.circle(d, (140, 230, 120), P(32, -34), int(7 * s))
    elif t == "zwijn":
        pygame.draw.ellipse(d, (110, 80, 60), (*P(-34, -18), int(60 * s), int(40 * s)))
        pygame.draw.circle(d, (130, 96, 72), P(26, 0), int(16 * s))
        pygame.draw.ellipse(d, (200, 140, 130), (*P(34, -4), int(12 * s), int(10 * s)))
        pygame.draw.line(d, (250, 245, 230), P(30, 8), P(38, 0), max(2, int(3 * s)))
        pygame.draw.circle(d, (20, 20, 20), P(24, -6), max(1, int(3 * s)))
        for lx in (-26, -10, 6, 16):
            pygame.draw.line(d, (80, 58, 44), P(lx, 18), P(lx, 32), max(2, int(5 * s)))
    elif t == "beer":
        pygame.draw.circle(d, (120, 80, 50), P(0, 6), int(30 * s))
        pygame.draw.circle(d, (120, 80, 50), P(-24, -22), int(10 * s))
        pygame.draw.circle(d, (120, 80, 50), P(24, -22), int(10 * s))
        pygame.draw.ellipse(d, (190, 150, 110), (*P(-12, 6), int(24 * s), int(18 * s)))
        pygame.draw.circle(d, (20, 20, 20), P(0, 10), max(2, int(4 * s)))
        pygame.draw.circle(d, (20, 20, 20), P(-11, -6), max(2, int(3 * s)))
        pygame.draw.circle(d, (20, 20, 20), P(11, -6), max(2, int(3 * s)))
    elif t == "draak":
        pygame.draw.polygon(d, (180, 50, 40), [P(-8, -4), P(-42, -30), P(-30, 6), P(-44, 16)])
        pygame.draw.polygon(d, (180, 50, 40), [P(8, -4), P(42, -30), P(30, 6), P(44, 16)])
        pygame.draw.ellipse(d, (210, 70, 50), (*P(-14, -14), int(28 * s), int(46 * s)))
        pygame.draw.circle(d, (220, 80, 56), P(0, -22), int(12 * s))
        pygame.draw.circle(d, (255, 230, 80), P(-5, -24), max(1, int(3 * s)))
        pygame.draw.circle(d, (255, 230, 80), P(5, -24), max(1, int(3 * s)))
        pygame.draw.polygon(d, (255, 170, 60), [P(-6, -12), P(0, 4), P(6, -12)])
    elif t == "vuurbal":
        for r, c in ((30, (200, 60, 30)), (22, (250, 130, 40)), (12, (255, 220, 110))):
            pygame.draw.circle(d, c, P(4, 4), int(r * s))
        pygame.draw.polygon(d, (230, 90, 40), [P(-30, -30), P(-6, -10), P(-14, 4)])
    elif t == "groei":
        pygame.draw.line(d, (90, 160, 70), P(0, 38), P(0, -20), max(2, int(5 * s)))
        pygame.draw.ellipse(d, (120, 210, 100), (*P(-30, -10), int(30 * s), int(16 * s)))
        pygame.draw.ellipse(d, (120, 210, 100), (*P(0, -26), int(30 * s), int(16 * s)))
        pygame.draw.polygon(d, (250, 230, 120), [P(0, -44), P(-10, -28), P(10, -28)])
    elif t == "maan":
        pygame.draw.circle(d, (240, 235, 200), P(14, -16), int(22 * s))
        pygame.draw.circle(d, tuple(int(c * 0.55) for c in don), P(24, -22), int(18 * s))
        pygame.draw.polygon(d, (90, 90, 104), [P(-36, 40), P(-30, 6), P(-22, -6), P(-18, 8), P(-8, 40)])
        pygame.draw.polygon(d, (90, 90, 104), [P(-24, -2), P(-28, -16), P(-16, -6)])
    elif t == "ridder":
        pygame.draw.rect(d, (190, 196, 210), (*P(-20, -34), int(40 * s), int(38 * s)), border_radius=max(2, int(10 * s)))
        pygame.draw.rect(d, (40, 40, 60), (*P(-14, -18), int(28 * s), int(6 * s)))
        pygame.draw.polygon(d, (210, 190, 120), [P(-26, 10), P(26, 10), P(20, 34), P(0, 44), P(-20, 34)])
        pygame.draw.line(d, (150, 60, 60), P(0, 14), P(0, 38), max(2, int(4 * s)))
        pygame.draw.line(d, (150, 60, 60), P(-12, 24), P(12, 24), max(2, int(4 * s)))
    elif t == "uil":
        pygame.draw.ellipse(d, (140, 110, 80), (*P(-28, -30), int(56 * s), int(70 * s)))
        for ox in (-12, 12):
            pygame.draw.circle(d, (250, 240, 210), P(ox, -10), int(11 * s))
            pygame.draw.circle(d, (30, 30, 50), P(ox, -10), int(5 * s))
        pygame.draw.polygon(d, (230, 170, 60), [P(-4, 2), P(4, 2), P(0, 10)])
        pygame.draw.polygon(d, (140, 110, 80), [P(-26, -26), P(-18, -40), P(-10, -28)])
        pygame.draw.polygon(d, (140, 110, 80), [P(26, -26), P(18, -40), P(10, -28)])
    elif t == "golem":
        pygame.draw.rect(d, (70, 130, 190), (*P(-26, -20), int(52 * s), int(50 * s)), border_radius=max(2, int(8 * s)))
        pygame.draw.circle(d, (90, 160, 220), P(0, -30), int(14 * s))
        pygame.draw.rect(d, (70, 130, 190), (*P(-40, -14), int(14 * s), int(34 * s)), border_radius=4)
        pygame.draw.rect(d, (70, 130, 190), (*P(26, -14), int(14 * s), int(34 * s)), border_radius=4)
        pygame.draw.circle(d, (200, 240, 255), P(-5, -32), max(1, int(3 * s)))
        pygame.draw.circle(d, (200, 240, 255), P(5, -32), max(1, int(3 * s)))
        for bx in (-14, 4):
            pygame.draw.circle(d, (180, 220, 250), P(bx, 0), max(2, int(4 * s)))
    elif t == "engel":
        pygame.draw.polygon(d, (250, 245, 230), [P(-6, -6), P(-44, -26), P(-34, 10)])
        pygame.draw.polygon(d, (250, 245, 230), [P(6, -6), P(44, -26), P(34, 10)])
        pygame.draw.polygon(d, (240, 230, 200), [P(-16, 40), P(0, -8), P(16, 40)])
        pygame.draw.circle(d, (240, 210, 180), P(0, -16), int(11 * s))
        pygame.draw.ellipse(d, (255, 220, 90), (*P(-12, -34), int(24 * s), int(8 * s)), max(1, int(3 * s)))
    elif t == "slang":
        pts = [P(-40 + i * 8, 16 * math.sin(i * 0.9)) for i in range(11)]
        pygame.draw.lines(d, (60, 150, 140), False, pts, max(3, int(12 * s)))
        pygame.draw.circle(d, (70, 170, 160), pts[-1], int(11 * s))
        pygame.draw.circle(d, (250, 230, 90), (pts[-1][0] + int(3 * s), pts[-1][1] - int(3 * s)), max(1, int(3 * s)))
        pygame.draw.line(d, (120, 190, 240), P(-44, 34), P(44, 34), max(2, int(3 * s)))
    elif t == "ijs":
        for a in range(3):
            ang = a * math.pi / 3
            pygame.draw.line(d, (200, 235, 255), P(math.cos(ang) * 34, math.sin(ang) * 34),
                             P(-math.cos(ang) * 34, -math.sin(ang) * 34), max(2, int(5 * s)))
        pygame.draw.circle(d, (230, 245, 255), P(0, 0), int(8 * s))
    elif t == "schild":
        pygame.draw.polygon(d, (250, 230, 150), [P(-26, -30), P(26, -30), P(22, 10), P(0, 38), P(-22, 10)])
        pygame.draw.polygon(d, (255, 250, 220), [P(-16, -20), P(16, -20), P(13, 6), P(0, 24), P(-13, 6)])
    elif t == "hart":
        pygame.draw.circle(d, (230, 90, 110), P(-12, -8), int(16 * s))
        pygame.draw.circle(d, (230, 90, 110), P(12, -8), int(16 * s))
        pygame.draw.polygon(d, (230, 90, 110), [P(-27, -2), P(27, -2), P(0, 32)])
        pygame.draw.line(d, (255, 250, 250), P(0, -12), P(0, 8), max(2, int(4 * s)))
        pygame.draw.line(d, (255, 250, 250), P(-10, -2), P(10, -2), max(2, int(4 * s)))
    elif t == "boek":
        pygame.draw.polygon(d, (230, 225, 210), [P(-36, -20), P(0, -12), P(0, 28), P(-36, 20)])
        pygame.draw.polygon(d, (245, 240, 225), [P(36, -20), P(0, -12), P(0, 28), P(36, 20)])
        for ly in (-4, 4, 12):
            pygame.draw.line(d, (120, 140, 180), P(-30, ly - 6), P(-6, ly), 1)
            pygame.draw.line(d, (120, 140, 180), P(30, ly - 6), P(6, ly), 1)
        pygame.draw.circle(d, (140, 200, 255), P(0, -30), int(7 * s))
    elif t == "straal":
        pygame.draw.polygon(d, (255, 245, 180), [P(-6, -44), P(6, -44), P(22, 40), P(-22, 40)])
        pygame.draw.polygon(d, (255, 255, 235), [P(-2, -44), P(2, -44), P(8, 40), P(-8, 40)])
    else:
        pygame.draw.circle(d, lic, P(0, 0), int(20 * s))


def teken_kaart(d, sl, r, aan=True, gloed=None, hover=False):
    """Een kaart in de hand: naam, kosten, plaatje, tekst, en bij wezens kracht/leven."""
    k = KAARTEN[sl]
    don, lic = KLEUREN[k["kleur"]]
    rr = pygame.Rect(r)
    if hover:
        rr = rr.move(0, -14)
    pygame.draw.rect(d, (30, 26, 40), rr.move(4, 5), border_radius=12)
    pygame.draw.rect(d, don if aan else tuple(int(c * 0.5) for c in don), rr, border_radius=12)
    pygame.draw.rect(d, gloed or (lic if aan else (90, 84, 104)), rr, 4 if gloed else 2, border_radius=12)
    ph = int(rr.h * 0.30)
    teken_plaatje(d, sl, (rr.x + 8, rr.y + 28, rr.w - 16, ph))
    naam = naam_van(sl)
    UI.tekst(d, naam if len(naam) < 13 else naam[:12] + ".", 15, UI.TEKST, (rr.x + 10, rr.y + 6))
    pygame.draw.circle(d, (40, 90, 200), (rr.right - 16, rr.y + 16), 15)
    pygame.draw.circle(d, (180, 210, 255), (rr.right - 16, rr.y + 16), 15, 2)
    UI.tekst(d, str(k["kost"]), 18, UI.TEKST, (rr.right - 16, rr.y + 16), mid=True)
    ty = rr.y + 32 + ph
    px = 13 if rr.w < 150 else 16
    regels = UI.Backgammon._knip(None, tekst_van(sl), px, rr.w - 14)
    for stuk in regels[:(3 if k["soort"] == "wezen" else 4)]:
        UI.tekst(d, stuk, px, (250, 246, 236), (rr.x + 7, ty), vet=False)
        ty += px + 3
    if k["soort"] == "wezen":
        pygame.draw.circle(d, (200, 150, 40), (rr.x + 16, rr.bottom - 16), 14)
        UI.tekst(d, str(k["kr"]), 18, (30, 20, 10), (rr.x + 16, rr.bottom - 16), mid=True)
        pygame.draw.circle(d, (190, 50, 60), (rr.right - 16, rr.bottom - 16), 14)
        UI.tekst(d, str(k["lv"]), 18, UI.TEKST, (rr.right - 16, rr.bottom - 16), mid=True)
    else:
        UI.tekst(d, T("spreuk"), 13, lic, (rr.centerx, rr.bottom - 14), mid=True)
    return rr


def teken_rug(d, r):
    rr = pygame.Rect(r)
    pygame.draw.rect(d, (54, 44, 84), rr, border_radius=10)
    pygame.draw.rect(d, (181, 156, 255), rr, 2, border_radius=10)
    pygame.draw.circle(d, (127, 119, 221), rr.center, min(rr.w, rr.h) // 4, 3)
    pygame.draw.polygon(d, (224, 184, 90), [(rr.centerx, rr.centery - 12), (rr.centerx + 8, rr.centery),
                                            (rr.centerx, rr.centery + 12), (rr.centerx - 8, rr.centery)])


# ------------------------------------------------------------------ het spel op het scherm
class Duel:
    def __init__(self, app, niveau):
        self.app = app
        self.niveau = niveau
        self.knoppen = []
        self.score = [0, 0]
        self.mijn_stok = None             # eerst kiezen
        self.melding = ""
        self.spel = None
        self.geklikt = None
        self.klaar = False

    def nieuw_potje(self, stok=None):
        if stok:
            self.mijn_stok = stok
        if not self.mijn_stok:
            return
        ander = "bw" if self.mijn_stok == "rg" else "rg"
        self.spel = Spel(self.mijn_stok, ander, zeg=self._zeg)
        self.gekozen = None               # ("hand", h) of ("wezen", id)
        self.melding = ""
        self.klaar = False
        self.uitslag = ""
        self.comp = None                  # {"acties": [...], "t": tijd}
        self.tip = None
        self.app.geluid.speel("klik")

    def _zeg(self, wat):
        soort, i = wat
        if i == 0:
            self.melding = T(soort)

    # ---------- plekken op het scherm
    def hand_rect(self, h, n):
        tot = n * (KW + 10) - 10
        x0 = max(30, (920 - tot) // 2)
        return pygame.Rect(x0 + h * (KW + 10), 612, KW, KH)

    def veld_rect(self, speler, k, n):
        tot = n * (VW + 14) - 14
        x0 = (920 - tot) // 2
        y = 392 if speler == 0 else 196
        return pygame.Rect(x0 + k * (VW + 14), y, VW, VH)

    def held_rect(self, speler):
        return pygame.Rect(960, 560 if speler == 0 else 70, 290, 110)

    def doel_op(self, pos):
        s = self.spel
        for i in (0, 1):
            for k, w in enumerate(s.sp[i].veld):
                if self.veld_rect(i, k, len(s.sp[i].veld)).collidepoint(pos):
                    return ("wezen", i, w.id)
            if self.held_rect(i).collidepoint(pos):
                return ("held", i)
        return None

    # ---------- invoer
    def klik(self, pos):
        if not self.spel:
            return
        s = self.spel
        if self.klaar or s.beurt != 0 or self.comp:
            return
        doel = self.doel_op(pos)
        if self.gekozen:
            soort, wat = self.gekozen
            if soort == "hand":
                if doel and s.speel(0, wat, doel):
                    self.app.geluid.speel("zet")
                    self.gekozen = None
                    self.melding = ""
                    self.na_actie()
                    return
            else:
                if doel and s.val_aan(0, wat, doel):
                    self.app.geluid.speel("sla")
                    self.gekozen = None
                    self.melding = ""
                    self.na_actie()
                    return
                if doel and doel[0] == "held" or (doel and doel[1] == 1):
                    if s.heeft_wacht(1):
                        self.melding = T("moet_wacht")
                        self.app.geluid.speel("fout")
                        return
            if doel and doel[0] == "wezen" and doel[1] == 0 and soort == "wezen":
                self.gekozen = None
            elif not doel:
                self.gekozen = None
        # een kaart uit de hand?
        for h in range(len(s.sp[0].hand) - 1, -1, -1):
            if self.hand_rect(h, len(s.sp[0].hand)).collidepoint(pos):
                self.kies_hand(h)
                return
        if doel and doel[0] == "wezen" and doel[1] == 0:
            w = s.zoek(0, doel[2])
            if w.bevroren:
                self.melding = T("bevroren")
            elif w.slaapt:
                self.melding = T("slaapt")
            elif w.aangevallen:
                self.melding = T("al_aangevallen")
            elif s.aanval_doelen(0, w.id):
                self.gekozen = ("wezen", w.id)
                self.melding = T("kies_aanval")
                self.app.geluid.speel("klik")
                return
            self.app.geluid.speel("fout")

    def kies_hand(self, h):
        s = self.spel
        sl = s.sp[0].hand[h]
        k = KAARTEN[sl]
        if k["kost"] > s.sp[0].mana:
            self.melding = T("te_duur")
            self.app.geluid.speel("fout")
            return
        if k["soort"] == "wezen" and len(s.sp[0].veld) >= VELD_MAX:
            self.melding = T("veld_vol")
            self.app.geluid.speel("fout")
            return
        if k["soort"] == "spreuk" and k["doel"]:
            if not s.doelen(0, k["doel"]):
                self.app.geluid.speel("fout")
                return
            self.gekozen = ("hand", h)
            self.melding = T("kies_doel")
            self.app.geluid.speel("klik")
            return
        if s.speel(0, h):
            self.app.geluid.speel("zet")
            self.gekozen = None
            self.melding = ""
            self.na_actie()

    def toets(self, e):
        if e.key == pygame.K_ESCAPE:
            self.app.naar_menu()
        elif e.key == pygame.K_BACKSPACE:
            self.gekozen = None
            self.melding = ""
        elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.klaar:
                self.nieuw_potje()
            else:
                self.einde_beurt()
        elif e.key == pygame.K_t:
            self.geef_tip()

    def einde_beurt(self):
        if not self.spel or self.klaar or self.spel.beurt != 0 or self.comp:
            return
        self.gekozen = None
        self.tip = None
        self.melding = ""
        self.spel.einde_beurt()
        self.app.geluid.speel("klik")
        self.na_actie()

    def geef_tip(self):
        s = self.spel
        if not s or self.klaar or s.beurt != 0:
            return
        acties = computer_zetten(s, 0, 3)
        if acties:
            a = acties[0]
            self.tip = ("hand", a[1]) if a[0] == "speel" else ("wezen", a[1])
            self.melding = T("tip_kop")
            self.app.geluid.speel("goed")
        else:
            self.melding = T("einde_beurt") + "!"

    def na_actie(self):
        s = self.spel
        self.tip = None
        if s.winnaar is not None and not self.klaar:
            self.klaar = True
            if s.winnaar == 0:
                self.score[0] += 1
                self.uitslag = T("jij_wint")
                self.app.geluid.speel("win")
            elif s.winnaar == 1:
                self.score[1] += 1
                self.uitslag = T("comp_wint")
                self.app.geluid.speel("verlies")
            else:
                self.uitslag = UI.T("gelijk") if "gelijk" in getattr(UI, "TX", {}) else "="

    def update(self):
        s = self.spel
        if not s or self.klaar or s.beurt != 1:
            return
        if self.comp is None:
            self.comp = {"acties": computer_zetten(s, 1, self.niveau), "t": time.time() + 0.9}
            self.melding = ""
            return
        if time.time() < self.comp["t"]:
            return
        if self.comp["acties"]:
            a = self.comp["acties"].pop(0)
            ok = s.speel(1, a[1], a[2]) if a[0] == "speel" else s.val_aan(1, a[1], a[2])
            if ok:
                self.app.geluid.speel("zet" if a[0] == "speel" else "sla")
                self.laatste_comp = a
            self.comp["t"] = time.time() + 0.9
            self.na_actie()
            return
        self.comp = None
        if s.winnaar is None:
            s.einde_beurt()
            self.na_actie()

    # ---------- tekenen
    def teken(self, d, muis):
        d.fill(UI.ACHTER)
        self.knoppen = []
        if not self.mijn_stok:
            self.teken_keuze(d, muis)
            return
        s = self.spel
        UI.tekst(d, T("duel"), 34, UI.ACCENT, (30, 10))
        UI.tekst(d, "%s %d  -  %d %s" % (UI.T("jij"), self.score[0], self.score[1], UI.T("computer")), 24, UI.GOUD, (260, 18))
        # speelveld
        pygame.draw.rect(d, (30, 26, 44), (20, 186, 900, 360), border_radius=18)
        pygame.draw.line(d, UI.RAND, (40, 366), (900, 366), 2)
        hulp = self.app.hulp
        mijn = s.beurt == 0 and not self.klaar and not self.comp
        doelen = []
        if self.gekozen and mijn:
            if self.gekozen[0] == "hand":
                k = KAARTEN[s.sp[0].hand[self.gekozen[1]]]
                doelen = s.doelen(0, k["doel"])
            else:
                doelen = s.aanval_doelen(0, self.gekozen[1])
        # tegenstander: hand (ruggen)
        n1 = len(s.sp[1].hand)
        for h in range(n1):
            teken_rug(d, (300 + h * 44, 92, 60, 84))
        # velden
        for i in (1, 0):
            veld = s.sp[i].veld
            for k, w in enumerate(veld):
                r = self.veld_rect(i, k, len(veld))
                doel = ("wezen", i, w.id)
                gloed = None
                if doel in doelen:
                    gloed = UI.GOUD
                elif i == 0 and mijn and hulp and s.aanval_doelen(0, w.id) and not self.gekozen:
                    gloed = UI.GROEN
                if self.gekozen == ("wezen", w.id):
                    gloed = UI.ACCENT
                if self.tip == ("wezen", w.id):
                    gloed = UI.GOUD
                self.teken_wezen(d, s, i, w, r, gloed, r.collidepoint(muis))
        # helden
        for i in (1, 0):
            r = self.held_rect(i)
            doel = ("held", i)
            pygame.draw.rect(d, UI.VAK, r, border_radius=16)
            pygame.draw.rect(d, UI.GOUD if doel in doelen else (UI.ACCENT if s.beurt == i and not self.klaar else UI.RAND), r,
                             4 if doel in doelen or s.beurt == i else 2, border_radius=16)
            naam = UI.T("jij") if i == 0 else UI.T("computer")
            UI.tekst(d, naam, 26, UI.TEKST, (r.x + 16, r.y + 10))
            stok = T("stok_rg") if s.sp[i].stok_sl == "rg" else T("stok_bw")
            UI.tekst(d, stok, 16, UI.ZACHT, (r.x + 16, r.y + 44), vet=False)
            pygame.draw.circle(d, (190, 50, 60), (r.right - 44, r.y + 34), 28)
            UI.tekst(d, str(max(0, s.sp[i].levens)), 28, UI.TEKST, (r.right - 44, r.y + 34), mid=True)
            # mana-bolletjes
            for m in range(s.sp[i].max_mana):
                kl = (60, 120, 230) if m < s.sp[i].mana else (50, 50, 70)
                pygame.draw.circle(d, kl, (r.x + 22 + m * 19, r.y + 86), 8)
            UI.tekst(d, "%s %d · %s %d" % (T("stok"), len(s.sp[i].stok), T("hand"), len(s.sp[i].hand)), 14, UI.ZACHT,
                     (r.right - 14, r.y + 74), rechts=True, vet=False)
        # mijn hand
        hand = s.sp[0].hand
        hov = None
        for h in range(len(hand) - 1, -1, -1):
            if self.hand_rect(h, len(hand)).collidepoint(muis):
                hov = h
                break
        for h, sl in enumerate(hand):
            r = self.hand_rect(h, len(hand))
            kan = mijn and s.kan_spelen(0, h)
            gloed = None
            if self.gekozen == ("hand", h):
                gloed = UI.ACCENT
            elif self.tip == ("hand", h):
                gloed = UI.GOUD
            elif kan and hulp:
                gloed = UI.GROEN
            teken_kaart(d, sl, r, aan=kan or not mijn, gloed=gloed, hover=(h == hov or self.gekozen == ("hand", h)))
        # vergrote kaart als je erboven hangt (grote letters)
        if hov is not None and not self.gekozen:
            teken_kaart(d, hand[hov], pygame.Rect(960, 196, 176, 250), aan=True)
        # tekst rechts
        y = 456 if hov is None or self.gekozen else 456
        regels = []
        if self.klaar:
            regels.append(self.uitslag)
        elif s.beurt == 1 or self.comp:
            regels.append(T("comp_denkt"))
        elif self.melding:
            regels.append(self.melding)
        else:
            regels.append(T("jouw_beurt"))
        if hov is None or self.gekozen:
            yy = 200
            for regel in regels:
                for stuk in UI.Backgammon._knip(None, regel, 21, 290):
                    UI.tekst(d, stuk, 21, UI.GOUD if (self.klaar or self.melding) else UI.TEKST, (960, yy))
                    yy += 28
        # knoppen
        if self.klaar:
            self.knoppen.append(UI.Knop((960, 470, 290, 64), UI.T("nog"), self.nieuw_potje, UI.GROEN, 26))
        else:
            self.knoppen.append(UI.Knop((960, 470, 290, 64), T("einde_beurt"), self.einde_beurt, UI.GOUD, 26, aan=mijn))
        self.knoppen.append(UI.Knop((960, 690, 140, 52), UI.T("menu"), self.app.naar_menu, UI.VAK, 22))
        self.knoppen.append(UI.Knop((1110, 690, 140, 52), UI.T("regels"), lambda: setattr(self.app, "toon_regels", True), UI.VAK, 20))
        self.knoppen.append(UI.Knop((960, 748, 140, 44), UI.T("tip"), self.geef_tip, UI.VAK, 20, aan=mijn))
        self.knoppen.append(UI.Knop((1110, 748, 140, 44), "%s: %s" % (UI.T("hulp"), UI.T("aan") if hulp else UI.T("uitm")),
                                    self.app.wissel_hulp, UI.VAK, 18))
        for k in self.knoppen:
            k.teken(d, muis)
        UI.tekst(d, T("toetsen_duel"), 14, UI.ZACHT, (30, 786), vet=False)

    def teken_wezen(self, d, s, i, w, r, gloed, hover):
        k = KAARTEN[w.sl]
        don, lic = KLEUREN[k["kleur"]]
        rr = pygame.Rect(r)
        flits = time.time() - w.flits < 0.35
        if flits:
            rr = rr.move(random.randint(-4, 4), 0)
        pygame.draw.rect(d, (20, 16, 30), rr.move(3, 4), border_radius=14)
        pygame.draw.rect(d, don, rr, border_radius=14)
        teken_plaatje(d, w.sl, (rr.x + 6, rr.y + 24, rr.w - 12, rr.h - 58))
        if w.wacht:
            pygame.draw.rect(d, (250, 230, 150), rr, 5, border_radius=14)
        pygame.draw.rect(d, gloed or lic, rr, 4 if gloed else 2, border_radius=14)
        naam = naam_van(w.sl)
        UI.tekst(d, naam if len(naam) < 13 else naam[:12] + ".", 14, UI.TEKST, (rr.x + 8, rr.y + 4))
        kr = kracht(s.sp[i], w)
        pygame.draw.circle(d, (200, 150, 40), (rr.x + 18, rr.bottom - 18), 16)
        UI.tekst(d, str(kr), 20, (30, 20, 10), (rr.x + 18, rr.bottom - 18), mid=True)
        pygame.draw.circle(d, (190, 50, 60), (rr.right - 18, rr.bottom - 18), 16)
        UI.tekst(d, str(max(0, w.lv)), 20, UI.TEKST, (rr.right - 18, rr.bottom - 18), mid=True)
        if w.bevroren:
            ijs = pygame.Surface((rr.w, rr.h), pygame.SRCALPHA)
            ijs.fill((170, 220, 255, 90))
            d.blit(ijs, rr.topleft)
        if w.slaapt and i == 0 and not w.bevroren:
            UI.tekst(d, "z z", 18, UI.ZACHT, (rr.right - 30, rr.y + 26))
        if flits:
            pygame.draw.rect(d, (255, 90, 80), rr, 4, border_radius=14)
        if hover:
            # uitleg onder de muis
            uit = tekst_van(w.sl)
            bx = min(rr.x, 920 - 260)
            by = rr.bottom + 6 if i == 1 else rr.y - 64
            pygame.draw.rect(d, UI.VAK, (bx, by, 260, 58), border_radius=10)
            pygame.draw.rect(d, UI.RAND, (bx, by, 260, 58), 2, border_radius=10)
            yy = by + 6
            for stuk in UI.Backgammon._knip(None, uit, 15, 244)[:3]:
                UI.tekst(d, stuk, 15, UI.TEKST, (bx + 8, yy), vet=False)
                yy += 18

    def teken_keuze(self, d, muis):
        UI.tekst(d, T("duel"), 48, UI.ACCENT, (UI.W // 2, 70), mid=True)
        UI.tekst(d, T("kies_stok"), 30, UI.TEKST, (UI.W // 2, 140), mid=True)
        for n, (sl, voorbeelden) in enumerate((("rg", ("wolf", "draak", "vuurbal")), ("bw", ("uil", "engel", "schild")))):
            x = 140 + n * 520
            r = pygame.Rect(x, 200, 480, 460)
            hover = r.collidepoint(muis)
            pygame.draw.rect(d, UI.VAK, r, border_radius=20)
            pygame.draw.rect(d, UI.ACCENT if hover else UI.RAND, r, 4 if hover else 2, border_radius=20)
            for j, v in enumerate(voorbeelden):
                teken_kaart(d, v, pygame.Rect(x + 30 + j * 145, 230, KW, KH), aan=True)
            UI.tekst(d, T("stok_" + sl), 32, UI.GOUD, (r.centerx, 440), mid=True)
            yy = 486
            for stuk in UI.Backgammon._knip(None, T("stok_%s_sub" % sl), 22, 420):
                UI.tekst(d, stuk, 22, UI.TEKST, (r.centerx, yy), mid=True, vet=False)
                yy += 30
            self.knoppen.append(UI.Knop((x + 90, 590, 300, 56), T("stok_" + sl), lambda s_=sl: self.nieuw_potje(s_), UI.GROEN, 24))
        self.knoppen.append(UI.Knop((40, UI.H - 90, 200, 60), UI.T("terug"), self.app.naar_menu, UI.VAK, 24))
        for k in self.knoppen:
            k.teken(d, muis)

    def stop(self):
        pass


# ------------------------------------------------------------------ zelftest (zonder scherm)
if __name__ == "__main__":
    import collections
    uitslag = collections.Counter()
    for n in range(60):
        s = Spel("rg", "bw", zaad=n)
        stappen = 0
        while s.winnaar is None and stappen < 200:
            for a in computer_zetten(s, s.beurt, 3 if s.beurt == 0 else 2):
                ok = s.speel(s.beurt, a[1], a[2]) if a[0] == "speel" else s.val_aan(s.beurt, a[1], a[2])
                assert ok, a
                if s.winnaar is not None:
                    break
            if s.winnaar is None:
                s.einde_beurt()
            stappen += 1
        uitslag[s.winnaar] += 1
    print("60 potjes computer tegen computer (rg niveau 3 tegen bw niveau 2):", dict(uitslag))
