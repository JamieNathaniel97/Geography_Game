"""Egypt's 27 governorates (Egypt_plan.md): the config for tools/build_country.py and the Learning card facts.
Card fact fields: see tools/at_facts.py ("local" is the name in Arabic, in the cards' Arabic font, right to left);
Egypt's own two: part (Upper or Lower Egypt, the Sinai or the desert) and sites (ancient sites). Games 5 and 6: "flags
and emblems": 25 governorates have flags on Commons, and Cairo and Luxor have emblems instead (FLAG_FALLBACK).
Disputed areas (DISPUTED): the Hala'ib Triangle (governed by Egypt, claimed by Sudan) is part of the Red Sea governorate
with its edges dotted; Bir Tawil (claimed by neither) is grey, untappable and labelled "Bir Tawil (unclaimed)".
Written from general knowledge and the downloaded Wikipedia articles (tools/downloads/eg/wiki/en, ar); checked by hand.
Populations: CAPMAS estimates for November 2023 (the newest by governorate), from "Governorates of Egypt"; they add up to
the table's national 106,668,704.
"""

A3, A2, CONT = "EGY", "EG", "Africa"
WINDOW = (19.0, 15.0, 41.0, 35.0)
DETAIL = (24.6, 21.5, 37.1, 31.8)
DISPUTED = [dict(ne="Halayib Triangle", join="BA"), dict(ne="Bir Tawil", grey="T-BRT", name="Bir Tawil (unclaimed)")]
FLAG_FALLBACK = "coats"
POP_SOURCE, POP_YEAR, TOTAL = "CAPMAS estimates, November 2023", "2023", 106668704
CAP_LL = {"Mansoura": [31.378, 31.040], "Damietta": [31.814, 31.417], "Faiyum": [30.842, 29.308], "Minya": [30.744, 28.110],
          "Kharga": [30.546, 25.451], "Arish": [33.799, 31.132], "Banha": [31.188, 30.460], "El Tor": [33.617, 28.241]}

G = "Governorate"
PARTS = {
    "ALX": dict(name="Alexandria", names=["Al Iskandariyah", "Iskandariya"], capital="Alexandria", pop=5703824, area=2300, kind=G),
    "ASN": dict(name="Aswan", capital="Aswan", pop=1698201, area=62726, kind=G),
    "AST": dict(name="Asyut", names=["Assiut", "Asyout"], capital="Asyut", capAlt=["Assiut"], pop=5071485, area=25926, kind=G),
    "BH": dict(name="Beheira", names=["Al Buhayrah", "Buhayra"], capital="Damanhur", pop=6940234, area=9826, kind=G),
    "BNS": dict(name="Beni Suef", names=["Bani Suwayf"], capital="Beni Suef", pop=3618395, area=10954, kind=G),
    "C": dict(name="Cairo", names=["Al Qahirah", "Qahira"], capital="Cairo", pop=10456284, area=3085, kind=G),
    "DK": dict(name="Dakahlia", names=["Ad Daqahliyah", "Daqahlia"], capital="Mansoura", capAlt=["El Mansoura"], pop=7058212, area=3538, kind=G),
    "DT": dict(name="Damietta", names=["Dumyat"], capital="Damietta", capAlt=["Dumyat"], pop=2023380, area=910, kind=G),
    "FYM": dict(name="Faiyum", names=["Fayoum", "Al Fayyum", "Fayum"], capital="Faiyum", capAlt=["Fayoum"], pop=4141222, area=6068, kind=G),
    "GH": dict(name="Gharbia", names=["Al Gharbiyah"], capital="Tanta", pop=5483000, area=1942, kind=G),
    "GZ": dict(name="Giza", names=["Al Jizah", "Gizeh"], capital="Giza", pop=9534283, area=13184, kind=G),
    "IS": dict(name="Ismailia", names=["Al Isma'iliyah"], capital="Ismailia", pop=1482999, area=5067, kind=G),
    "KFS": dict(name="Kafr El Sheikh", names=["Kafr el-Sheikh", "Kafr ash Shaykh"], capital="Kafr El Sheikh", pop=3731540, area=3467, kind=G),
    "LX": dict(name="Luxor", names=["Al Uqsur"], capital="Luxor", pop=1429385, area=460, kind=G),
    "MT": dict(name="Matrouh", names=["Matruh", "Marsa Matruh"], capital="Marsa Matruh", capAlt=["Mersa Matruh"], pop=580304, area=166563, kind=G),
    "MN": dict(name="Minya", names=["Al Minya", "El Minya"], capital="Minya", pop=6332918, area=32279, kind=G),
    "MNF": dict(name="Monufia", names=["Menoufia", "Al Minufiyah"], capital="Shibin El Kom", pop=4743341, area=2499, kind=G),
    "WAD": dict(name="New Valley", names=["Al Wadi al Jadid", "El Wadi El Gedid"], capital="Kharga", capAlt=["El Kharga"], pop=324600, area=440098, kind=G),
    "SIN": dict(name="North Sinai", names=["Shamal Sina'", "Shamal Sina"], capital="Arish", capAlt=["El Arish", "Al Arish"], pop=544494, area=28992, kind=G,
                notTypo=["South Sinai"]),
    "PTS": dict(name="Port Said", names=["Bur Sa'id"], capital="Port Said", pop=835193, area=1345, kind=G),
    "KB": dict(name="Qalyubia", names=["Qalyubiyya", "Al Qalyubiyah", "Kalyubia"], capital="Banha", capAlt=["Benha"], pop=6137896, area=1124, kind=G),
    "KN": dict(name="Qena", names=["Qina", "Kena"], capital="Qena", pop=3651215, area=10798, kind=G),
    "BA": dict(name="Red Sea", names=["Al Bahr al Ahmar"], capital="Hurghada", pop=409394, area=119099, kind=G),
    "SHR": dict(name="Sharqia", names=["Ash Sharqiyah", "Sharkia"], capital="Zagazig", pop=8032683, area=4911, kind=G),
    "SHG": dict(name="Sohag", names=["Suhaj"], capital="Sohag", pop=5714903, area=11022, kind=G),
    "JS": dict(name="South Sinai", names=["Janub Sina'", "Janub Sina"], capital="El Tor", capAlt=["Tor", "At Tur"], pop=145934, area=31272, kind=G,
               notTypo=["North Sinai"]),
    "SUZ": dict(name="Suez", names=["As Suways"], capital="Suez", pop=843385, area=9002, kind=G),
}

LE, UE, CZ = "Lower Egypt (the Nile Delta)", "Upper Egypt (the Nile valley)", "The Suez Canal zone"
FACTS = {
    "ALX": dict(local="الإسكندرية", dish="Kebda iskandarani (spiced liver) and seafood", club="Al Ittihad Alexandria", historic="The capital of Ptolemaic Egypt (founded 331 BC)",
                landmark="The Citadel of Qaitbay and the Bibliotheca Alexandrina", known="Egypt's main port and its Mediterranean summer city",
                part="Lower Egypt (the Mediterranean coast)", sites="The catacombs of Kom El Shoqafa and Pompey's Pillar"),
    "ASN": dict(local="أسوان", river="Nile", wonder="Lake Nasser and the Aswan High Dam", landmark="The temples of Abu Simbel", unesco="The Nubian Monuments from Abu Simbel to Philae",
                known="Nubian culture, granite and the High Dam", part=UE, sites="Abu Simbel, Philae and Kom Ombo"),
    "AST": dict(local="أسيوط", river="Nile", landmark="The Monastery of the Virgin Mary (Deir el-Muharraq)", known="Upper Egypt's biggest city and a large Coptic community",
                part=UE, sites="The tombs of Asyut's ancient nomarchs"),
    "BH": dict(local="البحيرة", historic="Rosetta (Rashid), where the Rosetta Stone was found (1799)", landmark="The monasteries of Wadi El Natrun",
               known="Farming in the western Delta", part=LE, sites="Rosetta's Ottoman houses and the Wadi El Natrun monasteries"),
    "BNS": dict(local="بني سويف", river="Nile", known="Cement and marble", part=UE, sites="The Meidum pyramid"),
    "C": dict(local="القاهرة", dish="Koshari and ful medames", club="Al Ahly", river="Nile", historic="The capital since the Fatimids founded it (969)",
              landmark="The Citadel of Saladin and the Egyptian Museum", unesco="Historic Cairo", person="Naguib Mahfouz (Nobel laureate)",
              known="The capital: Africa's and the Arab world's largest city", part="Greater Cairo, where the Delta meets the valley", sites="Islamic Cairo's mosques and the Egyptian Museum"),
    "DK": dict(local="الدقهلية", historic="The Battle of Mansoura (1250), where the Seventh Crusade was defeated", person="Umm Kulthum (singer)",
               known="Farming and Mansoura University", part=LE),
    "DT": dict(local="دمياط", dish="Damietta's sweets and white cheese", wonder="Ras El Bar, where the Nile meets the sea", known="Furniture making",
               part=LE),
    "FYM": dict(local="الفيوم", wonder="Wadi El Hitan (Whale Valley) and Lake Qarun", unesco="Wadi Al-Hitan (Whale Valley)", known="An oasis linked to the Nile, and the Faiyum mummy portraits",
                part="Upper Egypt (Middle Egypt: an oasis by the Nile valley)", sites="The Hawara pyramid"),
    "GH": dict(local="الغربية", festival="The Moulid of Sayyid al-Badawi in Tanta", known="Cotton and textiles (El Mahalla El Kubra)", part=LE),
    "GZ": dict(local="الجيزة", club="Zamalek", river="Nile", landmark="The Pyramids of Giza and the Great Sphinx", unesco="Memphis and its Necropolis (Giza to Dahshur)",
               known="The pyramids and the Grand Egyptian Museum", part="Greater Cairo and Upper Egypt", sites="The Pyramids of Giza, Saqqara and Dahshur"),
    "IS": dict(local="الإسماعيلية", club="Ismaily SC", wonder="Lake Timsah", landmark="The Suez Canal Authority's headquarters", known="The Suez Canal", part=CZ),
    "KFS": dict(local="كفر الشيخ", wonder="Lake Burullus", known="Rice and fish farming", part=LE),
    "LX": dict(local="الأقصر", river="Nile", landmark="Karnak Temple and the Valley of the Kings", unesco="Ancient Thebes with its Necropolis",
               known="'The world's greatest open-air museum', and hot-air balloons at dawn", part=UE, sites="Karnak, Luxor Temple, the Valley of the Kings and Hatshepsut's temple"),
    "MT": dict(local="مطروح", dialect="Bedouin Arabic, and Siwi (a Berber language) in Siwa", wonder="Siwa Oasis and the Mediterranean beaches",
               historic="The battles of El Alamein (1942)", landmark="The El Alamein war cemeteries", known="Siwa, beaches and Bedouin culture",
               part="The Western Desert and the Mediterranean coast", sites="The Temple of the Oracle of Amun at Siwa"),
    "MN": dict(local="المنيا", river="Nile", known="The 'bride of Upper Egypt' and a large Coptic community", part="Upper Egypt (Middle Egypt)",
               sites="Tell el-Amarna (Akhenaten's capital) and the tombs of Beni Hasan"),
    "MNF": dict(local="المنوفية", person="Presidents Anwar Sadat and Hosni Mubarak were both born here", known="Farming in the southern Delta", part=LE),
    "WAD": dict(local="الوادي الجديد", wonder="The White Desert and the oases of Kharga, Dakhla and Farafra", known="The largest governorate: desert oases",
                part="The Western Desert", sites="The Temple of Hibis and the Bagawat necropolis"),
    "SIN": dict(local="شمال سيناء", historic="Occupied by Israel 1967–1982", known="Palm groves and Bedouin culture", part="The Sinai"),
    "PTS": dict(local="بورسعيد", club="Al Masry", landmark="The domed Suez Canal Authority building", known="A port and free zone at the canal's northern end", part=CZ),
    "KB": dict(local="القليوبية", known="Industry around Shubra El Kheima, north of Cairo", city="Shubra El Kheima", part=LE),
    "KN": dict(local="قنا", river="Nile", landmark="The Temple of Hathor at Dendera", known="Sugar cane", part=UE, sites="Dendera Temple"),
    "BA": dict(local="البحر الأحمر", wonder="Coral reefs and the Eastern Desert's mountains", historic="Includes the Hala'ib Triangle (also claimed by Sudan)",
               known="Diving and resorts (Hurghada, Marsa Alam)", part="The Eastern Desert and the Red Sea coast", sites="Roman quarries at Mons Claudianus"),
    "SHR": dict(local="الشرقية", person="Ahmed Orabi (leader of the 1879–1882 revolt)", known="Farming in the eastern Delta", part=LE,
                sites="Tanis and Bubastis (Tell Basta)"),
    "SHG": dict(local="سوهاج", river="Nile", known="Akhmim's textiles", part=UE, sites="Abydos and the Temple of Seti I"),
    "JS": dict(local="جنوب سيناء", high="Mount Catherine, 2,629 m: Egypt's highest", wonder="The Red Sea reefs of Ras Mohammed, and Mount Sinai",
               landmark="Saint Catherine's Monastery", unesco="The Saint Catherine Area", known="Diving and resorts (Sharm El Sheikh, Dahab)", part="The Sinai"),
    "SUZ": dict(local="السويس", landmark="The southern entrance of the Suez Canal", known="Oil refining and the canal's port", part=CZ),
}
