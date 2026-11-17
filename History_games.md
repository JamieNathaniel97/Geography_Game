# History games – Ideas and plans

Games about history, in a new **History** tab of the New game menu. Each idea has a number (H1, H2 and so on). Started 2026-11-17. Nothing is built yet. **Open questions** are at the end of each idea.

## The History tab

- The New game menu's tabs become **Game | History | Learning mode**.
- The History tab lists the history games, with the same setup fields as the Game tab (region, Options for the timer).
- Later, the timelines already in the app (US statehood, Canada, Australia's colonies, Russia's expansion and decline) could also be reached from here, as "Timelines", as well as from their Learning maps.

---

## H1: Historical figures

Famous people from history (leaders, scientists, artists, writers, composers, philosophers, explorers and more), and where they were born and died.

### Game H1a: Where were they born and where did they die?

1. A person comes up at the top, for example **"Napoleon Bonaparte · French emperor"**, with their years (open question 4).
2. **The map zooms into the area** where the person lived (see "Zooming" below).
3. **First tap: the birth place guess.** A **green dot** appears where the user tapped.
4. **Second tap: the death place guess.** A **red dot** appears.
5. **The real places appear:** a **baby symbol** at the real birth place and a **skull symbol** at the real death place, each labelled with the place name and year ("Ajaccio, 1769", "Saint Helena, 1821"). A thin line joins each guess to the real place, with the distance ("212 km away").
6. The map zooms out just enough to show all four marks, then a "Next ›" button moves on.

- **Scoring:** nobody can tap an exact town, so it scores by distance, like GeoGuessr: for example up to 100 points for each place, falling the further away the tap was (100 points within 25 km, 0 beyond 2,000 km). The end-of-game pop-up shows the total, the average distance and the best and worst guesses.
- **Symbols:** drawn as small SVG icons (a baby's face, a skull), not emoji, so they look the same on every phone and work offline.
- Taps on the sea count (people die at sea, and coastal towns need taps near the shore).
- Back and forward arrows, Give up and the timer work as in the other games.

### Game H1b: Who is it?

The other way round:

1. The map shows the **baby symbol** at the birth place and the **skull symbol** at the death place, with the place names and years: "👶 Ajaccio, 1769 → 💀 Saint Helena, 1821".
2. The map zooms to fit both.
3. The user guesses the person (open question 5 on how).
4. Right: the person's name, description and photo-free card appear. Wrong or Give up: the answer is shown.

### Zooming

- **H1a:** before the taps, the map zooms to the area that holds both real places, with a generous, slightly random margin so the frame doesn't give the answer away. For someone who stayed in one country (Shakespeare), that's about the size of a country or region; for someone who travelled far (Napoleon, from Corsica to Saint Helena), it's much wider. If the frame would be smaller than a minimum size (about 1,500 km across), it's widened to that.
- **H1b:** zoom to fit the two symbols, with a margin.
- Smooth zooms (turn and zoom together), like the Learning mode clip.

### Choosing people

Before each game, like Region:

- **Kind:** All, Leaders, Scientists and inventors, Artists and architects, Writers and poets, Composers and musicians, Philosophers, Explorers.
- **Era:** All, Ancient (before 500), Medieval (500–1500), Early modern (1500–1800), 1800s, 1900s and later.
- **Region:** the usual continents, by where the person was born.
- Each game is 10 people (open question 2).

### Data

- **Source: Wikidata**, which is CC0 (public domain), so there are no licence worries. Credit it on the map anyway.
- **Script written:** `tools/build_people.py` writes `data/people.json`: each person's name, short description, kind, birth and death years (BC as negative), birth and death places with coordinates, the modern country of each place, and how famous they are (the number of Wikipedia languages with an article about them). Only people who have died are included, since the game needs a death place.
- **Not run yet:** the sandbox this plan was written in can only reach GitHub, so it couldn't download from Wikidata. **Run the script in VS Code**: `python tools/build_people.py 100`. The number is the fame cut-off (people with articles in at least 100 languages); lower it for more people. The first try will show how many people that gives; somewhere around 500 to 1,500 is a good size.
- **Check by hand** before shipping. The script prints people with several birth or death places, and places with no modern country (at sea, ancient sites). Fix them in its `FIXES` table. Some birthplaces in Wikidata are a country or region rather than a town, which would make a bad answer; drop or fix those.
- **Old places:** use the place's position, not old borders. The card can show the old name and the modern country ("Königsberg, Prussia (now Kaliningrad, Russia)").
- **Fairness:** Wikipedia fame leans towards European men. When choosing the cut-off, check the spread by region and era, and add a hand-picked list of important people from elsewhere if the set is lopsided (open question 3).

### Open questions for the user (H1)

1. **Scoring by distance:** points falling with distance, as above, or just "close enough" (green within some distance, red beyond)?
2. **How many people per game:** 10, 20, or the whole chosen set?
3. **Hand-picked extras:** add a hand-picked list to balance the set, or use Wikidata's fame ranking alone?
4. **H1a prompt:** show the years (helps a lot) or only the name and description?
5. **H1b answer:** type the name (forgiving matching, accepting surnames such as "Napoleon" or "Einstein"), or pick from 4 choices, or both as a setting?
6. **Pictures:** show a portrait on the answer card? Paintings of people who died long ago are mostly public domain (Wikimedia Commons), but photos of 20th-century people often aren't. **Proposed:** no pictures to start with.
