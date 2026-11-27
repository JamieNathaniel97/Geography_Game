"""New Zealand's 16 regions and the Chatham Islands (New_Zealand_plan.md): the config for tools/build_country.py and the
Learning card facts. Card fact fields: see tools/at_facts.py; New Zealand's own three: maori (Māori name and main iwi),
island (North or South Island), film (famous film location, Lord of the Rings sites first). No flag games.
The Chatham Islands sit east of the date line: moved 360° east (an unframed "inset") so they're drawn beside the
mainland, with an oval. The other outlying islands (Kermadec, Three Kings, the subantarctic islands) are left off.
Written from general knowledge and the downloaded Wikipedia articles (tools/downloads/nz/wiki/); checked by hand.
Populations: Census 2023 (Stats NZ). The 16 regions and the Chathams (612) add up to 18 fewer than the national count
of 4,993,923: the other outlying islands and Stats NZ's random rounding (TOTAL_TOL).
"""

A3, A2, CONT = "NZL", "NZ", "Oceania"
WINDOW = (158.0, -51.0, 190.0, -30.0)
DETAIL = (166.0, -47.5, 184.2, -34.2)
POP_SOURCE, POP_YEAR, TOTAL, TOTAL_TOL = "Stats NZ, Census 2023", "2023 census", 4993923, 25
DROP = ("X01~", "X03~", "X04~", "X05~", "X06~", "X07~")
INSETS = [dict(codes=["CIT"], box=(-177.0, -44.5, -175.9, -43.5), to=(-176.45 + 360, -44.0), frame=False)]
ISLES = [("CIT", (183.55, -44.0), 0.55)]
FLAGS = "no-flags"
CAP_LL = {"Waitangi": [-176.56, -43.95], "Stratford": [174.284, -39.338]}

R, U = "Region", "Region (unitary authority)"
PARTS = {
    "NTL": dict(name="Northland", names=["Te Taitokerau", "Te Tai Tokerau", "Northland Region"], capital="Whangārei", capAlt=["Whangarei"],
                pop=194007, area=12504, kind=R),
    "AUK": dict(name="Auckland", names=["Tāmaki Makaurau", "Tamaki Makaurau", "Auckland Region"], capital="Auckland", pop=1656486, area=4941, kind=U),
    "WKO": dict(name="Waikato", names=["Waikato Region"], capital="Hamilton", capAlt=["Kirikiriroa"], pop=498771, area=23900, kind=R),
    "BOP": dict(name="Bay of Plenty", names=["Te Moana-a-Toi", "Bay of Plenty Region"], capital="Whakatāne", capAlt=["Whakatane"], pop=334140,
                area=12072, kind=R),
    "GIS": dict(name="Gisborne", names=["Te Tairāwhiti", "Tairāwhiti", "Gisborne District", "East Coast"], capital="Gisborne", pop=51135, area=8385, kind=U),
    "HKB": dict(name="Hawke's Bay", names=["Hawkes Bay", "Te Matau-a-Māui", "Hawke's Bay Region"], capital="Napier", pop=175074, area=14138, kind=R),
    "TKI": dict(name="Taranaki", names=["Taranaki Region"], capital="Stratford", pop=126015, area=7254, kind=R),
    "MWT": dict(name="Manawatū-Whanganui", names=["Manawatu-Whanganui", "Manawatu-Wanganui", "Manawatū-Wanganui", "Manawatu", "Horizons"],
                capital="Palmerston North", pop=251412, area=22221, kind=R),
    "WGN": dict(name="Wellington", names=["Te Upoko-o-te-Ika-a-Māui", "Wellington Region", "Greater Wellington"], capital="Wellington",
                capAlt=["Te Whanganui-a-Tara"], pop=520971, area=8049, kind=R),
    "TAS": dict(name="Tasman", names=["Te Tai-o-Aorere", "Tasman District"], capital="Richmond", pop=57807, area=9616, kind=U),
    "NSN": dict(name="Nelson", names=["Whakatū", "Whakatu", "Nelson City"], capital="Nelson", pop=52584, area=422, kind=U),
    "MBH": dict(name="Marlborough", names=["Te Tauihu-o-te-Waka", "Marlborough District"], capital="Blenheim", pop=49431, area=10498, kind=U),
    "WTC": dict(name="West Coast", names=["Te Tai Poutini", "West Coast Region", "Westland"], capital="Greymouth", capAlt=["Māwhera"],
                pop=33390, area=23245, kind=R),
    "CAN": dict(name="Canterbury", names=["Waitaha", "Canterbury Region"], capital="Christchurch", capAlt=["Ōtautahi"], pop=651027, area=44504, kind=R),
    "OTA": dict(name="Otago", names=["Ōtākou", "Otakou", "Otago Region"], capital="Dunedin", capAlt=["Ōtepoti"], pop=240900, area=31186, kind=R),
    "STL": dict(name="Southland", names=["Murihiku", "Southland Region"], capital="Invercargill", pop=100143, area=31196, kind=R),
    "CIT": dict(name="Chatham Islands", names=["Chatham Islands Territory", "Rēkohu", "Rekohu", "Wharekauri", "Chathams"], capital="Waitangi",
                pop=612, area=966, kind="Territory (outside any region)"),
}

FACTS = {
    "NTL": dict(local="Te Taitokerau", demonym="Northlander", festival="Waitangi Day at the Treaty Grounds", river="Northern Wairoa River",
                wonder="The Bay of Islands and Tāne Mahuta, the biggest living kauri tree", historic="Where the Treaty of Waitangi was signed (1840)",
                landmark="Cape Rēinga lighthouse", person="Hone Heke (Ngāpuhi chief)", known="Kauri forests, the Bay of Islands and the Treaty",
                maori="Te Taitokerau; iwi: Ngāpuhi (the largest iwi), Te Rarawa, Ngāti Whātua", island="North Island"),
    "AUK": dict(local="Tāmaki Makaurau", demonym="Aucklander", dialect="English, with the world's largest Polynesian population", festival="The Pasifika Festival",
                club="Auckland City FC and Auckland FC", wonder="The Auckland volcanic field (Rangitoto Island)", historic="Tāmaki, then the colonial capital (1841–1865)",
                landmark="The Sky Tower and the Harbour Bridge", person="Lorde (singer)", known="New Zealand's biggest city: a third of the country lives here",
                company="Air New Zealand and Fisher & Paykel", maori="Tāmaki Makaurau; iwi: Ngāti Whātua Ōrākei and Tainui iwi", island="North Island",
                film="Bethells Beach and the Piha coast (many films and TV series)"),
    "WKO": dict(local="Waikato", demonym="Waikatoan", festival="Fieldays (the Southern Hemisphere's biggest agricultural show)", river="Waikato River (New Zealand's longest)",
                wonder="The Waitomo glowworm caves and Lake Taupō", historic="The heart of the Kīngitanga (the Māori King movement)", landmark="The Hobbiton Movie Set",
                unesco="Tongariro National Park (shared)", known="Dairy farming and Hamilton", maori="Waikato; iwi: Waikato-Tainui, Ngāti Maniapoto, Ngāti Tūwharetoa",
                island="North Island", film="Hobbiton at Matamata (The Shire)"),
    "BOP": dict(local="Te Moana-a-Toi", demonym="Bay of Plenty local", dish="Kiwifruit (Te Puke, the kiwifruit capital)", river="Rangitāiki River",
                wonder="Rotorua's geysers and Whakaari / White Island", historic="Landing place of the Te Arawa and Mātaatua canoes", landmark="Pōhutu Geyser at Te Puia",
                known="Kiwifruit, surf beaches and Rotorua's Māori culture and hot springs", company="Zespri (kiwifruit)", city="Tauranga",
                maori="Te Moana-a-Toi; iwi: Te Arawa, Ngāti Awa, Tūhoe, Ngāi Te Rangi", island="North Island"),
    "GIS": dict(local="Te Tairāwhiti", demonym="Gisborne local (Tairāwhiti)", drink="Chardonnay", festival="Rhythm and Vines on New Year's Eve",
                high="Hikurangi, 1,752 m", wonder="The East Cape", historic="Where James Cook first landed in New Zealand (1769)", landmark="Mount Hikurangi and Tolaga Bay Wharf",
                known="The first city in the world to see the sun each day", maori="Te Tairāwhiti; iwi: Ngāti Porou, Rongowhakaata", island="North Island",
                film="Whale Rider (Whangara)"),
    "HKB": dict(local="Te Matau-a-Māui", demonym="Hawke's Bay local", drink="Wine (Gimblett Gravels reds)", festival="The Art Deco Festival in Napier",
                wonder="Cape Kidnappers' gannets and Te Mata Peak", historic="Napier was rebuilt in Art Deco after the 1931 earthquake", landmark="Napier's Art Deco centre",
                known="Wine, fruit and Art Deco", maori="Te Matau-a-Māui; iwi: Ngāti Kahungunu", island="North Island"),
    "TKI": dict(local="Taranaki", demonym="Taranaki local", high="Taranaki Maunga, 2,518 m", wonder="Taranaki Maunga, a near-perfect volcanic cone",
                historic="The Taranaki Wars (1860s)", landmark="New Plymouth's Coastal Walkway and Len Lye's Wind Wand", known="Dairy farming, oil and gas",
                city="New Plymouth", maori="Taranaki; iwi: Te Āti Awa, Ngāti Ruanui, Taranaki iwi", island="North Island", film="The Last Samurai (Taranaki as Mount Fuji)"),
    "MWT": dict(local="Manawatū-Whanganui", demonym="Manawatū or Whanganui local", river="Whanganui River (legally a person since 2017)",
                high="Ruapehu, 2,797 m: the North Island's highest", wonder="The Tongariro Alpine Crossing", historic="The Whanganui River iwi",
                landmark="The Tongariro volcanoes", unesco="Tongariro National Park", known="Farming and Massey University",
                maori="Manawatū-Whanganui; iwi: Whanganui iwi, Rangitāne, Ngāti Raukawa, Ngāti Tūwharetoa", island="North Island",
                film="Mordor and Mount Doom (Tongariro and Ngauruhoe)"),
    "WGN": dict(local="Te Upoko-o-te-Ika-a-Māui", demonym="Wellingtonian", festival="World of WearableArt and CubaDupa", club="Wellington Phoenix",
                wonder="The Remutaka ranges and Cape Palliser", historic="The capital since 1865", landmark="Te Papa museum and the Beehive",
                person="Peter Jackson (film-maker)", known="The capital, coffee, wind and the film industry (Wētā Workshop)", company="Wētā Workshop and Xero",
                maori="Te Upoko-o-te-Ika-a-Māui ('the head of the fish of Māui'); iwi: Te Āti Awa, Ngāti Toa", island="North Island",
                film="Rivendell at Kaitoke and the Hutt River as the Anduin"),
    "TAS": dict(local="Te Tai-o-Aorere", demonym="Tasman local", wonder="Abel Tasman National Park and Farewell Spit", historic="Abel Tasman anchored in Golden Bay (1642)",
                landmark="Te Waikoropupū Springs", person="Ernest Rutherford (born in Brightwater)", known="Apples, hops and golden beaches",
                maori="Te Tai-o-Aorere; iwi: Ngāti Tama, Ngāti Rārua, Te Ātiawa", island="South Island", film="Mount Owen and Takaka Hill (Dimrill Dale and Chetwood Forest)"),
    "NSN": dict(local="Whakatū", demonym="Nelsonian", festival="The Nelson Arts Festival", wonder="Tāhunanui Beach", historic="One of the New Zealand Company's first settlements (1841)",
                landmark="The Centre of New Zealand monument and Christ Church Cathedral", known="Sunshine, arts and crafts, and the smallest region",
                maori="Whakatū; iwi: Ngāti Tama, Ngāti Kuia, Ngāti Koata", island="South Island"),
    "MBH": dict(local="Te Tauihu-o-te-Waka", demonym="Marlburian", drink="Sauvignon Blanc (New Zealand's biggest wine region)", wonder="The Marlborough Sounds",
                historic="Where the first settlers of the Wairau Bar landed (about 1300)", landmark="Queen Charlotte Track", known="Wine and the Interislander ferry at Picton",
                maori="Te Tauihu-o-te-Waka; iwi: Rangitāne o Wairau, Ngāti Kuia", island="South Island", film="The Pelorus River (the barrel scene in The Hobbit)"),
    "WTC": dict(local="Te Tai Poutini", demonym="Coaster", high="Aoraki / Mount Cook, 3,724 m (on the Canterbury border)",
                wonder="The Pancake Rocks at Punakaiki and the Franz Josef and Fox glaciers", historic="The 1860s gold rush", landmark="The Pancake Rocks",
                unesco="Te Wāhipounamu (South West New Zealand)", known="Pounamu (greenstone), coal and wild rainforest coast",
                maori="Te Tai Poutini; iwi: Ngāi Tahu (Poutini Ngāi Tahu)", island="South Island"),
    "CAN": dict(local="Waitaha", demonym="Cantabrian", club="Christchurch United", river="Waimakariri and Rakaia rivers",
                high="Aoraki / Mount Cook, 3,724 m: New Zealand's highest", wonder="Lake Tekapo, Aoraki and the Canterbury Plains",
                historic="The Canterbury Association's settlement (1850)", landmark="Christchurch's Cardboard Cathedral and the Church of the Good Shepherd",
                known="Christchurch, farming and the 2010–2011 earthquakes", maori="Waitaha; iwi: Ngāi Tahu", island="South Island", film="Edoras at Mount Sunday"),
    "OTA": dict(local="Ōtākou", demonym="Otagoite", drink="Central Otago Pinot Noir", wonder="Lake Wakatipu and the Remarkables",
                historic="The 1861 gold rush; Dunedin was settled by Scots", landmark="Dunedin Railway Station and Larnach Castle",
                unesco="Te Wāhipounamu (part)", person="Richie McCaw (rugby captain, born in Oamaru)", known="Queenstown's adventure tourism, gold and wine",
                maori="Ōtākou; iwi: Ngāi Tahu", island="South Island", film="Glenorchy and Queenstown (Isengard and Lothlórien)"),
    "STL": dict(local="Murihiku", demonym="Southlander", dish="Bluff oysters", wonder="Fiordland and Milford Sound", historic="Early whaling and sealing stations",
                landmark="The Bluff signpost and Stewart Island", unesco="Te Wāhipounamu (Fiordland)", person="Burt Munro (The World's Fastest Indian)",
                known="Fiordland, farming and Stewart Island", maori="Murihiku; iwi: Ngāi Tahu", island="South Island", film="The Mavora Lakes (the Anduin and Nen Hithoel)"),
    "CIT": dict(local="Rēkohu (Moriori) / Wharekauri (Māori)", demonym="Chatham Islander", dialect="English; the Moriori language is being revived",
                wonder="The basalt columns and the endemic black robin", historic="The homeland of the Moriori people", landmark="Waitangi and the Kōpinga Marae",
                person="Tommy Solomon (the last Moriori of unmixed descent)", known="Crayfish, isolation and one of the first places to see the new day",
                maori="Wharekauri; iwi: Ngāti Mutunga, and the Moriori people", island="Neither: about 800 km east of the South Island"),
}
