"""Builds the Britain and Ireland county data (build 4): two county sets, each with Ireland's 32 traditional counties
and the Crown Dependencies.

  data/uk-historic.json, data/uk-ceremonial.json   shapes, with the border and coastline lines worked out in advance
                    (the same layout as data/ca-provinces.json; France is a grey area near the Channel Islands)
  data/counties-historic.json, data/counties-ceremonial.json   the counties: names, county towns, nation, facts
  data/flags/uk/<id>.webp   county flags from the UK Flag Registry, and the Crown Dependencies' flags

Sources (all free to reuse, credited in the app):
  historic counties of Great Britain   Historic County Borders Project, Definition A, full resolution (https://www.county-borders.co.uk)
  coastline of Great Britain           GSHHG full resolution (Wessel and Smith, LGPL)
  ceremonial counties (England), preserved counties (Wales), lieutenancy areas (Scotland)
                                       Ordnance Survey Boundary-Line, Open Government Licence
  Ireland's 32 counties                townlands.ie (from OpenStreetMap, ODbL)
  Crown Dependencies                   Natural Earth 1:10m (public domain)
  county towns' positions              GeoNames cities500 (CC BY 4.0)
  county flags                         UK Flag Registry (Flag Institute), images from the Historic Counties Trust;
                                       Crown Dependencies from Flagpedia and Wikimedia Commons

Run from the repo root:  python tools/build_uk.py   (downloads go in tools/downloads/uk/)
"""
import io
import json
import pathlib
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
import zipfile

import geopandas as gpd
import shapely
from PIL import Image
from pyproj import Geod
from shapely.geometry import box, mapping, MultiLineString, Point
from shapely.ops import unary_union, linemerge

ROOT = pathlib.Path(__file__).resolve().parent.parent
DL = ROOT / "tools" / "downloads" / "uk"
UA = {"User-Agent": "GaiaQuestBuild/1.0 (map quiz data build)"}
SIMPLIFY = 0.004  # degrees (about 300 m), kept consistent between neighbouring counties
GEOD = Geod(ellps="WGS84")

# ---------- historic counties of Great Britain: county town(s), first = the one shown ----------
# Where the county town is disputed or has moved, the other commonly cited ones are accepted too.
HISTORIC = {
    # England
    "Bedfordshire": ["Bedford"], "Berkshire": ["Reading", "Abingdon"], "Buckinghamshire": ["Aylesbury", "Buckingham"],
    "Cambridgeshire": ["Cambridge"], "Cheshire": ["Chester"], "Cornwall": ["Truro", "Bodmin", "Launceston"],
    "Cumberland": ["Carlisle"], "Derbyshire": ["Derby", "Matlock"], "Devon": ["Exeter"], "Dorset": ["Dorchester"],
    "Durham": ["Durham"], "Essex": ["Chelmsford"], "Gloucestershire": ["Gloucester"], "Hampshire": ["Winchester"],
    "Herefordshire": ["Hereford"], "Hertfordshire": ["Hertford"], "Huntingdonshire": ["Huntingdon"],
    "Kent": ["Maidstone", "Canterbury"], "Lancashire": ["Lancaster", "Preston"], "Leicestershire": ["Leicester"],
    "Lincolnshire": ["Lincoln"], "Middlesex": ["Brentford", "Westminster"], "Norfolk": ["Norwich"],
    "Northamptonshire": ["Northampton"], "Northumberland": ["Alnwick", "Morpeth", "Newcastle upon Tyne", "Newcastle"],
    "Nottinghamshire": ["Nottingham", "West Bridgford"], "Oxfordshire": ["Oxford"], "Rutland": ["Oakham"],
    "Shropshire": ["Shrewsbury"], "Somerset": ["Taunton", "Ilchester", "Somerton"], "Staffordshire": ["Stafford"],
    "Suffolk": ["Ipswich", "Bury St Edmunds"], "Surrey": ["Guildford", "Kingston upon Thames", "Kingston"],
    "Sussex": ["Lewes", "Chichester"], "Warwickshire": ["Warwick"],
    "Westmorland": ["Appleby-in-Westmorland", "Appleby", "Kendal"], "Wiltshire": ["Trowbridge", "Wilton", "Salisbury"],
    "Worcestershire": ["Worcester"], "Yorkshire": ["York"],
    # Wales
    "Anglesey": ["Beaumaris", "Llangefni"], "Brecknockshire": ["Brecon"], "Caernarfonshire": ["Caernarfon"],
    "Cardiganshire": ["Cardigan", "Aberystwyth"], "Carmarthenshire": ["Carmarthen"], "Denbighshire": ["Denbigh", "Ruthin"],
    "Flintshire": ["Mold", "Flint"], "Glamorgan": ["Cardiff", "Cowbridge"], "Merionethshire": ["Dolgellau", "Bala"],
    "Monmouthshire": ["Monmouth", "Usk", "Newport"], "Montgomeryshire": ["Montgomery", "Welshpool"],
    "Pembrokeshire": ["Haverfordwest", "Pembroke"], "Radnorshire": ["Presteigne", "Llandrindod Wells", "New Radnor"],
    # Scotland
    "Aberdeenshire": ["Aberdeen"], "Angus": ["Forfar"], "Argyllshire": ["Inveraray", "Lochgilphead"], "Ayrshire": ["Ayr"],
    "Banffshire": ["Banff"], "Berwickshire": ["Duns", "Greenlaw"], "Buteshire": ["Rothesay"], "Caithness": ["Wick"],
    "Clackmannanshire": ["Alloa", "Clackmannan"], "Cromartyshire": ["Cromarty", "Dingwall"], "Dumfriesshire": ["Dumfries"],
    "Dunbartonshire": ["Dumbarton"], "East Lothian": ["Haddington"], "Fife": ["Cupar", "Glenrothes"],
    "Inverness-shire": ["Inverness"], "Kincardineshire": ["Stonehaven"], "Kinross-shire": ["Kinross"],
    "Kirkcudbrightshire": ["Kirkcudbright"], "Lanarkshire": ["Lanark", "Hamilton"], "Midlothian": ["Edinburgh"],
    "Morayshire": ["Elgin"], "Nairnshire": ["Nairn"], "Orkney": ["Kirkwall"], "Peeblesshire": ["Peebles"],
    "Perthshire": ["Perth"], "Renfrewshire": ["Renfrew", "Paisley"], "Ross-shire": ["Dingwall"],
    "Roxburghshire": ["Jedburgh"], "Selkirkshire": ["Selkirk"], "Shetland": ["Lerwick"], "Stirlingshire": ["Stirling"],
    "Sutherland": ["Dornoch"], "West Lothian": ["Linlithgow"], "Wigtownshire": ["Wigtown", "Stranraer"],
}
WALES_H = {"Anglesey", "Brecknockshire", "Caernarfonshire", "Cardiganshire", "Carmarthenshire", "Denbighshire", "Flintshire",
           "Glamorgan", "Merionethshire", "Monmouthshire", "Montgomeryshire", "Pembrokeshire", "Radnorshire"}
SCOTLAND_H = {"Aberdeenshire", "Angus", "Argyllshire", "Ayrshire", "Banffshire", "Berwickshire", "Buteshire", "Caithness",
              "Clackmannanshire", "Cromartyshire", "Dumfriesshire", "Dunbartonshire", "East Lothian", "Fife", "Inverness-shire",
              "Kincardineshire", "Kinross-shire", "Kirkcudbrightshire", "Lanarkshire", "Midlothian", "Morayshire", "Nairnshire",
              "Orkney", "Peeblesshire", "Perthshire", "Renfrewshire", "Ross-shire", "Roxburghshire", "Selkirkshire", "Shetland",
              "Stirlingshire", "Sutherland", "West Lothian", "Wigtownshire"}
HISTORIC_SHOWN = {"Durham": "County Durham"}  # the name shown, where it differs from the data's
# extra names accepted when typing (also: Scottish and Welsh "-shire" names without it, e.g. Argyll, Moray)
HISTORIC_ALT = {
    "Durham": ["Durham"], "Shropshire": ["Salop"], "Kirkcudbrightshire": ["Stewartry of Kirkcudbright", "The Stewartry"],
    "Caernarfonshire": ["Caernarvonshire", "Carnarvonshire"], "Brecknockshire": ["Breconshire", "Brecon"],
    "Cardiganshire": ["Ceredigion"], "Anglesey": ["Ynys Mon", "Isle of Anglesey"], "Angus": ["Forfarshire"],
    "Midlothian": ["Edinburghshire"], "West Lothian": ["Linlithgowshire"], "East Lothian": ["Haddingtonshire"],
    "Morayshire": ["Elginshire"], "Peeblesshire": ["Tweeddale"], "Monmouthshire": ["Gwent"], "Glamorgan": ["Morgannwg"],
    "Yorkshire": ["Yorks"],
}
# historic counties with a flag in the UK Flag Registry (the Historic Counties Trust's list); others aren't in the flag games
REGISTERED = {
    "Aberdeenshire", "Anglesey", "Banffshire", "Bedfordshire", "Berkshire", "Berwickshire", "Buckinghamshire", "Caernarfonshire",
    "Caithness", "Cambridgeshire", "Cheshire", "Cornwall", "Durham", "Cumberland", "Derbyshire", "Devon", "Dorset",
    "East Lothian", "Essex", "Flintshire", "Glamorgan", "Gloucestershire", "Hampshire", "Herefordshire", "Hertfordshire",
    "Huntingdonshire", "Kent", "Kirkcudbrightshire", "Lancashire", "Leicestershire", "Lincolnshire", "Merionethshire",
    "Middlesex", "Monmouthshire", "Morayshire", "Norfolk", "Northamptonshire", "Northumberland", "Nottinghamshire", "Orkney",
    "Oxfordshire", "Pembrokeshire", "Rutland", "Shetland", "Shropshire", "Somerset", "Staffordshire", "Suffolk", "Surrey",
    "Sussex", "Sutherland", "Warwickshire", "Westmorland", "Wiltshire", "Worcestershire", "Yorkshire",
}

# ---------- Ireland: the 32 traditional counties (both Northern Ireland and the Republic) ----------
# name: (county town(s), province); Northern Ireland's six are marked in NI6
IRELAND = {
    "Antrim": (["Antrim", "Carrickfergus", "Belfast"], "Ulster"), "Armagh": (["Armagh"], "Ulster"),
    "Carlow": (["Carlow"], "Leinster"), "Cavan": (["Cavan"], "Ulster"), "Clare": (["Ennis"], "Munster"),
    "Cork": (["Cork"], "Munster"), "Donegal": (["Lifford"], "Ulster"), "Down": (["Downpatrick"], "Ulster"),
    "Dublin": (["Dublin"], "Leinster"), "Fermanagh": (["Enniskillen"], "Ulster"), "Galway": (["Galway"], "Connacht"),
    "Kerry": (["Tralee"], "Munster"), "Kildare": (["Naas"], "Leinster"), "Kilkenny": (["Kilkenny"], "Leinster"),
    "Laois": (["Portlaoise", "Port Laoise"], "Leinster"), "Leitrim": (["Carrick-on-Shannon"], "Connacht"),
    "Limerick": (["Limerick", "Newcastle West"], "Munster"),
    "Londonderry": (["Coleraine", "Derry", "Londonderry"], "Ulster"), "Longford": (["Longford"], "Leinster"),
    "Louth": (["Dundalk"], "Leinster"), "Mayo": (["Castlebar"], "Connacht"), "Meath": (["Navan", "Trim"], "Leinster"),
    "Monaghan": (["Monaghan"], "Ulster"), "Offaly": (["Tullamore"], "Leinster"), "Roscommon": (["Roscommon"], "Connacht"),
    "Sligo": (["Sligo"], "Connacht"), "Tipperary": (["Clonmel", "Nenagh"], "Munster"), "Tyrone": (["Omagh"], "Ulster"),
    "Waterford": (["Waterford", "Dungarvan"], "Munster"), "Westmeath": (["Mullingar"], "Leinster"),
    "Wexford": (["Wexford"], "Leinster"), "Wicklow": (["Wicklow"], "Leinster"),
}
NI6 = {"Antrim", "Armagh", "Down", "Fermanagh", "Londonderry", "Tyrone"}
IRELAND_ALT = {"Londonderry": ["Derry"], "Laois": ["Leix", "Queen's County"], "Offaly": ["King's County"]}

# ---------- ceremonial counties (England), preserved counties (Wales), lieutenancy areas (Scotland) ----------
CEREMONIAL = {
    # England
    "Bedfordshire": ["Bedford"], "Berkshire": ["Reading"], "Bristol": ["Bristol"], "Buckinghamshire": ["Aylesbury"],
    "Cambridgeshire": ["Cambridge"], "Cheshire": ["Chester"], "City of London": ["London", "City of London"],
    "Cornwall": ["Truro"], "Cumbria": ["Carlisle"], "Derbyshire": ["Matlock", "Derby"], "Devon": ["Exeter"],
    "Dorset": ["Dorchester"], "Durham": ["Durham"], "East Riding of Yorkshire": ["Beverley"], "East Sussex": ["Lewes"],
    "Essex": ["Chelmsford"], "Gloucestershire": ["Gloucester"], "Greater London": ["London"],
    "Greater Manchester": ["Manchester"], "Hampshire": ["Winchester"], "Herefordshire": ["Hereford"],
    "Hertfordshire": ["Hertford"], "Isle of Wight": ["Newport"], "Kent": ["Maidstone"], "Lancashire": ["Preston", "Lancaster"],
    "Leicestershire": ["Leicester", "Glenfield"], "Lincolnshire": ["Lincoln"], "Merseyside": ["Liverpool"],
    "Norfolk": ["Norwich"], "North Yorkshire": ["Northallerton"], "Northamptonshire": ["Northampton"],
    "Northumberland": ["Morpeth", "Alnwick"], "Nottinghamshire": ["Nottingham", "West Bridgford"], "Oxfordshire": ["Oxford"],
    "Rutland": ["Oakham"], "Shropshire": ["Shrewsbury"], "Somerset": ["Taunton"], "South Yorkshire": ["Barnsley", "Sheffield"],
    "Staffordshire": ["Stafford"], "Suffolk": ["Ipswich"], "Surrey": ["Guildford", "Reigate", "Kingston upon Thames"],
    "Tyne and Wear": ["Newcastle upon Tyne", "Newcastle"], "Warwickshire": ["Warwick"], "West Midlands": ["Birmingham"],
    "West Sussex": ["Chichester"], "West Yorkshire": ["Wakefield"], "Wiltshire": ["Trowbridge"], "Worcestershire": ["Worcester"],
    # Wales
    "Clwyd": ["Mold"], "Dyfed": ["Carmarthen"], "Gwent": ["Cwmbran"], "Gwynedd": ["Caernarfon"],
    "Mid Glamorgan": ["Cardiff", "Bridgend"], "Powys": ["Llandrindod Wells"], "South Glamorgan": ["Cardiff"],
    "West Glamorgan": ["Swansea"],
    # Scotland
    "Aberdeen": ["Aberdeen"], "Aberdeenshire": ["Aberdeen"], "Angus": ["Forfar"], "Argyll and Bute": ["Lochgilphead", "Inveraray"],
    "Ayrshire and Arran": ["Ayr"], "Banffshire": ["Banff"], "Berwickshire": ["Duns"], "Caithness": ["Wick"],
    "Clackmannanshire": ["Alloa"], "Dumfries": ["Dumfries"], "Dunbartonshire": ["Dumbarton"], "Dundee": ["Dundee"],
    "East Lothian": ["Haddington"], "Edinburgh": ["Edinburgh"], "Fife": ["Glenrothes", "Cupar"], "Glasgow": ["Glasgow"],
    "Inverness": ["Inverness"], "Kincardineshire": ["Stonehaven"], "Lanarkshire": ["Hamilton", "Lanark"],
    "Midlothian": ["Dalkeith"], "Moray": ["Elgin"], "Nairn": ["Nairn"], "Orkney": ["Kirkwall"],
    "Perth and Kinross": ["Perth"], "Renfrewshire": ["Paisley", "Renfrew"], "Ross and Cromarty": ["Dingwall"],
    "Roxburgh, Ettrick and Lauderdale": ["Newtown St Boswells", "Jedburgh", "Selkirk"], "Shetland": ["Lerwick"],
    "Stirling and Falkirk": ["Stirling"], "Sutherland": ["Dornoch"], "The Stewartry of Kirkcudbright": ["Kirkcudbright"],
    "Tweeddale": ["Peebles"], "West Lothian": ["Livingston", "Linlithgow"], "Western Isles": ["Stornoway"],
    "Wigtown": ["Stranraer", "Wigtown"],
}
WALES_C = {"Clwyd", "Dyfed", "Gwent", "Gwynedd", "Mid Glamorgan", "Powys", "South Glamorgan", "West Glamorgan"}
SCOTLAND_C = {"Aberdeen", "Aberdeenshire", "Angus", "Argyll and Bute", "Ayrshire and Arran", "Banffshire", "Berwickshire",
              "Caithness", "Clackmannanshire", "Dumfries", "Dunbartonshire", "Dundee", "East Lothian", "Edinburgh", "Fife",
              "Glasgow", "Inverness", "Kincardineshire", "Lanarkshire", "Midlothian", "Moray", "Nairn", "Orkney",
              "Perth and Kinross", "Renfrewshire", "Ross and Cromarty", "Roxburgh, Ettrick and Lauderdale", "Shetland",
              "Stirling and Falkirk", "Sutherland", "The Stewartry of Kirkcudbright", "Tweeddale", "West Lothian",
              "Western Isles", "Wigtown"}
CEREMONIAL_SHOWN = {"Durham": "County Durham", "Aberdeen": "City of Aberdeen", "Dundee": "City of Dundee",
                    "Edinburgh": "City of Edinburgh", "Glasgow": "City of Glasgow"}
CEREMONIAL_ALT = {"Durham": ["Durham"], "Western Isles": ["Outer Hebrides", "Na h-Eileanan Siar"],
                  "East Riding of Yorkshire": ["East Riding", "East Yorkshire"], "The Stewartry of Kirkcudbright": ["Kirkcudbright", "Stewartry of Kirkcudbright", "The Stewartry"],
                  "City of London": ["The City"], "Aberdeen": ["Aberdeen"], "Dundee": ["Dundee"], "Edinburgh": ["Edinburgh"],
                  "Glasgow": ["Glasgow"], "Moray": ["Morayshire"], "Nairn": ["Nairnshire"], "Inverness": ["Inverness-shire"]}
# a ceremonial area flies the registered flag of the historic county it shares its name (or most of its land) with
CEREMONIAL_FLAG = {n: n for n in CEREMONIAL if n in REGISTERED}
CEREMONIAL_FLAG.update({"Durham": "Durham", "Moray": "Morayshire", "The Stewartry of Kirkcudbright": "Kirkcudbrightshire"})
# the Ordnance Survey's names, where they differ from the ones above
OS_NAMES = {"City and County of the City of London": "City of London", "City of Aberdeen": "Aberdeen",
            "City of Dundee": "Dundee", "City of Edinburgh": "Edinburgh", "City of Glasgow": "Glasgow",
            "Clackmannan": "Clackmannanshire", "Tyne & Wear": "Tyne and Wear"}

# ---------- Crown Dependencies (off by default in games) ----------
CROWN = {
    "D-IOM": ("Isle of Man", ["Douglas"], ["Mann"]),
    "D-JER": ("Jersey", ["St Helier", "Saint Helier"], []),
    "D-GGY": ("Guernsey", ["St Peter Port", "Saint Peter Port"], []),
    "D-ALD": ("Alderney", ["St Anne", "Saint Anne"], []),
    "D-SRK": ("Sark", ["La Seigneurie", "Sark"], []),
}
CROWN_FLAGS = {"D-IOM": "https://flagcdn.com/w640/im.webp", "D-JER": "https://flagcdn.com/w640/je.webp",
               "D-GGY": "https://flagcdn.com/w640/gg.webp",
               "D-ALD": "https://commons.wikimedia.org/wiki/Special:FilePath/Flag_of_Alderney.svg?width=640",
               "D-SRK": "https://commons.wikimedia.org/wiki/Special:FilePath/Flag_of_Sark.svg?width=640"}
TOWN_LL = {"Lifford": (-7.4797, 54.8339), "La Seigneurie": (-2.3606, 49.4316)}  # not in GeoNames cities500


def slug(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").upper()


def fetch(url, path):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300).read())
    return path


def sq_km(geom):
    return abs(GEOD.geometry_area_perimeter(geom)[0]) / 1e6


def lines_only(g):
    if g.is_empty:
        return []
    if g.geom_type == "LineString":
        return [g]
    if g.geom_type == "MultiLineString":
        return list(g.geoms)
    if hasattr(g, "geoms"):
        return [x for part in g.geoms for x in lines_only(part)]
    return []


def rounded(geom, nd=3):
    def r(c):
        return [round(c[0], nd), round(c[1], nd)] if isinstance(c[0], (int, float)) else [r(x) for x in c]
    g = mapping(geom)
    return {"type": g["type"], "coordinates": r(json.loads(json.dumps(g["coordinates"])))}


# ---------- sources ----------
def polygonal(g):
    """the area of a geometry (make_valid and overlays can leave stray lines and points)"""
    g = shapely.make_valid(g)
    if g.geom_type in ("Polygon", "MultiPolygon"):
        return g
    return unary_union([p for p in getattr(g, "geoms", []) if p.geom_type in ("Polygon", "MultiPolygon")])


def gb_land(near):
    """Great Britain's land at high water from GSHHG (full resolution, LGPL), within reach of `near` (the GB counties):
    the county sources draw some areas out over the water (Bristol's strip down the Severn to Flat and Steep Holm,
    the Wash's sandbanks, the historic counties' estuary borders)."""
    z = fetch("https://www.soest.hawaii.edu/pwessel/gshhg/gshhg-shp-2.3.7.zip", DL / "gshhg-shp-2.3.7.zip")
    g = gpd.read_file(f"zip://{z}!GSHHS_shp/f/GSHHS_f_L1.shp", bbox=(-9, 49.5, 2.5, 61.5))
    reach = polygonal(near.simplify(0.002)).buffer(0.03)  # keeps out Ireland, the Isle of Man and France
    return polygonal(unary_union(list(g.geometry)).intersection(reach))


def fit_to_land(areas, land):
    """Each county cut to the coastline, and the land the county outlines missed shared out by growing each county
    outwards a step at a time (so a long coastal strip is split between the counties it runs along)."""
    out = {k: polygonal(v.intersection(land)) for k, v in areas.items()}
    rest = polygonal(land.difference(unary_union(list(out.values()))))
    keys = list(out)
    grown = {k: [] for k in keys}
    base = {k: out[k].simplify(0.0005) for k in keys}
    for d in (0.003, 0.008, 0.02, 0.05, 0.12):
        if rest.is_empty:
            break
        for k in keys:
            take = rest.intersection(base[k].buffer(d))
            if not take.is_empty and take.area > 0:
                grown[k].append(take)
                rest = polygonal(rest.difference(take))
    print(f"  fitted to the coastline; land left unassigned: {round(rest.area * 7000, 2)} km²")
    return {k: polygonal(unary_union([out[k]] + grown[k])) for k in keys}


def joint_simplify(areas, tol=0.0002):
    """Lighter outlines for all the areas together, so neighbours keep exactly the same border (simplifying each county
    on its own left thin gaps and overlaps along every border, which turned into stray triangles)"""
    keys = list(areas)
    geo = [polygonal(g) for g in shapely.coverage_clean([polygonal(areas[k]) for k in keys], snapping_distance=0.00001)]
    return {k: polygonal(g) for k, g in zip(keys, shapely.coverage_simplify(geo, tol))}


def historic_gb():
    """The historic counties (Historic Counties Standard, Definition A: a detached part counts as part of the county
    it lies in, so no county is split into scattered pieces), full resolution; the coastline is fitted later"""
    z = DL / "hcbp_A_full.zip"
    fetch("https://county-borders.co.uk/UKDefinitionA_WG84_Full_Resolution.zip", z)
    g = gpd.read_file(f"zip://{z}!UKDefinitionA.shp").to_crs(4326)
    hist = {r["NAME"]: polygonal(r.geometry) for _, r in g.iterrows() if r["NAME"] in HISTORIC}  # NI comes from the Irish data
    missing = set(HISTORIC) - set(hist)
    assert not missing, missing
    return joint_simplify(hist)


def ireland():
    z = DL / "townlands_counties.geojson.zip"
    fetch("https://www.townlands.ie/static/downloads/counties.geojson.zip", z)
    g = gpd.read_file(f"zip://{z}!counties.geojson").to_crs(4326)
    out, irish = {}, {}
    for _, r in g.iterrows():
        n = r["NAME_TAG"]
        out[n] = shapely.make_valid(r.geometry)
        ga = r["NAME_GA"] or ""
        try:  # the file is UTF-8 but can come through read as Latin-1 ("ChorcaÃ­" for Chorcaí)
            ga = ga.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
        irish[n] = ga
    assert set(out) == set(IRELAND), set(out) ^ set(IRELAND)
    return out, irish


def ceremonial_gb():
    z = DL / "bdline_essh_gb.zip"
    fetch("https://api.os.uk/downloads/v1/products/BoundaryLine/downloads?area=GB&format=ESRI%C2%AE+Shapefile&redirect", z)
    names = zipfile.ZipFile(z).namelist()
    shp = next(n for n in names if re.search(r"ceremonial.*\.shp$", n, re.I))
    g = gpd.read_file(f"zip://{z}!{shp}").to_crs(4326)
    col = next(c for c in g.columns if c.lower() in ("name", "names"))
    out = {}
    for _, r in g.iterrows():
        n = OS_NAMES.get(r[col], r[col])
        out[n] = shapely.make_valid(r.geometry) if n not in out else shapely.make_valid(unary_union([out[n], r.geometry]))
    missing, extra = set(CEREMONIAL) - set(out), set(out) - set(CEREMONIAL)
    assert not missing and not extra, ("missing", missing, "unexpected", extra)
    return out


def crown_and_context():
    p = fetch("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_admin_0_countries.geojson",
              DL / "ne_10m_admin0.geojson")
    g = gpd.read_file(p)
    geom = lambda a3: g[g["ADM0_A3"] == a3].geometry.iloc[0]
    parts = list(geom("GGY").geoms)
    near = lambda lon, lat: [q for q in parts if q.centroid.distance(Point(lon, lat)) < 0.06]
    crown = {"D-IOM": geom("IMN"), "D-JER": geom("JEY"),
             "D-ALD": unary_union(near(-2.198, 49.717)), "D-SRK": unary_union(near(-2.366, 49.430)),
             "D-GGY": unary_union(near(-2.577, 49.463) + near(-2.451, 49.474))}  # Guernsey with Herm
    france = geom("FRA").intersection(box(-6, 47, 3.5, 51.3))
    return crown, {"T-FRA": france}


# ---------- one county set ----------
def build_set(kind, gb, irl, irish, crown, context):
    """features (id -> geometry) and the items list for one county set ("historic" or "ceremonial")"""
    items, geoms = [], {}
    table, wales, scotland = (HISTORIC, WALES_H, SCOTLAND_H) if kind == "historic" else (CEREMONIAL, WALES_C, SCOTLAND_C)
    shown = HISTORIC_SHOWN if kind == "historic" else CEREMONIAL_SHOWN
    alts = HISTORIC_ALT if kind == "historic" else CEREMONIAL_ALT
    prefix = "H-" if kind == "historic" else "C-"
    for n, towns in table.items():
        nation = "Wales" if n in wales else "Scotland" if n in scotland else "England"
        names = [shown.get(n, n)] + alts.get(n, [])
        if nation != "England" and kind == "historic" and n.endswith("shire"):
            names.append(re.sub(r"-?shire$", "", n))  # Argyll for Argyllshire, Inverness for Inverness-shire
        flag = n if kind == "historic" and n in REGISTERED else CEREMONIAL_FLAG.get(n) if kind == "ceremonial" else None
        iso = prefix + slug(n)
        geoms[iso] = gb[n]
        items.append({"iso": iso, "id": iso, "name": shown.get(n, n), "names": list(dict.fromkeys(names)), "capitals": towns,
                      "info": {"nation": nation, "kind": kind, "flagOf": flag}})
    for n, (towns, province) in IRELAND.items():
        iso = "I-" + slug(n)
        geoms[iso] = irl[n]
        items.append({"iso": iso, "id": iso, "name": n, "names": [n, f"County {n}", f"Co {n}"] + IRELAND_ALT.get(n, []),
                      "capitals": towns,
                      "info": {"nation": "Northern Ireland" if n in NI6 else "Republic of Ireland", "island": "Ireland",
                               "province": province, "irish": irish.get(n), "kind": "ireland", "flagOf": None}})
    for iso, (name, towns, alt) in CROWN.items():
        geoms[iso] = crown[iso]
        items.append({"iso": iso, "id": iso, "name": name, "names": [name] + alt, "capitals": towns,
                      "info": {"nation": "Crown Dependency", "cd": True, "kind": "crown", "flagOf": iso}})
    for it in items:
        it.update({"cont": ["Europe"], "car": False, "a2": it["iso"]})
        it["info"]["area"] = round(sq_km(geoms[it["iso"]]))
    geoms.update(context)
    return geoms, items


def absorb_enclaves(keys, geo):
    """Pieces of an area lying inside another area (the historic counties' detached parts, such as Dorset's in Devon
    or Cromartyshire's scattered fragments, and slivers left by the sources) join the area around them, so no county
    shows stray islands inside its neighbours. Islands at sea are kept."""
    def polygonal(g):
        g = shapely.make_valid(g)
        if g.geom_type in ("Polygon", "MultiPolygon"):
            return g
        return unary_union([p for p in getattr(g, "geoms", []) if p.geom_type in ("Polygon", "MultiPolygon")])
    parts = {k: [p for p in getattr(g, "geoms", [g]) if p.geom_type == "Polygon" and not p.is_empty] for k, g in zip(keys, geo)}
    outline = {k: unary_union([shapely.Polygon(p.exterior) for p in ps]) if ps else shapely.Polygon() for k, ps in parts.items()}
    tree_keys = [k for k in keys if not outline[k].is_empty]
    tree = shapely.STRtree([outline[k] for k in tree_keys])
    whole = dict(zip(keys, geo))

    def inland_host(k, p):
        """a piece with no coastline (its edge is all shared with other areas), where several counties meet: it
        joins the neighbour it shares the longest border with"""
        edge = p.boundary
        shared = {}
        for i in tree.query(p.buffer(1e-6)):
            j = tree_keys[i]
            if j != k:
                shared[j] = edge.intersection(whole[j].buffer(1e-6)).length
        if not shared or sum(shared.values()) < 0.97 * edge.length:
            return None  # touches the sea: a real island
        return max(shared, key=shared.get)
    moved = {k: [] for k in keys}
    keep = {}
    count = 0
    for k in keys:
        ps = parts[k]
        if len(ps) < 2:
            keep[k] = ps
            continue
        main = max(ps, key=lambda p: p.area)
        keep[k] = [main]
        for p in ps:
            if p is main:
                continue
            pt = p.representative_point()
            host = next((tree_keys[i] for i in tree.query(pt) if tree_keys[i] != k and outline[tree_keys[i]].contains(pt)), None) \
                or inland_host(k, p)
            if host:
                moved[host].append(p); count += 1
            else:
                keep[k].append(p)
    print(f"  enclaves joined to the area around them: {count}")
    return [polygonal(unary_union(keep[k] + moved[k])) if keep[k] or moved[k] else shapely.Polygon() for k in keys]


def shapes(geoms):
    """coverage-simplify all the areas together (neighbours keep matching borders), then work out the lines"""
    keys = list(geoms)
    # islets under about 0.5 km² are left out (thousands of them, too small to see or tap); the main part always stays
    def drop_small(g):
        polys = [p for p in getattr(g, "geoms", [g]) if p.geom_type == "Polygon"]
        if len(polys) <= 1:
            return g
        big = max(polys, key=lambda p: p.area)
        return unary_union([p for p in polys if p is big or sq_km(p) >= 0.5])
    def polygonal(g):  # make_valid can leave stray lines and points: keep the area
        g = shapely.make_valid(g)
        if g.geom_type in ("Polygon", "MultiPolygon"):
            return g
        return unary_union([p for p in getattr(g, "geoms", []) if p.geom_type in ("Polygon", "MultiPolygon")])
    geo = [polygonal(drop_small(polygonal(geoms[k]))) for k in keys]
    # the sources don't always meet exactly (the Ordnance Survey's ceremonial counties have thousands of tiny gaps and
    # overlaps): close gaps under about 50 m and make every shared edge identical, so borders are drawn once
    geo = [polygonal(g) for g in shapely.coverage_clean(geo, gap_width=0.0005, snapping_distance=0.00001)]
    for _ in range(3):  # again, for detached parts that sat inside another county's detached part
        geo = absorb_enclaves(keys, geo)
    arr = shapely.coverage_simplify(geo, SIMPLIFY)
    # snapped to a 0.001° grid (about 100 m) with valid output: plain rounding made some outlines cross themselves,
    # which drew as stray patches. Shared edges snap the same way, so neighbours still match.
    arr = [polygonal(shapely.set_precision(polygonal(g), 0.001)) for g in arr]
    arr = absorb_enclaves(keys, arr)  # simplifying can leave a detached piece newly enclosed
    simp = {k: polygonal(g) for k, g in zip(keys, arr)}
    borders = []
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            A, B = simp[a].bounds, simp[b].bounds
            if A[0] > B[2] or B[0] > A[2] or A[1] > B[3] or B[1] > A[3]:
                continue
            borders += lines_only(simp[a].boundary.intersection(simp[b].boundary))
    bu = unary_union(borders)
    coast = lines_only(unary_union([g.boundary for g in simp.values()]).difference(bu.buffer(1e-7)))
    merged = lambda ls: linemerge(ls) if ls else MultiLineString([])
    feats = [{"type": "Feature", "id": k, "geometry": rounded(g)} for k, g in simp.items() if not g.is_empty]
    return {"type": "FeatureCollection", "features": feats, "borders": rounded(merged(borders)), "coast": rounded(merged(coast))}


def nation_borders(fc, items):
    """Adds "nations": the borders between England, Scotland and Wales, and between Northern Ireland and the Republic
    (drawn bolder on the map), taken from the finished county outlines so they sit exactly on the county borders"""
    from shapely.geometry import shape as to_shape
    nation = {it["iso"]: it["info"]["nation"] for it in items if not it["info"].get("cd")}
    geo = {f["id"]: to_shape(f["geometry"]) for f in fc["features"] if f["id"] in nation}
    keys = list(geo)
    lines = []
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if nation[a] == nation[b]:
                continue
            A, B = geo[a].bounds, geo[b].bounds
            if A[0] > B[2] or B[0] > A[2] or A[1] > B[3] or B[1] > A[3]:
                continue
            lines += lines_only(geo[a].boundary.intersection(geo[b].boundary))
    fc["nations"] = rounded(linemerge(lines) if lines else MultiLineString([]))
    return fc


def town_coords(items, geoms):
    z = fetch("https://download.geonames.org/export/dump/cities500.zip", DL / "cities500.zip")
    rows = [l.split("\t") for l in zipfile.ZipFile(z).open("cities500.txt").read().decode("utf8").splitlines()]
    places = [r for r in rows if r[8] in ("GB", "IE", "IM", "JE", "GG")]
    norm = lambda s: re.sub(r"[^a-z]", "", unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower().replace("saint", "st"))
    index = {}
    for r in places:
        for nm in [r[1], r[2]] + r[3].split(","):
            if nm:
                index.setdefault(norm(nm), []).append(r)
    missing = []
    for it in items:
        town = it["capitals"][0]
        g = geoms[it["iso"]]
        if town in TOWN_LL:
            it["capLL"] = [list(TOWN_LL[town])]
            continue
        cands = index.get(norm(town), [])
        if not cands:
            missing.append(f"{it['name']}: {town}")
            continue
        # the one inside (or nearest to) the county, the biggest if several
        best = min(cands, key=lambda r: (round(g.distance(Point(float(r[5]), float(r[4]))), 2), -int(r[14] or 0)))
        it["capLL"] = [[round(float(best[5]), 3), round(float(best[4]), 3)]]
    if missing:
        print("county towns not found:", missing)


def flags(items):
    out = ROOT / "data" / "flags" / "uk"
    out.mkdir(parents=True, exist_ok=True)
    wanted = {}
    for it in items:
        f = it["info"]["flagOf"]
        if not f:
            continue
        url = CROWN_FLAGS[f] if f in CROWN_FLAGS else "https://historiccountiestrust.co.uk/images/" + urllib.parse.quote(f.replace(" ", "_")) + ".png"
        wanted[slug(f)] = url
        it["flagKey"] = "uk/" + slug(f)
    for key, url in wanted.items():
        p = out / f"{key}.webp"
        if p.exists():
            continue
        for attempt in range(4):
            try:
                data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
                break
            except Exception as e:
                print("retrying", key, e)
                time.sleep(5 * (attempt + 1))
        else:
            raise SystemExit(f"could not download the flag {key}")
        im = Image.open(io.BytesIO(data)).convert("RGB")
        if im.width > 640:
            im = im.resize((640, round(im.height * 640 / im.width)), Image.LANCZOS)
        im.save(p, "WEBP", quality=88)
        time.sleep(0.5)
    print("flags:", len(wanted), "in", out)


def main():
    irl, irish = ireland()
    crown, context = crown_and_context()
    cer = joint_simplify(ceremonial_gb())
    land = gb_land(unary_union(list(cer.values())))
    for kind, gb in (("historic", fit_to_land(historic_gb(), land)), ("ceremonial", fit_to_land(cer, land))):
        geoms, items = build_set(kind, gb, irl, irish, crown, context)
        town_coords(items, geoms)
        flags(items)
        for it in items:
            it["info"].pop("flagOf", None)
            it["info"]["flag"] = "flagKey" in it
        nations = ["England", "Scotland", "Wales", "Northern Ireland", "Republic of Ireland", "Crown Dependency"]
        by_area = sorted(items, key=lambda c: -c["info"]["area"])
        for it in items:
            it["info"]["areaRank"] = by_area.index(it) + 1
        (ROOT / "data" / f"uk-{kind}.json").write_text(json.dumps(nation_borders(shapes(geoms), items), separators=(",", ":")), encoding="utf8")
        add_facts(items)
        items.sort(key=lambda c: (nations.index(c["info"]["nation"]), c["name"]))
        (ROOT / "data" / f"counties-{kind}.json").write_text(json.dumps(items, ensure_ascii=False, indent=0), encoding="utf8")
        print(f"{kind}: {len(items)} areas, {sum(1 for i in items if i['info']['flag'])} with flags")
    build_nations()


def add_facts(items):
    """the Learning card facts (tools/uk_facts.py) on each county, by its id"""
    sys.path.insert(0, str(ROOT / "tools"))
    import uk_facts as F
    by_id = {}
    by_id.update({"H-" + slug(k): v for k, v in F.HISTORIC.items()})
    by_id.update({"I-" + slug(k): v for k, v in F.IRELAND.items()})
    by_id.update(F.CROWN)
    by_id.update({"C-" + slug(k): F.ceremonial(k) for k in CEREMONIAL})
    n = 0
    for it in items:
        f = by_id.get(it["iso"])
        if f:
            it["info"]["facts"] = {k: v for k, v in f.items() if v}
            n += 1
    return n


def apply_facts():
    """adds the facts to the county files already built (no need to rebuild the shapes)"""
    for name in ("counties-historic.json", "counties-ceremonial.json", "uk-nations-info.json"):
        p = ROOT / "data" / name
        items = json.loads(p.read_text(encoding="utf8"))
        n = add_facts(items)
        p.write_text(json.dumps(items, ensure_ascii=False, indent=0), encoding="utf8")
        print(f"{name}: facts for {n} of {len(items)}")


# ---------- the UK and Ireland's countries, for the Learning map's first view (counties come after "Focus on ...") ----------
# (name, capital, largest city if not the capital, population, census/estimate, area km², patron saint (day), languages,
#  highest point (name, m), national flower or emblem, history, how it's governed, flagcdn code)
NATIONS = {
    "N-ENG": ("England", "London", "", 56490048, "2021 census", 130279, "St George (23 April)", "English",
              ("Scafell Pike", 978), "Tudor rose", "Kingdom of England from 927; united with Scotland in 1707",
              "UK Parliament (no separate parliament of its own)", "gb-eng"),
    "N-SCO": ("Scotland", "Edinburgh", "Glasgow", 5439842, "2022 census", 80231, "St Andrew (30 November)",
              "English, Scots, Scottish Gaelic", ("Ben Nevis", 1345), "Thistle",
              "Kingdom of Scotland from 843; united with England in 1707", "Scottish Parliament (Holyrood), since 1999", "gb-sct"),
    "N-WAL": ("Wales", "Cardiff", "", 3107494, "2021 census", 20779, "St David (1 March)", "Welsh, English",
              ("Yr Wyddfa (Snowdon)", 1085), "Daffodil (and the leek)",
              "Welsh kingdoms and principalities; joined to England by the Laws in Wales Acts 1535–1542",
              "Senedd (Welsh Parliament), since 1999", "gb-wls"),
    "N-NIR": ("Northern Ireland", "Belfast", "", 1903175, "2021 census", 14130, "St Patrick (17 March)",
              "English, Irish, Ulster Scots", ("Slieve Donard", 850), "Flax (shamrock also used)",
              "Formed in 1921, when Ireland was partitioned", "Northern Ireland Assembly (Stormont), since 1998", "gb"),
    "N-IRL": ("Republic of Ireland", "Dublin", "", 5149139, "2022 census", 70273, "St Patrick (17 March)", "Irish, English",
              ("Carrauntoohil", 1039), "Shamrock", "Irish Free State from 1922; a republic since 1949",
              "Oireachtas (parliament) in Dublin; an independent country in the EU", None),
}
NATION_OF = {"N-ENG": "England", "N-SCO": "Scotland", "N-WAL": "Wales", "N-NIR": "Northern Ireland", "N-IRL": "Republic of Ireland"}


def build_nations():
    """data/uk-nations.json (the five countries, the Crown Dependencies and France, merged from the historic county
    shapes so coast and borders match them exactly) and data/uk-nations-info.json (the countries' facts)"""
    from shapely.geometry import shape as to_shape
    fc = json.loads((ROOT / "data" / "uk-historic.json").read_text(encoding="utf8"))
    hist = json.loads((ROOT / "data" / "counties-historic.json").read_text(encoding="utf8"))
    cer = json.loads((ROOT / "data" / "counties-ceremonial.json").read_text(encoding="utf8"))
    nation = {c["iso"]: c["info"]["nation"] for c in hist}
    geo = {f["id"]: to_shape(f["geometry"]) for f in fc["features"]}
    areas = {iso: polygonal(unary_union([g for k, g in geo.items() if nation.get(k) == n])) for iso, n in NATION_OF.items()}
    for k, g in geo.items():  # the Crown Dependencies and France stay as they are
        if k.startswith("D-") or k.startswith("T-"):
            areas[k] = g
    keys = list(areas)
    borders = []
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            borders += lines_only(areas[a].boundary.intersection(areas[b].boundary))
    bu = unary_union(borders)
    coast = lines_only(unary_union([g.boundary for g in areas.values()]).difference(bu.buffer(1e-7)))
    merged = lambda ls: linemerge(ls) if ls else MultiLineString([])
    out = {"type": "FeatureCollection", "features": [{"type": "Feature", "id": k, "geometry": rounded(g)} for k, g in areas.items()],
           "borders": rounded(merged(borders)), "coast": rounded(merged(coast))}
    (ROOT / "data" / "uk-nations.json").write_text(json.dumps(out, separators=(",", ":")), encoding="utf8")
    count = lambda items, n: sum(1 for c in items if c["info"]["nation"] == n)
    items = []
    for iso, (name, cap, city, pop, popYear, area, saint, langs, high, flower, history, gov, flag) in NATIONS.items():
        n = NATION_OF[iso]
        it = {"iso": iso, "id": iso, "name": name, "names": [name], "capitals": [cap], "cont": ["Europe"], "car": False, "a2": iso,
              "info": {"nation": n, "kind": "nation", "city": city, "pop": pop, "popYear": popYear, "area": area, "saint": saint,
                       "langs": langs, "high": high, "flower": flower, "history": history, "gov": gov,
                       "historic": count(hist, n), "ceremonial": count(cer, n), "flag": True},
              "flagKey": "uk/" + iso}
        items.append(it)
        p = ROOT / "data" / "flags" / "uk" / f"{iso}.webp"
        if not p.exists():
            if flag:
                data = urllib.request.urlopen(urllib.request.Request(f"https://flagcdn.com/w640/{flag}.webp", headers=UA), timeout=60).read()
                Image.open(io.BytesIO(data)).convert("RGB").save(p, "WEBP", quality=88)
            else:
                Image.open(ROOT / "data" / "flags" / "IRL.webp").convert("RGB").save(p, "WEBP", quality=88)
    items += [c for c in hist if c["info"].get("cd")]  # the Crown Dependencies keep their county-style cards
    (ROOT / "data" / "uk-nations-info.json").write_text(json.dumps(items, ensure_ascii=False, indent=0), encoding="utf8")
    print("nations:", len(items), "areas")


if __name__ == "__main__":
    if sys.argv[1:] == ["nations"]:
        build_nations()  # just the countries view, from the county files already built
    elif sys.argv[1:] == ["facts"]:
        apply_facts()  # just the Learning card facts, into the county files already built
    else:
        main()
