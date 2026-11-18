"""Builds Nigeria's country map (Nigeria_plan.md, jobs/build_countries.md): the 36 states and the Federal Capital Territory.

  data/ng-states.json   the 37 shapes (Natural Earth 1:10m admin-1), the countries around as grey context; lines
                        "borders", "coast"; "detail": the detail level's index
  data/ng-detail/       the detail level (tools/detail.py): fitted to the GSHHG full-resolution shoreline, in tiles
  data/ng-parts.json    names, capitals, zone, nickname, Learning facts (tools/ng_facts.py); populations: the National
                        Bureau of Statistics' 2019 estimates (the downloaded "States of Nigeria" table)

No flags (games 5 and 6 shelved). Run from the repo root:  python tools/build_ng.py
"""
import json
import pathlib
import re
import sys

import geopandas as gpd
import shapely
from shapely.geometry import mapping, MultiLineString, box
from shapely.ops import unary_union, linemerge

ROOT = pathlib.Path(__file__).resolve().parent.parent
NE = ROOT / "tools" / "downloads" / "ne10"
NGDL = ROOT / "tools" / "downloads" / "ng"
sys.path.insert(0, str(ROOT / "tools"))
from detail import build_detail, polygonal, lines_only  # noqa: E402

SIMPLIFY = 0.006
WINDOW = (0.5, 2.5, 16.5, 15.5)         # Nigeria and its neighbours, with room for a tall phone screen
DETAIL = (2.6, 3.0, 14.7, 13.9)         # where the high-resolution shoreline was downloaded (and the sea south of the delta)
CAP_ALT = {"Ikeja": ["Lagos"], "Benin City": ["Benin"], "Port Harcourt": ["PH"], "Abuja": [], "Ado Ekiti": ["Ado-Ekiti"]}
ALT = {"FC": ["FCT", "Abuja", "Federal Capital Territory", "Abuja FCT"], "NA": ["Nassarawa"], "AK": ["Akwa-Ibom"]}
CAP_LL = {"Yenagoa": [6.264, 4.925], "Abakaliki": [8.113, 6.325], "Ikeja": [3.348, 6.601], "Osogbo": [4.556, 7.771]}  # (no match in the place list)


def rounded(geom, nd=3):
    def r(c):
        return [round(c[0], nd), round(c[1], nd)] if isinstance(c[0], (int, float)) else [r(x) for x in c]
    m = mapping(geom)
    return {"type": m["type"], "coordinates": r(json.loads(json.dumps(m["coordinates"])))}


def table():
    """The "States of Nigeria" table: code, name, capital, largest city, zone, area, 2019 population."""
    s = (NGDL / "wiki" / "lists" / "States of Nigeria.wiki").read_text(encoding="utf8")
    s = s[:s.index("|}", s.index('!scope="row"'))]
    link = lambda c: (re.search(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", c) or [None, c.strip()])[1]
    out = {}
    for r in re.split(r'\n!scope="row"\|', s)[1:]:
        lines = r.split("\n")
        name = link(lines[0])
        cells = [x[1:] for x in lines[1:] if x.startswith("|") and not x.startswith("|-") and not x.startswith("|}")]
        code = cells[0].strip()
        i = 3
        if cells[i].startswith("colspan=2"):   # the capital is also the largest city
            cap = largest = link(cells[i]); i += 1
        else:
            cap, largest = link(cells[i]), link(cells[i + 1]); i += 2
        zone = link(cells[i])
        area = int(re.search(r"convert\|([\d,]+)", cells[i + 1]).group(1).replace(",", ""))
        pop = int(cells[i + 2].replace(",", ""))
        out[code] = dict(name=name, capital=cap, largest=largest, zone=zone, area=area, pop=pop)
    return out


def nicknames():
    s = (NGDL / "wiki" / "lists" / "List of Nigerian state nicknames.wiki").read_text(encoding="utf8")
    out = {}
    for m in re.finditer(r"\|\s*align=\"left\"\s*\|\s*\[\[([^\]|]+)(?:\|[^\]]*)?\]\]\s*\n\|\s*align=\"center\"\s*\|\s*(.+)", s):
        out[m.group(1).replace(" State", "").strip()] = re.sub(r"<ref.*", "", m.group(2)).strip()
    return out


def near(a, b):
    """Edit distance of at most 2 (short names the typo rule could mix up)."""
    a, b = a.lower(), b.lower()
    if abs(len(a) - len(b)) > 2:
        return False
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1] <= 2


def shapes():
    a1 = gpd.read_file(NE / "ne_10m_admin_1_states_provinces.geojson")
    a0 = gpd.read_file(NE / "ne_10m_admin_0_countries.geojson")
    areas = {"NG-" + r["iso_3166_2"][3:]: polygonal(r.geometry) for _, r in a1[a1["adm0_a3"] == "NGA"].iterrows()}
    assert len(areas) == 37, len(areas)
    nigeria = unary_union(list(areas.values()))
    names, win = {}, box(*WINDOW)
    for _, r in a0[a0.intersects(win)].iterrows():
        a3 = r["ADM0_A3"]
        if a3 == "NGA":
            continue
        g = polygonal(polygonal(r.geometry).intersection(win).difference(nigeria))
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
    detail = build_detail(areas, "ng", DETAIL)
    out = {"type": "FeatureCollection",
           "features": [{"type": "Feature", "id": k, "geometry": rounded(g)} for k, g in geo.items() if not g.is_empty],
           "borders": rounded(merged(borders)), "coast": rounded(merged(coast)), "detail": detail}
    coast_u = unary_union(coast).buffer(1e-4)
    extra = {}
    for k, g in geo.items():
        if k.startswith("NG-"):
            nb = sorted({names[j] for j, h in geo.items() if j.startswith("T-") and g.boundary.intersection(h.boundary).length > 0.01})
            extra[k] = {"coastal": g.boundary.intersection(coast_u).length > 0.03, "borders": nb}
            main = max(getattr(g, "geoms", [g]), key=lambda p: p.area)
            if not main.contains(main.centroid):
                p = shapely.maximum_inscribed_circle(main, 0.01).coords[0]
                extra[k]["anchorLL"] = [round(p[0], 3), round(p[1], 3)]
    return out, extra


def main():
    fc, extra = shapes()
    (ROOT / "data" / "ng-states.json").write_text(json.dumps(fc, separators=(",", ":")), encoding="utf8")
    import ng_facts
    import capitals
    rows, nick = table(), nicknames()
    assert len(rows) == 37, len(rows)
    items, missing = [], []
    for code, row in rows.items():
        iso = "NG-" + code
        name = "Federal Capital Territory" if code == "FC" else row["name"]
        f = dict(ng_facts.FACTS.get(code, {}))
        f["nickname"] = nick.get(name, nick.get(row["name"], ""))
        if row["largest"] != row["capital"]:
            f["city"] = row["largest"]
        names = [name] + ([f"{name} State"] if code != "FC" else []) + ALT.get(code, [])
        it = {"iso": iso, "id": iso, "name": name, "names": list(dict.fromkeys(names)),
              "capitals": [row["capital"]] + CAP_ALT.get(row["capital"], []), "cont": ["Africa"], "car": False, "a2": iso,
              "info": {"abbr": code, "kind": "Federal Capital Territory" if code == "FC" else "State", "region": row["zone"],
                       "pop": row["pop"], "popYear": "2019 estimate", "area": row["area"], "flag": False, "facts": f,
                       **{k: v for k, v in extra.get(iso, {}).items() if k != "anchorLL"}}}
        if "anchorLL" in extra.get(iso, {}):
            it["anchorLL"] = extra[iso]["anchorLL"]
        ll = CAP_LL.get(row["capital"]) or capitals.find(row["capital"], a2="NG")
        if not ll:
            missing.append(row["capital"])
        it["capLL"] = [ll] if ll else []
        items.append(it)
    # names (and capitals) close enough for the typo rule to mix up: neither counts for the other
    for a in items:
        nt = [b["name"] for b in items if b is not a and near(a["name"], b["name"])]
        nt += [c for b in items if b is not a for c in b["capitals"][:1] if near(a["capitals"][0], c) and c != a["capitals"][0]]
        if nt:
            a["notTypo"] = sorted(set(nt))
    total = sum(it["info"]["pop"] for it in items)
    print(f"  population {total:,} (NBS 2019 estimates)")
    print("  notTypo pairs:", {a["name"]: a["notTypo"] for a in items if "notTypo" in a})
    if missing:
        print("  capitals not found:", missing)
    by_area = sorted(items, key=lambda c: -c["info"]["area"])
    for it in items:
        it["info"]["areaRank"] = by_area.index(it) + 1
    (ROOT / "data" / "ng-parts.json").write_text(json.dumps(sorted(items, key=lambda s: s["name"]), ensure_ascii=False, indent=0), encoding="utf8")
    print("  wrote data/ng-states.json and data/ng-parts.json:", len(items), "parts")


if __name__ == "__main__":
    main()
