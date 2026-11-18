"""Builds Mexico's country map (Mexico_plan.md, jobs/build_countries.md): 31 states and Mexico City.

  data/mx-states.json   the 32 shapes (Natural Earth 1:10m admin-1; the Revillagigedo Islands left off) with the
                        countries around as grey context; lines "borders", "coast"; "detail": the detail level's index
  data/mx-detail/       the detail level (tools/detail.py): fitted to the GSHHG full-resolution shoreline, in tiles
  data/mx-parts.json    names, capitals, kind, region, Learning facts (tools/mx_facts.py + the INEGI census);
                        populations from the 2020 census (INEGI)
  data/flags/mx/        the states' coats of arms (Wikimedia Commons): games 5 and 6 are coat-of-arms games
  data/tribal-mx.json   the Indigenous layer: municipalities shaded by the share who speak an Indigenous language
                        (INEGI 2020 census ITER; municipal boundaries from geoBoundaries, CC BY 4.0)

Run from the repo root:  python tools/build_mx.py   (the downloads it needs are listed in jobs/build_countries.md)
"""
import csv
import difflib
import io
import json
import pathlib
import re
import sys
import unicodedata
import zipfile

import geopandas as gpd
import shapely
from PIL import Image
from shapely.geometry import mapping, MultiLineString, shape, box
from shapely.ops import unary_union, linemerge

ROOT = pathlib.Path(__file__).resolve().parent.parent
NE = ROOT / "tools" / "downloads" / "ne10"
MXDL = ROOT / "tools" / "downloads" / "mx"
sys.path.insert(0, str(ROOT / "tools"))
from detail import build_detail, polygonal, lines_only  # noqa: E402

SIMPLIFY = 0.01
WINDOW = (-124, 4, -80, 45)  # Mexico with the US borderlands, Central America and western Cuba; wide enough for a tall phone screen
DETAIL = (-118.5, 14.4, -86.6, 32.8)  # where the high-resolution shoreline was downloaded (tools/fetch_country_data.py)

# ISO 3166-2:MX code -> (shown name, Natural Earth name, INEGI number, other names)
STATES = {
    "AGU": ("Aguascalientes", "Aguascalientes", 1, []), "BCN": ("Baja California", "Baja California", 2, []),
    "BCS": ("Baja California Sur", "Baja California Sur", 3, []), "CAM": ("Campeche", "Campeche", 4, []),
    "COA": ("Coahuila", "Coahuila", 5, ["Coahuila de Zaragoza"]), "COL": ("Colima", "Colima", 6, []),
    "CHP": ("Chiapas", "Chiapas", 7, []), "CHH": ("Chihuahua", "Chihuahua", 8, []),
    "CMX": ("Mexico City", "Distrito Federal", 9, ["CDMX", "Ciudad de México", "DF", "Distrito Federal", "Federal District"]),
    "DUR": ("Durango", "Durango", 10, []), "GUA": ("Guanajuato", "Guanajuato", 11, []), "GRO": ("Guerrero", "Guerrero", 12, []),
    "HID": ("Hidalgo", "Hidalgo", 13, []), "JAL": ("Jalisco", "Jalisco", 14, []),
    "MEX": ("State of Mexico", "México", 15, ["Mexico", "Estado de México", "Edomex", "Mexico State"]),
    "MIC": ("Michoacán", "Michoacán", 16, ["Michoacán de Ocampo"]), "MOR": ("Morelos", "Morelos", 17, []),
    "NAY": ("Nayarit", "Nayarit", 18, []), "NLE": ("Nuevo León", "Nuevo León", 19, []), "OAX": ("Oaxaca", "Oaxaca", 20, []),
    "PUE": ("Puebla", "Puebla", 21, []), "QUE": ("Querétaro", "Querétaro", 22, ["Querétaro de Arteaga"]),
    "ROO": ("Quintana Roo", "Quintana Roo", 23, []), "SLP": ("San Luis Potosí", "San Luis Potosí", 24, []),
    "SIN": ("Sinaloa", "Sinaloa", 25, []), "SON": ("Sonora", "Sonora", 26, []), "TAB": ("Tabasco", "Tabasco", 27, []),
    "TAM": ("Tamaulipas", "Tamaulipas", 28, []), "TLA": ("Tlaxcala", "Tlaxcala", 29, []),
    "VER": ("Veracruz", "Veracruz", 30, ["Veracruz de Ignacio de la Llave"]), "YUC": ("Yucatán", "Yucatán", 31, []),
    "ZAC": ("Zacatecas", "Zacatecas", 32, []),
}
# the capital as shown, and other forms accepted (the official long names)
CAPITALS = {
    "AGU": ["Aguascalientes"], "BCN": ["Mexicali"], "BCS": ["La Paz"], "CAM": ["Campeche", "San Francisco de Campeche"],
    "COA": ["Saltillo"], "COL": ["Colima"], "CHP": ["Tuxtla Gutiérrez", "Tuxtla"], "CHH": ["Chihuahua"], "CMX": [],
    "DUR": ["Durango", "Victoria de Durango"], "GUA": ["Guanajuato"], "GRO": ["Chilpancingo", "Chilpancingo de los Bravo"],
    "HID": ["Pachuca", "Pachuca de Soto"], "JAL": ["Guadalajara"], "MEX": ["Toluca", "Toluca de Lerdo"], "MIC": ["Morelia"],
    "MOR": ["Cuernavaca"], "NAY": ["Tepic"], "NLE": ["Monterrey"], "OAX": ["Oaxaca", "Oaxaca de Juárez"],
    "PUE": ["Puebla", "Puebla de Zaragoza"], "QUE": ["Querétaro", "Santiago de Querétaro"], "ROO": ["Chetumal"],
    "SLP": ["San Luis Potosí"], "SIN": ["Culiacán", "Culiacán Rosales"], "SON": ["Hermosillo"], "TAB": ["Villahermosa"],
    "TAM": ["Ciudad Victoria", "Victoria"], "TLA": ["Tlaxcala", "Tlaxcala de Xicohténcatl"], "VER": ["Xalapa", "Jalapa", "Xalapa-Enríquez"],
    "YUC": ["Mérida"], "ZAC": ["Zacatecas"],
}
CAP_LL = {}  # coordinates for any capital tools/capitals.py can't find (filled in as needed)
RINGS = ["CMX", "TLA", "MOR", "AGU", "COL"]  # small parts: circles (see js/geo.js)


def rounded(geom, nd=3):
    def r(c):
        return [round(c[0], nd), round(c[1], nd)] if isinstance(c[0], (int, float)) else [r(x) for x in c]
    m = mapping(geom)
    return {"type": m["type"], "coordinates": r(json.loads(json.dumps(m["coordinates"])))}


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def shapes():
    a1 = gpd.read_file(NE / "ne_10m_admin_1_states_provinces.geojson")
    a0 = gpd.read_file(NE / "ne_10m_admin_0_countries.geojson")
    mx = a1[a1["adm0_a3"] == "MEX"]
    by_name = {v[1]: k for k, v in STATES.items()}
    areas, sliver = {}, None
    for _, r in mx.iterrows():
        g = polygonal(r.geometry)
        if r["iso_3166_2"] == "MX-X01~":
            sliver = g
            continue
        code = by_name[r["name"]]
        if code == "COL":  # the Revillagigedo Islands, far out in the Pacific: left off (Mexico_plan.md)
            g = polygonal(g.intersection(box(-105.5, 17, -102, 20)))
        areas["MX-" + code] = g
    assert len(areas) == 32, len(areas)
    if sliver is not None:
        k = max(areas, key=lambda k: areas[k].boundary.intersection(sliver.buffer(1e-6)).length)
        areas[k] = polygonal(unary_union([areas[k], sliver]))
    mexico = unary_union(list(areas.values()))
    names = {}
    win = box(*WINDOW)
    for _, r in a0[a0.intersects(win)].iterrows():
        a3 = r["ADM0_A3"]
        if a3 == "MEX":
            continue
        g = polygonal(polygonal(r.geometry).intersection(win).difference(mexico))
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
    detail = build_detail(areas, "mx", DETAIL)
    out = {"type": "FeatureCollection",
           "features": [{"type": "Feature", "id": k, "geometry": rounded(g)} for k, g in geo.items() if not g.is_empty],
           "borders": rounded(merged(borders)), "coast": rounded(merged(coast)), "detail": detail}
    coast_u = unary_union(coast).buffer(1e-4)
    extra = {}
    for k, g in geo.items():
        if k.startswith("MX-"):
            nb = sorted({names[j] for j, h in geo.items() if j.startswith("T-") and g.boundary.intersection(h.boundary).length > 0.01})
            extra[k] = {"coastal": g.boundary.intersection(coast_u).length > 0.03, "borders": nb}
            main = max(getattr(g, "geoms", [g]), key=lambda p: p.area)
            if not main.contains(main.centroid):
                p = shapely.maximum_inscribed_circle(main, 0.01).coords[0]
                extra[k]["anchorLL"] = [round(p[0], 3), round(p[1], 3)]
    return out, extra, areas


def languages():
    """INEGI 2020: speakers of an Indigenous language and the top languages, by state."""
    d = json.loads((MXDL / "indigenous" / "top_languages_by_state.json").read_text(encoding="utf8"))
    return {int(k.split(" ")[0]): v for k, v in d.items()}


def indigenous_layer(areas):
    """Municipalities shaded by the share (3 years and over) who speak an Indigenous language."""
    z = zipfile.ZipFile(MXDL / "indigenous" / "iter_00_cpv2020_csv.zip")
    rows = csv.DictReader(io.TextIOWrapper(z.open("iter_00_cpv2020/conjunto_de_datos/conjunto_de_datos_iter_00CSV20.csv"), encoding="utf-8-sig"))
    mun = {}
    for r in rows:
        if r["LOC"] == "0000" and r["MUN"] != "000":
            try:
                mun.setdefault(int(r["ENTIDAD"]), {})[norm(r["NOM_MUN"])] = (r["NOM_MUN"], int(r["P3YM_HLI"]), int(r["P_3YMAS"]))
            except ValueError:
                pass
    num_of = {"MX-" + k: v[2] for k, v in STATES.items()}
    name_of = {v[2]: v[0] for v in STATES.values()}
    langs = languages()
    gb = gpd.read_file(MXDL / "indigenous" / "mex_adm2_simplified.geojson")
    feats, unmatched = [], 0
    for _, r in gb.iterrows():
        g = polygonal(r.geometry)
        c = g.representative_point()
        st = next((num_of[k] for k, a in areas.items() if k.startswith("MX-") and a.contains(c)), None)
        if st is None or st not in mun:
            unmatched += 1
            continue
        key = norm(r["shapeName"])
        hit = mun[st].get(key)
        if not hit:
            close = difflib.get_close_matches(key, list(mun[st]), n=1, cutoff=0.85)
            hit = mun[st][close[0]] if close else None
        if not hit or not hit[2]:
            unmatched += 1
            continue
        name, hli, base = hit
        share = hli / base
        if share < 0.05:
            continue
        band = 4 if share >= 0.7 else 3 if share >= 0.4 else 2 if share >= 0.15 else 1
        top = ", ".join(t["lang"] for t in langs.get(st, {}).get("top", [])[:3])
        g = g.simplify(0.01)
        feats.append({"type": "Feature", "properties": {"n": f"{name}, {name_of[st]}", "band": band,
                      "k": f"{round(share * 100)}% speak an Indigenous language" + (f" (in {name_of[st]}: {top})" if top else "")},
                      "geometry": rounded(polygonal(g), 3)})
    (ROOT / "data" / "tribal-mx.json").write_text(json.dumps({"type": "FeatureCollection", "features": feats}, ensure_ascii=False,
                                                              separators=(",", ":")), encoding="utf8")
    print(f"  Indigenous layer: {len(feats)} municipalities with 5% or more speakers ({unmatched} of {len(gb)} not matched to the census)")


def main():
    fc, extra, areas = shapes()
    (ROOT / "data" / "mx-states.json").write_text(json.dumps(fc, separators=(",", ":")), encoding="utf8")
    import capitals
    import mx_facts
    table = {s["name"]: s for s in json.loads((MXDL / "states.json").read_text(encoding="utf8"))}
    table["State of Mexico"] = table.pop("México")
    langs = languages()
    items, missing = [], []
    out_flags = ROOT / "data" / "flags" / "mx"
    out_flags.mkdir(parents=True, exist_ok=True)
    for code, (name, ne_name, num, alts) in STATES.items():
        iso = "MX-" + code
        row = table[name]
        caps = CAPITALS[code]
        year = int(re.search(r"(\d{4})", row["admitted"] or "").group(1)) if row.get("admitted") else None
        f = dict(mx_facts.FACTS.get(code, {}))
        lg = langs.get(num, {})
        if lg.get("top"):
            f["langs"] = ", ".join(t["lang"] for t in lg["top"][:4])
            f["speakers"] = lg.get("speakers")
        if row.get("largest") and caps and norm(row["largest"]) != norm(row["capital"] or ""):
            f["city"] = row["largest"]
        coat_src = MXDL / "coats" / f"{row['name'] if name != 'State of Mexico' else 'México'}.png"
        has_coat = coat_src.exists()
        if has_coat:
            Image.open(coat_src).convert("RGBA").save(out_flags / f"{iso}.webp", "WEBP", quality=88)
        it = {"iso": iso, "id": iso, "name": name, "names": list(dict.fromkeys([name, ne_name] + alts)), "capitals": caps,
              "cont": ["North America"], "car": False, "a2": iso,
              "info": {"abbr": code, "kind": "Capital city" if code == "CMX" else "State", "region": f.get("region", ""),
                       "pop": row["pop2020"], "popYear": "2020 census", "area": round(row["area"]), "year": year, "order": row.get("order"),
                       "flag": has_coat, "emblem": "coat of arms", "facts": f,
                       **{k: v for k, v in extra.get(iso, {}).items() if k != "anchorLL"}},
              "flagKey": "mx/" + iso}
        if "anchorLL" in extra.get(iso, {}):
            it["anchorLL"] = extra[iso]["anchorLL"]
        if caps:
            ll = CAP_LL.get(caps[0]) or capitals.find(caps[0], a2="MX")
            if not ll:
                missing.append(f"{name}: {caps[0]}")
            it["capLL"] = [ll] if ll else []
        items.append(it)
    total = sum(it["info"]["pop"] for it in items)
    print(f"  population {total:,} (2020 census total: 126,014,024) {'OK' if total == 126014024 else 'MISMATCH'}")
    if missing:
        print("  capitals not found:", missing)
    by_area = sorted(items, key=lambda c: -c["info"]["area"])
    for it in items:
        it["info"]["areaRank"] = by_area.index(it) + 1
    (ROOT / "data" / "mx-parts.json").write_text(json.dumps(sorted(items, key=lambda s: s["name"]), ensure_ascii=False, indent=0), encoding="utf8")
    print("  wrote data/mx-states.json and data/mx-parts.json:", len(items), "parts;", sum(it["info"]["flag"] for it in items), "coats of arms")
    indigenous_layer(areas)


if __name__ == "__main__":
    main()
