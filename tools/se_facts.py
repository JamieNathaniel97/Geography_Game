"""Sweden's 21 counties (län) (Sweden_plan.md): the config for tools/build_country.py and the Learning card facts.
Card fact fields: see tools/at_facts.py; Sweden's own three: land (historic land and province), sami (the Sámi area),
invention (a Swedish invention or brand from there). Written from general knowledge and the downloaded Wikipedia
articles (tools/downloads/se/wiki/); checked by hand; facts not found are left out.
Populations: Statistics Sweden (SCB), the population register on 31 December 2024 (its open API); the counties add up to
10,587,710. Games 5 and 6 use the county coats of arms (official; Wikimedia Commons).
"""

A3, A2 = "SWE", "SE"
WINDOW = (3.0, 53.0, 32.0, 70.5)
DETAIL = (10.8, 55.2, 24.3, 69.2)
POP_SOURCE, POP_YEAR, TOTAL = "Statistics Sweden, 31 December 2024 (population register)", "2024", 10587710
FLAGS, EMBLEMS = "coats", True
DETAIL_TOL = 0.0035                   # the archipelagos: 8.5 MB of detail tiles at the usual 0.002°
CAP_LL = {"Gothenburg": [11.967, 57.707]}

C = "County"


def P(name, seat, pop, area, *names, **kw):
    short = name.replace(" County", "")
    return dict(name=name, names=[short, f"{short} län", f"{short}s län"] + list(names), capital=seat, pop=pop, area=area, kind=C, **kw)


PARTS = {
    "AB": P("Stockholm County", "Stockholm", 2473307, 6519),
    "C": P("Uppsala County", "Uppsala", 407912, 8207),
    "D": P("Södermanland County", "Nyköping", 301542, 6102, "Sodermanland", "Sörmland"),
    "E": P("Östergötland County", "Linköping", 472446, 10602, "Ostergotland", "East Gothland"),
    "F": P("Jönköping County", "Jönköping", 370009, 10495, "Jonkoping"),
    "G": P("Kronoberg County", "Växjö", 203351, 8466, capAlt=["Vaxjo"]),
    "H": P("Kalmar County", "Kalmar", 246352, 11218),
    "I": P("Gotland County", "Visby", 60971, 3151, "Gotland"),
    "K": P("Blekinge County", "Karlskrona", 157223, 2946),
    "M": P("Skåne County", "Malmö", 1428626, 11035, "Skane", "Scania", capAlt=["Malmo"]),
    "N": P("Halland County", "Halmstad", 345074, 5461, notTypo=["Gotland County"]),
    "O": P("Västra Götaland County", "Gothenburg", 1772821, 23949, "Vastra Gotaland", "West Gothland", capAlt=["Göteborg", "Goteborg"]),
    "S": P("Värmland County", "Karlstad", 283384, 17591, "Varmland"),
    "T": P("Örebro County", "Örebro", 308375, 8546, "Orebro"),
    "U": P("Västmanland County", "Västerås", 281158, 5146, "Vastmanland", capAlt=["Vasteras"]),
    "W": P("Dalarna County", "Falun", 286546, 28189, "Dalecarlia"),
    "X": P("Gävleborg County", "Gävle", 284558, 18199, "Gavleborg", capAlt=["Gavle"]),
    "Y": P("Västernorrland County", "Härnösand", 241458, 21684, "Vasternorrland", capAlt=["Harnosand"]),
    "Z": P("Jämtland County", "Östersund", 132839, 49341, "Jamtland", capAlt=["Ostersund"]),
    "AC": P("Västerbotten County", "Umeå", 281138, 55186, "Vasterbotten", capAlt=["Umea"], notTypo=["Norrbotten County"]),
    "BD": P("Norrbotten County", "Luleå", 248620, 98245, capAlt=["Lulea"], notTypo=["Västerbotten County"]),
}

FACTS = {
    "AB": dict(local="Stockholms län", demonym="Stockholmer", dialect="Central Swedish (Stockholm speech)", dish="Swedish meatballs (köttbullar)",
               festival="The Nobel Prize ceremony and Stockholm Pride", club="AIK, Djurgården and Hammarby", river="Norrström (where Lake Mälaren meets the Baltic)",
               wonder="The Stockholm archipelago (about 30,000 islands)", historic="Uppland and Södermanland", landmark="The Vasa Museum and the Royal Palace",
               unesco="Drottningholm Palace, Skogskyrkogården, and Birka and Hovgården", person="Greta Garbo", known="The capital: government, finance and tech start-ups",
               company="Spotify and Ericsson", land="Svealand (Uppland and Södermanland)", sami="No", invention="Dynamite (Alfred Nobel, born in Stockholm)"),
    "C": dict(local="Uppsala län", demonym="Uppsalabo", dialect="Uppland dialects", festival="Walpurgis Night (Valborg) at Uppsala University",
              club="IK Sirius", river="Fyrisån", historic="Uppland: Old Uppsala was a seat of the early Swedish kings", landmark="Uppsala Cathedral and the royal mounds of Old Uppsala",
              person="Anders Celsius (astronomer)", known="Uppsala University (1477), Scandinavia's oldest", land="Svealand (Uppland)", sami="No",
              invention="The Celsius temperature scale"),
    "D": dict(local="Södermanlands län", demonym="Sörmlänning", dialect="Södermanland dialects", landmark="Gripsholm Castle and Nyköping Castle",
              historic="Södermanland (Sörmland)", known="Manor houses, lakes and Eskilstuna's metal industry", company="Volvo Construction Equipment (Eskilstuna)",
              city="Eskilstuna", land="Svealand (Södermanland)", sami="No"),
    "E": dict(local="Östergötlands län", demonym="Östgöte", dialect="East Gothic dialects", club="IFK Norrköping", river="Motala ström",
              wonder="Lake Vättern's east shore and Omberg", historic="Östergötland", landmark="The Göta Canal's Berg locks and Vadstena Abbey",
              person="Saint Birgitta (founded Vadstena Abbey)", known="Aircraft and the Göta Canal", company="Saab (Linköping)", land="Götaland (Östergötland)",
              sami="No", invention="The Saab Gripen fighter jet"),
    "F": dict(local="Jönköpings län", demonym="Jönköpingsbo", dialect="Småland dialects", festival="DreamHack (a giant LAN party)", club="Jönköpings Södra",
              wonder="Lake Vättern and Visingsö island", historic="Småland", landmark="Visingsö and the Match Museum", known="Matches, furniture and the Bible Belt of Sweden",
              company="Husqvarna", land="Götaland (Småland)", sami="No", invention="The safety match (Jönköping, 1845)"),
    "G": dict(local="Kronobergs län", demonym="Smålänning", dialect="Småland dialects", club="Östers IF", wonder="Lakes and forests: the 'Kingdom of Crystal' glassworks",
              historic="Småland", landmark="The IKEA Museum in Älmhult", person="Carl Linnaeus (born in Råshult)", known="IKEA, founded in Älmhult in 1943",
              company="IKEA", land="Götaland (Småland)", sami="No", invention="Flat-pack furniture (IKEA)"),
    "H": dict(local="Kalmar län", demonym="Kalmarbo", dialect="Småland and Öland dialects", club="Kalmar FF", wonder="Öland's Stora Alvaret limestone plain",
              historic="Småland and Öland (the Kalmar Union of 1397)", landmark="Kalmar Castle and the Öland Bridge", unesco="The Agricultural Landscape of Southern Öland",
              person="Astrid Lindgren (born in Vimmerby)", known="Glass (Orrefors, Kosta) and summer on Öland", land="Götaland (Småland and Öland)", sami="No",
              invention="Pippi Longstocking (Astrid Lindgren)"),
    "I": dict(local="Gotlands län", demonym="Gotlander (gutar)", dialect="Gutnish", dish="Saffron pancake (saffranspannkaka)",
              festival="Medieval Week in Visby and Almedalen political week", wonder="The raukar sea stacks of Fårö", historic="Gotland (Hanseatic trading island)",
              landmark="Visby's town wall", unesco="The Hanseatic Town of Visby", person="Ingmar Bergman (lived on Fårö)", known="Medieval Visby and summer holidays",
              land="Götaland (Gotland)", sami="No"),
    "K": dict(local="Blekinge län", demonym="Blekinger", dialect="Blekinge dialect (South Swedish)", club="Mjällby AIF", wonder="The Blekinge archipelago",
              historic="Blekinge (Danish until 1658)", landmark="The naval base and Admiralty Church in Karlskrona", unesco="The Naval Port of Karlskrona",
              known="The 'garden of Sweden' and the navy", land="Götaland (Blekinge)", sami="No"),
    "M": dict(local="Skåne län", demonym="Scanian (skåning)", dialect="Scanian", dish="Spettekaka (spit cake) and goose dinner on St Martin's Eve",
              festival="The Malmö Festival", club="Malmö FF", wonder="Kullaberg and Söderåsen National Park", historic="Scania (Danish until 1658)",
              landmark="The Turning Torso, the Øresund Bridge and Ales stenar", person="Zlatan Ibrahimović (born in Malmö)",
              known="Farmland, Lund University and the link to Copenhagen", company="Tetra Pak (Lund)", land="Götaland (Skåne)", sami="No",
              invention="The Tetra Pak carton and Bluetooth (Ericsson in Lund)"),
    "N": dict(local="Hallands län", demonym="Hallänning", dialect="Halland dialects", club="Halmstads BK", wonder="Sandy beaches (Tylösand)",
              historic="Halland (Danish until 1645)", landmark="Varberg Fortress", unesco="The Grimeton Radio Station in Varberg",
              known="Beaches, surfing and farming", land="Götaland (Halland)", sami="No"),
    "O": dict(local="Västra Götalands län", demonym="West Swede (Gothenburger in the city)", dialect="Gothenburg and West Gothic dialects",
              festival="The Gothia Cup (youth football) and Way Out West", club="IFK Göteborg", river="Göta älv", wonder="Lake Vänern, the EU's biggest lake",
              historic="Västergötland, Bohuslän and Dalsland", landmark="Liseberg amusement park and Läckö Castle", unesco="The Tanum rock carvings",
              known="Scandinavia's biggest port and car-making", company="Volvo and SKF", city="Gothenburg is the capital and largest",
              land="Götaland (Västergötland, Bohuslän, Dalsland)", sami="No", invention="The three-point seat belt (Volvo) and the self-aligning ball bearing (SKF)"),
    "S": dict(local="Värmlands län", demonym="Värmlänning", dialect="Värmland dialects", river="Klarälven", wonder="Forests and the north shore of Lake Vänern",
              historic="Värmland", landmark="Mårbacka (Selma Lagerlöf's home)", person="Selma Lagerlöf (the first woman to win the Nobel Prize in Literature)",
              known="Forests, paper mills and storytelling", land="Svealand (Värmland)", sami="No"),
    "T": dict(local="Örebro län", demonym="Örebroare", dialect="Närke dialect", club="Örebro SK", historic="Närke", landmark="Örebro Castle",
              known="Logistics and its central position", land="Svealand (Närke, with parts of Västmanland and Värmland)", sami="No"),
    "U": dict(local="Västmanlands län", demonym="Västmanlänning", dialect="Västmanland dialects", historic="Västmanland (the Bergslagen mining district)",
              landmark="Anundshög (Sweden's largest burial mound)", unesco="Engelsberg Ironworks", known="Engineering and electrical power",
              company="ABB (Västerås)", land="Svealand (Västmanland)", sami="No"),
    "W": dict(local="Dalarnas län", demonym="Dalecarlian (dalkarl)", dialect="Dalecarlian (Elfdalian)", festival="Midsummer around Lake Siljan, and the Vasaloppet ski race",
              high="Storvätteshågna, 1,204 m", wonder="Lake Siljan", historic="Dalarna (Dalecarlia)", landmark="The Dala horse workshops in Nusnäs",
              unesco="The Great Copper Mountain in Falun", person="Anders Zorn (painter, Mora)", known="Folk traditions, copper and skiing (Sälen, Idre)",
              city="Borlänge", land="Svealand (Dalarna)", sami="A little: southern Sámi reindeer herding around Idre", invention="The Dala horse"),
    "X": dict(local="Gävleborgs län", demonym="Gävleborgare", dialect="Hälsingland and Gästrikland dialects", club="Gefle IF", river="Ljusnan",
              historic="Gästrikland and Hälsingland", landmark="The Gävle Goat (a giant straw goat each Christmas)", unesco="The Decorated Farmhouses of Hälsingland",
              known="Forests, steel (Sandviken) and the Gävle Goat", company="Sandvik", land="Norrland (Gästrikland and Hälsingland)", sami="No"),
    "Y": dict(local="Västernorrlands län", demonym="Västernorrlänning", dialect="Ångermanland and Medelpad dialects", river="Ångermanälven and Indalsälven",
              wonder="The High Coast (still rising after the ice age)", historic="Ångermanland and Medelpad", landmark="The High Coast Bridge",
              unesco="The High Coast / Kvarken Archipelago", known="Forests, paper and the High Coast", city="Sundsvall", land="Norrland (Ångermanland and Medelpad)",
              sami="No"),
    "Z": dict(local="Jämtlands län", demonym="Jämte", dialect="Jamtlandic, and Southern Sámi", club="Östersunds FK", high="Helagsfjället, 1,797 m",
              wonder="Lake Storsjön (and its legendary monster)", historic="Jämtland and Härjedalen (Norwegian until 1645)", landmark="Åre ski resort and Frösön",
              known="Skiing (Åre) and mountains", land="Norrland (Jämtland and Härjedalen)", sami="Yes: southern Sámi reindeer-herding lands"),
    "AC": dict(local="Västerbottens län", demonym="Västerbottning", dialect="Västerbotten dialects, and Ume and Southern Sámi", dish="Västerbotten cheese",
               river="Ume River and Skellefte River", high="Norra Sytertoppen, 1,768 m", historic="Västerbotten and southern Lapland",
               landmark="The Sara Cultural Centre in Skellefteå", person="Stieg Larsson (author of the Millennium books)", known="Umeå University, mining and forests",
               company="Boliden (mining) and Northvolt (batteries, Skellefteå)", land="Norrland (Västerbotten and Lapland)", sami="Yes: the Lapland part (Ume and Southern Sámi)"),
    "BD": dict(local="Norrbottens län", demonym="Norrbottning", dialect="Meänkieli (Tornedalen Finnish) and Northern Sámi", festival="The Jokkmokk Winter Market (since 1605)",
               river="Torne, Kalix and Lule rivers", high="Kebnekaise, about 2,097 m: Sweden's highest", wonder="Abisko National Park and the northern lights",
               historic="Norrbotten and northern Lapland", landmark="The Icehotel at Jukkasjärvi", unesco="The Laponian Area and Gammelstad Church Town",
               known="Iron ore (Kiruna), the midnight sun and Sápmi", company="LKAB (Kiruna iron mine)", land="Norrland (Norrbotten and Lapland)",
               sami="Yes: most of Swedish Sápmi", invention="The Icehotel (the first, 1989)"),
}
