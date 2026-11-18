"""Easy / Hard for the Historical figures game (2026-11-18): every person is "famous" (Easy) or "obscure" (Hard).

  tools/people_levels.txt  the list, for editing by hand: a "# Famous" section and a "# Obscure" section, one person a
                           line as "Name (born–died)". Move a line from one section to the other to change it.

The first run writes the file from a starting split: famous = an article in at least FAMOUS_LINKS Wikipedia languages
(about the top third), plus a few hand-added people Wikidata has no count for (FAMOUS_ALSO). After that the file is
the authority: this script only reads it and writes "level" into data/people.json (and tools/build_people.py calls it
at the end of every build). People not in the file yet (new to the data) go in by the same rule and are added to it.

Run from the repo root:  python tools/people_levels.py
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
LIST = ROOT / "tools" / "people_levels.txt"
DATA = ROOT / "data" / "people.json"
FAMOUS_LINKS = 150
FAMOUS_ALSO = {"Marie Curie", "Frida Kahlo", "Bruce Lee"}


def yr(y):
    return f"{-y} BC" if y is not None and y < 0 else str(y)


def label(p):
    return f"{p['name']} ({yr(p['born'])}–{yr(p['died'])})"


def read_list():
    if not LIST.exists():
        return None
    level, out = None, {}
    for line in LIST.read_text(encoding="utf8").splitlines():
        t = line.strip()
        if not t:
            continue
        if t.startswith("#"):
            low = t.lower()
            level = "famous" if "famous" in low else "obscure" if "obscure" in low else level
            continue
        if level:
            out[t] = level
    return out


def write_list(people):
    fam = sorted((label(p) for p in people if p["level"] == "famous"), key=str.lower)
    obs = sorted((label(p) for p in people if p["level"] == "obscure"), key=str.lower)
    LIST.write_text(
        "# Easy / Hard for the Historical figures game. Move a line between the sections to change who's where,\n"
        "# then run: python tools/people_levels.py   (lines are \"Name (born–died)\"; lines starting with # are notes)\n\n"
        f"# Famous (Easy): {len(fam)}\n" + "\n".join(fam) + f"\n\n# Obscure (Hard): {len(obs)}\n" + "\n".join(obs) + "\n",
        encoding="utf8")


def apply(people):
    """Sets p["level"] for each person from the list (writing or extending the list as needed)."""
    known = read_list() or {}
    added = False
    for p in people:
        lv = known.get(label(p))
        if lv is None:
            lv = "famous" if p["links"] >= FAMOUS_LINKS or p["name"] in FAMOUS_ALSO else "obscure"
            added = True
        p["level"] = lv
    if added or not LIST.exists():
        write_list(people)
    return people


def main():
    people = json.loads(DATA.read_text(encoding="utf8"))
    apply(people)
    DATA.write_text(json.dumps(people, ensure_ascii=False, separators=(",", ":")), encoding="utf8")
    n = sum(p["level"] == "famous" for p in people)
    print(f"  {n} famous (Easy), {len(people) - n} obscure (Hard); the list is {LIST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
