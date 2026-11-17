"""Builds Australia's country map (Australia_plan.md): 6 states, 2 mainland territories and Jervis Bay.

  data/au-states.json  the 9 shapes (Natural Earth 1:10m admin-1; Lord Howe Island with New South Wales; Macquarie
                       Island and the external territories left off), the countries around as grey context.
                       Lines: "borders", "coast".
  data/au-parts.json   names, capitals, kind, Learning facts (tools/au_facts.py); populations from the 2021 census
  data/flags/au/       the 8 state and territory flags (Wikimedia Commons; Jervis Bay has none)
  data/tribal-au.json  the Aboriginal land layer: native title (NNTT) and Indigenous Protected Areas (DCCEEW)

Run from the repo root:  python tools/build_au.py   (or  python tools/build_au.py land  for the layer only)
"""
import io
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request

import geopandas as gpd
import shapely
from PIL import Image
from shapely.geometry import mapping, MultiLineString
from shapely.ops import unary_union, linemerge

ROOT = pathlib.Path(__file__).resolve().parent.parent
NE = ROOT / "tools" / "downloads" / "ne10"
SIMPLIFY = 0.01
UA = {"User-Agent": "GaiaQuestBuild/1.0 (map quiz data build)"}

# abbreviation -> (name, kind, capitals, population (2021 census), area km² (Geoscience Australia), year it became a
#                  colony or territory, Natural Earth admin-1 names, Commons flag file)
PARTS = {
    "NSW": ("New South Wales", "State", ["Sydney"], 8072163, 800642, 1788, ["New South Wales", "Lord Howe Island"], "Flag of New South Wales.svg"),
    "VIC": ("Victoria", "State", ["Melbourne"], 6503491, 227416, 1851, ["Victoria"], "Flag of Victoria (Australia).svg"),
    "QLD": ("Queensland", "State", ["Brisbane"], 5156138, 1730648, 1859, ["Queensland"], "Flag of Queensland.svg"),
    "WA": ("Western Australia", "State", ["Perth"], 2660026, 2527013, 1829, ["Western Australia"], "Flag of Western Australia.svg"),
    "SA": ("South Australia", "State", ["Adelaide"], 1781516, 983482, 1836, ["South Australia"], "Flag of South Australia.svg"),
    "TAS": ("Tasmania", "State", ["Hobart"], 557571, 68401, 1825, ["Tasmania"], "Flag of Tasmania.svg"),
    "NT": ("Northern Territory", "Territory", ["Darwin"], 232605, 1349129, 1911, ["Northern Territory"], "Flag of the Northern Territory.svg"),
    "ACT": ("Australian Capital Territory", "Territory", ["Canberra"], 454499, 2358, 1911, ["Australian Capital Territory"],
            "Flag of the Australian Capital Territory.svg"),
    "JBT": ("Jervis Bay Territory", "Territory", [], 311, 67, 1915, ["Jervis Bay Territory"], None),
}
NAMES = {"NSW": ["NSW"], "VIC": ["VIC"], "QLD": ["QLD", "Queensland"], "WA": ["WA"], "SA": ["SA"], "TAS": ["TAS", "Tassie"],
         "NT": ["NT", "The Territory"], "ACT": ["ACT"], "JBT": ["Jervis Bay", "JBT"]}
NOT_TYPO = {"SA": ["WA"], "WA": ["SA"]}
WINDOW = shapely.box(100, -50, 165, -2)  # wide enough for a tall phone screen


def polygonal(g):
    g = shapely.make_valid(g)
    if g.geom_type in ("Polygon", "MultiPolygon"):
        return g
    return unary_union([p for p in getattr(g, "geoms", []) if p.geom_type in ("Polygon", "MultiPolygon")])


def lines_only(g):
    if g.is_empty:
        return []
    if g.geom_type == "LineString":
        return [g]
    if g.geom_type == "MultiLineString":
        return list(g.geoms)
    return [x for part in getattr(g, "geoms", []) for x in lines_only(part)]


def rounded(geom, nd=3):
    def r(c):
        return [round(c[0], nd), round(c[1], nd)] if isinstance(c[0], (int, float)) else [r(x) for x in c]
    m = mapping(geom)
    return {"type": m["type"], "coordinates": r(json.loads(json.dumps(m["coordinates"])))}


def shapes():
    a1 = gpd.read_file(NE / "ne_10m_admin_1_states_provinces.geojson")
    a0 = gpd.read_file(NE / "ne_10m_admin_0_countries.geojson")
    au = a1[a1["adm0_a3"] == "AUS"]
    areas = {}
    for code, p in PARTS.items():
        areas["AU-" + code] = polygonal(unary_union([polygonal(g) for g in au[au["name"].isin(p[6])].geometry]))
        assert not areas["AU-" + code].is_empty, code
    land = unary_union(list(areas.values()))
    names = {}
    for _, r in a0[a0.intersects(WINDOW)].iterrows():
        a3 = r["ADM0_A3"]
        if a3 == "AUS" or r["SOVEREIGNT"] == "Australia":
            continue  # external territories: left off (Australia_plan.md)
        g = polygonal(polygonal(r.geometry).intersection(WINDOW).difference(land))
        g = unary_union([q for q in getattr(g, "geoms", [g]) if q.area > 0.005])
        if not g.is_empty:
            areas["T-" + a3] = polygonal(g)
            names["T-" + a3] = r["NAME"]
    merged = lambda ls: linemerge(ls) if ls else MultiLineString([])
    keys = list(areas)
    geo = shapely.coverage_clean([areas[k] for k in keys], gap_width=0.002, snapping_distance=0.0001)
    geo = shapely.coverage_simplify([polygonal(g) for g in geo], SIMPLIFY)
    geo = {k: polygonal(shapely.set_precision(polygonal(g), 0.001)) for k, g in zip(keys, geo)}
    borders, pairs = [], []
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            A, B = geo[a].bounds, geo[b].bounds
            if A[0] > B[2] or B[0] > A[2] or A[1] > B[3] or B[1] > A[3]:
                continue
            ls = lines_only(geo[a].boundary.intersection(geo[b].boundary))
            borders += ls
            if ls:
                pairs.append([a, b, rounded(merged(ls))])
    bu = unary_union(borders)  # (merged is defined above the loop)
    coast = lines_only(unary_union([g.boundary for g in geo.values()]).difference(bu.buffer(1e-7))
                       .difference(WINDOW.exterior.buffer(0.01)))
    out = {"type": "FeatureCollection",
           "features": [{"type": "Feature", "id": k, "geometry": rounded(g)} for k, g in geo.items() if not g.is_empty],
           "borders": rounded(merged(borders)), "coast": rounded(merged(coast)), "pairs": pairs}
    coast_u = unary_union(coast).buffer(1e-4)
    extra = {k: {"coastal": g.boundary.intersection(coast_u).length > 0.02} for k, g in geo.items() if k.startswith("AU-")}
    return out, extra


# ----- the "Aboriginal land" layer (Learning mode, like the US reservations): data/tribal-au.json -----
# Native title determinations where native title exists (National Native Title Tribunal, CC BY 4.0) and dedicated
# Indigenous Protected Areas (DCCEEW, CC BY 4.0), simplified and clipped to the coast. Kinds: "NT" native title over the
# whole area, "NTP" native title in parts of it, "IPA" Indigenous Protected Area.
AU_DL = ROOT / "tools" / "downloads" / "au"


def land_layer():
    import tempfile
    import zipfile
    states = json.loads((ROOT / "data" / "au-states.json").read_text(encoding="utf8"))
    from shapely.geometry import shape
    coast = unary_union([shape(f["geometry"]) for f in states["features"] if f["id"].startswith("AU-")]).buffer(0.01)
    with tempfile.TemporaryDirectory() as tmp:
        zipfile.ZipFile(AU_DL / "ntd_register_nat_shp.zip").extractall(tmp)
        nt = gpd.read_file(pathlib.Path(tmp) / "NTD_Register_Nat.shp").to_crs(4326)
    ipa = gpd.read_file(AU_DL / "ipa_dedicated.geojson").to_crs(4326)
    rows = []
    for _, r in nt.iterrows():
        out = r["DETOUTCOME"] or ""
        if out.startswith("Native title exists in the entire"):
            rows.append((r["NAME"], "NT", r.geometry))
        elif out.startswith("Native title exists in parts"):
            rows.append((r["NAME"], "NTP", r.geometry))
    rows += [(r["NAME"], "IPA", r.geometry) for _, r in ipa.iterrows()]
    feats = []
    for name, kind, g in rows:
        if g is None:
            continue
        g = polygonal(polygonal(g).intersection(coast))
        if g.is_empty:
            continue
        g0, g = g, polygonal(shapely.set_precision(g.simplify(0.025), 0.005))  # about 2.5 km: lighter for phones
        parts = [q for q in getattr(g, "geoms", [g]) if max(q.bounds[2] - q.bounds[0], q.bounds[3] - q.bounds[1]) > 0.004]
        if parts:
            feats.append({"type": "Feature", "properties": {"n": name, "k": kind}, "geometry": rounded(unary_union(parts), 3)})
        else:  # too small to outline: a dot
            c = g0.representative_point()
            feats.append({"type": "Feature", "properties": {"n": name, "k": kind}, "geometry": {"type": "Point", "coordinates": [round(c.x, 3), round(c.y, 3)]}})
    # the protected areas last, so they draw over the native title they often sit inside
    feats.sort(key=lambda f: f["properties"]["k"] == "IPA")
    (ROOT / "data" / "tribal-au.json").write_text(json.dumps({"type": "FeatureCollection", "features": feats}, ensure_ascii=False,
                                                              separators=(",", ":")), encoding="utf8")
    print("wrote data/tribal-au.json:", len(feats), "areas")


def flags():
    out = ROOT / "data" / "flags" / "au"
    out.mkdir(parents=True, exist_ok=True)
    for code, p in PARTS.items():
        f = p[7]
        dest = out / f"AU-{code}.webp"
        if not f or dest.exists():
            continue
        url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(f.replace(" ", "_")) + "?width=640"
        for attempt in range(4):
            try:
                data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
                break
            except Exception as e:  # Commons rate-limits: wait and try again
                print("retrying", code, e)
                time.sleep(5 * (attempt + 1))
        else:
            raise SystemExit(f"could not download the flag of {code} ({f})")
        Image.open(io.BytesIO(data)).convert("RGB").save(dest, "WEBP", quality=88)
        time.sleep(1.5)
    print("flags in", out)


def main():
    fc, extra = shapes()
    (ROOT / "data" / "au-states.json").write_text(json.dumps(fc, separators=(",", ":")), encoding="utf8")
    sys.path.insert(0, str(ROOT / "tools"))
    import au_facts
    import capitals
    items = []
    for code, (name, kind, caps, pop, area, year, _, flag) in PARTS.items():
        iso = "AU-" + code
        it = {"iso": iso, "id": iso, "name": name, "names": list(dict.fromkeys([name] + NAMES.get(code, []))), "capitals": caps,
              "cont": ["Oceania"], "car": False, "a2": iso,
              "info": {"abbr": code, "kind": kind, "pop": pop, "popYear": "2021 census", "area": area, "year": year,
                       "flag": bool(flag), "facts": au_facts.FACTS.get(code, {}), **extra.get(iso, {})},
              "flagKey": "au/" + iso}
        if code in NOT_TYPO:
            it["notTypo"] = NOT_TYPO[code]
        it["capLL"] = [ll for ll in [capitals.find(c, a2="AU") for c in caps[:1]] if ll]
        if caps and not it["capLL"]:
            print("capital not found:", caps[0])
        items.append(it)
    by_area = sorted(items, key=lambda c: -c["info"]["area"])
    for it in items:
        it["info"]["areaRank"] = by_area.index(it) + 1
    (ROOT / "data" / "au-parts.json").write_text(json.dumps(sorted(items, key=lambda s: s["name"]), ensure_ascii=False, indent=0), encoding="utf8")
    print("wrote data/au-states.json and data/au-parts.json:", len(items), "parts")
    flags()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "land":
        land_layer()  # just the Aboriginal land layer (needs data/au-states.json)
    else:
        main()
        land_layer()
