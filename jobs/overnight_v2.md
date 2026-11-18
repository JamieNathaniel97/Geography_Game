# Job: overnight v2, five more country maps

Austria, the Netherlands, Poland, Czechia and Belgium: first the downloads, then the builds. Decided with the user on 2026-11-18. **Nothing here is started yet.**

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
