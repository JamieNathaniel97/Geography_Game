# Job: overnight v2, five more country maps

Austria, the Netherlands, Poland, Czechia and Belgium: first the downloads, then the builds. Decided with the user on 2026-11-18. **Done 2026-11-26 (started at the user's word): all five built and tested; see "Results" at the end. Not committed until the user says so.**

This is a separate job from the queue in [README.md](README.md). **Don't start it until the user says so** (decided 2026-11-18), even if the rest of the queue is finished, and don't change those job files to make room for it. Push only when the user says so, as for the rest of the queue.

The builds follow **"The checklist for every build"** in [build_countries.md](build_countries.md), and the downloads use the same scripts and folders as [download_new_countries.md](download_new_countries.md). Read both first. Where this file and the checklist differ, this file wins.

## The countries (decided 2026-11-18)

| Country | Code | Parts | Games 5 and 6 | Circles |
| --- | --- | --- | --- | --- |
| Austria | `at` | 9 states | flags | Vienna |
| Netherlands | `nl` | 12 provinces (the Caribbean Netherlands left off) | flags | – |
| Poland | `pl` | 16 voivodeships | flags | – |
| Czechia | `cz` | 14 regions | flags | Prague |
| Belgium | `be` | **two sets:** the 3 regions (Flanders, Wallonia, Brussels-Capital), and the 10 provinces plus Brussels (11) | flags (both sets) | Brussels |

- **Quick ones:** few parts, stable borders, and every part has an official flag. No disputed areas, no outlying islands, no recent boundary changes.
- **Every one** gets the six games (Find and Name for the parts, capitals, flags), the Learning card with the facts below, Focus on, a stats tab, and the high-resolution coast (Austria and Czechia are landlocked, so their detail level is just the borders and lakes).
- **Circles** (decided): Vienna (inside Lower Austria), Prague (inside Central Bohemia) and Brussels (inside Flemish Brabant), like Berlin.
- **The Netherlands:** Bonaire, Sint Eustatius and Saba are **left off** (decided), as with France's overseas regions. Check that Natural Earth doesn't put them in the Netherlands' admin-1 list; drop them if it does.
- **Belgium's two sets** (decided: both), like Spain's two levels. The regions set has 3 parts and the provinces set 11. The 3 regions have official flags (Flanders' lion, Wallonia's rooster, Brussels' iris). Brussels-Capital is in both sets. Build the provinces first, then dissolve them into the regions (Flanders: Antwerp, East Flanders, Flemish Brabant, Limburg, West Flanders; Wallonia: Hainaut, Liège, Luxembourg, Namur, Walloon Brabant).
- **Timelines and layers:** none for now.
- **Names matching:** the usual rules, plus the local names and the English ones: Lower Austria / Niederösterreich, North Holland / Noord-Holland, Lesser Poland / Małopolskie / Małopolska, South Moravian / Jihomoravský kraj, Flemish Brabant / Vlaams-Brabant / Brabant flamand, Liège / Luik / Lüttich. Polish and Czech accents optional (Łódź / Lodz, Ústí / Usti). Belgian parts accept the Dutch, French and German forms. Check for `notTypo` pairs: North / South Holland, Upper / Lower Austria, Lesser / Greater Poland, the Brabants, the two Flanders, Liberec / Pardubice style near-misses.

## Part 1: downloads

Into `tools/downloads/<code>/` (git-ignored), with `tools/fetch_country_data.py`, which re-runs skip what's already there.

1. **Main downloads:** `python tools/fetch_country_data.py at nl pl cz be`: `wikidata.json` (every division with an ISO 3166-2 code), the English and local Wikipedia articles (`wiki/en/`, and `wiki/de/` for Austria, `wiki/nl/` for the Netherlands, `wiki/pl/`, `wiki/cs/`, and both `wiki/nl/` and `wiki/fr/` for Belgium), flags and coats of arms at 500 px, and `coast_f.geojson`. Add the languages to the script if it doesn't know them yet.
2. **Shapes:** Natural Earth admin-1 (`tools/downloads/ne10/`, already downloaded). Check that each country's list matches the table above (9, 12, 16, 14, 11). If any is out of date or missing, say so in the log and use geoBoundaries ADM1 (CC BY 4.0, credit it) instead.
3. **Census totals** into `tools/downloads/<code>/census.json`, with the source and year: Austria (Statistik Austria), the Netherlands (CBS; it has no traditional census, so use the latest 1 January register figure and say so on the card), Poland (the 2021 census), Czechia (the 2021 census), Belgium (Statbel, latest 1 January figure). The parts must add up to the national total.
4. **Sources for the card facts:** `python tools/fetch_country_data.py --extras at nl pl cz be`, with searches added for the country-specific facts: for example "Partitions of Poland", "Land reclamation in the Netherlands" and "Flevoland", "Bohemia", "Moravia", "Czech Silesia", "Communities, regions and language areas of Belgium", "List of ski resorts in Austria". Check `extras.json` for what each search found.
5. **Download log:** add a table like the one in `download_new_countries.md` at the end of this file (divisions, articles, flags, coats of arms, coast), and note anything missing.

## Part 2: builds

Order: **Austria, Czechia, Poland, Netherlands, Belgium** (simplest first; Belgium last because of its two sets).

1. **Plans first:** write `Austria_plan.md`, `Czechia_plan.md`, `Poland_plan.md`, `Netherlands_plan.md` and `Belgium_plan.md` from the decisions in this file, in the same style as the existing plans, with no open questions.
2. **Then build each one** with the checklist in `build_countries.md`: `tools/build_<code>.py`, `tools/<code>_facts.py`, the app wiring (add each to `COUNTRY_MAPS` under Europe), the circles, the tests (all must pass), the preview, and a line in PLAN.md.
3. **Tests also check:** Belgium's region and province sets both work, with their own stats; Brussels is in both; the circles for Vienna, Prague and Brussels open their own cards and don't block taps on the part around them.

## Learning card facts (chosen 2026-11-18)

Every card also has the name, kind, capital, population (latest figure), area and rank, and the flag. Leave out any fact that isn't found rather than guess.

**All five (17):**

1. Name in the local language (Niederösterreich, Noord-Brabant, Małopolskie, Jihomoravský kraj, Vlaams-Brabant / Brabant wallon)
2. Demonym
3. Dialect or regional language (for example Limburgish, Frisian, Silesian, Kashubian, Moravian dialects, Walloon)
4. Famous dish
5. Famous drink (beer, wine, jenever, Becherovka, vodka)
6. Biggest festival or tradition
7. Football: the biggest club
8. Main river
9. Highest point
10. Natural wonder or national park
11. Historic region or old kingdom (Bohemia or Moravia, Galicia, Flanders, the Duchy of Brabant)
12. Famous castle or landmark
13. UNESCO World Heritage Sites
14. Famous person from there
15. Known for
16. Famous company from there (Red Bull, Philips, Škoda, Stella Artois)
17. Largest city, if it isn't the capital

**Plus one for each country (18 in all):**

- **Austria:** ski resorts or Alpine peaks
- **Netherlands:** land reclaimed from the sea, and how much lies below sea level
- **Poland:** which partition it was in before 1918 (Prussian, Russian or Austrian)
- **Czechia:** whether it's in Bohemia, Moravia or Czech Silesia
- **Belgium:** language community (Dutch-, French- or German-speaking)

**Belgium's 3 regions** get the same card, with their facts drawn from the regions' own articles.

## Results (2026-11-26)

**Built with one shared builder** rather than five copies of build_de.py: `python tools/build_country.py <code>` reads `tools/<code>_facts.py` (config, part table, card facts; Belgium's regions as `SET2`). In the app: one `NEW_MAPS` row each (js/app.js), `GG.loadCountry` (js/geo.js), `showCountryCard`, and a projection style each (js/mapview.js). The country-page Set switch is now generic (`SETS`, shared with Spain) and Belgium also gets a set button in Learning mode. SW cache v77.

### Download log

| Country | Divisions (Wikidata) | English articles | Local articles | List articles | Flags | Coats of arms | Coast |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Austria | 9 | 9 | 9 (de) | 8 | 9 (+ 9 state flags with arms) | 9 | 63 KB |
| Netherlands | 17 (incl. Caribbean) | 17 | 17 (nl) | 9 | 17 | 17 | 279 KB |
| Poland | 17 (incl. Kielce) | 17 | 17 (pl) | 8 | 17 | 17 | 421 KB |
| Czechia | 109 (regions and districts) | 106 | 107 (cs) | 9 | 30 | 30 | 21 KB |
| Belgium | 13 | 13 | 13 (nl), 13 (fr) | 7 | 13 | 13 | 48 KB |

`census.json` (new `--census` option: every dated population figure from Wikidata) for all five. Natural Earth admin-1 matched the table (9, 12 after dropping the Caribbean Netherlands, 16, 14, 11); geoBoundaries wasn't needed.

### Populations (all checked against a national total)

- Austria: Statistik Austria, 1 January 2025, 9,197,213.
- Czechia: Czech Statistical Office, 1 January 2026, 10,915,839.
- Poland: GUS, 30 June 2025, 37,401,692.
- Netherlands: CBS open data (70072ned), 1 January 2025, 18,044,027.
- Belgium: Statbel, 1 January 2025, 11,825,551 (both sets).

### Decisions to check

1. **Poland and Czechia: latest figures, not the 2021 census.** No census table by region was in the downloads, and GUS's API didn't answer. Poland uses GUS 30 June 2025 (the table's sum is the total); Czechia uses CZSO 1 January 2026 (adds up to CZSO's own total). Alternative: find the census tables and switch.
2. **Austria's flag games use the state flags with arms**: Salzburg, Vienna and Vorarlberg share one red-white civil flag.
3. **Netherlands: land area on the card** ("Land area"), and the light map cut to the shoreline (`FIT_LIGHT`) so the IJsselmeer, Markermeer and Flevoland's polders show. Natural Earth's provinces covered the lakes.
4. **Capitals outside the part:** Central Bohemia (Prague) and Flanders (Brussels) sit out the capitals games; their cards say why.
5. **Poland's split capitals:** Bydgoszcz / Toruń and Gorzów Wielkopolski / Zielona Góra are both accepted, with a dot each; the governor's seat is the one shown in Find by capital.
6. **Projections:** Austria and Belgium their national Lambert conics, Czechia a Lambert conic (49°N, 50.5°N), Poland transverse Mercator on 19°E, the Netherlands an oblique stereographic on Amersfoort.
7. **Belgium's card** says "Name in Dutch" or "Name in French" per part (Brussels: both).

### Also changed

- **Name matching:** ł, ß, ø, æ and đ now count as l, ss, o, ae and d (typing "Lodz" for Łódź didn't match before). Applies to every map.
- **Spain's provinces:** Palencia and Valencia no longer count as typos of each other (found by the new bench; `PROV_NOT_TYPO` in build_es.py, data patched).

### Tests (all pass)

`_bench_nm.html?d=<code>&r=<region>` (git-ignored; reports to the scratchpad test server): every part's anchor opens its card; every name, spelling, unaccented form and capital accepted, notTypo refused, no part accepting another's name; capital dots; flags load; card facts; the tap test at whole-map, 2.5x and 7.5x zoom with the detail level (100% for all five and Belgium's regions). `_bench_menu.html`: the Countries tab lists the five, Belgium's and Spain's set switches, a Belgium regions game, the stats tabs, Focus on Austria from the world map, and the US and Russia maps with their timelines; no script errors. Germany and both Spanish sets re-run: still 100%. Screenshots checked by eye (light and dark).
