# Job: Misc games (idea_01: airport codes)

Building the airport codes games planned in [Misc_games.md](../Misc_games.md). Added 2026-11-17. **Shelved (2026-11-17): don't build anything, not even the Find game, until the open questions below are discussed on the morning agenda** ([README.md](README.md)).

## Where it goes in the menu (changed 2026-11-17)

The plan's "Misc group on the Game tab" is **replaced** by the user's newer instruction: the **"More games"** menu's **Misc** column ([README.md](README.md), "Coming soon"). That menu change waits for the user's go-ahead; until the airport games are built, they show there as "soon".

## Data (already built)

`data/airports.json` (`tools/build_airports.py`, from OurAirports, public domain; credit it anyway): 3,268 airports with scheduled passenger flights and an IATA code, including Ukraine's 23 (flights suspended since 2022, marked `"suspended": true`, played like any other) and Crimea's under Ukraine. Load it only when an airport game starts.

**Still to do in the data:**
- The `SERVES` corrections: airports listed under their own town rather than the city they serve (Narita → Tokyo, Boryspil → Kyiv…), checked for every airport in the chosen sets.
- English city names where the source uses the local one (Munich, Rome, Lisbon).

## The games

| Game | Prompt | Answer |
| --- | --- | --- |
| Find the airport | a code ("LHR") | tap its dot (green if right; if wrong the right dot goes red, like game 1) |
| Name the city from the code | a code, its dot highlighted | type the city ("London") |
| Name the code from the city | "London Heathrow", its dot highlighted | type the code ("LHR") |

- Codes must match **exactly** (one letter is a different airport: LHR / LGW); city names use the usual forgiving matching.
- Back and forward arrows, Give up, the timer, stats, personal bests, Knowledge gaps for the Find game.
- **The map:** the world globe and flat map with a dot per airport in the chosen set, countries in a quiet colour as the background; region filter (the usual continents); the Magnifier works.
- **Close dots** (several airports in one city): the plan suggests numbered bubbles that split as you zoom in. Russia's bubble was removed by the user on 2026-11-17, so **check with the user** whether to use bubbles here or circles that separate as you zoom.
- **Sets:** build them so a set is just a list of codes (adding a set is adding a list, not code). Suggested: Top 50 busiest (ACI World ranking, hand-written), Top 100, capital cities, by country, all large airports.

## Open questions (ask before building these parts)

1. **Which sets** of airports (kept flexible: a starter set of Top 50 busiest is the plan's suggestion).
2. **Name games:** one prompt at a time, Sporcle-style (tap any dot and type), or both?
3. **Cities with several airports:** add the city codes (LON, NYC, TYO)?
4. **Learning mode** for airports (tap a dot for a card): yes or later?

5. **Close airports** (several in one city): numbered bubbles, or circles that separate as you zoom?

All five are on the morning agenda; nothing here is built until they're answered.

## Tests (all must pass)

- A full Find game on the Top 50 set: each code finds its dot; close dots in London, New York and Tokyo are tappable; wrong taps show the right dot.
- Codes are exact (LGW doesn't count for LHR); city names accept their English and local forms.
- The country games and Learning mode still work; no script errors. Credit OurAirports in the app.

Push only when the user says so, or as an overnight job list explicitly allows.
