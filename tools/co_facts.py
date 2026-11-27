"""Colombia's 32 departments and Bogotá (Colombia_plan.md): the config for tools/build_country.py and the Learning card
facts. Card fact fields: see tools/at_facts.py; Colombia's own three: region (natural region), crop (famous coffee, fruit
or crop), music (music style). Games 5 and 6: flags (all 33).
Bogotá (a Capital District inside Cundinamarca, Natural Earth's "CO-CUN" twin) gets a circle; Cundinamarca's government
sits in Bogotá, outside the department, so it sits out the capitals games. San Andrés and Providencia are moved closer
into a framed inset with an oval; Malpelo and the far cays are left off.
Written from general knowledge and the downloaded Wikipedia articles (tools/downloads/co/wiki/); checked by hand.
Populations: Census 2018 (DANE, adjusted total), from "2018 Colombian census" (its first row, labelled Cundinamarca, is
Bogotá); the 33 add up to 48,258,494.
"""

A3, A2, CONT = "COL", "CO", "South America"
WINDOW = (-85.0, -10.0, -62.0, 15.5)
DETAIL = (-80.3, -4.3, -66.8, 12.8)
NE_FIX = {("CO-CUN", "Bogota"): "DC"}
DROP = ("X01~",)
CLIP = [(-79.5, -4.5, -66.5, 12.7), (-81.85, 12.4, -81.3, 13.5)]
INSETS = [dict(codes=["SAP"], box=(-81.85, 12.4, -81.3, 13.5), to=(-79.7, 11.0), pad=0.2)]
# (the framed insets get square tap areas the shape of their frames: tools/build_country.py)
POP_SOURCE, POP_YEAR, TOTAL = "DANE, Census 2018", "2018 census", 48258494
CAP_LL = {}

D = "Department"


def P(name, cap, pop, area, *names, **kw):
    return dict(name=name, names=list(names) + [name + " Department"], capital=cap, pop=pop, area=area, kind=kw.pop("kind", D), **kw)


PARTS = {
    "DC": P("Bogotá", "Bogotá", 7412566, 1587, "Bogota", "Capital District", "Bogotá D.C.", "Santa Fe de Bogotá", capAlt=["Bogota"], kind="Capital District"),
    "AMA": P("Amazonas", "Leticia", 76589, 109665),
    "ANT": P("Antioquia", "Medellín", 6407102, 63612, capAlt=["Medellin"]),
    "ARA": P("Arauca", "Arauca", 262174, 23818),
    "ATL": P("Atlántico", "Barranquilla", 2535517, 3388, "Atlantico"),
    "BOL": P("Bolívar", "Cartagena", 2070110, 25978, "Bolivar", capAlt=["Cartagena de Indias"]),
    "BOY": P("Boyacá", "Tunja", 1217376, 23189, "Boyaca"),
    "CAL": P("Caldas", "Manizales", 998255, 7888),
    "CAQ": P("Caquetá", "Florencia", 401849, 88965, "Caqueta"),
    "CAS": P("Casanare", "Yopal", 420504, 44640),
    "CAU": P("Cauca", "Popayán", 1464488, 29308, capAlt=["Popayan"], notTypo=["Valle del Cauca"]),
    "CES": P("Cesar", "Valledupar", 1200574, 22905),
    "CHO": P("Chocó", "Quibdó", 534826, 46530, "Choco", capAlt=["Quibdo"]),
    "COR": P("Córdoba", "Montería", 1784783, 25020, "Cordoba", capAlt=["Monteria"]),
    "CUN": P("Cundinamarca", "", 2919060, 24210, capNote="Bogotá (the government sits in Bogotá, which isn't part of the department)"),
    "GUA": P("Guainía", "Inírida", 48114, 72238, "Guainia", capAlt=["Inirida", "Puerto Inírida"], notTypo=["Guaviare"]),
    "GUV": P("Guaviare", "San José del Guaviare", 82767, 53460, capAlt=["San Jose del Guaviare"], notTypo=["Guainía"]),
    "HUI": P("Huila", "Neiva", 1100386, 19890),
    "LAG": P("La Guajira", "Riohacha", 880560, 20848, "Guajira"),
    "MAG": P("Magdalena", "Santa Marta", 1341746, 23188),
    "MET": P("Meta", "Villavicencio", 1039722, 82805),
    "NAR": P("Nariño", "Pasto", 1630592, 33268, "Narino", capAlt=["San Juan de Pasto"]),
    "NSA": P("Norte de Santander", "Cúcuta", 1491689, 21658, "North Santander", capAlt=["Cucuta"], notTypo=["Santander"]),
    "PUT": P("Putumayo", "Mocoa", 348182, 24885),
    "QUI": P("Quindío", "Armenia", 539904, 1845, "Quindio"),
    "RIS": P("Risaralda", "Pereira", 943401, 4140),
    "SAN": P("Santander", "Bucaramanga", 2184837, 30537, notTypo=["Norte de Santander"]),
    "SAP": P("San Andrés and Providencia", "San Andrés", 61280, 52, "San Andrés", "San Andres", "San Andrés y Providencia", "San Andres and Providencia",
             "Archipelago of San Andrés, Providencia and Santa Catalina", "Providencia", capAlt=["San Andres"]),
    "SUC": P("Sucre", "Sincelejo", 904863, 10917),
    "TOL": P("Tolima", "Ibagué", 1330187, 23562, capAlt=["Ibague"]),
    "VAC": P("Valle del Cauca", "Cali", 4475886, 22140, "Valle", "Santiago de Cali"),
    "VAU": P("Vaupés", "Mitú", 40797, 54135, "Vaupes", capAlt=["Mitu"]),
    "VID": P("Vichada", "Puerto Carreño", 107808, 100242, capAlt=["Puerto Carreno"]),
}

FACTS = {
    "DC": dict(local="Bogotá, Distrito Capital", demonym="Bogotano (rolo)", dish="Ajiaco santafereño (chicken and potato soup)",
               drink="Hot chocolate with cheese", festival="Rock al Parque and the Ibero-American Theatre Festival", club="Millonarios and Santa Fe",
               river="Bogotá River", wonder="Monserrate, the mountain above the city", historic="Santa Fe de Bogotá, capital of New Granada",
               landmark="The Gold Museum and La Candelaria", known="The capital, 2,640 m up in the Andes", company="Avianca",
               region="Andes", crop="Flowers from the savanna around it"),
    "AMA": dict(local="Amazonas", demonym="Amazonense", dish="Pirarucú (giant river fish)", festival="The Amazon Confraternity Festival", river="Amazon",
                wonder="Amacayacu National Park", landmark="The Three Frontiers at Leticia", known="Rainforest and the border with Brazil and Peru",
                region="Amazon", crop="Copoazú and camu camu fruits", music="Indigenous music of the Amazon peoples"),
    "ANT": dict(local="Antioquia", demonym="Antioqueño (paisa)", dish="Bandeja paisa", drink="Aguardiente antioqueño", festival="The Flower Festival (Feria de las Flores)",
                club="Atlético Nacional and Independiente Medellín", river="Cauca and Magdalena", wonder="El Peñol rock at Guatapé",
                historic="Colonial Santa Fe de Antioquia", landmark="Medellín's Metrocable and Comuna 13", person="Fernando Botero (artist)",
                known="Paisa culture, industry and flowers", company="Bancolombia and EPM", region="Andes", crop="Coffee and flowers",
                music="Reggaeton (Medellín's J Balvin, Karol G and Maluma)"),
    "ARA": dict(local="Arauca", demonym="Araucano", dish="Mamona (spit-roasted veal)", river="Arauca", known="Oil and cattle ranching on the plains",
                region="Orinoquía (the Llanos)", crop="Cattle and plantain", music="Joropo (llanera music)"),
    "ATL": dict(local="Atlántico", demonym="Atlanticense", dish="Butifarra soledeña", festival="The Barranquilla Carnival", club="Junior",
                river="Magdalena (its mouth at Bocas de Ceniza)", historic="The Caribbean port that brought in immigrants and aviation",
                landmark="Barranquilla's Carnival and the Ventana al Mundo", person="Shakira (born in Barranquilla)", known="Carnival, the port and industry",
                region="Caribbean", music="Cumbia and Carnival music"),
    "BOL": dict(local="Bolívar", demonym="Bolivarense", dish="Coconut rice with fried fish", festival="The Cartagena Independence Festival (November)",
                river="Magdalena", wonder="The Rosario Islands", historic="Cartagena de Indias, Spain's great fortified port",
                landmark="Cartagena's walled city and Castillo San Felipe", unesco="Cartagena's port and fortifications, and Santa Cruz de Mompox",
                known="Cartagena's tourism and colonial Mompox", region="Caribbean", music="Champeta"),
    "BOY": dict(local="Boyacá", demonym="Boyacense", dish="Cocido boyacense", drink="Chicha (maize beer)", club="Boyacá Chicó",
                high="Ritacuba Blanco, 5,330 m (Sierra Nevada del Cocuy)", wonder="El Cocuy National Park and Lake Tota",
                historic="The Battle of Boyacá (1819), which won independence", landmark="The Boyacá Bridge and Villa de Leyva",
                person="Nairo Quintana (cyclist)", known="Emeralds (Muzo), cycling and potatoes", region="Andes", crop="Potatoes", music="Carranga"),
    "CAL": dict(local="Caldas", demonym="Caldense", festival="The Manizales Fair", club="Once Caldas", high="Nevado del Ruiz, 5,321 m",
                wonder="Los Nevados National Park", landmark="Manizales Cathedral", unesco="The Coffee Cultural Landscape", known="Coffee and the Ruiz volcano",
                region="Andes", crop="Coffee", music="Bambuco and pasillo"),
    "CAQ": dict(local="Caquetá", demonym="Caqueteño", river="Caquetá", wonder="Chiribiquete National Park (the world's largest tropical rainforest park)",
                unesco="Chiribiquete National Park (shared with Guaviare)", known="Cattle and the Amazon rainforest", region="Amazon", crop="Cattle and cacao"),
    "CAS": dict(local="Casanare", demonym="Casanareño", dish="Mamona (spit-roasted veal)", river="Meta and Casanare", known="Oil and cattle on the plains",
                region="Orinoquía (the Llanos)", crop="Cattle and rice", music="Joropo"),
    "CAU": dict(local="Cauca", demonym="Caucano", dish="Empanadas de pipián", festival="Holy Week processions in Popayán", river="Cauca and Patía",
                wonder="Puracé National Park and Gorgona Island", historic="Colonial Popayán, the 'White City'", landmark="Popayán's white colonial centre",
                unesco="The Tierradentro National Archaeological Park", known="Colonial Popayán and Indigenous Nasa and Misak peoples",
                region="Andes and Pacific", crop="Coffee", music="Pacific marimba music"),
    "CES": dict(local="Cesar", demonym="Cesarense", festival="The Vallenato Legend Festival in Valledupar", river="Cesar", wonder="The Sierra Nevada de Santa Marta (part)",
                person="Diomedes Díaz (vallenato singer)", known="Vallenato and coal mining", region="Caribbean", crop="Palm oil and cotton", music="Vallenato"),
    "CHO": dict(local="Chocó", demonym="Chocoano", festival="The San Pacho festival in Quibdó", river="Atrato",
                wonder="Humpback whales off Bahía Solano and Nuquí, and Utría National Park", known="One of the rainiest places on Earth, and Afro-Colombian culture",
                region="Pacific", crop="Plantain (and gold from the rivers)", music="Chirimía"),
    "COR": dict(local="Córdoba", demonym="Cordobés", dish="Mote de queso (yam and cheese soup)", festival="The Porro Festival in San Pelayo", river="Sinú",
                landmark="The sombrero vueltiao (Colombia's national hat)", known="Cattle and the sombrero vueltiao", region="Caribbean", crop="Cattle and maize",
                music="Porro"),
    "CUN": dict(local="Cundinamarca", demonym="Cundinamarqués", wonder="Lake Guatavita (the El Dorado legend)", historic="The Muisca Confederation",
                landmark="The Salt Cathedral of Zipaquirá", known="Flowers for export and the Bogotá savanna", city="Soacha", region="Andes",
                crop="Flowers", music="Torbellino"),
    "GUA": dict(local="Guainía", demonym="Guainiense", river="Inírida and Guaviare", wonder="The Cerros de Mavecure", known="Rivers, the Inírida flower and the Puinave people",
                region="Amazon (on the edge of the Orinoquía)"),
    "GUV": dict(local="Guaviare", demonym="Guaviarense", river="Guaviare", wonder="The rock paintings of the Serranía de la Lindosa",
                unesco="Chiribiquete National Park (shared with Caquetá)", known="Ancient rock art and rainforest", region="Amazon"),
    "HUI": dict(local="Huila", demonym="Huilense (opita)", dish="Asado huilense", festival="The Bambuco Folk Festival (San Pedro)", river="Magdalena (its source)",
                wonder="The Tatacoa Desert", unesco="San Agustín Archaeological Park", known="Coffee and the San Agustín statues", region="Andes", crop="Coffee",
                music="Bambuco"),
    "LAG": dict(local="La Guajira", demonym="Guajiro", wonder="Cabo de la Vela and Punta Gallinas, South America's northernmost point",
                known="The Wayuu people and their mochila bags, and coal", company="Cerrejón (coal)", region="Caribbean", music="Vallenato"),
    "MAG": dict(local="Magdalena", demonym="Magdalenense (samario in Santa Marta)", club="Unión Magdalena", high="Pico Cristóbal Colón, about 5,700 m: Colombia's highest",
                wonder="Tayrona National Park and the Sierra Nevada de Santa Marta", historic="Santa Marta (1525), the oldest surviving Spanish city in Colombia",
                landmark="Ciudad Perdida (the Lost City)", person="Gabriel García Márquez (born in Aracataca)", known="Tayrona, the Lost City and bananas",
                region="Caribbean", crop="Bananas", music="Cumbia"),
    "MET": dict(local="Meta", demonym="Metense (llanero)", dish="Mamona (spit-roasted veal)", festival="The International Joropo Tournament",
                river="Meta and Guaviare", wonder="Caño Cristales, the 'river of five colours'", known="The plains: cattle, rice and oil",
                region="Orinoquía (the Llanos)", crop="Rice and palm oil", music="Joropo"),
    "NAR": dict(local="Nariño", demonym="Nariñense (pastuso)", dish="Cuy (roast guinea pig)", festival="The Carnival of Blacks and Whites in Pasto",
                wonder="Galeras volcano and Laguna de la Cocha", landmark="Las Lajas Sanctuary, built across a gorge", region="Andes and Pacific",
                crop="Potatoes", music="Marimba (Tumaco) and Andean music"),
    "NSA": dict(local="Norte de Santander", demonym="Nortesantandereano", dish="Pastel de garbanzo", club="Cúcuta Deportivo",
                historic="The Congress of Cúcuta (1821), which founded Gran Colombia", landmark="Colonial Pamplona", known="Trade across the border with Venezuela",
                region="Andes", crop="Rice and coffee"),
    "PUT": dict(local="Putumayo", demonym="Putumayense", river="Putumayo", wonder="The Fin del Mundo waterfall near Mocoa", known="The Andes meeting the Amazon, and oil",
                region="Amazon"),
    "QUI": dict(local="Quindío", demonym="Quindiano", wonder="The Cocora Valley's wax palms (the national tree)", landmark="The Parque del Café",
                unesco="The Coffee Cultural Landscape", known="Coffee farms and Salento", region="Andes", crop="Coffee"),
    "RIS": dict(local="Risaralda", demonym="Risaraldense", club="Deportivo Pereira", wonder="The hot springs of Santa Rosa de Cabal", unesco="The Coffee Cultural Landscape",
                known="Coffee and Pereira's trade", region="Andes", crop="Coffee"),
    "SAN": dict(local="Santander", demonym="Santandereano", dish="Hormigas culonas (roasted big-bottomed ants) and mute", club="Atlético Bucaramanga",
                wonder="The Chicamocha Canyon", landmark="Colonial Barichara", known="Adventure sports in San Gil", region="Andes", crop="Cacao and tobacco"),
    "SAP": dict(local="San Andrés, Providencia y Santa Catalina", demonym="Raizal (sanandresano)", dialect="San Andrés–Providencia Creole (English-based)",
                dish="Rondón (coconut seafood stew)", wonder="The 'Sea of Seven Colours' and the Seaflower Biosphere Reserve", landmark="Johnny Cay",
                known="Raizal culture, coral reefs and duty-free shopping", region="Caribbean (islands)", music="Reggae and calypso"),
    "SUC": dict(local="Sucre", demonym="Sucreño", festival="The 20 January festival (corralejas) in Sincelejo", wonder="The Gulf of Morrosquillo",
                known="Cattle and the Morrosquillo beaches", region="Caribbean", crop="Cattle", music="Porro and fandango"),
    "TOL": dict(local="Tolima", demonym="Tolimense", dish="Lechona and tamal tolimense", festival="The Colombian Folk Festival in Ibagué", club="Deportes Tolima",
                high="Nevado del Tolima, 5,215 m", historic="The Armero tragedy (1985 eruption of Nevado del Ruiz)", known="Ibagué, 'the musical capital'",
                region="Andes", crop="Rice and coffee", music="Bambuco"),
    "VAC": dict(local="Valle del Cauca", demonym="Vallecaucano (caleño in Cali)", dish="Sancocho de gallina", drink="Lulada (lulo fruit drink)",
                festival="The Cali Fair and the Petronio Álvarez Pacific music festival", club="Deportivo Cali and América de Cali", river="Cauca",
                wonder="Malpelo Island (far offshore)", landmark="Cristo Rey above Cali", unesco="Malpelo Fauna and Flora Sanctuary",
                known="Salsa, sugar cane and the port of Buenaventura", region="Andes and Pacific", crop="Sugar cane", music="Salsa (Cali, the world capital of salsa)"),
    "VAU": dict(local="Vaupés", demonym="Vaupense", river="Vaupés", known="Remote rainforest and the Tukano peoples", region="Amazon"),
    "VID": dict(local="Vichada", demonym="Vichadense", river="Orinoco and Meta", wonder="El Tuparro National Park", known="Wide savannas on the Orinoco",
                region="Orinoquía (the Llanos)", music="Joropo"),
}
