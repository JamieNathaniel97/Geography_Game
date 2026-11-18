"""The detail level for country maps (PLAN.md, "High-resolution coasts"): the parts and their neighbours fitted to the
full-resolution GSHHG shoreline (tools/downloads/<code>/coast_f.geojson, from tools/fetch_country_data.py), simplified
to about 200 m, and cut into tiles so the app fetches only the ones on screen when zoomed in.

  index = build_detail(areas, "mx", window)     areas: {id: polygon} at Natural Earth level (parts "MX-…", grey "T-…")

Writes data/<code>-detail/<x>_<y>.json, each tile a FeatureCollection of its pieces of every area (ids as in the light
map) plus its "coast" and "borders" lines; returns the index the light map's file carries as "detail":
  {"dir": "data/<code>-detail/", "deg": tile size, "tol": simplify tolerance, "bounds": [w, s, e, n] (what the tiles
   cover: the app uses them only when the whole view is inside), "tiles": [[name, w, s, e, n], …]}
"""
import json
import math
import pathlib

import geopandas as gpd
import shapely
from shapely.geometry import box, mapping, MultiLineString
from shapely.ops import unary_union, linemerge

ROOT = pathlib.Path(__file__).resolve().parent.parent
DL = ROOT / "tools" / "downloads"


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


def rounded(geom, nd=4):
    def r(c):
        return [round(c[0], nd), round(c[1], nd)] if isinstance(c[0], (int, float)) else [r(x) for x in c]
    m = mapping(geom)
    return {"type": m["type"], "coordinates": r(json.loads(json.dumps(m["coordinates"])))}


def land(code, window):
    """GSHHG land in the window, with its lakes cut out."""
    g = gpd.read_file(DL / code / "coast_f.geojson")
    w = box(*window)
    lands = unary_union([polygonal(x) for x in g[g["level"] == "land"].geometry]).intersection(w)
    lakes = [polygonal(x) for x in g[g["level"] == "lake"].geometry]
    return polygonal(lands.difference(unary_union(lakes)) if lakes else lands)


def fit_to_land(areas, land_poly):
    """Each area cut to the coastline, and the land the outlines missed shared out by growing each area outwards a step
    at a time (as tools/build_uk.py does for counties); islands the light map left out join their nearest area."""
    out = {k: polygonal(v.intersection(land_poly)) for k, v in areas.items()}
    rest = polygonal(land_poly.difference(unary_union(list(out.values()))))
    keys = list(out)
    base = {k: out[k].simplify(0.002) for k in keys}
    grown = {k: [] for k in keys}
    for d in (0.01, 0.03, 0.08, 0.2, 0.5, 1.2):
        if rest.is_empty:
            break
        for k in keys:
            if base[k].is_empty:
                continue
            take = rest.intersection(base[k].buffer(d))
            if not take.is_empty and take.area > 0:
                grown[k].append(take)
                rest = polygonal(rest.difference(take))
    return {k: polygonal(unary_union([out[k]] + grown[k])) for k in keys}


def build_detail(areas, code, window, tol=0.002, deg=3, land_poly=None, name=None):
    """land_poly: the land to fit to, if not the downloaded shoreline in the window (Spain moves the Canaries into an
    inset); name: the output folder's code, if not `code` (Spain's two sets share one download)."""
    lp = land_poly if land_poly is not None else land(code, window)
    fitted = fit_to_land(areas, lp)
    keys = [k for k in fitted if not fitted[k].is_empty]
    geo = shapely.coverage_clean([fitted[k] for k in keys], gap_width=0.0005, snapping_distance=0.00005)
    geo = shapely.coverage_simplify([polygonal(g) for g in geo], tol)
    geo = {k: polygonal(shapely.set_precision(polygonal(g), 0.0002)) for k, g in zip(keys, geo)}
    borders = []
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            A, B = geo[a].bounds, geo[b].bounds
            if A[0] > B[2] or B[0] > A[2] or A[1] > B[3] or B[1] > A[3]:
                continue
            borders += lines_only(geo[a].boundary.intersection(geo[b].boundary))
    bu = unary_union(borders)
    coast = unary_union([g.boundary for g in geo.values()]).difference(bu.buffer(1e-7)).difference(box(*window).exterior.buffer(0.005))
    code = name or code
    out_dir = ROOT / "data" / f"{code}-detail"
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.json"):
        old.unlink()
    w, s, e, n = window
    tiles = []
    for ix in range(math.floor(w / deg), math.ceil(e / deg)):
        for iy in range(math.floor(s / deg), math.ceil(n / deg)):
            cell = box(ix * deg, iy * deg, (ix + 1) * deg, (iy + 1) * deg)
            feats = []
            for k, g in geo.items():
                if not g.intersects(cell):
                    continue
                piece = polygonal(g.intersection(cell))
                if not piece.is_empty:
                    feats.append({"type": "Feature", "id": k, "geometry": rounded(piece)})
            if not feats:
                continue
            def clip(lines):
                ls = lines_only(lines.intersection(cell)) if not lines.is_empty else []
                return rounded(linemerge(ls)) if ls else {"type": "MultiLineString", "coordinates": []}
            name = f"{ix}_{iy}"
            tile = {"type": "FeatureCollection", "features": feats, "coast": clip(coast), "borders": clip(bu)}
            (out_dir / f"{name}.json").write_text(json.dumps(tile, separators=(",", ":")), encoding="utf8")
            tiles.append([name, ix * deg, iy * deg, (ix + 1) * deg, (iy + 1) * deg])
    size = sum(p.stat().st_size for p in out_dir.glob("*.json"))
    print(f"  detail level: {len(tiles)} tiles, {size // 1024} KB in data/{code}-detail/")
    return {"dir": f"data/{code}-detail/", "deg": deg, "tol": tol, "bounds": list(window), "tiles": tiles}
