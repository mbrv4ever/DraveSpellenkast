# -*- coding: utf-8 -*-
"""Backgammon - de spelregels (zonder plaatjes), zodat ze ook voor de computer en online te gebruiken zijn.

Bord: 24 punten, index 0..23. Positief = stenen van WIT (speler 0), negatief = ZWART (speler 1).
Wit loopt van 23 naar 0 (thuis = 0..5), zwart loopt van 0 naar 23 (thuis = 18..23).
Een zet = (van, naar). van = "bar" of 0..23, naar = 0..23 of "uit".
Copyright (C) 2026 Dravenlock (Roger & Claudio). GNU GPL v3.0.
"""
import random

BAR, UIT = "bar", "uit"


def beginstand():
    b = [0] * 24
    b[23], b[12], b[7], b[5] = 2, 5, 3, 5           # wit
    b[0], b[11], b[16], b[18] = -2, -5, -3, -5     # zwart
    return {"bord": b, "bar": [0, 0], "uit": [0, 0]}


def kopie(s):
    return {"bord": list(s["bord"]), "bar": list(s["bar"]), "uit": list(s["uit"])}


def teken(sp):
    return 1 if sp == 0 else -1


def eigen(s, sp, p):
    return s["bord"][p] * teken(sp) > 0


def aantal(s, sp, p):
    return max(0, s["bord"][p] * teken(sp))


def thuis(sp):
    return range(0, 6) if sp == 0 else range(18, 24)


def alles_thuis(s, sp):
    if s["bar"][sp]:
        return False
    for p in range(24):
        if eigen(s, sp, p) and p not in thuis(sp):
            return False
    return True


def doel(sp, van, d):
    """Waar een steen uitkomt met worp d (kan buiten het bord vallen: <0 of >23)."""
    if van == BAR:
        return 24 - d if sp == 0 else d - 1
    return van - d if sp == 0 else van + d


def afstand_uit(sp, p):
    """Hoeveel ogen een steen op punt p nodig heeft om precies uit te gaan."""
    return p + 1 if sp == 0 else 24 - p


def mag_landen(s, sp, p):
    return s["bord"][p] * teken(sp) >= -1          # leeg, eigen, of 1 steen van de ander (slaan)


def stap(s, sp, van, d):
    """Geeft de zet (van, naar) voor één dobbelsteen, of None als het niet mag."""
    if s["bar"][sp] and van != BAR:
        return None
    if van == BAR:
        if not s["bar"][sp]:
            return None
    elif not eigen(s, sp, van):
        return None
    n = doel(sp, van, d)
    if 0 <= n <= 23:
        return (van, n) if mag_landen(s, sp, n) else None
    # uitspelen
    if van == BAR or not alles_thuis(s, sp):
        return None
    nodig = afstand_uit(sp, van)
    if d == nodig:
        return (van, UIT)
    if d > nodig:                                   # hogere worp mag alleen als er geen steen verder weg staat
        verder = range(van + 1, 6) if sp == 0 else range(18, van)
        if not any(eigen(s, sp, q) for q in verder):
            return (van, UIT)
    return None


def doe(s, sp, zet):
    """Voert één zet uit op een kopie. Geeft (nieuwe stand, geslagen ja/nee)."""
    s = kopie(s)
    van, naar = zet
    t = teken(sp)
    if van == BAR:
        s["bar"][sp] -= 1
    else:
        s["bord"][van] -= t
    geslagen = False
    if naar == UIT:
        s["uit"][sp] += 1
    else:
        if s["bord"][naar] == -t:                   # 1 steen van de ander: slaan
            s["bord"][naar] = 0
            s["bar"][1 - sp] += 1
            geslagen = True
        s["bord"][naar] += t
    return s, geslagen


def bronnen(s, sp):
    return [BAR] if s["bar"][sp] else [p for p in range(24) if eigen(s, sp, p)]


def reeksen(s, sp, worp, uniek=True, stenen=None):
    """Alle mogelijke volledige beurten (lijsten van zetten) die de regels toestaan.
    Regels: zoveel mogelijk dobbelstenen gebruiken; kan er maar één, dan de hoogste als dat kan.
    stenen = de dobbelstenen die nog over zijn (voor halverwege een beurt); anders volgt het uit de worp."""
    if stenen is None:
        stenen = [worp[0]] * 4 if worp[0] == worp[1] else list(worp)
    stenen = list(stenen)
    uit = {}

    def zoek(st, over, pad):
        verder = False
        geprobeerd = set()
        for i, d in enumerate(over):
            if d in geprobeerd:
                continue
            geprobeerd.add(d)
            for b in bronnen(st, sp):
                z = stap(st, sp, b, d)
                if z:
                    verder = True
                    nieuw, _ = doe(st, sp, z)
                    zoek(nieuw, over[:i] + over[i + 1:], pad + [(z, d)])
        if not verder:
            sleutel = tuple(z for z, _ in pad)
            uit[sleutel] = (pad, st)

    zoek(s, stenen, [])
    if not uit:
        return []
    maxlen = max(len(k) for k in uit)
    if maxlen == 0:
        return []
    goed = [(k, v) for k, v in uit.items() if len(k) == maxlen]
    if maxlen == 1 and len(set(stenen)) > 1:
        hoog = max(stenen)
        met_hoog = [(k, v) for k, v in goed if v[0][0][1] == hoog]
        if met_hoog:
            goed = met_hoog
    # verschillende volgordes die op dezelfde eindstand uitkomen tellen als één
    gezien, lijst = set(), []
    for k, (pad, st) in goed:
        eind = (tuple(st["bord"]), tuple(st["bar"]), tuple(st["uit"]))
        if uniek and eind in gezien and maxlen > 0:
            continue
        gezien.add(eind)
        lijst.append([z for z, _ in pad])
    return lijst


def mogelijke_eerste_zetten(s, sp, over_stenen, alle_reeksen, al_gedaan):
    """Welke enkele zetten nu mogen, gegeven de zetten die al gedaan zijn in deze beurt.
    Een zet mag als er een geldige volledige beurt is die met deze zetten begint."""
    n = len(al_gedaan)
    goed = set()
    for r in alle_reeksen:
        if len(r) > n and r[:n] == al_gedaan:
            goed.add(r[n])
    return goed


def worp_voor_zet(sp, zet, over):
    """Welke dobbelsteen (uit 'over') hoort bij deze zet. Bij uitspelen met een hogere worp: de kleinste die past."""
    van, naar = zet
    if naar == UIT:
        nodig = afstand_uit(sp, van)
        kand = sorted(d for d in over if d >= nodig)
        return kand[0] if kand else None
    if van == BAR:
        d = 24 - naar if sp == 0 else naar + 1
    else:
        d = van - naar if sp == 0 else naar - van
    return d if d in over else None


def winnaar(s):
    for sp in (0, 1):
        if s["uit"][sp] >= 15:
            return sp
    return None


def soort_winst(s, sp):
    """1 = gewoon, 2 = gammon (ander nog geen steen uit), 3 = backgammon (ander ook nog op bar of in jouw thuis)."""
    ander = 1 - sp
    if s["uit"][ander] > 0:
        return 1
    if s["bar"][ander] or any(eigen(s, ander, p) for p in thuis(sp)):
        return 3
    return 2


def pips(s, sp):
    tot = s["bar"][sp] * 25
    for p in range(24):
        n = aantal(s, sp, p)
        if n:
            tot += n * afstand_uit(sp, p)
    return tot


# ------------------------------------------------------------------ de computer
def _waarde(s, sp):
    """Hoe goed is deze stand voor speler sp (hoger = beter). Eenvoudige, maar slimme vuistregels."""
    ander = 1 - sp
    w = (pips(s, ander) - pips(s, sp)) * 1.0
    w += s["uit"][sp] * 6 - s["uit"][ander] * 6
    w += s["bar"][ander] * 14 - s["bar"][sp] * 16
    # waar staat de ander (om blots te beoordelen)
    ander_stenen = [p for p in range(24) if eigen(s, ander, p)] + ([BAR] if s["bar"][ander] else [])
    race = True
    for p in range(24):
        if eigen(s, sp, p) and any(
                (q == BAR) or (sp == 0 and q < p) or (sp == 1 and q > p) for q in ander_stenen):
            race = False
            break
    for p in range(24):
        n = aantal(s, sp, p)
        if n >= 2:
            w += 3.5 if p in thuis(sp) else 2.0     # gemaakte punten
            if n > 4:
                w -= (n - 4) * 0.6                   # niet alles op één hoop
        elif n == 1 and not race:
            # blot: hoe dichter de ander erbij staat, hoe gevaarlijker
            gevaar = 0
            for q in ander_stenen:
                if q == BAR:
                    afst = (24 - p) if sp == 1 else (p + 1)
                else:
                    afst = (p - q) if sp == 1 else (q - p)
                if 1 <= afst <= 12:
                    gevaar += 3 if afst <= 6 else 1
            w -= min(10, gevaar) * (1.4 if p in thuis(sp) else 1.0)
    # aaneengesloten blokkade
    rij, beste = 0, 0
    for p in range(24):
        if aantal(s, sp, p) >= 2:
            rij += 1
            beste = max(beste, rij)
        else:
            rij = 0
    w += beste * beste * 0.8
    return w


OPENING = {  # bekende goede eerste zetten (voor wit, punt = index + 1)
    (3, 1): [(7, 4), (5, 4)], (4, 2): [(7, 3), (5, 3)], (5, 3): [(7, 2), (5, 2)], (6, 1): [(12, 6), (7, 6)],
    (6, 4): [(23, 17), (12, 8)], (6, 5): [(23, 17), (17, 12)], (6, 2): [(23, 17), (12, 10)], (6, 3): [(23, 17), (12, 9)],
    (5, 4): [(23, 19), (12, 7)], (5, 2): [(12, 7), (12, 10)], (5, 1): [(12, 7), (5, 4)], (4, 3): [(12, 8), (12, 9)],
    (4, 1): [(23, 22), (12, 8)], (3, 2): [(23, 20), (12, 10)], (2, 1): [(12, 10), (5, 4)],
}


def _eigen_begin(s, sp):
    b = beginstand()["bord"]
    return not s["bar"][sp] and all((s["bord"][p] * teken(sp) > 0) == (b[p] * teken(sp) > 0) and
                                    (s["bord"][p] if s["bord"][p] * teken(sp) > 0 else 0) == (b[p] if b[p] * teken(sp) > 0 else 0)
                                    for p in range(24))


def computer_beurt(s, sp, worp, niveau=2, rnd=None, stenen=None):
    """Kiest de beste beurt. niveau 0 = oefenen (vaak een zwakke keuze), 1 = makkelijk, 2 = goed."""
    rnd = rnd or random
    rs = reeksen(s, sp, worp, stenen=stenen)
    sleutel = (max(worp), min(worp))
    if niveau >= 1 and stenen is None and worp[0] != worp[1] and sleutel in OPENING and _eigen_begin(s, sp):
        boek = OPENING[sleutel] if sp == 0 else [(23 - a, 23 - b) for a, b in OPENING[sleutel]]
        alle = reeksen(s, sp, worp, uniek=False)
        if boek in alle:
            return list(boek)
        if list(reversed(boek)) in alle:
            return list(reversed(boek))
    if not rs:
        return []
    scores = []
    for r in rs:
        st = s
        for z in r:
            st, _ = doe(st, sp, z)
        scores.append((_waarde(st, sp), r))
    scores.sort(key=lambda x: -x[0])
    if niveau <= 0 and len(scores) > 1 and rnd.random() < 0.7:
        return scores[rnd.randint(len(scores) // 2, len(scores) - 1)][1]
    if niveau <= 1 and len(scores) > 2 and rnd.random() < 0.35:
        return scores[rnd.randint(1, min(3, len(scores) - 1))][1]
    return scores[0][1]


def gooi(rnd=None):
    rnd = rnd or random
    return (rnd.randint(1, 6), rnd.randint(1, 6))


def in_gevaar(s, sp):
    """Punten waar speler sp één steen heeft die de ander rechtstreeks kan slaan (1..12 ogen weg)."""
    ander = 1 - sp
    bron = [p for p in range(24) if eigen(s, ander, p)] + ([BAR] if s["bar"][ander] else [])
    uit = set()
    for p in range(24):
        if aantal(s, sp, p) != 1:
            continue
        for q in bron:
            if q == BAR:
                afst = (24 - p) if ander == 0 else (p + 1)
            else:
                afst = (q - p) if ander == 0 else (p - q)
            if 1 <= afst <= 12:
                uit.add(p)
                break
    return uit


def tip(s, sp, worp, stenen):
    """De beste rest-beurt + een korte uitleg (de reden kijkt naar de hele rest van de beurt)."""
    r = computer_beurt(s, sp, worp, niveau=2, stenen=stenen)
    if not r:
        return None, ""
    st, sloeg = s, False
    for z in r:
        st, g = doe(st, sp, z)
        sloeg = sloeg or g
    nieuw_punt = any(aantal(st, sp, p) >= 2 and aantal(s, sp, p) < 2 for p in range(24))
    gevaar_voor, gevaar_na = len(in_gevaar(s, sp)), len(in_gevaar(st, sp))
    if r[0][0] == BAR:
        reden = "bar"
    elif any(z[1] == UIT for z in r):
        reden = "uit"
    elif sloeg:
        reden = "sla"
    elif nieuw_punt:
        reden = "dicht"
    elif gevaar_na < gevaar_voor:
        reden = "veilig"
    else:
        reden = "vooruit"
    return r[0], reden
