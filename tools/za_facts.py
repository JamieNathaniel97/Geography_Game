"""South Africa's 9 provinces (South_Africa_plan.md): the config for tools/build_country.py and the Learning card facts.
Card fact fields: see tools/at_facts.py; South Africa's own three: langs (main home languages), wildlife (Big Five reserve
or famous wildlife), before (what it was before 1994). No flag games (the provinces have no official flags).
Lesotho and Eswatini are enclaves: drawn in their flag colours (Lesotho blue, Eswatini red), tappable in Learning mode,
with a short card ("its own map: coming soon"). The Prince Edward Islands are left off (Natural Earth leaves them out).
Written from general knowledge and the downloaded Wikipedia articles (tools/downloads/za/wiki/); checked by hand.
Populations: Census 2022 (Stats SA). Its published provincial figures add up to 62,027,502, one less than the national
total of 62,027,503 (rounding in the census weighting); TOTAL_TOL allows that.
"""

A3, A2, CONT = "ZAF", "ZA", "Africa"
WINDOW = (8.0, -40.0, 41.0, -16.0)
DETAIL = (16.3, -35.0, 33.0, -22.0)
CLIP = (10, -36, 40, -15)            # the Prince Edward Islands (part of the Western Cape) are left off
POP_SOURCE, POP_YEAR, TOTAL, TOTAL_TOL = "Stats SA, Census 2022", "2022 census", 62027503, 1
CAP_LL = {"Mahikeng": [25.644, -25.865]}
FLAGS = "no-flags"                    # no official provincial flags: none on the cards either (the enclaves keep their national flags)

P = "Province"
PARTS = {
    "EC": dict(name="Eastern Cape", names=["Eastern Cape Province", "Oos-Kaap", "iMpuma-Koloni"], capital="Bhisho", capAlt=["Bisho"],
               pop=7230204, area=168966, kind=P, notTypo=["Western Cape"]),
    "FS": dict(name="Free State", names=["Orange Free State", "Vrystaat", "Foreisetata"], capital="Bloemfontein", pop=2964412, area=129825, kind=P),
    "GT": dict(name="Gauteng", capital="Johannesburg", capAlt=["Joburg", "Jozi"], pop=15099422, area=18178, kind=P),
    "NL": dict(name="KwaZulu-Natal", names=["KwaZulu Natal", "KZN", "Natal"], capital="Pietermaritzburg", pop=12423907, area=94361, kind=P),
    "LP": dict(name="Limpopo", names=["Northern Province"], capital="Polokwane", capAlt=["Pietersburg"], pop=6572720, area=125754, kind=P),
    "MP": dict(name="Mpumalanga", capital="Mbombela", capAlt=["Nelspruit"], pop=5143324, area=76495, kind=P),
    "NW": dict(name="North West", names=["North-West", "Bokone Bophirima", "Noordwes"], capital="Mahikeng", capAlt=["Mafikeng", "Mafeking"],
               pop=3804548, area=104882, kind=P),
    "NC": dict(name="Northern Cape", names=["Noord-Kaap"], capital="Kimberley", pop=1355946, area=372889, kind=P),
    "WC": dict(name="Western Cape", names=["Wes-Kaap", "Western Cape Province"], capital="Cape Town", capAlt=["Kaapstad"], pop=7433019,
               area=129462, kind=P, notTypo=["Eastern Cape"]),
}

ENCLAVES = {
    "LS": dict(a3="LSO", name="Lesotho", capital="Maseru", kind="Independent country (an enclave inside South Africa)", fill="#7fa4d6",
               about="A mountain kingdom entirely surrounded by South Africa; all of it lies above 1,000 m"),
    "SZ": dict(a3="SWZ", name="Eswatini", names=["Swaziland"], capital="Mbabane", kind="Independent country (bordering South Africa and Mozambique)",
               fill="#d98073", about="One of the world's last absolute monarchies, known for the Umhlanga Reed Dance"),
}

FACTS = {
    "EC": dict(local="iMpuma-Koloni (Xhosa)", demonym="Eastern Caper", dialect="isiXhosa", dish="Umngqusho (samp and beans)", drink="Umqombothi (sorghum beer)",
               festival="The National Arts Festival in Makhanda", club="Chippa United", river="Great Kei and Great Fish rivers", high="Ben Macdhui, 3,001 m",
               wonder="The Wild Coast and Addo Elephant National Park", historic="The Xhosa kingdoms and the Cape frontier", landmark="Hole in the Wall on the Wild Coast",
               unesco="Part of the Cape Floral Region (Baviaanskloof)", person="Nelson Mandela (born in Mvezo)", known="The Wild Coast and car-making (Gqeberha, East London)",
               company="Volkswagen South Africa (Kariega)", city="Gqeberha (Port Elizabeth)", langs="isiXhosa (about four in five), Afrikaans, English",
               wildlife="Addo Elephant National Park", before="Cape Province, with the Transkei and Ciskei homelands"),
    "FS": dict(local="Foreisetata (Sotho) / Vrystaat (Afrikaans)", demonym="Free Stater", dialect="Sesotho", festival="Macufe arts festival and the Bloemfontein Rose Festival",
               river="Orange and Vaal rivers", wonder="Golden Gate Highlands National Park", historic="The Orange Free State (a Boer republic, 1854–1902)",
               landmark="Naval Hill and the Vredefort crater", unesco="The Vredefort Dome (the world's largest known impact crater)",
               person="J. R. R. Tolkien (born in Bloemfontein)", known="Maize farming, gold mining (Welkom) and the judicial capital",
               company="Sasol (founded at Sasolburg)", langs="Sesotho, Afrikaans, isiXhosa", wildlife="Golden Gate's eland and black wildebeest",
               before="Orange Free State Province, with QwaQwa and part of Bophuthatswana"),
    "GT": dict(local="eGoli (Zulu: 'place of gold')", demonym="Gautenger", dialect="Many: isiZulu, English, Afrikaans, Sesotho, Setswana",
               festival="The Joburg Art Fair and Soweto Derby days", club="Kaizer Chiefs, Orlando Pirates and Mamelodi Sundowns", river="Vaal River",
               wonder="The Cradle of Humankind fossil caves", historic="The South African Republic (Transvaal)", landmark="The Union Buildings and Vilakazi Street in Soweto",
               unesco="The Fossil Hominid Sites of South Africa (Cradle of Humankind)", person="Elon Musk (born in Pretoria)",
               known="Gold, finance and the country's economic heart; the smallest but most populous province", company="Standard Bank and MTN",
               langs="isiZulu, English, Afrikaans, Sesotho (no single majority)", wildlife="Dinokeng Game Reserve (Big Five near Pretoria)",
               before="Transvaal (the PWV region), with parts of KwaNdebele and Bophuthatswana"),
    "NL": dict(local="iKwaZulu-Natali (Zulu)", demonym="KwaZulu-Natalian", dialect="isiZulu", dish="Bunny chow (Durban curry in bread)",
               festival="The Umhlanga Reed Dance and the Comrades Marathon", club="AmaZulu and Golden Arrows", river="Tugela (uThukela)",
               high="Mafadi, 3,450 m: South Africa's highest (on the Lesotho border)", wonder="The Drakensberg and the iSimangaliso Wetland Park",
               historic="The Zulu Kingdom and the Colony of Natal", landmark="Durban's Golden Mile and the Isandlwana battlefield",
               unesco="iSimangaliso Wetland Park and Maloti-Drakensberg Park", person="Shaka, king of the Zulus",
               known="Durban's port, sugar cane and beaches", city="Durban", langs="isiZulu (about four in five), English",
               wildlife="Hluhluwe–iMfolozi (saved the white rhino)", before="Natal, with the KwaZulu homeland"),
    "LP": dict(local="Limpopo", demonym="Limpopian", dialect="Sepedi, Xitsonga, Tshivenda", dish="Mopane worms", festival="The Mapungubwe Arts Festival",
               club="Polokwane City", river="Limpopo River", wonder="Northern Kruger National Park and its baobabs", historic="The Kingdom of Mapungubwe (about 1075–1220)",
               landmark="Mapungubwe Hill", unesco="The Mapungubwe Cultural Landscape and the Makapan Valley fossil site",
               known="Farming (tomatoes, mangoes) and platinum mining", langs="Sepedi, Xitsonga, Tshivenda",
               wildlife="Kruger National Park (north) and Mapungubwe", before="Northern Transvaal, with the Lebowa, Gazankulu and Venda homelands"),
    "MP": dict(local="iMpumalanga (Swazi: 'where the sun rises')", demonym="Mpumalangan", dialect="siSwati, isiZulu, Xitsonga, isiNdebele",
               festival="Innibos arts festival", club="TS Galaxy", river="Komati and Crocodile rivers", wonder="Blyde River Canyon and God's Window",
               historic="Eastern Transvaal (the old gold-rush towns of Pilgrim's Rest and Barberton)", landmark="Bourke's Luck Potholes",
               unesco="The Barberton Makhonjwa Mountains (some of the oldest rocks on Earth)", known="The gateway to Kruger, forests and coal power stations",
               company="Sasol's Secunda plant", langs="siSwati, isiZulu, Xitsonga, isiNdebele", wildlife="Kruger National Park (south): the Big Five",
               before="Eastern Transvaal, with the KaNgwane and KwaNdebele homelands"),
    "NW": dict(local="Bokone Bophirima (Tswana)", demonym="North Wester", dialect="Setswana", river="Vaal and Molopo rivers", wonder="Pilanesberg, an old volcano crater",
               historic="Western Transvaal and the Tswana chiefdoms", landmark="Sun City and the Lost City", unesco="The Taung skull fossil site and the Vredefort Dome (shared)",
               person="Sol Plaatje (writer, lived in Mahikeng)", known="Platinum mining (Rustenburg) and Sun City", city="Rustenburg", langs="Setswana (about two in three)",
               wildlife="Pilanesberg and Madikwe: Big Five reserves", before="Western Transvaal and part of the Cape, with most of Bophuthatswana"),
    "NC": dict(local="Noord-Kaap (Afrikaans)", demonym="Northern Caper", dialect="Afrikaans, Setswana, Nama", festival="Namaqualand's spring flowers",
               river="Orange River", wonder="Augrabies Falls and the Namaqualand flowers", historic="Griqualand West and the diamond fields", landmark="The Big Hole in Kimberley",
               unesco="The Richtersveld and the ǂKhomani Cultural Landscape", known="Diamonds, the biggest and emptiest province, and the SKA radio telescope",
               company="De Beers (founded in Kimberley)", langs="Afrikaans, Setswana", wildlife="Kgalagadi Transfrontier Park (black-maned lions)",
               before="Cape Province, with part of Bophuthatswana"),
    "WC": dict(local="Wes-Kaap (Afrikaans)", demonym="Western Caper", dialect="Afrikaans (Kaaps), isiXhosa, English", dish="Bobotie and Cape Malay curry",
               drink="Wine (Stellenbosch, Franschhoek)", festival="The Cape Town Minstrel Carnival (Kaapse Klopse)", club="Cape Town City and Stellenbosch FC",
               river="Breede River", wonder="Table Mountain and the Cape of Good Hope", historic="The Dutch Cape Colony (from 1652)", landmark="Robben Island",
               unesco="Robben Island and the Cape Floral Region", person="Desmond Tutu (Archbishop of Cape Town)", known="Tourism, wine and the Cape winelands",
               company="Naspers", langs="Afrikaans, isiXhosa, English", wildlife="Penguins at Boulders Beach and whales off Hermanus", before="Cape Province"),
}
