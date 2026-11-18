"""Builds Japan's country map (Japan_plan.md, jobs/build_countries.md): the 47 prefectures, with the 9 regions as filters.

  data/jp-states.json   the 47 shapes (Natural Earth 1:10m admin-1), the countries around as grey context (the southern
                        Kurils stay in Russia's grey, as Natural Earth has them); lines "borders", "coast"; "detail"
  data/jp-detail/       the detail level (tools/detail.py): fitted to the GSHHG full-resolution shoreline, in tiles
  data/jp-parts.json    names (English, with or without the suffix), capitals, region, Learning facts (tools/jp_facts.py),
                        the prefectural flower, tree and bird (each prefecture's Wikipedia infobox); the 2020 census;
                        island ovals for the outlying islands
  data/flags/jp/        the 47 flags (Wikimedia Commons)

Okinawa and the far islands stay in place (no inset). Minamitorishima and Okinotorishima (Tokyo) are outside the map.
Run from the repo root:  python tools/build_jp.py
"""
import json
import math
import pathlib
import re
import sys

import geopandas as gpd
import shapely
from PIL import Image
from shapely.geometry import mapping, MultiLineString, box
from shapely.ops import unary_union, linemerge

ROOT = pathlib.Path(__file__).resolve().parent.parent
NE = ROOT / "tools" / "downloads" / "ne10"
JPDL = ROOT / "tools" / "downloads" / "jp"
sys.path.insert(0, str(ROOT / "tools"))
from detail import build_detail, polygonal, lines_only  # noqa: E402

SIMPLIFY = 0.006
WINDOW = (121.5, 23.5, 149, 46.2)       # Japan from Yonaguni to Hokkaido, the Ogasawara Islands at the edge
DETAIL = (122.0, 24.0, 146.5, 46.0)     # where the high-resolution shoreline was downloaded (less the far Pacific islands)
SUFFIX = {"01": "", "13": "to", "26": "fu", "27": "fu"}   # the rest are -ken
KIND = {"01": "Circuit (dō)", "13": "Metropolis (to)", "26": "Urban prefecture (fu)", "27": "Urban prefecture (fu)"}
CAP_ALT = {"Tokyo": ["Shinjuku"], "Kobe": ["Kōbe"]}
# island ovals: (prefecture, centre, radius in degrees of latitude)
ISLES = [("47", (127.85, 26.45), 0.42), ("47", (125.3, 24.78), 0.2), ("47", (124.0, 24.35), 0.4), ("47", (131.25, 25.85), 0.12),
         ("47", (126.75, 26.2), 0.16), ("13", (139.6, 33.9), 0.45), ("13", (142.18, 27.05), 0.25),
         ("46", (129.4, 28.25), 0.35), ("46", (128.85, 27.6), 0.25), ("46", (130.55, 30.45), 0.3), ("32", (133.2, 36.18), 0.2)]
# fixes for the infobox symbols (missing ones)
SYMBOL_FIX = {"13": {"flower": "Somei-yoshino cherry", "tree": "Ginkgo", "bird": "Black-headed gull"},
              "34": {"flower": "Japanese maple"}}
CAP_LL = {"Saitama": [139.646, 35.861], "Chiba": [140.106, 35.607], "Yamaguchi": [131.471, 34.186], "Saga": [130.299, 33.249]}


def macron_forms(name):
    """Hyōgo -> Hyōgo, Hyougo, Hyoogo (the app drops accents itself, so 'Hyogo' already counts)."""
    out = [name]
    if any(ch in name for ch in "ōūŌŪ"):
        for o, u in (("ou", "uu"), ("oo", "uu")):
            out.append(name.replace("ō", o).replace("ū", u).replace("Ō", o.capitalize()).replace("Ū", u.capitalize()))
    return out


def symbols():
    """The prefectural flower, tree and bird from each prefecture's English Wikipedia infobox."""
    def clean(v):
        v = re.sub(r"<ref[^>]*/>|<ref.*?</ref>", "", v)
        v = re.sub(r"\(''.*?''\)|\([^)]*\)", "", v)
        v = re.sub(r"''+", "", v)
        v = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", v)
        v = re.sub(r"<br\s*/?>", ", ", v).replace("&nbsp;", " ")
        return re.sub(r"\s+", " ", v).strip(" ,")
    rows = json.loads((JPDL / "states.json").read_text(encoding="utf8"))
    out = {}
    for row in rows:
        title = "Tokyo" if row["code"] == "13" else row["name"] + " Prefecture"
        p = JPDL / "wiki" / "en" / f"{title}.wiki"
        d = {}
        if p.exists():
            s = p.read_text(encoding="utf8")
            for k in ("flower", "tree", "bird"):
                m = re.search(r"^\s*\|\s*" + k + r"\s*=(.*)$", s, re.M)
                if m and clean(m.group(1)):
                    d[k] = clean(m.group(1))
        d.update(SYMBOL_FIX.get(row["code"], {}))
        out[row["code"]] = d
    return out


def rounded(geom, nd=3):
    def r(c):
        return [round(c[0], nd), round(c[1], nd)] if isinstance(c[0], (int, float)) else [r(x) for x in c]
    m = mapping(geom)
    return {"type": m["type"], "coordinates": r(json.loads(json.dumps(m["coordinates"])))}


def shapes():
    a1 = gpd.read_file(NE / "ne_10m_admin_1_states_provinces.geojson")
    a0 = gpd.read_file(NE / "ne_10m_admin_0_countries.geojson")
    areas = {"JP-" + r["iso_3166_2"][3:]: polygonal(r.geometry) for _, r in a1[a1["adm0_a3"] == "JPN"].iterrows()}
    assert len(areas) == 47, len(areas)
    names, win = {}, box(*WINDOW)
    areas = {k: polygonal(v.intersection(win)) for k, v in areas.items()}
    # Natural Earth puts the Amami islands (Amami Ōshima to Yoron) in Okinawa: they're Kagoshima's. Yoron (27.04°N, 128.4°E)
    # is north of Cape Hedo (26.87°N); Iheya and Izena (Okinawa's, 27.0°N) are west of 128.2°E.
    amami = [p for p in areas["JP-47"].geoms if p.centroid.y > 26.95 and p.centroid.x > 128.2]
    areas["JP-47"] = polygonal(unary_union([p for p in areas["JP-47"].geoms if p not in amami]))
    areas["JP-46"] = polygonal(unary_union([areas["JP-46"]] + amami))
    print(f"  moved {len(amami)} Amami island pieces from Okinawa to Kagoshima")
    japan = unary_union(list(areas.values()))
    for _, r in a0[a0.intersects(win)].iterrows():
        a3 = r["ADM0_A3"]
        if a3 == "JPN":
            continue
        g = polygonal(polygonal(r.geometry).intersection(win).difference(japan))
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
    detail = build_detail(areas, "jp", DETAIL)
    out = {"type": "FeatureCollection",
           "features": [{"type": "Feature", "id": k, "geometry": rounded(g)} for k, g in geo.items() if not g.is_empty],
           "borders": rounded(merged(borders)), "coast": rounded(merged(coast)), "detail": detail}
    coast_u = unary_union(coast).buffer(1e-4)
    extra = {}
    for k, g in geo.items():
        if k.startswith("JP-"):
            extra[k] = {"coastal": g.boundary.intersection(coast_u).length > 0.03}
            main = max(getattr(g, "geoms", [g]), key=lambda p: p.area)
            if not main.contains(main.centroid):
                p = shapely.maximum_inscribed_circle(main, 0.01).coords[0]
                extra[k]["anchorLL"] = [round(p[0], 3), round(p[1], 3)]
    return out, extra


def main():
    fc, extra = shapes()
    (ROOT / "data" / "jp-states.json").write_text(json.dumps(fc, separators=(",", ":")), encoding="utf8")
    import jp_facts
    import capitals
    syms = symbols()
    rows = json.loads((JPDL / "states.json").read_text(encoding="utf8"))
    out_flags = ROOT / "data" / "flags" / "jp"
    out_flags.mkdir(parents=True, exist_ok=True)
    items, missing = [], []
    for row in rows:
        code = row["code"]
        iso = "JP-" + code
        name = row["name"]
        src = JPDL / "flags" / f"{iso}.png"
        if src.exists():
            im = Image.open(src).convert("RGBA")  # (some are palette images with transparency: onto white)
            bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
            Image.alpha_composite(bg, im).convert("RGB").save(out_flags / f"{iso}.webp", "WEBP", quality=88)
        f = dict(jp_facts.FACTS.get(code, {}))
        s = syms.get(code, {})
        if s:
            f["symbols"] = " · ".join(f"{k.capitalize()}: {v}" for k, v in s.items())
        suf = SUFFIX.get(code, "ken")
        names = []
        for n in macron_forms(name):
            names += [n, f"{n} Prefecture"] + ([f"{n}-{suf}", f"{n} {suf}", f"{n}{suf}"] if suf else [])
        names += {"13": ["Tokyo Metropolis"], "01": ["Hokkaidō", "Hokkaidou"]}.get(code, [])
        caps = [x for x in macron_forms(row["capital"])] + CAP_ALT.get(row["capital"], [])
        it = {"iso": iso, "id": iso, "name": name, "names": list(dict.fromkeys(names)), "capitals": list(dict.fromkeys(caps)),
              "cont": ["Asia"], "car": False, "a2": iso,
              "info": {"abbr": code, "kind": KIND.get(code, "Prefecture (ken)"), "region": f.get("region", ""), "pop": row["pop"],
                       "popYear": "2020 census", "area": round(row["area"]), "flag": src.exists(), "facts": f,
                       **{k: v for k, v in extra.get(iso, {}).items() if k != "anchorLL"}},
              "flagKey": "jp/" + iso}
        if "anchorLL" in extra.get(iso, {}):
            it["anchorLL"] = extra[iso]["anchorLL"]
        isles = [{"center": list(c), "ring": [[round(c[0] + r * math.cos(a) / math.cos(math.radians(c[1])), 3), round(c[1] + r * math.sin(a), 3)]
                                              for a in [i * math.pi / 12 for i in range(24)]]} for p, c, r in ISLES if p == code]
        if isles:
            it["isles"] = isles
        ll = CAP_LL.get(row["capital"]) or capitals.find(row["capital"], a2="JP")
        if not ll:
            missing.append(row["capital"])
        it["capLL"] = [ll] if ll else []
        items.append(it)
    total = sum(it["info"]["pop"] for it in items)
    print(f"  population {total:,} (2020 census total: 126,146,099) {'OK' if total == 126146099 else 'MISMATCH'}")
    if missing:
        print("  capitals not found:", missing)
    by_area = sorted(items, key=lambda c: -c["info"]["area"])
    for it in items:
        it["info"]["areaRank"] = by_area.index(it) + 1
    (ROOT / "data" / "jp-parts.json").write_text(json.dumps(sorted(items, key=lambda s: s["name"]), ensure_ascii=False, indent=0), encoding="utf8")
    print("  wrote data/jp-states.json and data/jp-parts.json:", len(items), "parts;", sum(it["info"]["flag"] for it in items), "flags")


if __name__ == "__main__":
    main()
