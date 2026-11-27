"""Malaysia's 13 states and 3 federal territories (Malaysia_plan.md): the config for tools/build_country.py and the
Learning card facts. Card fact fields: see tools/at_facts.py; Malaysia's own three: ruler (sultan, raja, governor, or
none for the federal territories), ethnic (main ethnic groups), half (Peninsula or Borneo). Games 5 and 6: flags.
East Malaysia (Sabah, Sarawak, Labuan) is moved into a framed inset below the peninsula, with Brunei and the Kalimantan
coast moved with it (a "context" inset), so both halves fit a tall phone screen at a usable size. Circles: Kuala
Lumpur, Putrajaya and Labuan.
Written from general knowledge and the downloaded Wikipedia articles (tools/downloads/my/wiki/); checked by hand.
Populations: Department of Statistics Malaysia (OpenDOSM, population_state.csv), estimates for 1 January 2026, in
thousands; they add up to DOSM's national 34,389.4 thousand within its rounding (TOTAL_TOL).
"""

A3, A2, CONT = "MYS", "MY", "Asia"
WINDOW = (92.5, -9.5, 109.0, 10.0)
DETAIL = (99.5, -6.6, 109.5, 7.5)
INSETS = [dict(codes=["12", "13", "15"], box=(109.5, 0.8, 119.5, 7.5), to=(104.2, -2.85), pad=0.25, tap=False, context=True, bar="top")]
POP_SOURCE, POP_YEAR, TOTAL, TOTAL_TOL = "DOSM, 1 January 2026 (estimate)", "2026", 34389400, 200
CAP_LL = {"Kota Bharu": [102.238, 6.125], "Malacca City": [102.249, 2.196]}

S, F = "State", "Federal territory"
PARTS = {
    "01": dict(name="Johor", names=["Johore"], capital="Johor Bahru", capAlt=["Johor Baharu", "JB"], pop=4224300, area=19210, kind=S),
    "02": dict(name="Kedah", capital="Alor Setar", capAlt=["Alor Star"], pop=2237400, area=9500, kind=S),
    "03": dict(name="Kelantan", capital="Kota Bharu", pop=1925300, area=15099, kind=S),
    "04": dict(name="Malacca", names=["Melaka"], capital="Malacca City", capAlt=["Melaka", "Malacca", "Bandar Melaka"], pop=1057400, area=1664, kind=S),
    "05": dict(name="Negeri Sembilan", names=["Negri Sembilan"], capital="Seremban", pop=1248500, area=6686, kind=S),
    "06": dict(name="Pahang", capital="Kuantan", pop=1686200, area=36137, kind=S),
    "07": dict(name="Penang", names=["Pulau Pinang", "Pinang"], capital="George Town", capAlt=["Georgetown"], pop=1808300, area=1048, kind=S),
    "08": dict(name="Perak", capital="Ipoh", pop=2577900, area=21035, kind=S, notTypo=["Perlis"]),
    "09": dict(name="Perlis", capital="Kangar", pop=297300, area=821, kind=S, notTypo=["Perak"]),
    "10": dict(name="Selangor", capital="Shah Alam", pop=7454200, area=8104, kind=S),
    "11": dict(name="Terengganu", names=["Trengganu"], capital="Kuala Terengganu", pop=1260900, area=13035, kind=S),
    "12": dict(name="Sabah", capital="Kota Kinabalu", capAlt=["KK"], pop=3767000, area=73631, kind=S),
    "13": dict(name="Sarawak", capital="Kuching", pop=2539800, area=124450, kind=S),
    "14": dict(name="Kuala Lumpur", names=["KL", "Federal Territory of Kuala Lumpur", "Wilayah Persekutuan Kuala Lumpur"], capital="Kuala Lumpur",
               capAlt=["KL"], pop=2082300, area=243, kind=F),
    "15": dict(name="Labuan", names=["Federal Territory of Labuan"], capital="Victoria", capAlt=["Bandar Labuan"], pop=101100, area=91, kind=F),
    "16": dict(name="Putrajaya", names=["Federal Territory of Putrajaya"], capital="Putrajaya", pop=121400, area=49, kind=F),
}

FACTS = {
    "01": dict(local="Johor Darul Ta'zim", demonym="Johorean", dialect="Johor Malay", dish="Laksa Johor and mee rebus", club="Johor Darul Ta'zim",
               river="Johor River", high="Gunung Ledang, 1,276 m", wonder="Endau-Rompin National Park", historic="The Johor Sultanate (after Malacca fell in 1511)",
               landmark="The Sultan Abu Bakar State Mosque and the Johor–Singapore Causeway", known="Industry, links to Singapore, and Legoland Malaysia",
               ruler="Sultan of Johor", ethnic="Malay majority, large Chinese and some Indian communities", half="Peninsula"),
    "02": dict(local="Kedah Darul Aman", demonym="Kedahan", dialect="Kedah Malay", dish="Laksa Kedah", club="Kedah Darul Aman FC",
               high="Gunung Jerai, 1,217 m", wonder="Langkawi's islands and rainforest", historic="One of the oldest Malay kingdoms (Bujang Valley, 1st millennium)",
               landmark="The Langkawi Sky Bridge", unesco="Langkawi UNESCO Global Geopark", known="The 'rice bowl of Malaysia' and Langkawi",
               ruler="Sultan of Kedah", ethnic="Malay majority, Chinese and Indian minorities", half="Peninsula"),
    "03": dict(local="Kelantan Darul Naim", demonym="Kelantanese", dialect="Kelantan Malay", dish="Nasi kerabu (blue rice)", club="Kelantan FA",
               river="Kelantan River", historic="The Kelantan Sultanate", landmark="The Istana Jahar royal palace", known="Malay crafts: batik, songket, kites (wau) and shadow puppets",
               ruler="Sultan of Kelantan", ethnic="Malay (about 95%)", half="Peninsula"),
    "04": dict(local="Melaka", demonym="Malaccan", dialect="Malay, Baba Malay and Kristang (Portuguese creole)", dish="Chicken rice balls and Nyonya laksa",
               river="Malacca River", historic="The Malacca Sultanate (about 1400), then Portuguese, Dutch and British rule", landmark="A Famosa and the Stadthuys",
               unesco="Melaka and George Town, historic cities of the Straits of Malacca", known="Colonial history and Peranakan (Baba-Nyonya) culture",
               ruler="Governor (Yang di-Pertua Negeri)", ethnic="Malay majority, Chinese, Indian, and Peranakan and Portuguese-Eurasian communities", half="Peninsula"),
    "05": dict(local="Negeri Sembilan Darul Khusus", demonym="Negeri Sembilan native", dialect="Negeri Sembilan Malay (Minangkabau-influenced)",
               dish="Masak lemak cili api (spicy coconut curry)", club="Negeri Sembilan FC", wonder="Port Dickson's beaches",
               historic="A federation of nine Minangkabau states", landmark="The Istana Lama at Seri Menanti", known="Minangkabau matrilineal customs (adat perpatih)",
               ruler="Yang di-Pertuan Besar (elected from four royal lines)", ethnic="Malay majority, Chinese and Indian minorities", half="Peninsula"),
    "06": dict(local="Pahang Darul Makmur", demonym="Pahangite", dialect="Pahang Malay", dish="Ikan patin tempoyak (river fish in fermented durian)",
               club="Sri Pahang FC", river="Pahang River, the peninsula's longest", high="Gunung Tahan, 2,187 m: the peninsula's highest",
               wonder="Taman Negara and the Cameron Highlands", historic="The Pahang Sultanate", landmark="The Cameron Highlands tea plantations",
               known="Rainforest, tea and highland resorts (Genting)", city="Kuantan is the capital and largest", ruler="Sultan of Pahang",
               ethnic="Malay majority, Chinese and Orang Asli minorities", half="Peninsula"),
    "07": dict(local="Pulau Pinang", demonym="Penangite", dialect="Penang Hokkien", dish="Char kway teow, asam laksa and nasi kandar", club="Penang FC",
               high="Penang Hill, 833 m", historic="A British trading post from 1786 (one of the Straits Settlements)", landmark="Kek Lok Si Temple and George Town's street art",
               unesco="Melaka and George Town, historic cities of the Straits of Malacca", known="Street food and electronics manufacturing",
               ruler="Governor (Yang di-Pertua Negeri)", ethnic="Chinese plurality, Malay and Indian communities", half="Peninsula"),
    "08": dict(local="Perak Darul Ridzuan", demonym="Perakian", dialect="Perak Malay", dish="Ipoh white coffee and bean sprout chicken", club="Perak FC",
               river="Perak River", high="Gunung Korbu, 2,183 m", wonder="The limestone caves around Ipoh and Royal Belum State Park",
               historic="The Perak Sultanate; the tin rush of the 1800s", landmark="Kellie's Castle", unesco="The archaeological heritage of the Lenggong Valley",
               known="Tin mining history and Ipoh's food", ruler="Sultan of Perak", ethnic="Malay, Chinese and Indian", half="Peninsula"),
    "09": dict(local="Perlis Indera Kayangan", demonym="Perlisian", dialect="Northern Malay", dish="Harumanis mango", club="Perlis FA",
               wonder="The Wang Kelian and Gua Kelam caves", historic="Split from Kedah in 1843", known="The smallest state; Harumanis mangoes",
               ruler="Raja of Perlis", ethnic="Malay majority, Chinese and Siamese minorities", half="Peninsula"),
    "10": dict(local="Selangor Darul Ehsan", demonym="Selangorean", dish="Nasi lemak and satay Kajang", club="Selangor FC", river="Klang and Selangor rivers",
               wonder="The Batu Caves and the fireflies of Kuala Selangor", historic="The Selangor Sultanate (1766)", landmark="The Batu Caves' golden statue of Murugan",
               known="The most populous and richest state; Port Klang", city="Petaling Jaya and Subang Jaya (Shah Alam is the capital)", ruler="Sultan of Selangor",
               ethnic="Malay, Chinese and Indian", half="Peninsula"),
    "11": dict(local="Terengganu Darul Iman", demonym="Terengganuan", dialect="Terengganu Malay", dish="Keropok lekor (fish crackers) and nasi dagang",
               club="Terengganu FC", wonder="The Perhentian and Redang islands", historic="The Terengganu Sultanate; the Terengganu Inscription Stone (1303)",
               landmark="The Crystal Mosque", known="Islands, turtles and oil and gas", ruler="Sultan of Terengganu", ethnic="Malay (about 95%)", half="Peninsula"),
    "12": dict(local="Sabah", demonym="Sabahan", dialect="Sabah Malay, Kadazandusun and Bajau", dish="Hinava (raw fish salad)", club="Sabah FC",
               high="Mount Kinabalu, 4,095 m: Malaysia's highest", wonder="Mount Kinabalu, Sipadan and the orangutans of Sepilok",
               historic="North Borneo (a British chartered company territory)", landmark="Mount Kinabalu", unesco="Kinabalu Park",
               known="Diving, wildlife and Mount Kinabalu", ruler="Governor (Yang di-Pertua Negeri)", ethnic="Kadazan-Dusun, Bajau, Murut, Malay and Chinese",
               half="Borneo"),
    "13": dict(local="Sarawak", demonym="Sarawakian", dialect="Sarawak Malay, Iban and Bidayuh", dish="Sarawak laksa and kolo mee", club="Kuching City FC",
               river="Rajang River, Malaysia's longest", high="Gunung Murud, 2,423 m", wonder="Gunung Mulu's caves and the Niah Caves",
               historic="Ruled by the 'White Rajahs' (the Brooke family), 1841–1946", landmark="The Sarawak State Legislative Assembly building in Kuching",
               unesco="Gunung Mulu National Park and the Niah Caves", known="The largest state: rainforest, longhouses and oil", city="Kuching is the capital and largest",
               ruler="Governor (Yang di-Pertua Negeri); led by a Premier", ethnic="Iban, Chinese, Malay, Bidayuh and Melanau", half="Borneo"),
    "14": dict(local="Wilayah Persekutuan Kuala Lumpur", demonym="KLite", dish="Nasi lemak and bak kut teh", club="Kuala Lumpur City FC",
               river="Klang and Gombak rivers (the 'muddy confluence')", historic="A tin-mining settlement (1857), capital since independence",
               landmark="The Petronas Twin Towers", known="The capital and largest city", company="Petronas", ruler="None (a federal territory)",
               ethnic="Malay, Chinese and Indian", half="Peninsula"),
    "15": dict(local="Wilayah Persekutuan Labuan", demonym="Labuanese", wonder="Wreck diving", historic="A British crown colony from 1848",
               known="Offshore finance and duty-free shopping", ruler="None (a federal territory)", ethnic="Malay, Kadazan-Dusun, Chinese and Bajau", half="Borneo"),
    "16": dict(local="Wilayah Persekutuan Putrajaya", demonym="Putrajayan", wonder="Putrajaya Lake and its wetlands", historic="Built from 1995 as the government's seat",
               landmark="The Putra Mosque and the Perdana Putra", known="The federal government's administrative centre", ruler="None (a federal territory)",
               ethnic="Mostly Malay", half="Peninsula"),
}
