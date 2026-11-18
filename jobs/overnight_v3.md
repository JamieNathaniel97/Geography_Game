# Job: overnight v3, six more country maps

Switzerland, Portugal, Sweden, South Africa, New Zealand and Colombia: first the downloads, then the builds. Decided with the user on 2026-11-18. **Nothing here is started yet.** The next five countries are in [overnight_v4.md](overnight_v4.md).

**Don't start this job until the user says so** (decided 2026-11-18), and don't change the other job files to make room for it. Push only when the user says so.

It works exactly like [overnight_v2.md](overnight_v2.md): the builds follow **"The checklist for every build"** in [build_countries.md](build_countries.md), and the downloads use the same scripts and folders as [download_new_countries.md](download_new_countries.md). Read all three first. The rules of the last overnight run ([OVERNIGHT.md](OVERNIGHT.md)) apply if this is run overnight: judgement calls allowed and recorded, missing data doesn't block a build, tests are the bar, and nothing that worked before may break. Where this file and the checklist differ, this file wins.

## The countries (decided 2026-11-18)

| Country | Code | Parts | Games 5 and 6 | Small parts |
| --- | --- | --- | --- | --- |
| Switzerland | `ch` | 26 cantons | flags | circles for the smallest (Basel-Stadt, Appenzell Innerrhoden, Zug; check others on the phone) |
| Portugal | `pt` | 18 districts and the 2 autonomous regions (Azores, Madeira): 20 | coats of arms, if every district has one (see below) | insets for the Azores and Madeira |
| Sweden | `se` | 21 counties | coats of arms | – |
| South Africa | `za` | 9 provinces | none (no official flags) | – |
| New Zealand | `nz` | 16 regions and the Chatham Islands: 17 | none (no official flags) | an oval for the Chatham Islands |
| Colombia | `co` | 32 departments and Bogotá: 33 | flags | a circle for Bogotá, an oval for San Andrés and Providencia |

- **Every one** gets the Find and Name games for its parts and capitals (and games 5 and 6 where the table says), the Learning card with the facts below, Focus on, a stats tab, and the high-resolution coast. No timelines or layers for now.
- **Switzerland:** cantons with several pieces (Fribourg, Bern, Solothurn and others have small exclaves): every piece belongs to its canton. Liechtenstein is grey context. Local names in German, French and Italian (`wiki/de/`, `wiki/fr/`, `wiki/it/`), and Romansh where it's official (Graubünden). Accept the English, German, French and Italian names (Geneva / Genève / Genf / Ginevra).
- **Portugal:** the districts' coats of arms are on Commons; if all 18 are found, games 5 and 6 are **coat-of-arms games** like Mexico's, with the Azores and Madeira using their flags. If some are missing, they sit out those games and are listed under "Waiting for data". Record the choice under "Decisions to check".
- **Sweden:** the county coats of arms are official; games 5 and 6 are coat-of-arms games. Gotland is big enough without an oval.
- **South Africa: Lesotho and Eswatini** (decided 2026-11-18) are treated like Vatican City and San Marino on the Italy map: **drawn in their flag colours, not grey** (proposed: **Lesotho blue**, **Eswatini red**; record under "Decisions to check"), tappable, each with its own **"Focus on Lesotho" / "Focus on Eswatini"** button. **Their own maps are a separate job, planned later** (Lesotho's 10 districts, Eswatini's 4 regions); until then the button can show "Coming soon". They're proper shapes, not circles. The Prince Edward Islands (part of the Western Cape, far in the Southern Ocean) are left off.
- **New Zealand:** the Chatham Islands aren't in any region; they're their own part (17). The other outlying islands (Kermadec, the subantarctic islands) are left off. Accept Māori names (Tāmaki Makaurau for Auckland's region where used, Te Tai Tokerau for Northland and so on, from the downloaded articles).
- **Colombia:** Bogotá is a Capital District inside Cundinamarca: a circle. San Andrés, Providencia and Santa Catalina are far off in the Caribbean: an oval (or an inset if the oval sits too far from the mainland on the phone).

## Part 1: downloads

As in overnight_v2, Part 1:

1. `python tools/fetch_country_data.py ch pt se za nz co`, with the local languages (de, fr, it for Switzerland; pt; sv; af and zu are optional for South Africa, English is enough; mi is optional for New Zealand; es for Colombia).
2. **Shapes:** Natural Earth admin-1. Check each country's count matches the table (26, 20, 21, 9, 17, 33). Portugal's Natural Earth list may be the districts plus the islands; New Zealand's may lack the Chatham Islands as a part (cut it out if so). If any is out of date, use geoBoundaries ADM1 (CC BY 4.0, credit it).
3. **Census totals** into `census.json` with source and year: Switzerland (FSO STATPOP, latest), Portugal (Census 2021), Sweden (SCB, latest register figure; say so on the card), South Africa (Census 2022), New Zealand (Census 2023), Colombia (DANE Census 2018).
4. **Fact sources:** `--extras` with searches for the country-specific facts below (for example "Cantons of Switzerland" for joining years, "Wine regions of Portugal", "Provinces of Sweden", "Sápmi", "Bantustan", "Iwi", "Natural regions of Colombia").
5. **Download log** at the end of this file.

## Part 2: builds

Order: **Sweden, South Africa, New Zealand, Portugal, Colombia, Switzerland** (simplest first; Switzerland last because of its many small cantons and exclaves).

1. **Plans first:** `Switzerland_plan.md`, `Portugal_plan.md`, `Sweden_plan.md`, `South_Africa_plan.md`, `New_Zealand_plan.md`, `Colombia_plan.md`, from this file, with no open questions.
2. **Build each one** with the checklist (`tools/build_<code>.py`, `tools/<code>_facts.py`, the app wiring with each in `COUNTRY_MAPS` under its continent, small parts, tests, preview, PLAN.md).
3. **Tests also check:** Switzerland's exclaves open their canton's card; Lesotho and Eswatini show in their colours, open their own cards and Focus buttons, and don't block taps on the provinces around them; the Chatham Islands, San Andrés and the Portuguese islands open their cards from the oval or inset.

## Learning card facts (chosen 2026-11-18)

Every card also has the name, kind, capital, population (latest figure), area and rank, and the flag or coat of arms. Leave out any fact that isn't found rather than guess.

**All six (17):** name in the local language; demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: biggest club; main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage Sites; famous person from there; known for; famous company from there; largest city if it isn't the capital.

**Plus three for each country (20 in all):**

- **Switzerland:** main language (German, French, Italian or Romansh); year it joined the Confederation (1291 for Uri, Schwyz and Unterwalden, up to Jura in 1979); famous cheese or chocolate.
- **Portugal:** wine region (Douro, Alentejo, Vinho Verde); historic province (Minho, Beira, Algarve); famous explorer or Age of Discovery link.
- **Sweden:** historic land (Götaland, Svealand, Norrland) and province; Sámi area (yes or no, and which part); famous Swedish invention or brand from there.
- **South Africa:** main home languages (Zulu, Xhosa, Afrikaans, English and others); Big Five game reserve or famous wildlife; what it was before 1994 (Transvaal, Cape Province, Natal, Orange Free State, and the former homelands it took in).
- **New Zealand:** Māori name and the main iwi; North or South Island; famous film location (Lord of the Rings sites).
- **Colombia:** natural region (Andes, Caribbean, Pacific, Orinoquía, Amazon); famous coffee, fruit or crop; music style (vallenato, cumbia, salsa).
