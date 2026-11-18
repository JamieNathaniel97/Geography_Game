# Argentina – Plan

The brief for Argentina's country map in Gaia Quest, in the same pattern as the built country maps (see [PLAN.md](PLAN.md)) and the build job ([jobs/build_countries.md](jobs/build_countries.md), with the checklist every build follows). Drafted 2026-11-18 from the decisions of 2026-11-17. **Open questions** are at the end.

## What's on the map

- **23 provinces and the Autonomous City of Buenos Aires**: 24 parts.
- **No Falklands** (decided 2026-11-17): left off the map, and no Antarctic claim. South Georgia isn't shown either.
- `kind`: Province, or Autonomous city.
- `unit` word: **"Provinces"**. Grey context: Chile, Bolivia, Paraguay, Brazil, Uruguay.

## Wiring

`COUNTRY_MAPS.ARG`: `{ name: "Argentina", focus: "Argentina", cont: "South America", unit: "Provinces", data: "ar", region: "argentina" }`. Loader `GG.loadAR`; `DATASETS.ar`. Projection: **Transverse Mercator**, centre 64°W (Argentina is long and thin, from 22°S to 55°S).

## Data build: `tools/build_ar.py`

- Shapes: Natural Earth admin-1 (24, complete; Tierra del Fuego without its Falklands and Antarctic claim); **detail level** from `tools/downloads/ar/coast_f.geojson` (Patagonia's coast, Tierra del Fuego).
- Population: the **2022 census** (INDEC); check against the national total.
- Flags: all 24 have flags (`tools/downloads/ar/flags/`).

## Capitals

La Plata (Buenos Aires Province), San Fernando del Valle de Catamarca, Resistencia, Rawson, Córdoba, Corrientes, Paraná, Formosa, San Salvador de Jujuy, Santa Rosa, La Rioja, Mendoza, Posadas, Neuquén, Viedma, Salta, San Juan, San Luis, Río Gallegos, Santa Fe, Santiago del Estero, Ushuaia, San Miguel de Tucumán; Buenos Aires (the city).

## Names matching

- **Buenos Aires Province vs the City of Buenos Aires:** typing "Buenos Aires" counts for the province (the bigger one); the city needs "City of Buenos Aires", "CABA", "Ciudad de Buenos Aires" or "Capital Federal". (Decided here; checked in the morning review.)
- Short forms for capitals: Catamarca, Jujuy, Tucumán, Santiago.
- Accents optional.

## Tiny parts

A circle for **the City of Buenos Aires** (decided 2026-11-17); Tucumán is the smallest province but big enough.

## Flags (games 5 and 6)

Flag games for all 24.

## Learning card

Name, kind, capital, population (2022 census), area and rank of 24, flag. **More facts (18, chosen 2026-11-17):** demonym; region; famous food; drink; music or dance; biggest festival; Indigenous peoples; football: biggest club; highest point; main river or lake; natural wonder or national park; climate; famous animal; became a province (1853 founder or former national territory); UNESCO World Heritage; famous person from there; known for; largest city if it isn't the capital.

## Layers and timeline

- No layer.
- **Timeline: to discuss** (morning agenda, 2026-11-18).

## Build order

1. `tools/build_ar.py`, `tools/ar_facts.py`.
2. Map, loader, card, stats tab, "Focus on Argentina".
3. Tests (the build job's checklist).
4. Timeline, once decided.

## Open questions for the user

- The timeline (morning agenda).
