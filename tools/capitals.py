"""Capital city coordinates for the capital dots (shown in the capitals games once a country or state is answered).

Looks each capital up in Natural Earth's populated places (public domain) by name and country. Countries with
several official capitals (the ones with a capital note, e.g. South Africa) get every one. Used by build_data.py
and build_us.py.
"""
import json
import pathlib
import re
import unicodedata
import urllib.request

DL = pathlib.Path(__file__).resolve().parent / "downloads"
SOURCE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_populated_places_simple.geojson"

# places Natural Earth doesn't have (or spells too differently to match): [lon, lat]
MANUAL = {
    "Ciudad de la Paz": [10.82, 1.59],          # Equatorial Guinea's new capital (Oyala)
    "Ngerulmud": [134.624, 7.501],
    "Sri Jayawardenepura Kotte": [79.887, 6.888],
    "Andorra la Vella": [1.521, 42.507],
    "Copenhagen": [12.568, 55.676],
    "South Tarawa": [172.979, 1.329],
    "Yaren": [166.920, -0.547],
    "East Jerusalem": [35.235, 31.783],
    "City of San Marino": [12.447, 43.936],
}


def norm(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", "", s.replace("saint", "st"))


_places = None


def places():
    global _places
    if _places is None:
        p = DL / "ne_places.geojson"
        if not p.exists():
            DL.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(SOURCE, p)
        _places = [f["properties"] for f in json.loads(p.read_text(encoding="utf8"))["features"]]
    return _places


def official_capitals(c):
    """The capital cities to mark: every capital named in the capital note (not former capitals or commercial or
    economic centres), else the first capital."""
    if c.get("capitalNote"):
        pairs = re.findall(r"([^,(]+?)\s*\(([^)]*)\)", c["capitalNote"])
        return [city.strip() for city, role in pairs if not re.search(r"former|commercial|economic", role)]
    return c["capitals"][:1]


def find(city, a2=None, adm1=None, near=None):
    if city in MANUAL:
        return MANUAL[city]
    n = norm(city)
    hits = []
    for p in places():
        names = [p.get("name"), p.get("nameascii")] + (p.get("namealt") or "").split("|")
        if n not in {norm(x) for x in names if x}:
            continue
        score = 0
        if a2 and p.get("iso_a2") == a2:
            score += 10
        if adm1 and p.get("adm1name") == adm1:
            score += 10
        if "capital" in (p.get("featurecla") or "").lower():
            score += 3
        if near:
            score -= abs(p["latitude"] - near[0]) / 30 + abs(p["longitude"] - near[1]) / 30
        hits.append((score, p))
    if not hits:
        return None
    best = max(hits, key=lambda h: h[0])[1]
    return [round(best["longitude"], 3), round(best["latitude"], 3)]


def add_capital_coords(items, country_code=None):
    """Adds "capLL": [[lon, lat], ...] to each country (or state, with country_code="US"). Prints any misses."""
    missing = []
    for c in items:
        pts = []
        for city in official_capitals(c):
            if country_code:
                ll = find(city, a2=country_code, adm1=c["name"])
            else:
                ll = find(city, a2=c.get("a2"), near=c.get("ll"))
            if ll:
                pts.append(ll)
            else:
                missing.append(f"{c['name']}: {city}")
        c["capLL"] = pts
    if missing:
        print("capitals not found:", "; ".join(missing))
