"""Hand-picked battles for the History games (History_games.md, H2), added to Wikidata's fame ranking so the set
covers every era and region, not just the best-known European wars. Each entry is the title of the battle's
English Wikipedia article; tools/build_battles.py looks them up in Wikidata and prints any it can't find, so fix
those here. Naval battles are marked by Wikidata itself, not here.
"""
EXTRA = {
    "Ancient (before 500)": [
        "Battle of Kadesh", "Battle of Marathon", "Battle of Thermopylae", "Battle of Salamis",
        "Battle of Gaugamela", "Battle of the Hydaspes", "Battle of Changping", "Battle of Gaixia",
        "Battle of Cannae", "Battle of Zama", "Battle of Alesia", "Battle of Actium", "Battle of the Teutoburg Forest",
        "Battle of Red Cliffs", "Battle of Adrianople", "Battle of the Catalaunian Plains",
    ],
    "Medieval (500-1500)": [
        "Battle of Badr", "Battle of Yarmouk", "Battle of al-Qadisiyyah", "Battle of Karbala", "Battle of Tours",
        "Battle of Talas", "Battle of Hastings", "Battle of Manzikert", "Battle of Hattin",
        "Battle of Las Navas de Tolosa", "Battle on the Ice", "Battle of Mohi", "Battle of Legnica",
        "Battle of Ain Jalut", "Battle of Bannockburn", "Battle of Crécy", "Battle of Kulikovo", "Battle of Kosovo",
        "Battle of Grunwald", "Battle of Agincourt", "Fall of Constantinople", "Battle of Bosworth Field",
    ],
    "Early modern (1500-1800)": [
        "Battle of Diu (1509)", "Battle of Chaldiran", "Fall of Tenochtitlan", "First Battle of Panipat",
        "Battle of Mohács", "Battle of Cajamarca", "Battle of Lepanto", "Battle of Haldighati",
        "Battle of Gravelines", "Battle of Myeongnyang", "Battle of Sekigahara", "Battle of Lützen (1632)",
        "Battle of Naseby", "Battle of Vienna", "Battle of Blenheim", "Battle of Poltava", "Battle of Plassey",
        "Battle of the Plains of Abraham", "Third Battle of Panipat", "Battles of Lexington and Concord",
        "Battle of Bunker Hill", "Battles of Saratoga", "Siege of Yorktown", "Battle of the Nile",
    ],
    "1800s": [
        "Battle of Assaye", "Battle of Vertières", "Battle of Trafalgar", "Battle of Austerlitz",
        "Battle of Borodino", "Battle of Leipzig", "Battle of New Orleans", "Battle of Waterloo",
        "Battle of Chacabuco", "Battle of Maipú", "Battle of Boyacá", "Battle of Carabobo", "Battle of Pichincha",
        "Battle of Ayacucho", "Battle of Navarino", "Battle of Blood River", "Battle of the Alamo",
        "Battle of San Jacinto", "Battle of Solferino", "Battle of Hampton Roads", "Battle of Antietam",
        "Battle of Puebla", "Battle of Gettysburg", "Battle of Gate Pā", "Battle of Riachuelo",
        "Battle of Königgrätz", "Battle of Sedan (1870)", "Battle of the Little Bighorn", "Battle of Shiroyama",
        "Battle of Isandlwana", "Battle of Adwa", "Battle of Omdurman",
    ],
    "1900-1945": [
        "Battle of Mukden", "Battle of Tsushima", "Battle of Tannenberg", "First Battle of the Marne",
        "Gallipoli campaign", "Battle of Verdun", "Battle of Jutland", "Battle of the Somme",
        "Battle of Vimy Ridge", "Battle of Passchendaele", "Battle of Caporetto", "Battle of Shanghai",
        "Battle of the River Plate", "Battle of Dunkirk", "Battle of Britain", "Battle of Moscow",
        "Siege of Leningrad", "Attack on Pearl Harbor", "Battle of Singapore", "Battle of the Coral Sea",
        "Battle of Midway", "Kokoda Track campaign", "Guadalcanal campaign", "Second Battle of El Alamein",
        "Battle of Stalingrad", "Battle of Kursk", "Battle of Monte Cassino", "Battle of Imphal",
        "Battle of Kohima", "Normandy landings", "Battle of Leyte Gulf", "Battle of the Bulge",
        "Battle of Iwo Jima", "Battle of Okinawa", "Battle of Berlin",
    ],
    "After 1945": [
        "Battle of Inchon", "Battle of Chosin Reservoir", "Battle of Dien Bien Phu", "Battle of Algiers",
        "Bay of Pigs Invasion", "Battle of Ia Drang", "Battle of Long Tan", "Battle of Huế",
        "Battle of Goose Green", "Battle of Cuito Cuanavale", "Battle of 73 Easting", "Battle of Mogadishu (1993)",
    ],
}
