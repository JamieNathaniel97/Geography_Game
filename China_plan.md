# China – Plan

The brief for China's country map in Gaia Quest. It follows the same pattern as Canada and India (see [PLAN.md](PLAN.md) and [India_plan.md](India_plan.md)). Drafted 2026-11-17. Nothing is built yet. **Open questions** are at the end and need the user's decision before building.

## What's on the map

China has **33 provincial-level divisions** that it actually governs. That makes 33 parts:

- **Provinces (22):** Anhui, Fujian, Gansu, Guangdong, Guizhou, Hainan, Hebei, Heilongjiang, Henan, Hubei, Hunan, Jiangsu, Jiangxi, Jilin, Liaoning, Qinghai, Shaanxi, Shandong, Shanxi, Sichuan, Yunnan, Zhejiang.
- **Autonomous regions (5):** Guangxi, Inner Mongolia, Ningxia, Tibet (Xizang), Xinjiang.
- **Municipalities (4):** Beijing, Chongqing, Shanghai, Tianjin.
- **Special administrative regions (2):** Hong Kong, Macau.
- **Taiwan:** China counts it as a 23rd province, but it is governed separately, and the world map already treats it as its own country (`EXTRA` in `tools/build_data.py`). **Decided 2026-11-17:** Taiwan is **not part of China on this map**. It is grey and untappable, labelled "Taiwan", like the other neighbours.
- Like Canada, each part has a `kind` (Province, Autonomous region, Municipality, SAR), shown on the Learning card.
- **No toggle** (decided 2026-11-17): every game always uses all 33 parts.
- `unit` word: **"Provinces"**. The New game page reads Find: Provinces, Capitals; Name: Provinces, Capitals.

## Wiring it into the app

- `COUNTRY_MAPS`: `CHN: { name: "China", focus: "China", cont: "Asia", unit: "Provinces", data: "cn", region: "china" }`. China is listed under Asia next to India.
- `isCountryMap`, `geoFor`, region button ("Whole China") and stats tab label ("Provinces") get a `"cn"` branch. If there are four or five country maps by then, move these into COUNTRY_MAPS itself.
- `geo.js` loader for `data/cn-provinces.json` + `data/cn-parts.json`.
- "Focus on China ›" on the world Learning map.
- Bump `CACHE` in `sw.js` and add the new files to the offline list.

## Data build: `tools/build_cn.py`

- `data/cn-provinces.json`: the 33 shapes, with the neighbours as grey context (Taiwan, Mongolia, Russia, North Korea, the Central Asian states, Afghanistan, Pakistan, India, Nepal, Bhutan, Myanmar, Laos, Vietnam), plus `borders`, `coast` and `disputed` lines.
- `data/cn-parts.json`: names, alternative names, capitals and Learning facts, hand-written.
- **Shape source:** Natural Earth 1:50m or 1:10m admin-1. Hong Kong and Macau are separate admin-0 shapes in Natural Earth, so join them in. The Chinese mainland map is stable, so the shapes should be current, but still check them.
- **Projection:** Albers equal-area conic, standard parallels 25°N and 47°N, central meridian 105°E. This is the usual projection for maps of China.

## Disputed borders and areas

Same rule as India (decided 2026-11-17): **disputed borders dotted, disputed areas grey and untappable.**

- **Aksai Chin** (China-administered, claimed by India): **Decided:** grey here too, matching India's map, with dotted borders.
- **Arunachal Pradesh** (India-administered, claimed by China as "South Tibet"): India's land. Grey context here, with its border dotted.
- **Taiwan:** see above.
- **South China Sea islands** (Paracel and Spratly Islands, disputed with Vietnam, the Philippines and others): **Decided:** leave them off, and don't draw the "nine-dash line".

## Capitals

| Part | Accept |
| --- | --- |
| Most provinces | one capital, such as Chengdu (Sichuan), Guangzhou (Guangdong), Wuhan (Hubei) |
| Inner Mongolia | Hohhot |
| Xinjiang | Ürümqi / Urumqi |
| Tibet | Lhasa |
| Guangxi | Nanning |
| Ningxia | Yinchuan |
| Municipalities (Beijing, Shanghai, Tianjin, Chongqing) | **Decided:** kept in the capitals games. The answer is the city's own name (Beijing → Beijing). |
| Hong Kong, Macau | Kept in too: Hong Kong → Hong Kong, Macau → Macau / Macao. |

Confirm the whole capitals list against an up-to-date source during the build, as with India.

**Spellings:** accept pinyin with or without tone marks and apostrophes (Xi'an / Xian, Ürümqi / Urumqi). Also accept the old English spellings people still know: Peking (Beijing), Canton (Guangzhou), Nanking (Nanjing), Tientsin (Tianjin), Amoy (Xiamen). Show a spelling note, like game 2 does.

## Names matching

- Old province spellings: Szechwan/Szechuan (Sichuan), Kwangtung (Guangdong), Fukien (Fujian), Shensi (Shaanxi), Shansi (Shanxi), Kansu (Gansu), Sinkiang (Xinjiang).
- **Shanxi and Shaanxi** differ by one letter. The one-typo rule must **not** let one count for the other. Treat them as an exact-match pair. (Same check for Hubei/Hebei and Hunan/Henan, which differ by one or two letters.)
- Short forms: Inner Mongolia / Nei Mongol, Tibet / Xizang, HK, Guangxi Zhuang, Ningxia Hui, Xinjiang Uyghur (full official names accepted too).

## Tiny parts

- **Adaptive circles:** Hong Kong, Macau (very small, and next to each other at the mouth of the Pearl River).
- **Check on the phone:** Shanghai, Tianjin, Beijing are small next to the big provinces, but probably fine at normal zoom.
- **Hainan** is a single big island and doesn't need an oval.

## Flags

Provinces have **no flags**. Only Hong Kong and Macau have regional flags. **Proposed: no flag games**, as for India, but show the Hong Kong and Macau flags on their Learning cards.

## Learning card

Same layout as the India card:

- Name in English and **Chinese characters** (四川 for Sichuan), with pinyin. This needs a CJK font subset bundled for offline use. Only the characters actually used are needed, which keeps it small.
- Kind, region (North, Northeast, East, South Central, Southwest, Northwest), capital, population (**2020 census**), area and rank of 33.
- **More facts:** all 18 ideas below (decided 2026-11-17).

## More facts (all 18 chosen 2026-11-17)

**People and culture**
1. Short one-character name (川 for Sichuan, 粤 for Guangdong), as used on car number plates
2. Main language or dialect (Cantonese, Shanghainese, Hokkien, Tibetan, Uyghur)
3. Main ethnic groups (for example Zhuang in Guangxi, Hui in Ningxia)
4. Cuisine and a famous dish: China has eight great cuisines (Sichuan, Cantonese, Hunan and so on)
5. Famous festival or tradition
6. Famous opera or art form (Peking opera, Sichuan face-changing)

**Land and nature**
7. Main river (Yangtze, Yellow River, Pearl River)
8. Climate type
9. Highest point (Everest is on the Tibet border)
10. A famous national park or scenic area (Zhangjiajie, Jiuzhaigou, Guilin)
11. Famous animal (giant pandas in Sichuan)

**History and landmarks**
12. Ancient kingdom or state it grew from (Shu for Sichuan, Chu for Hubei and Hunan)
13. UNESCO World Heritage Sites (Terracotta Army, Potala Palace)
14. A Great Wall section, if it has one
15. Year it got its present form (Hainan 1988, Chongqing 1997, Hong Kong 1997, Macau 1999)

**Economy**
16. Main industry or crop (tea in Fujian and Yunnan, factories in Guangdong)
17. GDP per person, with its rank out of 33
18. Largest city, if it isn't the capital (Shenzhen, Qingdao, Dalian)

## Build order

1. `tools/build_cn.py`: shapes (with Hong Kong and Macau joined in), parts data, capitals, disputed lines.
2. Map and loader (Albers projection, grey neighbours and Taiwan, lakes).
3. Find and Name: Provinces, then Capitals.
4. Tiny parts (Hong Kong and Macau circles).
5. Learning card with Chinese characters + "Focus on China".
6. Stats and personal bests (reuse the country-map code).

## Open questions for the user

None at the moment (all answered 2026-11-17).
