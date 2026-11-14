"""Builds the tiny-country test page (tiny-country-test.html) from template.html.

Steps:
1. Download Natural Earth 1:50m country shapes (world-atlas) and country facts (world-countries).
2. Fix the map data: give Kosovo an ID, merge Somaliland into Somalia and N. Cyprus into Cyprus,
   and split overseas territories off France, the Netherlands, New Zealand and Australia.
3. Make countries.json: the 197 countries with continents (per PLAN.md) and the Caribbean tag.
4. Put both into template.html.

Run:  python build.py
"""
import json
import pathlib
import urllib.request

HERE = pathlib.Path(__file__).parent
DL = HERE / "downloads"
TOPO_URL = "https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-50m.json"
FACTS_URL = "https://cdn.jsdelivr.net/npm/world-countries@5.1.0/countries.json"
CARIBBEAN = set("ATG BHS BRB CUB DMA DOM GRD HTI JAM KNA LCA VCT TTO".split())


def fetch(url, name):
    DL.mkdir(exist_ok=True)
    p = DL / name
    if not p.exists():
        urllib.request.urlretrieve(url, p)
    return json.loads(p.read_text(encoding="utf8"))


def build_topology():
    t = fetch(TOPO_URL, "countries-50m.json")
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
        if g.get("id") is None:
            g["id"] = "T-" + name

    # overseas parts that are territories, not part of the quiz country
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
            g["arcs"] = [p for p in g["arcs"] if not test(*first_point(p))]
            extra.append({"type": "MultiPolygon", "arcs": out, "id": name})
    geoms.extend(extra)
    return t


def build_countries():
    out = []
    for c in fetch(FACTS_URL, "world-countries.json"):
        iso = c["cca3"]
        if not (c.get("unMember") or iso in ("VAT", "PSE", "UNK", "TWN")):
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
        out.append({"iso": code, "id": "XKX" if iso == "UNK" else c["ccn3"], "name": c["name"]["common"],
                    "cont": cont, "car": iso in CARIBBEAN, "ll": c["latlng"]})
    assert len(out) == 197, len(out)
    return out


if __name__ == "__main__":
    topo = json.dumps(build_topology(), separators=(",", ":"), ensure_ascii=False)
    countries = json.dumps(build_countries(), separators=(",", ":"), ensure_ascii=False)
    html = (HERE / "template.html").read_text(encoding="utf8")
    html = html.replace("/*TOPO*/", topo).replace("/*COUNTRIES*/", countries)
    (HERE / "tiny-country-test.html").write_text(html, encoding="utf8")
    print("wrote tiny-country-test.html")
