"""The Netherlands' 12 provinces (Netherlands_plan.md): the config for tools/build_country.py and the Learning card facts.
Card fact fields: see tools/at_facts.py. special = land reclaimed from the sea, and how much lies below sea level.
Written from general knowledge and the downloaded Wikipedia articles (tools/downloads/nl/wiki/); checked by hand.
Populations: CBS (Statistics Netherlands) open data, table 70072ned, 1 January 2025 (the Netherlands has no
traditional census: these are the population register's figures). Areas: land area (CBS 2023), since the provinces'
totals include the IJsselmeer, the Wadden Sea and the estuaries. The Caribbean Netherlands are left off (DROP).
"""

A3, A2 = "NLD", "NL"
WINDOW = (0.5, 48.5, 10.5, 56.0)
DETAIL = (3.1, 50.6, 7.4, 53.7)
POP_SOURCE, POP_YEAR, TOTAL = "CBS, 1 January 2025 (population register)", "2025", 18044027
DROP = ("BQ1", "BQ2", "BQ3")
FIT_LIGHT = True                      # cut the light map to the shoreline: the IJsselmeer and Markermeer are water
CAP_LL = {"Lelystad": [5.471, 52.518]}

P = "Province"
PARTS = {
    "DR": dict(name="Drenthe", capital="Assen", pop=506529, area=2633, kind=P),
    "FL": dict(name="Flevoland", capital="Lelystad", pop=456395, area=1410, kind=P),
    "FR": dict(name="Friesland", names=["Fryslân", "Frisia", "Fryslan"], capital="Leeuwarden", capAlt=["Ljouwert"], pop=664222, area=3340, kind=P),
    "GE": dict(name="Gelderland", names=["Guelders"], capital="Arnhem", pop=2161358, area=4960, kind=P),
    "GR": dict(name="Groningen", capital="Groningen", pop=602833, area=2316, kind=P),
    "LI": dict(name="Limburg", capital="Maastricht", pop=1135328, area=2145, kind=P),
    "NB": dict(name="North Brabant", names=["Noord-Brabant", "Brabant"], capital="'s-Hertogenbosch",
               capAlt=["Den Bosch", "Hertogenbosch", "s-Hertogenbosch", "Bois-le-Duc"], pop=2664047, area=4902, kind=P),
    "NH": dict(name="North Holland", names=["Noord-Holland"], capital="Haarlem", pop=2992016, area=2663, kind=P, notTypo=["South Holland"]),
    "OV": dict(name="Overijssel", capital="Zwolle", pop=1195789, area=3317, kind=P),
    "UT": dict(name="Utrecht", capital="Utrecht", pop=1409144, area=1484, kind=P),
    "ZE": dict(name="Zeeland", names=["Zealand"], capital="Middelburg", pop=392969, area=1780, kind=P),
    "ZH": dict(name="South Holland", names=["Zuid-Holland"], capital="The Hague", capAlt=["Den Haag", "'s-Gravenhage", "s-Gravenhage", "Hague"],
               pop=3863397, area=2698, kind=P, notTypo=["North Holland"]),
}

FACTS = {
    "DR": dict(local="Drenthe", demonym="Drent", dialect="Drents (Dutch Low Saxon)", festival="The TT motorcycle races at Assen",
               wonder="The hunebedden (stone-age dolmens) and Drents-Friese Wold National Park", historic="Landschap Drenthe (a self-governing land)",
               landmark="The hunebedden of the Hondsrug", unesco="The Colonies of Benevolence (Frederiksoord, Wilhelminaoord, Veenhuizen)",
               known="Dolmens, cycling and peat moors", city="Emmen", special="High and dry: almost all above sea level"),
    "FL": dict(local="Flevoland", demonym="Flevolander", dialect="Mixed: settled from all over the country", festival="Lowlands music festival (Biddinghuizen)",
               club="Almere City", wonder="Oostvaardersplassen nature reserve", historic="The bed of the Zuiderzee until it was drained (1942–1968)",
               landmark="Schokland, a former island now on dry land", unesco="Schokland and surroundings",
               known="The newest province (1986), built entirely on reclaimed land", city="Almere",
               special="Almost all reclaimed: the Noordoostpolder and Flevopolder, most of it below sea level"),
    "FR": dict(local="Fryslân", demonym="Frisian", dialect="West Frisian (an official language) and Stellingwarfs", dish="Fryske dúmkes and Frisian sugar bread",
               drink="Beerenburg (herb gin)", festival="The Elfstedentocht (eleven-cities skating tour, when the ice allows)", club="SC Heerenveen",
               wonder="The Wadden Sea and the islands Vlieland, Terschelling, Ameland and Schiermonnikoog", historic="Frisia (the 'Frisian freedom')",
               landmark="The Oldehove leaning tower in Leeuwarden", unesco="The Wadden Sea and the Woudagemaal steam pumping station",
               person="M. C. Escher (born in Leeuwarden)", known="Lakes, sailing, skating and black-and-white Frisian cows",
               special="Built-up mounds (terpen) and coastal polders; the lake districts lie below sea level"),
    "GE": dict(local="Gelderland", demonym="Gelderlander", dialect="Achterhoeks (Low Saxon) and Veluws", festival="The Nijmegen Four Days Marches",
               club="Vitesse and NEC Nijmegen", river="Rhine, Waal and IJssel", wonder="Hoge Veluwe National Park",
               historic="The Duchy of Guelders", landmark="Het Loo Palace and the Kröller-Müller Museum", unesco="The Lower German Limes and the Dutch Water Defence Lines",
               known="The Veluwe forests and the Betuwe orchards", city="Nijmegen (the oldest city in the Netherlands)",
               special="River polders along the Rhine and Waal; mostly above sea level"),
    "GR": dict(local="Grunnen (Gronings)", demonym="Groninger", dialect="Gronings (Dutch Low Saxon)", dish="Mustard soup and Groninger koek",
               drink="Hooghoudt jenever", festival="Eurosonic Noorderslag music festival", club="FC Groningen", wonder="The Wadden Sea mudflats (wadlopen walks)",
               historic="The city of Groningen and the Ommelanden", landmark="The Martini Tower", unesco="The Wadden Sea",
               known="Europe's biggest gas field (and the earthquakes it caused)", company="Gasunie",
               special="Coastal polders won from the Wadden Sea; some land below sea level"),
    "LI": dict(local="Limburg", demonym="Limburger", dialect="Limburgish (a regional language)", dish="Vlaai (fruit tart)", drink="Brand and Gulpener beer",
               festival="Carnival (vastelaovend)", club="Fortuna Sittard, Roda JC and MVV Maastricht", river="Meuse (Maas)",
               high="Vaalserberg, 322.5 m: the highest point of the European Netherlands", wonder="The South Limburg hills and the Meinweg National Park",
               historic="The Duchy of Limburg and Upper Guelders", landmark="Maastricht's Vrijthof and the Three-Country Point",
               person="André Rieu", known="Hills, marl caves and the Maastricht Treaty (1992)", company="DSM (founded as the Dutch State Mines)",
               special="None: the hilliest province, all above sea level"),
    "NB": dict(local="Noord-Brabant", demonym="Brabander", dialect="Brabantian", dish="Worstenbrood (sausage roll)", drink="Bavaria and La Trappe beer",
               festival="Carnival", club="PSV Eindhoven", river="Meuse (Maas)", wonder="De Biesbosch National Park and the Loonse en Drunense Duinen",
               historic="The Duchy of Brabant", landmark="St John's Cathedral in 's-Hertogenbosch and the Efteling theme park",
               unesco="The Dutch Water Defence Lines", person="Vincent van Gogh (born in Zundert)", known="Technology, carnival and the Efteling",
               company="Philips and ASML", city="Eindhoven", special="Mostly above sea level; the Biesbosch and the north-west are polders"),
    "NH": dict(local="Noord-Holland", demonym="North Hollander", dialect="Hollandic and West Frisian dialects (Westfries)", dish="Raw herring and Edam cheese",
               drink="Heineken beer", festival="King's Day in Amsterdam", club="Ajax and AZ Alkmaar", river="Amstel and IJ",
               wonder="Texel and the Zuid-Kennemerland dunes", historic="The County of Holland and West Friesland",
               landmark="Amsterdam's canals and the Zaanse Schans windmills", unesco="Amsterdam's canal ring, the Beemster Polder and the Defence Line of Amsterdam",
               person="Anne Frank (hid in Amsterdam)", known="Amsterdam, tulips and cheese markets", company="Heineken and KLM", city="Amsterdam",
               special="The Beemster (1612), Haarlemmermeer (1852) and Wieringermeer (1930) polders; much of it below sea level"),
    "OV": dict(local="Overiessel (Low Saxon)", demonym="Overijsselaar", dialect="Twents and Sallands (Dutch Low Saxon)", drink="Grolsch beer",
               festival="Deventer Book Market", club="FC Twente, PEC Zwolle and Go Ahead Eagles", river="IJssel and Vecht",
               wonder="Weerribben-Wieden National Park and Giethoorn's canals", historic="The Oversticht (the Bishopric of Utrecht's lands)",
               landmark="Giethoorn, the village of canals", unesco="Ommerschans (Colonies of Benevolence)", known="Twente's textile industry",
               company="Grolsch", city="Enschede", special="Mostly above sea level; low polders in the north-west"),
    "UT": dict(local="Utrecht", demonym="Utrechter", dialect="Utrechts", club="FC Utrecht", river="Vecht and Lek", high="Amerongse Berg, 69 m",
               wonder="Utrechtse Heuvelrug National Park", historic="The Prince-Bishopric of Utrecht", landmark="The Dom Tower",
               unesco="The Rietveld Schröder House, the Lower German Limes and the Dutch Water Defence Lines",
               person="Dick Bruna (creator of Miffy)", known="The country's railway hub and its university", company="Rabobank",
               special="Peat polders: the west lies slightly below sea level"),
    "ZE": dict(local="Zeeland", demonym="Zeelander", dialect="Zeelandic", dish="Mussels, oysters and Zeeuwse bolus", festival="Ring riding (ringrijden)",
               river="Scheldt", wonder="Oosterschelde National Park", historic="The County of Zeeland", landmark="The Delta Works (the Oosterscheldekering)",
               person="Michiel de Ruyter (admiral, born in Vlissingen)", known="The Delta Works, built after the 1953 flood, and beaches",
               special="Islands of polders joined by dikes and dams; much of it below sea level"),
    "ZH": dict(local="Zuid-Holland", demonym="South Hollander", dialect="Hollandic", dish="Gouda cheese and stroopwafels", drink="Schiedam jenever",
               festival="North Sea Jazz Festival in Rotterdam", club="Feyenoord", river="Nieuwe Maas and Oude Rijn",
               wonder="The bulb fields and the dunes of the coast", historic="The County of Holland",
               landmark="The Kinderdijk windmills and the Binnenhof", unesco="Kinderdijk-Elshout, the Van Nelle Factory and the Lower German Limes",
               person="Rembrandt (born in Leiden)", known="Europe's biggest port (Rotterdam), government (The Hague) and bulb fields",
               city="Rotterdam", special="Holds the lowest point (−6.76 m, Zuidplaspolder); much of it below sea level"),
}
