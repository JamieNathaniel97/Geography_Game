"""Builds Spain's country map (Spain_plan.md, jobs/build_countries.md) in two sets, like the UK's county sets:

  data/es-states.json, es-parts.json, es-detail/     the 17 autonomous communities and the 2 autonomous cities (flags)
  data/esp-states.json, esp-parts.json, esp-detail/  the 50 provinces and the 2 cities (no flags; a short card)
  data/flags/es/                                     the 19 flags (Wikimedia Commons)

Both from Natural Earth 1:10m admin-1's 52 provinces (the communities dissolved from them). The Canary Islands are moved
into an inset at the lower left (SHIFT), with a frame around them; their capitals and detail level move with them.
Populations: INE's annual census for 1 January 2025 (the downloaded "Ranked lists of Spanish provinces"), the communities
summed from their provinces. The languages layer waits for data. Run from the repo root:  python tools/build_es.py
"""
import json
import pathlib
import re
import sys

import geopandas as gpd
import shapely
from PIL import Image
from shapely import affinity
from shapely.geometry import mapping, MultiLineString, LineString, box
from shapely.ops import unary_union, linemerge

ROOT = pathlib.Path(__file__).resolve().parent.parent
NE = ROOT / "tools" / "downloads" / "ne10"
ESDL = ROOT / "tools" / "downloads" / "es"
sys.path.insert(0, str(ROOT / "tools"))
from detail import build_detail, polygonal, lines_only, land  # noqa: E402

SIMPLIFY = 0.004
WINDOW = (-13.6, 33.6, 5.0, 44.6)       # the peninsula, the Balearics, Ceuta and Melilla, and the Canaries inset
DETAIL = (-13.2, 33.8, 4.6, 44.0)       # where the detail level is used (the inset included)
CANARIES = (-18.4, 27.5, -13.2, 29.5)   # where the Canaries really are
SHIFT = (5.5, 6.5)                      # moved this far (degrees east, north) into the inset
FRAME_PAD = 0.25
CANARY_PROV = {"GC", "TF"}

# province ISO code: (English name, name in the population table, capital, other names, other capital names)
PROVINCES = {
    "C": ("A Coruña", "A Coruña", "A Coruña", ["La Coruña", "Coruña", "Corunna"], ["La Coruña", "Corunna"]),
    "LU": ("Lugo", "Lugo", "Lugo", [], []), "OR": ("Ourense", "Ourense", "Ourense", ["Orense"], ["Orense"]),
    "PO": ("Pontevedra", "Pontevedra", "Pontevedra", [], []),
    "O": ("Asturias", "Asturias", "Oviedo", ["Asturies"], ["Uviéu"]), "S": ("Cantabria", "Cantabria", "Santander", [], []),
    "BI": ("Biscay", "Biscay", "Bilbao", ["Bizkaia", "Vizcaya"], ["Bilbo"]),
    "SS": ("Gipuzkoa", "Gipuzkoa", "San Sebastián", ["Guipúzcoa", "Guipuzcoa"], ["Donostia"]),
    "VI": ("Álava", "Álava", "Vitoria-Gasteiz", ["Araba"], ["Vitoria", "Gasteiz"]),
    "NA": ("Navarre", "Navarre", "Pamplona", ["Navarra", "Nafarroa"], ["Iruña"]), "LO": ("La Rioja", "La Rioja", "Logroño", ["Rioja"], []),
    "HU": ("Huesca", "Huesca", "Huesca", [], []), "Z": ("Zaragoza", "Zaragoza", "Zaragoza", ["Saragossa"], ["Saragossa"]),
    "TE": ("Teruel", "Teruel", "Teruel", [], []),
    "B": ("Barcelona", "Barcelona", "Barcelona", [], []), "GI": ("Girona", "Girona", "Girona", ["Gerona"], ["Gerona"]),
    "L": ("Lleida", "Lleida", "Lleida", ["Lérida"], ["Lérida"]), "T": ("Tarragona", "Tarragona", "Tarragona", [], []),
    "LE": ("León", "León", "León", [], []), "ZA": ("Zamora", "Zamora", "Zamora", [], []), "SA": ("Salamanca", "Salamanca", "Salamanca", [], []),
    "VA": ("Valladolid", "Valladolid", "Valladolid", [], []), "P": ("Palencia", "Palencia", "Palencia", [], []),
    "BU": ("Burgos", "Burgos", "Burgos", [], []), "SO": ("Soria", "Soria", "Soria", [], []), "SG": ("Segovia", "Segovia", "Segovia", [], []),
    "AV": ("Ávila", "Ávila", "Ávila", [], []),
    "M": ("Madrid", "Madrid", "Madrid", [], []), "GU": ("Guadalajara", "Guadalajara", "Guadalajara", [], []),
    "CU": ("Cuenca", "Cuenca", "Cuenca", [], []), "TO": ("Toledo", "Toledo", "Toledo", [], []),
    "CR": ("Ciudad Real", "Ciudad Real", "Ciudad Real", [], []), "AB": ("Albacete", "Albacete", "Albacete", [], []),
    "CC": ("Cáceres", "Cáceres", "Cáceres", [], []), "BA": ("Badajoz", "Badajoz", "Badajoz", [], []),
    "CS": ("Castellón", "Castellón", "Castellón de la Plana", ["Castelló"], ["Castellón", "Castelló de la Plana"]),
    "V": ("Valencia", "Valencia", "Valencia", ["València"], ["València"]), "A": ("Alicante", "Alicante", "Alicante", ["Alacant"], ["Alacant"]),
    "MU": ("Murcia", "Murcia", "Murcia", [], []),
    "PM": ("Balearic Islands", "Balearic Islands", "Palma", ["Baleares", "Illes Balears", "Islas Baleares"], ["Palma de Mallorca"]),
    "GC": ("Las Palmas", "Las Palmas", "Las Palmas de Gran Canaria", [], ["Las Palmas"]),
    "TF": ("Santa Cruz de Tenerife", "Santa Cruz de Tenerife", "Santa Cruz de Tenerife", ["Tenerife"], ["Santa Cruz"]),
    "H": ("Huelva", "Huelva", "Huelva", [], []), "SE": ("Seville", "Seville", "Seville", ["Sevilla"], ["Sevilla"]),
    "CA": ("Cádiz", "Cádiz", "Cádiz", [], []), "MA": ("Málaga", "Málaga", "Málaga", [], []), "CO": ("Córdoba", "Córdoba", "Córdoba", [], []),
    "J": ("Jaén", "Jaén", "Jaén", [], []), "GR": ("Granada", "Granada", "Granada", [], []), "AL": ("Almería", "Almería", "Almería", [], []),
    "CE": ("Ceuta", "Ceuta", "Ceuta", [], []), "ML": ("Melilla", "Melilla", "Melilla", [], []),
}
# community ISO code: (English name, capitals, other names); Natural Earth's region codes where they differ
COMMUNITIES = {
    "AN": ("Andalusia", ["Seville", "Sevilla"], ["Andalucía", "Andalucia"]),
    "AR": ("Aragon", ["Zaragoza", "Saragossa"], ["Aragón"]),
    "AS": ("Asturias", ["Oviedo"], ["Asturies", "Principality of Asturias"]),
    "IB": ("Balearic Islands", ["Palma", "Palma de Mallorca"], ["Illes Balears", "Islas Baleares", "Baleares", "Balearics"]),
    "PV": ("Basque Country", ["Vitoria-Gasteiz", "Vitoria", "Gasteiz"], ["País Vasco", "Euskadi", "Basque"]),
    "CN": ("Canary Islands", ["Santa Cruz de Tenerife", "Las Palmas de Gran Canaria", "Las Palmas"], ["Canarias", "Canaries", "Islas Canarias"]),
    "CB": ("Cantabria", ["Santander"], []),
    "CL": ("Castile and León", ["Valladolid"], ["Castilla y León", "Castile and Leon", "Castile-León"]),
    "CM": ("Castilla–La Mancha", ["Toledo"], ["Castilla-La Mancha", "Castile-La Mancha", "La Mancha"]),
    "CT": ("Catalonia", ["Barcelona"], ["Cataluña", "Catalunya"]),
    "EX": ("Extremadura", ["Mérida"], []),
    "GA": ("Galicia", ["Santiago de Compostela", "Santiago"], []),
    "RI": ("La Rioja", ["Logroño"], ["Rioja"]),
    "MD": ("Madrid", ["Madrid"], ["Community of Madrid", "Comunidad de Madrid"]),
    "MC": ("Murcia", ["Murcia"], ["Region of Murcia", "Región de Murcia"]),
    "NC": ("Navarre", ["Pamplona", "Iruña"], ["Navarra", "Nafarroa"]),
    "VC": ("Valencian Community", ["Valencia", "València"], ["Valencia", "Comunidad Valenciana", "Comunitat Valenciana"]),
    "CE": ("Ceuta", ["Ceuta"], []),
    "ML": ("Melilla", ["Melilla"], []),
}
NE_REGION = {"NA": "NC", "PM": "IB", "LO": "RI", "MU": "MC"}
CAP_LL = {"A Coruña": [-8.411, 43.362], "Lugo": [-7.556, 43.012], "Pontevedra": [-8.645, 42.431], "Vitoria-Gasteiz": [-2.672, 42.847],
          "Huesca": [-0.408, 42.136], "Teruel": [-1.106, 40.345], "Girona": [2.821, 41.979], "Lleida": [0.620, 41.614],
          "Palencia": [-4.530, 42.010], "Soria": [-2.464, 41.764], "Segovia": [-4.118, 40.948], "Ávila": [-4.700, 40.656],
          "Ciudad Real": [-3.927, 38.985], "Castellón de la Plana": [-0.038, 39.986], "Las Palmas de Gran Canaria": [-15.413, 28.124],
          "Santa Cruz de Tenerife": [-16.251, 28.464]}  # (the place list had no match for these)


def rounded(geom, nd=3):
    def r(c):
        return [round(c[0], nd), round(c[1], nd)] if isinstance(c[0], (int, float)) else [r(x) for x in c]
    m = mapping(geom)
    return {"type": m["type"], "coordinates": r(json.loads(json.dumps(m["coordinates"])))}


def populations():
    """INE's annual census, 1 January 2025, by province (from the downloaded "Ranked lists of Spanish provinces")."""
    s = (ESDL / "wiki" / "lists" / "Ranked lists of Spanish provinces.wiki").read_text(encoding="utf8")
    t = s[s.index("== Population and geography =="):s.index("== Economy ==")]
    out = {}
    for r in t.split("\n|-"):
        links = re.findall(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r)
        nums = [line[1:] for line in r.split("\n") if re.match(r"^\|[\d,]", line)]
        if links and nums:
            out[links[0]] = (int(nums[0].replace(",", "")), float(nums[1].replace(",", "")))
    return out


def shift(g):
    return affinity.translate(g, *SHIFT)


def frame():
    w, s, e, n = CANARIES
    return box(w + SHIFT[0] - FRAME_PAD, s + SHIFT[1] - FRAME_PAD, e + SHIFT[0] + FRAME_PAD, n + SHIFT[1] + FRAME_PAD)


def province_areas():
    a1 = gpd.read_file(NE / "ne_10m_admin_1_states_provinces.geojson")
    prov = a1[a1["adm0_a3"] == "ESP"]
    assert len(prov) == 52, len(prov)
    areas, community = {}, {}
    for _, r in prov.iterrows():
        code = r["iso_3166_2"][3:]
        g = polygonal(r.geometry)
        if code in CANARY_PROV:
            g = shift(g)
        areas[code] = g
        reg = r["region_cod"].strip()[3:]
        community[code] = code if code in ("CE", "ML") else NE_REGION.get(reg, reg)
    return areas, community


def build_set(areas, prefix, name):
    """One set: the shapes file with grey neighbours, borders, coast and the inset frame, and its detail level."""
    a0 = gpd.read_file(NE / "ne_10m_admin_0_countries.geojson")
    areas = {f"{prefix}-{k}": v for k, v in areas.items()}
    spain = unary_union(list(areas.values()))
    fr = frame()
    names, win = {}, box(*WINDOW)
    for _, r in a0[a0.intersects(win)].iterrows():
        a3 = r["ADM0_A3"]
        if a3 == "ESP":
            continue
        g = polygonal(polygonal(r.geometry).intersection(win).difference(spain).difference(fr))
        g = unary_union([p for p in getattr(g, "geoms", [g]) if p.area > 0.0005])
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
    borders.append(LineString(fr.exterior.coords))  # the inset's frame, drawn as a border line
    merged = lambda ls: linemerge(ls) if ls else MultiLineString([])
    # the detail level: the downloaded shoreline, with the Canaries' part moved into the inset like the shapes
    lp = polygonal(unary_union([land("es", DETAIL), shift(land("es", CANARIES))]))
    detail = build_detail({k: v for k, v in areas.items()}, "es", DETAIL, land_poly=lp, name=name)
    out = {"type": "FeatureCollection",
           "features": [{"type": "Feature", "id": k, "geometry": rounded(g)} for k, g in geo.items() if not g.is_empty],
           "borders": rounded(merged(borders)), "coast": rounded(merged(coast)), "detail": detail}
    coast_u = unary_union(coast).buffer(1e-4)
    extra = {}
    for k, g in geo.items():
        if k.startswith(prefix + "-"):
            nb = sorted({names[j] for j, h in geo.items() if j.startswith("T-") and g.boundary.intersection(h.boundary).length > 0.01})
            extra[k] = {"coastal": g.boundary.intersection(coast_u).length > 0.03, "borders": nb}
            main = max(getattr(g, "geoms", [g]), key=lambda p: p.area)
            if not main.contains(main.centroid):
                p = shapely.maximum_inscribed_circle(main, 0.01).coords[0]
                extra[k]["anchorLL"] = [round(p[0], 3), round(p[1], 3)]
    return out, extra


def cap_ll(name, prov_code):
    import capitals
    ll = CAP_LL.get(name) or capitals.find(name, a2="ES")
    if ll and prov_code in CANARY_PROV:
        ll = [round(ll[0] + SHIFT[0], 3), round(ll[1] + SHIFT[1], 3)]
    return ll


def flag(src, dst):
    im = Image.open(src).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    Image.alpha_composite(bg, im).convert("RGB").save(dst, "WEBP", quality=88)


def main():
    import es_facts
    pareas, community = province_areas()
    pops = populations()
    missing = []
    # ----- the provinces -----
    fc, extra = build_set(pareas, "ESP", "esp")
    (ROOT / "data" / "esp-states.json").write_text(json.dumps(fc, separators=(",", ":")), encoding="utf8")
    items = []
    for code, (name, table, cap, alt, cap_alt) in PROVINCES.items():
        iso = "ESP-" + code
        pop, area = pops[table]
        com = COMMUNITIES[community[code]][0]
        it = {"iso": iso, "id": iso, "name": name, "names": list(dict.fromkeys([name, table] + alt)), "capitals": [cap] + cap_alt,
              "cont": ["Europe"], "car": False, "a2": iso,
              "info": {"kind": "Autonomous city" if code in ("CE", "ML") else "Province", "community": com, "pop": pop, "popYear": "2025",
                       "area": round(area), "flag": False, "facts": {"landmark": es_facts.PROVINCE_LANDMARK.get(code, "")},
                       **{k: v for k, v in extra.get(iso, {}).items() if k != "anchorLL"}}}
        if code in CANARY_PROV:
            it["info"]["inset"] = True
        if "anchorLL" in extra.get(iso, {}):
            it["anchorLL"] = extra[iso]["anchorLL"]
        ll = cap_ll(cap, code)
        if not ll:
            missing.append(cap)
        it["capLL"] = [ll] if ll else []
        items.append(it)
    total = sum(it["info"]["pop"] for it in items)
    by_area = sorted(items, key=lambda c: -c["info"]["area"])
    for it in items:
        it["info"]["areaRank"] = by_area.index(it) + 1
    (ROOT / "data" / "esp-parts.json").write_text(json.dumps(sorted(items, key=lambda s: s["name"]), ensure_ascii=False, indent=0), encoding="utf8")
    print(f"  provinces: {len(items)} parts, population {total:,} (INE, 1 January 2025)")
    # ----- the communities (dissolved from the provinces) -----
    careas = {c: polygonal(unary_union([g for p, g in pareas.items() if community[p] == c]).buffer(0)) for c in COMMUNITIES}
    fc, extra = build_set(careas, "ES", "es")
    (ROOT / "data" / "es-states.json").write_text(json.dumps(fc, separators=(",", ":")), encoding="utf8")
    out_flags = ROOT / "data" / "flags" / "es"
    out_flags.mkdir(parents=True, exist_ok=True)
    citems = []
    for c, (name, caps, alt) in COMMUNITIES.items():
        iso = "ES-" + c
        src = ESDL / "flags" / f"{iso}.png"
        if src.exists():
            flag(src, out_flags / f"{iso}.webp")
        f = es_facts.FACTS.get(c, {})
        provs = [p for p in PROVINCES if community[p] == c]
        pop = sum(pops[PROVINCES[p][1]][0] for p in provs)
        area = sum(pops[PROVINCES[p][1]][1] for p in provs)
        names = [name, f.get("spanish", name), f.get("own", name)] + alt
        it = {"iso": iso, "id": iso, "name": name, "names": list(dict.fromkeys(names)), "capitals": caps, "cont": ["Europe"], "car": False,
              "a2": iso, "info": {"kind": "Autonomous city" if c in ("CE", "ML") else "Autonomous community", "pop": pop, "popYear": "2025",
                                  "area": round(area), "flag": src.exists(), "facts": f, "provinces": len(provs),
                                  **{k: v for k, v in extra.get(iso, {}).items() if k != "anchorLL"}},
              "flagKey": "es/" + iso}
        if c == "CN":
            it["info"]["inset"] = True
        if "anchorLL" in extra.get(iso, {}):
            it["anchorLL"] = extra[iso]["anchorLL"]
        lls = [cap_ll(x, "TF" if c == "CN" else "") for x in caps[:2 if c == "CN" else 1]]
        if not all(lls):
            missing.append(caps[0])
        it["capLL"] = [ll for ll in lls if ll]
        citems.append(it)
    by_area = sorted(citems, key=lambda c: -c["info"]["area"])
    for it in citems:
        it["info"]["areaRank"] = by_area.index(it) + 1
    ctotal = sum(it["info"]["pop"] for it in citems)
    (ROOT / "data" / "es-parts.json").write_text(json.dumps(sorted(citems, key=lambda s: s["name"]), ensure_ascii=False, indent=0), encoding="utf8")
    print(f"  communities: {len(citems)} parts, {sum(it['info']['flag'] for it in citems)} flags, population {ctotal:,}"
          f" {'(matches the provinces)' if ctotal == total else 'MISMATCH'}")
    if missing:
        print("  capitals not found:", missing)


if __name__ == "__main__":
    main()
