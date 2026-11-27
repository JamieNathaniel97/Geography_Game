"""Peru's 24 departments, Lima Province and Callao (Peru_plan.md): the config for tools/build_country.py and the Learning
card facts. Card fact fields: see tools/at_facts.py; Peru's own three: region (coast, Andes or Amazon), civ (ancient
civilisation), quechua (Quechua or Aymara speakers). Games 5 and 6: flags (Callao's fetched by name: it has no ISO entry
on Wikidata). Natural Earth gives Lima Province the Lima Region's code; the build splits them (NE_FIX). Circles: Lima
Province and Callao.
Written from general knowledge and the downloaded Wikipedia articles (tools/downloads/pe/wiki/); checked by hand.
Populations: INEI's estimates for 2025 (via Wikidata; the Lima Region and Callao from "Regions of Peru"). They add up to
34,170,116, 12,384 (0.04%) more than the national 2025 figure of 34,157,732: the sources round differently (TOTAL_TOL).
"""

A3, A2, CONT = "PER", "PE", "South America"
WINDOW = (-88.0, -21.5, -62.0, 3.0)
DETAIL = (-81.5, -18.5, -68.6, 0.1)
NE_FIX = {("PE-LIM", "Lima Province"): "LMA"}
POP_SOURCE, POP_YEAR, TOTAL, TOTAL_TOL = "INEI estimates, 2025", "2025", 34157732, 12500
CAP_LL = {}

D = "Department"
PARTS = {
    "AMA": dict(name="Amazonas", capital="Chachapoyas", pop=467688, area=39249, kind=D),
    "ANC": dict(name="Áncash", names=["Ancash"], capital="Huaraz", pop=1205923, area=35914, kind=D),
    "APU": dict(name="Apurímac", names=["Apurimac"], capital="Abancay", pop=467513, area=20896, kind=D),
    "ARE": dict(name="Arequipa", capital="Arequipa", pop=1814554, area=63345, kind=D),
    "AYA": dict(name="Ayacucho", capital="Ayacucho", pop=709026, area=43815, kind=D),
    "CAJ": dict(name="Cajamarca", capital="Cajamarca", pop=1490732, area=33318, kind=D),
    "CAL": dict(name="Callao", names=["Constitutional Province of Callao"], capital="Callao", pop=1101911, area=147, kind="Constitutional province",
                flagIso="PE-CAL"),
    "CUS": dict(name="Cusco", names=["Cuzco", "Qusqu"], capital="Cusco", capAlt=["Cuzco"], pop=1379167, area=71986, kind=D),
    "HUV": dict(name="Huancavelica", capital="Huancavelica", pop=372158, area=22131, kind=D),
    "HUC": dict(name="Huánuco", names=["Huanuco"], capital="Huánuco", capAlt=["Huanuco"], pop=807393, area=36849, kind=D),
    "ICA": dict(name="Ica", capital="Ica", pop=1033084, area=21328, kind=D),
    "JUN": dict(name="Junín", names=["Junin"], capital="Huancayo", pop=1422780, area=37667, kind=D),
    "LAL": dict(name="La Libertad", capital="Trujillo", pop=2056445, area=25500, kind=D),
    "LAM": dict(name="Lambayeque", capital="Chiclayo", pop=1404643, area=14231, kind=D),
    "LIM": dict(name="Lima Region", names=["Lima Department", "Región Lima", "Lima Provinces"], capital="Huacho", pop=1018876, area=32126, kind="Region",
                notTypo=["Lima Province"]),
    "LMA": dict(name="Lima Province", names=["Lima", "Metropolitan Lima", "Lima Metropolitana"], capital="Lima", pop=10142492, area=2672,
                kind="Province (the capital)", notTypo=["Lima Region", "Lima Provinces"]),
    "LOR": dict(name="Loreto", capital="Iquitos", pop=1032771, area=368852, kind=D),
    "MDD": dict(name="Madre de Dios", capital="Puerto Maldonado", pop=208667, area=85301, kind=D),
    "MOQ": dict(name="Moquegua", capital="Moquegua", pop=194828, area=15734, kind=D),
    "PAS": dict(name="Pasco", capital="Cerro de Pasco", pop=253549, area=25320, kind=D),
    "PIU": dict(name="Piura", capital="Piura", pop=2115215, area=35892, kind=D),
    "PUN": dict(name="Puno", capital="Puno", pop=1232993, area=66997, kind=D),
    "SAM": dict(name="San Martín", names=["San Martin"], capital="Moyobamba", pop=967923, area=51253, kind=D),
    "TAC": dict(name="Tacna", capital="Tacna", pop=389226, area=16076, kind=D),
    "TUM": dict(name="Tumbes", capital="Tumbes", pop=256691, area=4046, kind=D),
    "UCA": dict(name="Ucayali", capital="Pucallpa", pop=623868, area=101831, kind=D),
}

FACTS = {
    "AMA": dict(local="Departamento de Amazonas", dish="Juane (rice wrapped in bijao leaves)", wonder="Gocta, one of the world's tallest waterfalls",
                landmark="The Kuélap fortress", known="Cloud forests and the Chachapoyas ruins", region="Andes and Amazon", civ="The Chachapoyas (the 'Warriors of the Clouds')"),
    "ANC": dict(local="Departamento de Áncash", high="Huascarán, 6,768 m: Peru's highest", wonder="Huascarán National Park and the Cordillera Blanca",
                historic="The 1970 earthquake that buried Yungay", landmark="Chavín de Huántar", unesco="Chavín de Huántar and Huascarán National Park",
                known="Mountaineering and mining (Antamina)", region="Andes and coast", civ="Chavín (about 900–200 BC)", quechua="Many speak Áncash Quechua"),
    "APU": dict(local="Departamento de Apurímac", wonder="The Apurímac Canyon", landmark="Choquequirao, Machu Picchu's 'sister'", known="Copper mining (Las Bambas)",
                region="Andes", civ="The Chanka, then the Inca", quechua="Quechua is the main language"),
    "ARE": dict(local="Departamento de Arequipa", dish="Rocoto relleno (stuffed hot peppers)", club="FBC Melgar", high="Coropuna, 6,377 m",
                wonder="The Colca Canyon and its condors", landmark="Santa Catalina Monastery and the Misti volcano", unesco="The historic centre of Arequipa",
                person="Mario Vargas Llosa (Nobel laureate)", known="The 'White City' built of volcanic sillar", region="Coast and Andes", quechua="Some, in the highlands"),
    "AYA": dict(local="Departamento de Ayacucho", festival="Holy Week in Ayacucho", historic="The Battle of Ayacucho (1824), which won South America's independence",
                landmark="The Pampa de Quinua battlefield", known="Retablo folk art and 33 colonial churches", region="Andes", civ="Wari (about 600–1000)",
                quechua="Quechua is the main language"),
    "CAJ": dict(local="Departamento de Cajamarca", festival="The Cajamarca Carnival", historic="Pizarro captured the Inca Atahualpa here (1532)",
                landmark="The Ransom Room and Cumbe Mayo", known="Dairy farming and gold (Yanacocha)", region="Andes", civ="The Cajamarca culture, then the Inca"),
    "CAL": dict(local="Provincia Constitucional del Callao", club="Sport Boys", historic="The Battle of Callao (1866)", landmark="The Real Felipe Fortress",
                known="Peru's main port and the international airport", region="Coast"),
    "CUS": dict(local="Departamento del Cusco (Qusqu)", dish="Cuy al horno (roast guinea pig)", festival="Inti Raymi, the Festival of the Sun", club="Cienciano",
                wonder="The Sacred Valley and Rainbow Mountain", landmark="Machu Picchu", unesco="Machu Picchu and the city of Cusco",
                known="The Inca capital and tourism", region="Andes and Amazon", civ="The Inca (Cusco was their capital)", quechua="Quechua is the main language"),
    "HUV": dict(local="Departamento de Huancavelica", festival="The scissors dance (danza de tijeras)", known="Colonial mercury mines (Santa Bárbara)",
                region="Andes", civ="The Chanka, then the Inca", quechua="Quechua is the main language"),
    "HUC": dict(local="Departamento de Huánuco", wonder="Tingo María National Park", landmark="Kotosh, the Temple of the Crossed Hands",
                known="Coca, coffee and the meeting of the Andes and the jungle", region="Andes and Amazon", civ="Kotosh (about 2000 BC)", quechua="Many speak Quechua"),
    "ICA": dict(local="Departamento de Ica", dish="Tejas (filled sweets)", drink="Pisco", wonder="The Huacachina oasis and Paracas National Reserve",
                landmark="The Nazca Lines", unesco="The Lines and Geoglyphs of Nasca and Palpa", known="Pisco, wine and the Nazca Lines", region="Coast",
                civ="Paracas and Nazca"),
    "JUN": dict(local="Departamento de Junín", dish="Papa a la huancaína (potatoes in spicy cheese sauce)", festival="The Huaylarsh dance",
                landmark="The Mantaro Valley", known="Farming and the high railway to Huancayo", region="Andes and Amazon", civ="The Wanka (Huanca)",
                quechua="Many speak Quechua"),
    "LAL": dict(local="Departamento de La Libertad", dish="Shambar (wheat and bean soup)", festival="The Marinera Festival in Trujillo",
                club="Universidad César Vallejo", landmark="Chan Chan, the largest adobe city in the Americas", unesco="Chan Chan",
                known="The marinera dance, sugar cane and Huanchaco's reed boats", region="Coast and Andes", civ="Moche and Chimú"),
    "LAM": dict(local="Departamento de Lambayeque", dish="Arroz con pato (rice with duck)", club="Juan Aurich", landmark="The Royal Tombs of Sipán museum",
                known="The Lord of Sipán's tomb (found in 1987)", region="Coast", civ="Moche and Sicán (Lambayeque)"),
    "LIM": dict(local="Región Lima", landmark="Caral, the oldest city in the Americas", unesco="The Sacred City of Caral-Supe", known="Farming valleys and beaches",
                region="Coast and Andes", civ="Caral (about 3000 BC)"),
    "LMA": dict(local="Provincia de Lima", dish="Ceviche and anticuchos", drink="Pisco sour and Inca Kola", festival="The Lord of Miracles processions (October)",
                club="Alianza Lima, Universitario and Sporting Cristal", river="Rímac", landmark="The Plaza Mayor and Huaca Pucllana", unesco="The historic centre of Lima",
                known="The capital and Latin America's food capital", region="Coast", civ="The Lima culture (Huaca Pucllana)"),
    "LOR": dict(local="Departamento de Loreto", river="Amazon", wonder="The Pacaya-Samiria National Reserve", known="Iquitos, the largest city that no road reaches, and the rubber boom",
                region="Amazon"),
    "MDD": dict(local="Departamento de Madre de Dios", wonder="Tambopata and Manu (part)", known="Brazil nuts, rainforest and gold mining", region="Amazon"),
    "MOQ": dict(local="Departamento de Moquegua", known="Copper (Cuajone) and pisco", region="Coast and Andes"),
    "PAS": dict(local="Departamento de Pasco", wonder="The Huayllay stone forest", known="Mining; Cerro de Pasco is one of the world's highest cities",
                region="Andes and Amazon (Oxapampa)"),
    "PIU": dict(local="Departamento de Piura", dish="Ceviche and seco de chabelo", club="Atlético Grau", wonder="The beaches of Máncora",
                known="Mangoes, cotton and beaches", region="Coast", civ="Vicús"),
    "PUN": dict(local="Departamento de Puno", festival="The Fiesta de la Candelaria", wonder="Lake Titicaca and the Uros floating islands",
                landmark="The Sillustani burial towers", known="The 'folk capital of Peru'", region="Andes (the high altiplano)", civ="Pukara and Tiwanaku",
                quechua="Quechua and Aymara are both widely spoken"),
    "SAM": dict(local="Departamento de San Martín", unesco="Río Abiseo National Park", known="Coffee and cacao", region="Amazon"),
    "TAC": dict(local="Departamento de Tacna", historic="Held by Chile from 1880 to 1929", known="Trade with Chile", region="Coast and Andes",
                quechua="Some Aymara speakers"),
    "TUM": dict(local="Departamento de Tumbes", wonder="The mangroves of Tumbes", known="Beaches, shrimp farms and the northernmost department", region="Coast"),
    "UCA": dict(local="Departamento de Ucayali", river="Ucayali", known="Timber and Shipibo-Conibo art", region="Amazon"),
}
