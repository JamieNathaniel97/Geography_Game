# Job: overnight v7, five Asian country maps

Vietnam, Thailand, the Philippines, Indonesia and Pakistan: first the downloads, then the builds. Decided with the user on 2026-11-27. **Nothing here is started yet.**

**Don't start this job until the user says so**, and don't change the other job files to make room for it. Don't commit or push until the user says so.

It works like [overnight_v4.md](overnight_v4.md): the shared builder (`tools/build_country.py`, `tools/<code>_facts.py`), one `NEW_MAPS` row and a projection style each (add the style first), the same tests. Where this file and the earlier ones differ, this file wins.

## The countries (decided 2026-11-27)

| Country | Code | Parts | Games 5 and 6 | Small parts |
| --- | --- | --- | --- | --- |
| Vietnam | `vn` | **34 provinces and cities (the 2025 reform)** | none (no provincial flags) | circles for the smallest if needed |
| Thailand | `th` | 76 provinces and Bangkok: 77; the 6 regions as a filter | provincial seals: check Commons licences (as Nigeria's); otherwise none | circles for the smallest (Samut Songkhram?) |
| Philippines | `ph` | **18 regions** | none (regions have no official flags) | island ovals where needed |
| Indonesia | `id` | **38 provinces** (the 2022–2023 Papua splits) | none expected (provincial emblems: check licences) | island ovals where needed; a circle for Jakarta |
| Pakistan | `pk` | 4 provinces, Islamabad Capital Territory, Gilgit-Baltistan and Azad Kashmir: 7 | none expected (check) | a circle for Islamabad |

- **Vietnam:** on 1 July 2025 its 63 provinces were merged into 34 (28 provinces, 6 cities). **Natural Earth has the old 63:** dissolve them with the official merger table (`MERGE` in the shared builder, as for South Korea's Gwangju and South Jeolla). Record the table's source. The Paracel and Spratly Islands follow the disputes layer (not parts).
- **Thailand:** 77 parts, with the 6 regions (North, Northeast, Central, East, West, South) as a filter like Japan's. Thai script on the cards: **download Noto Sans Thai** and subset it (`tools/build_fonts.py`).
- **Philippines: build the 18 regions** (including BARMM and the Negros Island Region, re-created in 2024). **Also download the 82 provinces** (shapes, names, capitals, populations) into `tools/downloads/ph/provinces/`, for a possible second set later. Don't build them now. Sabah (claimed by the Philippines) and Scarborough Shoal follow the disputes layer.
- **Indonesia:** 38 provinces since the Papua splits (South Papua, Central Papua, Highland Papua 2022; Southwest Papua 2022–23). **Natural Earth is out of date (34):** use geoBoundaries ADM1 (CC BY 4.0, credited) if it has 38, or split Natural Earth's Papua and West Papua with the regencies of the new provinces. Very wide: check it fits a tall phone screen at a usable size (an inset or two may be needed, as for Malaysia's East Malaysia).
- **Pakistan:** Gilgit-Baltistan and Azad Kashmir are governed by Pakistan and claimed by India: **parts** (the governing side's map, as Dokdo on South Korea's), with the dispute added to their cards by the disputes layer. The Line of Control and the other disputed borders dotted. Urdu (and regional scripts) on the cards: the Arabic font subset already covers Urdu letters; extend it with Urdu-specific characters if needed.

Every country: Find and Name for the parts and capitals (games 5 and 6 where the table says), the Learning card, Focus on, a stats tab, the high-resolution coast. No timelines or layers.

## Part 1: downloads

1. Add the five to `tools/fetch_country_data.py` (local Wikipedia languages: vi, th, tl (and en), id, ur) and `COUNTRY_QID`.
2. `--extras` and `--census`, with searches for the facts below (for example "Vietnamese cuisine", "Provinces of Vietnam" (the 2025 reform and its merger table), "Regions of Thailand", "Loy Krathong", "Island groups of the Philippines", "Languages of the Philippines", "Ethnic groups in Indonesia", "Batik", "Languages of Pakistan", "Indus Valley Civilisation", "Gandhara").
3. **Fonts:** Noto Sans Thai (Thai script); check the Arabic subset covers Urdu (ٹ ڈ ڑ ں ھ ہ ی ے).
4. **Shapes:** Natural Earth admin-1; check every count (34 after dissolving, 77, 18, 38, 7). Use geoBoundaries for Indonesia (and for any other out-of-date list), credited.
5. **Populations: the latest official figure by default:** the General Statistics Office of Vietnam (summed into the 34 new units), Thailand's registration figures, the Philippine Statistics Authority (latest census or estimate), BPS Indonesia (latest estimate by province), the Pakistan Bureau of Statistics (the 2023 census; Gilgit-Baltistan and Azad Kashmir from their own figures); each checked against the national total.
6. **The Philippines' 82 provinces:** data for later (see above).
7. Download log at the end of this file.

## Part 2: builds

Order: **Pakistan, Thailand, Vietnam, Philippines, Indonesia** (Indonesia last: new provinces, size, islands).

1. Plans first: `Vietnam_plan.md`, `Thailand_plan.md`, `Philippines_plan.md`, `Indonesia_plan.md`, `Pakistan_plan.md`, with no open questions.
2. Build, wire, test (all must pass), preview, PLAN.md, results and decisions to check at the end of this file.
3. **Tests also check:** Vietnam's merged provinces each open one card; Thai script and Urdu show in light and dark themes; Gilgit-Baltistan and Azad Kashmir open their cards with the dispute added; Indonesia's islands and any insets tap right.

## Learning card facts (approved by the user 2026-11-27)

Every card also has the name, kind, capital, population (latest figure), area and rank, and the flag where there is one. Leave out any fact that isn't found rather than guess.

**All five (17):** name in the local language; demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: the biggest club; main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage; famous person from there; known for; famous company; largest city if it isn't the capital.

**Plus three for each country:**

- **Vietnam:** North, Centre or South; famous dish (phở, bánh mì...); war or dynasty history site.
- **Thailand:** region; famous temple; festival (Loy Krathong, Songkran).
- **Philippines:** island group (Luzon, Visayas, Mindanao); main language; volcano or beach.
- **Indonesia:** island; main ethnic group; traditional dance or batik.
- **Pakistan:** main language; river or mountain range; ancient site (Indus Valley, Gandhara).
