"""The airports for the airport code games (Misc_games.md, idea_01; changed 2026-11-18), from data/airports.json:

  data/airport-sets.json  {"rank": [codes, best known first], "capitals": [codes],
                           "airports": {code: {"n": name, "c": city served, "a": other accepted city names,
                                               "i": country code, "k": continents, "l": [lon, lat], "y": city code}},
                           "cities": {"LON": [codes], ...}}

  - rank: the "Easy" pot, best known first. The app takes the top of it for the chosen region, more for a big region
    (js/app.js, AP_EASY). Built from the busiest airports: the world top 100 (ACI World 2024, TOP100 here), then the
    regional lists (Wikipedia's busiest airports in Asia, Africa, the US, Canada and Oceania, downloaded to
    tools/downloads/airports/; Europe and Latin America written here by hand, their tables have no codes), then the
    rest of the large airports
  - "Hard": every airport in data/airports.json (3,268 with scheduled flights)
  - capitals: the main airport of each country's capital (one per country; PREFER picks where there are several)
  - cities: IATA city codes (LON, NYC, TYO...): typing one counts for any of its airports in "name the code"
  - SERVES: the city an airport serves, where the source has its own town (Narita -> Tokyo); the town still counts

Run from the repo root:  python tools/airport_sets.py
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent

TOP100 = ("ATL DXB DFW HND LHR DEN ORD IST DEL LAX CDG CAN JFK AMS MAD SIN ICN FRA PVG PEK BKK SZX LAS CKG MCO CLT TFU "
          "BCN SEA MIA KUL PHX SFO EWR CGK IAH FCO MEX BOM DOH YYZ SYD MUC BOS MSP LGW DTW HKG KMG SHA PKX MNL TPE FLL "
          "JED BLR GRU RUH SVO SAW CUN BOG HGH XIY LGA PHL NKG BWI IAD PMI DUB YVR ZRH CPH LIS AYT SLC MEL DCA ORY OSL "
          "VIE BNE ARN AUH HYD CMN MAA KIX GMP NRT DMK BER CTS FUK SGN MXP ATH CJU YUL").split()
TOP50 = TOP100[:50]
# the busiest airports in Europe and Latin America (their Wikipedia tables have no codes), roughly in order
EUROPE = ("LHR IST CDG AMS MAD FRA BCN LGW SAW MUC FCO PMI DUB ZRH CPH LIS AYT ORY OSL VIE ARN BER ATH MXP BRU STN MAN HEL "
          "AGP WAW DUS ALC PRG HAM LIN BUD NCE OPO EDI GVA BGY LTN SVO DME LED VCE TFS LPA ADB ESB BHX GLA OTP KRK CTA NAP "
          "BLQ SKG KBP RIX VNO TLL").split()
LATAM = ("MEX GRU BOG CUN LIM SCL GIG BSB EZE PTY CGH GDL MDE SDQ PUJ SJO UIO GYE MVD AEP MTY TIJ CNF REC SSA POA FOR CWB "
         "VCP HAV").split()
REGION_LISTS = ["List_of_the_busiest_airports_in_Asia", "List_of_the_busiest_airports_in_the_United_States",
                "List_of_the_busiest_airports_in_Africa", "List_of_the_busiest_airports_in_Oceania", "List_of_the_busiest_airports_in_Canada"]
# the capital's main airport, where the data has several for one capital
PREFER = {"JOR": "AMM", "ARG": "EZE", "SWE": "ARN", "ZAF": "CPT", "THA": "BKK", "FRA": "CDG", "IDN": "CGK", "ITA": "FCO",
          "LKA": "CMB", "RUS": "SVO", "NAM": "WDH", "KOR": "ICN", "IRN": "IKA", "SLV": "SAL", "ISL": "KEF", "GBR": "LHR",
          "MEX": "MEX", "LBR": "ROB", "KEN": "NBO", "CHN": "PEK", "CRI": "SJO", "UZB": "TAS", "CAN": "YOW", "USA": "IAD",
          "JPN": "HND", "ROU": "OTP", "UKR": "KBP"}
# city served (shown), where the source has the airport's own town; the source's town is still accepted
SERVES = {"KUL": "Kuala Lumpur", "EWR": "New York", "TPE": "Taipei", "SAW": "Istanbul", "IAD": "Washington", "NRT": "Tokyo",
          "FRA": "Frankfurt", "DFW": "Dallas", "DEL": "Delhi", "BOG": "Bogotá", "MXP": "Milan", "ATH": "Athens", "CJU": "Jeju",
          "YUL": "Montreal", "TFU": "Chengdu", "PKX": "Beijing", "KIX": "Osaka", "DMK": "Bangkok", "GMP": "Seoul",
          "CTS": "Sapporo", "BWI": "Baltimore", "HKG": "Hong Kong", "PMI": "Palma", "CGK": "Jakarta", "ICN": "Seoul",
          "BER": "Berlin", "MEX": "Mexico City", "SGN": "Ho Chi Minh City", "CUN": "Cancún", "SVO": "Moscow",
          "ZRH": "Zurich", "CMN": "Casablanca", "MAA": "Chennai", "BLR": "Bangalore", "BOM": "Mumbai", "GRU": "São Paulo", "OTP": "Bucharest", "KBP": "Kyiv",
          "BRU": "Brussels", "LIN": "Milan", "EDI": "Edinburgh", "BGY": "Bergamo", "VCE": "Venice", "LPA": "Las Palmas",
          "ADB": "Izmir", "KRK": "Kraków", "NAP": "Naples", "MVD": "Montevideo", "DPS": "Denpasar", "HNL": "Honolulu",
          "DJE": "Djerba", "NTL": "Newcastle", "YKF": "Waterloo", "ACE": "Lanzarote", "ANU": "St. John's", "BEM": "Beni Mellal",
          "BJX": "León", "BNX": "Banja Luka", "AVV": "Melbourne", "BDJ": "Banjarmasin", "LED": "Saint Petersburg",
          "TFS": "Tenerife", "CTA": "Catania", "GVA": "Geneva", "STN": "London", "LTN": "London", "SEN": "London", "LCY": "London",
          "BVA": "Paris", "CIA": "Rome", "HLP": "Jakarta", "NLU": "Mexico City", "ZIA": "Moscow", "VKO": "Moscow", "DME": "Moscow"}
# other city names that count (English and local forms, the old names people still use)
ALSO = {"DFW": ["Dallas-Fort Worth", "Fort Worth", "Dallas Fort Worth"], "DEL": ["New Delhi"], "BLR": ["Bengaluru"],
        "BOM": ["Bombay"], "MAA": ["Madras"], "SGN": ["Saigon"], "FRA": ["Frankfurt am Main"], "CAN": ["Canton"],
        "MUC": ["München"], "FCO": ["Roma"], "LIS": ["Lisboa"], "CPH": ["København"], "VIE": ["Wien"], "PEK": ["Peking"],
        "PKX": ["Peking"], "PMI": ["Palma de Mallorca", "Mallorca", "Majorca"], "YUL": ["Montréal"], "BOG": ["Bogota"],
        "GRU": ["Sao Paulo"], "CUN": ["Cancun"], "ZRH": ["Zürich"], "MXP": ["Milano"], "ATH": ["Athina"],
        "HND": ["Haneda"], "NRT": ["Narita"], "EWR": ["Newark"], "IAD": ["Dulles", "Washington DC", "Washington D.C."],
        "DCA": ["Washington DC", "Washington D.C."], "TPE": ["Taoyuan"], "KUL": ["Sepang"], "SAW": ["Pendik"],
        "HKG": ["Chek Lap Kok"], "OTP": ["Otopeni"], "KBP": ["Boryspil", "Kiev"], "BGY": ["Milan"], "LPA": ["Gran Canaria"], "DPS": ["Bali"], "ADB": ["İzmir"], "KRK": ["Krakow", "Cracow"], "NAP": ["Napoli"], "VCE": ["Venezia"], "BJX": ["Leon", "Guanajuato"], "ACE": ["Arrecife"], "TFS": ["Tenerife South"], "LED": ["St Petersburg"], "GVA": ["Genève", "Genf"], "YKF": ["Kitchener"], "CTS": ["Chitose"], "GMP": ["Gimpo"], "ICN": ["Incheon"], "KIX": ["Kansai"]}
# IATA city codes covering several airports
CITIES = {"LON": "LHR LGW STN LTN LCY SEN", "NYC": "JFK LGA EWR", "TYO": "HND NRT", "PAR": "CDG ORY BVA",
          "MOW": "SVO DME VKO ZIA", "CHI": "ORD MDW", "WAS": "IAD DCA BWI", "MIL": "MXP LIN BGY", "ROM": "FCO CIA",
          "STO": "ARN BMA NYO", "SEL": "ICN GMP", "OSA": "KIX ITM UKB", "BJS": "PEK PKX", "SHA": "PVG SHA",
          "BUE": "EZE AEP", "SAO": "GRU CGH VCP", "RIO": "GIG SDU", "YTO": "YYZ YTZ", "YMQ": "YUL", "JKT": "CGK HLP",
          "BKK": "BKK DMK", "IST": "IST SAW", "SPK": "CTS OKD", "THR": "IKA THR", "BER": "BER"}
CONT_FOR = {"HKG": "Asia", "MAC": "Asia", "PRI": "North America"}   # airports in territories (no country code)


BOXES = [("Europe", (-25, 34, 45, 72)), ("Africa", (-26, -37, 60, 34)), ("Asia", (25, -12, 180, 80)),
         ("North America", (-170, 5, -50, 84)), ("South America", (-93, -57, -33, 13)), ("Oceania", (110, -50, 180, 22))]


def region_codes(name, aps, countries, cont_name):
    """The codes in a downloaded busiest-airports list, in order (only airports in that region)."""
    p = ROOT / "tools" / "downloads" / "airports" / f"{name}.wiki"
    if not p.exists():
        return []
    s = p.read_text(encoding="utf8")
    i = s.find("{|")
    t = s[i:s.find("|}", i)] if i >= 0 else s
    out = []
    for line in t.splitlines():
        if line.startswith(("|", "!")):
            for m in re.finditer(r"(?<![A-Za-z])([A-Z]{3})(?![A-Za-z])", line):
                c = m.group(1)
                if c in aps and c not in out and cont_name in countries.get(aps[c]["iso"], {}).get("cont", [cont_name]):
                    out.append(c)
    return out


def main():
    aps = {a["code"]: a for a in json.loads((ROOT / "data" / "airports.json").read_text(encoding="utf8"))}
    countries = {c["iso"]: c for c in json.loads((ROOT / "data" / "countries.json").read_text(encoding="utf8"))}
    by_cap = {}
    for a in aps.values():
        if a["capital"] and a["iso"]:
            by_cap.setdefault(a["iso"], []).append(a)
    capitals = sorted(PREFER.get(iso, None) or sorted(v, key=lambda a: (a["size"] != "L", a["code"]))[0]["code"] for iso, v in by_cap.items())
    conts = {"List_of_the_busiest_airports_in_Asia": "Asia", "List_of_the_busiest_airports_in_the_United_States": "North America",
             "List_of_the_busiest_airports_in_Africa": "Africa", "List_of_the_busiest_airports_in_Oceania": "Oceania",
             "List_of_the_busiest_airports_in_Canada": "North America"}
    rank = list(TOP100)
    for extra in [EUROPE, LATAM] + [region_codes(n, aps, countries, conts[n]) for n in REGION_LISTS]:
        rank += [c for c in extra if c in aps and c not in rank]
    rank += sorted((c for c, a in aps.items() if a["size"] == "L" and c not in rank), key=lambda c: (not aps[c]["capital"], c))
    city_of = {code: cc for cc, codes in CITIES.items() for code in codes.split()}
    out = {}
    for code, a in aps.items():
        iso = a["iso"]
        if iso in countries:
            cont = countries[iso]["cont"]
        else:
            lo, la = a["ll"]
            cont = [CONT_FOR.get(code) or next((n for n, (w, s_, e, n_) in BOXES if w <= lo <= e and s_ <= la <= n_), "")]
        city = SERVES.get(code, a["city"])
        rec = {"n": a["name"], "c": city, "i": iso, "k": cont, "l": a["ll"]}
        also = [n for n in dict.fromkeys([a["city"]] + ALSO.get(code, [])) if n and n != city]
        if also:
            rec["a"] = also
        if code in city_of:
            rec["y"] = city_of[code]
        out[code] = rec
    cities = {cc: [c for c in codes.split() if c in out] for cc, codes in CITIES.items()}
    (ROOT / "data" / "airport-sets.json").write_text(json.dumps({"rank": rank, "capitals": capitals, "airports": out,
        "cities": {k: v for k, v in cities.items() if v}}, ensure_ascii=False, separators=(",", ":")), encoding="utf8")
    print(f"  {len(out)} airports; easy ranking {len(rank)} (top 100 then regional lists then large airports); capitals {len(capitals)}")


if __name__ == "__main__":
    main()
