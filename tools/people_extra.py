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
