# Job: overnight v8, five African and Middle Eastern country maps

Morocco, Kenya, Ethiopia, Saudi Arabia and Iran: first the downloads, then the builds. Decided with the user on 2026-11-27. **Nothing here is started yet.**

**Don't start this job until the user says so**, and don't change the other job files to make room for it. Don't commit or push until the user says so.

It works like [overnight_v4.md](overnight_v4.md): the shared builder (`tools/build_country.py`, `tools/<code>_facts.py`), one `NEW_MAPS` row and a projection style each (add the style first), the same tests. Where this file and the earlier ones differ, this file wins.

## The countries (decided 2026-11-27)

| Country | Code | Parts | Games 5 and 6 | Small parts |
| --- | --- | --- | --- | --- |
| Morocco | `ma` | 12 regions (Western Sahara as disputed grey: see below) | none (regions have no official flags): check | – |
| Kenya | `ke` | 47 counties (since 2013) | none expected (county seals: check licences) | circles for the smallest (Mombasa, Nairobi?) |
| Ethiopia | `et` | 12 regions and 2 chartered cities (Addis Ababa, Dire Dawa): 14 | flags (regional flags are official) | circles for Addis Ababa and Dire Dawa, Harari if needed |
| Saudi Arabia | `sa` | 13 regions (manatiq) | none (no regional flags) | – |
| Iran | `ir` | 31 provinces (ostanha) | none (no provincial flags) | – |

- **Morocco and Western Sahara (decided 2026-11-27):** Western Sahara is **not** part of Morocco's parts. It's **disputed grey, untappable as a part**, split into its two controlled areas: **the Moroccan-controlled area** (west of the berm, Natural Earth's disputed area "Morocco / W. Sahara", admin MAR) and **the Sahrawi Arab Democratic Republic-controlled area** (east of the berm, the "Free Zone", Natural Earth's "W. Sahara", admin SAH). Each has its own shade of grey (a light and a darker grey, or a pattern), the berm drawn as a dotted line, and each opens its own dispute card (who controls it, who claims it, since when: extend `tools/disputes_facts.py` with the two areas and adjust the world-map entry if needed). Morocco's regions that lie in Western Sahara (Laâyoune-Sakia El Hamra and Dakhla-Oued Ed-Dahab, and any other region that crosses the internationally recognised border: check Guelmim-Oued Noun) are **left out as parts**, or cut at that border: the parts are Morocco's regions north of it. Record the exact count and any region that was cut under "Decisions to check". Tamazight (Tifinagh script) and Arabic names on the cards: download Noto Sans Tifinagh and subset it; the Arabic subset exists.
- **Kenya:** 47 counties since 2013. **Natural Earth has the old 8 provinces:** use geoBoundaries ADM1 (CC BY 4.0, credited). The Ilemi Triangle follows the disputes layer.
- **Ethiopia:** 12 regions since the 2020–2023 splits (Sidama, South West Ethiopia Peoples', Central Ethiopia, South Ethiopia). **Natural Earth may have the old 9 or 10:** use geoBoundaries if it's up to date, or split with zone boundaries; record which. Amharic (Ge'ez script) on the cards: download Noto Sans Ethiopic and subset it.
- **Saudi Arabia:** 13 regions. Arabic names (the Arabic subset exists).
- **Iran:** 31 provinces. Persian names (the Arabic subset covers Persian letters; extend it with پ چ ژ گ ی if needed). Abu Musa and the Tunbs follow the disputes layer.

Every country: Find and Name for the parts and capitals (games 5 and 6 where the table says), the Learning card, Focus on, a stats tab, the high-resolution coast. No timelines or layers.

## Part 1: downloads

1. Add the five to `tools/fetch_country_data.py` (local Wikipedia languages: ar (and fr for Morocco), sw (and en) for Kenya, am, ar, fa) and `COUNTRY_QID`.
2. `--extras` and `--census`, with searches for the facts below (for example "Berbers", "Medina of Fez", "Moroccan cuisine", "Ethnic groups in Kenya", "National parks of Kenya", "Provinces of Kenya", "Ethnic groups in Ethiopia", "Kingdom of Aksum", "Coffee production in Ethiopia", "Holy sites in Islam", "Saudi Arabian cuisine", "Ethnic groups in Iran", "Persepolis", "Persian carpet").
3. **Fonts:** Noto Sans Tifinagh, Noto Sans Ethiopic; check the Arabic subset covers Persian.
4. **Shapes:** Natural Earth admin-1 where current; geoBoundaries ADM1 for Kenya (47) and, if needed, Ethiopia (12 + 2). Check every count.
5. **Populations: the latest official figure by default:** HCP Morocco (the 2024 census), KNBS Kenya (the 2019 census or a later official estimate), the Ethiopian Statistics Service (latest projection; there has been no census since 2007: say so), GASTAT Saudi Arabia (the 2022 census), the Statistical Centre of Iran (latest); each checked against the national total (Morocco's total without the Western Sahara regions: say so).
6. Download log at the end of this file.

## Part 2: builds

Order: **Saudi Arabia, Iran, Ethiopia, Kenya, Morocco** (Morocco last because of Western Sahara).

1. Plans first: `Morocco_plan.md`, `Kenya_plan.md`, `Ethiopia_plan.md`, `Saudi_Arabia_plan.md`, `Iran_plan.md`, with no open questions.
2. Build, wire, test (all must pass), preview, PLAN.md, results and decisions to check at the end of this file.
3. **Tests also check:** Western Sahara's two areas are grey in two shades, untappable as parts, the berm dotted, and each opens its own dispute card; Tifinagh, Ge'ez, Arabic and Persian names show in light and dark themes (right to left where needed); Kenya's 47 counties all tap.

## Learning card facts (approved by the user 2026-11-27)

Every card also has the name, kind, capital, population (latest figure), area and rank, and the flag where there is one. Leave out any fact that isn't found rather than guess.

**All five (17):** name in the local language; demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: the biggest club; main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage; famous person from there; known for; famous company; largest city if it isn't the capital.

**Plus three for each country:**

- **Morocco:** Amazigh (Berber) area; medina or kasbah; famous dish (tagine, couscous).
- **Kenya:** main ethnic group; wildlife park; former province.
- **Ethiopia:** main ethnic group and language; ancient kingdom or church; coffee origin.
- **Saudi Arabia:** holy site or old town; desert or mountains; famous dish (kabsa).
- **Iran:** main ethnic group; ancient site (Persepolis...); famous carpet or craft.
