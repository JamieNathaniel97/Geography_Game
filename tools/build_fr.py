"""Builds France's country map (France_plan.md, jobs/build_countries.md): the 13 metropolitan regions (no flags).

  data/fr-states.json   the 13 regions (Natural Earth 1:10m admin-1's 96 metropolitan departments, dissolved by region),
                        the countries around as grey context; lines "borders", "coast"; "detail": the detail level's index
  data/fr-detail/       the detail level (tools/detail.py): fitted to the GSHHG full-resolution shoreline, in tiles
  data/fr-parts.json    names, capitals, Learning facts (tools/fr_facts.py); INSEE's 2019 legal populations (summed from
                        the departments in the downloaded "List of French departments by population")

The 5 overseas regions are left off (France_plan.md). Run from the repo root:  python tools/build_fr.py
"""
import json
import pathlib
import re
import sys

import geopandas as gpd
import shapely
from shapely.geometry import mapping, MultiLineString, box
from shapely.ops import unary_union, linemerge

ROOT = pathlib.Path(__file__).resolve().parent.parent
NE = ROOT / "tools" / "downloads" / "ne10"
FRDL = ROOT / "tools" / "downloads" / "fr"
sys.path.insert(0, str(ROOT / "tools"))
from detail import build_detail, polygonal, lines_only  # noqa: E402

SIMPLIFY = 0.005
WINDOW = (-7.5, 40.0, 12.0, 53.5)       # metropolitan France and Corsica with their neighbours
DETAIL = (-5.5, 41.2, 10.0, 51.2)       # where the high-resolution shoreline is used
# code: (English name, capital, other names)
REGIONS = {
    "ARA": ("Auvergne-Rhône-Alpes", "Lyon", ["Auvergne Rhone Alpes", "Auvergne", "Rhône-Alpes"], ["Lyons"]),
    "BFC": ("Bourgogne-Franche-Comté", "Dijon", ["Burgundy-Franche-Comté", "Burgundy", "Bourgogne", "Franche-Comté"], ["Besançon"]),
    "BRE": ("Brittany", "Rennes", ["Bretagne"], []),
    "CVL": ("Centre-Val de Loire", "Orléans", ["Centre", "Centre Val de Loire", "Loire Valley"], ["Orleans"]),
    "COR": ("Corsica", "Ajaccio", ["Corse"], []),
    "GES": ("Grand Est", "Strasbourg", ["Great East", "Alsace", "Grand-Est"], []),
    "HDF": ("Hauts-de-France", "Lille", ["Upper France", "Hauts de France", "Nord-Pas-de-Calais"], []),
    "IDF": ("Île-de-France", "Paris", ["Ile de France", "Paris region", "Paris Region"], []),
    "NOR": ("Normandy", "Rouen", ["Normandie"], []),
    "NAQ": ("Nouvelle-Aquitaine", "Bordeaux", ["New Aquitaine", "Aquitaine", "Nouvelle Aquitaine"], []),
    "OCC": ("Occitanie", "Toulouse", ["Occitania"], []),
    "PDL": ("Pays de la Loire", "Nantes", ["Pays-de-la-Loire", "Loire Country"], []),
    "PAC": ("Provence-Alpes-Côte d'Azur", "Marseille", ["PACA", "Provence", "Provence-Alpes-Cote d'Azur", "Côte d'Azur"], ["Marseilles"]),
}
KIND = {"COR": "Territorial collectivity"}
CAP_LL = {}


def rounded(geom, nd=3):
    def r(c):
        return [round(c[0], nd), round(c[1], nd)] if isinstance(c[0], (int, float)) else [r(x) for x in c]
    m = mapping(geom)
    return {"type": m["type"], "coordinates": r(json.loads(json.dumps(m["coordinates"])))}


def populations(dept_region):
    """INSEE's 2019 legal populations and areas, by department (the downloaded list article), summed by region."""
    s = (FRDL / "wiki" / "lists" / "List of French departments by population.wiki").read_text(encoding="utf8")
    pop, area = {}, {}
    for line in re.findall(r"^\|\s*\[\[[^\]]+\]\]\s*\|\|(.*)$", s, re.M):
        cells = [re.sub(r"\{\{[^{}]*\}\}", "", c).strip().replace(",", "") for c in line.split("||")]
        dept = cells[-1]
        reg = dept_region.get(dept)
        if not reg:
            continue  # overseas
        pop[reg] = pop.get(reg, 0) + int(cells[3])
        area[reg] = area.get(reg, 0) + int(cells[4])
    return pop, area


def shapes():
    a1 = gpd.read_file(NE / "ne_10m_admin_1_states_provinces.geojson")
    a0 = gpd.read_file(NE / "ne_10m_admin_0_countries.geojson")
    deps = a1[(a1["adm0_a3"] == "FRA") & (a1["type_en"] == "Metropolitan department")]
    assert len(deps) == 96, len(deps)
    dept_region = {r["iso_3166_2"][3:]: r["region_cod"].strip()[3:] for _, r in deps.iterrows()}
    areas = {}
    for code in REGIONS:
        areas["FR-" + code] = polygonal(unary_union([polygonal(r.geometry) for _, r in deps.iterrows() if r["region_cod"].strip()[3:] == code]).buffer(0))
    france = unary_union(list(areas.values()))
    names, win = {}, box(*WINDOW)
    for _, r in a0[a0.intersects(win)].iterrows():
        a3 = r["ADM0_A3"]
        if a3 == "FRA":
            continue
        g = polygonal(polygonal(r.geometry).intersection(win).difference(france))
        g = unary_union([p for p in getattr(g, "geoms", [g]) if p.area > 0.002])
        if not g.is_empty:
            areas["T-" + a3] = polygonal(g)
            names["T-" + a3] = r["NAME"]
    keys = list(areas)
    geo = shapely.coverage_clean([areas[k] for k in keys], gap_width=0.002, snapping_distance=0.0001)
    geo = shapely.coverage_simplify([polygonal(g) for g in geo], SIMPLIFY)
    geo = {k: polygonal(shapely.set_precision(polygonal(g), 0.001)) for k, g in zip(keys, geo)}
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
    detail = build_detail(areas, "fr", DETAIL)
    out = {"type": "FeatureCollection",
           "features": [{"type": "Feature", "id": k, "geometry": rounded(g)} for k, g in geo.items() if not g.is_empty],
           "borders": rounded(merged(borders)), "coast": rounded(merged(coast)), "detail": detail}
    coast_u = unary_union(coast).buffer(1e-4)
    extra = {}
    for k, g in geo.items():
        if k.startswith("FR-"):
            nb = sorted({names[j] for j, h in geo.items() if j.startswith("T-") and g.boundary.intersection(h.boundary).length > 0.01})
            extra[k] = {"coastal": g.boundary.intersection(coast_u).length > 0.03, "borders": nb}
            main = max(getattr(g, "geoms", [g]), key=lambda p: p.area)
            if not main.contains(main.centroid):
                p = shapely.maximum_inscribed_circle(main, 0.01).coords[0]
                extra[k]["anchorLL"] = [round(p[0], 3), round(p[1], 3)]
    return out, extra, dept_region


def main():
    fc, extra, dept_region = shapes()
    (ROOT / "data" / "fr-states.json").write_text(json.dumps(fc, separators=(",", ":")), encoding="utf8")
    import fr_facts
    import capitals
    pop, area = populations(dept_region)
    items, missing = [], []
    for code, (name, cap, alt, cap_alt) in REGIONS.items():
        iso = "FR-" + code
        f = fr_facts.FACTS.get(code, {})
        it = {"iso": iso, "id": iso, "name": name, "names": list(dict.fromkeys([name, f.get("french", name)] + alt)),
              "capitals": [cap] + cap_alt, "cont": ["Europe"], "car": False, "a2": iso,
              "info": {"abbr": code, "kind": KIND.get(code, "Region"), "pop": pop[code], "popYear": "2019", "area": area[code],
                       "flag": False, "facts": f, **{k: v for k, v in extra.get(iso, {}).items() if k != "anchorLL"}},
              "flagKey": "fr/" + iso}
        if "anchorLL" in extra.get(iso, {}):
            it["anchorLL"] = extra[iso]["anchorLL"]
        ll = CAP_LL.get(cap) or capitals.find(cap, a2="FR")
        if not ll:
            missing.append(cap)
        it["capLL"] = [ll] if ll else []
        items.append(it)
    total = sum(it["info"]["pop"] for it in items)
    print(f"  metropolitan population {total:,} (INSEE 2019 legal population, metropolitan France: 65,096,768)"
          f" {'OK' if total == 65096768 else 'CHECK'}")
    if missing:
        print("  capitals not found:", missing)
    by_area = sorted(items, key=lambda c: -c["info"]["area"])
    for it in items:
        it["info"]["areaRank"] = by_area.index(it) + 1
    (ROOT / "data" / "fr-parts.json").write_text(json.dumps(sorted(items, key=lambda s: s["name"]), ensure_ascii=False, indent=0), encoding="utf8")
    print("  wrote data/fr-states.json and data/fr-parts.json:", len(items), "parts")


if __name__ == "__main__":
    main()
