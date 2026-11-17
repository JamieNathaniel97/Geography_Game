# India – Plan

The brief for India's country map in Gaia Quest. It comes after the US and Canada, and follows the same pattern as Canada (see "Canada (built 2026-11-16)" in [PLAN.md](PLAN.md)). Drafted 2026-11-17. Nothing is built yet. **Open questions** are at the end and need the user's decision before building.

## What's on the map

India has **28 states and 8 union territories (UTs)**. That's 36 parts in all, and the count hasn't changed since the 2020 UT merger.

- **States (28):** Andhra Pradesh, Arunachal Pradesh, Assam, Bihar, Chhattisgarh, Goa, Gujarat, Haryana, Himachal Pradesh, Jharkhand, Karnataka, Kerala, Madhya Pradesh, Maharashtra, Manipur, Meghalaya, Mizoram, Nagaland, Odisha, Punjab, Rajasthan, Sikkim, Tamil Nadu, Telangana, Tripura, Uttar Pradesh, Uttarakhand, West Bengal.
- **Union territories (8):** Andaman and Nicobar Islands, Chandigarh, Dadra and Nagar Haveli and Daman and Diu, Delhi, Jammu and Kashmir, Ladakh, Lakshadweep, Puducherry.
- The unit word (`unit` in COUNTRY_MAPS) is **"States & UTs"**. The New game page reads Find: States & UTs, Capitals; Name: States & UTs, Capitals.
- Like Canada, each part has a `kind`: "State" or "Union territory". The Learning card shows it.
- A **toggle before each game, "States only (28)" or "States & UTs (36)"**, defaulting to all 36. The counter follows the choice.

## Wiring it into the app

- `COUNTRY_MAPS`: `IND: { name: "India", focus: "India", cont: "Asia", unit: "States & UTs", data: "in", region: "india" }`. This makes it the first country map under the Asia heading in the Countries tab.
- `isCountryMap`, `geoFor`, the region button label ("Whole India") and the stats tab label ("States") in `app.js` all get an `"in"` branch, as `"ca"` did. If adding a third or fourth branch gets messy, move these per-country details into COUNTRY_MAPS itself.
- `geo.js`: a loader for `data/in-states.json` + `data/in-parts.json`, the same shape as the Canada loader (kind `"in"`).
- "Focus on India ›" button on the world Learning map.
- Bump `CACHE` in `sw.js`, and add the new data files to the offline list.

## Data build: `tools/build_in.py`

Same layout as `tools/build_ca.py`:

- `data/in-states.json`: the 36 shapes, with the neighbours (Pakistan, China, Nepal, Bhutan, Bangladesh, Myanmar, Sri Lanka) as grey context areas. Border and coast lines are worked out in advance.
- `data/in-parts.json`: names, alternative names, capitals and Learning facts, hand-written in the script.
- **Shape source:** the shapes must show the current map: the 2019 split of J&K and Ladakh, and the 2020 merger of Dadra and Nagar Haveli with Daman and Diu. Natural Earth's admin-1 file may still show the old J&K and the two separate UTs, so check it first. If it's out of date, use geoBoundaries ADM1 (open licence, credit it on the map) or fix the shapes by hand in the build script. Check the licence before bundling.
- **Projection:** Lambert conformal conic, standard parallels about 12°N and 28°N, centred near 80°E.

## Capitals (games 3 and 4 equivalents)

Most parts have one capital. These need care. **Decided 2026-11-17: confirm every multiple or seasonal capital against an up-to-date source during the build** (the table below is a starting list, not final). Assam's capital is **Dispur** only.

| Part | Accept |
| --- | --- |
| Maharashtra | Mumbai (also Nagpur, winter session) |
| Himachal Pradesh | Shimla (also Dharamshala, winter) |
| Uttarakhand | Dehradun (also Gairsain/Bhararisain, summer) |
| Jammu and Kashmir | Srinagar (summer), Jammu (winter) |
| Ladakh | Leh (also Kargil) |
| Andhra Pradesh | Amaravati. Check the current status before building, because it has changed more than once. |
| Karnataka | Bengaluru / Bangalore |
| Punjab, Haryana, Chandigarh | Chandigarh is the capital of all three. A dark red dot is shown once for each. |
| Dadra and Nagar Haveli and Daman and Diu | Daman |
| Delhi | New Delhi / Delhi |
| Andaman and Nicobar | Sri Vijaya Puram (renamed from Port Blair in 2024), and Port Blair is also accepted |

Old city names are also accepted, unlike former country names, because people still use them every day: Bombay, Madras, Calcutta, Bangalore, Trivandrum (Thiruvananthapuram), Pondicherry. Spell "Thiruvananthapuram" forgivingly. It's long, so the one-typo rule matters.

## Names matching

- "and" / "&": "Jammu & Kashmir", "Andaman & Nicobar".
- Short forms: UP, MP, AP, HP, J&K, TN, WB, NCT / National Capital Territory (Delhi).
- Old names: Orissa (Odisha), Pondicherry (Puducherry), Uttaranchal (Uttarakhand). Accept them, with a spelling note like the one game 2 shows.
- "Dadra and Nagar Haveli and Daman and Diu" is long. Accept "DNHDD", "Dadra and Nagar Haveli", "Daman and Diu" or "Daman".

## Tiny parts

Using the world map's tools (ovals, 8 px rings, adaptive circles like Prince Edward Island's):

- **Island ovals:** Lakshadweep (one oval), Andaman and Nicobar Islands (a long oval following the chain, or two lobes like Kiribati: Andamans to the north, Nicobars to the south).
- **Scattered pieces:** Puducherry has four separate enclaves (Puducherry and Karaikal on the Tamil Nadu coast, Mahé in Kerala, Yanam in Andhra Pradesh). Draw small rings around all four, so any of them counts as tapping Puducherry. DNHDD has three pieces (Dadra and Nagar Haveli, Daman, Diu), which get the same treatment.
- **Adaptive circles:** Chandigarh, Delhi, Goa. Sikkim and Tripura are probably large enough, but check this on the phone.
- Minimum shape size 8 px as elsewhere.

## Flags

**Indian states and UTs have no official flags.** J&K's flag was dropped in 2019. Games 5 and 6 (Find by flag, Name the flags) **don't apply**. The country page just leaves the Flags buttons out. The planned British counties map already leaves out counties with no registered flag, so this does the same.

Possible stand-ins (open question): state emblems, or a "Find by official language" game.

## Learning mode card

Same layout as the Canada province card:

- Name, kind (state / UT), region (North, Northeast, East, Central, West, South, Islands), capital(s) with what each is for.
- Population: **2011 census** is the latest published count. The 2027 census is under way, so update the figures when it's published, and label the year on the card as Canada does ("2011 census").
- **More facts:** largest city (when it isn't the capital), official language(s), area (km² and sq mi, rank of 36), highest point, year formed (with what it was split from), name origin, and state animal, bird, flower and tree.
- Coast or landlocked, and which countries it borders (useful for India, since many states sit on an international border).

## Timeline (later, after the basic games)

India's map changed by **splitting and redrawing**, not by new areas joining like the US states. So the US-style slider needs a set of historical shapes, not just one year per part. Key years: 1950 (Part A/B/C/D states), 1956 (States Reorganisation Act), 1960 (Bombay → Maharashtra and Gujarat), 1961 (Goa joined), 1963 (Nagaland), 1966 (Punjab → Punjab, Haryana, Himachal), 1971–72 (northeast states), 1975 (Sikkim), 1987 (Goa, Mizoram, Arunachal become states), 2000 (Chhattisgarh, Uttarakhand, Jharkhand), 2014 (Telangana), 2019 (J&K and Ladakh), 2020 (DNHDD). This is a big data job. Build it after the games, and only if the US timeline works well.

## Layer ideas (Learning mode only, like Reservations)

- Tiger reserves / national parks.
- Official languages, as a colour layer. The US plan turned down "colouring by topic", so ask first.

## Build order

1. `tools/build_in.py`: shapes, parts data, capitals; check the shapes are current.
2. Map and loader (`geo.js`, projection, grey neighbours, lakes as on the world map).
3. Find and Name: States & UTs, then Capitals.
4. Tiny-part handling (island ovals, enclave rings, Chandigarh/Delhi/Goa circles).
5. Learning card + "Focus on India".
6. States-only toggle, stats, personal bests (reuse the Canada code paths).
7. Later: timeline, layers.

## Open questions for the user

1. **Disputed borders:** which line to draw for Jammu and Kashmir and Ladakh? Options: (a) India's official claimed boundary (the whole of Kashmir including Pakistan- and China-administered areas, which is the map required in India); (b) the de facto Line of Control, with the claimed areas hatched or grey; (c) both, with a toggle. The world map's choice should also be checked so the two maps agree. Arunachal Pradesh (claimed by China) raises the same question.
2. **UTs:** include all 8 by default (36 total), or default to the 28 states?
3. **Flags:** leave the flag games out, or use something in their place (emblems, languages)?
4. Should India come **before the United Kingdom**, which is marked "soon"?
