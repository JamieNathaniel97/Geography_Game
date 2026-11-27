"""The disputes layer: every disputed territory in Natural Earth's 1:10m admin-0 disputed areas, with the facts in
tools/disputes_facts.py.

  data/disputes.json   [{id, name, admin, claim, since, info, country?, ring?: [lon, lat], shape?: GeoJSON}]
                       ring: a speck (Dokdo, Rockall...) drawn as a dotted ring; shape: an area drawn with a dotted outline;
                       country: the whole of a world-map country (Taiwan, Kosovo...), shown on that country's card instead.

In Learning mode the app draws them and a tap opens a small "Disputed" card (js/app.js showDisputeCard).
Run from the repo root:  python tools/build_disputes.py
"""
import json
import pathlib
import sys

import geopandas as gpd
import shapely
from shapely.geometry import mapping
from shapely.ops import unary_union

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from disputes_facts import DISPUTES  # noqa: E402
from detail import polygonal  # noqa: E402

SPECK = 0.004   # areas smaller than this (square degrees, about 40 km²) are drawn as rings


def rounded(geom, nd=3):
    def r(c):
        return [round(c[0], nd), round(c[1], nd)] if isinstance(c[0], (int, float)) else [r(x) for x in c]
    m = mapping(geom)
    return {"type": m["type"], "coordinates": r(json.loads(json.dumps(m["coordinates"])))}


def key_for(brk):
    b = brk.replace("﻿", "").strip()
    for k in DISPUTES:
        kk = k.replace("﻿", "")
        if kk == b or kk.startswith(b) or b.startswith(kk):
            return k
    return None


def main():
    d = gpd.read_file(ROOT / "tools" / "downloads" / "ne10" / "ne_10m_admin_0_disputed_areas.geojson")
    groups, missing = {}, []
    for _, r in d.iterrows():
        k = key_for(str(r["BRK_NAME"]))
        if not k:
            missing.append(r["BRK_NAME"])
            continue
        f = DISPUTES[k]
        if f.get("skip"):
            continue
        g = f.get("group", k)
        groups.setdefault(g, {"facts": f, "geoms": []})
        if f.get("group") and k.startswith("East Jerusalem"):  # the group's main entry gives its facts
            groups[g]["facts"] = f
        groups[g]["geoms"].append(polygonal(r.geometry))
    out = []
    for i, (g, v) in enumerate(sorted(groups.items())):
        f = v["facts"]
        item = {"id": f"D-{i:02d}", "name": f["name"] if not f.get("group") or g != "Jerusalem" else "East Jerusalem",
                **{k: f[k] for k in ("admin", "claim", "since", "info", "country") if k in f}}
        if not f.get("country"):
            geom = polygonal(unary_union(v["geoms"]))
            if geom.area < SPECK:
                c = geom.centroid
                item["ring"] = [round(c.x, 3), round(c.y, 3)]
            else:
                item["shape"] = rounded(shapely.simplify(geom, 0.01, preserve_topology=True))
        out.append(item)
    (ROOT / "data" / "disputes.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf8")
    print(f"wrote data/disputes.json: {len(out)} disputes ({sum('ring' in x for x in out)} rings, {sum('shape' in x for x in out)} areas, "
          f"{sum('country' in x for x in out)} on country cards)")
    if missing:
        print("no facts for:", missing)


if __name__ == "__main__":
    main()
