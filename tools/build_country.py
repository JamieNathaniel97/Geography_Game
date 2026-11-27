"""Builds a country map from one config module, tools/<code>_facts.py (jobs/overnight_v2.md: Austria, Czechia, Poland,
the Netherlands, Belgium). The same steps as tools/build_de.py, shared so each new country is just its facts file:

  data/<code>-states.json   the parts (Natural Earth 1:10m admin-1), the countries around as grey context ("T-…"),
                            lines "borders" and "coast", and "detail": the detail level's index
  data/<code>-detail/       the detail level (tools/detail.py): fitted to the GSHHG full-resolution shoreline, in tiles
  data/<code>-parts.json    names, capitals, populations (checked against the national total), areas, Learning facts
  data/flags/<code>/        the flags (Wikimedia Commons, tools/downloads/<code>/flags/), as WebP

A second set (Belgium's 3 regions) is dissolved from the parts: the module's SET2 gives its own code, id prefix,
groups and part table; it gets its own files (data/<set code>-states.json, -parts.json, -detail/).

The config module has:
  A3, A2            Natural Earth's adm0_a3 and the ISO alpha-2 code (for the capitals search)
  WINDOW            lon/lat box of the light map, wide enough for a tall phone screen (grey to the edges)
  DETAIL            where the high-resolution shoreline was downloaded (tools/fetch_country_data.py)
  POP_SOURCE, POP_YEAR, TOTAL   where the populations come from, and the national total they must add up to
                    (TOTAL_TOL: a published gap allowed, e.g. South Africa's census rounding)
  DROP              Natural Earth codes left off the map (the Caribbean Netherlands)
  PARTS             {code: dict(name, capital ("" = sits out the capitals games), capNote, capAlt, names, notTypo,
                     pop, area, kind)}
  FACTS             {code: dict(...)} the card facts (see the module's docstring)
  CAP_LL            {capital: [lon, lat]} for any the place list can't find
  LANDLOCKED        True: no part is coastal, whatever its lake shores
  FIT_LIGHT         True: the light map's parts are cut to the high-resolution land too (the Netherlands: Natural
                    Earth's provinces cover the IJsselmeer and the Markermeer, so Flevoland wasn't an island)
  MERGE             {new code: [Natural Earth codes]}: parts dissolved into one (Gwangju and South Jeolla, 2026)
  CLIP              lon/lat box (or a list of boxes) the parts are cut to (far islands left off)
  CONT              the continent (default "Europe")
  NE_FIX            {(Natural Earth ISO code, name): code} where Natural Earth reuses a code (Colombia: Bogotá is "CO-CUN")
  INSETS            [dict(codes, box, scale, to, frame, pad, part_box, tap, context)]: (part_box: only the part's piece inside
                    the box moves; tap=False: a plain drawn frame, no square tap area (several parts: Malaysia's East
                    Malaysia); context: the neighbours' land in the box moves too (Brunei, the Kalimantan coast); bar="top": its scale bar
                    in the frame's top left instead of the bottom left)
                    parts moved (and scaled) so their box's centre lands on `to`;
                    a framed inset's part gets a square tap area the shape of its frame (dashed and shaded like an island oval)
                    (Portugal's Azores and Madeira, framed; New Zealand's Chatham Islands, 360° east across the date line,
                    unframed). The shoreline for the detail level is moved the same way.
  ISLES             [(code, (lon, lat), radius°[, lat radius°])]: a tappable oval around far islands (as Brazil's), in map coordinates
  ENCLAVES          {code: dict(a3, name, capital, kind, fill, about)}: independent countries inside the map (South
                    Africa's Lesotho and Eswatini), drawn as shapes in their `fill` colour, in Learning mode only
  DETAIL_TOL        the detail level's simplify tolerance, if not 0.002° (Sweden: its archipelagos made 8 MB of tiles)
  DISPUTED          [dict(ne, join | grey, name, ring)]: Natural Earth disputed areas (ne = its NAME). join: added to that part
                    (governed by it), with its land edges dotted (Egypt's Hala'ib Triangle); ring: a dotted circle of that
                    radius instead, for a speck (South Korea's Dokdo); grey: its own grey, untappable area with that id,
                    dotted all round and labelled with `name` (Bir Tawil, claimed by neither Egypt nor Sudan)
  FLAG_FALLBACK     a folder in tools/downloads/<code>/ to take a part's image from when it has no flag (Egypt: coats/)
  EMBLEMS           games 5 and 6 use coats of arms (the module's FLAGS folder holds them)
  FLAGS             the flag folder in tools/downloads/<code>/, if not flags/ (Austria: flags_state/, the state flags
                    with arms, since Salzburg, Vienna and Vorarlberg share one red-white civil flag)

Run from the repo root:  python tools/build_country.py at   (or cz, pl, nl, be)
"""
import importlib
import json
import pathlib
import sys

import math

import geopandas as gpd
import shapely
from PIL import Image
from shapely import affinity
from shapely.geometry import mapping, MultiLineString, LineString, box
from shapely.ops import unary_union, linemerge

ROOT = pathlib.Path(__file__).resolve().parent.parent
NE = ROOT / "tools" / "downloads" / "ne10"
sys.path.insert(0, str(ROOT / "tools"))
from detail import build_detail, polygonal, lines_only, land, fit_to_land  # noqa: E402

SIMPLIFY = 0.002   # these countries are small: half Germany's tolerance


def rounded(geom, nd=3):
    def r(c):
        return [round(c[0], nd), round(c[1], nd)] if isinstance(c[0], (int, float)) else [r(x) for x in c]
    m = mapping(geom)
    return {"type": m["type"], "coordinates": r(json.loads(json.dumps(m["coordinates"])))}


def inset_tf(ins):
    """The move (and scale) of one inset: a function on geometries."""
    w, s_, e, n = ins["box"]
    cx, cy = (w + e) / 2, (s_ + n) / 2
    k = ins.get("scale", 1)
    return lambda g: affinity.translate(affinity.scale(g, k, k, origin=(cx, cy)), ins["to"][0] - cx, ins["to"][1] - cy)


def frames(cfg):
    out = []
    for ins in getattr(cfg, "INSETS", []):
        if ins.get("frame", True):
            g = inset_tf(ins)(box(*ins["box"]))
            out.append(g.buffer(ins.get("pad", 0.25), join_style=2))
    return out


def inset_scale_bars(cfg, parts=None, prefix=None):
    """A fixed scale bar for each framed inset (its own scale: the Azores are at half size), in map coordinates: two
    segments (km and miles) along the frame's bottom-left, each a round distance about a third of the frame's width."""
    out = []
    nice = lambda v: (lambda p: (5 if v / p >= 5 else 2 if v / p >= 2 else 1) * p)(10 ** math.floor(math.log10(v)))
    for ins in getattr(cfg, "INSETS", []):
        if not ins.get("frame", True):
            continue
        k = ins.get("scale", 1)
        w0, s0, e0, n0 = ins["box"]
        km_per_deg = 111.32 * math.cos(math.radians((s0 + n0) / 2))  # along the original latitude
        fw, fs, fe, fn = inset_tf(ins)(box(*ins["box"])).buffer(ins.get("pad", 0.25), join_style=2).bounds
        target = (fe - fw) * 0.34 / k * km_per_deg  # km for a third of the frame
        x0, step = fw + (fe - fw) * 0.06, (fn - fs) * 0.07
        if parts and not ins.get("part_box"):  # start no further left than the islands themselves (the frame's edge can run off the screen)
            x0 = max(x0, min(parts[f"{prefix}-{c}"].bounds[0] for c in ins["codes"] if f"{prefix}-{c}" in parts))
        for i, (unit, per_km) in enumerate((("km", 1), ("mi", 1 / 1.609344))):
            d = nice(target * per_km)
            length = d / per_km / km_per_deg * k
            y = (fn - (fn - fs) * 0.1 - i * step) if ins.get("bar") == "top" else (fs + (fn - fs) * 0.08 + (1 - i) * step)  # bar="top": above the land
            out.append({"from": [round(x0, 4), round(y, 4)], "to": [round(x0 + length, 4), round(y, 4)], "label": f"{d:g} {unit}"})
    return out


def land_poly(cfg, code):
    """The shoreline's land for the detail level, with the insets' land moved like their parts."""
    lp = land(code, cfg.DETAIL)
    extra = [inset_tf(ins)(land(code, ins["box"])) for ins in getattr(cfg, "INSETS", [])]
    return polygonal(unary_union([lp] + extra)) if extra else lp


def disputed_areas(cfg):
    if not getattr(cfg, "DISPUTED", None):
        return {}
    d = gpd.read_file(NE / "ne_10m_admin_0_disputed_areas.geojson")
    return {x["ne"]: polygonal(d[d["NAME"] == x["ne"]].geometry.iloc[0]) for x in cfg.DISPUTED}


def build_set(cfg, parts, dl_code, out_code, enclaves=None, prefix=None):
    """parts: {id: polygon}. Adds the grey neighbours, cleans and simplifies the coverage, finds the lines, builds the
    detail level. Returns the shapes file and, per part, coastal / borders / anchorLL."""
    a0 = gpd.read_file(NE / "ne_10m_admin_0_countries.geojson")
    enclaves = enclaves or {}
    areas = dict(parts, **enclaves)
    dsp = disputed_areas(cfg)
    grey_dsp = {}
    for x in getattr(cfg, "DISPUTED", []):
        if x.get("grey"):
            grey_dsp[x["grey"]] = dsp[x["ne"]]
    skip = {cfg.A3} | {e["a3"] for e in getattr(cfg, "ENCLAVES", {}).values()}
    country = unary_union(list(areas.values()) + list(grey_dsp.values()))
    fr = unary_union(frames(cfg)) if frames(cfg) else None
    names, win = {}, box(*cfg.WINDOW)
    ctx_boxes = [box(*i["box"]) for i in getattr(cfg, "INSETS", []) if i.get("context")]
    near = a0.intersects(win) if not ctx_boxes else (a0.intersects(win) | a0.intersects(unary_union(ctx_boxes)))
    for _, r in a0[near].iterrows():
        a3 = r["ADM0_A3"]
        if a3 in skip:
            continue
        g = polygonal(polygonal(r.geometry).intersection(win).difference(country))
        if fr is not None:
            g = polygonal(g.difference(fr))
        for ins in getattr(cfg, "INSETS", []):  # the neighbours' land inside a "context" inset moves with it
            if ins.get("context"):
                fi = inset_tf(ins)(box(*ins["box"])).buffer(ins.get("pad", 0.25), join_style=2)
                piece = polygonal(polygonal(r.geometry).intersection(box(*ins["box"])))
                if not piece.is_empty:
                    g = polygonal(unary_union([g, polygonal(inset_tf(ins)(piece).intersection(fi).difference(country))]))
        g = unary_union([p for p in getattr(g, "geoms", [g]) if p.area > 0.002])
        if not g.is_empty:
            areas["T-" + a3] = polygonal(g)
            names["T-" + a3] = r["NAME"]
    for x in getattr(cfg, "DISPUTED", []):  # grey disputed areas (Bir Tawil): their own untappable shape
        if x.get("grey"):
            areas[x["grey"]] = grey_dsp[x["grey"]]
            names[x["grey"]] = x["name"]
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
    disputed, labels = [], []
    if dsp:
        coast_b = unary_union(coast).buffer(0.01) if coast else None
        for x in cfg.DISPUTED:
            g = dsp[x["ne"]]
            if x.get("ring"):
                c = g.centroid
                disputed.append(LineString(c.buffer(x["ring"], quad_segs=12).exterior.coords))
            else:
                edge = g.boundary if coast_b is None else g.boundary.difference(coast_b)
                disputed += lines_only(shapely.simplify(edge, SIMPLIFY))
            if x.get("grey"):
                p = shapely.maximum_inscribed_circle(g, 0.01).coords[0]
                labels.append({"ll": [round(p[0], 3), round(p[1], 3)], "text": x["name"]})
        borders = lines_only(unary_union(borders).difference(unary_union(disputed).buffer(0.003)))
    # (the insets' frames aren't drawn as lines: each framed inset's part gets a square tap area the same shape, below)
    merged = lambda ls: linemerge(ls) if ls else MultiLineString([])
    detail = build_detail(areas, dl_code, cfg.DETAIL, name=out_code, land_poly=land_poly(cfg, dl_code), tol=getattr(cfg, "DETAIL_TOL", 0.002))
    out = {"type": "FeatureCollection",
           "features": [{"type": "Feature", "id": k, "geometry": rounded(g)} for k, g in geo.items() if not g.is_empty],
           "borders": rounded(merged(borders)), "coast": rounded(merged(coast)), "detail": detail}
    if disputed:
        out["disputed"] = rounded(merged(disputed))  # drawn dotted (js/mapview.js), even with Borders off
    if labels:
        out["labels"] = labels
    plain = [inset_tf(i)(box(*i["box"])).buffer(i.get("pad", 0.25), join_style=2) for i in getattr(cfg, "INSETS", [])
             if i.get("frame", True) and i.get("tap") is False]
    if plain:  # frames with no tap area, drawn straight by the app (as Spain's Canaries)
        out["frames"] = [[[round(x, 3), round(y, 3)] for x, y in f.exterior.coords] for f in plain]
    bars = inset_scale_bars(cfg, parts, prefix)
    if bars:
        out["scaleBars"] = bars  # the insets' own fixed scale bars
    # "coastal" means on the sea: the outer edge of all the land in the window (enclosed lakes such as the IJsselmeer,
    # Lake Geneva or Lake Constance are holes inside it, so their shores don't count), not the window's own edge
    land_all = unary_union(list(geo.values()))
    sea_edge = unary_union([LineString(p.exterior.coords) for p in getattr(land_all, "geoms", [land_all])]).difference(win.exterior.buffer(0.01))
    coast_u = sea_edge.buffer(1e-4) if not sea_edge.is_empty and not getattr(cfg, "LANDLOCKED", False) else None
    extra = {}
    for k, g in geo.items():
        if k in parts or k in enclaves:
            nb = sorted({names[j] for j, h in geo.items() if j.startswith("T-") and g.boundary.intersection(h.boundary).length > 0.01})
            extra[k] = {"coastal": bool(coast_u is not None and g.boundary.intersection(coast_u).length > 0.03), "borders": nb}
            main = max(getattr(g, "geoms", [g]), key=lambda p: p.area)
            # (also when the centre is near an edge or a hole: the app's spherical centre can fall just outside, e.g. Gyeonggi's in Seoul)
            if not main.contains(main.centroid) or main.boundary.distance(main.centroid) < 0.05:
                p = shapely.maximum_inscribed_circle(main, 0.01).coords[0]
                extra[k]["anchorLL"] = [round(p[0], 3), round(p[1], 3)]
    return out, extra


def flag(src, dst):
    im = Image.open(src).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    Image.alpha_composite(bg, im).convert("RGB").save(dst, "WEBP", quality=88)


def make_items(cfg, table, facts, prefix, flag_dir, flag_key, extra, cap_ll_cache, moved=None):
    import capitals
    out_flags = ROOT / "data" / "flags" / flag_key
    out_flags.mkdir(parents=True, exist_ok=True)
    items, missing = [], []
    for code, row in table.items():
        iso = f"{prefix}-{code}"
        src = flag_dir / f"{row.get('flagIso', cfg.A2 + '-' + code)}.png"
        if not src.exists() and getattr(cfg, "FLAG_FALLBACK", None):  # no flag: its emblem instead (Egypt's Cairo and Luxor)
            src = flag_dir.parent / cfg.FLAG_FALLBACK / src.name
        if src.exists():
            flag(src, out_flags / f"{iso}.webp")
        cap = row.get("capital", "")
        it = {"iso": iso, "id": iso, "name": row["name"], "names": list(dict.fromkeys([row["name"]] + row.get("names", []))),
              "capitals": ([cap] + row.get("capAlt", [])) if cap else [], "cont": [getattr(cfg, "CONT", "Europe")], "car": False, "a2": iso,
              "info": {"abbr": code, "kind": row.get("kind", ""), "pop": row["pop"], "popYear": cfg.POP_YEAR,
                       "area": round(row["area"]), "flag": src.exists(), "facts": facts.get(code, {}),
                       **({"capNote": row["capNote"]} if row.get("capNote") else {}),
                       **{k: v for k, v in extra.get(iso, {}).items() if k != "anchorLL"}},
              "flagKey": f"{flag_key}/{iso}"}
        if "anchorLL" in extra.get(iso, {}):
            it["anchorLL"] = extra[iso]["anchorLL"]
        if row.get("notTypo"):
            it["notTypo"] = row["notTypo"]
        lls = []
        for c in it["capitals"][:1] + row.get("capAlso", []):  # split capitals (Poland) get a dot each
            if c not in cap_ll_cache:
                cap_ll_cache[c] = cfg.CAP_LL.get(c) or capitals.find(c, a2=cfg.A2)
            if cap_ll_cache[c]:
                ll = cap_ll_cache[c]
                if moved and code in moved:  # a part in an inset: its capital moves with it
                    pt = moved[code](shapely.Point(ll))
                    ll = [round(pt.x, 3), round(pt.y, 3)]
                lls.append(ll)
            else:
                missing.append(c)
        it["capLL"] = lls
        isles = [{"center": list(c), "ring": [[round(c[0] + r[0] * math.cos(a), 3), round(c[1] + (r[1] if len(r) > 1 else r[0] * 0.75) * math.sin(a), 3)]
                                              for a in [i * math.pi / 12 for i in range(24)]]}
                 for k, c, *r in getattr(cfg, "ISLES", []) if k == code and table is cfg.PARTS]
        for ins in getattr(cfg, "INSETS", []):  # a framed inset: its tap area is the frame itself, drawn dashed and shaded
            if code in ins["codes"] and ins.get("frame", True) and ins.get("tap", True) and table is cfg.PARTS:
                fr = inset_tf(ins)(box(*ins["box"])).buffer(ins.get("pad", 0.25), join_style=2)
                w, s_, e, n = fr.bounds
                isles.append({"center": [round((w + e) / 2, 3), round((s_ + n) / 2, 3)], "square": True,
                              "ring": [[round(w, 3), round(s_, 3)], [round(e, 3), round(s_, 3)], [round(e, 3), round(n, 3)], [round(w, 3), round(n, 3)]]})
        if isles:
            it["isles"] = isles
        items.append(it)
    if missing:
        print("  capitals not found:", missing)
    by_area = sorted(items, key=lambda c: -c["info"]["area"])
    for it in items:
        it["info"]["areaRank"] = by_area.index(it) + 1
        it["info"]["of"] = len(items)
    return sorted(items, key=lambda s: s["name"])


def write(code, fc, items):
    (ROOT / "data" / f"{code}-states.json").write_text(json.dumps(fc, separators=(",", ":")), encoding="utf8")
    (ROOT / "data" / f"{code}-parts.json").write_text(json.dumps(items, ensure_ascii=False, indent=0), encoding="utf8")
    print(f"  wrote data/{code}-states.json and data/{code}-parts.json: {len(items)} parts;",
          sum(it["info"]["flag"] for it in items), "flags;", len(fc["detail"]["tiles"]) if fc.get("detail") else 0, "detail tiles")


def main(code):
    cfg = importlib.import_module(f"{code}_facts")
    dl = ROOT / "tools" / "downloads" / code
    prefix = cfg.A2
    a1 = gpd.read_file(NE / "ne_10m_admin_1_states_provinces.geojson")
    rows = a1[a1["adm0_a3"] == cfg.A3]
    parts = {}
    for _, r in rows.iterrows():
        c = getattr(cfg, "NE_FIX", {}).get((r["iso_3166_2"], r["name"])) or r["iso_3166_2"].split("-", 1)[1]
        if c in getattr(cfg, "DROP", ()) or r["iso_3166_2"].split("-", 1)[0] != prefix:
            continue
        parts[f"{prefix}-{c}"] = polygonal(r.geometry)
    if getattr(cfg, "CLIP", None):  # far islands left off (South Africa's Prince Edward Islands)
        boxes = cfg.CLIP if isinstance(cfg.CLIP[0], (list, tuple)) else [cfg.CLIP]  # one box, or several
        keep = unary_union([box(*b) for b in boxes])
        parts = {k: polygonal(v.intersection(keep)) for k, v in parts.items()}
    for x in getattr(cfg, "DISPUTED", []):  # governed by a part: joined to it (Hala'ib to the Red Sea, Dokdo to North Gyeongsang)
        if x.get("join"):
            k = f"{prefix}-{x['join']}"
            parts[k] = polygonal(unary_union([parts[k], disputed_areas(cfg)[x["ne"]]]))
    moved = {}
    for ins in getattr(cfg, "INSETS", []):
        for c in ins["codes"]:
            k = f"{prefix}-{c}"
            if ins.get("part_box"):  # only the part's islands inside the box move (Chile's Easter Island, Valparaíso's)
                b = box(*ins["box"])
                parts[k] = polygonal(unary_union([parts[k].difference(b), inset_tf(ins)(parts[k].intersection(b))]))
                continue
            moved[c] = inset_tf(ins)
            parts[k] = polygonal(moved[c](parts[k]))
    for new, members in getattr(cfg, "MERGE", {}).items():  # parts merged since Natural Earth's data (South Korea, July 2026)
        parts[f"{prefix}-{new}"] = polygonal(unary_union([parts.pop(f"{prefix}-{m}") for m in members]))
    assert set(parts) == {f"{prefix}-{c}" for c in cfg.PARTS}, sorted(set(parts) ^ {f"{prefix}-{c}" for c in cfg.PARTS})
    if getattr(cfg, "FIT_LIGHT", False):
        # the shoreline's land near the country, less the neighbours' land (so none of it is grown into the parts)
        a0 = gpd.read_file(NE / "ne_10m_admin_0_countries.geojson")
        here = unary_union(list(parts.values()))
        others = unary_union([polygonal(g) for g, a3 in zip(a0.geometry, a0["ADM0_A3"]) if a3 != cfg.A3 and g.intersects(here.buffer(0.1))])
        lp = polygonal(land(code, cfg.DETAIL).intersection(here.buffer(0.05)).difference(others))
        parts = fit_to_land(parts, lp)
    total = sum(p["pop"] for p in cfg.PARTS.values())
    print(f"  population {total:,} ({cfg.POP_SOURCE}: {cfg.TOTAL:,}) {'OK' if abs(total - cfg.TOTAL) <= getattr(cfg, "TOTAL_TOL", 0) else 'MISMATCH'}")
    cache = {}
    enc = {}
    if getattr(cfg, "ENCLAVES", None):
        a0 = gpd.read_file(NE / "ne_10m_admin_0_countries.geojson")
        for c, e in cfg.ENCLAVES.items():
            enc[f"{prefix}-{c}"] = polygonal(a0[a0["ADM0_A3"] == e["a3"]].geometry.iloc[0])
            for k in parts:  # Natural Earth's provinces can overlap the enclave's outline a little
                parts[k] = polygonal(parts[k].difference(enc[f"{prefix}-{c}"]))
    fc, extra = build_set(cfg, parts, code, code, enc, prefix)
    items = make_items(cfg, cfg.PARTS, cfg.FACTS, prefix, dl / getattr(cfg, "FLAGS", "flags"), code, extra, cache, moved)
    if enc:  # the enclaves: independent countries, in Learning mode only, filled in their colour
        world = {c["iso"]: c for c in json.loads((ROOT / "data" / "countries.json").read_text(encoding="utf8"))}
        for c, e in cfg.ENCLAVES.items():
            iso, w = f"{prefix}-{c}", world[e["a3"]]
            it = {"iso": iso, "id": iso, "name": e["name"], "names": [e["name"]] + e.get("names", []), "capitals": [e["capital"]],
                  "cont": [getattr(cfg, "CONT", "Europe")], "car": False, "a2": iso, "capLL": [],
                  "info": {"kind": e["kind"], "enclave": True, "fill": e["fill"], "pop": w["info"]["pop"], "popYear": "2025",
                           "area": round(w["info"].get("area") or e.get("area", 0)), "flag": True, "facts": {"about": e["about"]},
                           **{k: v for k, v in extra.get(iso, {}).items() if k != "anchorLL"}},
                  "flagKey": e["a3"]}
            if "anchorLL" in extra.get(iso, {}):
                it["anchorLL"] = extra[iso]["anchorLL"]
            items.append(it)
        items.sort(key=lambda s: s["name"])
    write(code, fc, items)
    s2 = getattr(cfg, "SET2", None)
    if s2:  # the second set, dissolved from the first
        p2 = {f"{s2['prefix']}-{g}": unary_union([parts[f"{prefix}-{m}"] for m in members]) for g, members in s2["groups"].items()}
        fc2, extra2 = build_set(cfg, p2, code, s2["code"])
        total2 = sum(p["pop"] for p in s2["parts"].values())
        print(f"  {s2['code']} population {total2:,} {'OK' if total2 == cfg.TOTAL else 'MISMATCH'}")
        write(s2["code"], fc2, make_items(cfg, s2["parts"], s2["facts"], s2["prefix"], dl / "flags", code, extra2, cache))


if __name__ == "__main__":
    main(sys.argv[1])
