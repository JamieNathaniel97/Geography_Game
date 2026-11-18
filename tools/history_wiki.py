"""Adds the facts Wikidata lacks to the History games' battles and shipwrecks, from each one's English Wikipedia infobox
(2026-11-18):

  battles  "war" (the infobox's "part of"), "sides" (combatant1, combatant2), "result" (who won), "losses" (casualties1,
           casualties2), "strength" (strength1, strength2)
  wrecks   "cause" (the ship infobox's fate: what sank it), "war" (the war it was lost in, where the article says)

The articles are cached in tools/downloads/wiki_battles/ and wiki_wrecks/ (delete to refresh). Facts already set by hand
(FIXES in the build scripts) are kept. The text is cleaned of templates and links and cut short.
Run from the repo root, after tools/build_battles.py and tools/build_wrecks.py:  python tools/history_wiki.py
Source: Wikipedia (CC BY-SA 4.0), credited in the app.
"""
import json
import pathlib
import re
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
UA = {"User-Agent": "GaiaQuestBuild/1.0 (geography quiz data build)"}


def fetch(title, cache_dir):
    cache_dir.mkdir(parents=True, exist_ok=True)
    f = cache_dir / (re.sub(r"[^\w\-]+", "_", title)[:120] + ".wiki")
    if f.exists():
        return f.read_text(encoding="utf8")
    url = "https://en.wikipedia.org/w/index.php?" + urllib.parse.urlencode({"title": title, "action": "raw", "redirect": "yes"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                text = r.read().decode("utf8")
            m = re.match(r"\s*#REDIRECT\s*\[\[([^\]|#]+)", text, re.I)
            if m:  # follow one redirect
                with urllib.request.urlopen(urllib.request.Request(
                        "https://en.wikipedia.org/w/index.php?" + urllib.parse.urlencode({"title": m.group(1), "action": "raw"}),
                        headers=UA), timeout=30) as r:
                    text = r.read().decode("utf8")
            f.write_text(text, encoding="utf8")
            time.sleep(0.3)
            return text
        except Exception as e:
            print("   retry", title, e)
            time.sleep(3)
    return ""


def infobox(text, names):
    """The infobox fields (top-level "| key = value" lines inside the first matching infobox), as raw wikitext."""
    m = re.search(r"\{\{\s*Infobox\s+(%s)" % "|".join(names), text, re.I)
    if not m:
        return {}
    i, depth, j = m.start(), 0, m.start()
    while j < len(text):  # find the infobox's end, counting nested {{ }}
        if text.startswith("{{", j):
            depth += 1; j += 2; continue
        if text.startswith("}}", j):
            depth -= 1; j += 2
            if depth == 0:
                break
            continue
        j += 1
    body = text[i + 2:j - 2]
    out, key, depth, buf = {}, None, 0, []
    k = 0
    # split on "|" at nesting depth 0
    parts, cur, d1, d2 = [], [], 0, 0
    while k < len(body):
        two = body[k:k + 2]
        if two == "{{": d1 += 1; cur.append(two); k += 2; continue
        if two == "}}": d1 -= 1; cur.append(two); k += 2; continue
        if two == "[[": d2 += 1; cur.append(two); k += 2; continue
        if two == "]]": d2 -= 1; cur.append(two); k += 2; continue
        if body[k] == "|" and d1 == 0 and d2 == 0:
            parts.append("".join(cur)); cur = []; k += 1; continue
        cur.append(body[k]); k += 1
    parts.append("".join(cur))
    for p in parts[1:]:
        if "=" in p:
            a, b = p.split("=", 1)
            out[a.strip().lower()] = b.strip()
    return out


def clean(v, limit=140):
    """Wikitext to a short plain line: no refs, comments, files, flags or formatting; lists joined with commas."""
    if not v:
        return ""
    v = re.sub(r"<!--.*?-->", "", v, flags=re.S)
    v = re.sub(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>", "", v, flags=re.S)
    v = re.sub(r"\[\[(File|Image):[^\]]*(\[\[[^\]]*\]\][^\]]*)*\]\]", "", v, flags=re.I)
    for _ in range(4):  # templates, innermost first
        v = re.sub(r"\{\{\s*(flagicon|flagdeco)\s*\|[^{}]*\}\}", "", v, flags=re.I)
        v = re.sub(r"\{\{\s*(flag|flagcountry|flagu|country data [^|]*)\s*\|\s*([^|{}]+)[^{}]*\}\}", r"\2", v, flags=re.I)
        v = re.sub(r"\{\{\s*(plainlist|plain list|unbulleted list|ubl|hlist|flatlist|collapsible list)\s*\|", "{{list|", v, flags=re.I)
        v = re.sub(r"\{\{\s*list\s*\|([^{}]*)\}\}", lambda m: ", ".join(x.strip(" *") for x in m.group(1).split("|") if x.strip() and "=" not in x), v)
        v = re.sub(r"\{\{\s*(nowrap|small|lang\|[^|]*|nobr)\s*\|([^{}]*)\}\}", r"\2", v, flags=re.I)
        v = re.sub(r"\{\{\s*(?:convert|cvt)\s*\|([\d,.]+)\s*\|([^|{}]+)[^{}]*\}\}", r"\1 \2", v, flags=re.I)
        v = re.sub(r"\{\{[^{}]*\}\}", "", v)
    v = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", v)
    v = re.sub(r"\[https?://\S+\s*([^\]]*)\]", r"\1", v)
    v = re.sub(r"<br\s*/?>|\n\*+|\n", ", ", v)
    v = re.sub(r"<[^>]+>", "", v)
    v = re.sub(r"'{2,}", "", v)
    v = re.sub(r"\s*,\s*(,\s*)+", ", ", v)
    v = re.sub(r"\s+", " ", v).strip(" ,;*:")
    v = re.sub(r"(^|, )[^,]{1,40}:(?=, |$)", lambda m: m.group(1), v).strip(" ,")  # list headings ("Allied Powers:, Naval support:, ...")
    v = re.sub(r"^, |, , ", ", ", v).strip(" ,")
    v = v.replace("&nbsp;", " ").replace("&ndash;", "–")
    if len(v) > limit:
        v = v[:limit].rsplit(" ", 1)[0].rstrip(",;") + "…"
    return v


# sides the infobox cleaning gets wrong (nested flag lists), set by hand
SIDE_FIX = {"Gallipoli Campaign": ["British Empire, France, Russian Empire", "Ottoman Empire, German Empire, Austria-Hungary"],
            "Gallipoli campaign": ["British Empire, France, Russian Empire", "Ottoman Empire, German Empire, Austria-Hungary"]}


def short(v):
    """The first figure or two of a casualty or strength line ("23,049"; "3,500 killed, 10,200 wounded")."""
    v = re.sub(r"^(total|totals?)\s*:\s*", "", v, flags=re.I)
    parts = [x.strip() for x in v.split(", ") if x.strip() and re.search(r"\d|unknown|heavy|light|all", x, re.I)]  # (", ": not the commas in 1,129,619)
    out = ", ".join(parts[:2]) if parts else ""
    return out[:70].rsplit(" ", 1)[0] + "…" if len(out) > 70 else out


def battles():
    p = ROOT / "data" / "battles.json"
    data = json.loads(p.read_text(encoding="utf8"))
    n = 0
    for b in data:
        title = b.get("title") or b["name"]
        ib = infobox(fetch(title, ROOT / "tools" / "downloads" / "wiki_battles"), ["military conflict", "military operation"])
        if not ib:
            continue
        n += 1
        war = clean(ib.get("partof", ""), 90)
        if war and not b.get("war"):
            b["war"] = war
        sides = SIDE_FIX.get(b["name"]) or [clean(ib.get(k, ""), 90) for k in ("combatant1", "combatant2")]
        b["sides"] = sides if all(sides) else []  # (Wikidata's participants mix in commanders: not used)
        res = clean(ib.get("result", ""), 120)
        if res:
            b["result"] = res
        losses = [short(clean(ib.get(k, ""), 200)) for k in ("casualties1", "casualties2")]
        if any(losses):
            b["losses"] = losses
        strength = [short(clean(ib.get(k, ""), 200)) for k in ("strength1", "strength2")]
        if any(strength):
            b["strength"] = strength
    p.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf8")
    print(f"  battles: {n} of {len(data)} with an infobox; {sum(1 for b in data if b.get('result'))} with a result, "
          f"{sum(1 for b in data if b.get('losses'))} with losses")


# the war each wreck sunk in war was lost in (ship articles rarely say), and fates the infobox has none for (by hand)
WAR_NAMES = {"Bismarck": "Second World War", "Moskva": "Russian invasion of Ukraine", "HMS Hood": "Second World War",
             "USS Yorktown": "Second World War", "German cruiser Karlsruhe": "Second World War", "HMS Indefatigable": "First World War",
             "Kronan": "Scanian War", "USS Gambier Bay": "Second World War", "SS President Coolidge": "Second World War",
             "RMS Lusitania": "First World War", "HMHS Britannic": "First World War", "Mary Rose": "Italian War of 1542–1546",
             "H. L. Hunley": "American Civil War", "Yamato": "Second World War", "MV Wilhelm Gustloff": "Second World War",
             "SS Thistlegorm": "Second World War", "USS Arizona": "Second World War", "USS Indianapolis": "Second World War"}
NOT_WAR = {"USS Massachusetts"}  # sunk as a target ship in 1921, not in war
CAUSES = {"Moskva": "Sunk by Ukrainian anti-ship missiles, 14 April 2022", "Uluburun shipwreck": "Wrecked off Cape Uluburun, Turkey, around 1300 BC",
          "Antikythera wreck": "Wrecked off the island of Antikythera, Greece", "Belitung shipwreck": "Wrecked off Belitung Island, Indonesia",
          "Nanhai One": "Sank in the South China Sea",
          "MV Wilhelm Gustloff": "Torpedoed by the Soviet submarine S-13, 30 January 1945",
          "Batavia": "Wrecked on Morning Reef in the Houtman Abrolhos, 4 June 1629",
          "H. L. Hunley": "Sank on 17 February 1864, just after sinking USS Housatonic off Charleston"}


def wrecks():
    p = ROOT / "data" / "wrecks.json"
    data = json.loads(p.read_text(encoding="utf8"))
    n = 0
    for w in data:
        title = w.get("title") or w["name"]
        text = fetch(title, ROOT / "tools" / "downloads" / "wiki_wrecks")
        ib = infobox(text, ["ship", "shipwreck", "ship begin", "ship career"])
        fate = clean(ib.get("ship fate", "") or ib.get("fate", ""), 130) if ib else ""
        if not fate:  # the ship infobox is often several templates: find "Ship fate" / "fate" anywhere
            m = re.search(r"\|\s*(?:Ship fate|fate)\s*=\s*(.+)", text, re.I)
            fate = clean(m.group(1), 130) if m else ""
        if fate.startswith("{{") or not fate:
            fate = ""
        fate = CAUSES.get(w["name"], fate)
        if fate:
            w["cause"] = fate; n += 1
        if w["name"] in NOT_WAR:
            w["war"] = False
        if w["name"] in WAR_NAMES:
            w["war"] = True; w["warName"] = WAR_NAMES[w["name"]]
        if w.get("war") is True or w.get("war"):
            m = re.search(r"\|\s*(?:partof|part of)\s*=\s*(.+)", text, re.I)
            if m and not isinstance(w.get("warName"), str):
                w["warName"] = clean(m.group(1), 80)
    p.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf8")
    print(f"  wrecks: {n} of {len(data)} with how it sank")


if __name__ == "__main__":
    battles()
    wrecks()
