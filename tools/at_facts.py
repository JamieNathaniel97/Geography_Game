"""Austria's 9 states (Austria_plan.md): the config for tools/build_country.py and the Learning card facts.

Card fact fields (shared by the overnight_v2 countries; any may be missing, the card leaves out what's missing):
  local (name in the local language)  demonym  dialect  dish  drink  festival  club (football: the biggest club)
  river  high (highest point)  wonder (natural wonder or national park)  historic (historic region or old kingdom)
  landmark (famous castle or landmark)  unesco  person (a famous person from there)  known (known for)
  company  city (largest city, if it isn't the capital)  special (Austria: ski resorts or Alpine peaks)
Written from general knowledge and the downloaded Wikipedia articles (tools/downloads/at/wiki/); checked by hand.
"""

A3, A2 = "AUT", "AT"
WINDOW = (5.5, 43.5, 21.5, 51.6)      # Austria and its neighbours, with room for a tall phone screen
DETAIL = (9.3, 46.3, 17.3, 49.1)      # where the high-resolution shoreline (lakes) was downloaded
POP_SOURCE, POP_YEAR, TOTAL = "Statistik Austria, 1 January 2025 (via Wikidata)", "2025", 9197213
FLAGS = "flags_state"                 # the state flags with arms: Salzburg, Vienna and Vorarlberg share one civil flag
CAP_LL = {"St. Pölten": [15.626, 48.204]}

PARTS = {
    "1": dict(name="Burgenland", capital="Eisenstadt", pop=301790, area=3965, kind="State"),
    "2": dict(name="Carinthia", names=["Kärnten", "Karnten", "Kaernten"], capital="Klagenfurt",
              capAlt=["Klagenfurt am Wörthersee"], pop=570095, area=9537, kind="State"),
    "3": dict(name="Lower Austria", names=["Niederösterreich", "Niederosterreich", "Niederoesterreich"], capital="St. Pölten",
              capAlt=["Sankt Pölten", "St Pölten", "St. Polten", "St Polten", "Sankt Polten"], pop=1727514, area=19180,
              kind="State", notTypo=["Upper Austria"]),
    "4": dict(name="Upper Austria", names=["Oberösterreich", "Oberosterreich", "Oberoesterreich"], capital="Linz",
              pop=1535519, area=11983, kind="State", notTypo=["Lower Austria"]),
    "5": dict(name="Salzburg", names=["Land Salzburg", "Salzburgerland"], capital="Salzburg", pop=572846, area=7155, kind="State"),
    "6": dict(name="Styria", names=["Steiermark"], capital="Graz", pop=1271716, area=16399, kind="State"),
    "7": dict(name="Tyrol", names=["Tirol"], capital="Innsbruck", pop=777660, area=12648, kind="State"),
    "8": dict(name="Vorarlberg", capital="Bregenz", pop=411784, area=2602, kind="State"),
    "9": dict(name="Vienna", names=["Wien"], capital="Vienna", capAlt=["Wien"], pop=2028289, area=415, kind="State and city"),
}

FACTS = {
    "1": dict(local="Burgenland", demonym="Burgenlander", dialect="Central Bavarian dialects, with Burgenland Croatian and Hungarian minorities",
              dish="Fish from Lake Neusiedl and Martini goose", drink="Wine (Blaufränkisch)", festival="St. Martin's Day goose and new wine",
              river="Raab (Rába) and the Leitha", high="Geschriebenstein, 884 m", wonder="Lake Neusiedl and Neusiedler See–Seewinkel National Park",
              historic="Part of the Kingdom of Hungary until 1921", landmark="Esterházy Palace and Forchtenstein Castle",
              unesco="Fertő / Neusiedlersee Cultural Landscape", person="Joseph Haydn worked in Eisenstadt; Franz Liszt was born in Raiding",
              known="Wine, wind power and the youngest state (joined Austria in 1921)"),
    "2": dict(local="Kärnten", demonym="Carinthian", dialect="Carinthian (Southern Bavarian), with a Slovene minority",
              dish="Kärntner Kasnudeln (cheese dumplings)", drink="Beer and schnapps", festival="Villacher Kirchtag",
              river="Drava (Drau)", high="Grossglockner, 3,798 m (on the border with Tyrol): Austria's highest",
              wonder="Lake Wörthersee and Hohe Tauern National Park", historic="Duchy of Carinthia",
              landmark="Hochosterwitz Castle and the Pyramidenkogel tower", unesco="The Keutschacher See pile dwelling (Prehistoric Pile Dwellings around the Alps)",
              person="Ingeborg Bachmann (writer)", known="Lakes and summer holidays",
              special="Bad Kleinkirchheim and the Nassfeld ski area"),
    "3": dict(local="Niederösterreich", demonym="Lower Austrian", dialect="Central Bavarian", dish="Wachauer apricots and Wiener Schnitzel",
              drink="Wine (Grüner Veltliner from the Wachau)", festival="The Wachau wine and apricot festivals", club="SKN St. Pölten",
              river="Danube", high="Schneeberg (Klosterwappen), 2,076 m", wonder="Donau-Auen National Park and the Wachau valley",
              historic="The Archduchy of Austria below the Enns: the Habsburgs' heartland", landmark="Melk Abbey",
              unesco="The Wachau, the Semmering Railway, Baden bei Wien (Great Spa Towns) and the Danube Limes", person="Egon Schiele (painter)",
              known="Wine, farming and the countryside around Vienna",
              special="Semmering, Vienna's ski resort"),
    "4": dict(local="Oberösterreich", demonym="Upper Austrian", dialect="Central Bavarian (Mühlviertel and Innviertel dialects)",
              dish="Linzer Torte and Mühlviertler Knödel", drink="Most (pear and apple cider)", festival="Ars Electronica and Linz's Pflasterspektakel",
              club="LASK", river="Danube and the Inn", high="Hoher Dachstein, 2,995 m", wonder="The Salzkammergut lakes and Kalkalpen National Park",
              historic="The Archduchy of Austria above the Enns", landmark="Linz's Pöstlingberg and St. Florian Monastery",
              unesco="Hallstatt–Dachstein / Salzkammergut, the Attersee and Mondsee pile dwellings, the Danube Limes", person="Anton Bruckner (composer)",
              known="Steel, chemicals and industry", company="Voestalpine and KTM", special="Hinterstoder and the Dachstein West ski area"),
    "5": dict(local="Salzburg", demonym="Salzburger", dialect="Central Bavarian (Salzburg dialect)", dish="Salzburger Nockerl (a soufflé)",
              drink="Stiegl beer", festival="The Salzburg Festival (music and theatre, since 1920)", club="Red Bull Salzburg",
              river="Salzach", high="Grossvenediger, 3,657 m (on the border with Tyrol)", wonder="Krimml Waterfalls and Hohe Tauern National Park",
              historic="The Prince-Archbishopric of Salzburg (joined Austria in 1816)", landmark="Hohensalzburg Fortress",
              unesco="The historic centre of Salzburg", person="Wolfgang Amadeus Mozart", known="Mozart, music and The Sound of Music",
              company="Red Bull (Fuschl am See)", special="Saalbach-Hinterglemm, Zell am See–Kaprun and the Kitzsteinhorn glacier"),
    "6": dict(local="Steiermark", demonym="Styrian", dialect="Central and Southern Bavarian (Styrian)", dish="Pumpkin seed oil and Backhendl (fried chicken)",
              drink="Schilcher rosé and wines from the South Styrian hills", festival="Aufsteirern folk festival in Graz", club="Sturm Graz",
              river="Mur", high="Hoher Dachstein, 2,995 m (on the border with Upper Austria)", wonder="Gesäuse National Park",
              historic="Duchy of Styria", landmark="Graz's Schlossberg clock tower and Mariazell Basilica",
              unesco="Graz's historic centre and Schloss Eggenberg; the Semmering Railway", person="Arnold Schwarzenegger (born in Thal)",
              known="Cars and engineering; the Red Bull Ring (Austrian Grand Prix)", company="Magna Steyr and AVL",
              special="Schladming–Dachstein (Planai)"),
    "7": dict(local="Tirol", demonym="Tyrolean", dialect="Southern Bavarian (Tyrolean)", dish="Tiroler Gröstl and Speck",
              drink="Schnapps", festival="The Innsbruck Christmas markets and the Hahnenkamm race in Kitzbühel", club="WSG Tirol",
              river="Inn", high="Grossglockner, 3,798 m (on the border with Carinthia)", wonder="Hohe Tauern National Park and the Zillertal Alps",
              historic="County of Tyrol (South Tyrol went to Italy in 1919)", landmark="The Golden Roof in Innsbruck",
              person="Andreas Hofer (folk hero of 1809)",
              known="Skiing, mountains and two Winter Olympics in Innsbruck (1964, 1976)", company="Swarovski (Wattens)",
              special="Kitzbühel, St. Anton, Ischgl, Sölden and the Stubai Glacier"),
    "8": dict(local="Vorarlberg", demonym="Vorarlberger", dialect="Alemannic (close to Swiss German)", dish="Käsknöpfle (cheese noodles)",
              drink="Mohrenbräu beer", festival="The Bregenz Festival (opera on a floating stage)", club="SCR Altach",
              river="Rhine and the Ill", high="Piz Buin, 3,312 m", wonder="Lake Constance and the Bregenzerwald",
              historic="Habsburg lands acquired in the 14th and 15th centuries", landmark="The Bregenz Festival's lake stage",
              known="Textiles, industry and the Alemannic culture",
              company="Doppelmayr (cable cars) and Blum", city="Dornbirn (Bregenz is the capital)",
              special="Lech-Zürs (part of the Arlberg ski area) and Montafon"),
    "9": dict(local="Wien", demonym="Viennese", dialect="Viennese German (Wienerisch)", dish="Wiener Schnitzel and Sachertorte",
              drink="Coffee (Viennese coffee houses) and Heuriger wine", festival="The Vienna Opera Ball and the Donauinselfest",
              club="Rapid Wien and Austria Wien", river="Danube", high="Hermannskogel, 542 m", wonder="The Vienna Woods (Wienerwald)",
              historic="Capital of the Habsburg monarchy and Austria-Hungary", landmark="Schönbrunn Palace and St. Stephen's Cathedral",
              unesco="The historic centre of Vienna, Schönbrunn Palace and the Danube Limes", person="Sigmund Freud, and composers from Schubert to Strauss",
              known="Music, coffee houses and the UN's Vienna office", company="Erste Group and OMV"),
}
