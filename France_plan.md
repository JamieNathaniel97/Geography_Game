# France – Plan

The brief for France's country map in Gaia Quest, in the same pattern as the built country maps (see [PLAN.md](PLAN.md)) and the build job ([jobs/build_countries.md](jobs/build_countries.md), with the checklist every build follows). Drafted 2026-11-18 from the decisions of 2026-11-17. **Open questions** are at the end.

## What's on the map

- **The 13 metropolitan regions** (decided 2026-11-17: regions only, not departments): Auvergne-Rhône-Alpes, Bourgogne-Franche-Comté, Brittany, Centre-Val de Loire, Corsica, Grand Est, Hauts-de-France, Île-de-France, Normandy, Nouvelle-Aquitaine, Occitanie, Pays de la Loire, Provence-Alpes-Côte d'Azur.
- **The 5 overseas regions are left off** (decided: too far away): Guadeloupe, Martinique, French Guiana, Réunion and Mayotte.
- `kind`: Region; Corsica: Territorial collectivity.
- `unit` word: **"Regions"**. Grey context: the UK (Channel coast), Belgium, Luxembourg, Germany, Switzerland, Italy, Monaco, Andorra, Spain; the Channel Islands (Crown Dependencies) grey.

## Wiring

`COUNTRY_MAPS.FRA`: `{ name: "France", focus: "France", cont: "Europe", unit: "Regions", data: "fr", region: "france" }`. Loader `GG.loadFR`; `DATASETS.fr` with **`noFlags: true`**. Projection: **Lambert conformal conic** (Lambert-93: standard parallels 44°N and 49°N, centre 3°E).

## Data build: `tools/build_fr.py`

- Shapes: Natural Earth admin-1 lists the 96 metropolitan departments with their region: **dissolve them into the 13 regions**; drop the overseas ones. **Detail level** from `tools/downloads/fr/coast_f.geojson`.
- Population: INSEE's latest legal populations, from the downloaded list articles; check against the metropolitan total.

## Capitals

Lyon, Dijon, Rennes, Orléans, Ajaccio, Strasbourg, Lille, Paris, Rouen, Bordeaux, Toulouse, Nantes, Marseille.

## Names matching

- English and French: Brittany / Bretagne, Normandy / Normandie, Corsica / Corse, Provence-Alpes-Côte d'Azur / PACA / Provence, Île-de-France / Ile de France / Paris region, Burgundy-Franche-Comté / Bourgogne-Franche-Comté, Grand Est / Great East, Hauts-de-France / Upper France, Occitania / Occitanie, New Aquitaine / Nouvelle-Aquitaine.
- Accents optional. Capitals: Marseille / Marseilles, Lyon / Lyons.

## Tiny parts

None needed (Île-de-France and Corsica are big enough); Monaco grey.

## Flags (games 5 and 6)

**None** (decided 2026-11-17: most regions have no official flag, only a logo). Like India, no flag games and no Flags stats tab.

## Learning card

Name, kind, capital, population, area and rank of 13. **More facts (18, chosen 2026-11-17):** name in French; demonym; regional language; famous dish; famous cheese; famous wine or drink; biggest festival; highest point; main river; coast; natural wonder or national park; historic provinces it covers; formed (2016 merger, or unchanged); famous landmark; UNESCO World Heritage; famous person from there; known for; largest city if it isn't the capital.

## Layers and timeline

- No layer.
- Timeline: the Napoleonic idea is **shelved** (2026-11-17).

## Build order

1. `tools/build_fr.py` (departments dissolved into regions, detail level, parts, capitals) and `tools/fr_facts.py`.
2. Map, loader, card, stats tab, "Focus on France".
3. Tests (the build job's checklist).

## Open questions for the user

None at the moment.
