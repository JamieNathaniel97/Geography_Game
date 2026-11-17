"""Hand-picked shipwrecks for the History games (History_games.md, H3), added to Wikidata's fame ranking so the set
covers every era and ocean. Each entry is the title of the English Wikipedia article (about the ship or the wreck);
tools/build_wrecks.py looks them up in Wikidata and prints any it can't find, so fix those here.
"""
EXTRA = {
    "Ancient and medieval": [
        "Uluburun shipwreck", "Antikythera wreck", "Belitung shipwreck", "Nanhai One",
    ],
    "Age of sail (1500-1850)": [
        "Mary Rose", "Flor de la Mar", "Nuestra Señora de Atocha", "Batavia (ship)", "Vasa (ship)", "Kronan (ship)",
        "La Belle (ship)", "Queen Anne's Revenge", "Whydah Gally", "San José (galleon)", "Zuytdorp",
        "HMS Victory (1737)", "HMS Royal George (1756)", "HMS Bounty", "Tek Sing", "HMS Erebus (1826)",
        "HMS Terror (1813)",
    ],
    "Steam and early 1900s": [
        "SS Arctic", "RMS Tayleur", "Royal Charter (ship)", "SS Central America", "Sultana (steamboat)",
        "USS Monitor", "H. L. Hunley (submarine)", "Mary Celeste", "SS Yongala", "RMS Titanic",
        "Endurance (1912 ship)", "RMS Empress of Ireland", "RMS Lusitania", "SS Eastland", "HMHS Britannic",
    ],
    "Second World War": [
        "USS Arizona (BB-39)", "HMS Hood", "German battleship Bismarck", "SS Thistlegorm",
        "SS President Coolidge", "USS Indianapolis (CA-35)", "Japanese battleship Yamato", "MV Wilhelm Gustloff",
    ],
    "After 1945": [
        "SS Andrea Doria", "SS Edmund Fitzgerald", "ARA General Belgrano", "SS Admiral Nakhimov", "MV Doña Paz",
    ],
}
