# Job: optimise the app (a whole-code efficiency pass)

Make Gaia Quest leaner and faster **without changing what it does or how it looks**. Written 2026-11-28 with the user, for
whichever model does it (the user may give it to Fable, claude-fable-5-2). **Start only when the user says so.**

## The app in brief

A map quiz and learning app: plain JavaScript, no build step, no framework, hosted on GitHub Pages as an installable
web app (PWA) that works offline. Read `PLAN.md` and `jobs/README.md` first.

- `index.html`, `css/app.css`; scripts loaded in order: `js/splash.js`, `names.js`, `stats.js`, `geo.js` (loading
  the map data), `mapview.js` (the canvas map: globe and flat, drawing, zoom, taps), `earth.js` (Earth mode),
  `app.js` (everything else: games, menus, cards, Learning mode), `history.js` (History games), `tutorial.js`.
  `vendor/` has d3, topojson-client and d3-geo-projection. `js/quakes-live.js` is written but not loaded yet.
- `sw.js`: the service worker (offline cache). `data/`: the map data (94.5 MB, 2,424 files), built by the scripts in
  `tools/` from sources in `tools/downloads/` (git-ignored; not on your machine unless downloaded).
- Sizes now: `app.js` 2,493 lines, `mapview.js` 1,509, `earth.js` 475, `geo.js` 430, `history.js` 404.

## Rules

1. **Work on a branch** (`optimise`), never on `main`. Small commits, one idea each, with a message saying what
   changed and the numbers before and after. **Don't push or merge**: the user reviews and says "go".
2. **Run the tests after every change**: `python tests/run.py` (about 2 minutes; see `tests/README.md`). Nothing is
   committed while a test fails. Run `python tests/run.py --full` (about 30 minutes, every country map) before
   handing back, and after anything touching map data, `mapview.js` or `geo.js`.
3. **Don't update the baseline** (`tests/baseline.json`) to make a test pass. A metric may only change if the change
   is meant and explained (e.g. a timing that got faster is fine: it passes anyway).
4. **What must not change:** what the user sees (screens, maps, colours, labels, wording, card facts), how anything
   behaves (taps, games, scoring, menus, the back button, offline use), the data's content and its credits and
   licences, the job files' decisions. If an improvement would change any of these, **don't do it: list it as a
   question for the user** in the results.
5. **Keep the setup:** plain scripts with the `GG` namespace, no bundler, no new libraries or frameworks, no
   TypeScript, still served as static files from GitHub Pages. Keep the code's comment style (plain English saying why).
6. When unsure whether something is used (code, CSS, a data file), search the whole repo, including `tools/` and the
   job files, before removing it; if still unsure, leave it and list it.
7. Bump `CACHE` in `sw.js` once, at the end, if any cached file changed.

## Where the gains probably are (in order)

Measured 2026-11-28; check them yourself first.

1. **The offline cache (biggest, for phones).** On install, `sw.js` downloads **135 files, 35.7 MB** (every country
   map, the History data, 14 fonts, the Learning clip in four versions), then about 900 flags. **On every release** (each
   `CACHE` bump) it downloads all of it again (`cache: "reload"`), keeping only the terrain tiles. Ideas, safest first:
   - keep unchanged files between versions (e.g. a manifest of file hashes made by a small script in `tools/`, so
     only changed files are fetched): no change in behaviour, a much smaller update;
   - the Learning clip: only the version for the phone's theme and format, not all four (check `clipSource`);
   - caching country maps, History data and flags when first used instead of at install **would change offline
     behaviour** (an unopened map wouldn't work offline): ask the user (rule 4), don't do it.
2. **Data sizes.** The biggest files: `ru-regions.json` 1.8 MB, `tribal-au.json` 1.55, `cn-provinces.json` 1.48,
   `uk-historic.json` and `uk-ceremonial.json` 1.3 each, `tribal-ca.json` 1.25, `cl-states.json` 1.0, `se-states.json`
   0.9; the detail tiles 38 MB (761 files); flags 14 MB (904 files; Mexico's coats of arms alone 4.3 MB). Check the
   coordinate precision and TopoJSON quantisation against what's drawn (the light maps are replaced by detail tiles when
   zoomed in), and image sizes against how big they're shown. Changes go in the build scripts (`tools/`), so a rebuild
   gives the same result; the `maps` suite's tap accuracy must not drop and the maps must look the same (compare
   screenshots at the whole map and zoomed in, light and dark).
3. **Startup.** All 10 scripts load before anything shows; `history.js`, `tutorial.js` and `earth.js` are only needed
   later and could load when first used, if nothing changes for the user. `geo.js` already loads the world map in
   batches. The `perf` suite measures the start (`startup (ms)`).
4. **Drawing.** The `perf` suite times one draw of each main view. **Measured on the test machine (2026-11-28): the
   globe at rest takes about 145 ms a draw** (Find, Learning and Earth modes alike), against about 19 ms while spinning
   (the lighter outlines) and under 1 ms for the flat world map (its shapes are cached as `Path2D`). So every time the
   globe settles after a spin or zoom, a phone may freeze for most of a second: probably the biggest win in the app
   (for example, caching the full-detail globe's paths for the current rotation, or drawing only what's in view, or
   drawing the detail in steps). Other likely costs: the globe redraws every shape and line
   each frame (light outlines while spinning); Earth mode on the globe redraws every layer and projects all 1,209
   volcanoes each frame; `drawOverlays` (rings, ovals, bubbles) runs on every frame. Caching what doesn't change between
   frames is the usual win. Phones are 5–10 times slower than the test machine, so small savings matter.
5. **Code structure.** `app.js` grew feature by feature: repeated patterns (14 `S.mode === "explore"` checks, many
   similar card builders and menu-panel switches), code for features since replaced, and CSS for elements that no longer
   exist. Tidy where it makes the code smaller and clearer without risk; splitting `app.js` into a few files is fine
   if every script stays a plain script and the tests pass. Don't rewrite working code just for style.

## What to hand back

A **Results** section at the end of this file:

- the numbers before and after: install download (MB and files), the update download for a release, the biggest data
  files, startup and draw times (the `perf` metrics), lines of code;
- the commits on `optimise`, one line each;
- anything not done and why, and the **questions for the user** (rule 4);
- the full test run's summary (`python tests/run.py --full`).

Then stop and tell the user it's ready for review.
