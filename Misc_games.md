# Misc games – Ideas and plans

Games that aren't about countries, regions, capitals or flags. Each idea has a number (idea_01, idea_02 and so on), so they can be talked about and built in any order. Started 2026-11-17. Nothing here is built yet. Each idea has its own **open questions**.

---

## idea_01: Airport codes

Learn the three-letter IATA airport codes (LHR, JFK, DXB) and the cities they serve. First suggested on 2026-11-16 (PLAN.md, "Nice-to-haves"), as a follow-on from the state abbreviations idea.

### Games

| Game | Prompt | Answer |
| --- | --- | --- |
| **Find the airport** | a code, such as "LHR" | tap its dot on the map. One tap: green if right; if wrong, the right dot goes red, like game 1 |
| **Name the city from the code** | a code, with its dot highlighted on the map | type the city, such as "London" |
| **Name the code from the city** | a city and airport name, such as "London Heathrow", with its dot highlighted | type the code, "LHR" |

- The two Name games could also work Sporcle-style, like game 2: tap any dot and type its city or code, until every dot is green (open question 3).
- Same rules as the other games: back and forward arrows, Give up, the optional timer, stats, personal bests, and Knowledge gaps for the Find game.
- **Matching:** city names use the usual forgiving matching (accents, case, a typo in long names), with common English names accepted (Munich / München, Rome / Roma, Lisbon / Lisboa). Codes must be **exact**, with no typo allowed, because one wrong letter is a different airport (LHR / LGW).

### The map

- The world globe and flat map, with **a dot for each airport** in the chosen set. Countries are drawn in a quiet colour with borders, as a background.
- **Close dots:** many cities have several airports close together (London has six). Dots that would overlap when zoomed out join into one numbered bubble that splits as you zoom in, like the Lesser Antilles. The Magnifier works too.
- Region filter: the usual continents.
- **Learning mode (idea):** tap a dot for an airport card: code, full name, city, country (with flag), and whether it's the main airport for that city.

### Data (downloaded 2026-11-17)

- **Source:** [OurAirports](https://ourairports.com/data/), public domain, so no licence worries. Credit it on the map anyway.
- **Built:** `tools/build_airports.py` writes `data/airports.json`, every airport with **scheduled passenger flights and an IATA code**: **3,245 airports** (1,151 graded "large", 2,094 "medium"). Each record has the code, airport name, city, the app's country code, position, size and whether the city is its country's capital (188 airports, in 150 countries).
- The file is about 480 KB. The app should only load it when an airport game starts, and could ship a smaller file per set (see the sets below) so phones don't download all of it.
- **Countries with no airport in the data:** Andorra, Liechtenstein, Monaco, San Marino and Vatican City (no airports of their own), Palestine (no scheduled flights), and **Ukraine** (no scheduled flights since 2022, so OurAirports marks its airports as having none).
- **Fixes needed during the build:**
  - Some airports are listed under their own town, not the city they serve: Narita is "Narita", not Tokyo. The build needs a hand-written list of corrections (`SERVES = {"NRT": "Tokyo", "STN": "London", ...}`), checked for every airport in the chosen sets.
  - Bracketed details are already removed ("Paris (Roissy-en-France, Val-d'Oise)" → "Paris"); the original is kept as `cityFull`.
  - Check English city names (the source sometimes uses the local name).

### Which airports? (open question 1)

3,245 is far too many for one quiz. Possible sets, chosen before each game like the Region:

- **Top 50 busiest** (by passengers, from the latest ACI World ranking, hand-written into the build script). In 2025, Atlanta was the busiest, followed by Dubai and Tokyo Haneda. This is the best starter set.
- **Top 100 busiest.**
- **Capital cities:** the main airport of each country's capital (about 150 countries in the data; some capitals have several, so one per capital would need choosing).
- **By country:** for example all the UK's airports, or all the US's large airports, on the country maps. These could appear on a country's page in the Countries tab.
- **All large airports** (1,151), as an expert set.

### Where it goes in the menu (open question 2)

A new group on the Game tab, "Misc", under Find and Name, with the airport games in it. Later misc games (idea_02 and so on) join the same group.

### Open questions for the user

1. **Which sets** of airports? (Top 50, Top 100, capitals, by country, all large, or some of these.)
2. **Menu:** a "Misc" group on the Game tab?
3. **Name games:** one prompt at a time (as in the table), Sporcle-style (tap any dot and type), or both?
4. **Cities with several airports:** in "Name the code from the city", the prompt names the airport ("London Gatwick"), so there's one right answer. Should there also be the **city codes** that cover all a city's airports (LON for London, NYC for New York, TYO for Tokyo)?
5. **Learning mode** for airports: yes or later?
