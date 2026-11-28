# Tests

The real app, driven in headless Chrome at a phone's size (390 × 844), plus a few checks of the files. Run them after
every change; nothing is committed while one fails.

```
python tests/run.py                 the quick set, about 2 minutes
python tests/run.py --full          also every country map, about 30 minutes (before handing work back)
python tests/run.py earth menu      just those suites
python tests/run.py --maps at,es    just those country maps
python tests/run.py --online        also the live earthquake feed (needs the internet)
python tests/run.py -v              every check, note and metric
```

Needs Python 3 and Google Chrome (found in the usual places, or `--chrome PATH`, or the `CHROME` environment variable).
No other packages. It exits with 0 when everything passed.

## The suites (`tests/suites/`)

| Suite | What it checks |
| --- | --- |
| files (no browser) | every file in the offline cache (`sw.js`) exists, the page's scripts and styles exist, every script is cached |
| smoke | the app starts; every world game starts on the globe and the flat map; a region game, Learning mode, Earth mode; the menu, stats and themes |
| menu | the Countries list; Belgium's and Spain's sets; a Belgium regions game; the stats tabs; Focus on Austria; South Africa's enclaves; Sweden's coats of arms; the US and Russia timelines |
| fixes | a missed (red) country doesn't count as a guess; Ireland's own page and game; the Countries list is alphabetical; games use the ceremonial counties |
| back | the phone's back button closes one thing at a time (CloseWatcher, no history entries), then "Press back again to exit" |
| earth | Earth mode: the tab; plates and seas the right way round; taps on volcanoes, hotspots, named ridges and trenches, a boundary, the Ring of Fire, seas and plates on the globe and the flat map; the Layers panel; leaving and coming back |
| perf | how long the app takes to start, and one draw of the map in each main view (run on its own, after the others) |
| maps (`--full`) | each country map: every part opens its own card; names, unaccented names and capitals are accepted and no part takes another's; capital dots; flags; the tap test at the whole map and zoomed in (with the detail level) |
| quakes (`--online`) | the live earthquake module: the USGS feed, the cache, the offline fallback |

## The baseline (`tests/baseline.json`)

Suites also report **metrics**: counts, tap accuracy, timings. The runner compares each with the baseline:

- a number may not drop below its baseline (accuracy, parts, flags);
- a timing (a name ending "(ms)") may not be more than 30% slower (timings vary between runs);
- text must match.

`python tests/run.py --full --update-baseline` saves the current metrics as the new baseline. Only do that after checking
that a change in them is meant (for example, a country map rebuilt with more parts), and say so in the commit.

## How it works

`tests/run.py` starts a small web server (a separate process) that serves the repo. `/__test__<suite>.html` is
`index.html` with `tests/harness.js` and the suite added, so the suite drives the real app: it calls the app's own
functions (`GG.debug`, `GG.Earth`), clicks its buttons and taps its map. Each page opens in its own headless Chrome with
a fresh profile; three run at a time (`--jobs`). Suites report through `T.check`, `T.eq`, `T.metric` and `T.info`
(see `tests/harness.js`); a script error on the page is a fail. A page that fails is tried once more (a busy machine can drop
a request); a pass on the second try is shown as FLAKY with -v, so a test that keeps needing it can be looked at. Each page's messages are kept in `tests/.runs/`
(git-ignored) while it runs.

To add a test: a new `tests/suites/<name>.js` that calls `T.run(async () => { await T.ready(); ... })`, and its name
in `QUICK` in `tests/run.py` if it belongs in the quick set.
