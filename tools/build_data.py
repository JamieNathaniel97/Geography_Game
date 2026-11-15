"""Builds the app's bundled data files in data/.

  data/world-50m.json   detailed country shapes (Natural Earth 1:50m), used when the map is still
  data/world-110m.json  light country shapes (1:110m), used while the globe is spinning
  data/countries.json   the 197 quiz countries: names, capitals, continents, Caribbean tag

Fixes applied to the shapes (see PLAN.md):
  - Kosovo gets the ID "XKX"; Somaliland merges into Somalia, N. Cyprus into Cyprus.
  - Overseas parts of France and the Netherlands, Tokelau (NZ) and Ashmore Reef (Australia)
    become separate territories (grey, untappable).
  - Every geometry without a quiz country is a territory, with an ID starting "T-".

Run from the repo root:  python tools/build_data.py
Downloads are cached in tools/downloads/ (git-ignored).
"""
import json
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DL = ROOT / "tools" / "downloads"
OUT = ROOT / "data"
SOURCES = {
    "countries-50m.json": "https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-50m.json",
    "countries-110m.json": "https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-110m.json",
    "world-countries.json": "https://cdn.jsdelivr.net/npm/world-countries@5.1.0/countries.json",
}
CARIBBEAN = set("ATG BHS BRB CUB DMA DOM GRD HTI JAM KNA LCA VCT TTO".split())
EXTRA = ("VAT", "PSE", "UNK", "TWN")  # non-UN-members included in the quiz (UNK = Kosovo)

# Extra names accepted in the naming games: current names, short forms and nicknames only (no former names
# such as Swaziland, Burma or Macedonia; decided 2026-11-15). Each country's common and official names
# from the source data are accepted as well.
ALT = {
    "USA": ["USA", "US", "America", "United States of America"],
    "GBR": ["UK", "Britain", "Great Britain"],
    "ARE": ["UAE", "Emirates"],
    "COD": ["DRC", "DR Congo", "Congo-Kinshasa", "Congo Kinshasa"],
    "COG": ["Congo", "Congo-Brazzaville", "Congo Brazzaville"],
    "CAF": ["CAR"],
    "CIV": ["Ivory Coast", "Cote d'Ivoire"],
    "CZE": ["Czech Republic"],
    "TLS": ["East Timor"],
    "PNG": ["PNG"],
    "NZL": ["NZ"],
    "SAU": ["KSA", "Saudi"],
    "BIH": ["Bosnia", "BiH"],
    "VAT": ["Vatican", "Holy See"],
    "NLD": ["Holland"],
    "KNA": ["St Kitts", "Saint Kitts", "St Kitts and Nevis"],
    "VCT": ["St Vincent", "Saint Vincent"],
    "LCA": ["St Lucia"],
    "STP": ["Sao Tome"],
    "TTO": ["Trinidad"],
    "ATG": ["Antigua"],
    "CPV": ["Cape Verde"],
    "TUR": ["Turkey", "Turkiye"],
    "GMB": ["The Gambia"],
    "BHS": ["The Bahamas"],
    "LAO": ["Lao"],
    "VNM": ["Viet Nam"],
    "KOR": ["Korea"],
    "PRK": ["DPRK"],
    "FSM": ["FSM"],
    "XKX": ["Kosova"],
    "PSE": ["State of Palestine"],
    "GNB": ["Guinea Bissau"],
}
# display names where the source's common name isn't the usual English one
DISPLAY = {"TUR": "Türkiye", "CIV": "Côte d'Ivoire", "CPV": "Cabo Verde"}

# Capitals. The first is the one shown in "Find the country by its capital"; every listed one is accepted when
# typing. Countries with several official capitals accept any of them (PLAN.md), and common English
# spellings are accepted (e.g. Kiev, per PLAN.md).
CAPITALS = {
    "SWZ": ["Mbabane", "Lobamba"],
    "BOL": ["Sucre", "La Paz"],
    "BEN": ["Porto-Novo", "Cotonou"],
    "CIV": ["Yamoussoukro", "Abidjan"],
    "LKA": ["Sri Jayawardenepura Kotte", "Kotte", "Colombo"],
    "MYS": ["Kuala Lumpur", "Putrajaya"],
    "MNG": ["Ulaanbaatar", "Ulan Bator"],
    "KIR": ["South Tarawa", "Tarawa"],
    "PSE": ["Ramallah", "East Jerusalem", "Jerusalem"],
    "PLW": ["Ngerulmud", "Melekeok"],
    "SMR": ["City of San Marino", "San Marino"],
    "VAT": ["Vatican City", "Vatican"],
    "KWT": ["Kuwait City", "Kuwait"],
    "GTM": ["Guatemala City", "Guatemala"],
    "MEX": ["Mexico City"],
    "PAN": ["Panama City"],
    "USA": ["Washington, D.C.", "Washington", "Washington DC"],
    "UKR": ["Kyiv", "Kiev"],
    "XKX": ["Pristina", "Prishtina"],
    "CHE": ["Bern", "Berne"],
    "GNQ": ["Ciudad de la Paz", "Malabo"],
}
# what each capital is for, shown in Learning mode where a country has more than one
CAPITAL_NOTES = {
    "ZAF": "Pretoria (executive), Cape Town (legislative), Bloemfontein (judicial)",
    "BOL": "Sucre (constitutional), La Paz (seat of government)",
    "SWZ": "Mbabane (executive), Lobamba (royal and legislative)",
    "BEN": "Porto-Novo (official), Cotonou (seat of government)",
    "CIV": "Yamoussoukro (official), Abidjan (economic centre)",
    "LKA": "Sri Jayawardenepura Kotte (official), Colombo (commercial centre)",
    "MYS": "Kuala Lumpur (official), Putrajaya (seat of government)",
    "PSE": "Ramallah (administrative), East Jerusalem (proclaimed)",
    "GNQ": "Ciudad de la Paz (new capital), Malabo (former capital)",
}


def fetch(name):
    DL.mkdir(parents=True, exist_ok=True)
    p = DL / name
    if not p.exists():
        print("downloading", SOURCES[name])
        urllib.request.urlretrieve(SOURCES[name], p)
    return json.loads(p.read_text(encoding="utf8"))


def fix_topology(t, quiz_ids):
    sc, tr = t["transform"]["scale"], t["transform"]["translate"]

    def first_point(poly):
        i = poly[0][0]
        a = t["arcs"][i if i >= 0 else ~i]
        return a[0][0] * sc[0] + tr[0], a[0][1] * sc[1] + tr[1]

    geoms = t["objects"]["countries"]["geometries"]
    for g in geoms:
        name = g["properties"]["name"]
        if name == "Kosovo":
            g["id"] = "XKX"
        elif name == "Somaliland":
            g["id"] = "706"
        elif name == "N. Cyprus":
            g["id"] = "196"
        g.pop("properties", None)
        if g.get("id") is None or g["id"] not in quiz_ids:
            g["id"] = "T-" + (g.get("id") or name)

    rules = {
        "250": (lambda lo, la: lo < -30 or la < 0 or lo > 40, "T-France overseas"),
        "528": (lambda lo, la: lo < -30, "T-Caribbean Netherlands"),
        "554": (lambda lo, la: la > -20, "T-Tokelau"),
    }
    extra = []
    for g in geoms:
        if g["id"] == "036" and g["type"] == "Polygon":
            g["id"] = "T-Ashmore"
            continue
        if g["id"] in rules and g["type"] == "MultiPolygon":
            test, name = rules[g["id"]]
            out = [p for p in g["arcs"] if test(*first_point(p))]
            if out:
                g["arcs"] = [p for p in g["arcs"] if not test(*first_point(p))]
                extra.append({"type": "MultiPolygon", "arcs": out, "id": name})
    geoms.extend(extra)
    t["objects"] = {"countries": t["objects"]["countries"]}  # drop the unused "land" object
    # Borders (arcs between two different countries or territories) and coastlines (arcs used by one only),
    # worked out here once so the app doesn't have to on every start (it made the splash stutter on phones).
    # (Lines inside a merged country, e.g. Somalia-Somaliland, are neither, so they aren't drawn.)
    users = {}
    def walk(arcs, n, gid):
        for a in arcs:
            if isinstance(a, list):
                walk(a, n, gid)
            else:
                users.setdefault(a if a >= 0 else ~a, []).append((n, gid))
    for n, g in enumerate(geoms):
        walk(g["arcs"], n, g["id"])
    borders = [[i] for i, u in sorted(users.items()) if len({gid for _, gid in u}) > 1]
    coast = [[i] for i, u in sorted(users.items()) if len({n for n, _ in u}) == 1]
    t["objects"]["borders"] = {"type": "MultiLineString", "arcs": borders}
    t["objects"]["coast"] = {"type": "MultiLineString", "arcs": coast}
    return t


def build_countries():
    out = []
    for c in fetch("world-countries.json"):
        iso = c["cca3"]
        if not (c.get("unMember") or iso in EXTRA):
            continue
        r, s = c["region"], c.get("subregion", "")
        cont = (["South America"] if s == "South America" else ["North America"]) if r == "Americas" else [r]
        if iso in ("RUS", "TUR"):
            cont = ["Europe", "Asia"]
        if iso == "CYP":
            cont = ["Europe"]
        if iso in ("GEO", "ARM", "AZE", "KAZ"):
            cont = ["Asia"]
        if iso == "EGY":
            cont = ["Africa"]
        code = "XKX" if iso == "UNK" else iso
        name = DISPLAY.get(code, c["name"]["common"])
        names = [name, c["name"]["common"], c["name"]["official"]] + ALT.get(code, [])
        out.append({
            "iso": code,
            "id": "XKX" if iso == "UNK" else c["ccn3"],
            "name": name,
            "names": list(dict.fromkeys(names)),
            "capitals": CAPITALS.get(code, c.get("capital", [])),
            "capitalNote": CAPITAL_NOTES.get(code, ""),
            "a2": "XK" if iso == "UNK" else c["cca2"],
            "cont": cont,
            "car": iso in CARIBBEAN,
            "ll": c["latlng"],
        })
    assert len(out) == 197, len(out)
    return sorted(out, key=lambda c: c["name"])


WB = {
    "wb_countries.json": "https://api.worldbank.org/v2/country?format=json&per_page=400",
    "wb_pop.json": "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json&mrnev=1&per_page=400",
    "wb_gdppc.json": "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.PCAP.CD?format=json&mrnev=1&per_page=400",
}


def add_learning_info(countries):
    """Learning mode facts: from the country data, the World Bank, and tools/facts.py."""
    import facts
    for name, url in WB.items():
        SOURCES[name] = url
    inc = {x["id"]: x["incomeLevel"]["value"] for x in fetch("wb_countries.json")[1]}
    pop = {x["countryiso3code"]: (x["value"], x["date"]) for x in fetch("wb_pop.json")[1] if x["value"]}
    gdp = {x["countryiso3code"]: (x["value"], x["date"]) for x in fetch("wb_gdppc.json")[1] if x["value"]}
    src = {("XKX" if c["cca3"] == "UNK" else c["cca3"]): c for c in fetch("world-countries.json")}
    areas = {}
    for area, isos in facts.AREAS.items():
        for i in isos.split():
            areas.setdefault(i, []).append(area)
    by_area = sorted(countries, key=lambda c: -src[c["iso"]]["area"])
    rank = {c["iso"]: n + 1 for n, c in enumerate(by_area)}
    missing = [c["iso"] for c in countries if c["iso"] not in facts.FACTS]
    assert not missing, f"no facts for {missing}"
    for c in countries:
        i, s = c["iso"], src[c["iso"]]
        tz, ind, gov, high, city, coast = facts.FACTS[i]
        extra = facts.EXTRA_FIGURES.get(i, {})
        p = pop.get(i)
        g = gdp.get(i)
        income = extra.get("income", inc.get(i) or "")
        cur = "; ".join(f"{v['name']} ({k})" for k, v in s.get("currencies", {}).items())
        c["info"] = {
            "sub": facts.SUBREGION_NAMES.get(s.get("subregion", ""), s.get("subregion", "")),
            "areas": areas.get(i, []),
            "former": facts.FORMER.get(i, ""),
            "langs": list(s.get("languages", {}).values()),
            "pop": extra.get("pop", p[0] if p else None),
            "popYear": extra.get("popYear", p[1] if p else ""),
            "area": s["area"],
            "areaRank": rank[i],
            "currency": cur,
            "demonym": s.get("demonyms", {}).get("eng", {}).get("m", ""),
            "city": city,
            "coast": coast,
            "high": high,
            "tz": tz,
            "drive": "Left" if i in facts.DRIVE_LEFT else "Right",
            "ind": ind,
            "gov": gov,
            "rec": facts.RECOGNITION.get(i, ""),
            "income": "" if income in ("Not classified", "Aggregates") else income,
            "gdppc": extra.get("gdppc", round(g[0]) if g else None),
            "gdpYear": extra.get("gdpYear", g[1] if g else ""),
        }


def main():
    OUT.mkdir(exist_ok=True)
    countries = build_countries()
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    add_learning_info(countries)
    ids = {c["id"] for c in countries}
    for res in ("50m", "110m"):
        topo = fix_topology(fetch(f"countries-{res}.json"), ids)
        (OUT / f"world-{res}.json").write_text(json.dumps(topo, separators=(",", ":")), encoding="utf8")
    (OUT / "countries.json").write_text(json.dumps(countries, ensure_ascii=False, indent=0), encoding="utf8")
    print("wrote data/world-50m.json, data/world-110m.json, data/countries.json")


if __name__ == "__main__":
    main()
