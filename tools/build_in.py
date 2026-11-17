"""Builds India's country map (India_plan.md): 28 states and 8 union territories.

  data/in-states.json   the 36 shapes (Natural Earth 1:10m admin-1, which shows the areas India administers and is
                        current: Ladakh split from Jammu and Kashmir in 2019, Dadra and Nagar Haveli and Daman and Diu
                        merged in 2020), the neighbours as grey areas, and the disputed areas of Kashmir and the China
                        border as grey areas of their own. Lines: "borders", "coast" and "disputed" (drawn dotted).
  data/in-parts.json    the 36 parts: names, capitals, kind, region and Learning facts (hand-written below; populations
                        from the 2011 census, the latest published)

Run from the repo root:  python tools/build_in.py
"""
import json
import pathlib
import sys

import geopandas as gpd
import shapely
from shapely.geometry import shape, mapping, MultiLineString
from shapely.ops import unary_union, linemerge

ROOT = pathlib.Path(__file__).resolve().parent.parent
NE = ROOT / "tools" / "downloads" / "ne10"
SIMPLIFY = 0.01  # degrees (about 1 km): India is big, and the coverage is simplified as a whole

# name (as Natural Earth spells it) -> (id, shown name, kind, region, capitals (first shown), population 2011, area km²,
#                                       year formed in its present shape, formed from)
PARTS = {
    "Andhra Pradesh": ("AP", "Andhra Pradesh", "State", "South", ["Amaravati"], 49386799, 162968, 2014, "split into Andhra Pradesh and Telangana (1953 as Andhra State)"),
    "Arunachal Pradesh": ("AR", "Arunachal Pradesh", "State", "Northeast", ["Itanagar"], 1383727, 83743, 1987, "the North-East Frontier Agency; a state in 1987"),
    "Assam": ("AS", "Assam", "State", "Northeast", ["Dispur"], 31205576, 78438, 1950, "a founding state"),
    "Bihar": ("BR", "Bihar", "State", "East", ["Patna"], 104099452, 94163, 2000, "Jharkhand split off in 2000"),
    "Chhattisgarh": ("CG", "Chhattisgarh", "State", "Central", ["Raipur", "Nava Raipur"], 25545198, 135192, 2000, "Madhya Pradesh"),
    "Goa": ("GA", "Goa", "State", "West", ["Panaji", "Panjim"], 1458545, 3702, 1987, "Portuguese India until 1961; a state in 1987"),
    "Gujarat": ("GJ", "Gujarat", "State", "West", ["Gandhinagar"], 60439692, 196024, 1960, "Bombay State"),
    "Haryana": ("HR", "Haryana", "State", "North", ["Chandigarh"], 25351462, 44212, 1966, "Punjab"),
    "Himachal Pradesh": ("HP", "Himachal Pradesh", "State", "North", ["Shimla", "Dharamshala"], 6864602, 55673, 1971, "a union territory from 1950; a state in 1971"),
    "Jharkhand": ("JH", "Jharkhand", "State", "East", ["Ranchi"], 32988134, 79716, 2000, "Bihar"),
    "Karnataka": ("KA", "Karnataka", "State", "South", ["Bengaluru", "Bangalore"], 61095297, 191791, 1956, "Mysore State, renamed Karnataka in 1973"),
    "Kerala": ("KL", "Kerala", "State", "South", ["Thiruvananthapuram", "Trivandrum"], 33406061, 38852, 1956, "Travancore-Cochin and Malabar"),
    "Madhya Pradesh": ("MP", "Madhya Pradesh", "State", "Central", ["Bhopal"], 72626809, 308252, 1956, "Madhya Bharat, Vindhya Pradesh, Bhopal State and part of Central Provinces"),
    "Maharashtra": ("MH", "Maharashtra", "State", "West", ["Mumbai", "Bombay", "Nagpur"], 112374333, 307713, 1960, "Bombay State"),
    "Manipur": ("MN", "Manipur", "State", "Northeast", ["Imphal"], 2855794, 22327, 1972, "a union territory from 1956; a state in 1972"),
    "Meghalaya": ("ML", "Meghalaya", "State", "Northeast", ["Shillong"], 2966889, 22429, 1972, "Assam"),
    "Mizoram": ("MZ", "Mizoram", "State", "Northeast", ["Aizawl"], 1097206, 21081, 1987, "Assam; a union territory from 1972"),
    "Nagaland": ("NL", "Nagaland", "State", "Northeast", ["Kohima"], 1978502, 16579, 1963, "Assam"),
    "Odisha": ("OD", "Odisha", "State", "East", ["Bhubaneswar"], 41974218, 155707, 1950, "a founding state (Orissa, renamed Odisha in 2011)"),
    "Punjab": ("PB", "Punjab", "State", "North", ["Chandigarh"], 27743338, 50362, 1966, "split into Punjab, Haryana and Himachal Pradesh"),
    "Rajasthan": ("RJ", "Rajasthan", "State", "North", ["Jaipur"], 68548437, 342239, 1956, "the Rajputana princely states, joined 1948–1956"),
    "Sikkim": ("SK", "Sikkim", "State", "Northeast", ["Gangtok"], 610577, 7096, 1975, "the Kingdom of Sikkim"),
    "Tamil Nadu": ("TN", "Tamil Nadu", "State", "South", ["Chennai", "Madras"], 72147030, 130060, 1956, "Madras State, renamed Tamil Nadu in 1969"),
    "Telangana": ("TS", "Telangana", "State", "South", ["Hyderabad"], 35193978, 112077, 2014, "Andhra Pradesh"),
    "Tripura": ("TR", "Tripura", "State", "Northeast", ["Agartala"], 3673917, 10486, 1972, "a union territory from 1956; a state in 1972"),
    "Uttar Pradesh": ("UP", "Uttar Pradesh", "State", "North", ["Lucknow"], 199812341, 240928, 2000, "Uttarakhand split off in 2000"),
    "Uttarakhand": ("UK", "Uttarakhand", "State", "North", ["Dehradun", "Gairsain", "Bhararisain"], 10086292, 53483, 2000, "Uttar Pradesh (as Uttaranchal)"),
    "West Bengal": ("WB", "West Bengal", "State", "East", ["Kolkata", "Calcutta"], 91276115, 88752, 1950, "a founding state"),
    "Andaman and Nicobar": ("AN", "Andaman and Nicobar Islands", "Union territory", "Islands", ["Sri Vijaya Puram", "Port Blair"], 380581, 8249, 1956, "a union territory since 1956"),
    "Chandigarh": ("CH", "Chandigarh", "Union territory", "North", ["Chandigarh"], 1055450, 114, 1966, "Punjab, as the shared capital of Punjab and Haryana"),
    "Dadra and Nagar Haveli and Daman and Diu": ("DH", "Dadra and Nagar Haveli and Daman and Diu", "Union territory", "West", ["Daman"], 586956, 603, 2020, "two union territories merged in 2020"),
    "Delhi": ("DL", "Delhi", "Union territory", "North", ["New Delhi", "Delhi"], 16787941, 1484, 1956, "a union territory since 1956; the National Capital Territory since 1991"),
    "Jammu and Kashmir": ("JK", "Jammu and Kashmir", "Union territory", "North", ["Srinagar", "Jammu"], 12267013, 42241, 2019, "the state of Jammu and Kashmir, split in 2019"),
    "Ladakh": ("LA", "Ladakh", "Union territory", "North", ["Leh", "Kargil"], 274289, 59146, 2019, "the state of Jammu and Kashmir, split in 2019"),
    "Lakshadweep": ("LD", "Lakshadweep", "Union territory", "Islands", ["Kavaratti"], 64473, 32, 1956, "a union territory since 1956"),
    "Puducherry": ("PY", "Puducherry", "Union territory", "South", ["Puducherry", "Pondicherry"], 1247953, 479, 1962, "French India, joined 1954–1962"),
}
# capitals with more than one seat: shown on the card
CAPITAL_NOTE = {
    "MH": "Mumbai (Nagpur hosts the winter session)", "HP": "Shimla (Dharamshala in winter)",
    "UK": "Dehradun (Bhararisain/Gairsain in summer)", "JK": "Srinagar in summer, Jammu in winter",
    "LA": "Leh (also Kargil)", "AN": "Sri Vijaya Puram (Port Blair until 2024)",
}
# extra names accepted when typing (accents and "&" are already handled)
NAMES = {
    "UP": ["UP"], "MP": ["MP"], "AP": ["AP"], "HP": ["HP"], "TN": ["TN"], "WB": ["WB", "Bengal"], "JK": ["J&K", "JK", "Kashmir"],
    "DL": ["NCT", "National Capital Territory", "New Delhi"], "OD": ["Orissa"], "PY": ["Pondicherry"], "UK": ["Uttaranchal"],
    "AN": ["Andaman and Nicobar", "Andaman", "Andamans"], "DH": ["DNHDD", "Dadra and Nagar Haveli", "Daman and Diu", "Daman"],
    "TS": ["Telengana"], "CG": ["Chattisgarh"], "KA": ["Mysore"], "MH": [], "AR": ["Arunachal"],
}
# grey neighbours (Natural Earth admin-0) and disputed areas (Natural Earth disputed areas), by their names there
NEIGHBOURS = {"PAK": "Pakistan", "CHN": "China", "NPL": "Nepal", "BTN": "Bhutan", "BGD": "Bangladesh", "MMR": "Myanmar",
              "LKA": "Sri Lanka", "AFG": "Afghanistan"}
DISPUTED_GREY = {"Gilgit-Baltistan": "T-GB", "Azad Kashmir": "T-AJK", "Aksai Chin": "T-AKSAI", "Shaksam Valley": "T-SHAKSGAM",
                 "Siachen Glacier": "T-SIACHEN"}
# Indian-administered areas China claims: their borders with China are dotted
CLAIMED_BY_CHINA = {"Arunachal Pradesh", "Demchok", "Samdu Valleys", "Tirpani Valleys", "Bara Hotii Valleys"}


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
    dsp = gpd.read_file(NE / "ne_10m_admin_0_disputed_areas.geojson")
    ind = a1[a1["adm0_a3"] == "IND"]
    areas = {}
    for _, r in ind.iterrows():
        if r["name"] not in PARTS:
            raise SystemExit(f"unexpected part: {r['name']}")
        areas[PARTS[r["name"]][0]] = polygonal(r.geometry)
    assert len(areas) == 36, len(areas)
    grey_dsp = {}
    for _, r in dsp.iterrows():
        if r["BRK_NAME"] in DISPUTED_GREY:
            grey_dsp[DISPUTED_GREY[r["BRK_NAME"]]] = polygonal(r.geometry)
    assert set(grey_dsp) == set(DISPUTED_GREY.values()), set(DISPUTED_GREY.values()) - set(grey_dsp)
    dsp_all = unary_union(list(grey_dsp.values()))
    window = shapely.box(55, 0, 105, 40)  # neighbours only near India
    for a3 in NEIGHBOURS:
        g = polygonal(a0[a0["ADM0_A3"] == a3].geometry.iloc[0]).intersection(window)
        areas["T-" + a3] = polygonal(g.difference(dsp_all))  # the disputed areas are their own grey shapes
    areas.update(grey_dsp)
    keys = list(areas)
    geo = shapely.coverage_clean([areas[k] for k in keys], gap_width=0.002, snapping_distance=0.0001)
    geo = shapely.coverage_simplify([polygonal(g) for g in geo], SIMPLIFY)
    geo = {k: polygonal(shapely.set_precision(polygonal(g), 0.001)) for k, g in zip(keys, geo)}
    # lines: shared borders, coast, and the disputed stretches (Kashmir's Line of Control and the borders with
    # Pakistan there, the line with China in Ladakh and Aksai Chin, Arunachal Pradesh's border with China)
    claimed = unary_union([polygonal(r.geometry) for _, r in dsp.iterrows() if r["BRK_NAME"] in CLAIMED_BY_CHINA])
    borders, disputed = [], []
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            A, B = geo[a].bounds, geo[b].bounds
            if A[0] > B[2] or B[0] > A[2] or A[1] > B[3] or B[1] > A[3]:
                continue
            ls = lines_only(geo[a].boundary.intersection(geo[b].boundary))
            if not ls:
                continue
            pair = {a, b}
            indian = [k for k in pair if not k.startswith("T-")]
            if not indian:
                borders += ls  # between two grey areas: not India's line, drawn as an ordinary border
            elif pair & set(DISPUTED_GREY.values()) or (pair & {"T-PAK"} and pair & {"JK", "LA"}):
                disputed += ls
            elif indian and "T-CHN" in pair:
                line = unary_union(ls)
                d = line.intersection(claimed.buffer(0.05))
                disputed += lines_only(d)
                borders += lines_only(line.difference(claimed.buffer(0.05)))
            else:
                borders += ls
    bu = unary_union(borders + disputed)
    coast = lines_only(unary_union([g.boundary for g in geo.values()]).difference(bu.buffer(1e-7)))
    merged = lambda ls: linemerge(ls) if ls else MultiLineString([])
    out = {"type": "FeatureCollection",
           "features": [{"type": "Feature", "id": k, "geometry": rounded(g)} for k, g in geo.items() if not g.is_empty],
           "borders": rounded(merged(borders)), "coast": rounded(merged(coast)), "disputed": rounded(merged(disputed))}
    # for the cards: which parts reach the sea, and which countries each one borders (disputed areas named as such)
    coast_u = unary_union(coast).buffer(1e-4)
    names = {"T-" + k: v for k, v in NEIGHBOURS.items()}
    names.update({"T-GB": "Pakistan (Gilgit-Baltistan, disputed)", "T-AJK": "Pakistan (Azad Kashmir, disputed)",
                  "T-AKSAI": "China (Aksai Chin, disputed)", "T-SHAKSGAM": "China (Shaksgam, disputed)", "T-SIACHEN": "Siachen (disputed)"})
    extra = {}
    for k, g in geo.items():
        if k.startswith("T-"):
            continue
        nb = sorted({names[j] for j, h in geo.items() if j.startswith("T-") and g.boundary.intersection(h.boundary).length > 0.01})
        extra[k] = {"coastal": g.boundary.intersection(coast_u).length > 0.05, "borders": nb}
    return out, geo, extra


def main():
    fc, geo, extra = shapes()
    sys.path.insert(0, str(ROOT / "tools"))
    import in_facts
    (ROOT / "data" / "in-states.json").write_text(json.dumps(fc, separators=(",", ":")), encoding="utf8")
    items = []
    for ne_name, (iso, name, kind, region, caps, pop, area, year, origin) in PARTS.items():
        names = [name] + NAMES.get(iso, [])
        names += [n.replace(" and ", " & ") for n in names if " and " in n]  # "Jammu & Kashmir"
        items.append({"iso": iso, "id": iso, "name": name, "names": list(dict.fromkeys(names)), "capitals": caps,
                      "cont": ["Asia"], "car": False, "a2": iso,
                      "info": {"abbr": iso, "kind": kind, "region": region, "pop": pop, "popYear": "2011 census", "area": area,
                               "year": year, "origin": origin, "capNote": CAPITAL_NOTE.get(iso), "flag": False,
                               "facts": in_facts.FACTS.get(iso, {}), **extra.get(iso, {})}})
    by_area = sorted(items, key=lambda c: -c["info"]["area"])
    for it in items:
        it["info"]["areaRank"] = by_area.index(it) + 1
    import capitals
    missing = []
    for it in items:
        pts = []
        for city in sorted(set([it["capitals"][0]] + ([it["capitals"][1]] if it["iso"] == "JK" else [])), key=it["capitals"].index):
            ll = capitals.find({"Sri Vijaya Puram": "Port Blair"}.get(city, city), a2="IN")
            (pts.append(ll) if ll else missing.append(f"{it['name']}: {city}"))
        it["capLL"] = pts
    if missing:
        print("capitals not found:", missing)
    (ROOT / "data" / "in-parts.json").write_text(json.dumps(sorted(items, key=lambda s: s["name"]), ensure_ascii=False, indent=0), encoding="utf8")
    print("wrote data/in-states.json and data/in-parts.json:", len(items), "parts;",
          f"{sum(len(l) for l in fc['disputed']['coordinates']) if fc['disputed']['type'] == 'MultiLineString' else len(fc['disputed']['coordinates'])} disputed-line points")


if __name__ == "__main__":
    main()
