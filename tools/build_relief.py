"""Builds the terrain (shaded relief) layer from Natural Earth's shaded relief rasters.

  data/relief.jpg            4096x2048 whole world, from SR_50M. Used by the globe and the zoomed-out flat map.
  data/relief/<level>/x_y.jpg  512 px tiles from SR_HR (1:10m, 21600x10800) at two sharper levels,
                             8192 and 16384 px wide, for the zoomed-in flat map. Tiles that are all
                             flat ground or sea, or outside the flat map's 85N-60S, are skipped.
  data/relief/index.json     which tiles exist.

The sources are greyscale plate carree images where flat ground and sea are about 206. They are
re-levelled so flat ground and sea are white (255): the app blends the layer over the map with
"multiply", so white changes nothing (sea stays clean) while shadowed slopes darken the land
colour underneath (classic hill shading).

Run from the repo root:  python tools/build_relief.py
"""
import json
import pathlib
import shutil
import urllib.request
import zipfile

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
DL = ROOT / "tools" / "downloads"
SOURCES = {
    "SR_50M": "https://naciscdn.org/naturalearth/50m/raster/SR_50M.zip",
    "SR_HR": "https://naciscdn.org/naturalearth/10m/raster/SR_HR.zip",
}
FLAT, CONTRAST, DARKEST = 206, 2.0, 105
WORLD_SIZE = (4096, 2048)
TILE = 512
TILE_LEVELS = [8192, 16384]  # widths; heights are half
LUT = [255 - min(255 - DARKEST, max(0, round((FLAT - v) * CONTRAST))) for v in range(256)]


def source(name):
    DL.mkdir(parents=True, exist_ok=True)
    z = DL / f"{name}.zip"
    if not z.exists():
        print("downloading", SOURCES[name])
        urllib.request.urlretrieve(SOURCES[name], z)
    folder = DL / name.lower()
    tif = folder / f"{name}.tif"
    if not tif.exists():
        zipfile.ZipFile(z).extractall(folder)
    Image.MAX_IMAGE_PIXELS = None
    return Image.open(tif).convert("L")


def main():
    data = ROOT / "data"
    world = source("SR_50M").resize(WORLD_SIZE, Image.LANCZOS).point(LUT)
    world.save(data / "relief.jpg", quality=82, optimize=True, progressive=True)
    print("relief.jpg", (data / "relief.jpg").stat().st_size // 1024, "KB")

    hr = source("SR_HR")
    out = data / "relief"
    if out.exists():
        shutil.rmtree(out)
    index = {"tile": TILE, "levels": []}
    for width in TILE_LEVELS:
        im = hr.resize((width, width // 2), Image.LANCZOS).point(LUT)
        names, total = [], 0
        (out / str(width)).mkdir(parents=True)
        for ty in range(width // 2 // TILE):
            for tx in range(width // TILE):
                lat_top = 90 - ty * TILE * 180 / (width // 2)
                lat_bottom = lat_top - TILE * 180 / (width // 2)
                if lat_bottom >= 85 or lat_top <= -60:  # outside the flat map (85N-60S)
                    continue
                tile = im.crop((tx * TILE, ty * TILE, (tx + 1) * TILE, (ty + 1) * TILE))
                if tile.getextrema()[0] >= 250:  # nothing but flat ground or sea
                    continue
                p = out / str(width) / f"{tx}_{ty}.jpg"
                tile.save(p, quality=80, optimize=True)
                names.append(f"{tx}_{ty}")
                total += p.stat().st_size
        index["levels"].append({"w": width, "h": width // 2, "tiles": names})
        print(f"level {width}: {len(names)} tiles, {total // 1024} KB")
    (out / "index.json").write_text(json.dumps(index, separators=(",", ":")), encoding="utf8")


if __name__ == "__main__":
    main()
