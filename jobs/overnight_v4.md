# Job: overnight v4, five more country maps

Chile, Malaysia, South Korea, Peru and Egypt: first the downloads, then the builds. Decided with the user on 2026-11-18, as the second half of the batch started in [overnight_v3.md](overnight_v3.md). **Done 2026-11-27 (started at the user's word): all five built and tested; see "Results" at the end. Not committed until the user says so.**

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

## Results (2026-11-27)

Built with the shared builder (`python tools/build_country.py <code>`, `tools/<code>_facts.py`), which gained:
- `part_box` insets (only a part's islands move: Easter Island, enlarged three times, and the Juan Fernández Islands, both Valparaíso's);
  `context` insets that move the neighbours' land too, and `tap=False` drawn frames (East Malaysia below the peninsula, with Brunei);
  `bar="top"` for an inset's scale bar.
- `MERGE` (parts dissolved since Natural Earth's data), `DISPUTED` (join / ring / grey, with dotted lines and map `labels`),
  `FLAG_FALLBACK` (an emblem where there's no flag), custom emblem wording ("flags and emblems").
- Anchors also move inside when a part's centre is near an edge or hole (Gyeonggi's centre fell in Seoul).
- Hangul and Arabic card fonts (`fonts/gq-hangul.woff` 6 KB, `fonts/gq-arabic.woff` 10 KB; tools/build_fonts.py), and native-script
  names on the shared card in the script font with `dir="auto"` (Arabic right to left).

Projections: Chile transverse Mercator 71°W; Peru transverse Mercator 75.5°W; South Korea transverse Mercator 127.5°E; Malaysia Mercator;
Egypt Lambert conic (24°N, 30°N, 30.5°E).

### Download log

| Country | Divisions (Wikidata) | English articles | Local articles | Flags | Coats of arms | Coast |
| --- | --- | --- | --- | --- | --- | --- |
| Chile | 16 | 16 | 16 (es) | 16 | 14 | 14.3 MB |
| Peru | 26 | 26 | 26 (es) | 26 | – | 1.0 MB |
| South Korea | 17 (Gwangju and South Jeolla dissolved) | 17 | 15 (ko) | 15 | – | – |
| Malaysia | 16 | 16 | 16 (ms) | 16 | 15 | 2.9 MB |
| Egypt | 27 | 27 | 27 (ar) | 25 | 15 (some failed on Commons rate limits; Cairo's and Luxor's are in) | 1.7 MB |

Fonts: `tools/downloads/fonts/NotoSansKR.ttf`, `NotoSansArabic.ttf`. Also saved: OpenDOSM CSVs (`tools/downloads/my/dosm/`) and the MOIS
resident registration page (`tools/downloads/kr/mois/statMonth.html`).

### Populations (latest official figure by default, each checked against a national total)

- Chile: Census 2024, 18,480,432 (the list article's Arica y Parinacota figure was a typo: 224,569 for 244,569).
- Peru: INEI estimates 2025; the parts add up to 34,170,116, 12,384 (0.04%) above the national 34,157,732 (mixed rounding; allowed).
- South Korea: MOIS resident registration, end of October 2026, 51,075,282.
- Malaysia: OpenDOSM estimates, 1 January 2026, 34,389,400 (thousands, within rounding).
- Egypt: CAPMAS estimates, November 2023, 106,668,704.

### Decisions to check

1. **South Korea has 16 parts, not 17: Gwangju and South Jeolla merged on 1 July 2026** (the Jeonnam-Gwangju Integrated Special City;
   Korean Wikipedia, MOIS and Wikidata all have it). The plan said 17. The merged city has no flag on Commons yet: it sits out the flag
   games ("Waiting for data"). Natural Earth's shapes also predate Daegu absorbing Gunwi County (2023).
2. **Japan's map doesn't show Dokdo** (sea there, no dotted line); South Korea's shows it as North Gyeongsang's with a dotted ring. Fix
   in tools/build_jp.py (a grey speck and a dotted ring) if wanted.
3. **Malaysia: East Malaysia is an inset below the peninsula** (with Brunei and the Kalimantan coast moved with it), not in its true place.
4. **Egypt's games 5 and 6 are "flags and emblems"**: 25 flags, plus Cairo's and Luxor's emblems.
5. **Peru uses 2025 estimates** that are 0.04% off the national figure, rather than the 2017 census (which adds up exactly).
6. **Easter Island is shown three times larger** than true scale in its inset (it has its own scale bar).
7. Bir Tawil's label shows once zoomed in a little (it's too small at whole-country zoom).

### Tests

`_bench_nm.html?d=<code>&r=<region>` for all five (anchors including the circles and insets; names, unaccented forms and capitals;
capital dots; flags and emblems; card facts; the tap test at three zooms with the detail level), plus South Africa, Portugal and Spain as
regression checks, and `_bench_menu.html` (the Countries tab lists all sixteen new countries; set switches; Focus; the US and Russia
timelines).

**All pass (2026-11-27):** every anchor (16, 26, 16, 16, 27), names with no problems, capital dots, flags and emblems (Jeonnam-Gwangju has none yet), 100% on the tap test at whole-map, 2.5x and close zoom with the detail level on, for all five; South Africa, Portugal and Spain unchanged; the menu bench lists all sixteen new countries and every older check still passes; no script errors. Screenshots checked by eye, light and dark (the Hangul and Arabic names render; Arabic right to left).

## Disputed territories (added 2026-11-27, at the user's request)

**Every disputed territory in the world now has a dotted outline (areas) or dotted ring (specks) and a small "Disputed" info card in Learning mode**, on the world map (flat and globe) and every country map: who governs it, who claims it, since when, and a sentence or two on why.
- Data: `tools/build_disputes.py` -> `data/disputes.json` (83 KB): Natural Earth's 99 disputed areas, with hand-written facts in `tools/disputes_facts.py` (neutral wording: governed by / claimed by). 92 entries after merging pieces (Jerusalem, the Korean DMZ) and skipping artefacts: 37 rings, 50 areas, and 5 that are whole world-map countries (Taiwan, Kosovo, Palestine's Gaza and West Bank, Belize), which get a "Disputed" section on that country's card instead of a separate tap area.
- **Dokdo** shows as a dotted ring with its card on both the South Korea and the Japan maps (and the world map). The South Korea map's own ring was removed in favour of the shared layer; Dokdo stays part of North Gyeongsang there.
- Taps (js/mapview.js `disputeAt`, before the country tap): inside an area's shape first; then the nearest ring (within 14 px over the sea; over a country's land only within 6 px and once zoomed in, so Taiwan or Somaliland aren't taken by a neighbouring speck); then small areas over the sea by their box plus a margin (the Falklands at world zoom). Quiz games ignore the layer. A map with its own dotted disputed lines (India, Egypt) keeps those and shows only the rings.
- Tests: `_bench_nm.html?...&dsp=<names>&card=<ISO>` taps each named dispute and checks its card; all pass on the world, South Korea, Japan and Egypt maps. Bir Tawil is about a pixel tall at world zoom (a tap there gives Egypt); zoomed in it opens its card.
- **A tapped disputed territory is highlighted grey** (areas filled, rings filled) while its card is open; the highlight goes when the card closes or a country is tapped, and a country's highlight goes when a dispute is tapped (2026-11-27).
- **Fix (2026-11-27): places with their own card keep it.** A dispute over a country or part that has a card (Kashmir and Ladakh, Arunachal Pradesh, Crimea in Ukraine, Somaliland in Somalia, Hala'ib in the Red Sea governorate) now opens that card with a "Disputed" line and the full dispute in More facts (`addDisputeToCard`), with the area in grey; the standalone dispute card is only for disputes over grey land or the sea (Aksai Chin, Gilgit-Baltistan, the Falklands, Bir Tawil). Before this fix the dispute card replaced those cards.
