# Job: overnight v10, five South American and Caribbean country maps

Venezuela, Ecuador, Bolivia, Uruguay and Cuba: first the downloads, then the builds. Decided with the user on 2026-11-28. **The downloads are done (2026-11-28, see the log at the end); the builds aren't started.**

**Don't start this job until the user says so**, and don't change the other job files to make room for it. Don't commit or push until the user says so.

It works like [overnight_v4.md](overnight_v4.md): the shared builder (`tools/build_country.py`, `tools/<code>_facts.py`), one `NEW_MAPS` row and a projection style each (add the style first), the same tests. Where this file and the earlier ones differ, this file wins.

## The countries (decided 2026-11-28)

| Country | Code | Parts | Games 5 and 6 | Small parts |
| --- | --- | --- | --- | --- |
| Venezuela | `ve` | 23 states and the Capital District: 24 (the Federal Dependencies: see below) | flags (state flags are official) | a circle for the Capital District; an oval for Nueva Esparta |
| Ecuador | `ec` | 24 provinces | flags (provincial flags are official) | the Galápagos as an inset |
| Bolivia | `bo` | 9 departments | flags (official) | – |
| Uruguay | `uy` | 19 departments | flags where all 19 are on Commons; otherwise none | a circle for Montevideo if needed |
| Cuba | `cu` | 15 provinces and the special municipality of Isla de la Juventud: 16 | none (provincial flags aren't official): check | – |

- **Venezuela and Guayana Esequiba (decided 2026-11-28): a dotted dispute only, not a part.** Guyana governs it; Venezuela claims it and in 2024 declared it a Venezuelan "state". It's drawn as a dotted disputed area with a dispute card (who governs it, who claims it, the 1899 award, the 1966 Geneva Agreement, the 2023 referendum, the ICJ case). Check the disputes layer has it (`tools/disputes_facts.py`); add it with a source if not. If Natural Earth or Wikidata lists "Guayana Esequiba" as a Venezuelan state, leave it out of the parts and record that. **The Federal Dependencies** (many small Caribbean islands): left off as a part unless they can be one tappable oval: judgement call, record it.
- **Ecuador:** the Galápagos (a province, 1,000 km offshore) as a framed inset with a square tap area and its own scale bar (as Spain's Canaries). Check Ecuador's mainland fits a tall phone screen with it.
- **Bolivia:** 9 departments. Spanish names, with the Quechua, Aymara or Guaraní name on the card where official. Sea access (lost to Chile in 1884) is history for the card, not a dispute area.
- **Uruguay:** 19 departments.
- **Cuba:** 15 provinces since 2011 (Artemisa and Mayabeque split from Havana Province) and Isla de la Juventud. Check Natural Earth has the 2011 map, not the old 14. **Guantánamo Bay** (leased to the United States, and Cuba says the lease is void) follows the disputes layer: check it's there, add it with a source if not.

Every country: Find and Name for the parts and capitals (games 5 and 6 where the table says), the Learning card, Focus on, a stats tab, the high-resolution coast. No timelines or layers.

## Part 1: downloads

1. Add the five to `tools/fetch_country_data.py` (local Wikipedia language: es for all five, plus qu and ay where there are articles for Bolivia) and `COUNTRY_QID`.
2. `--extras` and `--census`, with searches for the facts below (for example "Angel Falls", "Tepui", "Llanos", "Guayana Esequiba", "Galápagos Islands", "Volcanoes of Ecuador", "Indigenous peoples in Ecuador", "Salar de Uyuni", "Lake Titicaca", "Languages of Bolivia", "Candombe", "Uruguayan cuisine", "Music of Cuba", "Cuban cigar", "Cuban Revolution").
3. **Fonts:** Latin only (the Noto Sans subset covers Spanish and Quechua/Aymara letters: check ñ and the apostrophe forms).
4. **Shapes:** Natural Earth admin-1; check every count (24, 24, 9, 19, 16). Cuba's 2011 provinces: geoBoundaries ADM1 (credited) if Natural Earth has the old map.
5. **Populations: the latest official figure by default:** INE Venezuela (the 2011 census is the last; a later official projection if there is one: say which), INEC Ecuador (the 2022 census), INE Bolivia (the 2024 census), INE Uruguay (the 2023 census), ONEI Cuba (latest); each checked against the national total.
6. Download log at the end of this file.

## Part 2: builds

Order: **Uruguay, Bolivia, Cuba, Ecuador, Venezuela** (Venezuela last because of Guayana Esequiba and the Federal Dependencies).

1. Plans first: `Venezuela_plan.md`, `Ecuador_plan.md`, `Bolivia_plan.md`, `Uruguay_plan.md`, `Cuba_plan.md`, with no open questions.
2. Build, wire, test (all must pass), preview, PLAN.md, results and decisions to check at the end of this file.
3. **Tests also check:** Guayana Esequiba is dotted, isn't a Venezuelan part, and opens its dispute card; the Galápagos inset taps right and has its own scale bar; Guantánamo Bay opens its dispute card.

## Learning card facts (the 17 approved by the user 2026-11-27; the three per country approved 2026-11-28)

Every card also has the name, kind, capital, population (latest figure), area and rank, and the flag where there is one. Leave out any fact that isn't found rather than guess.

**All five (17):** name in the local language; demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: the biggest club; main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage; famous person from there; known for; famous company; largest city if it isn't the capital.

**Plus three for each country:**

- **Venezuela:** region (the Andes, the Llanos, the coast, Guayana); oil or mining; waterfall or tepui.
- **Ecuador:** region (Coast, Sierra, Amazon, Galápagos); volcano; Indigenous people.
- **Bolivia:** zone (Altiplano, valleys, lowlands); Indigenous language (Quechua, Aymara, Guaraní); salt flat, lake or mine.
- **Uruguay:** coast or interior; beach or port; gaucho, mate or asado tradition.
- **Cuba:** music or dance style; cigars, sugar or rum; revolution site.

## Download log (2026-11-28)

Downloaded ahead of the run (the user asked for the data first). `python tools/fetch_country_data.py --extras --no-images <codes>`, then `--census`, `python tools/fetch_boundaries.py` (geoBoundaries, into `tools/downloads/<code>/geoboundaries/`, with each file's licence in its .json), then the flags and coats of arms at Commons' pace (no failures; Slovenia's 212 municipal arms skipped: not needed).

| Country | Wikidata divisions (current) | Natural Earth admin-1 | English articles | Local articles | List articles | Flags | Coats of arms | Coast | Census items | geoBoundaries |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Venezuela | 25 (23 states, Capital District, Federal Dependencies) | 26 (want 24 + Federal Dependencies: one unnamed unit, check it) | 25 | 25 (es) | 6 | 24 | 23 | 1.4 MB | 18 | VEN_ADM1 |
| Ecuador | 24 | 24 (want 24) | 24 | 24 (es) | 6 | 23 | 14 | 0.7 MB | 25 | – |
| Bolivia | 9 | 9 (want 9) | 9 | 9 (es) | 6 | 9 | 7 | 0.1 MB | 10 | – |
| Uruguay | 19 | 19 (want 19) | 19 | 19 (es) | 5 | 17 | 19 | 0.3 MB | 20 | – |
| Cuba | 16 | 16 (want 16, the 2011 map) | 16 | 16 (es) | 7 | 0 | 10 | 2.8 MB | 17 | CUB_ADM1 |

**Shapes to use** (checked 2026-11-28):

- **Venezuela:** Natural Earth (23 states, the Capital District, the Federal Dependencies); its 26th, unnamed unit is probably a lake or a sliver: check and drop it. geoBoundaries VEN ADM1 (OCHA/INE, CC BY 3.0 IGO) as a cross-check. Guayana Esequiba isn't in Venezuela's admin-1 (it's Guyana's): the disputes layer.
- **Ecuador, Bolivia, Uruguay, Cuba:** Natural Earth, current (Cuba has Artemisa and Mayabeque).
- **Flags:** Uruguay 17 of 19 (games 5 and 6 only if the last 2 are found in the articles' infoboxes); Ecuador 23 of 24 (find the last one the same way); Cuba none (as planned).
