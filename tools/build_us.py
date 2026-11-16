"""Builds the US states data for build 3:

  data/us-states.json   state shapes (us-atlas 1:10m, from the US Census Bureau), ids = postal codes, with border and
                        coastline lines prepared in advance. Washington, D.C. is kept as a grey non-quiz area; the
                        territories (Puerto Rico, Guam...) are left out, since they don't fit the usual US map layout.
  data/states.json      the 50 states: names, capitals and Learning mode facts (hand-written below, 2020 census)

Run from the repo root:  python tools/build_us.py
"""
import json
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DL = ROOT / "tools" / "downloads"
SOURCE = "https://cdn.jsdelivr.net/npm/us-atlas@3.0.1/states-10m.json"

# code: (name, capital, largest city if not the capital, nickname, statehood year, order, population 2020, census region)
STATES = {
    "AL": ("Alabama", "Montgomery", "Huntsville", "Yellowhammer State", 1819, 22, 5024279, "South"),
    "AK": ("Alaska", "Juneau", "Anchorage", "The Last Frontier", 1959, 49, 733391, "West"),
    "AZ": ("Arizona", "Phoenix", "", "Grand Canyon State", 1912, 48, 7151502, "West"),
    "AR": ("Arkansas", "Little Rock", "", "The Natural State", 1836, 25, 3011524, "South"),
    "CA": ("California", "Sacramento", "Los Angeles", "Golden State", 1850, 31, 39538223, "West"),
    "CO": ("Colorado", "Denver", "", "Centennial State", 1876, 38, 5773714, "West"),
    "CT": ("Connecticut", "Hartford", "Bridgeport", "Constitution State", 1788, 5, 3605944, "Northeast"),
    "DE": ("Delaware", "Dover", "Wilmington", "First State", 1787, 1, 989948, "South"),
    "FL": ("Florida", "Tallahassee", "Jacksonville", "Sunshine State", 1845, 27, 21538187, "South"),
    "GA": ("Georgia", "Atlanta", "", "Peach State", 1788, 4, 10711908, "South"),
    "HI": ("Hawaii", "Honolulu", "", "Aloha State", 1959, 50, 1455271, "West"),
    "ID": ("Idaho", "Boise", "", "Gem State", 1890, 43, 1839106, "West"),
    "IL": ("Illinois", "Springfield", "Chicago", "Prairie State", 1818, 21, 12812508, "Midwest"),
    "IN": ("Indiana", "Indianapolis", "", "Hoosier State", 1816, 19, 6785528, "Midwest"),
    "IA": ("Iowa", "Des Moines", "", "Hawkeye State", 1846, 29, 3190369, "Midwest"),
    "KS": ("Kansas", "Topeka", "Wichita", "Sunflower State", 1861, 34, 2937880, "Midwest"),
    "KY": ("Kentucky", "Frankfort", "Louisville", "Bluegrass State", 1792, 15, 4505836, "South"),
    "LA": ("Louisiana", "Baton Rouge", "New Orleans", "Pelican State", 1812, 18, 4657757, "South"),
    "ME": ("Maine", "Augusta", "Portland", "Pine Tree State", 1820, 23, 1362359, "Northeast"),
    "MD": ("Maryland", "Annapolis", "Baltimore", "Old Line State", 1788, 7, 6177224, "South"),
    "MA": ("Massachusetts", "Boston", "", "Bay State", 1788, 6, 7029917, "Northeast"),
    "MI": ("Michigan", "Lansing", "Detroit", "Great Lakes State", 1837, 26, 10077331, "Midwest"),
    "MN": ("Minnesota", "Saint Paul", "Minneapolis", "North Star State", 1858, 32, 5706494, "Midwest"),
    "MS": ("Mississippi", "Jackson", "", "Magnolia State", 1817, 20, 2961279, "South"),
    "MO": ("Missouri", "Jefferson City", "Kansas City", "Show-Me State", 1821, 24, 6154913, "Midwest"),
    "MT": ("Montana", "Helena", "Billings", "Treasure State", 1889, 41, 1084225, "West"),
    "NE": ("Nebraska", "Lincoln", "Omaha", "Cornhusker State", 1867, 37, 1961504, "Midwest"),
    "NV": ("Nevada", "Carson City", "Las Vegas", "Silver State", 1864, 36, 3104614, "West"),
    "NH": ("New Hampshire", "Concord", "Manchester", "Granite State", 1788, 9, 1377529, "Northeast"),
    "NJ": ("New Jersey", "Trenton", "Newark", "Garden State", 1787, 3, 9288994, "Northeast"),
    "NM": ("New Mexico", "Santa Fe", "Albuquerque", "Land of Enchantment", 1912, 47, 2117522, "West"),
    "NY": ("New York", "Albany", "New York City", "Empire State", 1788, 11, 20201249, "Northeast"),
    "NC": ("North Carolina", "Raleigh", "Charlotte", "Tar Heel State", 1789, 12, 10439388, "South"),
    "ND": ("North Dakota", "Bismarck", "Fargo", "Peace Garden State", 1889, 39, 779094, "Midwest"),
    "OH": ("Ohio", "Columbus", "", "Buckeye State", 1803, 17, 11799448, "Midwest"),
    "OK": ("Oklahoma", "Oklahoma City", "", "Sooner State", 1907, 46, 3959353, "South"),
    "OR": ("Oregon", "Salem", "Portland", "Beaver State", 1859, 33, 4237256, "West"),
    "PA": ("Pennsylvania", "Harrisburg", "Philadelphia", "Keystone State", 1787, 2, 13002700, "Northeast"),
    "RI": ("Rhode Island", "Providence", "", "Ocean State", 1790, 13, 1097379, "Northeast"),
    "SC": ("South Carolina", "Columbia", "Charleston", "Palmetto State", 1788, 8, 5118425, "South"),
    "SD": ("South Dakota", "Pierre", "Sioux Falls", "Mount Rushmore State", 1889, 40, 886667, "Midwest"),
    "TN": ("Tennessee", "Nashville", "", "Volunteer State", 1796, 16, 6910840, "South"),
    "TX": ("Texas", "Austin", "Houston", "Lone Star State", 1845, 28, 29145505, "South"),
    "UT": ("Utah", "Salt Lake City", "", "Beehive State", 1896, 45, 3271616, "West"),
    "VT": ("Vermont", "Montpelier", "Burlington", "Green Mountain State", 1791, 14, 643077, "Northeast"),
    "VA": ("Virginia", "Richmond", "Virginia Beach", "Old Dominion", 1788, 10, 8631393, "South"),
    "WA": ("Washington", "Olympia", "Seattle", "Evergreen State", 1889, 42, 7705281, "West"),
    "WV": ("West Virginia", "Charleston", "", "Mountain State", 1863, 35, 1793716, "South"),
    "WI": ("Wisconsin", "Madison", "Milwaukee", "Badger State", 1848, 30, 5893718, "Midwest"),
    "WY": ("Wyoming", "Cheyenne", "", "Equality State", 1890, 44, 576851, "West"),
}
# More Learning facts (hand-written): time zones (main first), name origin, highest point (name, ft, m),
# total area in square miles (Census), state bird, state flower
FACTS = {
    "AL": ("Central", "Possibly from the Alabama (Alibamu) people; a Choctaw phrase often given as \"thicket clearers\"", ("Cheaha Mountain", 2413, 735), 52420, "Yellowhammer (northern flicker)", "Camellia"),
    "AK": ("Alaska; Hawaii–Aleutian (western Aleutians)", "Aleut alaxsxaq, \"the mainland\"", ("Denali (Mount McKinley)", 20310, 6190), 665384, "Willow ptarmigan", "Forget-me-not"),
    "AZ": ("Mountain (no daylight saving, except the Navajo Nation)", "Probably O'odham ali ṣonak, \"small spring\"", ("Humphreys Peak", 12633, 3851), 113990, "Cactus wren", "Saguaro blossom"),
    "AR": ("Central", "A French spelling of an Illinois name for the Quapaw people", ("Mount Magazine", 2753, 839), 53179, "Northern mockingbird", "Apple blossom"),
    "CA": ("Pacific", "A mythical island in a 16th-century Spanish novel", ("Mount Whitney", 14505, 4421), 163695, "California quail", "California poppy"),
    "CO": ("Mountain", "Spanish for \"coloured red\", after the Colorado River", ("Mount Elbert", 14440, 4401), 104094, "Lark bunting", "Rocky Mountain columbine"),
    "CT": ("Eastern", "Mohegan-Pequot quinatucquet, \"upon the long river\"", ("Mount Frissell (south slope)", 2380, 725), 5543, "American robin", "Mountain laurel"),
    "DE": ("Eastern", "The Delaware River, named after Lord De La Warr, an early governor of Virginia", ("Ebright Azimuth", 448, 137), 2489, "Blue Hen chicken", "Peach blossom"),
    "FL": ("Eastern; Central (western Panhandle)", "Spanish for \"flowery\": Ponce de León landed at Easter (Pascua Florida) 1513", ("Britton Hill", 345, 105), 65758, "Northern mockingbird", "Orange blossom"),
    "GA": ("Eastern", "King George II of Great Britain", ("Brasstown Bald", 4784, 1458), 59425, "Brown thrasher", "Cherokee rose"),
    "HI": ("Hawaii–Aleutian (no daylight saving)", "Hawaiian; possibly from Hawaiki, the Polynesian homeland", ("Mauna Kea", 13803, 4207), 10932, "Nēnē (Hawaiian goose)", "Yellow hibiscus"),
    "ID": ("Mountain; Pacific (northern panhandle)", "Uncertain: an invented word, claimed to mean \"gem of the mountains\"", ("Borah Peak", 12662, 3859), 83569, "Mountain bluebird", "Syringa (mock orange)"),
    "IL": ("Central", "A French form of the Algonquian name of the Illinois people", ("Charles Mound", 1235, 376), 57914, "Northern cardinal", "Violet"),
    "IN": ("Eastern; Central (northwest and southwest corners)", "\"Land of the Indians\"", ("Hoosier Hill", 1257, 383), 36420, "Northern cardinal", "Peony"),
    "IA": ("Central", "The Ioway people", ("Hawkeye Point", 1670, 509), 56273, "Eastern goldfinch", "Wild prairie rose"),
    "KS": ("Central; Mountain (four western counties)", "The Kansa (Kaw) people, \"people of the south wind\"", ("Mount Sunflower", 4039, 1231), 82278, "Western meadowlark", "Sunflower"),
    "KY": ("Eastern; Central (western half)", "Probably Iroquoian, often said to mean \"on the meadow\"", ("Black Mountain", 4145, 1263), 40408, "Northern cardinal", "Goldenrod"),
    "LA": ("Central", "King Louis XIV of France", ("Driskill Mountain", 535, 163), 52378, "Brown pelican", "Magnolia"),
    "ME": ("Eastern", "Uncertain: perhaps sailors' word for \"the mainland\", or the French province of Maine", ("Katahdin", 5267, 1605), 35380, "Black-capped chickadee", "White pine cone and tassel"),
    "MD": ("Eastern", "Queen Henrietta Maria, wife of King Charles I", ("Hoye-Crest", 3360, 1024), 12406, "Baltimore oriole", "Black-eyed Susan"),
    "MA": ("Eastern", "The Massachusett people, \"at the great hill\"", ("Mount Greylock", 3489, 1063), 10554, "Black-capped chickadee", "Mayflower"),
    "MI": ("Eastern; Central (four counties bordering Wisconsin)", "Ojibwe mishigami, \"great water\"", ("Mount Arvon", 1979, 603), 96714, "American robin", "Apple blossom"),
    "MN": ("Central", "Dakota mní sóta, \"clear water\"", ("Eagle Mountain", 2301, 701), 86936, "Common loon", "Pink and white lady's slipper"),
    "MS": ("Central", "The Mississippi River; Ojibwe misi-ziibi, \"great river\"", ("Woodall Mountain", 807, 246), 48432, "Northern mockingbird", "Magnolia"),
    "MO": ("Central", "The Missouria people, \"people with wooden canoes\"", ("Taum Sauk Mountain", 1772, 540), 69707, "Eastern bluebird", "Hawthorn"),
    "MT": ("Mountain", "Spanish montaña, \"mountainous\"", ("Granite Peak", 12799, 3901), 147040, "Western meadowlark", "Bitterroot"),
    "NE": ("Central; Mountain (western panhandle)", "Otoe for \"flat water\", the Platte River", ("Panorama Point", 5424, 1653), 77348, "Western meadowlark", "Goldenrod"),
    "NV": ("Pacific", "Spanish for \"snow-covered\", after the Sierra Nevada", ("Boundary Peak", 13140, 4005), 110572, "Mountain bluebird", "Sagebrush"),
    "NH": ("Eastern", "The county of Hampshire in England", ("Mount Washington", 6288, 1917), 9349, "Purple finch", "Purple lilac"),
    "NJ": ("Eastern", "The island of Jersey in the Channel Islands", ("High Point", 1803, 550), 8723, "Eastern goldfinch", "Violet"),
    "NM": ("Mountain", "Spanish Nuevo México, after the Valley of Mexico", ("Wheeler Peak", 13161, 4011), 121590, "Greater roadrunner", "Yucca"),
    "NY": ("Eastern", "The Duke of York, later King James II", ("Mount Marcy", 5344, 1629), 54555, "Eastern bluebird", "Rose"),
    "NC": ("Eastern", "King Charles I (Carolus in Latin)", ("Mount Mitchell", 6684, 2037), 53819, "Northern cardinal", "Dogwood"),
    "ND": ("Central; Mountain (southwest)", "The Dakota people, \"friends\" or \"allies\"", ("White Butte", 3506, 1069), 70698, "Western meadowlark", "Wild prairie rose"),
    "OH": ("Eastern", "Seneca ohiːyo', \"good river\"", ("Campbell Hill", 1549, 472), 44826, "Northern cardinal", "Red carnation"),
    "OK": ("Central", "Choctaw okla humma, \"red people\"", ("Black Mesa", 4973, 1516), 69899, "Scissor-tailed flycatcher", "Oklahoma rose"),
    "OR": ("Pacific; Mountain (most of Malheur County)", "Uncertain: perhaps \"Ouragon\", an early name for the Columbia River", ("Mount Hood", 11249, 3429), 98379, "Western meadowlark", "Oregon grape"),
    "PA": ("Eastern", "\"Penn's woods\", after Admiral William Penn, the founder's father", ("Mount Davis", 3213, 979), 46054, "Ruffed grouse", "Mountain laurel"),
    "RI": ("Eastern", "Probably Dutch Roodt Eylandt, \"red island\", or the Greek island of Rhodes", ("Jerimoth Hill", 812, 247), 1545, "Rhode Island Red (chicken)", "Violet"),
    "SC": ("Eastern", "King Charles I (Carolus in Latin)", ("Sassafras Mountain", 3553, 1083), 32020, "Carolina wren", "Yellow jessamine"),
    "SD": ("Central; Mountain (western half)", "The Dakota people, \"friends\" or \"allies\"", ("Black Elk Peak", 7242, 2207), 77116, "Ring-necked pheasant", "Pasque flower"),
    "TN": ("Central; Eastern (east Tennessee)", "Tanasi, a Cherokee town", ("Kuwohi (formerly Clingmans Dome)", 6643, 2025), 42144, "Northern mockingbird", "Iris"),
    "TX": ("Central; Mountain (far west, around El Paso)", "Caddo táyshaʔ, \"friends\" or \"allies\"", ("Guadalupe Peak", 8751, 2667), 268596, "Northern mockingbird", "Bluebonnet"),
    "UT": ("Mountain", "The Ute people", ("Kings Peak", 13528, 4123), 84897, "California gull", "Sego lily"),
    "VT": ("Eastern", "French vert mont, \"green mountain\"", ("Mount Mansfield", 4393, 1339), 9616, "Hermit thrush", "Red clover"),
    "VA": ("Eastern", "Queen Elizabeth I, the \"Virgin Queen\"", ("Mount Rogers", 5729, 1746), 42775, "Northern cardinal", "American dogwood"),
    "WA": ("Pacific", "George Washington", ("Mount Rainier", 14411, 4392), 71298, "American goldfinch", "Coast rhododendron"),
    "WV": ("Eastern", "The western counties of Virginia, which split away in 1863", ("Spruce Knob", 4863, 1482), 24230, "Northern cardinal", "Rhododendron"),
    "WI": ("Central", "Uncertain: a Miami name for the Wisconsin River, often given as \"river running through a red place\"", ("Timms Hill", 1951, 595), 65496, "American robin", "Wood violet"),
    "WY": ("Mountain", "Lenape for \"at the big river flat\", via the Wyoming Valley in Pennsylvania", ("Gannett Peak", 13804, 4207), 97813, "Western meadowlark", "Indian paintbrush"),
}
# extra names accepted when typing
NAMES = {"WA": ["Washington State"]}
CAPITALS = {"MN": ["Saint Paul", "St Paul"]}


def main():
    DL.mkdir(parents=True, exist_ok=True)
    src = DL / "us-states-10m.json"
    if not src.exists():
        urllib.request.urlretrieve(SOURCE, src)
    t = json.loads(src.read_text(encoding="utf8"))
    code_by_name = {v[0]: k for k, v in STATES.items()}
    keep = []
    for g in t["objects"]["states"]["geometries"]:
        name = g["properties"]["name"]
        if name in code_by_name:
            g["id"] = code_by_name[name]
        elif name == "District of Columbia":
            g["id"] = "T-DC"
        else:
            continue  # territories
        g.pop("properties", None)
        keep.append(g)
    t["objects"] = {"states": {"type": "GeometryCollection", "geometries": keep}}
    # borders (between two areas) and coastline (one area only), prepared once
    users = {}
    def walk(arcs, n, gid):
        for a in arcs:
            if isinstance(a, list):
                walk(a, n, gid)
            else:
                users.setdefault(a if a >= 0 else ~a, []).append((n, gid))
    for n, g in enumerate(keep):
        walk(g["arcs"], n, g["id"])
    t["objects"]["borders"] = {"type": "MultiLineString", "arcs": [[i] for i, u in sorted(users.items()) if len({gid for _, gid in u}) > 1]}
    t["objects"]["coast"] = {"type": "MultiLineString", "arcs": [[i] for i, u in sorted(users.items()) if len({n for n, _ in u}) == 1]}
    (ROOT / "data" / "us-states.json").write_text(json.dumps(t, separators=(",", ":")), encoding="utf8")

    states = []
    for code, (name, capital, city, nick, year, order, pop, region) in STATES.items():
        states.append({
            "iso": code, "id": code, "name": name,
            "names": [name] + NAMES.get(code, []),
            "capitals": CAPITALS.get(code, [capital]),
            "cont": ["North America"], "car": False, "a2": code,
            "info": {"abbr": code, "city": city, "nickname": nick, "year": year, "order": order,
                     "pop": pop, "popYear": "2020 census", "region": region,
                     "tz": FACTS[code][0], "origin": FACTS[code][1], "high": FACTS[code][2],
                     "areaSqMi": FACTS[code][3], "bird": FACTS[code][4], "flower": FACTS[code][5]},
        })
    by_area = sorted(STATES, key=lambda k: -FACTS[k][3])
    for st in states:
        st["info"]["areaRank"] = by_area.index(st["iso"]) + 1
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    import capitals
    capitals.add_capital_coords(states, country_code="US")
    (ROOT / "data" / "states.json").write_text(json.dumps(sorted(states, key=lambda s: s["name"]), ensure_ascii=False, indent=0), encoding="utf8")
    print("wrote data/us-states.json and data/states.json:", len(states), "states")


if __name__ == "__main__":
    main()
