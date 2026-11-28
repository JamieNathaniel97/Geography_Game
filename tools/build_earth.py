"""Builds Earth mode's stage 1 data (jobs/geoscience.md) into data/earth/, from tools/downloads/earth/
(python tools/fetch_earth.py) and the hand-picked facts in tools/earth_facts.py:

  plates.json        the 52 PB2002 plates (merged where split at the date line): code, name, kind, area, neighbours,
                     a colour index (neighbours differ), a label point, motion and note
  boundaries.json    every plate boundary as lines, typed divergent / convergent / transform, with the speed (mm a
                     year), length, depth and seafloor age measured from PB2002's 5,824 steps
  features.json      the named ridges, trenches, faults, rifts and collision zones (earth_facts.FEATURES), as lines
                     picked out of the steps, with their measured length and speed
  ring.json          the Ring of Fire: the subduction zones round the Pacific
  volcanoes.json     the 1,209 Holocene volcanoes (Smithsonian GVP): compact rows, a priority for thinning at world zoom
  vnotes/<n>.json    the GVP's geological summary of each, one file per GVP region (loaded when a card opens)
  seas.json          Natural Earth's oceans, seas, gulfs and bays: name, kind, area, which ocean, label point
  hotspots.json      the hotspots and their island chains (earth_facts.HOTSPOTS)

Geometry is in d3's winding (outer rings clockwise), coordinates rounded to 0.001° (about 100 m).
  python tools/build_earth.py
"""
import json
import math
import pathlib
import re
import sys

from pyproj import Geod
from shapely.geometry import shape, mapping, Polygon, MultiPolygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union, polylabel

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import earth_facts as F

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "downloads" / "earth"
OUT = ROOT / "data" / "earth"
GEOD = Geod(ellps="WGS84")
TYPE = {"OSR": "divergent", "CRB": "divergent", "SUB": "convergent", "OCB": "convergent", "CCB": "convergent",
        "OTF": "transform", "CTF": "transform"}
CLASS_NAME = {"OSR": "Oceanic spreading ridge", "CRB": "Continental rift", "SUB": "Subduction zone",
              "OCB": "Oceanic convergent boundary", "CCB": "Continental collision", "OTF": "Oceanic transform fault",
              "CTF": "Continental transform fault"}


def load(name):
    return json.loads((SRC / name).read_text(encoding="utf8"))


def rnd(o):
    if isinstance(o, float):
        return round(o, 3)
    if isinstance(o, (list, tuple)):
        return [rnd(x) for x in o]
    if isinstance(o, dict):
        return {k: rnd(v) for k, v in o.items()}
    return o


def d3_geom(g):
    """Polygon or MultiPolygon with outer rings clockwise (d3's spherical convention)."""
    polys = [g] if isinstance(g, Polygon) else list(g.geoms)
    polys = [orient(p, sign=-1.0) for p in polys if not p.is_empty]
    return mapping(polys[0] if len(polys) == 1 else MultiPolygon(polys))


def area_km2(g):
    return abs(GEOD.geometry_area_perimeter(g)[0]) / 1e6


def label_point(g):
    polys = [g] if isinstance(g, Polygon) else list(g.geoms)
    big = max(polys, key=lambda p: p.area)
    p = polylabel(big, tolerance=0.1)
    return [round(p.x, 2), round(p.y, 2)]


def codes(bound):
    return re.findall(r"[A-Z]{2}", bound)


def pair_key(a, b):
    return "-".join(sorted([a, b]))


def in_box(lon, lat, box):
    if not box:
        return True
    w, s, e, n = box
    if not (s <= lat <= n):
        return False
    return (w <= lon <= e) if w <= e else (lon >= w or lon <= e)


def merge(steps, key):
    """Steps (PB2002 order) into polylines: a new line starts where the next step doesn't continue the last one, or
    where `key` changes. Returns [(key, [steps], [[lon, lat]...])]."""
    lines = []
    for s in steps:
        p = s["properties"]
        k = key(s)
        a, b = [p["STARTLONG"], p["STARTLAT"]], [p["FINALLONG"], p["FINALLAT"]]
        if lines and lines[-1][0] == k and abs(lines[-1][2][-1][0] - a[0]) < 0.02 and abs(lines[-1][2][-1][1] - a[1]) < 0.02:
            lines[-1][1].append(s); lines[-1][2].append(b)
        else:
            lines.append((k, [s], [a, b]))
    return lines


def split_dateline(pts):
    """A polyline cut where it jumps across the date line (PB2002 keeps longitudes in -180..180)."""
    out, cur = [], [pts[0]]
    for p in pts[1:]:
        if abs(p[0] - cur[-1][0]) > 180:
            # the crossing point, on the 180° line
            q = cur[-1]; p2 = [p[0] + (360 if p[0] < q[0] else -360), p[1]]
            t = ((180 if p2[0] > q[0] else -180) - q[0]) / (p2[0] - q[0])
            lat = q[1] + t * (p2[1] - q[1]); edge = 180 if p2[0] > q[0] else -180
            cur.append([edge, lat]); out.append(cur); cur = [[-edge, lat], p]
        else:
            cur.append(p)
    out.append(cur)
    return [c for c in out if len(c) > 1]


def measure(steps):
    L = sum(s["properties"]["STEPLENGTH"] for s in steps) or 1
    w = lambda k: sum(s["properties"][k] * s["properties"]["STEPLENGTH"] for s in steps) / L
    ages = [s for s in steps if 0 < (s["properties"].get("SEAFLOORAG") or 0) < 250]  # (PB2002: 260 = no ocean floor, on land)
    La = sum(s["properties"]["STEPLENGTH"] for s in ages)
    return dict(len=round(L), rate=round(w("VELOCITYLE"), 1), rateMax=round(max(s["properties"]["VELOCITYLE"] for s in steps), 1),
                depth=round(w("ELEVATION")), age=round(sum(s["properties"]["SEAFLOORAG"] * s["properties"]["STEPLENGTH"] for s in ages) / La, 1) if La else None)


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    names = {}
    # ----- plates
    raw = load("pb2002_plates.json")["features"]
    by = {}
    for f in raw:
        p = f["properties"]; names[p["Code"]] = p["PlateName"]
        by.setdefault(p["Code"], []).append(shape(f["geometry"]))
    bounds = load("pb2002_boundaries.json")["features"]
    neigh = {c: set() for c in by}
    for b in bounds:
        a, c = b["properties"]["PlateA"], b["properties"]["PlateB"]
        if a in neigh and c in neigh and a != c:
            neigh[a].add(c); neigh[c].add(a)
    # colours: greedy, biggest plates first, so neighbours never share one of the 6 soft colours
    areas = {c: sum(area_km2(g) for g in gs) for c, gs in by.items()}
    colour = {}
    for c in sorted(by, key=lambda c: -areas[c]):
        used = {colour[n] for n in neigh[c] if n in colour}
        colour[c] = next(i for i in range(12) if i not in used)
    plates = []
    for c, gs in sorted(by.items()):
        g = unary_union(gs) if len(gs) > 1 else gs[0]
        g = g.simplify(0.01, preserve_topology=True)
        meta = F.PLATES.get(c, {})
        kind = meta.get("kind") or ("Minor plate" if areas[c] >= 1e6 else "Microplate")
        plates.append({"type": "Feature", "geometry": d3_geom(g), "properties": dict(
            code=c, name=names[c] + " plate", kind=kind, area=round(areas[c], -3), colour=colour[c] % 6,
            neighbours=sorted(neigh[c], key=lambda n: -areas.get(n, 0)), label=label_point(g),
            motion=meta.get("motion"), note=meta.get("note"), alias=meta.get("alias"))})
    write("plates.json", {"type": "FeatureCollection", "features": plates})

    # ----- boundaries (all of them, typed) from the steps
    steps = load("pb2002_steps.json")["features"]
    for s in steps:
        p = s["properties"]; cs = codes(p["PLATEBOUND"])
        s["pair"] = pair_key(cs[0], cs[1]); s["plates"] = cs[:2]; s["type"] = TYPE[p["STEPCLASS"]]
        s["mid"] = [(p["STARTLONG"] + p["FINALLONG"]) / 2 if abs(p["STARTLONG"] - p["FINALLONG"]) < 180 else p["STARTLONG"], (p["STARTLAT"] + p["FINALLAT"]) / 2]
    bfeats = []
    for (pair, typ), ss, pts in merge(steps, lambda s: (s["pair"], s["type"])):
        cls = max({s["properties"]["STEPCLASS"] for s in ss}, key=lambda k: sum(x["properties"]["STEPLENGTH"] for x in ss if x["properties"]["STEPCLASS"] == k))
        m = measure(ss)
        for part in split_dateline(pts):
            bfeats.append({"type": "Feature", "geometry": {"type": "LineString", "coordinates": part},
                           "properties": dict(plates=ss[0]["plates"], type=typ, cls=cls, **m)})
    write("boundaries.json", {"type": "FeatureCollection", "classes": CLASS_NAME, "features": bfeats})

    # ----- named features
    taken = {}
    for s in steps:
        for fd in F.FEATURES:
            if s["properties"]["STEPCLASS"] in fd["classes"] and s["pair"] in {pair_key(*x.split("-")) for x in fd["pairs"]} and in_box(*s["mid"], fd.get("box")):
                taken.setdefault(fd["id"], []).append(s); break
    ffeats, missing = [], []
    for fd in F.FEATURES:
        ss = taken.get(fd["id"])
        if not ss:
            missing.append(fd["name"]); continue
        lines = []
        for _, _, pts in merge(ss, lambda s: 0):
            lines += split_dateline(pts)
        m = measure(ss)
        pl = sorted({c for s in ss for c in s["plates"]}, key=lambda c: -areas.get(c, 0))
        ffeats.append({"type": "Feature", "geometry": {"type": "MultiLineString", "coordinates": lines},
                       "properties": dict(id=fd["id"], name=fd["name"], kind=fd["kind"], plates=pl, note=fd.get("note"),
                                          facts=fd.get("facts", []), depthMax=fd.get("depth"), **m)})
    write("features.json", {"type": "FeatureCollection", "features": ffeats})
    print("features:", len(ffeats), "of", len(F.FEATURES), "; not found:", missing)

    # ----- the Ring of Fire: subduction round the Pacific (not the Caribbean, the Scotia Sea or the Mediterranean)
    PAC = {"PA", "PS", "MA", "TO", "KE", "NZ", "CO", "JF", "RI", "NH", "SB", "SS", "CL", "MN", "NB", "WL", "BR", "CR", "FT", "NI",
           "AN", "SU", "TI", "BS", "MS", "BH", "ON", "OK", "AM"}
    # (the Caribbean's, the Mediterranean's and Makran's trenches touch no Pacific plate; the Scotia Sea's are left out by name)
    rsteps = [s for s in steps if s["properties"]["STEPCLASS"] == "SUB" and set(s["plates"]) & PAC and not set(s["plates"]) & {"SC", "SW", "SL"}]
    rlines = []
    for _, _, pts in merge(rsteps, lambda s: s["pair"]):
        rlines += split_dateline(pts)
    write("ring.json", {"type": "Feature", "geometry": {"type": "MultiLineString", "coordinates": rlines},
                        "properties": dict(F.RING, len=round(sum(s["properties"]["STEPLENGTH"] for s in rsteps)))})
    print("ring of fire:", len(rsteps), "steps,", round(sum(s["properties"]["STEPLENGTH"] for s in rsteps)), "km")

    # ----- volcanoes
    gv = load("gvp_holocene.json")["features"]
    types, countries, settings, rocks, notes, rows = [], [], [], [], {}, []
    idx = lambda lst, v: (lst.index(v) if v in lst else (lst.append(v) or len(lst) - 1))
    famous = {k: v for k, v in F.VOLCANOES.items() if v}
    found = set()
    for f in gv:
        p = f["properties"]
        name = p["Volcano_Name"]; fam = famous.get(name)
        if fam: found.add(name)
        last = p.get("Last_Eruption_Year")
        pri = 0 if fam else 1 if (last is not None and last >= 1900) else 2 if (last is not None and last >= 1500) else 3
        t = re.sub(r"\(.*?\)|\?", "", p.get("Primary_Volcano_Type") or "Unknown").strip()
        rows.append([p["Volcano_Number"], name, round(p["Longitude"], 3), round(p["Latitude"], 3), p.get("Elevation"),
                     idx(types, t), last, idx(countries, p.get("Country") or ""), pri, idx(settings, p.get("Tectonic_Setting") or ""),
                     idx(rocks, p.get("Major_Rock_Type") or ""), fam or ""])
        if p.get("Geological_Summary"):
            notes[p["Volcano_Number"]] = p["Geological_Summary"]
    rows.sort(key=lambda r: (r[8], -(r[4] or 0)))
    write("volcanoes.json", {"cols": ["num", "name", "lon", "lat", "elev", "type", "last", "country", "pri", "setting", "rock", "famous"],
                             "types": types, "countries": countries, "settings": settings, "rocks": rocks, "rows": rows,
                             "credit": "Global Volcanism Program, Smithsonian Institution: Volcanoes of the World"})
    # the GVP's summaries, one small file per GVP region (the first two digits of the volcano number), loaded when a card opens
    (OUT / "vnotes").mkdir(exist_ok=True)
    for old in (OUT / "vnotes").glob("*.json"):
        old.unlink()
    chunks = {}
    for num, text in notes.items():
        chunks.setdefault(num // 10000, {})[num] = text
    for k, ch in chunks.items():
        (OUT / "vnotes" / f"{k}.json").write_text(json.dumps(ch, ensure_ascii=False, separators=(",", ":")), encoding="utf8")
    print(f"   vnotes/: {len(chunks)} files, the biggest {max(len(json.dumps(c)) for c in chunks.values()) // 1024} KB")
    print("volcanoes:", len(rows), "; famous not matched:", sorted(set(famous) - found))

    # ----- seas
    mp = load("ne_10m_geography_marine_polys.geojson")["features"]
    keep = [f for f in mp if f["properties"]["featurecla"] in ("ocean", "sea") or
            (f["properties"]["featurecla"] in ("gulf", "bay") and f["properties"]["scalerank"] <= 5)]
    oceans = [(f["properties"]["name"], shape(f["geometry"])) for f in mp if f["properties"]["featurecla"] == "ocean"]
    sfeats = []
    for f in keep:
        p = f["properties"]; g = shape(f["geometry"]).buffer(0)
        name = p["name"].title() if p["name"].isupper() else p["name"]
        kind = p["featurecla"]
        ocean = None
        if kind != "ocean" and name not in ("Caspian Sea",):
            ocean = min(oceans, key=lambda o: o[1].distance(g))[0]
            ocean = ocean.title() if ocean.isupper() else ocean
        gs = g.simplify(0.02, preserve_topology=True)
        if gs.is_empty:
            continue
        o = F.OCEANS.get(name, {})
        sfeats.append({"type": "Feature", "geometry": d3_geom(gs), "properties": dict(
            name=name, kind=kind.title() if kind != "ocean" else "Ocean", area=round(area_km2(g), -2), ocean=ocean,
            label=label_point(gs), rank=p["scalerank"], deepest=o.get("deepest"), lake=name == "Caspian Sea")})
    sfeats.sort(key=lambda f: f["properties"]["rank"])
    write("seas.json", {"type": "FeatureCollection", "features": sfeats})
    print("seas:", len(sfeats))

    # ----- hotspots
    write("hotspots.json", F.HOTSPOTS)


def write(name, obj):
    f = OUT / name
    f.write_text(json.dumps(rnd(obj), ensure_ascii=False, separators=(",", ":")), encoding="utf8")
    print(f"   {name}: {f.stat().st_size // 1024} KB")


if __name__ == "__main__":
    build()
