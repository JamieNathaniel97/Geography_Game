"""Small fonts for the scripts on the Learning cards (Noto, SIL Open Font Licence): each Noto font cut down to just the
characters the cards use, so they cost a few kilobytes and work offline.

  fonts/gq-<script>.woff   one per script, loaded by css/app.css (@font-face "GQ Scripts", with unicode ranges)

Text comes from tools/in_facts.py (India's names in their own scripts) , tools/cn_facts.py (China's characters) and tools/ru_facts.py (Russia's Cyrillic); Japan's kanji (tools/jp_facts.py) go in their own font, fonts/gq-japanese.woff.
Run from the repo root:  python tools/build_fonts.py   (needs fontTools; the Noto fonts are in tools/downloads/fonts/)
"""
import pathlib
import sys

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "downloads" / "fonts"
OUT = ROOT / "fonts"

# script: (Noto font file, first and last code point of its Unicode block)
SCRIPTS = {
    "devanagari": ("NotoSansDevanagari-Regular.ttf", 0x0900, 0x097F),
    "bengali": ("NotoSansBengali-Regular.ttf", 0x0980, 0x09FF),
    "gurmukhi": ("NotoSansGurmukhi-Regular.ttf", 0x0A00, 0x0A7F),
    "gujarati": ("NotoSansGujarati-Regular.ttf", 0x0A80, 0x0AFF),
    "oriya": ("NotoSansOriya-Regular.ttf", 0x0B00, 0x0B7F),
    "tamil": ("NotoSansTamil-Regular.ttf", 0x0B80, 0x0BFF),
    "telugu": ("NotoSansTelugu-Regular.ttf", 0x0C00, 0x0C7F),
    "kannada": ("NotoSansKannada-Regular.ttf", 0x0C80, 0x0CFF),
    "malayalam": ("NotoSansMalayalam-Regular.ttf", 0x0D00, 0x0D7F),
    "chinese": ("NotoSansSC.ttf", 0x4E00, 0x9FFF),  # CJK Unified Ideographs (China's names, simplified characters)
    "cyrillic": ("NotoSans-Regular.ttf", 0x0400, 0x04FF),  # Russia's names
    "hangul": ("NotoSansKR.ttf", 0xAC00, 0xD7AF),  # South Korea's names (Hangul syllables; tools/kr_facts.py)
    "arabic": ("NotoSansArabic.ttf", 0x0600, 0x06FF),  # Egypt's names (tools/eg_facts.py), right to left
}


def card_text():
    sys.path.insert(0, str(ROOT / "tools"))
    import in_facts
    import cn_facts
    import ru_facts
    return ("".join(f.get("script", "") for f in in_facts.FACTS.values()) +
            "".join(f.get("zh", "") + f.get("short", "") for f in cn_facts.FACTS.values()) +
            "".join(f.get("ru", "") for f in ru_facts.FACTS.values()) + v4_text())


def v4_text():
    """South Korea's and Egypt's local names (overnight_v4), if their facts files exist yet."""
    out = ""
    for mod in ("kr_facts", "eg_facts"):
        try:
            m = __import__(mod)
            out += "".join(f.get("local", "") for f in m.FACTS.values())
        except ImportError:
            pass
    return out


def japanese():
    """Japan's kanji and kana from NotoSansJP (Japanese glyph shapes, which differ from the Chinese font's), as its own
    family "GQ Japanese" (css/app.css: .native-ja), since its characters overlap the Chinese font's range."""
    sys.path.insert(0, str(ROOT / "tools"))
    import jp_facts
    text = "".join(f.get("kanji", "") for f in jp_facts.FACTS.values())
    chars = sorted({ch for ch in text if ord(ch) > 0x2E80})
    opts = subset.Options()
    opts.flavor = "woff"
    opts.name_IDs = ["*"]
    font = TTFont(SRC / "NotoSansJP.ttf")
    if "fvar" in font:
        from fontTools.varLib import instancer
        font = instancer.instantiateVariableFont(font, {"wght": 400})
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=[ord(c) for c in chars] + [0x20])
    sub.subset(font)
    out = OUT / "gq-japanese.woff"
    font.flavor = "woff"
    font.save(out)
    print(f"{out.name}: {len(chars)} characters, {out.stat().st_size // 1024 + 1} KB")


def main():
    if sys.argv[1:] == ["japanese"]:  # just the Japanese font (the others unchanged)
        japanese()
        return
    OUT.mkdir(exist_ok=True)
    text = card_text()
    css = []
    for name, (file, lo, hi) in SCRIPTS.items():
        chars = sorted({ch for ch in text if lo <= ord(ch) <= hi})
        if not chars:
            continue
        # the joining characters (virama, ZWJ/ZWNJ) and a space, so conjuncts shape as they should
        unicodes = [ord(c) for c in chars] + [0x20, 0x200C, 0x200D, 0x25CC]
        opts = subset.Options()
        opts.layout_features = ["*"]  # keep every shaping rule: Indic scripts need them to join letters
        opts.flavor = "woff"
        opts.name_IDs = ["*"]  # keep the licence and copyright names
        font = TTFont(SRC / file)
        if "fvar" in font:  # a variable font: just the Regular weight (and default width)
            from fontTools.varLib import instancer
            font = instancer.instantiateVariableFont(font, {a.axisTag: (400 if a.axisTag == "wght" else a.defaultValue) for a in font["fvar"].axes})
        sub = subset.Subsetter(opts)
        sub.populate(unicodes=unicodes)
        sub.subset(font)
        out = OUT / f"gq-{name}.woff"
        font.flavor = "woff"
        font.save(out)
        css.append(f'@font-face {{ font-family: "GQ Scripts"; src: url("../fonts/{out.name}") format("woff"); '
                   f'unicode-range: U+{lo:04X}-{hi:04X}; font-display: swap; }}')
        print(f"{out.name}: {len(chars)} characters, {out.stat().st_size // 1024 + 1} KB")
    japanese()
    (OUT / "fonts.css").write_text("\n".join(css) + "\n", encoding="utf8")
    print("wrote fonts/fonts.css (the @font-face rules, copied into css/app.css)")


if __name__ == "__main__":
    main()
