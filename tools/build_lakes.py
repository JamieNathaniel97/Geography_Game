"""Builds data/lakes.json: the world's larger lakes (Natural Earth 1:50m lakes, public domain), drawn in the sea
colour on the world map. Without them the Great Lakes showed as land, and the US state borders (which stop at the
real shorelines) looked broken there.

Run from the repo root:  python tools/build_lakes.py
"""
import json
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DL = ROOT / "tools" / "downloads"
SOURCE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_lakes.geojson"
MIN_AREA = 1000  # km²: smaller lakes would just add clutter (Lake St Clair, between Michigan and Ontario, is about 1,100 km²)


def rnd(c):
    """coordinates rounded to 0.01° (about 1 km, plenty for the 1:50m world map), repeated points dropped"""
    if isinstance(c[0][0], (int, float)):  # a ring
        out = []
        for x, y in c:
            p = [round(x, 2), round(y, 2)]
            if not out or p != out[-1]:
                out.append(p)
        return out
    return [rnd(x) for x in c]


def area_km2(geom):
    import math
    polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
    tot = 0
    for poly in polys:
        for k, ring in enumerate(poly):
            a = 0
            for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
                a += (x2 - x1) * (y1 + y2) / 2 * math.cos(math.radians((y1 + y2) / 2))
            tot += abs(a) * (1 if k == 0 else -1)
    return tot * 111.32 ** 2


def main():
    DL.mkdir(parents=True, exist_ok=True)
    src = DL / "ne_50m_lakes.geojson"
    if not src.exists():
        urllib.request.urlretrieve(SOURCE, src)
    g = json.loads(src.read_text(encoding="utf8"))
    out = []
    for f in g["features"]:
        p = f["properties"]
        if area_km2(f["geometry"]) < MIN_AREA:
            continue
        out.append({"type": "Feature", "properties": {"name": p.get("name")},
                    "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    (ROOT / "data" / "lakes.json").write_text(json.dumps({"type": "FeatureCollection", "features": out}, separators=(",", ":"), ensure_ascii=False), encoding="utf8")
    print("wrote data/lakes.json:", len(out), "lakes")


if __name__ == "__main__":
    main()
