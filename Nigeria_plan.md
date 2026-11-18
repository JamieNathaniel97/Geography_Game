# Nigeria – Plan

The brief for Nigeria's country map in Gaia Quest, the first map for Africa, in the same pattern as the built country maps (see [PLAN.md](PLAN.md)) and the build job ([jobs/build_countries.md](jobs/build_countries.md), with the checklist every build follows). Drafted 2026-11-18 from the decisions of 2026-11-17. **Open questions** are at the end.

## What's on the map

- **36 states and the Federal Capital Territory** (Abuja): 37 parts.
- `kind`: State, or Federal Capital Territory.
- `unit` word: **"States"**. Grey context: Benin, Niger, Chad, Cameroon (and the Bakassi peninsula, Cameroonian since 2008), with the Gulf of Guinea to the south.

## Wiring

`COUNTRY_MAPS.NGA`: `{ name: "Nigeria", focus: "Nigeria", cont: "Africa", unit: "States", data: "ng", region: "nigeria" }`. Loader `GG.loadNG`; `DATASETS.ng` with **`noFlags: true`** (games 5 and 6 shelved). Projection: **Lambert conformal conic**, standard parallels 6°N and 12°N, centre 8°E.

## Data build: `tools/build_ng.py`

- Shapes: Natural Earth admin-1 (37, complete); **detail level** from `tools/downloads/ng/coast_f.geojson` (the Niger Delta's creeks).
- Population: the **2006 census** (the last full count; the card says so); check against the national total.

## Capitals

Umuahia, Yola, Uyo, Awka, Bauchi, Yenagoa, Makurdi, Maiduguri, Calabar, Asaba, Abakaliki, Benin City, Ado Ekiti, Enugu, Gombe, Owerri, Dutse, Kaduna, Kano, Katsina, Birnin Kebbi, Lokoja, Ilorin, Ikeja (Lagos), Lafia, Minna, Abeokuta, Akure, Osogbo, Ibadan, Jos, Port Harcourt, Sokoto, Jalingo, Damaturu, Gusau; Abuja (FCT).

## Names matching

- "State" optional: "Lagos" counts for Lagos State. "FCT", "Abuja", "Federal Capital Territory".
- Capitals: Ikeja is Lagos State's capital, and typing "Lagos" also counts (the city most people know); Benin City / Benin; Port Harcourt / PH.
- At the build, list every pair of state names (and capitals) one letter apart and add them to `notTypo`, so neither counts for the other.

## Tiny parts

Circles if needed for the small states: Lagos (the smallest by area), Anambra, Imo, Ebonyi; check on the phone.

## Flags (games 5 and 6)

**None for now** (2026-11-17): state flags are mostly unofficial, and the **seal games are shelved** (many seals aren't freely licensed). Like France, no games 5 and 6 and no Flags stats tab.

## Learning card

Name, kind, capital, population (2006 census), area and rank of 37. **More facts (17, chosen 2026-11-17):** nickname (the number-plate slogan); main ethnic groups; main languages; main religions; famous dish; biggest festival; traditional ruler; main river; climate or vegetation; highest point; natural wonder or park; created (year) and from which state; old kingdom or empire; UNESCO World Heritage; known for; largest city if it isn't the capital; famous person from there.

## Layers and timeline

- No layer.
- **Timeline: to discuss** (morning agenda, 2026-11-18). The idea: how the states were split, 1967 (12) → 1976 (19) → 1987 (21) → 1991 (30) → 1996 (36), which suits this map well since the splits follow today's borders.

## Build order

1. `tools/build_ng.py`, `tools/ng_facts.py`.
2. Map, loader, card, stats tab, "Focus on Nigeria".
3. Tests (the build job's checklist).
4. Timeline, once decided; seal games, if their licences allow.

## Open questions for the user

- The timeline (morning agenda).
- The seal games (shelved: check licences first).
