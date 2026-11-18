"""Builds Argentina's country map (Argentina_plan.md, jobs/build_countries.md): the 23 provinces and the Autonomous City of
Buenos Aires. No Falklands (decided 2026-11-17): left off, with no Antarctic claim.

  data/ar-states.json   the 24 shapes (Natural Earth 1:10m admin-1), the countries around as grey context (not the
                        Falklands); lines "borders", "coast"; "detail": the detail level's index
  data/ar-detail/       the detail level (tools/detail.py): fitted to the GSHHG full-resolution shoreline, in tiles
  data/ar-parts.json    names, capitals, Learning facts (tools/ar_facts.py); the 2022 census (INDEC, from the downloaded
                        "Provinces of Argentina" table)
  data/flags/ar/        the 24 flags (Wikimedia Commons)

Run from the repo root:  python tools/build_ar.py
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
ARDL = ROOT / "tools" / "downloads" / "ar"
sys.path.insert(0, str(ROOT / "tools"))
from detail import build_detail, polygonal, lines_only  # noqa: E402

SIMPLIFY = 0.008
WINDOW = (-77.0, -56.5, -50.0, -20.0)   # Argentina and its neighbours, from the Bolivian border to Cape Horn
DETAIL = (-73.6, -56.0, -53.6, -21.7)   # where the high-resolution shoreline is used (it ends at 55.1°S: the sea beyond)
LEFT_OFF = {"FLK", "ATA", "SGS"}        # the Falklands, Antarctica, South Georgia
# ISO letter: (shown name, name in the population table, capital, other names, other capital names)
PROVINCES = {
    "C": ("City of Buenos Aires", "Autonomous City of Buenos Aires", "Buenos Aires",
          ["CABA", "Ciudad de Buenos Aires", "Capital Federal", "Autonomous City of Buenos Aires", "Buenos Aires City"], []),
    "B": ("Buenos Aires", "Buenos Aires", "La Plata", ["Buenos Aires Province", "Provincia de Buenos Aires"], []),
    "K": ("Catamarca", "Catamarca", "San Fernando del Valle de Catamarca", [], ["Catamarca"]),
    "H": ("Chaco", "Chaco", "Resistencia", [], []),
    "U": ("Chubut", "Chubut", "Rawson", [], []),
    "X": ("Córdoba", "Córdoba", "Córdoba", [], []),
    "W": ("Corrientes", "Corrientes", "Corrientes", [], []),
    "E": ("Entre Ríos", "Entre Ríos", "Paraná", [], []),
    "P": ("Formosa", "Formosa", "Formosa", [], []),
    "Y": ("Jujuy", "Jujuy", "San Salvador de Jujuy", [], ["Jujuy"]),
    "L": ("La Pampa", "La Pampa", "Santa Rosa", ["Pampa"], []),
    "F": ("La Rioja", "La Rioja", "La Rioja", ["Rioja"], []),
    "M": ("Mendoza", "Mendoza", "Mendoza", [], []),
    "N": ("Misiones", "Misiones", "Posadas", [], []),
    "Q": ("Neuquén", "Neuquén", "Neuquén", [], []),
    "R": ("Río Negro", "Río Negro", "Viedma", [], []),
    "A": ("Salta", "Salta", "Salta", [], []),
    "J": ("San Juan", "San Juan", "San Juan", [], []),
    "D": ("San Luis", "San Luis", "San Luis", [], []),
    "Z": ("Santa Cruz", "Santa Cruz", "Río Gallegos", [], []),
    "S": ("Santa Fe", "Santa Fe", "Santa Fe", [], ["Santa Fe de la Vera Cruz"]),
    "G": ("Santiago del Estero", "Santiago del Estero", "Santiago del Estero", [], ["Santiago"]),
    "V": ("Tierra del Fuego", "Tierra del Fuego", "Ushuaia", ["Tierra del Fuego, Antarctica and South Atlantic Islands"], []),
    "T": ("Tucumán", "Tucumán", "San Miguel de Tucumán", [], ["Tucumán"]),
}
CAP_LL = {"San Fernando del Valle de Catamarca": [-65.779, -28.469]}  # (no match in the place list)


def rounded(geom, nd=3):
    def r(c):
        return [round(c[0], nd), round(c[1], nd)] if isinstance(c[0], (int, float)) else [r(x) for x in c]
    m = mapping(geom)
    return {"type": m["type"], "coordinates": r(json.loads(json.dumps(m["coordinates"])))}


def populations():
    """The 2022 census (INDEC) and areas, from the downloaded "Provinces of Argentina" table."""
    s = (ARDL / "wiki" / "lists" / "Provinces of Argentina.wiki").read_text(encoding="utf8")
    s = s[s.index("! class=\"unsortable\" | Flag"):]
    s = s[:s.index("|}")]
    out = {}
    for r in s.split("\n|-")[1:]:
        lines = [x for x in r.split("\n") if x.startswith("|")]
        if len(lines) < 7:
            continue
        name = re.search(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", lines[1]).group(1)
        nums = [x for x in lines if 'align="right"' in x]
        pop = int(re.sub(r"[^\d]", "", nums[0].split("|")[-1]))
        area = float(re.search(r"convert\|([\d,\.]+)", nums[1]).group(1).replace(",", ""))
        out[name] = (pop, area)
    return out


def shapes():
    a1 = gpd.read_file(NE / "ne_10m_admin_1_states_provinces.geojson")
    a0 = gpd.read_file(NE / "ne_10m_admin_0_countries.geojson")
    areas = {"AR-" + r["iso_3166_2"][3:]: polygonal(r.geometry) for _, r in a1[a1["adm0_a3"] == "ARG"].iterrows()}
    assert len(areas) == 24, len(areas)
    argentina = unary_union(list(areas.values()))
    names, win = {}, box(*WINDOW)
    for _, r in a0[a0.intersects(win)].iterrows():
        a3 = r["ADM0_A3"]
        if a3 == "ARG" or a3 in LEFT_OFF:
            continue
        g = polygonal(polygonal(r.geometry).intersection(win).difference(argentina))
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
    detail = build_detail(areas, "ar", DETAIL)   # (the Falklands' land is too far from any area to be joined to one)
    out = {"type": "FeatureCollection",
           "features": [{"type": "Feature", "id": k, "geometry": rounded(g)} for k, g in geo.items() if not g.is_empty],
           "borders": rounded(merged(borders)), "coast": rounded(merged(coast)), "detail": detail}
    coast_u = unary_union(coast).buffer(1e-4)
    extra = {}
    for k, g in geo.items():
        if k.startswith("AR-"):
            nb = sorted({names[j] for j, h in geo.items() if j.startswith("T-") and g.boundary.intersection(h.boundary).length > 0.01})
            extra[k] = {"coastal": g.boundary.intersection(coast_u).length > 0.03, "borders": nb}
            main = max(getattr(g, "geoms", [g]), key=lambda p: p.area)
            if not main.contains(main.centroid):
                p = shapely.maximum_inscribed_circle(main, 0.01).coords[0]
                extra[k]["anchorLL"] = [round(p[0], 3), round(p[1], 3)]
    return out, extra


def main():
    fc, extra = shapes()
    (ROOT / "data" / "ar-states.json").write_text(json.dumps(fc, separators=(",", ":")), encoding="utf8")
    import ar_facts
    import capitals
    pops = populations()
    out_flags = ROOT / "data" / "flags" / "ar"
    out_flags.mkdir(parents=True, exist_ok=True)
    items, missing = [], []
    for code, (name, table, cap, alt, cap_alt) in PROVINCES.items():
        iso = "AR-" + code
        src = ARDL / "flags" / f"{iso}.png"
        if src.exists():
            im = Image.open(src).convert("RGBA")
            bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
            Image.alpha_composite(bg, im).convert("RGB").save(out_flags / f"{iso}.webp", "WEBP", quality=88)
        f = ar_facts.FACTS.get(code, {})
        pop, area = pops[table]
        it = {"iso": iso, "id": iso, "name": name, "names": list(dict.fromkeys([name] + alt)), "capitals": [cap] + cap_alt,
              "cont": ["South America"], "car": False, "a2": iso,
              "info": {"abbr": code, "kind": "Autonomous city" if code == "C" else "Province", "region": f.get("region", ""),
                       "pop": pop, "popYear": "2022 census", "area": round(area), "flag": src.exists(), "facts": f,
                       **{k: v for k, v in extra.get(iso, {}).items() if k != "anchorLL"}},
              "flagKey": "ar/" + iso}
        if code == "B":
            it["notTypo"] = ["City of Buenos Aires"]
        if "anchorLL" in extra.get(iso, {}):
            it["anchorLL"] = extra[iso]["anchorLL"]
        ll = CAP_LL.get(cap) or capitals.find(cap, a2="AR")
        if not ll:
            missing.append(cap)
        it["capLL"] = [ll] if ll else []
        items.append(it)
    total = sum(it["info"]["pop"] for it in items)
    print(f"  population {total:,} (2022 census, INDEC)")
    if missing:
        print("  capitals not found:", missing)
    by_area = sorted(items, key=lambda c: -c["info"]["area"])
    for it in items:
        it["info"]["areaRank"] = by_area.index(it) + 1
    (ROOT / "data" / "ar-parts.json").write_text(json.dumps(sorted(items, key=lambda s: s["name"]), ensure_ascii=False, indent=0), encoding="utf8")
    print("  wrote data/ar-states.json and data/ar-parts.json:", len(items), "parts;", sum(it["info"]["flag"] for it in items), "flags")


if __name__ == "__main__":
    main()
