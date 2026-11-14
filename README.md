# Geography Game

Map games for learning every country, capital and flag. It runs offline on an Android phone as an installable web app (PWA). The full brief is in [PLAN.md](PLAN.md).

## Status

Build 1 foundation:

- spinnable 3D globe and flat world map, with pinch zoom
- game 1, Find the country, for all 197 countries
- tiny-country handling (island ovals, rings, the Lesser Antilles bubble, magnifier)
- jump bar, borders toggle, Give up, back and forward arrows

## Install on a phone

Open the GitHub Pages link in Chrome, then use the menu and choose **Add to Home screen** (or **Install app**). After the first visit it works with no signal.

## Layout

| Path | What it is |
| --- | --- |
| `index.html`, `css/`, `js/` | the app (`geo.js` data and tiny-country shapes, `mapview.js` globe and flat map, `app.js` game and screens) |
| `data/` | bundled map and country data, built by `tools/build_data.py` |
| `vendor/` | d3 and topojson-client, stored locally so the app works offline |
| `sw.js`, `manifest.webmanifest`, `icons/` | offline support and install details. **Bump `CACHE` in `sw.js` on every release**, or installed phones keep the old version. |
| `tools/` | `build_data.py` (map data), `make_icons.py` (icons), `make_preview.py` (single-page test build) |
| `prototype/` | the tiny-country test page used to settle the design |

Map data: [Natural Earth](https://www.naturalearthdata.com/) (public domain), via [world-atlas](https://github.com/topojson/world-atlas). Country facts: [mledoze/countries](https://github.com/mledoze/countries) (ODbL).
