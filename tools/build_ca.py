"""Builds the Canada data (provinces and territories), the second country map after the US states:

  data/ca-provinces.json  the 13 shapes (Natural Earth 1:50m admin-1, public domain), with the US and Greenland as grey
                          areas around them for context, and the border and coastline lines worked out in advance:
                          {"type": "FeatureCollection", "features": [...], "borders": MultiLineString, "coast": MultiLineString}
  data/provinces.json     the 13 provinces and territories: names, capitals and Learning mode facts (hand-written below,
                          2021 census)
  data/flags/ca/<code>.webp  their flags (Wikimedia Commons, 640 px wide)

Run from the repo root:  python tools/build_ca.py
"""
import io
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request

from PIL import Image
from shapely.geometry import shape, mapping, MultiLineString, LineString
from shapely.ops import unary_union, linemerge

ROOT = pathlib.Path(__file__).resolve().parent.parent
DL = ROOT / "tools" / "downloads" / "canada"
NE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
ADMIN1 = NE + "ne_50m_admin_1_states_provinces.geojson"
ADMIN0 = NE + "ne_50m_admin_0_countries.geojson"
UA = {"User-Agent": "GaiaQuestBuild/1.0 (map quiz data build)"}

# code: (name, capital, largest city if not the capital, kind, joined Confederation, population 2021 census, region)
PROVINCES = {
    "AB": ("Alberta", "Edmonton", "Calgary", "Province", 1905, 4262635, "Prairies"),
    "BC": ("British Columbia", "Victoria", "Vancouver", "Province", 1871, 5000879, "West Coast"),
    "MB": ("Manitoba", "Winnipeg", "", "Province", 1870, 1342153, "Prairies"),
    "NB": ("New Brunswick", "Fredericton", "Moncton", "Province", 1867, 775610, "Atlantic"),
    "NL": ("Newfoundland and Labrador", "St. John's", "", "Province", 1949, 510550, "Atlantic"),
    "NS": ("Nova Scotia", "Halifax", "", "Province", 1867, 969383, "Atlantic"),
    "NT": ("Northwest Territories", "Yellowknife", "", "Territory", 1870, 41070, "The North"),
    "NU": ("Nunavut", "Iqaluit", "", "Territory", 1999, 36858, "The North"),
    "ON": ("Ontario", "Toronto", "", "Province", 1867, 14223942, "Central"),
    "PE": ("Prince Edward Island", "Charlottetown", "", "Province", 1873, 154331, "Atlantic"),
    "QC": ("Quebec", "Quebec City", "Montreal", "Province", 1867, 8501833, "Central"),
    "SK": ("Saskatchewan", "Regina", "Saskatoon", "Province", 1905, 1132505, "Prairies"),
    "YT": ("Yukon", "Whitehorse", "", "Territory", 1898, 40232, "The North"),
}
# More Learning facts (hand-written): time zones (main first), name origin, highest point (name, m),
# total area in km² (Statistics Canada), bird, flower, Commons file name of the flag
FACTS = {
    "AB": ("Mountain", "Princess Louise Caroline Alberta, a daughter of Queen Victoria", ("Mount Columbia", 3747), 661848,
           "Great horned owl", "Wild rose", "Flag of Alberta.svg"),
    "BC": ("Pacific; Mountain (the northeast and the East Kootenays)", "The Columbia River, named after the ship Columbia; \"British\" set it apart from the American Columbia district",
           ("Mount Fairweather", 4663), 944735, "Steller's jay", "Pacific dogwood", "Flag of British Columbia.svg"),
    "MB": ("Central", "Probably Cree or Ojibwe for \"strait of the spirit\", after the narrows of Lake Manitoba", ("Baldy Mountain", 832), 647797,
           "Great grey owl", "Prairie crocus", "Flag of Manitoba.svg"),
    "NB": ("Atlantic", "The German duchy of Brunswick-Lüneburg, the family home of King George III", ("Mount Carleton", 817), 72908,
           "Black-capped chickadee", "Purple violet", "Flag of New Brunswick.svg"),
    "NL": ("Newfoundland; Atlantic (most of Labrador)", "Newfoundland: the \"new found land\"; Labrador probably after the Portuguese explorer João Fernandes Lavrador",
           ("Mount Caubvick", 1652), 405212, "Atlantic puffin", "Pitcher plant", "Flag of Newfoundland and Labrador.svg"),
    "NS": ("Atlantic", "Latin for \"New Scotland\"", ("White Hill", 532), 55284, "Osprey", "Mayflower", "Flag of Nova Scotia.svg"),
    "NT": ("Mountain", "The old North-Western Territory, bought from the Hudson's Bay Company in 1870", ("Mount Nirvana", 2773), 1346106,
           "Gyrfalcon", "Mountain avens", "Flag of the Northwest Territories.svg"),
    "NU": ("Eastern; Central; Mountain", "Inuktitut for \"our land\"", ("Barbeau Peak", 2616), 2093190,
           "Rock ptarmigan", "Purple saxifrage", "Flag of Nunavut.svg"),
    "ON": ("Eastern; Central (the northwest)", "Lake Ontario; an Iroquoian word often given as \"great lake\" or \"beautiful water\"", ("Ishpatina Ridge", 693), 1076395,
           "Common loon", "White trillium", "Flag of Ontario.svg"),
    "PE": ("Atlantic", "Prince Edward, Duke of Kent, the father of Queen Victoria", ("Near Springton", 142), 5660,
           "Blue jay", "Pink lady's slipper", "Flag of Prince Edward Island.svg"),
    "QC": ("Eastern; Atlantic (the Magdalen Islands and the far east)", "Algonquin for \"where the river narrows\", at Quebec City", ("Mont D'Iberville", 1652), 1542056,
           "Snowy owl", "Blue flag iris", "Flag of Quebec.svg"),
    "SK": ("Central (no daylight saving); Mountain (around Lloydminster)", "The Saskatchewan River; Cree kisiskāciwani-sīpiy, \"swift-flowing river\"", ("Cypress Hills", 1392), 651036,
           "Sharp-tailed grouse", "Western red lily", "Flag of Saskatchewan.svg"),
    "YT": ("Mountain (all year)", "The Yukon River; Gwich'in for \"great river\"", ("Mount Logan", 5959), 482443,
           "Common raven", "Fireweed", "Flag of Yukon.svg"),
}
# extra names accepted when typing (accents are already ignored, so Québec matches Quebec)
NAMES = {"PE": ["PEI", "PE Island"], "NL": ["Newfoundland"], "NT": ["NWT", "Northwest Territory"], "YT": ["Yukon Territory", "The Yukon"]}
CAPITALS = {"QC": ["Quebec City", "Quebec"], "NL": ["St. John's", "St Johns", "Saint John's"]}
NE_NAME = {"QC": "Québec"}  # Natural Earth's spelling, where it differs
NE_CITY = {"QC": "Québec"}  # Natural Earth's name for the capital, where it differs


def fetch(url, path):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers=UA)
        path.write_bytes(urllib.request.urlopen(req, timeout=120).read())
    return json.loads(path.read_text(encoding="utf8"))


def rounded(geom, nd=3):
    """GeoJSON geometry with coordinates rounded (0.001 degrees is about 100 m)"""
    def r(c):
        return [round(c[0], nd), round(c[1], nd)] if isinstance(c[0], (int, float)) else [r(x) for x in c]
    g = mapping(geom)
    return {"type": g["type"], "coordinates": r(json.loads(json.dumps(g["coordinates"])))}


def lines_only(g):
    """the line parts of a shapely result (intersections of outlines can also give points)"""
    if g.is_empty:
        return []
    if g.geom_type == "LineString":
        return [g]
    if g.geom_type == "MultiLineString":
        return list(g.geoms)
    if hasattr(g, "geoms"):
        return [x for part in g.geoms for x in lines_only(part)]
    return []


def shapes():
    a1 = fetch(ADMIN1, DL / "ne_50m_admin1.geojson")["features"]
    a0 = fetch(ADMIN0, DL / "ne_50m_admin0.geojson")["features"]
    areas = {}
    for f in a1:
        p = f["properties"]
        if p.get("adm0_a3") == "CAN":
            areas[p["postal"]] = shape(f["geometry"]).buffer(0)
    # grey areas for context: the US (its states merged; Hawaii is far off, so it's left out) and Greenland
    us = [shape(f["geometry"]).buffer(0) for f in a1 if f["properties"].get("adm0_a3") == "USA" and f["properties"].get("postal") != "HI"]
    areas["T-USA"] = unary_union(us)
    for f in a0:
        if f["properties"].get("ADM0_A3") == "GRL":
            areas["T-GRL"] = shape(f["geometry"]).buffer(0)
    assert set(PROVINCES) <= set(areas), set(PROVINCES) - set(areas)
    # borders: outline shared by two areas; coastline: the rest of each outline
    keys = list(areas)
    borders = []
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if areas[a].bounds[0] > areas[b].bounds[2] or areas[b].bounds[0] > areas[a].bounds[2]:
                continue
            borders += lines_only(areas[a].boundary.intersection(areas[b].boundary))
    border_union = unary_union(borders)
    coast = lines_only(unary_union([g.boundary for g in areas.values()]).difference(border_union.buffer(1e-7)))
    merged = lambda ls: linemerge(ls) if ls else MultiLineString([])
    b, c = merged(borders), merged(coast)
    print(f"borders: {len(lines_only(b))} lines, coastline: {len(lines_only(c))} lines")
    features = [{"type": "Feature", "id": k, "geometry": rounded(g)} for k, g in areas.items()]
    return {"type": "FeatureCollection", "features": features, "borders": rounded(b), "coast": rounded(c)}


def flags():
    out = ROOT / "data" / "flags" / "ca"
    out.mkdir(parents=True, exist_ok=True)
    for code, f in FACTS.items():
        p = out / f"{code}.webp"
        if p.exists():
            continue
        url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(f[6].replace(" ", "_")) + "?width=640"
        for attempt in range(4):
            try:
                data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
                break
            except Exception as e:  # Commons rate-limits: wait and try again
                print("retrying", code, e)
                time.sleep(5 * (attempt + 1))
        else:
            raise SystemExit(f"could not download the flag of {code}")
        Image.open(io.BytesIO(data)).convert("RGB").save(p, "WEBP", quality=88)
        time.sleep(1.5)
    print("flags in", out)


def main():
    (ROOT / "data" / "ca-provinces.json").write_text(json.dumps(shapes(), separators=(",", ":")), encoding="utf8")
    items = []
    for code, (name, capital, city, kind, year, pop, region) in PROVINCES.items():
        tz, origin, high, area, bird, flower, _ = FACTS[code]
        items.append({
            "iso": code, "id": code, "name": name,
            "names": [name] + NAMES.get(code, []),
            "capitals": CAPITALS.get(code, [capital]),
            "cont": ["North America"], "car": False, "a2": code,
            "info": {"abbr": code, "kind": kind, "city": city, "year": year, "pop": pop, "popYear": "2021 census",
                     "region": region, "tz": tz, "origin": origin, "high": high, "area": area, "bird": bird, "flower": flower},
        })
    by_area = sorted(PROVINCES, key=lambda k: -FACTS[k][3])
    for it in items:
        it["info"]["areaRank"] = by_area.index(it["iso"]) + 1
    sys.path.insert(0, str(ROOT / "tools"))
    import capitals
    for it in items:  # Natural Earth's places list the province under its own spelling
        it["_ne"] = NE_NAME.get(it["iso"], it["name"])
    missing = []
    for it in items:
        ll = capitals.find(NE_CITY.get(it["iso"], it["capitals"][0]), a2="CA", adm1=it["_ne"])
        if ll:
            it["capLL"] = [ll]
        else:
            missing.append(it["name"])
        del it["_ne"]
    if missing:
        print("capitals not found:", missing)
    (ROOT / "data" / "provinces.json").write_text(json.dumps(sorted(items, key=lambda s: s["name"]), ensure_ascii=False, indent=0), encoding="utf8")
    print("wrote data/ca-provinces.json and data/provinces.json:", len(items), "provinces and territories")
    flags()


if __name__ == "__main__":
    main()
