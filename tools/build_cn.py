"""Builds China's country map (China_plan.md): its 33 provincial-level divisions.

  data/cn-provinces.json  the 33 shapes (Natural Earth 1:10m admin-1, with Hong Kong and Macau from admin-0; the Paracel
                          Islands left off), the neighbours as grey areas (Taiwan among them: governed separately), and
                          Aksai Chin and the Shaksgam Valley as grey disputed areas. Lines: "borders", "coast", "disputed".
  data/cn-parts.json      names (with Chinese characters and pinyin), capitals, kind, region and Learning facts
                          (tools/cn_facts.py); populations from the 2020 census (Hong Kong and Macau: their 2021 censuses)
  data/flags/cn/          the Hong Kong and Macau regional flags (Flagpedia), shown on their Learning cards

Run from the repo root:  python tools/build_cn.py
"""
import io
import json
import pathlib
import sys
import urllib.request

import geopandas as gpd
import shapely
from PIL import Image
from shapely.geometry import mapping, MultiLineString
from shapely.ops import unary_union, linemerge

ROOT = pathlib.Path(__file__).resolve().parent.parent
NE = ROOT / "tools" / "downloads" / "ne10"
SIMPLIFY = 0.02  # degrees (about 2 km): China is twice India's size, and the coverage is simplified as a whole

# Natural Earth name -> (code (ISO 3166-2:CN), shown name, kind, region, capitals, population, area km²)
PARTS = {
    "Anhui": ("AH", "Anhui", "Province", "East", ["Hefei"], 61027171, 140100),
    "Fujian": ("FJ", "Fujian", "Province", "East", ["Fuzhou"], 41540086, 124000),
    "Gansu": ("GS", "Gansu", "Province", "Northwest", ["Lanzhou"], 25019831, 425800),
    "Guangdong": ("GD", "Guangdong", "Province", "South Central", ["Guangzhou", "Canton"], 126012510, 179800),
    "Guizhou": ("GZ", "Guizhou", "Province", "Southwest", ["Guiyang"], 38562148, 176200),
    "Hainan": ("HI", "Hainan", "Province", "South Central", ["Haikou"], 10081232, 35400),
    "Hebei": ("HE", "Hebei", "Province", "North", ["Shijiazhuang"], 74610235, 188800),
    "Heilongjiang": ("HL", "Heilongjiang", "Province", "Northeast", ["Harbin"], 31850088, 473000),
    "Henan": ("HA", "Henan", "Province", "South Central", ["Zhengzhou"], 99365519, 167000),
    "Hubei": ("HB", "Hubei", "Province", "South Central", ["Wuhan"], 57752557, 185900),
    "Hunan": ("HN", "Hunan", "Province", "South Central", ["Changsha"], 66444864, 211800),
    "Jiangsu": ("JS", "Jiangsu", "Province", "East", ["Nanjing", "Nanking"], 84748016, 107200),
    "Jiangxi": ("JX", "Jiangxi", "Province", "East", ["Nanchang"], 45188635, 166900),
    "Jilin": ("JL", "Jilin", "Province", "Northeast", ["Changchun"], 24073453, 187400),
    "Liaoning": ("LN", "Liaoning", "Province", "Northeast", ["Shenyang", "Mukden"], 42591407, 148000),
    "Qinghai": ("QH", "Qinghai", "Province", "Northwest", ["Xining"], 5923957, 722300),
    "Shaanxi": ("SN", "Shaanxi", "Province", "Northwest", ["Xi'an", "Xian"], 39528999, 205600),
    "Shandong": ("SD", "Shandong", "Province", "East", ["Jinan"], 101527453, 157100),
    "Shanxi": ("SX", "Shanxi", "Province", "North", ["Taiyuan"], 34915616, 156700),
    "Sichuan": ("SC", "Sichuan", "Province", "Southwest", ["Chengdu"], 83674866, 486000),
    "Yunnan": ("YN", "Yunnan", "Province", "Southwest", ["Kunming"], 47209277, 394100),
    "Zhejiang": ("ZJ", "Zhejiang", "Province", "East", ["Hangzhou"], 64567588, 105500),
    "Guangxi": ("GX", "Guangxi", "Autonomous region", "South Central", ["Nanning"], 50126804, 237600),
    "Inner Mongol": ("NM", "Inner Mongolia", "Autonomous region", "North", ["Hohhot"], 24049155, 1183000),
    "Ningxia": ("NX", "Ningxia", "Autonomous region", "Northwest", ["Yinchuan"], 7202654, 66400),
    "Xizang": ("XZ", "Tibet", "Autonomous region", "Southwest", ["Lhasa"], 3648100, 1228400),
    "Xinjiang": ("XJ", "Xinjiang", "Autonomous region", "Northwest", ["Ürümqi", "Urumqi"], 25852345, 1664900),
    "Beijing": ("BJ", "Beijing", "Municipality", "North", ["Beijing", "Peking"], 21893095, 16410),
    "Chongqing": ("CQ", "Chongqing", "Municipality", "Southwest", ["Chongqing", "Chungking"], 32054159, 82400),
    "Shanghai": ("SH", "Shanghai", "Municipality", "East", ["Shanghai"], 24870895, 6341),
    "Tianjin": ("TJ", "Tianjin", "Municipality", "North", ["Tianjin", "Tientsin"], 13866009, 11966),
}
SARS = {"HKG": ("HK", "Hong Kong", "Special administrative region", "South Central", ["Hong Kong"], 7413070, 1114),
        "MAC": ("MO", "Macau", "Special administrative region", "South Central", ["Macau", "Macao"], 683218, 33)}
# extra names accepted when typing: old spellings and the full official names
NAMES = {
    "SC": ["Szechwan", "Szechuan"], "GD": ["Kwangtung"], "FJ": ["Fukien"], "SN": ["Shensi"], "SX": ["Shansi"], "GS": ["Kansu"],
    "XJ": ["Sinkiang", "Xinjiang Uyghur", "Xinjiang Uygur"], "XZ": ["Xizang"], "NM": ["Nei Mongol", "Nei Menggu"],
    "GX": ["Guangxi Zhuang"], "NX": ["Ningxia Hui"], "HK": ["HK"], "MO": ["Macao"], "BJ": ["Peking"], "TJ": ["Tientsin"],
    "HL": ["Heilungkiang"], "JS": ["Kiangsu"], "ZJ": ["Chekiang"], "HN": [], "HB": ["Hupeh"], "HA": ["Honan"], "HE": ["Hopeh"],
    "YN": [], "GZ": ["Kweichow"], "JX": ["Kiangsi"], "AH": ["Anhwei"], "SD": ["Shantung"], "LN": [], "JL": ["Kirin"], "QH": [],
}
# never accept one of these as a typo of the other (they differ by a letter)
NOT_TYPO = {"SN": ["Shanxi"], "SX": ["Shaanxi"], "HB": ["Hebei"], "HE": ["Hubei"], "HN": ["Henan"], "HA": ["Hunan"]}
NEIGHBOURS = {"TWN": "Taiwan", "MNG": "Mongolia", "RUS": "Russia", "PRK": "North Korea", "KOR": "South Korea", "JPN": "Japan",
              "KAZ": "Kazakhstan", "KGZ": "Kyrgyzstan", "TJK": "Tajikistan", "AFG": "Afghanistan", "PAK": "Pakistan", "IND": "India",
              "NPL": "Nepal", "BTN": "Bhutan", "MMR": "Myanmar", "LAO": "Laos", "VNM": "Vietnam", "BGD": "Bangladesh", "PHL": "Philippines"}
DISPUTED_GREY = {"Aksai Chin": "T-AKSAI", "Shaksam Valley": "T-SHAKSGAM", "Siachen Glacier": "T-SIACHEN"}
# Indian-administered areas China claims: China's borders with them are dotted
CLAIMED_BY_CHINA = {"Arunachal Pradesh", "Demchok", "Samdu Valleys", "Tirpani Valleys", "Bara Hotii Valleys"}
FLAGS = {"HK": "hk", "MO": "mo"}
NAMES_OF = {}  # grey area id -> its name (filled in by shapes())


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
    areas = {}
    for _, r in a1[a1["adm0_a3"] == "CHN"].iterrows():
        if r["name"] == "Paracel Islands":
            continue  # disputed in the South China Sea: left off (China_plan.md)
        areas["CN-" + PARTS[r["name"]][0]] = polygonal(r.geometry)
    for a3, part in SARS.items():
        areas["CN-" + part[0]] = polygonal(a0[a0["ADM0_A3"] == a3].geometry.iloc[0])
    assert len(areas) == 33, len(areas)
    grey_dsp = {DISPUTED_GREY[r["BRK_NAME"]]: polygonal(r.geometry) for _, r in dsp.iterrows() if r["BRK_NAME"] in DISPUTED_GREY}
    dsp_all = unary_union(list(grey_dsp.values()))
    for k in list(areas):  # Natural Earth draws Aksai Chin and Shaksgam inside Xinjiang and Tibet: cut them out, grey
        areas[k] = polygonal(areas[k].difference(dsp_all))
    china = unary_union(list(areas.values()))
    # every country in a wide window (a tall phone screen shows well beyond China), grey; tiny islands dropped
    window = shapely.box(50, -12, 165, 64)
    for _, r in a0[a0.intersects(window)].iterrows():
        a3 = r["ADM0_A3"]
        if a3 in ("CHN", "HKG", "MAC") or a3 in DISPUTED_GREY.values():
            continue
        g = polygonal(polygonal(r.geometry).intersection(window).difference(dsp_all).difference(china))
        g = unary_union([p for p in getattr(g, "geoms", [g]) if p.area > 0.02 or a3 in NEIGHBOURS])
        if not g.is_empty:
            areas["T-" + a3] = polygonal(g)
            NAMES_OF["T-" + a3] = NEIGHBOURS.get(a3, r["NAME"])
    for k, g in grey_dsp.items():
        areas[k] = polygonal(g.difference(china))
    keys = list(areas)
    geo = shapely.coverage_clean([areas[k] for k in keys], gap_width=0.002, snapping_distance=0.0001)
    geo = shapely.coverage_simplify([polygonal(g) for g in geo], SIMPLIFY)
    geo = {k: polygonal(shapely.set_precision(polygonal(g), 0.001)) for k, g in zip(keys, geo)}
    claimed = unary_union([polygonal(r.geometry) for _, r in dsp.iterrows() if r["BRK_NAME"] in CLAIMED_BY_CHINA]).buffer(0.05)
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
            chinese = [k for k in pair if k.startswith("CN-")]
            if not chinese:
                borders += ls
            elif pair & set(DISPUTED_GREY.values()):
                disputed += ls
            elif "T-IND" in pair:
                line = unary_union(ls)
                disputed += lines_only(line.intersection(claimed))
                borders += lines_only(line.difference(claimed))
            else:
                borders += ls
    bu = unary_union(borders + disputed)
    coast = lines_only(unary_union([g.boundary for g in geo.values()]).difference(bu.buffer(1e-7))
                       .difference(window.exterior.buffer(0.01)))  # not the window's own edges
    merged = lambda ls: linemerge(ls) if ls else MultiLineString([])
    out = {"type": "FeatureCollection",
           "features": [{"type": "Feature", "id": k, "geometry": rounded(g)} for k, g in geo.items() if not g.is_empty],
           "borders": rounded(merged(borders)), "coast": rounded(merged(coast)), "disputed": rounded(merged(disputed))}
    coast_u = unary_union(coast).buffer(1e-4)
    names = dict(NAMES_OF)
    names.update({"T-AKSAI": "Aksai Chin (disputed)", "T-SHAKSGAM": "Shaksgam Valley (disputed)", "T-SIACHEN": "Siachen (disputed)"})
    extra = {}
    for k, g in geo.items():
        if k.startswith("CN-"):
            nb = sorted({names[j] for j, h in geo.items() if j.startswith("T-") and g.boundary.intersection(h.boundary).length > 0.01})
            extra[k] = {"coastal": g.boundary.intersection(coast_u).length > 0.05, "borders": nb}
    for k, g in geo.items():  # a curved part (Gansu) has its centre outside it: give a point well inside instead
        if k.startswith("CN-"):
            main = max(getattr(g, "geoms", [g]), key=lambda p: p.area)
            if not main.contains(main.centroid):
                p = shapely.maximum_inscribed_circle(main, 0.01).coords[0]
                extra[k]["anchorLL"] = [round(p[0], 3), round(p[1], 3)]
    return out, extra


def main():
    fc, extra = shapes()
    (ROOT / "data" / "cn-provinces.json").write_text(json.dumps(fc, separators=(",", ":")), encoding="utf8")
    sys.path.insert(0, str(ROOT / "tools"))
    import cn_facts
    import capitals
    items = []
    for code, name, kind, region, caps, pop, area in list(PARTS.values()) + list(SARS.values()):
        iso = "CN-" + code
        f = cn_facts.FACTS.get(code, {})
        it = {"iso": iso, "id": iso, "name": name, "names": list(dict.fromkeys([name] + NAMES.get(code, []))), "capitals": caps,
              "cont": ["Asia"], "car": False, "a2": iso,
              "info": {"abbr": code, "kind": kind, "region": region, "pop": pop,
                       "popYear": "2021 census" if code in ("HK", "MO") else "2020 census", "area": area,
                       "flag": code in FLAGS, "facts": f, **extra.get(iso, {})}}
        if "anchorLL" in it["info"]:
            it["anchorLL"] = it["info"].pop("anchorLL")
        if code in NOT_TYPO:
            it["notTypo"] = NOT_TYPO[code]
        if code in FLAGS:
            it["flagKey"] = "cn/" + iso
        items.append(it)
    by_area = sorted(items, key=lambda c: -c["info"]["area"])
    for it in items:
        it["info"]["areaRank"] = by_area.index(it) + 1
    missing = []
    for it in items:
        city = {"Ürümqi": "Urumqi", "Hong Kong": "Hong Kong", "Macau": "Macau"}.get(it["capitals"][0], it["capitals"][0])
        a2 = {"CN-HK": "HK", "CN-MO": "MO"}.get(it["iso"], "CN")
        ll = capitals.find(city, a2=a2)
        if ll:
            it["capLL"] = [ll]
        else:
            missing.append(f"{it['name']}: {city}")
            it["capLL"] = []
    if missing:
        print("capitals not found:", missing)
    out = ROOT / "data" / "flags" / "cn"
    out.mkdir(parents=True, exist_ok=True)
    for code, fc_code in FLAGS.items():
        p = out / f"CN-{code}.webp"
        if not p.exists():
            data = urllib.request.urlopen(urllib.request.Request(f"https://flagcdn.com/w640/{fc_code}.webp",
                                                                 headers={"User-Agent": "GaiaQuestBuild/1.0"}), timeout=60).read()
            Image.open(io.BytesIO(data)).convert("RGB").save(p, "WEBP", quality=88)
    (ROOT / "data" / "cn-parts.json").write_text(json.dumps(sorted(items, key=lambda s: s["name"]), ensure_ascii=False, indent=0), encoding="utf8")
    print("wrote data/cn-provinces.json and data/cn-parts.json:", len(items), "parts")


if __name__ == "__main__":
    main()
