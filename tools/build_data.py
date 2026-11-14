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
        out.append({
            "iso": code,
            "id": "XKX" if iso == "UNK" else c["ccn3"],
            "name": c["name"]["common"],
            "capitals": c.get("capital", []),
            "cont": cont,
            "car": iso in CARIBBEAN,
            "ll": c["latlng"],
        })
    assert len(out) == 197, len(out)
    return sorted(out, key=lambda c: c["name"])


def main():
    OUT.mkdir(exist_ok=True)
    countries = build_countries()
    ids = {c["id"] for c in countries}
    for res in ("50m", "110m"):
        topo = fix_topology(fetch(f"countries-{res}.json"), ids)
        (OUT / f"world-{res}.json").write_text(json.dumps(topo, separators=(",", ":")), encoding="utf8")
    (OUT / "countries.json").write_text(json.dumps(countries, ensure_ascii=False, indent=0), encoding="utf8")
    print("wrote data/world-50m.json, data/world-110m.json, data/countries.json")


if __name__ == "__main__":
    main()
