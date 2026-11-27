"""Portugal's 18 districts and 2 autonomous regions (Portugal_plan.md): the config for tools/build_country.py and the
Learning card facts. Card fact fields: see tools/at_facts.py; Portugal's own three: wine (wine region), province
(historic province), discovery (an explorer or Age of Discovery link).
Games 5 and 6: none. The districts have no coats of arms of their own (the district articles show their capital
cities' arms), so only the Azores and Madeira have flags, which show on their cards.
The Azores (scaled to half size) and Madeira are moved into framed insets off the west coast; the Selvagens are left off.
Written from general knowledge and the downloaded Wikipedia articles (tools/downloads/pt/wiki/); checked by hand.
Populations: Census 2021 (INE), from "Districts of Portugal"; the 20 add up to 10,343,066.
"""

A3, A2 = "PRT", "PT"
WINDOW = (-16.5, 35.0, -4.0, 44.0)
DETAIL = (-14.2, 36.8, -6.1, 42.2)
CLIP = [(-10.0, 36.5, -6.0, 42.5), (-31.5, 36.5, -24.5, 40.0), (-17.5, 32.2, -16.1, 33.3)]
INSETS = [dict(codes=["20"], box=(-31.4, 36.8, -24.9, 39.8), scale=0.5, to=(-11.9, 41.1)),
          dict(codes=["30"], box=(-17.4, 32.3, -16.2, 33.2), to=(-11.2, 38.2))]
# (the framed insets get square tap areas the shape of their frames: tools/build_country.py)   # tappable ovals: the islands are small on a phone
POP_SOURCE, POP_YEAR, TOTAL = "INE, Census 2021", "2021 census", 10343066
CAP_LL = {}

D = "District"
PARTS = {
    "01": dict(name="Aveiro", capital="Aveiro", pop=700787, area=2798, kind=D),
    "02": dict(name="Beja", capital="Beja", pop=144401, area=10229, kind=D),
    "03": dict(name="Braga", capital="Braga", pop=846293, area=2706, kind=D),
    "04": dict(name="Bragança", names=["Braganca", "Braganza"], capital="Bragança", capAlt=["Braganca"], pop=122804, area=6608, kind=D),
    "05": dict(name="Castelo Branco", capital="Castelo Branco", pop=177962, area=6675, kind=D),
    "06": dict(name="Coimbra", capital="Coimbra", pop=408551, area=3947, kind=D),
    "07": dict(name="Évora", names=["Evora"], capital="Évora", capAlt=["Evora"], pop=152444, area=7393, kind=D),
    "08": dict(name="Faro", names=["Algarve"], capital="Faro", pop=467343, area=4960, kind=D),
    "09": dict(name="Guarda", capital="Guarda", pop=142974, area=5518, kind=D),
    "10": dict(name="Leiria", capital="Leiria", pop=458605, area=3505, kind=D),
    "11": dict(name="Lisbon", names=["Lisboa"], capital="Lisbon", capAlt=["Lisboa"], pop=2275385, area=2761, kind=D),
    "12": dict(name="Portalegre", capital="Portalegre", pop=104923, area=6065, kind=D),
    "13": dict(name="Porto", names=["Oporto"], capital="Porto", capAlt=["Oporto"], pop=1785405, area=2408, kind=D),
    "14": dict(name="Santarém", names=["Santarem"], capital="Santarém", capAlt=["Santarem"], pop=424973, area=6747, kind=D),
    "15": dict(name="Setúbal", names=["Setubal"], capital="Setúbal", capAlt=["Setubal"], pop=874806, area=5064, kind=D),
    "16": dict(name="Viana do Castelo", capital="Viana do Castelo", pop=231266, area=2255, kind=D),
    "17": dict(name="Vila Real", capital="Vila Real", pop=185695, area=4328, kind=D),
    "18": dict(name="Viseu", capital="Viseu", pop=351292, area=5007, kind=D),
    "20": dict(name="Azores", names=["Açores", "Acores", "The Azores"], capital="Ponta Delgada", capAlt=["Horta", "Angra do Heroísmo", "Angra"],
               capAlso=["Horta", "Angra do Heroísmo"], capNote="Ponta Delgada (government), Horta (assembly) and Angra do Heroísmo (courts)",
               pop=236413, area=2322, kind="Autonomous region"),
    "30": dict(name="Madeira", capital="Funchal", pop=250744, area=801, kind="Autonomous region"),
}

FACTS = {
    "01": dict(local="Distrito de Aveiro", demonym="Aveirense", dish="Ovos moles (egg-yolk sweets)", drink="Bairrada sparkling wine", club="CD Feirense",
               river="Vouga", wonder="The Ria de Aveiro lagoon", historic="Beira Litoral", landmark="The moliceiro boats and the striped houses of Costa Nova",
               known="'Portugal's Venice', salt pans and porcelain", company="Vista Alegre (porcelain)", wine="Bairrada", province="Beira Litoral (and Douro Litoral in the north)",
               discovery="João Afonso de Aveiro, who reached the Kingdom of Benin (1486)"),
    "02": dict(local="Distrito de Beja", demonym="Bejense", dish="Açorda alentejana (bread and coriander soup)", drink="Alentejo wine",
               festival="Ovibeja agricultural fair", river="Guadiana", wonder="The Guadiana Valley Natural Park and Lake Alqueva",
               historic="Baixo Alentejo (Roman Pax Julia)", landmark="Beja Castle's keep", known="Wheat fields, cork oaks and cante alentejano singing",
               wine="Alentejo", province="Baixo Alentejo"),
    "03": dict(local="Distrito de Braga", demonym="Bracarense", dish="Papas de sarrabulho", drink="Vinho Verde", festival="São João and Holy Week in Braga",
               club="SC Braga and Vitória de Guimarães", river="Cávado", wonder="Peneda-Gerês National Park (part)", historic="Minho; Roman Bracara Augusta",
               landmark="Bom Jesus do Monte's stairway", unesco="Bom Jesus do Monte and the historic centre of Guimarães",
               person="Afonso Henriques, first king of Portugal (Guimarães)", known="'The birthplace of Portugal' (Guimarães) and textiles",
               wine="Vinho Verde", province="Minho"),
    "04": dict(local="Distrito de Bragança", demonym="Brigantino", dialect="Mirandese (an official regional language)", dish="Alheira de Mirandela and posta mirandesa",
               festival="The Caretos masked festivals at midwinter", river="Douro (the Spanish border) and Sabor", wonder="Montesinho and International Douro natural parks",
               historic="Trás-os-Montes", landmark="Bragança Castle", known="Remote mountain villages, chestnuts and Mirandese", wine="Trás-os-Montes",
               province="Trás-os-Montes e Alto Douro"),
    "05": dict(local="Distrito de Castelo Branco", demonym="Albicastrense", dish="Castelo Branco cheese", river="Tagus and Zêzere",
               wonder="Tagus International Natural Park", historic="Beira Baixa", landmark="Monsanto, the village among boulders",
               known="Embroidered bedspreads (bordado de Castelo Branco)", wine="Beira Interior", province="Beira Baixa",
               discovery="Pedro Álvares Cabral (born in Belmonte), who reached Brazil in 1500"),
    "06": dict(local="Distrito de Coimbra", demonym="Conimbricense", dish="Chanfana (goat stewed in wine)", festival="Queima das Fitas (students' festival)",
               club="Académica", river="Mondego", wonder="Serra da Lousã", historic="Beira Litoral; Portugal's first capital (1131–1255)",
               landmark="The University of Coimbra and the Joanina Library", unesco="The University of Coimbra – Alta and Sofia",
               known="One of Europe's oldest universities (1290) and Coimbra fado", wine="Bairrada and Dão (parts)", province="Beira Litoral"),
    "07": dict(local="Distrito de Évora", demonym="Eborense", dish="Black pork (porco preto) and migas", drink="Alentejo wine", river="Guadiana",
               wonder="Lake Alqueva, Europe's largest artificial lake", historic="Alto Alentejo", landmark="The Roman Temple and the Chapel of Bones",
               unesco="The historic centre of Évora", known="Cork, megaliths (the Almendres Cromlech) and marble", wine="Alentejo", province="Alto Alentejo"),
    "08": dict(local="Distrito de Faro", demonym="Algarvio", dish="Cataplana (seafood stew)", drink="Medronho (strawberry-tree brandy)", festival="The Loulé Carnival",
               club="SC Farense and Portimonense", river="Guadiana and Arade", high="Fóia, 902 m", wonder="The Ria Formosa lagoon and the Benagil sea cave",
               historic="The Kingdom of the Algarve (a separate title of the crown)", landmark="Ponta da Piedade and Sagres Fortress",
               known="Beaches, golf and tourism", wine="Algarve", province="Algarve", discovery="Sagres and Lagos, where Henry the Navigator's caravels set out"),
    "09": dict(local="Distrito da Guarda", demonym="Guardense", dish="Serra da Estrela cheese", high="Torre, 1,993 m: the mainland's highest",
               wonder="Serra da Estrela", historic="Beira Alta and the frontier castles", landmark="Guarda Cathedral and the historic village of Sortelha",
               unesco="The prehistoric rock art of the Côa Valley", known="The highest city, the cold, and cheese", wine="Beira Interior and Dão", province="Beira Alta"),
    "10": dict(local="Distrito de Leiria", demonym="Leiriense", river="Lis", wonder="The giant waves of Nazaré", historic="Estremadura and Beira Litoral",
               landmark="Batalha Monastery and Alcobaça Monastery", unesco="The monasteries of Batalha and Alcobaça",
               known="Nazaré's surfing, moulds and plastics, and the King's Pine Forest", wine="Lisboa (Óbidos)", province="Beira Litoral and Estremadura"),
    "11": dict(local="Distrito de Lisboa", demonym="Lisboeta", dish="Pastéis de nata (custard tarts)", drink="Ginjinha (cherry liqueur)",
               festival="Santo António in June", club="Benfica and Sporting CP", river="Tagus", wonder="Sintra's hills and Cabo da Roca, mainland Europe's westernmost point",
               historic="Estremadura", landmark="Belém Tower and the Jerónimos Monastery", unesco="Jerónimos and Belém Tower, Sintra, and Mafra",
               person="Fernando Pessoa (poet)", known="The capital, fado and trams", company="TAP Air Portugal and EDP", wine="Lisboa (Colares, Bucelas)",
               province="Estremadura", discovery="Vasco da Gama sailed for India from Belém (1497)"),
    "12": dict(local="Distrito de Portalegre", demonym="Portalegrense", high="Serra de São Mamede, 1,025 m", wonder="Serra de São Mamede Natural Park",
               historic="Alto Alentejo", landmark="Marvão's hilltop castle", unesco="The garrison border town of Elvas", known="Tapestries and cork",
               wine="Alentejo", province="Alto Alentejo"),
    "13": dict(local="Distrito do Porto", demonym="Portuense (tripeiro)", dish="Francesinha and tripas à moda do Porto", drink="Port wine",
               festival="São João on 23 June", club="FC Porto", river="Douro", historic="Douro Litoral", landmark="The Dom Luís I Bridge and Livraria Lello",
               unesco="The historic centre of Porto", person="Prince Henry the Navigator (born in Porto)", known="Port wine and the 'Invicta' city",
               company="Sonae", wine="Port (aged across the river in Gaia) and Vinho Verde", province="Douro Litoral",
               discovery="Prince Henry the Navigator was born here (1394)"),
    "14": dict(local="Distrito de Santarém", demonym="Escalabitano", dish="Sopa da pedra (Almeirim)", festival="The National Agriculture Fair",
               river="Tagus", wonder="The Lezíria floodplains", historic="Ribatejo", landmark="The Convent of Christ in Tomar and the Sanctuary of Fátima",
               unesco="The Convent of Christ in Tomar", known="Bulls and horses, and the Fátima pilgrimages", wine="Tejo", province="Ribatejo",
               discovery="The Order of Christ (Tomar) helped pay for the voyages"),
    "15": dict(local="Distrito de Setúbal", demonym="Setubalense", dish="Choco frito (fried cuttlefish)", drink="Moscatel de Setúbal",
               club="Vitória de Setúbal", river="Sado", wonder="Arrábida Natural Park and the Sado estuary's dolphins", historic="Estremadura and Baixo Alentejo",
               landmark="Palmela Castle", known="Dolphins, salt and car-making", company="Volkswagen Autoeuropa", wine="Península de Setúbal",
               province="Estremadura and Baixo Alentejo", discovery="Vasco da Gama (born in Sines)"),
    "16": dict(local="Distrito de Viana do Castelo", demonym="Vianense", drink="Vinho Verde (Alvarinho)", festival="The Romaria of Senhora d'Agonia",
               river="Lima and Minho", wonder="Peneda-Gerês National Park (part)", historic="Minho", landmark="Santa Luzia Sanctuary",
               known="Gold filigree and folk costumes", wine="Vinho Verde", province="Minho"),
    "17": dict(local="Distrito de Vila Real", demonym="Vila-realense", drink="Port grapes and Mateus Rosé", river="Douro", wonder="Alvão Natural Park",
               historic="Trás-os-Montes and Alto Douro", landmark="Mateus Palace", unesco="The Alto Douro Wine Region",
               known="The terraced Douro vineyards", wine="Douro (Port)", province="Trás-os-Montes e Alto Douro",
               discovery="Ferdinand Magellan (Sabrosa claims him)"),
    "18": dict(local="Distrito de Viseu", demonym="Viseense", drink="Dão wine", festival="The Feira de São Mateus (since 1392)", river="Vouga and Paiva",
               wonder="Serra do Caramulo", historic="Beira Alta (the legend of Viriathus)", landmark="Viseu Cathedral and the Sanctuary of Lamego",
               known="Dão wine", wine="Dão", province="Beira Alta"),
    "20": dict(local="Região Autónoma dos Açores", demonym="Azorean (açoriano)", dish="Cozido das Furnas (stew cooked by volcanic heat)",
               drink="Azorean tea (Gorreana, Europe's oldest tea plantation)", festival="The Holy Spirit festivals and Santo Cristo dos Milagres",
               high="Mount Pico, 2,351 m: Portugal's highest", wonder="The crater lakes of Sete Cidades", historic="Settled by the Portuguese from the 1430s",
               landmark="Angra do Heroísmo", unesco="Angra do Heroísmo and the Pico Island vineyards", known="Volcanoes, whale watching and nine islands",
               wine="Pico", province="None: autonomous since 1976", discovery="Reached by Portuguese sailors in the 1420s–1430s"),
    "30": dict(local="Região Autónoma da Madeira", demonym="Madeiran (madeirense)", dish="Espetada and bolo do caco", drink="Madeira wine and poncha",
               festival="New Year's fireworks and the Flower Festival", club="CS Marítimo and CD Nacional", high="Pico Ruivo, 1,862 m",
               wonder="The Laurisilva forest", historic="Settled from 1420", landmark="The Monte toboggans and the levada walks",
               unesco="The Laurisilva of Madeira", person="Cristiano Ronaldo (born in Funchal)", known="Madeira wine, levadas and flowers", wine="Madeira",
               province="None: autonomous since 1976", discovery="Discovered by João Gonçalves Zarco (1419)"),
}
