"""Builds Germany's country map (Germany_plan.md, jobs/build_countries.md): the 16 states (Länder).

  data/de-states.json   the 16 shapes (Natural Earth 1:10m admin-1), the countries around as grey context; lines
                        "borders", "coast"; "detail": the detail level's index
  data/de-detail/       the detail level (tools/detail.py): fitted to the GSHHG full-resolution shoreline, in tiles
  data/de-parts.json    names, capitals, Learning facts (tools/de_facts.py); populations (Destatis, 31 December 2024,
                        on the 2022 census basis: tools/downloads/de/states.json)
  data/flags/de/        the 16 flags (Wikimedia Commons)

Run from the repo root:  python tools/build_de.py
"""
import json
import pathlib
import sys

import geopandas as gpd
import shapely
from PIL import Image
from shapely.geometry import mapping, MultiLineString, box
from shapely.ops import unary_union, linemerge

ROOT = pathlib.Path(__file__).resolve().parent.parent
NE = ROOT / "tools" / "downloads" / "ne10"
DEDL = ROOT / "tools" / "downloads" / "de"
sys.path.insert(0, str(ROOT / "tools"))
from detail import build_detail, polygonal, lines_only  # noqa: E402

SIMPLIFY = 0.004
WINDOW = (0.5, 44.5, 21.5, 58)          # Germany and its neighbours, with room for a tall phone screen
DETAIL = (5.0, 47.0, 15.5, 55.2)        # where the high-resolution shoreline was downloaded
# German names, and the other names people use
ALT = {"BY": ["Bayern"], "HE": ["Hessen"], "NI": ["Niedersachsen"], "NW": ["Nordrhein-Westfalen", "NRW"],
       "RP": ["Rheinland-Pfalz"], "SN": ["Sachsen"], "ST": ["Sachsen-Anhalt"], "TH": ["Thüringen"],
       "MV": ["Mecklenburg-Western Pomerania", "Mecklenburg-West Pomerania", "Mecklenburg"], "HB": ["Freie Hansestadt Bremen"],
       "BW": ["Baden-Wurttemberg", "Baden Württemberg"], "SH": ["Schleswig Holstein"]}
CAP_ALT = {"Munich": ["München"], "Hanover": ["Hannover"], "Düsseldorf": ["Duesseldorf"], "Saarbrücken": ["Saarbruecken"]}
NOT_TYPO = {"SN": ["Lower Saxony", "Saxony-Anhalt"], "NI": ["Saxony"], "ST": ["Saxony"]}
KIND = {"BE": "City-state", "HH": "City-state", "HB": "City-state"}
CAP_LL = {}


def rounded(geom, nd=3):
    def r(c):
        return [round(c[0], nd), round(c[1], nd)] if isinstance(c[0], (int, float)) else [r(x) for x in c]
    m = mapping(geom)
    return {"type": m["type"], "coordinates": r(json.loads(json.dumps(m["coordinates"])))}


def shapes():
    a1 = gpd.read_file(NE / "ne_10m_admin_1_states_provinces.geojson")
    a0 = gpd.read_file(NE / "ne_10m_admin_0_countries.geojson")
    areas = {"DE-" + r["iso_3166_2"][3:]: polygonal(r.geometry) for _, r in a1[a1["adm0_a3"] == "DEU"].iterrows()}
    assert len(areas) == 16, len(areas)
    germany = unary_union(list(areas.values()))
    names, win = {}, box(*WINDOW)
    for _, r in a0[a0.intersects(win)].iterrows():
        a3 = r["ADM0_A3"]
        if a3 == "DEU":
            continue
        g = polygonal(polygonal(r.geometry).intersection(win).difference(germany))
        g = unary_union([p for p in getattr(g, "geoms", [g]) if p.area > 0.01])
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
    detail = build_detail(areas, "de", DETAIL)
    out = {"type": "FeatureCollection",
           "features": [{"type": "Feature", "id": k, "geometry": rounded(g)} for k, g in geo.items() if not g.is_empty],
           "borders": rounded(merged(borders)), "coast": rounded(merged(coast)), "detail": detail}
    coast_u = unary_union(coast).buffer(1e-4)
    extra = {}
    for k, g in geo.items():
        if k.startswith("DE-"):
            nb = sorted({names[j] for j, h in geo.items() if j.startswith("T-") and g.boundary.intersection(h.boundary).length > 0.01})
            extra[k] = {"coastal": g.boundary.intersection(coast_u).length > 0.03, "borders": nb}
            main = max(getattr(g, "geoms", [g]), key=lambda p: p.area)
            if not main.contains(main.centroid):
                p = shapely.maximum_inscribed_circle(main, 0.01).coords[0]
                extra[k]["anchorLL"] = [round(p[0], 3), round(p[1], 3)]
    return out, extra


def main():
    fc, extra = shapes()
    (ROOT / "data" / "de-states.json").write_text(json.dumps(fc, separators=(",", ":")), encoding="utf8")
    import de_facts
    import capitals
    rows = json.loads((DEDL / "states.json").read_text(encoding="utf8"))
    out_flags = ROOT / "data" / "flags" / "de"
    out_flags.mkdir(parents=True, exist_ok=True)
    items, missing = [], []
    for row in rows:
        code = row["code"]
        iso = "DE-" + code
        name = row["name"]
        src = DEDL / "flags" / f"{iso}.png"
        if src.exists():
            Image.open(src).convert("RGB").save(out_flags / f"{iso}.webp", "WEBP", quality=88)
        f = de_facts.FACTS.get(code, {})
        it = {"iso": iso, "id": iso, "name": name, "names": list(dict.fromkeys([name] + ALT.get(code, []))),
              "capitals": [row["capital"]] + CAP_ALT.get(row["capital"], []), "cont": ["Europe"], "car": False, "a2": iso,
              "info": {"abbr": code, "kind": KIND.get(code, "State"), "pop": row["pop"], "popYear": "2024",
                       "area": round(row["area"]), "year": row["established"], "flag": src.exists(), "facts": f,
                       **{k: v for k, v in extra.get(iso, {}).items() if k != "anchorLL"}},
              "flagKey": "de/" + iso}
        if "anchorLL" in extra.get(iso, {}):
            it["anchorLL"] = extra[iso]["anchorLL"]
        if code in NOT_TYPO:
            it["notTypo"] = NOT_TYPO[code]
        ll = CAP_LL.get(row["capital"]) or capitals.find(row["capital"], a2="DE")
        if not ll:
            missing.append(row["capital"])
        it["capLL"] = [ll] if ll else []
        items.append(it)
    total = sum(it["info"]["pop"] for it in items)
    print(f"  population {total:,} (Destatis total, 31 Dec 2024: 83,577,140) {'OK' if total == 83577140 else 'MISMATCH'}")
    if missing:
        print("  capitals not found:", missing)
    by_area = sorted(items, key=lambda c: -c["info"]["area"])
    for it in items:
        it["info"]["areaRank"] = by_area.index(it) + 1
    (ROOT / "data" / "de-parts.json").write_text(json.dumps(sorted(items, key=lambda s: s["name"]), ensure_ascii=False, indent=0), encoding="utf8")
    print("  wrote data/de-states.json and data/de-parts.json:", len(items), "parts;", sum(it["info"]["flag"] for it in items), "flags")


if __name__ == "__main__":
    main()
