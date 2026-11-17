"""Builds Russia's country map (Russia_plan.md): its 83 federal subjects.

  data/ru-regions.json  the 83 shapes (Natural Earth 1:10m admin-1; Chukotka joined across the 180° line, so longitudes
                        run past 180 in the far east), every country around as grey context, and Crimea and Sevastopol
                        grey with Ukraine. Lines: "borders", "coast", "disputed" (Russia's border with the Donetsk and
                        Luhansk regions, and the sea line between the southern Kurils and Japan).
  data/ru-parts.json    names (with Russian in Cyrillic), capitals, kind, federal district and Learning facts
                        (tools/ru_facts.py); populations from the 2021 census, areas from Rosreestr (via Wikipedia)
  data/flags/ru/        every subject's flag (Wikimedia Commons, 640 px wide)

  data/ru-history.json  the expansion timeline: approximate pieces (today's oblasts and countries) with the years Russia
                        held them, and a caption for each stop

Run from the repo root:  python tools/build_ru.py   (or  python tools/build_ru.py history  for the timeline only)
"""
import io
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request

import geopandas as gpd
import shapely
from PIL import Image
from shapely.affinity import translate
from shapely.geometry import mapping, LineString, MultiLineString
from shapely.ops import unary_union, linemerge

ROOT = pathlib.Path(__file__).resolve().parent.parent
NE = ROOT / "tools" / "downloads" / "ne10"
SIMPLIFY = 0.03  # degrees (about 2–3 km): Russia spans 170° of longitude
UA = {"User-Agent": "GaiaQuestBuild/1.0 (map quiz data build)"}

# ISO 3166-2:RU code -> (shown name, kind, federal district, capitals (the first is shown; the rest are also accepted),
#                        population (2021 census), area km²)
PARTS = {
    "AD": ("Adygea", "Republic", "Southern", ["Maykop", "Maikop"], 496934, 7792),
    "AL": ("Altai Republic", "Republic", "Siberian", ["Gorno-Altaysk", "Gorno-Altaisk"], 210924, 92903),
    "BA": ("Bashkortostan", "Republic", "Volga", ["Ufa"], 4091423, 142947),
    "BU": ("Buryatia", "Republic", "Far Eastern", ["Ulan-Ude"], 978588, 351334),
    "CE": ("Chechnya", "Republic", "North Caucasian", ["Grozny"], 1510824, 16165),
    "CU": ("Chuvashia", "Republic", "Volga", ["Cheboksary"], 1186909, 18343),
    "DA": ("Dagestan", "Republic", "North Caucasian", ["Makhachkala"], 3182054, 50270),
    "IN": ("Ingushetia", "Republic", "North Caucasian", ["Magas"], 509541, 3628),
    "KB": ("Kabardino-Balkaria", "Republic", "North Caucasian", ["Nalchik"], 904200, 12470),
    "KL": ("Kalmykia", "Republic", "Southern", ["Elista"], 267133, 74731),
    "KC": ("Karachay-Cherkessia", "Republic", "North Caucasian", ["Cherkessk"], 469865, 14277),
    "KR": ("Karelia", "Republic", "Northwestern", ["Petrozavodsk"], 533121, 180520),
    "KK": ("Khakassia", "Republic", "Siberian", ["Abakan"], 534795, 61569),
    "KO": ("Komi", "Republic", "Northwestern", ["Syktyvkar"], 737853, 416774),
    "ME": ("Mari El", "Republic", "Volga", ["Yoshkar-Ola"], 677097, 23375),
    "MO": ("Mordovia", "Republic", "Volga", ["Saransk"], 783552, 26128),
    "SE": ("North Ossetia–Alania", "Republic", "North Caucasian", ["Vladikavkaz"], 687357, 7987),
    "SA": ("Sakha (Yakutia)", "Republic", "Far Eastern", ["Yakutsk"], 995686, 3083523),
    "TA": ("Tatarstan", "Republic", "Volga", ["Kazan"], 4004809, 67847),
    "TY": ("Tuva", "Republic", "Siberian", ["Kyzyl"], 336651, 168604),
    "UD": ("Udmurtia", "Republic", "Volga", ["Izhevsk"], 1452914, 42061),
    "ALT": ("Altai Krai", "Krai", "Siberian", ["Barnaul"], 2163693, 167996),
    "KAM": ("Kamchatka Krai", "Krai", "Far Eastern", ["Petropavlovsk-Kamchatsky"], 291705, 464275),
    "KHA": ("Khabarovsk Krai", "Krai", "Far Eastern", ["Khabarovsk"], 1292944, 787633),
    "KDA": ("Krasnodar Krai", "Krai", "Southern", ["Krasnodar"], 5838273, 75485),
    "KYA": ("Krasnoyarsk Krai", "Krai", "Siberian", ["Krasnoyarsk"], 2856971, 2366797),
    "PER": ("Perm Krai", "Krai", "Volga", ["Perm"], 2532405, 160236),
    "PRI": ("Primorsky Krai", "Krai", "Far Eastern", ["Vladivostok"], 1845165, 164673),
    "STA": ("Stavropol Krai", "Krai", "North Caucasian", ["Stavropol"], 2907593, 66160),
    "ZAB": ("Zabaykalsky Krai", "Krai", "Far Eastern", ["Chita"], 1004125, 431892),
    "AMU": ("Amur Oblast", "Oblast", "Far Eastern", ["Blagoveshchensk"], 766912, 361908),
    "ARK": ("Arkhangelsk Oblast", "Oblast", "Northwestern", ["Arkhangelsk", "Archangel"], 978873, 413103),
    "AST": ("Astrakhan Oblast", "Oblast", "Southern", ["Astrakhan"], 960142, 49024),
    "BEL": ("Belgorod Oblast", "Oblast", "Central", ["Belgorod"], 1540486, 27134),
    "BRY": ("Bryansk Oblast", "Oblast", "Central", ["Bryansk"], 1169161, 34857),
    "CHE": ("Chelyabinsk Oblast", "Oblast", "Ural", ["Chelyabinsk"], 3431224, 88529),
    "IRK": ("Irkutsk Oblast", "Oblast", "Siberian", ["Irkutsk"], 2370102, 774846),
    "IVA": ("Ivanovo Oblast", "Oblast", "Central", ["Ivanovo"], 927828, 21437),
    "KGD": ("Kaliningrad Oblast", "Oblast", "Northwestern", ["Kaliningrad", "Königsberg", "Konigsberg"], 1029966, 15125),
    "KLU": ("Kaluga Oblast", "Oblast", "Central", ["Kaluga"], 1069904, 29777),
    "KEM": ("Kemerovo Oblast", "Oblast", "Siberian", ["Kemerovo"], 2600923, 95725),
    "KIR": ("Kirov Oblast", "Oblast", "Volga", ["Kirov", "Vyatka"], 1153680, 120374),
    "KOS": ("Kostroma Oblast", "Oblast", "Central", ["Kostroma"], 580976, 60211),
    "KGN": ("Kurgan Oblast", "Oblast", "Ural", ["Kurgan"], 776661, 71488),
    "KRS": ("Kursk Oblast", "Oblast", "Central", ["Kursk"], 1082458, 29997),
    "LEN": ("Leningrad Oblast", "Oblast", "Northwestern", ["Gatchina", "Saint Petersburg", "St Petersburg", "St. Petersburg"], 2000997, 83908),
    "LIP": ("Lipetsk Oblast", "Oblast", "Central", ["Lipetsk"], 1143224, 24047),
    "MAG": ("Magadan Oblast", "Oblast", "Far Eastern", ["Magadan"], 136085, 462464),
    "MOS": ("Moscow Oblast", "Oblast", "Central", ["Krasnogorsk", "Moscow"], 8524665, 44329),
    "MUR": ("Murmansk Oblast", "Oblast", "Northwestern", ["Murmansk"], 667744, 144902),
    "NIZ": ("Nizhny Novgorod Oblast", "Oblast", "Volga", ["Nizhny Novgorod", "Nizhniy Novgorod", "Gorky"], 3119115, 76624),
    "NGR": ("Novgorod Oblast", "Oblast", "Northwestern", ["Veliky Novgorod", "Novgorod"], 583387, 54501),
    "NVS": ("Novosibirsk Oblast", "Oblast", "Siberian", ["Novosibirsk"], 2797176, 177756),
    "OMS": ("Omsk Oblast", "Oblast", "Siberian", ["Omsk"], 1858798, 141140),
    "ORE": ("Orenburg Oblast", "Oblast", "Volga", ["Orenburg"], 1862767, 123702),
    "ORL": ("Oryol Oblast", "Oblast", "Central", ["Oryol", "Orel"], 713374, 24652),
    "PNZ": ("Penza Oblast", "Oblast", "Volga", ["Penza"], 1266348, 43352),
    "PSK": ("Pskov Oblast", "Oblast", "Northwestern", ["Pskov"], 599084, 55399),
    "ROS": ("Rostov Oblast", "Oblast", "Southern", ["Rostov-on-Don", "Rostov-na-Donu", "Rostov"], 4200729, 100967),
    "RYA": ("Ryazan Oblast", "Oblast", "Central", ["Ryazan"], 1102810, 39605),
    "SAK": ("Sakhalin Oblast", "Oblast", "Far Eastern", ["Yuzhno-Sakhalinsk"], 466609, 87101),
    "SAM": ("Samara Oblast", "Oblast", "Volga", ["Samara", "Kuybyshev", "Kuibyshev"], 3172925, 53565),
    "SAR": ("Saratov Oblast", "Oblast", "Volga", ["Saratov"], 2442575, 101240),
    "SMO": ("Smolensk Oblast", "Oblast", "Central", ["Smolensk"], 888421, 49779),
    "SVE": ("Sverdlovsk Oblast", "Oblast", "Ural", ["Yekaterinburg", "Ekaterinburg", "Sverdlovsk"], 4268998, 194307),
    "TAM": ("Tambov Oblast", "Oblast", "Central", ["Tambov"], 982991, 34462),
    "TOM": ("Tomsk Oblast", "Oblast", "Siberian", ["Tomsk"], 1062666, 314391),
    "TUL": ("Tula Oblast", "Oblast", "Central", ["Tula"], 1501214, 25679),
    "TVE": ("Tver Oblast", "Oblast", "Central", ["Tver", "Kalinin"], 1230171, 84201),
    "TYU": ("Tyumen Oblast", "Oblast", "Ural", ["Tyumen"], 1601940, 160122),
    "ULY": ("Ulyanovsk Oblast", "Oblast", "Volga", ["Ulyanovsk", "Simbirsk"], 1196745, 37181),
    "VLA": ("Vladimir Oblast", "Oblast", "Central", ["Vladimir"], 1348134, 29084),
    "VGG": ("Volgograd Oblast", "Oblast", "Southern", ["Volgograd", "Stalingrad"], 2500781, 112877),
    "VLG": ("Vologda Oblast", "Oblast", "Northwestern", ["Vologda"], 1142827, 144527),
    "VOR": ("Voronezh Oblast", "Oblast", "Central", ["Voronezh"], 2308792, 52216),
    "YAR": ("Yaroslavl Oblast", "Oblast", "Central", ["Yaroslavl"], 1209811, 36177),
    "MOW": ("Moscow", "Federal city", "Central", ["Moscow"], 13010112, 2561),
    "SPE": ("Saint Petersburg", "Federal city", "Northwestern", ["Saint Petersburg", "St Petersburg", "St. Petersburg", "Leningrad"], 5601911, 1403),
    "YEV": ("Jewish Autonomous Oblast", "Autonomous oblast", "Far Eastern", ["Birobidzhan"], 150453, 36271),
    "CHU": ("Chukotka", "Autonomous okrug", "Far Eastern", ["Anadyr"], 47490, 721481),
    "KHM": ("Khanty-Mansi", "Autonomous okrug", "Ural", ["Khanty-Mansiysk"], 1711480, 534801),
    "NEN": ("Nenets", "Autonomous okrug", "Northwestern", ["Naryan-Mar"], 41434, 176810),
    "YAN": ("Yamalo-Nenets", "Autonomous okrug", "Ural", ["Salekhard"], 510490, 769250),
}
FLAGS = {  # Wikimedia Commons file names

    "AD": "Flag of Adygea.svg",
    "AL": "Flag of Altai Republic.svg",
    "BA": "Flag of Bashkortostan.svg",
    "BU": "Flag of Buryatia.svg",
    "CE": "Flag of Chechnya.svg",
    "CU": "Flag of Chuvashia.svg",
    "DA": "Flag of Dagestan.svg",
    "IN": "Flag of Ingushetia.svg",
    "KB": "Flag of Kabardino-Balkaria.svg",
    "KL": "Flag of Kalmykia.svg",
    "KC": "Flag of Karachay-Cherkessia.svg",
    "KR": "Flag of Karelia.svg",
    "KK": "Flag of Khakassia.svg",
    "KO": "Flag of Komi.svg",
    "ME": "Flag of Mari El.svg",
    "MO": "Flag of Mordovia.svg",
    "SE": "Flag of North Ossetia.svg",
    "SA": "Flag of Sakha.svg",
    "TA": "Flag of Tatarstan.svg",
    "TY": "Flag of Tuva.svg",
    "UD": "Flag of Udmurtia.svg",
    "ALT": "Flag of Altai Krai.svg",
    "KAM": "Flag of Kamchatka Krai.svg",
    "KHA": "Flag of Khabarovsk Krai.svg",
    "KDA": "Flag of Krasnodar Krai.svg",
    "KYA": "Flag of Krasnoyarsk Krai.svg",
    "PER": "Flag of Perm Krai.svg",
    "PRI": "Flag of Primorsky Krai.svg",
    "STA": "Flag of Stavropol Krai.svg",
    "ZAB": "Flag of Zabaykalsky Krai.svg",
    "AMU": "Flag of Amur Oblast.svg",
    "ARK": "Flag of Arkhangelsk Oblast.svg",
    "AST": "Flag of Astrakhan Oblast.svg",
    "BEL": "Flag of Belgorod Oblast (Dark color).svg",
    "BRY": "Flag of Bryansk Oblast (large).svg",
    "CHE": "Flag of Chelyabinsk Oblast.svg",
    "IRK": "Flag of Irkutsk Oblast.svg",
    "IVA": "Flag of Ivanovo Oblast.svg",
    "KGD": "Flag of Kaliningrad Oblast.svg",
    "KLU": "Flag of Kaluga Oblast.svg",
    "KEM": "Flag of Kemerovo oblast.svg",
    "KIR": "Flag of Kirov Region.svg",
    "KOS": "Flag of Kostroma Oblast.svg",
    "KGN": "Flag of Kurgan Oblast.svg",
    "KRS": "Flag of Kursk Oblast (large fix).svg",
    "LEN": "Flag of Leningrad Oblast.svg",
    "LIP": "Flag of Lipetsk Oblast.svg",
    "MAG": "Flag of Magadan Oblast.svg",
    "MOS": "Flag of Moscow Oblast (large).svg",
    "MUR": "Flag of Murmansk Oblast.svg",
    "NIZ": "Flag of Nizhny Novgorod Region.svg",
    "NGR": "Flag of Novgorod Oblast.svg",
    "NVS": "Flag of Novosibirsk Oblast.svg",
    "OMS": "Flag of Omsk Oblast.svg",
    "ORE": "Flag of Orenburg Oblast.svg",
    "ORL": "Flag of Oryol Oblast.svg",
    "PNZ": "Flag of Penza Oblast.svg",
    "PSK": "Flag of Pskov Oblast.svg",
    "ROS": "Flag of Rostov Oblast.svg",
    "RYA": "Flag of Ryazan Oblast.svg",
    "SAK": "Flag of Sakhalin Oblast.svg",
    "SAM": "Flag of Samara Oblast.svg",
    "SAR": "Flag of Saratov Oblast.svg",
    "SMO": "Flag of Smolensk oblast.svg",
    "SVE": "Flag of Sverdlovsk Oblast.svg",
    "TAM": "Flag of Tambov Oblast.svg",
    "TOM": "Flag of Tomsk Oblast.svg",
    "TUL": "Flag of Tula Oblast.svg",
    "TVE": "Flag of Tver Oblast.svg",
    "TYU": "Flag of Tyumen Oblast (large).svg",
    "ULY": "Флаг Ульяновской области (2013).svg",
    "VLA": "Flag of Vladimirskaya Oblast.svg",
    "VGG": "Flag of Volgograd Oblast.svg",
    "VLG": "Flag of Vologda oblast.svg",
    "VOR": "Flag of Voronezh Oblast.svg",
    "YAR": "Flag of Yaroslavl Oblast.svg",
    "MOW": "Flag of Moscow, Russia.svg",
    "SPE": "Flag of Saint Petersburg.svg",
    "YEV": "Flag of the Jewish Autonomous Oblast.svg",
    "CHU": "Flag of Chukotka.svg",
    "KHM": "Flag of Yugra.svg",
    "NEN": "Flag of Nenets Autonomous District.svg",
    "YAN": "Flag of Yamal-Nenets Autonomous District.svg",
}


# Natural Earth swaps Moscow city and Moscow Oblast's codes
NE_CODE = {"MOS": "MOW", "MOW": "MOS"}
# extra names accepted when typing (the kind word is optional anyway: see NAMES below)
ALT = {
    "SA": ["Sakha", "Yakutia", "Sakha Republic"], "BA": ["Bashkiria"], "CU": ["Chuvash Republic", "Chuvashiya"],
    "KHM": ["Yugra", "Khanty-Mansi Autonomous Okrug", "Khanty-Mansiysk"], "SE": ["North Ossetia", "Alania", "North Ossetia-Alania"],
    "PRI": ["Primorye", "Primorsky", "Primorski"], "ZAB": ["Zabaikalsky Krai", "Trans-Baikal", "Transbaikal", "Zabaykalsky", "Zabaikalsky"],
    "KEM": ["Kuzbass"], "AL": ["Altai Republic", "Gorno-Altai"], "ALT": ["Altai Krai"], "KO": ["Komi Republic"],
    "KR": ["Republic of Karelia"], "TY": ["Tyva"], "UD": ["Udmurt Republic"], "KL": ["Kalmyk Republic"], "ME": ["Mari"],
    "KB": ["Kabardino Balkaria"], "KC": ["Karachay Cherkessia", "Karachayevo-Cherkessia"], "IN": ["Ingush Republic"],
    "CE": ["Chechen Republic", "Chechnia"], "BU": ["Buryat Republic"], "KK": ["Khakasia"], "AD": ["Adygeya"],
    "YEV": ["Jewish Autonomous Region", "Jewish Oblast", "Birobidzhan"], "CHU": ["Chukotka Autonomous Okrug", "Chukchi"],
    "NEN": ["Nenets Autonomous Okrug"], "YAN": ["Yamalo-Nenets Autonomous Okrug", "Yamal-Nenets", "Yamal"],
    "SPE": ["St Petersburg", "St. Petersburg", "Petersburg", "Leningrad", "St Pete"], "MOW": ["Moscow City", "Moskva"],
    "NIZ": ["Nizhniy Novgorod Oblast", "Nizhegorod Oblast"], "NGR": ["Veliky Novgorod Oblast"], "ORL": ["Orel Oblast"],
    "ARK": ["Archangel Oblast"], "KAM": ["Kamchatka"], "ROS": ["Rostov-on-Don Oblast"],
}
# never accept one of these as a typo of the other
NOT_TYPO = {"NGR": ["Nizhny Novgorod"], "AL": ["Altai Krai"], "ALT": ["Altai Republic"], "NEN": ["Yamalo-Nenets"],
            "KUR": [], "KRS": ["Kirov", "Kurgan"], "KGN": ["Kursk"], "KIR": ["Kursk"], "OMS": ["Tomsk"], "TOM": ["Omsk"],
            "MOW": ["Moscow Oblast"], "MOS": ["Moscow"], "TAM": ["Tambov"], "PNZ": ["Perm"], "PER": ["Penza"]}
DISPUTED_UA = {"Donets'k", "Luhans'k"}  # annexed by Russia in 2022 (with Zaporizhzhia and Kherson, which don't border it)
# the sea line between the southern Kurils (Russia, claimed by Japan) and Hokkaido: approximate, drawn dotted
KURIL_LINE = [(145.05, 44.75), (145.32, 44.25), (145.45, 43.9), (145.62, 43.55), (145.85, 43.33), (146.4, 43.15)]
# capitals the gazetteer spells differently, or lacks (Magas, built in the 1990s)
CAP_SEARCH = {"Arkhangelsk": "Arkhangel'sk", "Veliky Novgorod": "Velikiy Novgorod", "Oryol": "Orel"}
CAP_LL = {"Magas": [44.81, 43.17], "Arkhangelsk": [40.54, 64.54]}
WINDOW = shapely.box(5, 12, 200, 84)  # Kaliningrad in the west, Chukotka (past 180°) in the east; south far enough for a tall screen


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


def east(g):
    """Pieces in the western hemisphere (Chukotka's tip, Alaska) moved 360° east, so they join up across 180°."""
    g = polygonal(g)
    return unary_union([translate(p, 360) if p.bounds[2] <= -100 + 1e-9 or p.bounds[2] < 0 else p for p in getattr(g, "geoms", [g])])


def rounded(geom, nd=3):
    def r(c):
        return [round(c[0], nd), round(c[1], nd)] if isinstance(c[0], (int, float)) else [r(x) for x in c]
    m = mapping(geom)
    return {"type": m["type"], "coordinates": r(json.loads(json.dumps(m["coordinates"])))}


def shapes():
    a1 = gpd.read_file(NE / "ne_10m_admin_1_states_provinces.geojson")
    a0 = gpd.read_file(NE / "ne_10m_admin_0_countries.geojson")
    areas, crimea, sliver = {}, [], None
    for _, r in a1[a1["adm0_a3"] == "RUS"].iterrows():
        iso = r["iso_3166_2"]
        if iso in ("UA-40", "UA-43"):
            crimea.append(r.geometry)  # Crimea and Sevastopol: Ukraine on this map (Russia_plan.md)
            continue
        if iso == "RU-X01~":
            sliver = east(r.geometry)  # a tiny unnamed piece in the Urals: joined to its neighbour below
            continue
        code = iso[3:]
        code = NE_CODE.get(code, code)
        assert code in PARTS, iso
        areas["RU-" + code] = east(r.geometry)
    assert len(areas) == 83, len(areas)
    if sliver is not None:
        k = max(areas, key=lambda k: areas[k].boundary.intersection(sliver.buffer(1e-6)).length)
        areas[k] = polygonal(unary_union([areas[k], sliver]))
    russia = unary_union(list(areas.values()))
    names = {}
    for _, r in a0[a0.intersects(shapely.box(-180, WINDOW.bounds[1], 180, 84))].iterrows():
        a3 = r["ADM0_A3"]
        if a3 == "RUS":
            continue
        g = east(r.geometry)
        if a3 == "UKR":
            g = unary_union([g] + [polygonal(c) for c in crimea])
        g = polygonal(g.intersection(WINDOW).difference(russia))
        g = unary_union([p for p in getattr(g, "geoms", [g]) if p.area > 0.03])
        if not g.is_empty:
            areas["T-" + a3] = polygonal(g)
            names["T-" + a3] = r["NAME"]
    keys = list(areas)
    geo = shapely.coverage_clean([areas[k] for k in keys], gap_width=0.002, snapping_distance=0.0001)
    geo = shapely.coverage_simplify([polygonal(g) for g in geo], SIMPLIFY)
    geo = {k: polygonal(shapely.set_precision(polygonal(g), 0.001)) for k, g in zip(keys, geo)}
    annexed = unary_union([polygonal(r.geometry) for _, r in a1[a1["adm0_a3"] == "UKR"].iterrows()
                           if r["name"] in DISPUTED_UA]).buffer(0.05)
    borders, disputed = [], [LineString(KURIL_LINE)]
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            A, B = geo[a].bounds, geo[b].bounds
            if A[0] > B[2] or B[0] > A[2] or A[1] > B[3] or B[1] > A[3]:
                continue
            ls = lines_only(geo[a].boundary.intersection(geo[b].boundary))
            if not ls:
                continue
            if "T-UKR" in (a, b) and (a.startswith("RU-") or b.startswith("RU-")):
                line = unary_union(ls)
                disputed += lines_only(line.intersection(annexed))
                borders += lines_only(line.difference(annexed))
            else:
                borders += ls
    bu = unary_union(borders + disputed[1:])
    coast = lines_only(unary_union([g.boundary for g in geo.values()]).difference(bu.buffer(1e-7))
                       .difference(WINDOW.exterior.buffer(0.01)))
    merged = lambda ls: linemerge(ls) if ls else MultiLineString([])
    out = {"type": "FeatureCollection",
           "features": [{"type": "Feature", "id": k, "geometry": rounded(g)} for k, g in geo.items() if not g.is_empty],
           "borders": rounded(merged(borders)), "coast": rounded(merged(coast)), "disputed": rounded(merged(disputed))}
    coast_u = unary_union(coast).buffer(1e-4)
    extra = {}
    for k, g in geo.items():
        if k.startswith("RU-"):
            nb = sorted({names[j] for j, h in geo.items() if j.startswith("T-") and g.boundary.intersection(h.boundary).length > 0.01})
            extra[k] = {"coastal": g.boundary.intersection(coast_u).length > 0.05, "borders": nb}
            main = max(getattr(g, "geoms", [g]), key=lambda p: p.area)
            if not main.contains(main.centroid):  # a curved shape: a point well inside instead of its centre
                p = shapely.maximum_inscribed_circle(main, 0.01).coords[0]
                extra[k]["anchorLL"] = [round(p[0], 3), round(p[1], 3)]
    return out, extra, geo, a1, crimea


# ----- Russia's expansion and decline (the Learning mode timeline): data/ru-history.json -----
# Approximate: each piece is today's oblasts, countries or provinces (Natural Earth, public domain), not the historical
# borders, which ran elsewhere. `held`: the years Russia (the Tsardom, the Empire, then the Soviet Union) held it.
# Sources: (kind, ...): ("ru", codes) today's subjects; ("a0", A3) a whole country; ("a1", A3, names) provinces of one;
# ("sak", "north"|"south"|"kurils") parts of Sakhalin Oblast.
HISTORY = [
    ("moscow", "The Grand Duchy of Moscow", ("ru", ["MOW", "MOS"]), [[1300, None]], ""),
    ("princ", "Vladimir, Tver, Yaroslavl and the other Russian principalities", ("ru", ["VLA", "IVA", "YAR", "KOS", "NIZ", "TVE", "KLU", "TUL"]),
     [[1478, None]], "absorbed by Moscow in the 1400s"),
    ("novgorod", "The lands of Novgorod", ("ru", ["NGR", "VLG", "ARK", "KR", "KO", "MUR", "NEN", "KIR", "PER"]), [[1478, None]],
     "the Novgorod Republic, taken in 1478"),
    ("ingria", "Ingria, on the Gulf of Finland", ("ru", ["LEN", "SPE"]), [[1478, 1617], [1721, None]],
     "Novgorod; lost to Sweden in 1617, won back in 1721"),
    ("pskov", "Pskov, Ryazan and the Oka lands", ("ru", ["PSK", "RYA", "ORL", "KRS", "LIP", "TAM"]), [[1521, None]],
     "Pskov (1510), Ryazan (1521) and the southern frontier"),
    ("smolensk", "Smolensk and Bryansk", ("ru", ["SMO", "BRY"]), [[1514, 1618], [1667, None]],
     "Poland–Lithuania; lost again 1618–1667"),
    ("kazan", "The Khanate of Kazan", ("ru", ["TA", "CU", "ME", "MO", "UD", "ULY", "PNZ"]), [[1552, None]], "the Khanate of Kazan"),
    ("astrakhan", "Astrakhan and the lower Volga", ("ru", ["AST", "SAM", "SAR", "VGG", "KL", "BA"]), [[1556, None]],
     "the Khanate of Astrakhan and the Nogai Horde"),
    ("siberia", "Siberia, to the Pacific", ("ru", ["SVE", "TYU", "KHM", "YAN", "OMS", "TOM", "NVS", "KEM", "KYA", "IRK", "SA", "MAG", "KHA", "BU", "ZAB"]),
     [[1639, None]], "the Khanate of Sibir and Siberia's own peoples"),
    ("belgorod", "Belgorod and Voronezh, the steppe frontier", ("ru", ["BEL", "VOR"]), [[1654, None]], "the open steppe, settled behind the Belgorod Line"),
    ("urals", "Kamchatka, the southern Urals and Altai", ("ru", ["KAM", "CHE", "KGN", "ORE", "ALT", "AL", "KK"]), [[1740, None]],
     "Kamchatka (1697), the Kazakh and Bashkir steppe and the Dzungars"),
    ("chukotka", "Chukotka", ("ru", ["CHU"]), [[1778, None]], "the Chukchi, after long wars"),
    ("kuban", "The Don, Kuban and Stavropol steppe", ("ru", ["ROS", "KDA", "STA", "AD"]), [[1783, None]],
     "the Crimean Khanate and the Ottoman Empire"),
    ("caucasus", "The North Caucasus", ("ru", ["KC", "KB", "SE", "IN", "CE", "DA"]), [[1864, None]],
     "the mountain peoples, after the Caucasian War (1817–1864)"),
    ("amur", "The Amur and Primorye", ("ru", ["AMU", "YEV", "PRI"]), [[1860, None]], "Qing China (treaties of Aigun and Peking)"),
    ("sakhalin_n", "Northern Sakhalin", ("sak", "north"), [[1875, None]], "shared with Japan until 1875"),
    ("sakhalin_s", "Southern Sakhalin", ("sak", "south"), [[1875, 1905], [1945, None]], "lost to Japan in 1905, retaken in 1945"),
    ("kurils", "The Kuril Islands", ("sak", "kurils"), [[1945, None]], "Japan (Japan still claims the southern four)"),
    ("kaliningrad", "Kaliningrad (northern East Prussia)", ("ru", ["KGD"]), [[1945, None]], "Germany"),
    ("tuva", "Tuva", ("ru", ["TY"]), [[1944, None]], "the independent Tuvan People's Republic"),
    ("ukr_left", "Left-bank Ukraine", ("a1", "UKR", ["Chernihiv", "Poltava", "Sumy", "Kharkiv", "Kiev City"]), [[1654, 1991]],
     "Poland–Lithuania (the Cossack Hetmanate, Pereyaslav 1654)"),
    ("ukr_right", "Right-bank Ukraine", ("a1", "UKR", ["Kiev", "Zhytomyr", "Vinnytsya", "Khmel'nyts'kyy", "Cherkasy", "Kirovohrad"]),
     [[1793, 1991]], "Poland–Lithuania (the second partition)"),
    ("volhynia", "Volhynia", ("a1", "UKR", ["Volyn", "Rivne"]), [[1795, 1921], [1939, 1991]], "Poland–Lithuania; Polish 1921–1939"),
    ("galicia", "Eastern Galicia", ("a1", "UKR", ["L'viv", "Ternopil'", "Ivano-Frankivs'k"]), [[1939, 1991]], "Poland"),
    ("bukovina", "Northern Bukovina", ("a1", "UKR", ["Chernivtsi"]), [[1940, 1991]], "Romania"),
    ("ruthenia", "Transcarpathia", ("a1", "UKR", ["Transcarpathia"]), [[1945, 1991]], "Czechoslovakia"),
    ("novoross", "New Russia (southern Ukraine)", ("a1", "UKR", ["Odessa", "Mykolayiv", "Dnipropetrovs'k"]), [[1783, 1991]],
     "the Crimean Khanate and the Ottoman Empire"),
    ("annex22", "Donetsk, Luhansk, Zaporizhzhia and Kherson", ("a1", "UKR", ["Donets'k", "Luhans'k", "Zaporizhzhya", "Kherson"]),
     [[1783, 1991]], "the Crimean Khanate and the Ottoman Empire; Ukraine's since 1991", 2022),
    ("crimea", "Crimea", ("a1", "UKR", ["Crimea", "Sevastopol"]), [[1783, 1991]],
     "the Crimean Khanate; Ukraine's since 1991 (the Soviet Union gave it to Ukraine in 1954)", 2014),
    ("blr_e", "Eastern Belarus", ("a1", "BLR", ["Vitebsk", "Mogilev", "Gomel", "Minsk", "City of Minsk"]), [[1793, 1991]],
     "Poland–Lithuania (the first and second partitions)"),
    ("blr_w", "Western Belarus", ("a1", "BLR", ["Brest", "Grodno"]), [[1795, 1921], [1939, 1991]], "Poland–Lithuania; Polish 1921–1939"),
    ("lithuania", "Lithuania", ("a0", "LTU"), [[1795, 1918], [1940, 1991]], "Poland–Lithuania (the third partition)"),
    ("latvia", "Latvia", ("a0", "LVA"), [[1721, 1918], [1940, 1991]], "Sweden (Riga, 1721) and Courland (1795)"),
    ("estonia", "Estonia", ("a0", "EST"), [[1721, 1918], [1940, 1991]], "Sweden (Treaty of Nystad)"),
    ("finland", "Finland", ("a0", "FIN"), [[1809, 1917]], "Sweden"),
    ("poland", "Congress Poland", ("a1", "POL", ["Masovian", "Łódź", "Lublin", "Świętokrzyskie", "Podlachian"]), [[1815, 1915]],
     "Napoleon's Duchy of Warsaw (Congress of Vienna)"),
    ("bessarabia", "Bessarabia (Moldova)", ("a0", "MDA"), [[1812, 1918], [1940, 1991]], "the Ottoman Empire; Romanian 1918–1940"),
    ("georgia", "Georgia", ("a0", "GEO"), [[1801, 1918], [1921, 1991]], "the Georgian kingdoms; independent 1918–1921"),
    ("azerbaijan", "Azerbaijan", ("a0", "AZE"), [[1813, 1918], [1920, 1991]], "Persia; independent 1918–1920"),
    ("armenia", "Armenia", ("a0", "ARM"), [[1828, 1918], [1920, 1991]], "Persia; independent 1918–1920"),
    ("kazakhstan", "Kazakhstan", ("a0", "KAZ"), [[1847, 1991]], "the Kazakh khanates"),
    ("uzbekistan", "Uzbekistan", ("a0", "UZB"), [[1868, 1991]], "the khanates of Kokand, Bukhara and Khiva"),
    ("tajikistan", "Tajikistan", ("a0", "TJK"), [[1868, 1991]], "the Emirate of Bukhara"),
    ("kyrgyzstan", "Kyrgyzstan", ("a0", "KGZ"), [[1876, 1991]], "the Khanate of Kokand"),
    ("turkmenistan", "Turkmenistan", ("a0", "TKM"), [[1885, 1991]], "the Turkmen tribes and Khiva"),
    ("alaska", "Russian America (Alaska)", ("a1", "USA", ["Alaska"]), [[1799, 1867]], "its Native peoples; sold to the United States in 1867"),
]
# what each stop on the slider says (every year a piece is gained or lost needs one)
STOPS = {
    1300: "The small Grand Duchy of Moscow", 1478: "Moscow takes Novgorod's lands, reaching the White Sea",
    1514: "Smolensk taken from Poland–Lithuania", 1521: "Pskov and Ryazan join",
    1552: "Ivan the Terrible conquers Kazan", 1556: "Astrakhan falls: the whole Volga is Russian",
    1617: "Ingria lost to Sweden", 1618: "Smolensk lost to Poland",
    1639: "Across Siberia to the Pacific Ocean", 1654: "Left-bank Ukraine joins (Pereyaslav)", 1667: "Smolensk won back",
    1721: "The Baltic coast from Sweden (Treaty of Nystad)", 1740: "Kamchatka, the southern Urals and Altai",
    1778: "Chukotka", 1783: "Crimea and the Black Sea steppe annexed", 1793: "Second partition of Poland",
    1795: "Third partition of Poland: Lithuania", 1799: "Russian America (Alaska)", 1801: "Georgia",
    1809: "Finland taken from Sweden", 1812: "Bessarabia", 1813: "Azerbaijan, from Persia", 1815: "Congress Poland",
    1828: "Armenia, from Persia", 1847: "The Kazakh steppe", 1860: "The Amur and Primorye, from China (Vladivostok founded)",
    1864: "The North Caucasus, after the Caucasian War", 1867: "Alaska sold to the United States",
    1868: "Central Asia: Tashkent, Samarkand and Bukhara", 1875: "All of Sakhalin (the Kurils to Japan)",
    1876: "Kokand: Kyrgyzstan", 1885: "Turkmenistan: the empire at its largest", 1905: "Southern Sakhalin lost to Japan",
    1915: "Poland lost in the First World War", 1917: "Revolution: Finland leaves", 1918: "The Baltic states, Poland, Bessarabia and the Caucasus break away",
    1920: "Azerbaijan and Armenia retaken", 1921: "Georgia retaken; western Belarus and Volhynia go to Poland",
    1922: "The Soviet Union is formed", 1939: "Eastern Poland taken (the pact with Germany)",
    1940: "The Baltic states, Bessarabia and northern Bukovina", 1944: "Tuva joins",
    1945: "After the war: Kaliningrad, southern Sakhalin, the Kurils, Transcarpathia",
    1991: "The Soviet Union breaks into 15 countries", 2014: "Crimea annexed (not recognised by most countries)",
    2022: "Four Ukrainian regions annexed (not recognised): today",
}


def history(geo, a1, crimea):
    """The timeline's pieces: each a polygon with the years Russia held it, from the map's own shapes so they line up."""
    rows = {}  # country -> {province name: polygon}
    for _, r in a1[a1["adm0_a3"].isin(["UKR", "BLR", "POL", "USA"])].iterrows():
        rows.setdefault(r["adm0_a3"], {})[r["name"]] = east(r.geometry)
    rows["UKR"]["Crimea"] = polygonal(unary_union([polygonal(g) for g in crimea]))
    rows["UKR"].pop("Sevastopol", None)
    sak = geo["RU-SAK"]
    parts = {"north": sak.intersection(shapely.box(140, 50, 145.2, 56)), "south": sak.intersection(shapely.box(140, 40, 145.2, 50)),
             "kurils": sak.intersection(shapely.box(145.2, 40, 160, 52))}
    used = {}
    for h in HISTORY:
        if h[2][0] == "a1":
            used.setdefault(h[2][1], []).append((h[0], h[2][2]))
    feats = []
    for h in HISTORY:
        pid, name, src, held, frm = h[:5]
        annexed = h[5] if len(h) > 5 else None
        if src[0] == "ru":
            g = unary_union([geo["RU-" + c] for c in src[1]])
        elif src[0] == "sak":
            g = parts[src[1]]
        elif src[0] == "a0":
            g = geo["T-" + src[1]]
        else:
            # this group's provinces, grown a little out to sea (the map's coast is simplified), minus every other province
            a3, names = src[1], [n for n in src[2] if n != "Sevastopol"]
            mine = unary_union([rows[a3][n] for n in names])
            others = unary_union([g for n, g in rows[a3].items() if n not in names])
            g = geo["T-" + a3].intersection(mine.buffer(0.08).difference(others))
        g = polygonal(g)
        assert not g.is_empty, pid
        props = {"name": name, "held": held, "from": frm}
        if annexed:
            props["annexed"] = annexed
        feats.append({"type": "Feature", "id": pid, "properties": props, "geometry": rounded(shapely.set_precision(g, 0.01), 2)})
    years = sorted({y for h in HISTORY for span in h[3] for y in span if y} | {h[5] for h in HISTORY if len(h) > 5} | {1922})
    missing = [y for y in years if y not in STOPS]
    assert not missing, f"no caption for {missing}"
    russia = unary_union([g for k, g in geo.items() if k.startswith("RU-")])
    today = rounded(shapely.set_precision(russia.boundary, 0.01), 2)
    out = {"type": "FeatureCollection", "features": feats, "today": today,
           "stops": [[y, STOPS[y]] for y in sorted(STOPS)]}
    (ROOT / "data" / "ru-history.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf8")
    print("wrote data/ru-history.json:", len(feats), "pieces,", len(STOPS), "stops")


def flags():
    out = ROOT / "data" / "flags" / "ru"
    out.mkdir(parents=True, exist_ok=True)
    for code, f in FLAGS.items():
        p = out / f"RU-{code}.webp"
        if p.exists():
            continue
        url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(f.replace(" ", "_")) + "?width=640"
        for attempt in range(4):
            try:
                data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
                break
            except Exception as e:  # Commons rate-limits: wait and try again
                print("retrying", code, e)
                time.sleep(5 * (attempt + 1))
        else:
            raise SystemExit(f"could not download the flag of {code} ({f})")
        Image.open(io.BytesIO(data)).convert("RGB").save(p, "WEBP", quality=88)
        time.sleep(1.5)
    print("flags in", out)


def main(only=None):
    fc, extra, geo, a1, crimea = shapes()
    history(geo, a1, crimea)
    if only == "history":
        return
    (ROOT / "data" / "ru-regions.json").write_text(json.dumps(fc, separators=(",", ":")), encoding="utf8")
    sys.path.insert(0, str(ROOT / "tools"))
    import capitals
    try:
        import ru_facts
        FACTS = ru_facts.FACTS
    except ImportError:
        FACTS = {}
    items, missing = [], []
    for code, (name, kind, fd, caps, pop, area) in PARTS.items():
        iso = "RU-" + code
        short = name.replace(" Oblast", "").replace(" Krai", "").replace(" (Yakutia)", "")
        names = list(dict.fromkeys([name, short] + ALT.get(code, []) +
                                   ([short + " Region", short + " Oblast"] if kind == "Oblast" else []) +
                                   ([short + " Territory"] if kind == "Krai" else []) +
                                   ([short + " Republic", "Republic of " + short] if kind == "Republic" else [])))
        f = FACTS.get(code, {})
        e = dict(extra.get(iso, {}))
        it = {"iso": iso, "id": iso, "name": name, "names": names, "capitals": caps, "cont": ["Europe", "Asia"], "car": False, "a2": iso,
              "info": {"abbr": code, "kind": kind, "region": fd, "pop": pop, "popYear": "2021 census", "area": area,
                       "flag": True, "facts": f, **{k: v for k, v in e.items() if k != "anchorLL"}},
              "flagKey": "ru/" + iso}
        if "anchorLL" in e:
            it["anchorLL"] = e["anchorLL"]
        if NOT_TYPO.get(code):
            it["notTypo"] = NOT_TYPO[code]
        ll = CAP_LL.get(caps[0]) or capitals.find(CAP_SEARCH.get(caps[0], caps[0]), a2="RU")
        if ll:
            it["capLL"] = [ll]
        else:
            missing.append(f"{name}: {caps[0]}")
            it["capLL"] = []
        items.append(it)
    if missing:
        print("capitals not found:", missing)
    by_area = sorted(items, key=lambda c: -c["info"]["area"])
    for it in items:
        it["info"]["areaRank"] = by_area.index(it) + 1
    (ROOT / "data" / "ru-parts.json").write_text(json.dumps(sorted(items, key=lambda s: s["name"]), ensure_ascii=False, indent=0), encoding="utf8")
    print("wrote data/ru-regions.json and data/ru-parts.json:", len(items), "parts")
    flags()


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)  # "history": just data/ru-history.json
