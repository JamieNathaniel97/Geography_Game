"""Builds data/tribal-us.json and data/tribal-ca.json: Indigenous reserved lands for the "Reservations" layer in Learning mode.

  United States  federal American Indian reservations and Oklahoma tribal statistical areas
                 (US Census Bureau TIGERweb, public domain)
  Canada         Aboriginal Lands of Canada Legislative Boundaries: First Nations reserves and settlement lands
                 (Natural Resources Canada, Open Government Licence - Canada; attribution in the app)

Shapes come simplified from the services (about 1 km), with coordinates rounded to 0.001 degrees.
Run from the repo root:  python tools/build_tribal.py
"""
import json
import pathlib
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DL = ROOT / "tools" / "downloads" / "tribal"
US = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/AIANNHA/MapServer/{}/query"
CA = "https://proxyinternet.nrcan-rncan.gc.ca/arcgis/rest/services/CLSS-SATC/CLSS_Administrative_Boundaries/MapServer/0/query"
SIMPLIFY = 0.01  # degrees


def get(url, params, name):
    p = DL / name
    if not p.exists():
        DL.mkdir(parents=True, exist_ok=True)
        q = urllib.parse.urlencode({**params, "returnGeometry": "true", "outSR": 4326,
                                    "maxAllowableOffset": SIMPLIFY, "geometryPrecision": 3, "f": "geojson"})
        urllib.request.urlretrieve(url + "?" + q, p)
    return json.loads(p.read_text(encoding="utf8"))


TOL = 0.015     # degrees: Douglas-Peucker tolerance (the services' own simplifying leaves far too many points)
MIN_SIZE = 0.004  # degrees: rings smaller than this across are dropped (specks, even fully zoomed in)
MIN_PART = 0.02   # degrees: extra parts of one area smaller than this are dropped


def dp(pts):
    if len(pts) < 5:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        (ax, ay), (bx, by) = pts[a], pts[b]
        dx, dy = bx - ax, by - ay
        L = dx * dx + dy * dy
        best, bd = -1, TOL * TOL
        for i in range(a + 1, b):
            px, py = pts[i]
            u = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L)) if L else 0
            d = (ax + u * dx - px) ** 2 + (ay + u * dy - py) ** 2
            if d > bd:
                best, bd = i, d
        if best > 0:
            keep[best] = True
            stack += [(a, best), (best, b)]
    out = [p for p, k in zip(pts, keep) if k]
    if len(out) < 4:  # keep small areas as a simple shape rather than losing them
        out = [pts[0], pts[len(pts) // 3], pts[2 * len(pts) // 3], pts[0]]
    pts2 = []
    for x, y in out:  # 0.01 degrees (about 1 km) is plenty at these sizes
        q = [round(x, 2), round(y, 2)]
        if not pts2 or q != pts2[-1]:
            pts2.append(q)
    return pts2


def orient(rings):
    """d3 wants outer rings clockwise and holes anticlockwise (the services give the opposite); else an area
    reads as the whole world except that area"""
    out = []
    for i, r in enumerate(rings):
        a = sum((x2 - x1) * (y2 + y1) for (x1, y1), (x2, y2) in zip(r, r[1:]))  # > 0: clockwise (x east, y north)
        if (i == 0) != (a > 0):
            r = r[::-1]
        out.append(r)
    return out


def ring_ok(r):
    xs, ys = [p[0] for p in r], [p[1] for p in r]
    return len(r) >= 4 and max(max(xs) - min(xs), max(ys) - min(ys)) >= MIN_SIZE


DOT = 0.03       # degrees: areas smaller than this across (about 3 km) are kept as a dot: smaller file, easier to see


def clean(geom):
    """simplify, and drop rings that are too small to see; very small areas become a dot"""
    if not geom:
        return None
    outer = [geom["coordinates"][0]] if geom["type"] == "Polygon" else [p[0] for p in geom["coordinates"] if p]
    xs = [x for r in outer for x, _ in r]
    ys = [y for r in outer for _, y in r]
    if xs and max(max(xs) - min(xs), max(ys) - min(ys)) < DOT:
        return {"type": "Point", "coordinates": [round((max(xs) + min(xs)) / 2, 3), round((max(ys) + min(ys)) / 2, 3)]}
    if geom["type"] == "Polygon":
        geom = {"type": "Polygon", "coordinates": [dp(r) for r in geom["coordinates"] if ring_ok(r)]}
    elif geom["type"] == "MultiPolygon":
        # the biggest part always stays; extra parts (often thousands of tiny Arctic islands) only if 2 km+ across
        size = lambda p: max(max(x for x, _ in p[0]) - min(x for x, _ in p[0]), max(y for _, y in p[0]) - min(y for _, y in p[0]))
        polys = sorted([p for p in geom["coordinates"] if p and len(p[0]) >= 4], key=size, reverse=True)
        polys = polys[:1] + [p for p in polys[1:] if size(p) >= MIN_PART]
        geom = {"type": "MultiPolygon", "coordinates": [[dp(r) for r in p if ring_ok(r)] for p in polys]}
    if geom["type"] == "Polygon":
        rings = orient([r for r in geom["coordinates"] if len(r) >= 4])
        return {"type": "Polygon", "coordinates": rings} if rings else None
    if geom["type"] == "MultiPolygon":
        polys = [orient([r for r in p if len(r) >= 4]) for p in geom["coordinates"]]
        polys = [p for p in polys if p]
        return {"type": "MultiPolygon", "coordinates": polys} if polys else None
    return geom


def nice(name):
    """Canada's names come in capitals: "KAHNAWAKE 14" -> "Kahnawake 14" """
    if name and name.isupper():
        name = name.title().replace("'S ", "'s ").replace(" Of ", " of ").replace(" And ", " and ").replace(" No. ", " No. ")
    return name


def main():
    out = []
    # US: federal reservations (layer 2) and Oklahoma tribal statistical areas (layer 7)
    for layer, kind in ((2, "Reservation"), (7, "Oklahoma tribal area")):
        g = get(US.format(layer), {"where": "1=1", "outFields": "NAME"}, f"us_layer{layer}.json")
        for f in g["features"]:
            geom = clean(f["geometry"])
            if geom:
                out.append({"type": "Feature", "geometry": geom,
                            "properties": {"n": f["properties"]["NAME"], "c": "US", "k": kind}})
    # Canada: 500 records per request
    offset = 0
    while True:
        g = get(CA, {"where": "1=1", "outFields": "adminAreaNameEng", "resultOffset": offset, "resultRecordCount": 500,
                     "orderByFields": "OBJECTID"}, f"ca_{offset}.json")
        feats = g.get("features", [])
        for f in feats:
            geom = clean(f["geometry"])
            if geom:
                out.append({"type": "Feature", "geometry": geom,
                            "properties": {"n": nice(f["properties"]["adminAreaNameEng"]), "c": "CA", "k": "Reserve"}})
        if len(feats) < 500:
            break
        offset += 500
    # one file per country: the US Learning map loads only its own (Canada's is kept for a future Canada map)
    for c, name in (("US", "tribal-us.json"), ("CA", "tribal-ca.json")):
        fs = [f for f in out if f["properties"]["c"] == c]
        (ROOT / "data" / name).write_text(
            json.dumps({"type": "FeatureCollection", "features": fs}, separators=(",", ":"), ensure_ascii=False), encoding="utf8")
        print(f"wrote data/{name}: {len(fs)} areas")


if __name__ == "__main__":
    main()
