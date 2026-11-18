"""Builds Brazil's country map (Brazil_plan.md, jobs/build_countries.md): 26 states and the Federal District.

  data/br-states.json   the 27 shapes (Natural Earth 1:10m admin-1), the countries around as grey context (French
                        Guiana among them); lines "borders", "coast"; "detail": the detail level's index
  data/br-detail/       the detail level (tools/detail.py): fitted to the GSHHG full-resolution shoreline, in tiles
  data/br-parts.json    names, capitals, region, Learning facts (tools/br_facts.py); 2022 census (IBGE); island ovals
                        for Fernando de Noronha (Pernambuco) and Trindade (Espírito Santo)
  data/flags/br/        the 27 flags (Wikimedia Commons)
  data/tribal-br.json   the Indigenous lands layer: FUNAI's Indigenous territories (credit FUNAI)

Run from the repo root:  python tools/build_br.py
"""
import json
import math
import pathlib
import sys
import tempfile
import zipfile

import geopandas as gpd
import shapely
from PIL import Image
from shapely.geometry import mapping, MultiLineString, box
from shapely.ops import unary_union, linemerge

ROOT = pathlib.Path(__file__).resolve().parent.parent
NE = ROOT / "tools" / "downloads" / "ne10"
BRDL = ROOT / "tools" / "downloads" / "br"
sys.path.insert(0, str(ROOT / "tools"))
from detail import build_detail, polygonal, lines_only  # noqa: E402

SIMPLIFY = 0.015
WINDOW = (-84, -42, -24, 13)            # Brazil and its neighbours, with room for a tall phone screen and the far islands
DETAIL = (-74.1, -33.8, -28.6, 5.4)     # where the high-resolution shoreline was downloaded
# extra names (the two-letter codes are widely used in Brazil, so they count)
ALT = {"AM": ["Amazon State"], "DF": ["Distrito Federal", "Federal District", "Brasília", "Brasilia"],
       "RJ": ["Rio"], "SP": ["Sao Paulo State"], "ES": ["Espirito Santo"], "MS": ["Mato Grosso do Sul"]}
NOT_TYPO = {"PA": ["Paraná", "Paraíba"], "PR": ["Pará", "Paraíba"], "PB": ["Pará", "Paraná"]}
SHOWN = {"DF": "Federal District"}
# island ovals: (state, centre, radius in degrees)
ISLES = [("PE", (-32.42, -3.85), 0.12), ("ES", (-29.33, -20.51), 0.1)]
CAP_LL = {}


def rounded(geom, nd=3):
    def r(c):
        return [round(c[0], nd), round(c[1], nd)] if isinstance(c[0], (int, float)) else [r(x) for x in c]
    m = mapping(geom)
    return {"type": m["type"], "coordinates": r(json.loads(json.dumps(m["coordinates"])))}


def shapes():
    a1 = gpd.read_file(NE / "ne_10m_admin_1_states_provinces.geojson")
    a0 = gpd.read_file(NE / "ne_10m_admin_0_countries.geojson")
    areas = {"BR-" + r["iso_3166_2"][3:]: polygonal(r.geometry) for _, r in a1[a1["adm0_a3"] == "BRA"].iterrows()}
    assert len(areas) == 27, len(areas)
    brazil = unary_union(list(areas.values()))
    names, win = {}, box(*WINDOW)
    for _, r in a0[a0.intersects(win)].iterrows():
        a3 = r["ADM0_A3"]
        if a3 == "BRA":
            continue
        g = polygonal(polygonal(r.geometry).intersection(win).difference(brazil))
        g = unary_union([p for p in getattr(g, "geoms", [g]) if p.area > 0.01])
        if not g.is_empty:
            areas["T-" + a3] = polygonal(g)
            names["T-" + a3] = "French Guiana" if a3 == "FRA" else r["NAME"]
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
    detail = build_detail(areas, "br", DETAIL)
    out = {"type": "FeatureCollection",
           "features": [{"type": "Feature", "id": k, "geometry": rounded(g)} for k, g in geo.items() if not g.is_empty],
           "borders": rounded(merged(borders)), "coast": rounded(merged(coast)), "detail": detail}
    coast_u = unary_union(coast).buffer(1e-4)
    extra = {}
    for k, g in geo.items():
        if k.startswith("BR-"):
            nb = sorted({names[j] for j, h in geo.items() if j.startswith("T-") and g.boundary.intersection(h.boundary).length > 0.01})
            extra[k] = {"coastal": g.boundary.intersection(coast_u).length > 0.03, "borders": nb}
            main = max(getattr(g, "geoms", [g]), key=lambda p: p.area)
            if not main.contains(main.centroid):
                p = shapely.maximum_inscribed_circle(main, 0.01).coords[0]
                extra[k]["anchorLL"] = [round(p[0], 3), round(p[1], 3)]
    return out, extra


def indigenous_layer():
    """FUNAI's Indigenous territories (the shapefile export from its geoserver), simplified."""
    with tempfile.TemporaryDirectory() as tmp:
        zipfile.ZipFile(BRDL / "funai" / "tis_poligonais.zip").extractall(tmp)
        g = gpd.read_file(pathlib.Path(tmp) / "tis_poligonais.shp").to_crs(4326)
    feats = []
    for _, r in g.iterrows():
        if r.geometry is None:
            continue
        geom = polygonal(polygonal(r.geometry).simplify(0.01))
        people = (r["etnia_nome"] or "").strip()
        kind = f"Indigenous territory{' of the ' + people if people else ''} ({(r['fase_ti'] or '').strip().lower()})"
        if geom.is_empty:
            c = r.geometry.representative_point()
            feats.append({"type": "Feature", "properties": {"n": r["terrai_nom"], "k": kind}, "geometry": {"type": "Point", "coordinates": [round(c.x, 3), round(c.y, 3)]}})
        else:
            feats.append({"type": "Feature", "properties": {"n": r["terrai_nom"], "k": kind}, "geometry": rounded(geom, 3)})
    (ROOT / "data" / "tribal-br.json").write_text(json.dumps({"type": "FeatureCollection", "features": feats}, ensure_ascii=False,
                                                              separators=(",", ":")), encoding="utf8")
    print(f"  Indigenous lands layer: {len(feats)} territories")


def main():
    fc, extra = shapes()
    (ROOT / "data" / "br-states.json").write_text(json.dumps(fc, separators=(",", ":")), encoding="utf8")
    import br_facts
    import capitals
    rows = json.loads((BRDL / "states.json").read_text(encoding="utf8"))
    out_flags = ROOT / "data" / "flags" / "br"
    out_flags.mkdir(parents=True, exist_ok=True)
    items, missing = [], []
    for row in rows:
        code = row["code"]
        iso = "BR-" + code
        name = SHOWN.get(code, row["name"])
        src = BRDL / "flags" / f"{code}.png"
        if src.exists():
            Image.open(src).convert("RGB").save(out_flags / f"{iso}.webp", "WEBP", quality=88)
        f = br_facts.FACTS.get(code, {})
        it = {"iso": iso, "id": iso, "name": name, "names": list(dict.fromkeys([name, row["name"], code] + ALT.get(code, []))),
              "capitals": [row["capital"]], "cont": ["South America"], "car": False, "a2": iso,
              "info": {"abbr": code, "kind": "Federal District" if code == "DF" else "State", "region": f.get("region", ""),
                       "pop": row["pop2022"], "popYear": "2022 census", "area": round(row["area"]), "year": row["established"],
                       "flag": src.exists(), "facts": f, **{k: v for k, v in extra.get(iso, {}).items() if k != "anchorLL"}},
              "flagKey": "br/" + iso}
        if "anchorLL" in extra.get(iso, {}):
            it["anchorLL"] = extra[iso]["anchorLL"]
        if code in NOT_TYPO:
            it["notTypo"] = NOT_TYPO[code]
        isles = [{"center": list(c), "ring": [[round(c[0] + r * math.cos(a), 3), round(c[1] + r * math.sin(a), 3)]
                                              for a in [i * math.pi / 12 for i in range(24)]]} for s, c, r in ISLES if s == code]
        if isles:
            it["isles"] = isles
        ll = CAP_LL.get(row["capital"]) or capitals.find(row["capital"], a2="BR")
        if not ll:
            missing.append(row["capital"])
        it["capLL"] = [ll] if ll else []
        items.append(it)
    total = sum(it["info"]["pop"] for it in items)
    print(f"  population {total:,} (2022 census total: 203,080,756) {'OK' if total == 203080756 else 'MISMATCH'}")
    if missing:
        print("  capitals not found:", missing)
    by_area = sorted(items, key=lambda c: -c["info"]["area"])
    for it in items:
        it["info"]["areaRank"] = by_area.index(it) + 1
    (ROOT / "data" / "br-parts.json").write_text(json.dumps(sorted(items, key=lambda s: s["name"]), ensure_ascii=False, indent=0), encoding="utf8")
    print("  wrote data/br-states.json and data/br-parts.json:", len(items), "parts;", sum(it["info"]["flag"] for it in items), "flags")
    indigenous_layer()


if __name__ == "__main__":
    main()
