# Job: overnight v9, five Central European and Balkan country maps

Croatia, Serbia, Bulgaria, Slovakia and Slovenia: first the downloads, then the builds. Decided with the user on 2026-11-28. **The downloads are done (2026-11-28, see the log at the end); the builds aren't started.**

**Don't start this job until the user says so**, and don't change the other job files to make room for it. Don't commit or push until the user says so.

It works like [overnight_v4.md](overnight_v4.md): the shared builder (`tools/build_country.py`, `tools/<code>_facts.py`), one `NEW_MAPS` row and a projection style each (add the style first), the same tests. Where this file and the earlier ones differ, this file wins.

## The countries (decided 2026-11-28)

| Country | Code | Parts | Games 5 and 6 | Small parts |
| --- | --- | --- | --- | --- |
| Croatia | `hr` | 20 counties (županije) and the City of Zagreb: 21 | coats of arms (official county arms) | a circle for Zagreb City if needed; island ovals if needed |
| Serbia | `rs` | 24 districts (okruzi) outside Kosovo and the City of Belgrade: 25 | none expected (districts have no official flags): check | a circle for Belgrade if needed |
| Bulgaria | `bg` | 28 provinces (oblasti), Sofia City included | coats of arms if all 28 are on Commons; otherwise none | a circle for Sofia City (inside Sofia Province) |
| Slovakia | `sk` | 8 self-governing regions (kraje) | coats of arms (official) | – |
| Slovenia | `si` | 12 statistical regions | none (statistical regions have no official symbols) | – |

- **Serbia and Kosovo (decided 2026-11-28): Kosovo is disputed grey, not a Serbian part.** It's grey and untappable as a part, with its own dispute card (it declared independence in 2008, Serbia still claims it, and how many countries recognise it), like Western Sahara on Morocco's map ([overnight_v8.md](overnight_v8.md)). Serbia's 5 districts in Kosovo (Kosovo, Peć, Prizren, Kosovska Mitrovica, Kosovo-Pomoravlje) are left out, so the parts are the 24 districts outside it and Belgrade (25). Check the disputes layer already has Kosovo (`tools/disputes_facts.py`); add it with a source if not. Serbia's total population is without Kosovo: say so on the card. Serbian names in Cyrillic and Latin (Београд / Beograd) both accepted, with the Latin shown and the Cyrillic on the card.
- **Croatia:** 20 counties and the City of Zagreb (a county in its own right, separate from Zagreb County). The long Dalmatian coast and its islands: island ovals where a county is mostly islands and too small to tap. Check Croatia still fits a tall phone screen (its curved shape) and record the window. The Bay of Piran (with Slovenia) follows the disputes layer.
- **Bulgaria:** Sofia City Province is separate from Sofia Province (a circle). Bulgarian names in Cyrillic (the subset has it) and Latin.
- **Slovakia:** 8 regions. Hungarian names where official in the south are accepted as alternatives.
- **Slovenia:** it has no official top-level units, so build the 12 statistical regions (NUTS 3, the usual subdivision on maps). Also download the 212 municipalities into `tools/downloads/si/municipalities/` for a possible second set later. Don't build them now. Record the choice under "Decisions to check".

Every country: Find and Name for the parts and capitals (games 5 and 6 where the table says), the Learning card, Focus on, a stats tab, the high-resolution coast. No timelines or layers.

## Part 1: downloads

1. Add the five to `tools/fetch_country_data.py` (local Wikipedia languages: hr, sr, bg, sk, sl) and `COUNTRY_QID`.
2. `--extras` and `--census`, with searches for the facts below (for example "Dalmatia", "Croatian islands", "Plitvice Lakes National Park", "Vojvodina", "Serbian Orthodox monasteries", "Kosovo", "Bulgarian rose oil", "Rila Monastery", "Thrace", "Castles in Slovakia", "High Tatras", "Postojna Cave", "Wine regions of Slovenia").
3. **Fonts:** Cyrillic is in the Noto Sans subset; check it covers Serbian (ђ ћ џ љ њ ј) and Bulgarian, and that the Latin covers č ć đ š ž ľ ĺ ŕ ô ä.
4. **Shapes:** Natural Earth admin-1; check every count (21, 25 after leaving out Kosovo, 28, 8, 12). Slovenia's statistical regions: Natural Earth may have the 193/212 municipalities instead: dissolve them into the 12 with the official table (SURS), or use geoBoundaries ADM1 if it has the 12, credited.
5. **Populations: the latest official figure by default:** DZS Croatia (the 2021 census or a later estimate), RZS Serbia (the 2022 census, without Kosovo), NSI Bulgaria, the Statistical Office of the Slovak Republic, SURS Slovenia; each checked against the national total.
6. **Slovenia's 212 municipalities:** data for later (see above).
7. Download log at the end of this file.

## Part 2: builds

Order: **Slovakia, Slovenia, Bulgaria, Croatia, Serbia** (Serbia last because of Kosovo).

1. Plans first: `Croatia_plan.md`, `Serbia_plan.md`, `Bulgaria_plan.md`, `Slovakia_plan.md`, `Slovenia_plan.md`, with no open questions.
2. Build, wire, test (all must pass), preview, PLAN.md, results and decisions to check at the end of this file.
3. **Tests also check:** Kosovo is grey, untappable as a part, and opens its dispute card; Croatia's islands and Zagreb City tap right; Sofia City and Sofia Province are told apart; Cyrillic names show in light and dark themes.

## Learning card facts (the 17 approved by the user 2026-11-27; the three per country approved 2026-11-28)

Every card also has the name, kind, capital, population (latest figure), area and rank, and the flag or coat of arms where there is one. Leave out any fact that isn't found rather than guess.

**All five (17):** name in the local language; demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: the biggest club; main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage; famous person from there; known for; famous company; largest city if it isn't the capital.

**Plus three for each country:**

- **Croatia:** historic region (Dalmatia, Istria, Slavonia...); famous island or beach; Roman or Venetian heritage.
- **Serbia:** historic region (Vojvodina, Šumadija...); monastery; Danube or other river site.
- **Bulgaria:** historic region (Thrace, Moesia, Macedonia); Orthodox monastery; rose oil, yoghurt or wine.
- **Slovakia:** historic region; castle; the Tatras or caves.
- **Slovenia:** historic region (Carniola, Styria, the Littoral...); caves or Alps; wine region.

## Download log (2026-11-28)

Downloaded ahead of the run (the user asked for the data first). `python tools/fetch_country_data.py --extras --no-images <codes>`, then `--census`, `python tools/fetch_boundaries.py` (geoBoundaries, into `tools/downloads/<code>/geoboundaries/`, with each file's licence in its .json), then the flags and coats of arms at Commons' pace (no failures; Slovenia's 212 municipal arms skipped: not needed).

| Country | Wikidata divisions (current) | Natural Earth admin-1 | English articles | Local articles | List articles | Flags | Coats of arms | Coast | Census items | geoBoundaries |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Croatia | 21 | 21 (want 21) | 21 | 21 (hr) | 6 | 21 | 21 | 1.2 MB | 22 | – |
| Serbia | 32 (incl. 5 Kosovo districts and Kosovo itself) | 25 (want 25: Kosovo is its own country in Natural Earth) | 31 | 32 (sr) | 6 | 2 | 2 | – | 32 | SRB_ADM1, SRB_ADM2 |
| Bulgaria | 28 | 28 (want 28) | 28 | 28 (bg) | 6 | 0 | 4 | 0.1 MB | 29 | – |
| Slovakia | 8 | 8 (want 8) | 8 | 8 (sk) | 5 | 8 | 8 | – | 9 | – |
| Slovenia | 212 municipalities | 193 municipalities (want 12 regions) | 212 | 212 (sl) | 6 | – | – | 0.1 MB | 213 | SVN_ADM1 (2 cohesion regions), SVN_ADM2 (213 municipalities) |

**Shapes to use** (checked 2026-11-28):

- **Croatia:** Natural Earth: 20 counties + Zagreb City, current (check the duplicate "Brodsko-Posavska" name: one of the two is probably Požeško-Slavonska, mislabelled).
- **Serbia:** Natural Earth: 24 districts + Belgrade, without Kosovo (Kosovo is its own admin-0 unit: draw it grey from there). geoBoundaries SRB ADM1 (OpenStreetMap, ODbL) as a cross-check only.
- **Bulgaria, Slovakia:** Natural Earth, current.
- **Slovenia:** dissolve Natural Earth's 193 municipalities into the 12 statistical regions with the membership table in `Statistical regions of Slovenia` (wiki/lists/); the 19 newer municipalities were split from old ones inside one region, so the old 193 dissolve cleanly (check each lands in one region). geoBoundaries SVN ADM2 (213, ODbL) only if that fails.
- **Coats of arms:** Bulgaria has only 4 on Wikidata: games 5 and 6 stay off unless the province articles' infoboxes give all 28 (as Nigeria's seals). Serbia's districts: 2, so none (as planned).
- **Slovenia's 212 municipalities:** `tools/downloads/si/` (wikidata.json, wiki/en, wiki/sl, census.json) and SVN_ADM2.
