"""Chile's 16 regions (Chile_plan.md): the config for tools/build_country.py and the Learning card facts.
Card fact fields: see tools/at_facts.py; Chile's own three: climate (climate zone), valley (a famous wine valley or
mine), peoples (Indigenous peoples). Games 5 and 6: flags (all 16).
Insets: Easter Island (Rapa Nui), enlarged three times, and the Juan Fernández Islands at their own place; both are
Valparaíso's. The Desventuradas islets and the Antarctic claim are left off.
Written from general knowledge and the downloaded Wikipedia articles (tools/downloads/cl/wiki/); checked by hand.
Populations: Census 2024 (INE), from "Regions of Chile" (its Arica y Parinacota figure, 224,569, is a typo for 244,569:
the region's own article and the table's density agree on 244,569); the 16 add up to 18,480,432.
"""

A3, A2, CONT = "CHL", "CL", "South America"
WINDOW = (-100.0, -61.0, -45.0, -11.0)
DETAIL = (-82.6, -56.2, -66.3, -17.4)
CLIP = [(-76.0, -56.2, -66.3, -17.4), (-109.5, -27.3, -109.2, -27.0), (-80.9, -34.0, -78.7, -33.5)]
INSETS = [dict(codes=["VS"], part_box=True, box=(-109.5, -27.3, -109.2, -27.0), scale=3, to=(-81.5, -27.5), pad=0.3),
          dict(codes=["VS"], part_box=True, box=(-80.9, -34.0, -78.7, -33.5), to=(-79.8, -33.75), pad=0.25)]
POP_SOURCE, POP_YEAR, TOTAL = "INE, Census 2024", "2024 census", 18480432
CAP_LL = {"Coyhaique": [-72.066, -45.571]}
DETAIL_TOL = 0.0035                   # the fjords: 6.3 MB of detail tiles at the usual 0.002°

R = "Region"
PARTS = {
    "AP": dict(name="Arica and Parinacota", names=["Arica y Parinacota", "Arica"], capital="Arica", pop=244569, area=16873, kind=R),
    "TA": dict(name="Tarapacá", names=["Tarapaca"], capital="Iquique", pop=369806, area=42226, kind=R),
    "AN": dict(name="Antofagasta", capital="Antofagasta", pop=635416, area=126049, kind=R),
    "AT": dict(name="Atacama", capital="Copiapó", capAlt=["Copiapo"], pop=299180, area=75176, kind=R),
    "CO": dict(name="Coquimbo", capital="La Serena", pop=832864, area=40580, kind=R),
    "VS": dict(name="Valparaíso", names=["Valparaiso"], capital="Valparaíso", capAlt=["Valparaiso"], pop=1896053, area=16396, kind=R),
    "RM": dict(name="Santiago Metropolitan", names=["Santiago Metropolitan Region", "Metropolitana", "Región Metropolitana", "Santiago", "RM"],
               capital="Santiago", pop=7400741, area=15403, kind="Metropolitan region"),
    "LI": dict(name="O'Higgins", names=["OHiggins", "Libertador General Bernardo O'Higgins", "O'Higgins Region"], capital="Rancagua", pop=987228, area=16387, kind=R),
    "ML": dict(name="Maule", capital="Talca", pop=1123008, area=30296, kind=R),
    "NB": dict(name="Ñuble", names=["Nuble"], capital="Chillán", capAlt=["Chillan"], pop=512289, area=13179, kind=R),
    "BI": dict(name="Biobío", names=["Biobio", "Bío Bío", "Bío-Bío", "Bio Bio"], capital="Concepción", capAlt=["Concepcion"], pop=1613059, area=23890, kind=R),
    "AR": dict(name="Araucanía", names=["Araucania", "La Araucanía", "La Araucania"], capital="Temuco", pop=1010423, area=31842, kind=R),
    "LR": dict(name="Los Ríos", names=["Los Rios"], capital="Valdivia", pop=398230, area=18430, kind=R, notTypo=["Los Lagos"]),
    "LL": dict(name="Los Lagos", capital="Puerto Montt", pop=890284, area=48584, kind=R, notTypo=["Los Ríos"]),
    "AI": dict(name="Aysén", names=["Aysen", "Aisén", "Aysén del General Carlos Ibáñez del Campo"], capital="Coyhaique", capAlt=["Coihaique"],
               pop=100745, area=108494, kind=R),
    "MA": dict(name="Magallanes", names=["Magallanes y Antártica Chilena", "Magallanes and Chilean Antarctica", "Magellan"], capital="Punta Arenas",
               pop=166537, area=132291, kind=R),
}

FACTS = {
    "AP": dict(local="Región de Arica y Parinacota", demonym="Ariqueño", festival="The Andean Carnival 'con la Fuerza del Sol'", club="San Marcos de Arica",
               river="Lluta and San José", high="Parinacota, 6,348 m (on the Bolivian border)", wonder="Lauca National Park and Lake Chungará",
               historic="Part of Peru until the War of the Pacific (1879–1884)", landmark="The Morro de Arica", unesco="The Chinchorro mummies (the world's oldest)",
               known="The 'city of eternal spring' and the Azapa valley's olives", climate="Desert on the coast, high plateau (altiplano) inland",
               peoples="Aymara"),
    "TA": dict(local="Región de Tarapacá", demonym="Tarapaqueño", festival="La Tirana (masked dances, every July)", club="Deportes Iquique",
               wonder="The Pica oasis and the Giant of Atacama geoglyph", historic="Part of Peru until the War of the Pacific", landmark="The ghost nitrate towns",
               unesco="The Humberstone and Santa Laura saltpeter works", known="Iquique's duty-free zone (ZOFRI) and nitrate history",
               climate="Desert (the Atacama)", valley="Collahuasi copper mine", peoples="Aymara and Quechua"),
    "AN": dict(local="Región de Antofagasta", demonym="Antofagastino", club="Deportes Antofagasta", high="Llullaillaco, 6,739 m (on the Argentine border)",
               wonder="San Pedro de Atacama, the Valley of the Moon and the El Tatio geysers", historic="Bolivia's coast until the War of the Pacific",
               landmark="La Portada sea arch", known="Copper, lithium and the giant telescopes (ALMA, Paranal)", company="Codelco (Chuquicamata) and SQM",
               climate="The world's driest desert", valley="Chuquicamata and Escondida copper mines; lithium from the Salar de Atacama",
               peoples="Atacameño (Lickanantay)"),
    "AT": dict(local="Región de Atacama", demonym="Atacameño", river="Copiapó", high="Ojos del Salado, 6,893 m: the world's highest volcano",
               wonder="The flowering desert and Pan de Azúcar National Park", landmark="The San José mine (the 2010 rescue of 33 miners)",
               known="Copper and iron mining, and the 2010 mine rescue", climate="Desert, wetter towards the south", valley="Candelaria copper mine",
               peoples="Colla and Diaguita"),
    "CO": dict(local="Región de Coquimbo", demonym="Coquimbano", drink="Pisco from the Elqui Valley", river="Elqui", wonder="Fray Jorge Forest and the clear night skies",
               landmark="The Cerro Tololo and La Silla observatories", person="Gabriela Mistral (Nobel laureate, from the Elqui Valley)",
               known="Pisco, astronomy and beaches", climate="Semi-arid", valley="The Elqui Valley (pisco grapes)", peoples="Diaguita"),
    "VS": dict(local="Región de Valparaíso", demonym="Porteño (in Valparaíso)", festival="The Viña del Mar International Song Festival and New Year fireworks",
               club="Santiago Wanderers and Everton", wonder="Easter Island and La Campana National Park", landmark="Valparaíso's funiculars and Pablo Neruda's La Sebastiana",
               unesco="The historic quarter of Valparaíso and Rapa Nui National Park", known="The main port, the National Congress and Easter Island",
               city="Viña del Mar", climate="Mediterranean (Easter Island: subtropical)", valley="The Casablanca Valley (white wine)",
               peoples="Rapa Nui (Easter Island)"),
    "RM": dict(local="Región Metropolitana de Santiago", demonym="Santiaguino", dish="Pastel de choclo and the completo hot dog", club="Colo-Colo and Universidad de Chile",
               river="Mapocho and Maipo", wonder="The Andes above the city (Valle Nevado and Cajón del Maipo)", landmark="La Moneda Palace and the Gran Torre Santiago",
               known="The capital: four in ten Chileans live here", company="LATAM Airlines", climate="Mediterranean", valley="The Maipo Valley (Cabernet Sauvignon)",
               peoples="Mapuche (the largest urban Mapuche population)"),
    "LI": dict(local="Región del Libertador General Bernardo O'Higgins", demonym="O'higginiano", festival="The national rodeo championship in Rancagua",
               wonder="Pichilemu's surf", historic="The Battle of Rancagua (1814)", landmark="Sewell, the mountain copper town", unesco="Sewell Mining Town",
               known="Copper, fruit and wine", climate="Mediterranean", valley="The Colchagua Valley (wine) and El Teniente, the world's largest underground copper mine"),
    "ML": dict(local="Región del Maule", demonym="Maulino", club="Rangers de Talca", river="Maule", historic="Chile's independence was proclaimed in Talca (1818)",
               known="Farming, wine and the 2010 earthquake", climate="Mediterranean", valley="The Maule Valley, Chile's biggest wine region"),
    "NB": dict(local="Región de Ñuble", demonym="Ñublensino", dish="Longaniza de Chillán (sausage)", club="Ñublense", wonder="The Nevados de Chillán hot springs",
               historic="The newest region (2018)", person="Bernardo O'Higgins (born in Chillán)", known="The newest region, crafts and longaniza",
               climate="Mediterranean", valley="The Itata Valley (old-vine wine)"),
    "BI": dict(local="Región del Biobío", demonym="Biobiense", club="Huachipato and Universidad de Concepción", river="Biobío",
               historic="The frontier of the Arauco War with the Mapuche", known="Industry: steel, forestry and ports", climate="Temperate, rainier towards the south",
               valley="The Bío-Bío Valley (wine)", peoples="Mapuche (Lafkenche)"),
    "AR": dict(local="Región de La Araucanía", demonym="Araucano", club="Deportes Temuco", wonder="Conguillío National Park and the Villarrica volcano at Pucón",
               historic="The heart of the Mapuche lands; occupied by Chile 1861–1883", landmark="The Villarrica volcano", known="Mapuche culture, lakes and volcanoes",
               climate="Temperate and rainy", peoples="Mapuche"),
    "LR": dict(local="Región de Los Ríos", demonym="Valdiviano", drink="Kunstmann beer (German heritage)", festival="Noche Valdiviana (river parade and fireworks)",
               river="Valdivia and Calle-Calle", wonder="The Valdivian rainforest", historic="The 1960 Valdivia earthquake, the strongest ever recorded",
               landmark="The Spanish forts of Valdivia", known="Rivers, rain and German heritage", climate="Oceanic and rainy", peoples="Mapuche-Huilliche"),
    "LL": dict(local="Región de Los Lagos", demonym="Lagino", dish="Curanto (Chiloé's earth-oven feast)", wonder="Chiloé, the Osorno volcano and the lakes",
               historic="German settlement around Lake Llanquihue (from 1850)", landmark="The stilt houses (palafitos) of Castro", unesco="The Churches of Chiloé",
               known="Salmon farming, lakes and Chiloé's myths", climate="Oceanic and rainy", peoples="Huilliche"),
    "AI": dict(local="Región de Aysén del General Carlos Ibáñez del Campo", demonym="Aysenino", high="Monte San Valentín, 4,058 m",
               wonder="The Marble Caves of General Carrera Lake and Laguna San Rafael", landmark="The Carretera Austral road",
               known="Patagonian wilderness and fly-fishing; the least populated region", climate="Patagonian: cold and wet in the west, steppe in the east",
               peoples="Tehuelche and Kawésqar"),
    "MA": dict(local="Región de Magallanes y de la Antártica Chilena", demonym="Magallánico", wonder="Torres del Paine and Cape Horn",
               historic="The Strait of Magellan (1520)", landmark="The Torres del Paine", known="Patagonia, sheep farming and the gateway to Antarctica",
               climate="Patagonian (subpolar)", peoples="Kawésqar, Yagán and Selk'nam"),
}
