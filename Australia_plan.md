# Australia – Plan

The brief for Australia's country map in Gaia Quest. It follows the same pattern as the other country maps (see [PLAN.md](PLAN.md) and the India, China and Russia plans). Drafted 2026-11-17. Nothing is built yet. **Open questions** are at the end and need the user's decision before building.

## What's on the map

- **States (6):** New South Wales, Queensland, South Australia, Tasmania, Victoria, Western Australia.
- **Mainland territories (2):** Australian Capital Territory, Northern Territory.
- **Jervis Bay Territory:** a tiny separate territory on the New South Wales coast, run by the federal government. **Proposed:** tappable as its own part (with a circle), or part of the ACT (open question 1).
- **External territories:** Norfolk Island, Christmas Island, Cocos (Keeling) Islands, Ashmore and Cartier Islands, Coral Sea Islands, Heard Island and McDonald Islands, and the Australian Antarctic Territory. **Proposed:** a toggle, "External territories", off by default (open question 2). When on, the inhabited ones (Norfolk, Christmas, Cocos) get island ovals and insets. Ashmore Reef is already a grey territory on the world map.
- With 8 main parts this is the smallest country map, so the games are quick. That's fine; it's good practice.
- `unit` word: **"States & territories"**.

## Wiring it into the app

- `COUNTRY_MAPS`: `AUS: { name: "Australia", focus: "Australia", cont: "Oceania", unit: "States & territories", data: "au", region: "australia" }`. It's the first map under the Oceania heading.
- The usual branches (or COUNTRY_MAPS fields): `isCountryMap`, `geoFor`, region button ("Whole Australia"), stats label, Focus button.
- `geo.js` loader for `data/au-states.json` + `data/au-parts.json`. Bump `CACHE` in `sw.js`.

## Data build: `tools/build_au.py`

- `data/au-states.json`: the shapes, with neighbours as grey context (Papua New Guinea, Indonesia, Timor-Leste, New Zealand if an inset is used), plus `borders` and `coast` lines.
- `data/au-parts.json`: names, capitals and Learning facts, hand-written.
- **Shape source:** Natural Earth admin-1 for the mainland, which is in good order. For the external territories, use Natural Earth admin-0 territory shapes.
- **Projection:** Albers equal-area conic, standard parallels 18°S and 36°S, central meridian 132°E (the usual one for maps of Australia).

## Capitals

| Part | Capital |
| --- | --- |
| New South Wales | Sydney |
| Victoria | Melbourne |
| Queensland | Brisbane |
| Western Australia | Perth |
| South Australia | Adelaide |
| Tasmania | Hobart |
| Northern Territory | Darwin |
| ACT | Canberra |
| Jervis Bay (if its own part) | none (no town big enough), so leave it out of the capitals games |
| Norfolk Island | Kingston |
| Christmas Island | Flying Fish Cove |
| Cocos (Keeling) Islands | West Island |

Confirm during the build, as for the other plans.

## Names matching

- Short forms: NSW, QLD, SA, WA, TAS, VIC, NT, ACT. The app's two-letter codes rule applies (they are well known in Australia).
- "Tassie" for Tasmania.
- "Australian Capital Territory" / "ACT" / "Canberra" (open question: should typing "Canberra" count as naming the ACT? **Proposed:** no, it's the capital).

## Tiny parts

- **ACT** is small inside New South Wales, so an adaptive circle.
- **Jervis Bay**, if tappable: a circle.
- **Tasmania** is big enough.
- External territories: island ovals.

## Flags (games 5 and 6)

**All 6 states and both mainland territories have official flags**, so the flag games work. Norfolk Island also has an official flag, and Christmas Island and Cocos have flags used locally (check status). Flags from Wikimedia Commons, built to `data/flags/au/`.

## Learning card

- Kind (State / Territory), capital, population (**2021 census**; the 2026 census results are due in 2027, so update then), area and rank.
- **More facts:** choose from the ideas below (open question 3).

## Layers (Learning mode only, like Reservations)

- **Aboriginal land:** native title areas and Indigenous Protected Areas from the National Native Title Tribunal (check the licence; it's usually CC BY, which means credit it on the map).
- The well-known AIATSIS map of Aboriginal language and nation areas doesn't allow storing copies without permission, the same issue as Native Land Digital in PLAN.md, so leave it out unless permission is given.

## Timeline (optional)

Australia's states started as **colonies split off from New South Wales**, a bit like the US statehood timeline. Key years: 1788 New South Wales, 1825 Van Diemen's Land (Tasmania), 1829 Western Australia (Swan River Colony), 1836 South Australia, 1851 Victoria, 1859 Queensland, 1901 Federation, 1911 Northern Territory and ACT. This could reuse the US timeline code (open question 4).

## Fact ideas for the user to choose from

**People and culture**
1. Nickname (Sunshine State for Queensland, Garden State for Victoria)
2. Main Aboriginal or Torres Strait Islander groups and languages
3. A famous food or drink (Barossa wine in SA, Tim Tams were made in NSW)
4. Sport: the main football code (AFL in Victoria, rugby league in NSW and Queensland)
5. Demonym (Queenslander, Tasmanian, Territorian, Sandgroper for WA)

**Land and nature**
6. Main river or water feature (Murray, Uluru's waterholes, Great Artesian Basin)
7. Climate type (tropical, desert, temperate)
8. Highest point (Mount Kosciuszko in NSW)
9. Time zone(s), including daylight saving (Queensland and WA don't use it)
10. A famous natural wonder or national park (Uluru, Great Barrier Reef, Kakadu, Cradle Mountain)
11. State animal, bird and flower (official emblems, like the US states)
12. A famous dangerous animal (saltwater crocodile in the NT)

**History and landmarks**
13. Year founded as a colony, and how (penal colony or free settlement)
14. UNESCO World Heritage Sites (Sydney Opera House, Great Barrier Reef)
15. Name origin (Victoria from Queen Victoria, Tasmania from Abel Tasman)
16. Car number plate slogan ("Queensland – Sunshine State")

**Economy**
17. Main industry or resource (iron ore in WA, coal in Queensland, wine in SA)
18. Largest city if it isn't the capital (Gold Coast, Newcastle, Alice Springs)

## Build order

1. `tools/build_au.py`: shapes, parts data, capitals, flags.
2. Map and loader (Albers projection, grey neighbours).
3. Find and Name: States & territories, Capitals, Flags.
4. Tiny parts (ACT and Jervis Bay circles), external territories toggle.
5. Learning card + "Focus on Australia".
6. Optional: Aboriginal land layer, colony timeline.

## Open questions for the user

1. **Jervis Bay Territory:** its own tappable part, or part of the ACT?
2. **External territories:** a toggle (off by default), always on, or left out?
3. **Facts:** which of the 18 ideas go on the card?
4. **Timeline:** add the colony timeline?
5. **Aboriginal land layer:** add it?
