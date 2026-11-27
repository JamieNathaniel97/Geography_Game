"""Belgium (Belgium_plan.md): two sets, the 10 provinces plus Brussels (11), and the 3 regions (SET2: dissolved from the
provinces by tools/build_country.py, ids "BER-…" so each set has its own stats). The config and the card facts.
Card fact fields: see tools/at_facts.py. special = the language community (Dutch-, French- or German-speaking).
Written from general knowledge and the downloaded Wikipedia articles (tools/downloads/be/wiki/en, nl, fr); checked by hand.
Populations: Statbel, 1 January 2025 (via Wikidata); the provinces and Brussels, and the 3 regions, each add up to the
national total. Areas: "Provinces of Belgium".
"""

A3, A2 = "BEL", "BE"
WINDOW = (0.5, 47.5, 8.5, 53.5)
DETAIL = (2.4, 49.4, 6.5, 51.6)
POP_SOURCE, POP_YEAR, TOTAL = "Statbel, 1 January 2025 (via Wikidata)", "2025", 11825551
CAP_LL = {"Ghent": [3.725, 51.054], "Leuven": [4.701, 50.879], "Wavre": [4.611, 50.717]}

P = "Province"
BRUSSELS = dict(name="Brussels", names=["Brussels-Capital Region", "Brussels Capital Region", "Bruxelles", "Brussel", "Brussels-Capital"],
                capital="Brussels", capAlt=["City of Brussels", "Bruxelles", "Brussel"], pop=1255795, area=162, kind="Region (bilingual)")
PARTS = {
    "VAN": dict(lang="Dutch", name="Antwerp", names=["Antwerpen", "Anvers"], capital="Antwerp", capAlt=["Antwerpen", "Anvers"], pop=1921189, area=2876, kind=P),
    "VOV": dict(lang="Dutch", name="East Flanders", names=["Oost-Vlaanderen", "Flandre orientale", "Ostflandern"], capital="Ghent", capAlt=["Gent", "Gand"],
                pop=1602532, area=3007, kind=P, notTypo=["West Flanders"]),
    "VBR": dict(lang="Dutch", name="Flemish Brabant", names=["Vlaams-Brabant", "Brabant flamand", "Flämisch-Brabant"], capital="Leuven", capAlt=["Louvain"],
                pop=1204541, area=2118, kind=P, notTypo=["Walloon Brabant"]),
    "VLI": dict(lang="Dutch", name="Limburg", names=["Limbourg"], capital="Hasselt", pop=904919, area=2427, kind=P),
    "VWV": dict(lang="Dutch", name="West Flanders", names=["West-Vlaanderen", "Flandre occidentale", "Westflandern"], capital="Bruges", capAlt=["Brugge"],
                pop=1231585, area=3197, kind=P, notTypo=["East Flanders"]),
    "WHT": dict(lang="French", name="Hainaut", names=["Henegouwen", "Hennegau"], capital="Mons", capAlt=["Bergen"], pop=1365328, area=3813, kind=P),
    "WLG": dict(lang="French", name="Liège", names=["Luik", "Lüttich"], capital="Liège", capAlt=["Luik", "Lüttich"], pop=1122925, area=3857, kind=P),
    "WLX": dict(lang="French", name="Luxembourg", names=["Luxemburg", "Belgian Luxembourg"], capital="Arlon", capAlt=["Aarlen"], pop=296008, area=4459, kind=P),
    "WNA": dict(lang="French", name="Namur", names=["Namen"], capital="Namur", capAlt=["Namen"], pop=505348, area=3675, kind=P),
    "WBR": dict(lang="French", name="Walloon Brabant", names=["Brabant wallon", "Waals-Brabant", "Wallonisch-Brabant"], capital="Wavre", capAlt=["Waver"],
                pop=415381, area=1097, kind=P, notTypo=["Flemish Brabant"]),
    "BRU": BRUSSELS,
}

FB = dict(lang="Dutch and French", local="Brussel / Bruxelles", demonym="Bruxellois (Brusselaar)", dialect="Bilingual French and Dutch; Brusseleir (Marols) dialect",
          dish="Moules-frites and Brussels waffles", drink="Gueuze (Cantillon brewery)", festival="The Ommegang pageant and the Flower Carpet",
          club="RSC Anderlecht", river="Senne", wonder="The Sonian Forest (in part)", historic="Duchy of Brabant",
          landmark="The Grand-Place and the Atomium", unesco="The Grand-Place, Victor Horta's town houses and the Stoclet Palace",
          person="Audrey Hepburn (born in Ixelles)", known="The EU and NATO headquarters, chocolate and comics", company="Godiva (founded here)",
          special="Bilingual: French and Dutch")
FACTS = {
    "VAN": dict(local="Antwerpen", demonym="Antwerpenaar", dialect="Antwerpian (Brabantian Dutch)", dish="Fries and Antwerpse handjes (biscuits)",
                drink="De Koninck and Westmalle Trappist beer", festival="Tomorrowland (Boom)", club="Royal Antwerp FC", river="Scheldt",
                wonder="Kalmthout Heath", historic="Duchy of Brabant (the Margraviate of Antwerp)", landmark="The Cathedral of Our Lady and Antwerp Central Station",
                unesco="The Plantin-Moretus Museum and the beguinages", person="Peter Paul Rubens (worked in Antwerp)",
                known="Europe's second-biggest port and the diamond trade", company="Agfa-Gevaert", special="Dutch-speaking (Flemish Community)"),
    "VOV": dict(local="Oost-Vlaanderen", demonym="East Fleming", dialect="East Flemish", dish="Waterzooi and cuberdons (Ghent noses)",
                festival="The Ghent Festivities (Gentse Feesten)", club="KAA Gent", river="Scheldt and Lys (Leie)", historic="County of Flanders",
                landmark="Gravensteen castle and the Ghent Altarpiece", unesco="Ghent's belfry and beguinages",
                person="Emperor Charles V (born in Ghent)", known="Ghent, flowers (the Floralies) and textiles", company="Volvo Car Gent",
                special="Dutch-speaking (Flemish Community)"),
    "VBR": dict(local="Vlaams-Brabant", demonym="Flemish Brabander", dialect="Brabantian Dutch", drink="Stella Artois, and gueuze from the Pajottenland",
                club="OH Leuven", river="Dyle (Dijle) and Demer", wonder="The Sonian Forest (old beech forest)", historic="Duchy of Brabant",
                landmark="Leuven Town Hall", unesco="The Sonian Forest beeches and the Great Beguinage of Leuven",
                known="KU Leuven (founded 1425) and beer", company="AB InBev (Leuven)",
                special="Dutch-speaking (Flemish Community); six municipalities offer services in French"),
    "VLI": dict(local="Limburg", demonym="Limburger", dialect="Limburgish", dish="Limburgse vlaai", drink="Hasselt jenever",
                festival="Pukkelpop (Hasselt)", club="KRC Genk", river="Meuse (Maas)", wonder="Hoge Kempen National Park (Belgium's first)",
                historic="County of Loon (in the Prince-Bishopric of Liège)", landmark="Alden Biesen castle", unesco="The beguinages of Tongeren and Sint-Truiden",
                known="Former coal mines and the Haspengouw orchards", special="Dutch-speaking (Flemish Community)"),
    "VWV": dict(local="West-Vlaanderen", demonym="West Fleming", dialect="West Flemish", drink="Westvleteren Trappist beer",
                festival="The Procession of the Holy Blood in Bruges", club="Club Brugge", river="Yser (IJzer)", wonder="The Zwin and the coastal dunes",
                historic="County of Flanders", landmark="Bruges' belfry and canals, and the Menin Gate in Ypres",
                unesco="The historic centre of Bruges and the First World War cemeteries", person="James Ensor (painter, Ostend)",
                known="Bruges, the Belgian coast and the Ypres battlefields", company="Barco (Kortrijk)", special="Dutch-speaking (Flemish Community)"),
    "WHT": dict(local="Hainaut", demonym="Hainuyer", dialect="Picard and Walloon", dish="Chimay cheese", drink="Chimay Trappist beer",
                festival="The Binche Carnival (the Gilles) and the Doudou in Mons", club="Sporting Charleroi", river="Sambre and Scheldt",
                historic="County of Hainaut", landmark="Tournai Cathedral and the Mons belfry",
                unesco="Tournai Cathedral, the Spiennes flint mines, Grand-Hornu and the Canal du Centre boat lifts",
                known="Coal mining (the Borinage) and carnival", city="Charleroi", special="French-speaking (French Community)"),
    "WLG": dict(local="Liège", demonym="Liégeois", dialect="Walloon; German in the East Cantons (Eupen, Sankt Vith)", dish="Liège waffles and boulets à la liégeoise",
                drink="Jupiler beer and peket (gin)", festival="15 August in Outremeuse", club="Standard Liège", river="Meuse (Maas) and Ourthe",
                high="Signal de Botrange, 694 m: Belgium's highest", wonder="The High Fens (Hautes Fagnes)", historic="Prince-Bishopric of Liège",
                landmark="The Montagne de Bueren steps and the town of Spa", unesco="Spa (Great Spa Towns) and the Blegny-Mine",
                person="Georges Simenon (born in Liège)", known="Steel, Spa and the Spa-Francorchamps circuit", company="FN Herstal",
                special="French-speaking, with the German-speaking Community in the east"),
    "WLX": dict(local="Luxembourg", demonym="Luxembourgeois (Belgian)", dialect="Walloon, Gaumais, and Luxembourgish around Arlon", dish="Ardennes ham",
                drink="Orval Trappist beer", river="Semois and Ourthe", wonder="The Ardennes forests and the Semois valley",
                historic="Duchy of Luxembourg (split from the Grand Duchy in 1839)", landmark="Bouillon Castle and the Mardasson Memorial in Bastogne",
                known="Forests, the Battle of the Bulge (1944) and the least crowded province", special="French-speaking (French Community)"),
    "WNA": dict(local="Namur", demonym="Namurois", dialect="Walloon", drink="Rochefort and Maredsous beer", festival="The Walloon Festivities in Namur",
                river="Meuse and Sambre", wonder="The Caves of Han", historic="County of Namur", landmark="The Citadel of Namur and Dinant",
                unesco="The belfry of Namur", person="Adolphe Sax (inventor of the saxophone, born in Dinant)", known="The Meuse valley, caves and kayaking",
                special="French-speaking (French Community)"),
    "WBR": dict(local="Brabant wallon", demonym="Walloon Brabander", dialect="Walloon", dish="Tarte al djote (Nivelles cheese tart)", river="Dyle",
                historic="Duchy of Brabant", landmark="The Lion's Mound at Waterloo", known="The Battle of Waterloo (1815) and Louvain-la-Neuve's university",
                company="UCB (Braine-l'Alleud)", special="French-speaking (French Community)"),
    "BRU": FB,
}

SET2 = dict(
    code="ber", prefix="BER",
    groups={"VLG": ["VAN", "VOV", "VBR", "VLI", "VWV"], "WAL": ["WHT", "WLG", "WLX", "WNA", "WBR"], "BRU": ["BRU"]},
    parts={
        "VLG": dict(lang="Dutch", name="Flanders", names=["Flemish Region", "Vlaanderen", "Flandre", "Flandern", "Vlaams Gewest"], capital="",
                    capNote="Brussels (the Flemish government sits in Brussels, outside the region)", pop=6864766, area=13625, kind="Region"),
        "WAL": dict(lang="French", name="Wallonia", names=["Walloon Region", "Wallonie", "Wallonien", "Walloon"], capital="Namur", capAlt=["Namen"],
                    pop=3704990, area=16901, kind="Region"),
        "BRU": dict(BRUSSELS, name="Brussels-Capital Region", names=["Brussels", "Brussels Capital Region", "Bruxelles", "Brussel", "Brussels-Capital"]),
    },
    facts={
        "VLG": dict(local="Vlaanderen", demonym="Fleming", dialect="Dutch (Flemish dialects: West Flemish, Brabantian, Limburgish)",
                    dish="Flemish stew (stoofvlees) with fries", drink="Beer: Stella Artois, Westvleteren, Duvel", festival="The Ghent Festivities and Tomorrowland",
                    club="Club Brugge", river="Scheldt", wonder="Hoge Kempen National Park", historic="County of Flanders and Duchy of Brabant",
                    landmark="Bruges, Ghent and Antwerp's old towns", unesco="The Flemish belfries and beguinages, Bruges and the Plantin-Moretus Museum",
                    person="Peter Paul Rubens", known="The port of Antwerp, chocolate and cycling (the Tour of Flanders)", company="AB InBev",
                    city="Antwerp", special="Dutch-speaking (Flemish Community)"),
        "WAL": dict(local="Wallonie", demonym="Walloon", dialect="French, Walloon and Picard; German in the East Cantons",
                    dish="Liège waffles and Ardennes ham", drink="Trappist beers: Chimay, Orval and Rochefort", festival="The Binche Carnival",
                    club="Standard Liège", river="Meuse", high="Signal de Botrange, 694 m: Belgium's highest",
                    wonder="The Ardennes and the Caves of Han", historic="Prince-Bishopric of Liège, the counties of Hainaut and Namur, and Luxembourg",
                    landmark="The Citadel of Namur", unesco="The major mining sites, Tournai Cathedral, Spiennes and the Canal du Centre lifts",
                    person="Adolphe Sax (born in Dinant)", known="Steel and coal history, and the Ardennes", company="FN Herstal", city="Charleroi",
                    special="French-speaking, with the German-speaking Community in the east"),
        "BRU": FB,
    },
)
