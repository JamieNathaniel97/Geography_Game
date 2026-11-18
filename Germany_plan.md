# Germany – Plan

The brief for Germany's country map in Gaia Quest, in the same pattern as the built country maps (see [PLAN.md](PLAN.md), [Russia_plan.md](Russia_plan.md)) and the build job ([jobs/build_countries.md](jobs/build_countries.md), which has the checklist every build follows). Drafted 2026-11-18 from the decisions of 2026-11-17. **Open questions** are at the end.

## What's on the map

- **16 states** (*Länder*): Baden-Württemberg, Bavaria, Berlin, Brandenburg, Bremen, Hamburg, Hesse, Lower Saxony, Mecklenburg-Vorpommern, North Rhine-Westphalia, Rhineland-Palatinate, Saarland, Saxony, Saxony-Anhalt, Schleswig-Holstein, Thuringia.
- `kind`: State, or City-state (Berlin, Hamburg, Bremen).
- `unit` word: **"States"**. Neighbours as grey context: Denmark, the Netherlands, Belgium, Luxembourg, France, Switzerland, Austria, the Czech Republic, Poland.

## Wiring

`COUNTRY_MAPS.DEU`: `{ name: "Germany", focus: "Germany", cont: "Europe", unit: "States", data: "de", region: "germany" }` (drop `soon`). Loader `GG.loadDE` for `data/de-states.json` + `data/de-parts.json`; `DATASETS.de`; projection: **Lambert conformal conic**, standard parallels 48.67°N and 53.67°N, centre 10.5°E (the usual one for maps of Germany).

## Data build: `tools/build_de.py`

- Shapes: Natural Earth admin-1 (16 states, complete); **detail level** from `tools/downloads/de/coast_f.geojson` (the Frisian islands, Rügen, the Wadden Sea coast).
- Population: the **2022 census** (Zensus 2022), from the downloaded list articles; check the states add up to the national total.
- Flags: all 16 states have official flags (`tools/downloads/de/flags/`; Bavaria's lozenge flag is the common one).

## Capitals

Stuttgart, Munich, Berlin, Potsdam, Bremen, Hamburg, Wiesbaden, Hanover, Schwerin, Düsseldorf, Mainz, Saarbrücken, Dresden, Magdeburg, Kiel, Erfurt. The three city-states are their own capitals (sit in the capitals games as themselves, like Moscow).

## Names matching

- English and German names: Bavaria / Bayern, Hesse / Hessen, Lower Saxony / Niedersachsen, North Rhine-Westphalia / Nordrhein-Westfalen / NRW, Rhineland-Palatinate / Rheinland-Pfalz, Saxony / Sachsen, Saxony-Anhalt / Sachsen-Anhalt, Thuringia / Thüringen, Mecklenburg-Vorpommern / Mecklenburg-Western Pomerania.
- Capitals: Munich / München, Hanover / Hannover, Cologne isn't a capital.
- Umlauts optional (Thuringen, Munchen, Dusseldorf), ß as ss.
- Saxony and Saxony-Anhalt, Lower Saxony: typing "Saxony" counts only for Saxony.

## Tiny parts

Adaptive circles for **Berlin** and **Bremen** (Bremen's two pieces: Bremen and Bremerhaven); Hamburg and Saarland are big enough.

## Flags (games 5 and 6)

Flag games for all 16.

## Learning card

Name, kind, capital, population (2022 census), area and rank of 16, flag. **More facts (17, chosen 2026-11-17):** name in German; demonym; dialect; famous dish; beer or wine; biggest festival or tradition; football: biggest club; main river; highest point; coast (North Sea, Baltic, or landlocked); natural wonder or national park; former kingdom or duchy; East or West Germany before 1990; famous castle or landmark; UNESCO World Heritage; known for; famous company from there.

## Layers and timeline

- No layer.
- **Timeline: to discuss (morning agenda, 2026-11-18).** The idea: the unification of the German-speaking states (Prussia and the others, to the German Empire in 1871); then zoom out for Nazi Germany's expansion and collapse; then the division (East red, West blue) and reunification in 1990.

## Build order

1. `tools/build_de.py` (shapes, detail level, parts, capitals, flags) and `tools/de_facts.py`.
2. Map, loader, card, stats tab, "Focus on Germany".
3. Tests (the build job's checklist).
4. Timeline, once decided.

## Open questions for the user

- The timeline (morning agenda).
