# Job: overnight v4, five more country maps

Chile, Malaysia, South Korea, Peru and Egypt: first the downloads, then the builds. Decided with the user on 2026-11-18, as the second half of the batch started in [overnight_v3.md](overnight_v3.md). **Nothing here is started yet.**

**Don't start this job until the user says so** (decided 2026-11-18), and don't change the other job files to make room for it. Push only when the user says so.

It works exactly like [overnight_v2.md](overnight_v2.md) and [overnight_v3.md](overnight_v3.md): the builds follow **"The checklist for every build"** in [build_countries.md](build_countries.md), and the downloads use the same scripts and folders as [download_new_countries.md](download_new_countries.md). The overnight rules in [OVERNIGHT.md](OVERNIGHT.md) apply if this is run overnight. Where this file and the checklist differ, this file wins.

## The countries (decided 2026-11-18)

| Country | Code | Parts | Games 5 and 6 | Small parts |
| --- | --- | --- | --- | --- |
| Chile | `cl` | 16 regions | flags | an inset for Easter Island and the Juan Fernández Islands (part of Valparaíso) |
| Malaysia | `my` | 13 states and 3 federal territories: 16 | flags | circles for Kuala Lumpur, Putrajaya and Labuan |
| South Korea | `kr` | 17 (8 provinces, 6 metropolitan cities, Seoul, Sejong, Jeju) | flags | circles for the cities that are too small to tap; Jeju is big enough |
| Peru | `pe` | 24 departments, Lima Province and Callao: 26 | flags, where official (see below) | circles for Lima Province and Callao if needed |
| Egypt | `eg` | 27 governorates | to decide at build (see below) | – |

- **Every one** gets the Find and Name games for its parts and capitals (and games 5 and 6 where the table says), the Learning card with the facts below, Focus on, a stats tab, and the high-resolution coast. No timelines or layers for now.
- **Chile:** the Antarctic claim is left off, as with Argentina. Easter Island and the Juan Fernández Islands are far out in the Pacific: an inset box, like Spain's Canaries, belonging to Valparaíso. Check the Natural Earth list has Ñuble (created 2018): 16 regions.
- **Malaysia:** two parts of the map, the peninsula and Borneo (Sabah, Sarawak, Labuan), with the sea between them; Brunei, Singapore, Indonesia and Thailand are grey context. Fit both in a tall phone window, with an inset if they won't fit at a usable size.
- **South Korea:** recent names: Gangwon State (2023) and Jeonbuk State (2024); accept the old names (Gangwon Province, North Jeolla). **Hangul names on the cards: download a Korean font** (Noto Sans KR) and subset it (`tools/build_fonts.py`), as for Japan. **Dokdo** (the Liancourt Rocks, governed by South Korea and claimed by Japan): part of North Gyeongsang, following the rule used for the Kurils on the Russia map: tappable for the side that governs it, with a dotted line on Japan's side. Check the Japan map shows it the same way (grey, dotted), and record any mismatch under "Decisions to check". North Korea is grey context.
- **Peru:** Lima Province (the capital) is separate from the Lima Region; Callao is its own part. Most regions have flags; any without an official one sits out the flag games (list it under "Waiting for data").
- **Egypt:** governorate flags and emblems are patchy. If every governorate has a flag or emblem on Commons, make games 5 and 6 "Find by emblem" games like Mexico's coats of arms; otherwise no games 5 and 6, like France. Record the choice. **Arabic names on the cards: download an Arabic font** (Noto Sans Arabic), subset it, and check right-to-left text displays correctly. **The Hala'ib Triangle** (governed by Egypt, claimed by Sudan): the Kurils rule again, tappable as part of the Red Sea governorate with a dotted line. **Bir Tawil** (claimed by neither country): grey, labelled "Bir Tawil (unclaimed)". Record both under "Decisions to check".

## Part 1: downloads

As in overnight_v2, Part 1:

1. `python tools/fetch_country_data.py cl my kr pe eg`, with the local languages (es for Chile and Peru; ms for Malaysia; ko; ar).
2. **Shapes:** Natural Earth admin-1. Check each country's count matches the table (16, 16, 17, 26, 27). Egypt's governorates have changed several times; Peru's Natural Earth list may join Lima Province and the Lima Region. If any is out of date, use geoBoundaries ADM1 (CC BY 4.0, credit it).
3. **Fonts:** `tools/downloads/fonts/NotoSansKR.ttf` and `NotoSansArabic.ttf`.
4. **Populations** into `census.json` with source and date: **the latest official figure by default** (decided by the user 2026-11-26), checked against the national total for the same date; a census only if nothing newer is published by region. Say which on the card.
5. **Fact sources:** `--extras` with searches for the country-specific facts below (for example "Climate of Chile", "Mapuche", "Malay rulers", "Three Kingdoms of Korea", "Inca Empire", "Upper and Lower Egypt").
6. **Download log** at the end of this file.

## Part 2: builds

Order: **Chile, Peru, South Korea, Malaysia, Egypt** (Egypt last because of its font, right-to-left text and the disputed areas).

1. **Plans first:** `Chile_plan.md`, `Malaysia_plan.md`, `South_Korea_plan.md`, `Peru_plan.md`, `Egypt_plan.md`, from this file, with no open questions.
2. **Build each one** with the checklist (`tools/build_<code>.py`, `tools/<code>_facts.py`, the app wiring with each in `COUNTRY_MAPS` under its continent, small parts, tests, preview, PLAN.md).
3. **Tests also check:** Easter Island opens Valparaíso's card from the inset; Malaysia's two halves both fit and tap; Hangul and Arabic names show correctly in light and dark themes (Arabic right to left); Dokdo and the Hala'ib Triangle show their dotted lines; Bir Tawil can't be tapped.

## Learning card facts (chosen 2026-11-18)

Every card also has the name, kind, capital, population (latest figure), area and rank, and the flag where there is one. Leave out any fact that isn't found rather than guess.

**All five (17):** name in the local language; demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: biggest club; main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage Sites; famous person from there; known for; famous company from there; largest city if it isn't the capital.

**Plus three for each country (20 in all):**

- **Chile:** climate zone (desert north, Mediterranean centre, Patagonian south); famous wine valley or mine (copper, lithium); Indigenous peoples (Mapuche, Aymara, Rapa Nui).
- **Malaysia:** ruler (sultan, raja, governor, or none for the federal territories); main ethnic groups (Malay, Chinese, Indian, Iban, Kadazan-Dusun); Peninsula or Borneo.
- **South Korea:** name in Hangul with its romanisation; famous food (a kimchi variety, Jeonju's bibimbap); historic kingdom (Silla, Baekje, Goguryeo).
- **Peru:** natural region (coast, Andes, Amazon); ancient civilisation (Inca, Moche, Nazca, Chimú); Quechua or Aymara speakers.
- **Egypt:** Upper or Lower Egypt, or the Sinai or the desert; ancient sites (pyramids, temples, tombs); name in Arabic.
