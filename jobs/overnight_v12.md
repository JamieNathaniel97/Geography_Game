# Job: overnight v12, five African country maps

Algeria, Tunisia, Ghana, Tanzania and the Democratic Republic of the Congo: first the downloads, then the builds. Decided with the user on 2026-11-28. **The downloads are done (2026-11-28, see the log at the end); the builds aren't started.**

**Don't start this job until the user says so**, and don't change the other job files to make room for it. Don't commit or push until the user says so.

It works like [overnight_v4.md](overnight_v4.md): the shared builder (`tools/build_country.py`, `tools/<code>_facts.py`), one `NEW_MAPS` row and a projection style each (add the style first), the same tests. Where this file and the earlier ones differ, this file wins.

## The countries (decided 2026-11-28)

| Country | Code | Parts | Games 5 and 6 | Small parts |
| --- | --- | --- | --- | --- |
| Algeria | `dz` | **69 provinces (wilayas) since the 2025 law** (58 since 2019): see the download log | none (no provincial flags) | circles for the smallest coastal ones (Algiers, Boumerdès?) |
| Tunisia | `tn` | 24 governorates | none (no governorate flags) | circles for the Tunis governorates if needed (Tunis, Ariana, Ben Arous, Manouba) |
| Ghana | `gh` | 16 regions (since 2018) | none expected: check | – |
| Tanzania | `tz` | 31 regions (26 on the mainland, 5 on Zanzibar) | none expected: check | island ovals for Zanzibar's 5 regions |
| DR Congo | `cd` | 26 provinces (since 2015), Kinshasa included | none expected: check | a circle for Kinshasa if needed |

- **Algeria:** 48 wilayas became 58 in 2019 (10 in the south), and a 2025 law may have added more: **check the current count** (Wikidata and the official journal) and build the current one; record it. **Natural Earth may have the old 48:** use geoBoundaries ADM1 if it's current, or split with the district (daïra) boundaries; record which. Arabic names (the Arabic subset exists) and Tamazight in Tifinagh (the font from [overnight_v8.md](overnight_v8.md); download it here if v8 hasn't run). Very large and mostly desert: check the north's small coastal wilayas are tappable at a usable zoom (circles where not).
- **Tunisia:** 24 governorates; Arabic and French names both accepted. Tunis and its three neighbours are small: circles if needed.
- **Ghana:** the 2018 referendum split 10 regions into 16. **Natural Earth may have the old 10:** use geoBoundaries ADM1 (credited) if it has 16; record which.
- **Tanzania:** 31 regions (Songwe 2016). Zanzibar's 5 regions (3 on Unguja, 2 on Pemba) as island ovals. Check Natural Earth has 31. Swahili names. **Lake Malawi's border** (Tanzania claims the half of the lake; Malawi claims all of it) follows the disputes layer: check it's there, add it with a source if not.
- **DR Congo:** 26 provinces since the 2015 split of the old 11. **Natural Earth may have the old 11:** use geoBoundaries ADM1 if it has 26; record which. French names, with Lingala, Swahili, Kikongo or Tshiluba on the card where found.

Every country: Find and Name for the parts and capitals (games 5 and 6 where the table says), the Learning card, Focus on, a stats tab, the high-resolution coast. No timelines or layers.

## Part 1: downloads

1. Add the five to `tools/fetch_country_data.py` (local Wikipedia languages: ar (and fr, kab) for Algeria, ar (and fr) for Tunisia, en (and tw where there are articles) for Ghana, sw for Tanzania, fr (and ln) for DR Congo) and `COUNTRY_QID`.
2. `--extras` and `--census`, with searches for the facts below (for example "Kabylia", "Roman ruins in Algeria", "Tassili n'Ajjer", "Carthage", "Tunisian cuisine", "Ashanti Empire", "Cocoa production in Ghana", "Ethnic groups in Ghana", "Mount Kilimanjaro", "Serengeti National Park", "Zanzibar spice trade", "Languages of the Democratic Republic of the Congo", "Mining in the Democratic Republic of the Congo", "Congo River").
3. **Fonts:** the Arabic subset (check it); Noto Sans Tifinagh (from v8, or download it here); Latin covers the rest.
4. **Shapes:** Natural Earth admin-1 where current; geoBoundaries ADM1 where it isn't (Algeria, Ghana and DR Congo probably). Check every count (58 or the current one, 24, 16, 31, 26).
5. **Populations: the latest official figure by default:** ONS Algeria (the 2008 census is the last: the latest official estimate, and say so), INS Tunisia (the 2024 census), the Ghana Statistical Service (the 2021 census), NBS Tanzania (the 2022 census), INS DR Congo (no census since 1984: the latest official estimate, and say so); each checked against the national total.
6. Download log at the end of this file.

## Part 2: builds

Order: **Tunisia, Ghana, Tanzania, DR Congo, Algeria** (Algeria last: the wilaya count to settle and its size).

1. Plans first: `Algeria_plan.md`, `Tunisia_plan.md`, `Ghana_plan.md`, `Tanzania_plan.md`, `DR_Congo_plan.md`, with no open questions.
2. Build, wire, test (all must pass), preview, PLAN.md, results and decisions to check at the end of this file.
3. **Tests also check:** Zanzibar's island ovals tap right; Tunis's small governorates and Algeria's small coastal wilayas tap right; Arabic and Tifinagh names show in light and dark themes (right to left where needed); the Lake Malawi dispute card opens.

## Learning card facts (the 17 approved by the user 2026-11-27; the three per country approved 2026-11-28)

Every card also has the name, kind, capital, population (latest figure), area and rank, and the flag where there is one. Leave out any fact that isn't found rather than guess.

**All five (17):** name in the local language; demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: the biggest club; main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage; famous person from there; known for; famous company; largest city if it isn't the capital.

**Plus three for each country:**

- **Algeria:** region (the Tell, the High Plateaus, the Sahara, Kabylie); Amazigh (Berber) area; Roman or ancient ruins.
- **Tunisia:** coast, interior or Sahara; Carthage, Roman or Islamic site; olive oil or dates.
- **Ghana:** main ethnic group; traditional kingdom (Ashanti...); cocoa or gold.
- **Tanzania:** safari park or mountain; main ethnic group; Swahili coast or spice island.
- **DR Congo:** main language (Lingala, Swahili, Kikongo, Tshiluba); mineral (cobalt, copper, diamonds...); river or rainforest.

## Download log (2026-11-28)

Downloaded ahead of the run (the user asked for the data first). `python tools/fetch_country_data.py --extras --no-images <codes>`, then `--census`, `python tools/fetch_boundaries.py` (geoBoundaries, into `tools/downloads/<code>/geoboundaries/`, with each file's licence in its .json), then the flags and coats of arms at Commons' pace (no failures; Slovenia's 212 municipal arms skipped: not needed).

| Country | Wikidata divisions (current) | Natural Earth admin-1 | English articles | Local articles | List articles | Flags | Coats of arms | Coast | Census items | geoBoundaries |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Algeria | 58 (out of date: 69 since 2025, see below) | 48 (want 69) | 58 + the 11 new | 58 (ar), 58 (fr) + the 11 new | 5 | 0 | 0 | 0.9 MB | 55 | DZA_ADM1 (48, old), DZA_ADM2 (48) |
| Tunisia | 24 | 23 (want 24) | 24 | 24 (ar), 24 (fr) | 5 | 1 | 1 | 0.3 MB | 25 | – |
| Ghana | 17 (16 + the old Brong-Ahafo) | 10 (want 16) | 17 | – | 6 | 5 | 0 | 0.2 MB | 5 | GHA_ADM1 (16), GHA_ADM2 (260) |
| Tanzania | 31 | 30 (want 31: no Songwe) | 31 | 31 (sw) | 6 | 0 | 0 | 0.9 MB | 32 | TZA_ADM1 (31) |
| DR Congo | 26 (Kasaï added by hand: its ISO code is on the old Kasaï District in Wikidata) | 11 (want 26) | 26 | 26 (fr) | 5 | 1 | 1 | 0.7 MB | 27 | COD_ADM1 (26) |

**Algeria has 69 wilayas (found 2026-11-28):** the Council of Ministers approved 11 new wilayas on 16 November 2025 and the Council of the Nation passed the law on 24 December 2025 (Aflou, Barika, El Kantara, Bir El Ater, El Aricha, Ksar Chellala, Aïn Oussera, Messaad, Ksar El Boukhari, Bou Saâda, El Abiodh Sidi Cheikh). Sources: [Radio Algérie](https://news.radioalgerie.dz/fr/node/81255), [Algérie360](https://www.algerie360.com/organisation-territoriale-lalgerie-passe-officiellement-a-69-wilayas/), [Algérie Eco, June 2026, the decree's numbers](https://algerie-eco.com/2026/06/05/algerie-les-noms-et-les-numeros-des-nouvelles-wilayas-fixes/). Reports differ on the numbers 59–69: use the decree's (OpenStreetMap's codes match it). **Build 69** (this replaces "58" in the table above).

**Shapes to use** (checked 2026-11-28):

- **Algeria:** **OpenStreetMap** (`python tools/fetch_osm_admin.py dz dz6`): `tools/downloads/dz/osm/admin4.geojson` has 68 wilayas (DZ-01..62, 64..69); **El Aricha (DZ-63) isn't mapped as a wilaya yet**: cut it from Tlemcen with its daïra (`osm/admin6.geojson`, "Daïra d'El Aricha"; check the law's list of its communes, and whether it takes more than that one daïra). ODbL: "© OpenStreetMap contributors" on the map. The 11 new wilayas' articles (en, ar, fr) are in wiki/; their Wikidata IDs in `tools/downloads/dz/new_wilayas_2025.json`. Their populations: from their communes (2008 census or the latest estimate), and say so.
- **Tunisia:** Natural Earth has 23: find the missing governorate (probably Tunis merged with a neighbour) and split it with geoBoundaries or OpenStreetMap, credited.
- **Ghana:** geoBoundaries GHA ADM1 (16) is OpenStreetMap-derived under **CC BY-SA 2.0**: prefer dissolving GHA ADM2 (260 districts, USAID/Ghana Statistical Service 2019, CC BY 4.0) into the 16 regions. Census: Wikidata has only 5 items: use "Regions of Ghana" (the 2021 census) for populations.
- **Tanzania:** geoBoundaries TZA ADM1 (31, NBS 2019, CC BY 4.0), credited.
- **DR Congo:** geoBoundaries COD ADM1 (26; OpenStreetMap, ODbL): the only up-to-date source; credit it as above.
- **Fonts:** Tifinagh in `tools/downloads/fonts/NotoSansTifinagh.ttf`; the Arabic subset exists.
