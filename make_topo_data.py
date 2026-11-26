# -*- coding: utf-8 -*-
"""Maakt assets/topo_nl.json voor Topografie (eenmalig, in de cloud).
Bronnen (open data): CBS gebiedsindelingen 2026 via cartomap/nl (provincies, gemeentes),
plaatsen + inwoners uit GeoNames (CC-BY 4.0) via het pakket geonamescache."""
import json
import math
import sys

import geonamescache

BRON = sys.argv[1] if len(sys.argv) > 1 else "/tmp/topo"
LAT0, LON0 = 53.62, 3.30          # linksboven
K = 266.0                         # pixels per graad breedte
CX = math.cos(math.radians(52.2))
MX, MY = 136, 22                  # waar de kaart begint op het 1280x800-scherm


def xy(lon, lat):
    return round(MX + (lon - LON0) * CX * K, 1), round(MY + (LAT0 - lat) * K, 1)


def ringen(g):
    ps = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    return [[xy(*q) for q in p[0]] for p in ps if len(p[0]) >= 4]


def oppervlak_midden(rs):
    """zwaartepunt van de grootste ring"""
    r = max(rs, key=lambda r: abs(_opp(r)))
    a = _opp(r)
    cx = cy = 0
    for (x1, y1), (x2, y2) in zip(r, r[1:] + r[:1]):
        f = x1 * y2 - x2 * y1
        cx += (x1 + x2) * f
        cy += (y1 + y2) * f
    return round(cx / (6 * a), 1), round(cy / (6 * a), 1)


def _opp(r):
    return sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(r, r[1:] + r[:1])) / 2


def binnen(pt, r):
    x, y = pt
    c = False
    for (x1, y1), (x2, y2) in zip(r, r[1:] + r[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def in_welke(pt, items):
    for it in items:
        if any(binnen(pt, r) for r in it["r"]):
            return it["n"]
    # net buiten de kust: dichtstbijzijnde
    return min(items, key=lambda it: (it["m"][0] - pt[0]) ** 2 + (it["m"][1] - pt[1]) ** 2)["n"]


prov = []
for f in json.load(open(BRON + "/provincie_2026.geojson", encoding="utf-8"))["features"]:
    rs = ringen(f["geometry"])
    prov.append({"n": f["properties"]["statnaam"], "r": rs, "m": oppervlak_midden(rs)})

NAAM_GM = {"'s-Gravenhage": "Den Haag ('s-Gravenhage)"}
gem = []
for f in json.load(open(BRON + "/gemeente_2026.geojson", encoding="utf-8"))["features"]:
    rs = ringen(f["geometry"])
    m = oppervlak_midden(rs)
    n = f["properties"]["statnaam"]
    gem.append({"n": NAAM_GM.get(n, n), "r": rs, "m": m, "p": in_welke(m, prov)})

WEG = {"Amsterdam-Zuidoost", "Leidsche Rijn", "Hoogvliet", "Ypenburg", "Groot IJsselmonde", "Ommoord", "Scheveningen",
       "De Meern", "Tongelre", "Korrewegwijk", "Merenwijk", "Schiebroek", "Maaspoort", "Lindenholt", "Hoge Vucht",
       "Wisch", "Cranendonck", "Velsen-Zuid", "Zaanstad", "Blerick", "Glanerbrug", "Velserbroek", "Borssele",
       "Benthuizen", "Hoofddorp-dummy"}
HERNOEM = {"The Hague": "Den Haag", "Almere Stad": "Almere", "Noordwijk-Binnen": "Noordwijk", "Katwijk aan Zee": "Katwijk",
           "Loon op Zand": "Kaatsheuvel"}
plaatsen = {}
for c in geonamescache.GeonamesCache(min_city_population=15000).get_cities().values():
    if c["countrycode"] != "NL" or c["name"] in WEG:
        continue
    n = HERNOEM.get(c["name"], c["name"])
    pt = xy(c["longitude"], c["latitude"])
    if n not in plaatsen or plaatsen[n]["i"] < c["population"]:
        plaatsen[n] = {"n": n, "m": pt, "i": c["population"], "p": in_welke(pt, prov)}
pl = sorted(plaatsen.values(), key=lambda v: -v["i"])

HOOFD = {"Groningen": "Groningen", "Fryslân": "Leeuwarden", "Drenthe": "Assen", "Overijssel": "Zwolle",
         "Flevoland": "Lelystad", "Gelderland": "Arnhem", "Utrecht": "Utrecht", "Noord-Holland": "Haarlem",
         "Zuid-Holland": "Den Haag", "Zeeland": "Middelburg", "Noord-Brabant": "'s-Hertogenbosch", "Limburg": "Maastricht"}
for p in prov:
    p["h"] = HOOFD[p["n"]]
    assert p["h"] in plaatsen, p["h"]

uit = {"bron": "CBS gebiedsindeling 2026 (cartomap/nl), GeoNames CC-BY 4.0", "k": K,
       "prov": prov, "gem": gem, "plaats": pl}
json.dump(uit, open(sys.argv[2] if len(sys.argv) > 2 else "assets/topo_nl.json", "w", encoding="utf-8"),
          ensure_ascii=False, separators=(",", ":"))
print(len(prov), "provincies,", len(gem), "gemeentes,", len(pl), "plaatsen")
print([(p["n"], p["p"]) for p in pl[:12]])
xs = [x for it in prov for r in it["r"] for x, _ in r]
ys = [y for it in prov for r in it["r"] for _, y in r]
print("x", min(xs), max(xs), "y", min(ys), max(ys))
