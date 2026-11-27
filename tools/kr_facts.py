"""South Korea's 16 first-level divisions (South_Korea_plan.md): the config for tools/build_country.py and the Learning
card facts. Card fact fields: see tools/at_facts.py ("local" is the name in Hangul with its romanisation, in the cards'
Korean font); South Korea's own two: food (a famous food) and kingdom (historic kingdom). Games 5 and 6: flags.
**Gwangju and South Jeolla merged on 1 July 2026** into the Jeonnam-Gwangju Integrated Special City (전남광주통합특별시):
Natural Earth still has them apart, so the build dissolves them (MERGE) into one part, id KR-JG (it has no ISO code yet);
its flag isn't on Commons yet, so it sits out the flag games. Dokdo (the Liancourt Rocks, governed by South Korea and
claimed by Japan) is joined to North Gyeongsang, with a dotted ring (DISPUTED).
Written from general knowledge and the downloaded Wikipedia articles (tools/downloads/kr/wiki/en, ko); checked by hand.
Populations: Ministry of the Interior and Safety, resident registration at the end of October 2026 (jumin.mois.go.kr,
saved in tools/downloads/kr/mois/); the 16 add up to 51,075,282. Areas: Korean Wikipedia ("대한민국의 행정 구역").
"""

A3, A2, CONT = "KOR", "KR", "Asia"
WINDOW = (121.0, 30.5, 134.0, 40.5)
DETAIL = (124.5, 33.0, 132.0, 38.7)
MERGE = {"JG": ["29", "46"]}
DISPUTED = [dict(ne="Dokdo", join="47")]  # (its dotted ring and info card come from the world disputes layer, data/disputes.json)
POP_SOURCE, POP_YEAR, TOTAL = "Ministry of the Interior and Safety, resident registration, October 2026", "2026", 51075282
CAP_LL = {"Sejong": [127.289, 36.480], "Hongseong": [126.661, 36.601], "Jeju City": [126.531, 33.499]}

C, P = "Metropolitan city", "Province"
PARTS = {
    "11": dict(name="Seoul", names=["Seoul Special City", "Seoul-teukbyeolsi"], capital="Seoul", pop=9274392, area=605, kind="Special city"),
    "26": dict(name="Busan", names=["Pusan", "Busan Metropolitan City"], capital="Busan", capAlt=["Pusan"], pop=3226446, area=770, kind=C),
    "27": dict(name="Daegu", names=["Taegu", "Daegu Metropolitan City"], capital="Daegu", capAlt=["Taegu"], pop=2345185, area=1500, kind=C),
    "28": dict(name="Incheon", names=["Inchon", "Incheon Metropolitan City"], capital="Incheon", capAlt=["Inchon"], pop=3070203, area=1063, kind=C),
    "30": dict(name="Daejeon", names=["Taejon", "Daejeon Metropolitan City"], capital="Daejeon", capAlt=["Taejon"], pop=1443171, area=539, kind=C),
    "31": dict(name="Ulsan", names=["Ulsan Metropolitan City"], capital="Ulsan", pop=1085888, area=1061, kind=C),
    "50": dict(name="Sejong", names=["Sejong City", "Sejong Special Self-Governing City"], capital="Sejong", pop=390618, area=465,
               kind="Special self-governing city"),
    "41": dict(name="Gyeonggi", names=["Gyeonggi-do", "Gyeonggi Province", "Kyonggi"], capital="Suwon", pop=13780735, area=10183, kind=P),
    "42": dict(name="Gangwon", names=["Gangwon State", "Gangwon Province", "Gangwon-do", "Kangwon"], capital="Chuncheon", pop=1506690, area=16875,
               kind="Special self-governing province"),
    "43": dict(name="North Chungcheong", names=["Chungcheongbuk-do", "Chungbuk", "North Chungcheong Province"], capital="Cheongju", pop=1602382, area=7407,
               kind=P, notTypo=["South Chungcheong"]),
    "44": dict(name="South Chungcheong", names=["Chungcheongnam-do", "Chungnam", "South Chungcheong Province"], capital="Hongseong", pop=2140278, area=8226,
               kind=P, notTypo=["North Chungcheong"]),
    "45": dict(name="Jeonbuk", names=["Jeonbuk State", "North Jeolla", "North Jeolla Province", "Jeollabuk-do"], capital="Jeonju", pop=1715109, area=8069,
               kind="Special self-governing province"),
    "47": dict(name="North Gyeongsang", names=["Gyeongsangbuk-do", "Gyeongbuk", "North Gyeongsang Province"], capital="Andong", pop=2489894, area=18424,
               kind=P, notTypo=["South Gyeongsang"]),
    "48": dict(name="South Gyeongsang", names=["Gyeongsangnam-do", "Gyeongnam", "South Gyeongsang Province"], capital="Changwon", pop=3189204, area=10540,
               kind=P, notTypo=["North Gyeongsang"]),
    "49": dict(name="Jeju", names=["Jeju-do", "Jeju Province", "Jeju Island", "Cheju"], capital="Jeju City", capAlt=["Jeju", "Jeju-si"], pop=662117, area=1849,
               kind="Special self-governing province"),
    "JG": dict(name="Jeonnam-Gwangju", names=["Jeonnam-Gwangju Integrated Special City", "Gwangju-Jeonnam", "Gwangju", "South Jeolla", "Jeollanam-do", "Jeonnam"],
               capital="Gwangju", capAlt=["Muan", "Suncheon"], capNote="Gwangju (main office), with offices in Muan and Suncheon", pop=3152970, area=12820,
               kind="Integrated special city (since July 2026)", flagIso="none"),
}

FACTS = {
    "11": dict(local="서울특별시 (Seoul Teukbyeolsi)", dialect="The Seoul dialect (standard Korean)", festival="The Lotus Lantern Festival (Yeondeunghoe)",
               club="FC Seoul", river="Han River", high="Bukhansan, 836 m", wonder="Bukhansan National Park", historic="The capital of Joseon (1394–1910)",
               landmark="Gyeongbokgung Palace and N Seoul Tower", unesco="Changdeokgung, Jongmyo Shrine and the Joseon royal tombs",
               person="King Sejong the Great, who created Hangul", known="The capital: government, K-pop and technology", company="Samsung and LG",
               food="Seolleongtang (ox-bone soup) and tteokbokki", kingdom="Baekje's first capital, then Joseon's"),
    "26": dict(local="부산광역시 (Busan Gwangyeoksi)", dialect="Gyeongsang dialect", festival="The Busan International Film Festival", club="Busan IPark",
               river="Nakdong River (its mouth)", wonder="Haeundae Beach", historic="The last refuge of the South in the Korean War (1950)",
               landmark="Gamcheon Culture Village", known="South Korea's biggest port", food="Dwaeji gukbap (pork soup) and milmyeon", kingdom="Gaya and Silla"),
    "27": dict(local="대구광역시 (Daegu Gwangyeoksi)", dialect="Gyeongsang dialect", festival="The Chimac (chicken and beer) Festival", club="Daegu FC",
               wonder="Palgongsan", landmark="Donghwasa Temple and Seomun Market", known="Textiles, apples and the hottest summers", company="Samsung (founded here in 1938)",
               food="Makchang (grilled intestines)", kingdom="Silla"),
    "28": dict(local="인천광역시 (Incheon Gwangyeoksi)", club="Incheon United", historic="The Incheon landing (1950)", landmark="Incheon Airport and Songdo",
               known="The main airport and port", food="Jajangmyeon (first made in Incheon's Chinatown)", kingdom="Baekje (Michuhol)"),
    "30": dict(local="대전광역시 (Daejeon Gwangyeoksi)", dialect="Chungcheong dialect", club="Daejeon Hana Citizen", landmark="Expo Science Park",
               known="The science city: research institutes (Daedeok) and Expo '93", food="Kalguksu and the Sungsimdang bakery", kingdom="Baekje"),
    "31": dict(local="울산광역시 (Ulsan Gwangyeoksi)", dialect="Gyeongsang dialect", club="Ulsan HD", river="Taehwa River",
               wonder="Ganjeolgot, where the mainland sees the first sunrise", unesco="The petroglyphs along the Bangucheon stream",
               known="Shipbuilding and Hyundai's car plant", company="Hyundai Heavy Industries and Hyundai Motor", food="Eonyang bulgogi", kingdom="Silla"),
    "50": dict(local="세종특별자치시 (Sejong Teukbyeoljachisi)", river="Geum River", historic="Built from 2007 as the new administrative capital",
               landmark="The Government Complex Sejong and its rooftop garden", known="Government ministries (since 2012), named after King Sejong", kingdom="Baekje"),
    "41": dict(local="경기도 (Gyeonggi-do)", club="Suwon Samsung Bluewings", river="Han and Imjin rivers", historic="The ring around the capital (Joseon's heartland)",
               landmark="Hwaseong Fortress and Panmunjom on the DMZ", unesco="Hwaseong Fortress and Namhansanseong", known="The most populous province, round Seoul",
               company="Samsung Electronics (Suwon)", food="Suwon galbi (grilled ribs)", kingdom="Baekje, then Goguryeo and Silla in turn"),
    "42": dict(local="강원특별자치도 (Gangwon Teukbyeoljachido)", dialect="Gangwon dialect", festival="The Hwacheon Sancheoneo Ice Festival", club="Gangwon FC",
               high="Daecheongbong (Seoraksan), 1,708 m", wonder="Seoraksan National Park", landmark="Pyeongchang, host of the 2018 Winter Olympics",
               known="Mountains, skiing and the DMZ", food="Chuncheon dakgalbi and makguksu", kingdom="Goguryeo and Silla"),
    "43": dict(local="충청북도 (Chungcheongbuk-do)", dialect="Chungcheong dialect", wonder="Songnisan National Park", landmark="Beopjusa Temple",
               unesco="Beopjusa (Buddhist mountain monasteries)", known="South Korea's only landlocked province", company="SK hynix (Cheongju)",
               food="Cheongju's jikji-themed dishes and Chungju apples", kingdom="Baekje, Silla and Goguryeo met here"),
    "44": dict(local="충청남도 (Chungcheongnam-do)", dialect="Chungcheong dialect", festival="The Boryeong Mud Festival", historic="Baekje's later capitals Gongju and Buyeo",
               landmark="Gongsanseong Fortress", unesco="The Baekje Historic Areas", known="The mud festival and Baekje history", city="Cheonan",
               food="Cheonan walnut cakes (hodu-gwaja)", kingdom="Baekje"),
    "45": dict(local="전북특별자치도 (Jeonbuk Teukbyeoljachido)", dialect="Jeolla dialect", festival="The Jeonju International Film Festival",
               club="Jeonbuk Hyundai Motors", historic="Jeonju was the capital of Later Baekje and the Joseon royal family's home", landmark="Jeonju Hanok Village",
               unesco="The Gochang dolmens", known="Korea's food capital", food="Jeonju bibimbap", kingdom="Baekje"),
    "47": dict(local="경상북도 (Gyeongsangbuk-do)", dialect="Gyeongsang dialect", drink="Andong soju", festival="The Andong Mask Dance Festival", club="Pohang Steelers",
               river="Nakdong River", wonder="Ulleungdo and Dokdo", historic="Gyeongju was Silla's capital for nearly 1,000 years", landmark="Bulguksa Temple",
               unesco="Gyeongju's historic areas, Seokguram and Bulguksa, and Hahoe village", known="Silla heritage and steel (Pohang)", company="POSCO",
               city="Pohang", food="Andong jjimdak (braised chicken)", kingdom="Silla"),
    "48": dict(local="경상남도 (Gyeongsangnam-do)", dialect="Gyeongsang dialect", festival="The Jinju Namgang Lantern Festival", club="Gyeongnam FC",
               high="Cheonwangbong (Jirisan), 1,915 m: the mainland's highest", wonder="Jirisan National Park", landmark="Haeinsa Temple",
               unesco="Haeinsa's Tripitaka Koreana woodblocks", known="Shipbuilding (Geoje) and machinery", food="Tongyeong oysters and chungmu gimbap", kingdom="Gaya"),
    "49": dict(local="제주특별자치도 (Jeju Teukbyeoljachido)", dialect="The Jeju language", festival="The Jeju Fire Festival", club="Jeju SK",
               high="Hallasan, 1,947 m: South Korea's highest", wonder="Seongsan Ilchulbong (Sunrise Peak)", landmark="The dol hareubang stone statues",
               unesco="Jeju Volcanic Island and Lava Tubes", known="Haenyeo women divers, tangerines and holidays", food="Black pork and Jeju tangerines",
               kingdom="Tamna (an island kingdom)"),
    "JG": dict(local="전남광주통합특별시 (Jeonnam Gwangju Tonghap Teukbyeolsi)", dialect="Jeolla dialect", club="Gwangju FC and Jeonnam Dragons",
               river="Yeongsan River", wonder="Suncheon Bay's reed wetlands and the islands of Sinan", historic="The Gwangju Uprising (1980); merged in July 2026",
               landmark="The May 18th National Cemetery and Suncheon Bay", unesco="The Hwasun dolmens and the Korean tidal flats (Getbol)",
               known="Islands, green tea (Boseong) and the 1980 democracy uprising", food="Tteokgalbi and Jeolla hanjeongsik (many-dish meals)",
               kingdom="Baekje (the Mahan lands before it)"),
}
