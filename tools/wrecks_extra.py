"""Hand-picked shipwrecks for the History games (History_games.md, H3), added to Wikidata's fame ranking so the set
covers every era and ocean. Each entry is the title of the English Wikipedia article (about the ship or the wreck);
tools/build_wrecks.py looks them up in Wikidata and prints any it can't find, so fix those here.
Only wrecks whose place is known (decided 2026-11-17): no wrecks that have never been found, such as the Flor de la
Mar, the Santa María, the SS Arctic or the ARA General Belgrano, none whose position is secret (the San José galleon)
and none whose identification is doubtful (the Mary Celeste).
"""
EXTRA = {
    "Ancient and medieval": [
        "Uluburun shipwreck", "Antikythera wreck", "Belitung shipwreck", "Nanhai One",
    ],
    "Age of sail (1500-1850)": [
        "Mary Rose", "Nuestra Señora de Atocha", "Batavia (ship)", "Vasa (ship)", "Kronan (ship)",
        "La Belle (ship)", "Queen Anne's Revenge", "Whydah Gally", "Zuytdorp",
        "HMS Victory (1737)", "HMS Royal George (1756)", "HMS Bounty", "Tek Sing", "HMS Erebus (1826)",
        "HMS Terror (1813)",
    ],
    "Steam and early 1900s": [
        "RMS Tayleur", "Royal Charter (ship)", "SS Central America", "Sultana (steamboat)",
        "USS Monitor", "H. L. Hunley (submarine)", "SS Yongala", "RMS Titanic",
        "Endurance (1912 ship)", "RMS Empress of Ireland", "RMS Lusitania", "SS Eastland", "HMHS Britannic",
    ],
    "Second World War": [
        "USS Arizona (BB-39)", "HMS Hood", "German battleship Bismarck", "SS Thistlegorm",
        "SS President Coolidge", "USS Indianapolis (CA-35)", "Japanese battleship Yamato", "MV Wilhelm Gustloff",
    ],
    "After 1945": [
        "SS Andrea Doria", "SS Edmund Fitzgerald", "SS Admiral Nakhimov", "MS Estonia", "Russian submarine Kursk (K-141)", "MV Le Joola", "Costa Concordia", "MV Sewol",
        "ARA San Juan (S-42)",
    ],
}


# Hand-picked wrecks Wikidata has no wreck position for (checked 2026-11-18): written here from the published accounts
# of where each wreck lies. Positions are approximate (to a few kilometres). Only found wrecks: the SS Arctic (never
# found) and the San José galleon (its position is kept secret) are left out, as is the Doña Paz (not surveyed).
# year: when it sank; deaths: lives lost; found: when the wreck was found; raised: a note if it's now ashore.
HAND = {
    "RMS Lusitania": dict(name="RMS Lusitania", desc="British ocean liner, torpedoed by a German U-boat", year=1915, ll=[-8.546, 51.413], deaths=1198, found=1935, war=True),
    "HMHS Britannic": dict(name="HMHS Britannic", desc="British hospital ship, the Titanic's sister, sunk by a mine", year=1916, ll=[24.285, 37.701], deaths=30, found=1975, war=True),
    "SS Edmund Fitzgerald": dict(name="SS Edmund Fitzgerald", desc="American lake freighter lost in a storm on Lake Superior", year=1975, ll=[-85.108, 46.999], deaths=29, found=1975),
    "Mary Rose": dict(name="Mary Rose", desc="Henry VIII's warship, sunk in the Solent in battle", year=1545, ll=[-1.106, 50.766], deaths=500, found=1971, war=True, raised="Raised in 1982: now in its own museum in Portsmouth"),
    "Vasa (ship)": dict(name="Vasa", desc="Swedish warship that sank on her maiden voyage", year=1628, ll=[18.103, 59.322], deaths=30, found=1956, raised="Raised in 1961: now in the Vasa Museum, Stockholm"),
    "Batavia (ship)": dict(name="Batavia", desc="Dutch East India Company ship wrecked on the Houtman Abrolhos", year=1629, ll=[113.794, -28.491], found=1963),
    "Endurance (1912 ship)": dict(name="Endurance", desc="Shackleton's ship, crushed by the Antarctic ice", year=1915, ll=[-52.326, -68.739], deaths=0, found=2022),
    "H. L. Hunley (submarine)": dict(name="H. L. Hunley", desc="Confederate submarine, the first to sink a warship", year=1864, ll=[-79.773, 32.722], deaths=8, found=1995, war=True, raised="Raised in 2000: now in North Charleston"),
    "HMS Bounty": dict(name="HMS Bounty", desc="Royal Navy ship burned by her mutineers at Pitcairn", year=1790, ll=[-130.096, -25.068], deaths=0, found=1957),
    "HMS Erebus (1826)": dict(name="HMS Erebus", desc="Franklin's lost Arctic expedition ship", year=1848, ll=[-98.863, 68.244], deaths=129, found=2014),
    "HMS Terror (1813)": dict(name="HMS Terror", desc="Franklin's lost Arctic expedition ship", year=1848, ll=[-97.92, 68.97], deaths=129, found=2016),
    "HMS Royal George (1756)": dict(name="HMS Royal George", desc="Royal Navy flagship that sank at anchor at Spithead", year=1782, ll=[-1.11, 50.765], deaths=900),
    "HMS Victory (1737)": dict(name="HMS Victory (1737)", desc="Royal Navy flagship lost in a storm in the English Channel", year=1744, ll=[-2.8, 49.75], deaths=1100, found=2008),
    "Japanese battleship Yamato": dict(name="Yamato", desc="Japanese battleship, the largest ever built", year=1945, ll=[128.067, 30.717], deaths=3055, found=1985, war=True),
    "La Belle (ship)": dict(name="La Belle", desc="La Salle's ship, wrecked in Matagorda Bay, Texas", year=1686, ll=[-96.377, 28.625], found=1995, raised="Raised in 1997: now in the Bullock Museum, Austin"),
    "MV Le Joola": dict(name="MV Le Joola", desc="Senegalese ferry that capsized off the Gambia", year=2002, ll=[-17.13, 13.55], deaths=1863, found=2002),
    "MV Sewol": dict(name="MV Sewol", desc="South Korean ferry that capsized off Jindo", year=2014, ll=[125.95, 34.22], deaths=304, found=2014, raised="Raised in 2017: now at Mokpo"),
    "MV Wilhelm Gustloff": dict(name="MV Wilhelm Gustloff", desc="German liner carrying refugees, torpedoed in the Baltic", year=1945, ll=[17.417, 55.067], deaths=9400, found=1946, war=True),
    "RMS Empress of Ireland": dict(name="RMS Empress of Ireland", desc="Canadian liner sunk in a collision in the St Lawrence", year=1914, ll=[-68.4, 48.63], deaths=1012, found=1964),
    "RMS Tayleur": dict(name="RMS Tayleur", desc="Emigrant clipper wrecked on Lambay Island, Ireland", year=1854, ll=[-6.01, 53.492], deaths=380),
    "Royal Charter (ship)": dict(name="Royal Charter", desc="Steam clipper wrecked off Anglesey in a great storm", year=1859, ll=[-4.25, 53.357], deaths=450),
    "Russian submarine Kursk (K-141)": dict(name="Kursk", desc="Russian nuclear submarine lost in the Barents Sea", year=2000, ll=[37.58, 69.617], deaths=118, found=2000, raised="Raised in 2001 and broken up"),
    "SS Admiral Nakhimov": dict(name="SS Admiral Nakhimov", desc="Soviet liner sunk in a collision off Novorossiysk", year=1986, ll=[37.83, 44.68], deaths=423, found=1986),
    "SS Andrea Doria": dict(name="SS Andrea Doria", desc="Italian liner sunk in a collision off Nantucket", year=1956, ll=[-69.85, 40.49], deaths=46, found=1956),
    "SS Central America": dict(name="SS Central America", desc="American steamship lost in a hurricane with a cargo of gold", year=1857, ll=[-76.9, 31.6], deaths=425, found=1988),
    "SS Eastland": dict(name="SS Eastland", desc="Passenger ship that rolled over in the Chicago River", year=1915, ll=[-87.633, 41.887], deaths=844, found=1915, raised="Raised in 1915 and used again"),
    "SS Thistlegorm": dict(name="SS Thistlegorm", desc="British cargo ship bombed in the Red Sea", year=1941, ll=[33.92, 27.81], deaths=9, found=1955, war=True),
    "SS Yongala": dict(name="SS Yongala", desc="Australian passenger ship lost in a cyclone", year=1911, ll=[147.622, -19.304], deaths=122, found=1958),
    "Tek Sing": dict(name="Tek Sing", desc="Chinese junk wrecked in the Gaspar Strait", year=1822, ll=[107.08, -2.42], deaths=1600, found=1999),
    "USS Arizona (BB-39)": dict(name="USS Arizona", desc="US battleship sunk in the attack on Pearl Harbor", year=1941, ll=[-157.95, 21.365], deaths=1177, found=1941, war=True),
    "USS Indianapolis (CA-35)": dict(name="USS Indianapolis", desc="US cruiser torpedoed after delivering parts of the atomic bomb", year=1945, ll=[134.8, 12.03], deaths=879, found=2017, war=True),
    "USS Monitor": dict(name="USS Monitor", desc="Union ironclad lost in a storm off Cape Hatteras", year=1862, ll=[-75.408, 35.0], deaths=16, found=1973),
    "Whydah Gally": dict(name="Whydah Gally", desc="Pirate ship wrecked off Cape Cod", year=1717, ll=[-69.97, 41.93], deaths=144, found=1984),
    "Zuytdorp": dict(name="Zuytdorp", desc="Dutch East India Company ship wrecked on the Western Australian coast", year=1712, ll=[113.95, -27.18], found=1927),
    "ARA San Juan (S-42)": dict(name="ARA San Juan", desc="Argentine submarine lost in the South Atlantic", year=2017, ll=[-59.77, -45.95], deaths=44, found=2018),
    "Nanhai One": dict(name="Nanhai One", desc="Song dynasty merchant ship", year=1180, ll=[111.9, 21.55], found=1987, raised="Raised in 2007: now in a museum at Yangjiang"),
}
