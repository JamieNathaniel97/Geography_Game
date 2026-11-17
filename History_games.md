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

1. A person comes up at the top, for example **"Napoleon Bonaparte · French emperor · 1769–1821"**. The years are always shown (decided 2026-11-17).
2. **The map zooms into the area** where the person lived (see "Zooming" below).
3. **First tap: the birth place guess.** A **green dot** appears where the user tapped.
4. **Second tap: the death place guess.** A **red dot** appears.
5. **The real places appear:** a **baby symbol** at the real birth place and a **skull symbol** at the real death place, each labelled with the place name and year ("Ajaccio, 1769", "Saint Helena, 1821"). A thin line joins each guess to the real place, with the distance ("212 km away").
6. The map zooms out just enough to show all four marks, then a "Next ›" button moves on.

- **Scoring (decided 2026-11-17): each round is worth up to 100 points**, so a 10-round game is out of **1,000**. A place's score is **100** within 20 km, and **1** means the opposite side of the Earth (20,000 km away). In between, the score falls on a log scale, so being close matters most:

  `score = 100 − 99 × log(d / 20) / log(1000)`, rounded, where d is the distance in km (100 at 20 km or less, 1 at 20,000 km)

  | Distance | 20 km | 50 km | 100 km | 200 km | 500 km | 1,000 km | 2,000 km | 5,000 km | 10,000 km | 20,000 km |
  | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
  | Score | 100 | 87 | 77 | 67 | 54 | 44 | 34 | 21 | 11 | 1 |

  Each person gets two place scores (birth and death), shown next to the symbols, and **the round's score is their average** (out of 100). The running total builds up round by round: after 3 rounds a player might have 240, and a perfect fourth round adds 100. The end-of-game pop-up shows the total (out of 100 × the number of rounds: 1,000 for 10, 5,000 for 50), the average per round, the average distance, and the best and worst guesses. Personal bests use the total for the 10, 20 and 50 lengths, and the average per round for Marathon.
- **Symbols:** drawn as small SVG icons (a baby's face, a skull), not emoji, so they look the same on every phone and work offline.
- Taps on the sea count (people die at sea, and coastal towns need taps near the shore).
- Back and forward arrows, Give up and the timer work as in the other games.

### Game H1b: Who is it?

The other way round:

1. The map shows the **baby symbol** at the birth place and the **skull symbol** at the death place, with the place names and years: "👶 Ajaccio, 1769 → 💀 Saint Helena, 1821".
2. The map zooms to fit both.
3. The user guesses the person (open question 5 on how).
4. Right: the person's card appears (name, description, years, places, and a portrait if there's a free one). Wrong or Give up: the answer is shown.

- **Answering (decided 2026-11-17): both ways, as a setting** in Options: **Type the name** (forgiving matching; surnames and well-known short names count, such as "Napoleon", "Einstein", "Gandhi") or **4 choices** (the other three are people of the same kind and era, so it isn't too easy).

### Zooming

- **H1a:** before the taps, the map zooms to the area that holds both real places, with a generous, slightly random margin so the frame doesn't give the answer away. For someone who stayed in one country (Shakespeare), that's about the size of a country or region; for someone who travelled far (Napoleon, from Corsica to Saint Helena), it's much wider. If the frame would be smaller than a minimum size (about 1,500 km across), it's widened to that.
- **H1b:** zoom to fit the two symbols, with a margin.
- Smooth zooms (turn and zoom together), like the Learning mode clip.

### Choosing people

Before each game, like Region:

- **Kind:** All, Leaders, Scientists and inventors, Artists and architects, Writers and poets, Composers and musicians, Philosophers, Explorers.
- **Era:** All, Ancient (before 500), Medieval (500–1500), Early modern (1500–1800), 1800s, 1900s and later.
- **Region:** the usual continents, by where the person was born.
- **Length (decided 2026-11-17):** a choice of **10, 20 or 50** people, or **Marathon**: the whole chosen set. "Marathon" is the app's name for "every item in the chosen set", to be used for the same option in other games too (PLAN.md).

### Data

- **Source: Wikidata**, which is CC0 (public domain), so there are no licence worries. Credit it on the map anyway.
- **Script written:** `tools/build_people.py` writes `data/people.json`: each person's name, short description, kind, birth and death years (BC as negative), birth and death places with coordinates, the modern country of each place, and how famous they are (the number of Wikipedia languages with an article about them). Only people who have died are included, since the game needs a death place.
- **Hand-picked people (decided 2026-11-17):** `tools/people_extra.py` holds **174 hand-picked people** to balance the set: leaders, thinkers, artists and scientists from Africa, the Middle East, South Asia, East and Southeast Asia, Latin America, Indigenous North America and Oceania, and women from Europe and North America. They're always included whatever their fame score, marked `"picked": true`. The script prints any title it can't find in Wikidata; fix those in the file. Add more freely: it's just a list of English Wikipedia article titles.
- **Not run yet:** the sandbox this plan was written in can only reach GitHub, so it couldn't download from Wikidata. **Run the script in VS Code**: `python tools/build_people.py 100`. The number is the fame cut-off (people with articles in at least 100 languages); lower it for more people. The first try will show how many people that gives; somewhere around 500 to 1,500 is a good size.
- **Check by hand** before shipping. The script prints people with several birth or death places, and places with no modern country (at sea, ancient sites). Fix them in its `FIXES` table. Some birthplaces in Wikidata are a country or region rather than a town, which would make a bad answer; drop or fix those.
- **Old places:** use the place's position, not old borders. The card can show the old name and the modern country ("Königsberg, Prussia (now Kaliningrad, Russia)").
- **Fairness:** Wikipedia fame leans towards European men, which is why the hand-picked list exists. After the first run, check the spread by region, era and kind, and add to the list where it's thin.
- **Pictures (decided 2026-11-17: yes, if free):** `python tools/build_people.py 100 --images` also downloads a small portrait (240 px wide, WebP) for each person whose Wikidata picture has a **free licence**, checked file by file with the Wikimedia Commons API: public domain, CC0, CC BY or CC BY-SA. Pictures go in `data/people/<id>.webp`, and each record keeps the credit and licence, which the card shows in small print under the picture (CC BY and CC BY-SA require it). People with no free picture (many 20th-century photos) just have no picture. At about 10 KB each, 1,000 portraits is about 10 MB, so load them only when a card opens, and let the offline cache keep the ones that have been seen, rather than bundling them all at install.

### Open questions for the user (H1)

None at the moment (all answered 2026-11-17). Run `tools/build_people.py` in VS Code and check the results by hand first.

---

## H2: Famous battles

Famous battles from every era, from Kadesh (about 1274 BC) to the late 20th century, on land and at sea. Same idea as H1. Added 2026-11-17.

### Game H2a: Where was it fought?

1. A battle comes up at the top with its year: **"Battle of Hastings · 1066"**.
2. **No zooming in** (decided 2026-11-17): the map stays on the whole chosen region (the world, or a continent), so the user has to know where it was. They can still pinch to zoom themselves.
3. **One tap:** a dot appears where the user tapped.
   - **Hint button:** tapping **Hint** before answering zooms the map to the general area (the same frame as H1a: the real place inside a generous, slightly random margin, at least about 1,500 km across). The round's score is then **halved**: a perfect answer earns 50 instead of 100 (it's half of whatever the tap scores, not a cap on the game). The round shows a small "hint" mark.
4. **The real place appears** as a **crossed-swords symbol** (an **anchor** for naval battles), labelled with the place and year, with a line from the tap and the distance.
5. **Score: up to 100 per round**, the same distance formula as H1 (100 within 20 km, 1 at 20,000 km), so a 10-battle game is out of 1,000. With a hint, the round's score is halved (a perfect answer earns 50). Example: a player on 300 after three rounds can reach 400 with a perfect fourth answer, or 350 if they used the hint.

**Big-area battles** (decided 2026-11-17): battles fought over a large area (the Battle of Britain, Gallipoli, Normandy, Kursk, Midway and others, listed in `AREAS` in `tools/battles_extra.py`) are **shapes, not points**. When the answer is shown, the whole area is highlighted, like a country highlight. A tap anywhere inside scores the full 100; outside, the score uses the distance to the nearest edge of the area.

### Game H2b: Which battle was it?

1. The symbol appears on the map at the battle's place, with the year: **"⚔ 1815"**. Big-area battles show their highlighted area instead.
2. **The map zooms in** to fit it (decided 2026-11-17: H2b zooms, H2a doesn't), with enough around it to recognise where it is.
3. The user names the battle: **type the name or pick from 4 choices**, the same setting as H1b. The wrong choices are battles from a similar time and region. Typing is forgiving: "Waterloo" counts for "Battle of Waterloo", "Battle of" is optional, and so are "First" and "Second" where only one battle has that name in the set.
4. The answer card shows the name, year, the war it was part of, a short description, **the sides and who won** (decided 2026-11-17). Where Wikidata has no winner, or the result was unclear, the card says "Inconclusive" or leaves the line out; don't guess.

### Choosing battles

Like H1, before each game:

- **Kind:** All, Land, Naval, **Sieges** (decided 2026-11-17: sieges are included; "All" mixes all three).
- **Era:** All, Ancient (before 500), Medieval (500–1500), Early modern (1500–1800), 1800s, 1900–1945, After 1945.
- **Region:** the usual continents, plus **At sea** for naval battles away from any coast.
- **War** (idea): a filter for the big wars with many battles in the set, such as the Napoleonic Wars, the American Civil War, the First and Second World Wars.
- **Length:** 10, 20, 50 or Marathon, as in H1.

### Symbols (decided 2026-11-17)

- **Crossed swords** for land battles and sieges, an **anchor** for naval battles, as small SVG icons.

### Naval battles

- Included (decided 2026-11-17). Their places are at sea, so taps on the sea count, and the map shows enough coast to give a sense of where it is.
- Many naval battles only have a rough position. The card says "approximate" where Wikidata gives no exact one.

### Data

- **Source: Wikidata** (CC0), like H1.
- **Script written:** `tools/build_battles.py` writes `data/battles.json`: name, short description, start and end years (BC as negative), position, the modern country (none at sea), whether it was naval or a siege, the war it was part of, and the fame score. **Run it in VS Code:** `python tools/build_battles.py 40` (battles with articles in at least 40 Wikipedia languages; change the number to get more or fewer).
- **Hand-picked battles:** `tools/battles_extra.py` holds **141 hand-picked battles** across every era and region: Kadesh, Gaugamela, Red Cliffs, Talas, Ain Jalut, Panipat, Sekigahara, Myeongnyang, Ayacucho, Adwa, Isandlwana, Tsushima, Kohima, Dien Bien Phu, Cuito Cuanavale and many more. They're always included. The script prints any title it can't find.
- **Cut-off (decided 2026-11-17):** the set ends in **1993** (`MAX_YEAR` in the script), where the hand-picked list ends. Nothing from wars still being fought.
- **Sides and winners:** the script also fetches who fought and who won. Wikidata is patchy here: it prints how many battles have none, and the important ones should be filled or fixed in its `FIXES` table.
- **Area shapes (decided 2026-11-17: an action item for the build):** drawing the big-area shapes is **a task in the H2 build**, not something to leave for later. Each battle in `AREAS` gets a hand-drawn, simplified shape in `tools/battle_areas.geojson` (one feature per battle, with its title), drawn from historical maps of where the fighting happened. The build script lists the ones still missing, and H2 isn't finished until that list is empty.
- **Check by hand:** the script also lists battles with no country, which it counts as naval; check them. Ancient battles' places are sometimes disputed (Kadesh, Teutoburg Forest); use the most accepted place, and say so on the card.

### Build order (H2)

1. Run `tools/build_battles.py` and fix the hand-picked titles it can't find.
2. **Draw the big-area shapes** in `tools/battle_areas.geojson` for every battle in `AREAS`, and re-run the script until none are missing.
3. Check sides and winners for the hand-picked battles, and fill gaps in `FIXES`.
4. H2a (tap the place, Hint button, area highlighting and scoring), then H2b (name it, with typing and 4 choices).
5. Filters (kind, era, region, war) and lengths.

### Open questions for the user (H2)

None at the moment (all answered 2026-11-17). Still to decide later: whether H1a (people) should also stop zooming in and get the same Hint button, to match H2a.
