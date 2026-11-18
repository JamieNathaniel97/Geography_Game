"""Builds Italy's country map (Italy_plan.md, jobs/build_countries.md): the 20 regions, with Vatican City and San Marino as
coloured circles (tappable for a short card; left out of the games).

  data/it-states.json   the 20 regions (Natural Earth 1:10m admin-1's provinces, dissolved by region) and the two enclaves
                        (admin-0), the countries around as grey context; lines "borders", "coast"; "detail"
  data/it-detail/       the detail level (tools/detail.py): fitted to the GSHHG full-resolution shoreline, in tiles
  data/it-parts.json    names, capitals, Learning facts (tools/it_facts.py); populations on 1 January 2026 (ISTAT, from
                        the downloaded "Regions of Italy" table)
  data/flags/it/        the 20 regions' flags and the two countries' flags

The provinces (the second set, to confirm) aren't built yet. Run from the repo root:  python tools/build_it.py
"""
import json
import pathlib
import re
import sys

import geopandas as gpd
import shapely
from PIL import Image
from shapely.geometry import mapping, MultiLineString, box
from shapely.ops import unary_union, linemerge

ROOT = pathlib.Path(__file__).resolve().parent.parent
NE = ROOT / "tools" / "downloads" / "ne10"
ITDL = ROOT / "tools" / "downloads" / "it"
sys.path.insert(0, str(ROOT / "tools"))
from detail import build_detail, polygonal, lines_only  # noqa: E402

SIMPLIFY = 0.005
WINDOW = (4.5, 35.0, 21.0, 48.0)        # Italy, Sicily and Sardinia with their neighbours
DETAIL = (6.5, 35.4, 18.6, 47.1)        # where the high-resolution shoreline was downloaded
# code: (English name as in the table, shown name, capital, other names, other capital names)
REGIONS = {
    "21": ("Piedmont", "Piedmont", "Turin", ["Piemonte"], ["Torino"]),
    "23": ("Aosta Valley", "Aosta Valley", "Aosta", ["Valle d'Aosta", "Vallée d'Aoste", "Val d'Aosta"], []),
    "25": ("Lombardy", "Lombardy", "Milan", ["Lombardia"], ["Milano"]),
    "32": ("Trentino-Alto Adige/Südtirol", "Trentino-South Tyrol", "Trento", ["Trentino-Alto Adige", "Trentino", "South Tyrol", "Südtirol", "Alto Adige", "Trentino-Alto Adige/Südtirol"], ["Trient"]),
    "34": ("Veneto", "Veneto", "Venice", ["Venetia"], ["Venezia"]),
    "36": ("Friuli-Venezia Giulia", "Friuli-Venezia Giulia", "Trieste", ["Friuli", "Friuli Venezia Giulia"], []),
    "42": ("Liguria", "Liguria", "Genoa", [], ["Genova"]),
    "45": ("Emilia-Romagna", "Emilia-Romagna", "Bologna", ["Emilia Romagna"], []),
    "52": ("Tuscany", "Tuscany", "Florence", ["Toscana"], ["Firenze"]),
    "55": ("Umbria", "Umbria", "Perugia", [], []),
    "57": ("Marche", "Marche", "Ancona", ["The Marches", "Marches"], []),
    "62": ("Lazio", "Lazio", "Rome", ["Latium"], ["Roma"]),
    "65": ("Abruzzo", "Abruzzo", "L'Aquila", ["Abruzzi"], ["L Aquila", "Aquila"]),
    "67": ("Molise", "Molise", "Campobasso", [], []),
    "72": ("Campania", "Campania", "Naples", [], ["Napoli"]),
    "75": ("Apulia", "Apulia", "Bari", ["Puglia"], []),
    "77": ("Basilicata", "Basilicata", "Potenza", ["Lucania"], []),
    "78": ("Calabria", "Calabria", "Catanzaro", [], []),
    "82": ("Sicily", "Sicily", "Palermo", ["Sicilia"], []),
    "88": ("Sardinia", "Sardinia", "Cagliari", ["Sardegna"], []),
}
SPECIAL = {"23", "32", "36", "82", "88"}   # the autonomous regions with special statute
ENCLAVE_A3 = {"VA": "VAT", "SM": "SMR"}
ENCLAVE_LL = {"VA": [12.453, 41.904], "SM": [12.458, 43.942]}
CAP_LL = {}


def rounded(geom, nd=3):
    def r(c):
        return [round(c[0], nd), round(c[1], nd)] if isinstance(c[0], (int, float)) else [r(x) for x in c]
    m = mapping(geom)
    return {"type": m["type"], "coordinates": r(json.loads(json.dumps(m["coordinates"])))}


def populations():
    """1 January 2026 populations and areas from the "Regions of Italy" table (ISTAT figures)."""
    s = (ITDL / "wiki" / "lists" / "Regions of Italy.wiki").read_text(encoding="utf8").replace('"', "")
    tab = s[s.index("! class=unsortable rowspan=2|[[Flags"):]
    tab = tab[:tab.index("|}")]
    out = {}
    for r in tab.split("\n|-"):
        m = re.search(r"'''\[\[([^\]|]+)(?:\|[^\]]*)?\]\]'''", r)
        if not m:
            continue
        nums = [re.sub(r"^\|\s*align=right\s*\|", "", c) for c in r.split("\n") if re.match(r"\|\s*align=right", c)]
        out[m.group(1)] = (int(nums[0].replace(",", "").replace("'''", "")), float(re.search(r"convert\|([\d,\.]+)", nums[2]).group(1).replace(",", "")))
    return out


def shapes():
    a1 = gpd.read_file(NE / "ne_10m_admin_1_states_provinces.geojson")
    a0 = gpd.read_file(NE / "ne_10m_admin_0_countries.geojson")
    prov = a1[a1["adm0_a3"] == "ITA"]
    areas = {}
    for code in REGIONS:
        areas["IT-" + code] = polygonal(unary_union([polygonal(r.geometry) for _, r in prov.iterrows() if r["region_cod"].strip() == "IT-" + code]).buffer(0))
    enclaves = {}
    for k, a3 in ENCLAVE_A3.items():
        g = polygonal(a0[a0["ADM0_A3"] == a3].geometry.iloc[0])
        enclaves["IT-" + k] = g
        areas["IT-" + k] = g
    italy = unary_union(list(areas.values()))
    for k in list(REGIONS):
        areas["IT-" + k] = polygonal(areas["IT-" + k].difference(unary_union(list(enclaves.values()))))
    names, win = {}, box(*WINDOW)
    for _, r in a0[a0.intersects(win)].iterrows():
        a3 = r["ADM0_A3"]
        if a3 in ("ITA", "VAT", "SMR"):
            continue
        g = polygonal(polygonal(r.geometry).intersection(win).difference(italy))
        g = unary_union([p for p in getattr(g, "geoms", [g]) if p.area > 0.002])
        if not g.is_empty:
            areas["T-" + a3] = polygonal(g)
            names["T-" + a3] = r["NAME"]
    keys = list(areas)
    geo = shapely.coverage_clean([areas[k] for k in keys], gap_width=0.002, snapping_distance=0.0001)
    geo = shapely.coverage_simplify([polygonal(g) for g in geo], SIMPLIFY)
    geo = {k: polygonal(shapely.set_precision(polygonal(g), 0.001)) for k, g in zip(keys, geo)}
    for k, g in enclaves.items():  # too small to simplify (Vatican City is half a square kilometre)
        geo[k] = polygonal(shapely.set_precision(g, 0.0001))
    borders = []
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            A, B = geo[a].bounds, geo[b].bounds
            if A[0] > B[2] or B[0] > A[2] or A[1] > B[3] or B[1] > A[3]:
                continue
            borders += lines_only(geo[a].boundary.intersection(geo[b].boundary))
    bu = unary_union(borders)
    coast = lines_only(unary_union([g.boundary for g in geo.values()]).difference(bu.buffer(1e-7)).difference(win.exterior.buffer(0.01)))
    merged = lambda ls: linemerge(ls) if ls else MultiLineString([])
    detail = build_detail({k: v for k, v in areas.items()}, "it", DETAIL)
    out = {"type": "FeatureCollection",
           "features": [{"type": "Feature", "id": k, "geometry": rounded(g, 4 if k in enclaves else 3)} for k, g in geo.items() if not g.is_empty],
           "borders": rounded(merged(borders)), "coast": rounded(merged(coast)), "detail": detail}
    coast_u = unary_union(coast).buffer(1e-4)
    extra = {}
    for k, g in geo.items():
        if k.startswith("IT-") and k not in enclaves:
            nb = sorted({names[j] for j, h in geo.items() if j.startswith("T-") and g.boundary.intersection(h.boundary).length > 0.01})
            nb += [{"IT-VA": "Vatican City", "IT-SM": "San Marino"}[e] for e in enclaves if g.boundary.intersection(geo[e].boundary).length > 0]
            extra[k] = {"coastal": g.boundary.intersection(coast_u).length > 0.03, "borders": nb}
            main = max(getattr(g, "geoms", [g]), key=lambda p: p.area)
            if not main.contains(main.centroid):
                p = shapely.maximum_inscribed_circle(main, 0.01).coords[0]
                extra[k]["anchorLL"] = [round(p[0], 3), round(p[1], 3)]
    return out, extra


def flag(src, dst):
    im = Image.open(src).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    Image.alpha_composite(bg, im).convert("RGB").save(dst, "WEBP", quality=88)


def main():
    fc, extra = shapes()
    (ROOT / "data" / "it-states.json").write_text(json.dumps(fc, separators=(",", ":")), encoding="utf8")
    import it_facts
    import capitals
    pops = populations()
    out_flags = ROOT / "data" / "flags" / "it"
    out_flags.mkdir(parents=True, exist_ok=True)
    items, missing = [], []
    for code, (table, name, cap, alt, cap_alt) in REGIONS.items():
        iso = "IT-" + code
        src = ITDL / "flags" / f"{iso}.png"
        if src.exists():
            flag(src, out_flags / f"{iso}.webp")
        f = it_facts.FACTS.get(code, {})
        pop, area = pops[table]
        it = {"iso": iso, "id": iso, "name": name, "names": list(dict.fromkeys([name, table, f.get("italian", name)] + alt)),
              "capitals": [cap] + cap_alt, "cont": ["Europe"], "car": False, "a2": iso,
              "info": {"kind": "Autonomous region" if code in SPECIAL else "Region", "pop": pop, "popYear": "2026", "area": round(area),
                       "flag": src.exists(), "facts": f, **{k: v for k, v in extra.get(iso, {}).items() if k != "anchorLL"}},
              "flagKey": "it/" + iso}
        if "anchorLL" in extra.get(iso, {}):
            it["anchorLL"] = extra[iso]["anchorLL"]
        ll = CAP_LL.get(cap) or capitals.find(cap, a2="IT")
        if not ll:
            missing.append(cap)
        it["capLL"] = [ll] if ll else []
        items.append(it)
    total = sum(it["info"]["pop"] for it in items)
    # the table's last row is the national total (its first bold link is the capital, Rome)
    national = pops["Rome"][0]
    print(f"  population {total:,} (Italy, 1 January 2026: {national:,}) {'OK' if total == national else 'MISMATCH'}")
    if missing:
        print("  capitals not found:", missing)
    by_area = sorted(items, key=lambda c: -c["info"]["area"])
    for it in items:
        it["info"]["areaRank"] = by_area.index(it) + 1
    # the enclaves: in Learning mode only, as coloured circles (js/app.js leaves them out of the games)
    flags0 = ROOT / "data" / "flags"
    for k, e in it_facts.ENCLAVES.items():
        iso = "IT-" + k
        items.append({"iso": iso, "id": iso, "name": e["name"], "names": [e["name"], e["italian"]], "capitals": [e["capital"]],
                      "cont": ["Europe"], "car": False, "a2": iso, "anchorLL": ENCLAVE_LL[k], "capLL": [],
                      "info": {"kind": e["kind"], "enclave": True, "ringColour": e["colour"], "pop": e["pop"], "popYear": e["popYear"],
                               "flag": (flags0 / f"{ENCLAVE_A3[k]}.webp").exists(), "facts": e},
                      "flagKey": ENCLAVE_A3[k]})
    (ROOT / "data" / "it-parts.json").write_text(json.dumps(sorted(items, key=lambda s: s["name"]), ensure_ascii=False, indent=0), encoding="utf8")
    print("  wrote data/it-states.json and data/it-parts.json:", len(items), "parts (20 regions and 2 enclaves);",
          sum(it["info"]["flag"] for it in items), "flags")


if __name__ == "__main__":
    main()
