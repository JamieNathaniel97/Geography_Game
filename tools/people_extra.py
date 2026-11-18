"""Hand-picked historical figures for the History games (History_games.md, H1), added to Wikidata's fame ranking
so the set isn't mostly European men. Each entry is the title of the person's English Wikipedia article;
tools/build_people.py looks them up in Wikidata (and prints any title it can't find, so fix those here).
Grouped by where the person was born. Only people who have died, with known birth and death places.
"""
EXTRA = {
    "Africa": [
        "Mansa Musa", "Sundiata Keita", "Shaka", "Nzinga of Ndongo and Matamba", "Yaa Asantewaa", "Menelik II",
        "Haile Selassie", "Cleopatra", "Augustine of Hippo", "Ibn Battuta", "Ibn Khaldun", "Nelson Mandela",
        "Desmond Tutu", "Steve Biko", "Miriam Makeba", "Kwame Nkrumah", "Patrice Lumumba", "Thomas Sankara",
        "Julius Nyerere", "Jomo Kenyatta", "Samora Machel", "Amílcar Cabral", "Ahmed Sékou Touré",
        "Léopold Sédar Senghor", "Cheikh Anta Diop", "Gamal Abdel Nasser", "Naguib Mahfouz", "Umm Kulthum",
        "Wangari Maathai", "Chinua Achebe", "Fela Kuti", "Kofi Annan",
    ],
    "Middle East and Central Asia": [
        "Saladin", "Avicenna", "Averroes", "Maimonides", "Ibn al-Haytham", "Rumi", "Omar Khayyam", "Hafez",
        "Suleiman the Magnificent", "Mehmed II", "Mustafa Kemal Atatürk", "Kahlil Gibran", "Mahmoud Darwish",
        "Golda Meir", "Timur", "Babur",
    ],
    "South Asia": [
        "Mahatma Gandhi", "Jawaharlal Nehru", "B. R. Ambedkar", "Rabindranath Tagore", "Akbar", "Shah Jahan",
        "Srinivasa Ramanujan", "Swami Vivekananda", "Rani of Jhansi", "Indira Gandhi", "Muhammad Ali Jinnah",
        "Muhammad Iqbal", "Tipu Sultan", "Guru Nanak", "C. V. Raman", "Homi J. Bhabha", "Benazir Bhutto",
        "Satyajit Ray", "Lata Mangeshkar", "Sheikh Mujibur Rahman", "Ranjit Singh",
    ],
    "East and Southeast Asia": [
        "Confucius", "Qin Shi Huang", "Wu Zetian", "Li Bai", "Du Fu", "Kublai Khan", "Zheng He",
        "Empress Dowager Cixi", "Sun Yat-sen", "Lu Xun", "Mao Zedong", "Zhou Enlai", "Deng Xiaoping", "Bruce Lee",
        "Oda Nobunaga", "Toyotomi Hideyoshi", "Tokugawa Ieyasu", "Hokusai", "Emperor Meiji", "Hirohito",
        "Akira Kurosawa", "Yukio Mishima", "Sejong the Great", "Yi Sun-sin", "Ho Chi Minh", "Aung San", "Sukarno",
        "Kartini", "José Rizal", "Lee Kuan Yew", "Norodom Sihanouk", "Chulalongkorn",
    ],
    "Latin America and the Caribbean": [
        "Moctezuma II", "Atahualpa", "Túpac Amaru II", "Toussaint Louverture", "Simón Bolívar",
        "José de San Martín", "Bernardo O'Higgins", "Miguel Hidalgo y Costilla", "Benito Juárez", "José Martí",
        "Pedro II of Brazil", "Emiliano Zapata", "Pancho Villa", "Sor Juana Inés de la Cruz", "Frida Kahlo",
        "Diego Rivera", "Che Guevara", "Fidel Castro", "Salvador Allende", "Eva Perón", "Juan Perón",
        "Pablo Neruda", "Gabriela Mistral", "Gabriel García Márquez", "Jorge Luis Borges", "Octavio Paz",
        "Heitor Villa-Lobos", "Oscar Niemeyer", "Carmen Miranda", "Celia Cruz", "Pelé", "Diego Maradona",
        "Bob Marley", "Marcus Garvey",
    ],
    "North America (Indigenous leaders)": [
        "Tecumseh", "Sequoyah", "Pocahontas", "Sitting Bull", "Crazy Horse", "Geronimo", "Chief Joseph",
    ],
    "Oceania": [
        "Kamehameha I", "Liliʻuokalani", "Te Rauparaha", "Kate Sheppard", "Ernest Rutherford", "Edmund Hillary",
        "Banjo Paterson", "Don Bradman", "Albert Namatjira", "Eddie Mabo",
    ],
    "Women in Europe and North America": [
        "Hypatia", "Hildegard of Bingen", "Joan of Arc", "Elizabeth I", "Artemisia Gentileschi", "Maria Theresa",
        "Catherine the Great", "Queen Victoria", "Jane Austen", "Mary Shelley", "Ada Lovelace",
        "Florence Nightingale", "Clara Schumann", "Emily Dickinson", "Harriet Tubman", "Emmeline Pankhurst",
        "Marie Curie", "Lise Meitner", "Virginia Woolf", "Simone de Beauvoir", "Rosalind Franklin", "Rosa Parks",
    ],
}


# Hand-picked people Wikidata couldn't place (checked 2026-11-18): written here (places approximate to the town).
# Left out: Mansa Musa and Nzinga of Ndongo and Matamba (where they were born isn't known for sure).
HAND = {
    "Wangari Maathai": dict(name="Wangari Maathai", desc="Kenyan environmentalist, Nobel Peace Prize 2004", kind="other", born=1940, died=2011,
                            bp="Ihithe", bll=[36.94, -0.33], dp="Nairobi", dll=[36.82, -1.29]),
    "B. R. Ambedkar": dict(name="B. R. Ambedkar", desc="Indian jurist who led the drafting of India's constitution", kind="leader", born=1891, died=1956,
                           bp="Mhow", bll=[75.76, 22.55], dp="Delhi", dll=[77.21, 28.61]),
    "Rani of Jhansi": dict(name="Rani Lakshmibai of Jhansi", desc="Queen of Jhansi, a leader of the 1857 rebellion", kind="leader", born=1828, died=1858,
                           bp="Varanasi", bll=[83.0, 25.32], dp="Gwalior", dll=[78.18, 26.22], also=["Lakshmibai", "Rani of Jhansi"]),
    "Empress Dowager Cixi": dict(name="Empress Dowager Cixi", desc="Ruler of China in the late Qing dynasty", kind="leader", born=1835, died=1908,
                                 bp="Beijing", bll=[116.39, 39.91], dp="Beijing", dll=[116.39, 39.92], also=["Cixi"]),
    "Bruce Lee": dict(name="Bruce Lee", desc="Martial artist and film star", kind="other", born=1940, died=1973,
                      bp="San Francisco", bll=[-122.42, 37.77], dp="Hong Kong", dll=[114.17, 22.32]),
    "Oda Nobunaga": dict(name="Oda Nobunaga", desc="Japanese warlord who began the unification of Japan", kind="leader", born=1534, died=1582,
                         bp="Nagoya", bll=[136.9, 35.18], dp="Kyoto", dll=[135.76, 35.01], also=["Nobunaga"]),
    "Emperor Meiji": dict(name="Emperor Meiji", desc="Emperor of Japan during its rapid modernisation", kind="leader", born=1852, died=1912,
                          bp="Kyoto", bll=[135.76, 35.02], dp="Tokyo", dll=[139.69, 35.69], also=["Meiji"]),
    "Sejong the Great": dict(name="Sejong the Great", desc="King of Joseon Korea who created the Hangul alphabet", kind="leader", born=1397, died=1450,
                             bp="Hanseong (Seoul)", bll=[126.98, 37.57], dp="Hanseong (Seoul)", dll=[126.99, 37.58], also=["Sejong", "King Sejong"]),
    "Benito Juárez": dict(name="Benito Juárez", desc="President of Mexico", kind="leader", born=1806, died=1872,
                          bp="San Pablo Guelatao", bll=[-96.49, 17.33], dp="Mexico City", dll=[-99.13, 19.43], also=["Juarez"]),
    "José Martí": dict(name="José Martí", desc="Cuban poet and leader of Cuba's fight for independence", kind="writer", born=1853, died=1895,
                       bp="Havana", bll=[-82.37, 23.13], dp="Dos Ríos", dll=[-76.2, 20.35], also=["Marti"]),
    "Pancho Villa": dict(name="Pancho Villa", desc="General of the Mexican Revolution", kind="leader", born=1878, died=1923,
                         bp="La Coyotada, Durango", bll=[-104.6, 24.9], dp="Parral", dll=[-105.66, 26.93]),
    "Sor Juana Inés de la Cruz": dict(name="Sor Juana Inés de la Cruz", desc="Mexican poet, scholar and nun", kind="writer", born=1648, died=1695,
                                      bp="San Miguel Nepantla", bll=[-98.84, 19.03], dp="Mexico City", dll=[-99.13, 19.43], also=["Sor Juana"]),
    "Frida Kahlo": dict(name="Frida Kahlo", desc="Mexican painter", kind="artist", born=1907, died=1954,
                        bp="Coyoacán, Mexico City", bll=[-99.16, 19.35], dp="Coyoacán, Mexico City", dll=[-99.16, 19.35]),
    "Diego Rivera": dict(name="Diego Rivera", desc="Mexican muralist", kind="artist", born=1886, died=1957,
                         bp="Guanajuato", bll=[-101.26, 21.02], dp="Mexico City", dll=[-99.13, 19.43]),
    "Te Rauparaha": dict(name="Te Rauparaha", desc="Māori chief of the Ngāti Toa", kind="leader", born=1765, died=1849,
                         bp="Kāwhia", bll=[174.82, -38.07], dp="Ōtaki", dll=[175.15, -40.75]),
    "Marie Curie": dict(name="Marie Curie", desc="Physicist and chemist, the first person to win two Nobel Prizes", kind="scientist", born=1867, died=1934,
                        bp="Warsaw", bll=[21.01, 52.23], dp="Passy, Haute-Savoie", dll=[6.72, 45.93], also=["Curie", "Marie Skłodowska-Curie"]),
}


# The kind (the History games' "Kind" filter) from the job in the person's own description, which is far more reliable
# than Wikidata's list of occupations (checked 2026-11-18: Verdi had come out as a leader, actors as composers).
# The first rule that matches wins; no match keeps the script's kind.
import re as _re
KIND_RULES = [
    ("other", r"\b(actor|actress|comedian|footballer|football player|chess player|model|dancer|choreographer|martial artist|mystic|seer|astrologer|nun|missionary|saint|apostle|guru|founder of sikhism|bahá|church father|doctor of the church|businessman|entrepreneur|industrialist|business magnate|philanthropist|sports official)\b"),
    ("composer", r"\b(compos\w*|musician|singer|pianist|violinist|conductor|songwriter|rapper|guitarist|organist)\b"),
    ("writer", r"\b(writer|poet|novelist|author|playwright|dramatist|essayist|journalist|satirist|tragedian|storyteller|lyricist|lexicographer|literary|historian|historiographer)\b"),
    ("philosopher", r"\b(philosoph\w*|theolog\w*)\b"),
    ("scientist", r"\b(physicist|chemist|mathematician|astronomer|biologist|naturalist|inventor|engineer|scientist|physician|economist|geologist|botanist|psycholog\w*|psychiatrist|zoologist|physiologist|neurologist|anthropologist|sociologist|ethnologist|oceanographer|polymath|scholar|radio pioneer|automotive)\b"),
    ("artist", r"\b(painter|artist|sculptor|architect|photographer|muralist|illustrator|filmmaker|film director|director|animator)\b"),
    ("explorer", r"\b(explorer|navigator|astronaut|cosmonaut|aviator|mountaineer|conquistador|sailor|privateer)\b"),
    ("leader", r"\b(emperor|empress|king|queen|president|minister|ruler|politician|sultan|pharaoh|general|tsar|monarch|statesman|duke|shah|khan|caliph|dictator|chairman|premier|marshal|commander|chief|revolutionary|nationalist|activist|suffrag\w*|abolitionist|reformer|first lady|pope|imam|daimyo|samurai|prince|princess|consort|wife of|heir|diplomat|secretary of state|national hero|founding father|founder of the|legislator|senator|magistrate|lawyer|jurist)\b"),
]


def kind_from_desc(desc, kind):
    d = (desc or "").lower()
    for k, rx in KIND_RULES:
        if _re.search(rx, d):
            return k
    return kind
