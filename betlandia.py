import pygame  # Importuje knihovnu pygame pro tvorbu herní grafiky
import random  # Importuje knihovnu random pro generování náhodných čísel
import sys  # Importuje knihovnu sys pro ukončení programu
import mysql.connector  # Importuje knihovnu mysql.connector pro práci s MySQL databází
import hashlib  # Importuje knihovnu hashlib pro hashování hesel

# Funkce pro připojení k MySQL databázi
def connect_db():
    return mysql.connector.connect(
        host="dbs.spskladno.cz",  # Adresa databázového serveru
        user="student14",  # Uživatelské jméno pro přístup k databázi
        password="spsnet",  # Heslo pro přístup k databázi
        database="vyuka14"  # Název databáze, se kterou budeme pracovat
    )

# Funkce pro hashování hesla pomocí SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()  # Zakóduje heslo a převede ho na hash

# Funkce pro registraci nového uživatele
def register_user(username, password):
    """ Registruje uživatele a nastaví mu počáteční hodnoty (balance, days_in_game). """
    if not username or not password:  # Kontrola, zda jsou vyplněny všechny údaje
        print("⚠️ Chyba: Uživatelské jméno a heslo nesmí být prázdné!")
        return False  # Pokud nejsou vyplněny, registrace se neprovede

    try:
        print(f"🛠️ Pokus o registraci: '{username}'")  # Debug výpis pro kontrolu registrace
        db = connect_db()  # Připojení k databázi
        if db is None:  # Kontrola, zda připojení proběhlo úspěšně
            print("Chyba: Připojení k databázi selhalo!")
            return False
        
        cursor = db.cursor()  # Vytvoření kurzoru pro práci s databází

        hashed_password = hash_password(password)  # Hashování hesla

        # Ověření, zda uživatel s tímto jménem již existuje
        cursor.execute("SELECT username FROM betlandia_users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        print(f"🔎 Hledaný uživatel: '{username}'")  # Výpis hledaného uživatele
        print(f"📜 Výsledek dotazu: {existing_user}")  # Výpis existujícího uživatele, pokud existuje

        if existing_user:  # Pokud uživatel existuje, registrace se neprovede
            print(f"Uživatelské jméno '{username}' už existuje!")
            cursor.close()
            db.close()
            return False  

        # Vložení nového uživatele do databáze s počátečním kapitálem a dnem hry
        cursor.execute(
            "INSERT INTO betlandia_users (username, password, balance, days_in_game) VALUES (%s, %s, %s, %s)", 
            (username, hashed_password, 15, 1)  # Počáteční zůstatek: 15$, Počet dní ve hře: 1
        )
        db.commit()  # Uložení změn v databázi
        print(f"Úspěšná registrace: {username}")

        # Ověření, zda byl uživatel přidán
        cursor.execute("SELECT * FROM betlandia_users WHERE username = %s", (username,))
        user_after_insert = cursor.fetchone()
        print(f"📌 Ověření po registraci: {user_after_insert}")  # Ověříme, zda uživatel byl opravdu přidán

        cursor.close()
        db.close()
        return True  # Registrace proběhla úspěšně

    except mysql.connector.Error as err:
        print(f"Chyba při registraci: {err}")  # Výpis chyby při selhání
        return False  # Vrátí False při selhání registrace


#-----------------------------------------------------------------------------------------------------------------------------



# Funkce pro přihlášení uživatele
# Funkce pro přihlášení uživatele a načtení jeho stavu
def login_user(username, password):
    """ Přihlásí uživatele, ověří heslo a načte uložený stav. """
    global user_balance, days_in_game, logged_in_user  # Použití globálních proměnných pro uchování stavu uživatele

    try:
        print(f"🛠️ Pokus o přihlášení: {username}")  # Debug výpis pro kontrolu přihlašovacího procesu
        db = connect_db()  # Připojení k databázi
        cursor = db.cursor()  # Vytvoření kurzoru pro provádění SQL dotazů

        hashed_password = hash_password(password)  # Hashování zadaného hesla pro porovnání s databází

        # SQL dotaz pro ověření existence uživatele a načtení jeho stavu (kapitál a počet dní ve hře)
        cursor.execute("SELECT username, balance, days_in_game FROM betlandia_users WHERE username = %s AND password = %s", 
                       (username, hashed_password))
        user = cursor.fetchone()  # Načtení výsledku dotazu (None, pokud uživatel neexistuje)
        
        cursor.close()  # Uzavření kurzoru
        db.close()  # Uzavření spojení s databází

        if user:  # Kontrola, zda byl uživatel nalezen
            logged_in_user, user_balance, days_in_game = user  # Načtení údajů do globálních proměnných
            print(f"✅ Uživatel {logged_in_user} se úspěšně přihlásil! Kapitál: {user_balance} $, Den: {days_in_game}")
            return True  # Přihlášení bylo úspěšné
        else:
            print(f"❌ Neúspěšné přihlášení: {username}")  # Uživatel nebyl nalezen nebo zadal špatné heslo
            return False  # Přihlášení selhalo

    except mysql.connector.Error as err:
        print(f"Chyba při přihlášení: {err}")  # Výpis chyby v případě problémů s databází
        return False  # Přihlášení selhalo kvůli chybě databáze





# Funkce pro uložení stavu hráče do databáze
# Tato funkce aktualizuje zůstatek a počet dní uživatele v databázi
def save_progress(username, balance, days):
    """ Uloží stav hráče do databáze. """
    db = connect_db()  # Připojení k databázi
    cursor = db.cursor()  # Vytvoření kurzoru pro práci s databází

    # Aktualizace zůstatku a počtu dní ve hře pro konkrétního uživatele
    cursor.execute("UPDATE betlandia_users SET balance = %s, days_in_game = %s WHERE username = %s",
                   (balance, days, username))
    db.commit()  # Uložení změn v databázi

    cursor.close()  # Uzavření kurzoru
    db.close()  # Uzavření připojení k databázi

    print(f"✅ Data uložena: {balance} $, den {days}")  # Výpis potvrzení o úspěšném uložení




# Funkce pro načtení stavu hráče z databáze
def load_progress(username):
    """ Načte uložený stav hráče (kapitál, počet dní) z databáze. """
    global user_balance, days_in_game  # Použití globálních proměnných pro uložení hodnot

    db = connect_db()  # Připojení k databázi
    cursor = db.cursor()  # Vytvoření kurzoru pro provádění SQL dotazů

    # SQL dotaz pro načtení zůstatku a počtu dní uživatele
    cursor.execute("SELECT balance, days_in_game FROM betlandia_users WHERE username = %s", (username,))
    result = cursor.fetchone()  # Získání výsledku dotazu

    if result:
        user_balance, days_in_game = result  # Načteme hodnoty z databáze
        print(f"✅ Úspěšně načteno: {user_balance} $, {days_in_game}. den")
    else:
        print("⚠️ Uživatel nenalezen, nastavujeme výchozí hodnoty.")
        user_balance = starting_capital  # Nastavení výchozího zůstatku
        days_in_game = 1  # Nastavení výchozího dne

    cursor.close()  # Uzavření kurzoru
    db.close()  # Uzavření připojení k databázi

# Inicializace Pygame
pygame.init()  # Inicializace knihovny Pygame



# Rozměry obrazovky
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Otevření hry v režimu celé obrazovky
WIDTH, HEIGHT = screen.get_size()  # Získání aktuální šířky a výšky obrazovky
pygame.display.set_caption("Sázkovka")  # Nastavení názvu okna

# Barvy
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (169, 169, 169)
DARK_GRAY = (100, 100, 100)
LIGHT_GRAY = (211, 211, 211)
BLUE = (0, 102, 204)
YELLOW = (255, 153, 51) 
GREEN = (50,250,50)

logged_in_user = None  # Proměnná pro aktuálně přihlášeného uživatele (None znamená, že nikdo není přihlášen)
active_bets = {}  # Slovník pro ukládání aktivních sázek uživatelů (indexován podle zápasu a typu sázky)
total_bets = {}  # Slovník pro ukládání celkových vsazených částek v daném dni
days_in_game = 1  # Začínáme od prvního dne hry
daily_total_bets = 0  # Uchovává celkovou vsazenou částku pro aktuální den
 # Celkově vsazené peníze

 
# Fonty pro různé textové prvky ve hře
title_font = pygame.font.Font(None, 60)  # Font pro hlavní nadpisy (velikost 60)
small_font = pygame.font.Font(None, 30)  # Font pro menší texty a popisky (velikost 30)
large_font = pygame.font.Font(None, 50)  # Font pro důležité texty (velikost 50)
big_font = pygame.font.Font(None, 200)  # Font pro velmi velké texty (například titulní obrazovku)

# Základní kapitál hráče na začátku hry
starting_capital = 15  # Počáteční suma peněz, kterou hráč dostane
user_balance = starting_capital  # Nastavení počátečního zůstatku hráče




def draw_button(surface, rect, text, font, bg_color, text_color, shadow_color=None):
    """
    Vykreslí tlačítko na daný povrch (surface) s možností stínu.
    
    Parametry:
    - surface: Pygame povrch, kam se tlačítko vykreslí
    - rect: Obdélníkový objekt určující pozici a velikost tlačítka
    - text: Text, který se zobrazí na tlačítku
    - font: Font, kterým bude text vykreslen
    - bg_color: Barva pozadí tlačítka
    - text_color: Barva textu na tlačítku
    - shadow_color: Volitelná barva stínu tlačítka
    """
    if shadow_color:  # Pokud je definována barva stínu, vykreslíme stín tlačítka
        shadow_rect = rect.move(5, 5)  # Posun stínu mírně dolů a doprava
        pygame.draw.rect(surface, shadow_color, shadow_rect, border_radius=10)  # Vykreslení stínu
    
    pygame.draw.rect(surface, bg_color, rect, border_radius=10)  # Vykreslení hlavního tlačítka
    
    text_surface = font.render(text, True, text_color)  # Vytvoření textového povrchu s daným textem
    text_rect = text_surface.get_rect(center=rect.center)  # Umístění textu doprostřed tlačítka
    surface.blit(text_surface, text_rect)  # Vykreslení textu na tlačítko




# Funkce pro vykreslení gradientního textu
def draw_gradient_text(surface, text, font, start_color, end_color, position):
    """
    Vykreslí text s plynulým přechodem mezi dvěma barvami.
    
    Parametry:
    - surface: Pygame povrch, kam se text vykreslí
    - text: Řetězec textu, který se zobrazí
    - font: Použitý font pro text
    - start_color: Počáteční barva textu (RGB tuple)
    - end_color: Koncová barva textu (RGB tuple)
    - position: Pozice středu textu na obrazovce
    """
    text_surface = font.render(text, True, start_color)  # Vytvoření textového povrchu
    width, height = text_surface.get_size()  # Získání rozměrů textu
    gradient_surface = pygame.Surface((width, height), pygame.SRCALPHA)  # Povrch pro gradient

    # Vytvoření barevného přechodu pixel po pixelu
    for y in range(height):
        r = start_color[0] + (end_color[0] - start_color[0]) * y // height  # Výpočet červené složky
        g = start_color[1] + (end_color[1] - start_color[1]) * y // height  # Výpočet zelené složky
        b = start_color[2] + (end_color[2] - start_color[2]) * y // height  # Výpočet modré složky
        pygame.draw.line(gradient_surface, (r, g, b), (0, y), (width, y))  # Vykreslení jednoho řádku gradientu

  # Aplikace gradientu na text
    text_surface.blit(gradient_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)  # Použití blendovacího režimu pro aplikaci barevného přechodu na text
    
    # Vykreslení textu s gradientem na cílový povrch
    surface.blit(text_surface, text_surface.get_rect(center=position))  # Umístění textu na zadanou pozici
# Data týmů NHL s kvalitou
nhl_teams = [
    {"name": "Anaheim Ducks", "logo": "anaheim_ducks.png", "quality": 65,},
    {"name": "Arizona Coyotes", "logo": "arizona_coyotes.png", "quality": 60,},
    {"name": "Boston Bruins", "logo": "Boston_Bruins.png", "quality": 85,},
    {"name": "Buffalo Sabres", "logo": "Buffalo_Sabres_Logo.png", "quality": 73,},
    {"name": "Calgary Flames", "logo": "Calgary_Flames_logo.svg.png", "quality": 67},
    {"name": "Carolina Hurricanes", "logo": "Carolina_Hurricanes.svg.png", "quality": 85},
    {"name": "Chicago Blackhawks", "logo": "chicago.png", "quality": 68,},
    {"name": "Colorado Avalanche", "logo": "Colorado_Avalanche_logo.svg.png", "quality": 83,},
    {"name": "Columbus Blue Jackets", "logo": "Columbus_Blue_Jackets_logo.svg.png", "quality": 70,},
    {"name": "Dallas Stars", "logo": "Dallas_Stars_logo_(2013).svg.png", "quality": 72,},
    {"name": "Detroit Red Wings", "logo": "Detroit_Red_Wings_logo.svg.png", "quality": 85,},
    {"name": "Edmonton Oilers", "logo": "Logo_Edmonton_Oilers.svg.png", "quality": 87,},
    {"name": "Florida Panthers", "logo": "Florida_Panthers_2016_logo.svg.png", "quality": 86,},
    {"name": "Los Angeles Kings", "logo": "Los_Angeles_Kings_2024_Logo.svg.png", "quality": 69,},
    {"name": "Minnesota Wild", "logo": "Minnesota_Wild.svg.png", "quality": 65,},
    {"name": "Montreal Canadiens", "logo": "Montreal_Canadiens.svg.png", "quality": 70,},
    {"name": "Nashville Predators", "logo": "Nashville_Predators_Logo_(2011).svg.png", "quality": 65,},
    {"name": "New Jersey Devils", "logo": "New_Jersey_Devils_logo.svg.png", "quality": 75,},
    {"name": "New York Islanders", "logo": "Logo_New_York_Islanders.svg.png", "quality": 70,},
    {"name": "New York Rangers", "logo": "New_York_Rangers.svg.png", "quality": 85,},
    {"name": "Ottawa Senators", "logo": "Ottawa_Senators_2020-2021_logo.svg.png", "quality": 70,},
    {"name": "Philadelphia Flyers", "logo": "Philadelphia_Flyers.svg.png", "quality": 65,},
    {"name": "Pittsburgh Penguins", "logo": "Pittsburgh_Penguins_logo_(2016).svg.png", "quality": 90,},
    {"name": "San Jose Sharks", "logo": "SanJoseSharksLogo.svg.png", "quality": 57,},
    {"name": "Seattle Kraken", "logo": "Seattle_Kraken_official_logo.svg.png", "quality": 85,},
    {"name": "St. Louis Blues", "logo": "St._Louis_Blues_logo.svg.png", "quality": 65,},
    {"name": "Tampa Bay Lightning", "logo": "Tampa-Bay-Lightning-Logo.png", "quality": 75,},
    {"name": "Toronto Maple Leafs", "logo": "Toronto_Maple_Leafs_2016_logo.svg.png", "quality": 80,},
    {"name": "Vancouver Canucks", "logo": "Vancouver_Canucks_logo.svg.png", "quality": 75,},
    {"name": "Vegas Golden Knights", "logo": "Vegas_Golden_Knights_logo.svg.png", "quality": 88,},
    {"name": "Washington Capitals", "logo": "Washington_Capitals.svg.png", "quality": 90, },
    {"name": "Winnipeg Jets", "logo": "Winnipeg_Jets_Logo_2011.svg.png", "quality": 72,},
]


# Načtení pozadí
# Načtení obrázků na pozadí
# Načtení a přizpůsobení obrázků na pozadí
try:
    # Načtení obrázků pro hlavní menu a herní obrazovku
    main_menu_bg = pygame.image.load("pozadi10.webp")  # Načtení pozadí hlavního menu
    game_bg = pygame.image.load("pozadi10.webp")  # Načtení pozadí pro herní obrazovku

    # Přizpůsobení velikosti obrázků na celou obrazovku
    main_menu_bg = pygame.transform.scale(main_menu_bg, (WIDTH, HEIGHT))  # Úprava rozměrů hlavního menu
    game_bg = pygame.transform.scale(game_bg, (WIDTH, HEIGHT))  # Úprava rozměrů herního pozadí
except pygame.error as e:
    # Ošetření chyby v případě neúspěšného načtení obrázků
    print(f"Chyba při načítání obrázku: {e}")  # Výpis chybového hlášení
    
    # Vytvoření náhradního povrchu s modrou barvou, pokud obrázky nelze načíst
    main_menu_bg = pygame.Surface(screen.get_size())  # Náhradní povrch pro hlavní menu
    game_bg = pygame.Surface(screen.get_size())  # Náhradní povrch pro herní obrazovku
    
    main_menu_bg.fill((0, 0, 255))  # Nastavení náhradního pozadí na modrou barvu
    game_bg.fill((0, 0, 255))  # Nastavení náhradního pozadí na modrou barvu


    
def calculate_odds(team1_quality, team2_quality):
    """
    Funkce vypočítá kurzy na výhru dvou týmů na základě jejich kvality.

    Parametry:
    - team1_quality: Číselná hodnota reprezentující kvalitu prvního týmu.
    - team2_quality: Číselná hodnota reprezentující kvalitu druhého týmu.

    Návratová hodnota:
    - Dva kurzy (team1_odds, team2_odds), které určují, jaká je pravděpodobnost výhry každého týmu.
    """
    
    # Výpočet kurzu pro první tým: čím je druhý tým kvalitnější oproti prvnímu, tím vyšší kurz
    team1_odds = round((team2_quality / team1_quality) * 2, 2)

    # Výpočet kurzu pro druhý tým: čím je první tým kvalitnější oproti druhému, tím vyšší kurz
    team2_odds = round((team1_quality / team2_quality) * 2, 2)

    # Vrátíme oba vypočítané kurzy
    return team1_odds, team2_odds



# Funkce pro generování zápasů
def generate_matches(teams):
    """
    Vygeneruje náhodné zápasy mezi týmy a vypočítá kurzy na základě jejich kvality.
    
    Parametry:
    - teams: Seznam týmů, kde každý tým je reprezentován slovníkem obsahujícím jeho jméno a kvalitu.
    
    Návratová hodnota:
    - Seznam zápasů, kde každý zápas obsahuje informace o dvou soupeřích, jejich kurzech a výsledku (který je zpočátku None).
    """
    matches = []  # Seznam pro ukládání vygenerovaných zápasů
    min_games = 1  # Minimální počet zápasů
    max_games = 7  # Maximální počet zápasů
    num_matches = random.randint(min_games, max_games)  # Náhodný počet zápasů mezi minimem a maximem
    
    # Náhodný výběr týmů tak, aby byl jejich počet sudý (každý zápas potřebuje 2 týmy)
    selected_teams = random.sample(teams, min(len(teams), num_matches * 2))
    
    # Procházíme seznam vybraných týmů po dvojicích a generujeme zápasy
    for i in range(0, len(selected_teams), 2):
        if i + 1 < len(selected_teams):  # Kontrola, zda máme dostatek týmů pro zápas
            team1 = selected_teams[i]  # První tým v zápase
            team2 = selected_teams[i + 1]  # Druhý tým v zápase
            
            # Přidání náhodné fluktuace ke kvalitě každého týmu (-5 až +5 bodů)
            fluctuated_quality1 = random.randint(team1["quality"] - 5, team1["quality"] + 5)
            fluctuated_quality2 = random.randint(team2["quality"] - 5, team2["quality"] + 5)
            
            # Výpočet kurzů na základě upravené kvality týmů
            team1_odds, team2_odds = calculate_odds(fluctuated_quality1, fluctuated_quality2)
            
            # Uložení informací o zápasu do seznamu zápasů
            matches.append({
                "team1": team1,  # První tým
                "team2": team2,  # Druhý tým
                "team1_odds": team1_odds,  # Kurz na výhru prvního týmu
                "team2_odds": team2_odds,  # Kurz na výhru druhého týmu
                "result": None  # Výsledek zápasu (zatím neurčený)
            })
    
    return matches  # Vrací seznam vygenerovaných zápasů




def handle_events(event, match_positions, bet_values, user_balance):
    """
    Zpracovává události kliknutí na prvky sázkového rozhraní.
    
    Parametry:
    - event: Událost Pygame (kliknutí myší)
    - match_positions: Seznam interaktivních prvků (tlačítek) na sázkovém tiketu
    - bet_values: Slovník s aktuálními hodnotami sázek
    - user_balance: Aktuální zůstatek uživatele
    
    Návratová hodnota:
    - Aktualizovaný zůstatek uživatele po změnách sázek
    """
    global total_bets  # Použití globální proměnné pro sledování celkových vsazených částek

    for item in match_positions:  # Procházíme všechny interaktivní prvky zápasů
        if isinstance(item[1], pygame.Rect) and item[1].collidepoint(event.pos):  # Kontrola, zda bylo kliknuto na tlačítko
            index, option = item[2], item[3]  # Získání indexu zápasu a možnosti sázky
            key = (index, option)  # Vytvoření klíče pro identifikaci sázky

            if item[0] == "expand":  # Kliknutí na tlačítko pro rozbalení detailů zápasu
                pass  # Funkcionalita rozbalení zatím není implementována
            
            elif item[0] == "decrease":  # Kliknutí na tlačítko pro snížení sázky
                if bet_values.get(key, 0) > 0:  # Kontrola, zda lze sázku snížit (nesmggí být menší než 0)
                    bet_values[key] -= 1  # Snížení sázky o 1 dolar

            elif item[0] == "increase":  # Kliknutí na tlačítko pro zvýšení sázky
                if bet_values.get(key, 0) < user_balance:  # Kontrola, zda uživatel má dostatek peněz
                    bet_values[key] += 1  # Zvýšení sázky o 1 dolar

            elif item[0] == "confirm":  # Kliknutí na tlačítko pro potvrzení sázky
                bet_amount = bet_values.get(key, 0)  # Získání hodnoty sázky
                if bet_amount > 0 and bet_amount <= user_balance:  # Kontrola, zda je částka platná a dostupná
                    user_balance -= bet_amount  # Odečtení sázky z uživatelského zůstatku
                    total_bets += bet_amount  # Přičtení sázky do celkového vsazeného množství
                    active_bets[key] = (bet_amount, item[4])  # Uložení sázky do aktivních sázek
                    bet_values[key] = 0  # Resetování hodnoty sázky na 0
                    print(f"✅ Sázka {bet_amount} $ na {option} potvrzena! (Celkem vsazeno: {total_bets} $)")

    return user_balance  # Vrací aktualizovaný zůstatek hráče po změnách sázek



def draw_matches(matches, y_offset, expanded_match, user_balance, bet_values):
    """
    Vykreslí zápasy na obrazovku a umožní sázení.
    
    Parametry:
    - matches: Seznam zápasů s informacemi o týmech a kurzech.
    - y_offset: Počáteční vertikální pozice pro vykreslování zápasů.
    - expanded_match: Index zápasu, který má být rozbalen (pro detaily sázení).
    - user_balance: Aktuální zůstatek uživatele.
    - bet_values: Slovník obsahující sázky uživatele na jednotlivé možnosti.

    Návratová hodnota:
    - match_positions: Seznam interaktivních prvků na obrazovce (např. tlačítka na sázení).
    """
    
    total_y_offset = y_offset  # Uchovává aktuální pozici pro vykreslování zápasů
    match_positions = []  # Seznam interaktivních prvků pro události myši

    # 🏦 Zobrazení aktuálního zůstatku uživatele na obrazovce
    balance_text = large_font.render(f"Kapitál: ${user_balance:.2f}", True, WHITE)
    screen.blit(balance_text, (20, 20))  # Vykreslení textu v levém horním rohu

    # 🎮 Procházíme všechny zápasy a vykreslujeme je na obrazovku
    for index, match in enumerate(matches):
        team1 = match["team1"]
        team2 = match["team2"]

        # 🖼️ Načtení a zmenšení log týmů (pokud chybí, zobrazí se šedé čtverce)
        try:
            logo1 = pygame.image.load(team1["logo"])
            logo1 = pygame.transform.smoothscale(logo1, (50, 50))
        except:
            logo1 = pygame.Surface((50, 50))
            logo1.fill(GRAY)

        try:
            logo2 = pygame.image.load(team2["logo"])
            logo2 = pygame.transform.smoothscale(logo2, (50, 50))
        except:
            logo2 = pygame.Surface((50, 50))
            logo2.fill(GRAY)

        # 🔽 Pokud je zápas rozbalený, nastavíme větší výšku pro tabulku
        if expanded_match == index:
            match_height = 100 + 40 * 5  # Více místa pro možnosti sázek
        else:
            match_height = 100  # Výchozí výška

        # 📋 Vykreslení tabulky zápasu (šedá s žlutým okrajem)
        match_rect = pygame.Rect(WIDTH // 2 - 450, total_y_offset, 900, match_height)
        pygame.draw.rect(screen, (30, 30, 30), match_rect)  # Šedé pozadí
        pygame.draw.rect(screen, YELLOW, match_rect, 2)  # Žlutý rámeček

        # 🏒 Zarovnání log a textu uprostřed řádku
        center_y = total_y_offset + 50

        # 🏆 Levý tým - vykreslení loga a názvu
        logo1_x = match_rect.x + 150
        screen.blit(logo1, (logo1_x, center_y - logo1.get_height() // 2))

        team1_name = small_font.render(f"{team1['name']}", True, YELLOW)
        name1_x = logo1_x + (logo1.get_width() // 2) - (team1_name.get_width() // 2)
        screen.blit(team1_name, (name1_x, center_y + 30))

        # 🏅 Zobrazení kurzu pro tým 1
        team1_odds_text = small_font.render(f"({match['team1_odds']})", True, WHITE)
        screen.blit(team1_odds_text, (name1_x + team1_name.get_width() + 10, center_y + 30))

        # 🏆 Pravý tým - vykreslení loga a názvu
        logo2_x = match_rect.right - 250
        screen.blit(logo2, (logo2_x, center_y - logo2.get_height() // 2))

        team2_name = small_font.render(f"{team2['name']}", True, YELLOW)
        name2_x = logo2_x + (logo2.get_width() // 2) - (team2_name.get_width() // 2)
        screen.blit(team2_name, (name2_x, center_y + 30))

        # 🏅 Zobrazení kurzu pro tým 2
        team2_odds_text = small_font.render(f"({match['team2_odds']})", True, WHITE)
        screen.blit(team2_odds_text, (name2_x + team2_name.get_width() + 10, center_y + 30))

        # 📌 Tlačítko pro rozbalení možností sázení
        expand_button = pygame.Rect(match_rect.centerx - 15, center_y - 15, 33, 30)
        pygame.draw.rect(screen, YELLOW if expanded_match == index else RED, expand_button)
        arrow = "0" if expanded_match == index else "V"
        arrow_text = small_font.render(arrow, True, WHITE)
        screen.blit(arrow_text, (expand_button.x + 10, expand_button.y + 5))

        match_positions.append(("expand", expand_button, index))

        # 🔽 Pokud je zápas rozbalený, zobrazíme možnosti sázek
        if expanded_match == index:
            line_y = total_y_offset + 100
            pygame.draw.line(screen, YELLOW, (match_rect.x, line_y), (match_rect.right, line_y), 2)

            bet_options = [
                ("Výhra domácího týmu", match["team1_odds"]),
                ("Výhra hostujícího týmu", match["team2_odds"]),
                ("Remíza(3.0)", 3.0),  # Pevně daný kurz pro remízu
            ]
            option_y = line_y + 10

            for option, odds in bet_options:
                option_text = small_font.render(option, True, WHITE)
                screen.blit(option_text, (match_rect.x + 20, option_y))

                # 📥 Pole pro zadání sázky
                input_box = pygame.Rect(match_rect.x + 300, option_y, 50, 30)
                pygame.draw.rect(screen, WHITE, input_box)
                pygame.draw.rect(screen, BLACK, input_box, 2)

                key = (index, option)
                bet_value = bet_values.get(key, 0)
                bet_value_text = small_font.render(str(bet_value), True, BLACK)
                screen.blit(bet_value_text, (input_box.x + 10, input_box.y + 5))

                match_positions.append(("input", input_box, index, option))

                # 🔺 Tlačítka pro úpravu sázky
                decrease_button = pygame.Rect(input_box.x - 30, option_y, 30, 30)
                increase_button = pygame.Rect(input_box.right, option_y, 30, 30)
                pygame.draw.rect(screen, DARK_GRAY, decrease_button)
                pygame.draw.rect(screen, DARK_GRAY, increase_button)

                decrease_text = small_font.render("-", True, WHITE)
                increase_text = small_font.render("+", True, WHITE)
                screen.blit(decrease_text, (decrease_button.x + 10, decrease_button.y + 5))
                screen.blit(increase_text, (increase_button.x + 10, increase_button.y + 5))

                match_positions.append(("decrease", decrease_button, index, option))
                match_positions.append(("increase", increase_button, index, option))

                # 💰 Zobrazení možné výhry
                possible_win = round(bet_value * odds, 2)
                possible_win_text = small_font.render(f"Možná výhra: ${possible_win}", True, YELLOW)
                screen.blit(possible_win_text, (input_box.right + 140, option_y + 5))

                # ✅ Tlačítko potvrzení sázky
                confirm_button = pygame.Rect(match_rect.x + 720, option_y, 80, 30)
                pygame.draw.rect(screen, YELLOW, confirm_button)
                confirm_text = small_font.render("Vsadit", True, WHITE)
                screen.blit(confirm_text, (confirm_button.x + 5, confirm_button.y + 5))
                match_positions.append(("confirm", confirm_button, index, option))

                option_y += 40

        total_y_offset += match_height + 20

    return match_positions


# Funkce pro zobrazení zápasů
# Globální definice výchozí ligy na začátku skriptu

# Globální slovník pro ukládání zápasů obou lig
# Základní kapitál a aktuální vstup pro sázky
starting_capital = 15.00  # Nastaveno jako float s dvěma desetinnými místy
user_balance = round(starting_capital, 2)

input_text = ""



def simulate_score(team_quality):
    """
    Simuluje počet gólů, které tým vstřelí v zápase, na základě jeho kvality.
    
    Parametry:
    - team_quality: Číselná hodnota reprezentující sílu týmu (čím vyšší, tím lepší tým).

    Návratová hodnota:
    - Počet gólů, které tým vstřelí (celé číslo, minimálně 0).
    """
    
    # ⚽ Průměrný počet gólů, který tým vstřelí v zápase
    # Silnější týmy mají vyšší průměr, slabší týmy nižší
    mean_goals = 1.5 + (team_quality / 30)  # Např. tým s kvalitou 60 bude mít průměr 3,5 gólu (1.5 + 60/30)

    # 📈 Standardní odchylka - určuje, jak moc se může počet gólů odchylovat od průměru
    std_dev = 1.2  # Vyšší odchylka znamená větší variabilitu skóre

    # 🎲 Vygenerování skóre pomocí normálního rozdělení
    # `random.gauss(mean, std_dev)` generuje náhodné číslo s normálním rozdělením
    # `int(...)` zaokrouhluje hodnotu dolů na celé číslo (počet gólů musí být celé číslo)
    # `max(0, ...)` zajistí, že tým nemůže mít záporný počet gólů
    goals = max(0, int(random.gauss(mean_goals, std_dev)))

    return goals  # 🔄 Vrací počet vstřelených gólů


def generate_results(matches):
    """
    Vygeneruje výsledky zápasů a vyhodnotí, zda hráči vyhráli své sázky.

    Parametry:
    - matches: Seznam zápasů, kde každý obsahuje informace o týmech, kurzech a sázkách.

    Aktualizuje:
    - `user_balance`: Přidává výhru nebo ponechává zůstatek stejný.
    - `matches`: Každému zápasu přidá výsledek a případné prodloužení/nájezdy.
    - `active_bets`: Odstraní sázky, které již byly vyhodnoceny.
    """
    global user_balance  # Použití globální proměnné pro správu peněz hráče

    # 📌 Procházíme všechny zápasy a generujeme jejich výsledky
    for index, match in enumerate(matches):
        # 🎲 Simulujeme skóre obou týmů na základě jejich kvality
        team1_score = simulate_score(match["team1"]["quality"])
        team2_score = simulate_score(match["team2"]["quality"])

        # 🏆 Uložíme výsledek zápasu (např. "2 - 1")
        match["result"] = f"{team1_score} - {team2_score}"
        match["overtime_result"] = ""  # Výsledek prodloužení (pokud bude potřeba)

        # ⏳ Pokud je remíza, rozhodneme vítěze v prodloužení nebo nájezdech
        if team1_score == team2_score:
            overtime_winner = random.choice(["team1", "team2"])  # Náhodně zvolíme vítěze
            overtime_method = random.choice(["P", "SN"])  # "P" = prodloužení, "SN" = samostatné nájezdy

            if overtime_winner == "team1":
                match["overtime_result"] = f"{overtime_method} {team1_score + 1} - {team2_score}"
            else:
                match["overtime_result"] = f"{overtime_method} {team1_score} - {team2_score + 1}"

        # 📌 Vyhodnocení sázek na tento zápas
        to_remove = []  # Seznam sázek, které budou po vyhodnocení odstraněny

        for (bet_index, bet_option), (bet_amount, odds) in active_bets.items():
            if bet_index == index:  # Sázka odpovídá právě vyhodnocovanému zápasu
                won = False  # Výchozí stav - sázka je prohraná

                # 🏅 Podmínky pro výhru sázky
                if bet_option == "Výhra domácího týmu" and team1_score > team2_score:
                    won = True
                elif bet_option == "Výhra hostujícího týmu" and team2_score > team1_score:
                    won = True
                elif bet_option == "Remíza(3.0)" and team1_score == team2_score:
                    won = True

                # 💰 Pokud hráč vyhrál sázku, přidáme mu peníze podle kurzu
                if won:
                    win_amount = round(bet_amount * odds, 2)  # Výhra = sázka * kurz
                    user_balance += win_amount  # Přičtení výhry k zůstatku
                    print(f"✅ Výhra! {bet_option} přinesla {win_amount} $ (sázka: {bet_amount} * kurz: {odds})")
                else:
                    print(f"❌ Prohra! {bet_option} nevyšla. (Sázka: {bet_amount} $)")

                to_remove.append((bet_index, bet_option))  # Uložíme sázku k odstranění

    # 🗑️ Odstraníme sázky, které už byly vyhodnoceny
    for key in to_remove:
        del active_bets[key]


def display_matches():
    """
    Hlavní funkce pro správu herní obrazovky.

    Co dělá:
    - Zobrazuje zápasy na aktuální den a umožňuje na ně sázet.
    - Udržuje přehled o zůstatku hráče a jeho aktivních sázkách.
    - Po stisknutí tlačítka "Simulovat" vygeneruje výsledky zápasů.
    - Pokud hráč vyhraje sázku, přičte mu výhru k zůstatku.
    - Po simulaci umožní přejít na další den a vygenerovat nové zápasy.

    Parametry:
    - Nepřijímá žádné vstupy, ale pracuje s globálními proměnnými, jako jsou:
      - `user_balance` (peníze hráče),
      - `active_bets` (seznam aktuálních sázek),
      - `matches` (seznam dnešních zápasů),
      - `days_in_game` (počítadlo dní),
      - `logged_in_user` (aktuálně přihlášený uživatel).

    Návratová hodnota:
    - Nemá návratovou hodnotu, ale průběžně aktualizuje globální stav hry.
    """
    global user_balance, active_bets, matches, total_bets, days_in_game, logged_in_user  

    if logged_in_user is None:
        print("⚠️ Hra se hraje bez přihlášení.")
        user_balance = starting_capital  
    else:
        print(f"🎮 Hraje přihlášený uživatel: {logged_in_user}, Kapitál: {user_balance} $, Den: {days_in_game}")

    active_bets.clear()  # 🗑️ Vymaže všechny předchozí sázky
    total_bets = 0  # 📊 Reset celkové vsazené částky
    bet_tickets = []  # 🎟️ Seznam tiketů sázek
    payout_amount = 0  # 💰 Uchovává součet výher před připsáním na účet hráče

    # 🏒 **Generování nových zápasů na dnešní den**
    matches = generate_matches(nhl_teams)  
    bet_values = {}  # 🔢 Uchovává částky vsazené na jednotlivé zápasy

    # 🔄 **Stav hry pro dnešní den**
    can_simulate = True  # ✅ Umožňuje spuštění simulace
    betting_disabled = False  # 🚫 Blokuje sázení po simulaci
    next_day_enabled = False  # 📅 Povolení tlačítka "Další den"
    expanded_match = None  # 🔽 Index rozbaleného zápasu (zobrazení sázek)

    small_ticket_font = pygame.font.Font(None, 22)  # 🔤 Malý font pro zobrazení tiketů

    running = True
    while running:
        screen.blit(game_bg, (0, 0))  

        days_text = large_font.render(f"{days_in_game}. den", True, WHITE)
        screen.blit(days_text, (WIDTH // 2 - days_text.get_width() // 2, 20))

        match_positions = draw_matches(matches, 100, expanded_match, user_balance, bet_values)

        button_height = 50

        back_button_rect = pygame.Rect(20, HEIGHT - button_height - 20, 150, button_height)
        draw_button(screen, back_button_rect, "Menu", small_font, RED, WHITE)

        recharge_button_rect = pygame.Rect(180, HEIGHT - button_height - 20, 150, button_height)
        recharge_color = (255, 140, 0) if user_balance < 2 else DARK_GRAY
        draw_button(screen, recharge_button_rect, "Dobít kredit", small_font, recharge_color, WHITE)

        simulate_button_rect = pygame.Rect(WIDTH - 320, HEIGHT - button_height - 20, 150, button_height)
        simulate_button_color = GREEN if can_simulate else DARK_GRAY
        draw_button(screen, simulate_button_rect, "Simulovat", small_font, simulate_button_color, WHITE)

        next_day_button_rect = pygame.Rect(WIDTH - 170, HEIGHT - button_height - 20, 150, button_height)
        next_day_button_color = BLUE if next_day_enabled else DARK_GRAY
        draw_button(screen, next_day_button_rect, "Další den", small_font, next_day_button_color, WHITE)

        # ✅ **Zobrazení "Kapitál"**
        balance_text = large_font.render(f"Kapitál: ${user_balance:.2f}", True, WHITE)
        screen.blit(balance_text, (20, 20))

        # ✅ **Zobrazení "K výplatě", pouze pokud je větší než 0**
        if payout_amount > 0:
            payout_text = large_font.render(f"K výplatě: ${payout_amount}", True, YELLOW)
            screen.blit(payout_text, (20, 60))  

        # ✅ **Zobrazení tiketů**
        y_offset = 100  
        for ticket in bet_tickets:
            ticket_parts = ticket.split("\n")  
            for i, line in enumerate(ticket_parts):  
                ticket_text = small_ticket_font.render(line, True, YELLOW)
                screen.blit(ticket_text, (20, y_offset + i * 20))  
            y_offset += 70  

        # ✅ **Zobrazení výsledků po simulaci zápasů**
        if betting_disabled:
            for index, match in enumerate(matches):
                if match["result"]:
                    match_x = WIDTH // 2 - 450  
                    result_x = match_x + 430  
                    result_y = 100 + (index * 120) + 70  

                    result_text = small_font.render(match["result"], True, WHITE)
                    screen.blit(result_text, (result_x, result_y))

                    if match.get("overtime_result"):
                        overtime_text = small_font.render(match["overtime_result"], True, YELLOW)
                        screen.blit(overtime_text, (result_x, result_y - 60))  

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if logged_in_user:
                    save_progress(logged_in_user, user_balance, days_in_game)
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button_rect.collidepoint(event.pos):
                    if logged_in_user:
                        save_progress(logged_in_user, user_balance, days_in_game)
                    running = False  

                elif recharge_button_rect.collidepoint(event.pos) and user_balance < 2:
                    user_balance += 15
                    print(f"✅ Kredit dobit! Nový zůstatek: {user_balance} $")
                    if logged_in_user:
                        save_progress(logged_in_user, user_balance, days_in_game)

                elif simulate_button_rect.collidepoint(event.pos) and can_simulate:
                    expanded_match = None  
                    bet_values.clear()  

                    payout_amount = 0  
                    for (bet_index, bet_option), (bet_amount, odds) in active_bets.items():
                        for index, match in enumerate(matches):
                            if bet_index == index and match["result"]:  
                                try:
                                    team1_score, team2_score = map(int, match["result"].split(" - "))

                                    won = False
                                    if bet_option == "Výhra domácího týmu" and team1_score > team2_score:
                                        won = True
                                    elif bet_option == "Výhra hostujícího týmu" and team2_score > team1_score:
                                        won = True
                                    elif bet_option == "Remíza(3.0)" and team1_score == team2_score:
                                        won = True

                                    if won:
                                        win_amount = round(bet_amount * odds, 2)
                                        payout_amount += win_amount  

                                except ValueError:
                                    print(f"⚠️ Chyba při čtení výsledku zápasu: {match['result']}")

                    generate_results(matches)  
                    can_simulate = False
                    betting_disabled = True
                    next_day_enabled = True
                    total_bets = 0  

                elif next_day_button_rect.collidepoint(event.pos) and next_day_enabled:
                    matches = generate_matches(nhl_teams)
                    can_simulate = True
                    betting_disabled = False
                    next_day_enabled = False
                    
                    bet_tickets.clear()
                    
                    # ✅ Oprava chyby – smazání starých sázek
                    active_bets.clear()  # Odstraní všechny uložené sázky z minulého dne
                    payout_amount = 0  # Vynuluje se výplatní částka

                    if logged_in_user:
                        save_progress(logged_in_user, user_balance, days_in_game)

                    matches = generate_matches(nhl_teams)
                    can_simulate = True
                    betting_disabled = False
                    next_day_enabled = False
                    days_in_game += 1
                    bet_tickets.clear()  
                    payout_amount = 0  # ✅ Výplata se vynuluje při dalším dni

                    if logged_in_user:
                        save_progress(logged_in_user, user_balance, days_in_game)

                else:
                    if not betting_disabled:
                        for item in match_positions:
                            if isinstance(item[1], pygame.Rect) and item[1].collidepoint(event.pos):
                                if item[0] == "expand":
                                    if expanded_match is not None and expanded_match != item[2]:
                                        bet_values.clear()  
                                    expanded_match = item[2] if expanded_match != item[2] else None
                                elif item[0] == "increase":
                                    index, option = item[2], item[3]
                                    key = (index, option)
                                    if bet_values.get(key, 0) < user_balance:
                                        bet_values[key] = bet_values.get(key, 0) + 1
                                elif item[0] == "decrease":
                                    index, option = item[2], item[3]
                                    key = (index, option)
                                    if bet_values.get(key, 0) > 0:
                                        bet_values[key] -= 1
                                elif item[0] == "confirm":
                                    index, option = item[2], item[3]
                                    key = (index, option)
                                    bet_amount = bet_values.get(key, 0)

                                    odds = None
                                    for match in matches:
                                        if index == matches.index(match):
                                            if option == "Výhra domácího týmu":
                                                odds = match["team1_odds"]
                                                team_name = match["team1"]["name"]
                                            elif option == "Výhra hostujícího týmu":
                                                odds = match["team2_odds"]
                                                team_name = match["team2"]["name"]
                                            elif option == "Remíza(3.0)":
                                                odds = 3.0
                                                team_name = "Remíza"

                                    if odds is not None and bet_amount > 0 and bet_amount <= user_balance:
                                        user_balance -= bet_amount
                                        possible_win = round(bet_amount * odds, 2)
                                        active_bets[key] = (bet_amount, odds)
                                        bet_values[key] = 0  

                                        ticket_info = f"Vsazeno {bet_amount}$\nna {team_name}\nMožná výhra {possible_win}$"
                                        bet_tickets.append(ticket_info)

    main_menu()



def login_screen():
    """
    Přihlašovací a registrační obrazovka pro uživatele.

    Co tato funkce dělá:
    - Umožňuje uživateli zadat uživatelské jméno a heslo.
    - Poskytuje možnost přihlášení nebo registrace.
    - Při úspěšném přihlášení/registraci přesměruje uživatele do hlavního menu.
    - Pokud se přihlášení nepodaří, zobrazí chybovou zprávu.
    - Obsahuje tlačítko pro návrat do hlavního menu.

    Používá globální proměnné:
    - `logged_in_user`: Aktuálně přihlášený uživatel.
    - `user_balance`: Zůstatek hráče.
    - `days_in_game`: Počet dní ve hře.
    - `notification_text`, `notification_time`: Pro zobrazení oznámení o přihlášení.
    """

    # 🛠 **Použití globálních proměnných**
    global logged_in_user, user_balance, days_in_game, notification_text, notification_time  

    # 🔑 **Inicializace vstupních proměnných**
    input_active = "username"  # Určuje, které pole je aktivní (uživatelské jméno nebo heslo)
    username_input = ""  # Textové pole pro uživatelské jméno
    password_input = ""  # Textové pole pro heslo
    error_message = ""  # Uchovává chybové hlášení v případě neúspěšného přihlášení

    # 🎨 **Načtení pozadí přihlašovací obrazovky**
    try:
        login_bg = pygame.image.load("pozadi9.jpg")
        login_bg = pygame.transform.scale(login_bg, (WIDTH, HEIGHT))  # Přizpůsobení velikosti na celou obrazovku
    except pygame.error as e:
        print(f"Chyba při načítání pozadí: {e}")  # Debug hláška při chybě
        login_bg = pygame.Surface(screen.get_size())  # Vytvoření náhradního povrchu
        login_bg.fill((30, 0, 30))  # Náhradní tmavě fialová barva pozadí

    # 🔄 **Herní smyčka - zajišťuje interaktivitu**
    running = True
    while running:
        screen.blit(login_bg, (0, 0))  # 🖼 Vykreslení pozadí na obrazovku

        # 📌 **Vytvoření obdélníku pro přihlašovací formulář**
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        login_box = pygame.Rect(center_x - 300, center_y - 250, 600, 550)  # Velikost a pozice formuláře
        pygame.draw.rect(screen, (50, 50, 50), login_box, border_radius=20)  # Šedé pozadí
        pygame.draw.rect(screen, (150, 150, 150), login_box, 3, border_radius=20)  # Obrys formuláře

        # 📌 **Nadpis obrazovky**
        draw_gradient_text(screen, "Přihlášení do Betlandia", large_font, (250, 30, 250), (255, 69, 0), (center_x, center_y - 200))

        # 📌 **Vstupní pole pro uživatelské jméno**
        username_rect = pygame.Rect(center_x - 250, center_y - 100, 500, 60)
        pygame.draw.rect(screen, WHITE, username_rect, 2)  # Obrys
        username_text = small_font.render(username_input or "Uživatelské jméno", True, WHITE)
        screen.blit(username_text, (username_rect.x + 15, username_rect.y + 20))  # Zobrazení textu

        # 📌 **Vstupní pole pro heslo**
        password_rect = pygame.Rect(center_x - 250, center_y, 500, 60)
        pygame.draw.rect(screen, WHITE, password_rect, 2)  # Obrys
        password_text = small_font.render("*" * len(password_input) or "Heslo", True, WHITE)  # Nahrazení hesla hvězdičkami
        screen.blit(password_text, (password_rect.x + 15, password_rect.y + 20))

        # 📌 **Zobrazení chybového hlášení, pokud existuje**
        if error_message:
            error_text = small_font.render(error_message, True, RED)
            screen.blit(error_text, (center_x - error_text.get_width() // 2, center_y + 80))

        # 📌 **Tlačítka**
        login_button = pygame.Rect(center_x - 200, center_y + 140, 200, 60)
        draw_button(screen, login_button, "Přihlásit", small_font, GREEN, WHITE)

        register_button = pygame.Rect(center_x + 10, center_y + 140, 200, 60)
        draw_button(screen, register_button, "Registrovat", small_font, BLUE, WHITE)

        back_button = pygame.Rect(center_x - 100, center_y + 230, 200, 60)
        draw_button(screen, back_button, "Menu", small_font, (204, 102, 0), WHITE, shadow_color=(153, 51, 0))

        pygame.display.flip()  # 🔄 Aktualizace obrazovky

        # 🖱 **Zpracování akcí uživatele**
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 🎯 Kliknutí na pole pro uživatelské jméno
                if username_rect.collidepoint(event.pos):
                    input_active = "username"
                # 🎯 Kliknutí na pole pro heslo
                elif password_rect.collidepoint(event.pos):
                    input_active = "password"
                # 🎯 Kliknutí na tlačítko "Přihlásit"
                elif login_button.collidepoint(event.pos):
                    if login_user(username_input, password_input):  # ✅ Úspěšné přihlášení
                        print(f"✅ Přihlášen jako {username_input}")
                        notification_text = f"Uživatel {username_input} se přihlásil."
                        notification_time = time.time()
                        main_menu()
                        return  
                    else:
                        error_message = "Chybné jméno nebo heslo!"  # ❌ Chybné údaje

                # 🎯 Kliknutí na tlačítko "Registrovat"
                elif register_button.collidepoint(event.pos):
                    if register_user(username_input, password_input):  # ✅ Úspěšná registrace
                        login_user(username_input, password_input)  # Automatické přihlášení po registraci
                        print(f"✅ Registrován a přihlášen jako {username_input}")
                        notification_text = f"Uživatel {username_input} se přihlásil."
                        notification_time = time.time()
                        main_menu()
                        return  
                    else:
                        error_message = "Registrace selhala! Možná už existuje účet."  # ❌ Chyba registrace

                # 🎯 Kliknutí na tlačítko "Menu"
                elif back_button.collidepoint(event.pos):
                    print("🔙 Návrat do hlavního menu")
                    return  

            # ⌨ **Zpracování klávesnice (zadávání jména/hesla)**
            elif event.type == pygame.KEYDOWN:
                if input_active == "username":
                    if event.key == pygame.K_BACKSPACE:
                        username_input = username_input[:-1]
                    elif event.key == pygame.K_RETURN:
                        input_active = "password"
                    else:
                        username_input += event.unicode
                elif input_active == "password":
                    if event.key == pygame.K_BACKSPACE:
                        password_input = password_input[:-1]
                    elif event.key == pygame.K_RETURN:
                        if login_user(username_input, password_input):
                            main_menu()
                            return  
                        else:
                            error_message = "❌ Chybné jméno nebo heslo!"
                    else:
                        password_input += event.unicode

def simulate_and_display_results(matches):
    results_surface = pygame.Surface((600, 400))
    results_surface.fill((50, 50, 50))  # Tmavě šedé pozadí pro okno výsledků
    font = pygame.font.Font(None, 30)

    # Přidání tlačítka pro zavření (posunuto více doprava a dolů)
    close_button_rect = pygame.Rect(540, 360, 50, 30)  # Posunutí dolů a doprava
    close_button_text = font.render("X", True, WHITE)

    y_offset = 50  # Začínáme 50 pixelů od horního okraje
    for match in matches:
        # Generování výsledku
        team1_score = random.randint(0, int(match["team1"]["quality"] / 20))
        team2_score = random.randint(0, int(match["team2"]["quality"] / 20))
        match["result"] = f"{match['team1']['name']} {team1_score} - {team2_score} {match['team2']['name']}"

        # Vytvoření a vykreslení textu s výsledkem
        result_text = font.render(match["result"], True, WHITE)
        results_surface.blit(result_text, (50, y_offset))
        y_offset += 40  # Posun o 40 pixelů dolů pro další zápas

    results_position = (WIDTH // 2 - 300, HEIGHT // 2 - 200)
    results_active = True

    while results_active:
        screen.blit(game_bg, (0, 0))  # Vymaže celou obrazovku
        screen.blit(results_surface, results_position)
        pygame.draw.rect(results_surface, RED, close_button_rect)  # Tlačítko zavření na tabulce
        screen.blit(close_button_text, (close_button_rect.x + 15, close_button_rect.y + 5))

        screen.blit(results_surface, results_position)  # Opětovné vykreslení okna výsledků
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Správná detekce kliknutí na tlačítko zavření
                relative_x = event.pos[0] - results_position[0]
                relative_y = event.pos[1] - results_position[1]
                if close_button_rect.collidepoint(relative_x, relative_y):
                    results_active = False  # Zavřít okno výsledků

    # Po zavření okna výsledků překreslíme hlavní obrazovku
    screen.blit(game_bg, (0, 0))
    pygame.display.flip()



def display_teams():
    running = True
    num_per_row = 7
    logo_size = 100
    padding = 150

    total_logo_width = num_per_row * logo_size + (num_per_row - 1) * padding
    start_x = (WIDTH - total_logo_width) // 2

    num_rows = (len(nhl_teams) + num_per_row - 1) // num_per_row
    total_height = num_rows * (logo_size + 30) + (num_rows - 1) * 50
    start_y = (HEIGHT - total_height) // 2

    font_quality = pygame.font.Font(None, 25)

    while running:
        screen.blit(game_bg, (0, 0))

        menu_rect = pygame.Rect(20, HEIGHT - 70, 150, 50)
        pygame.draw.rect(screen, RED, menu_rect)
        menu_text = small_font.render("Menu", True, WHITE)
        screen.blit(menu_text, (menu_rect.x + 10, menu_rect.y + 10))

        x_start = start_x
        y_start = start_y
        team_rects = []

        for team in nhl_teams:
            logo_path = team["logo"]

            try:
                logo = pygame.image.load(logo_path)
                logo = pygame.transform.smoothscale(logo, (logo_size, logo_size))
            except:
                logo = pygame.Surface((logo_size, logo_size))
                logo.fill(GRAY)

            logo_rect = pygame.Rect(x_start, y_start, logo_size, logo_size)
            screen.blit(logo, logo_rect)

            team_name_text = small_font.render(team["name"], True, WHITE)
            text_rect = team_name_text.get_rect(center=(logo_rect.centerx, logo_rect.bottom + 20))
            screen.blit(team_name_text, text_rect)

            team_rects.append((logo_rect, team["quality"]))

            x_start += logo_size + padding

            if len(team_rects) % num_per_row == 0:
                x_start = start_x
                y_start += logo_size + 80

        mouse_pos = pygame.mouse.get_pos()
        for rect, quality in team_rects:
            if rect.collidepoint(mouse_pos):
                dialog_rect = pygame.Rect(mouse_pos[0] + 10, mouse_pos[1] - 25, 120, 30)
                pygame.draw.rect(screen, (30, 30, 30), dialog_rect, border_radius=5)
                pygame.draw.rect(screen, WHITE, dialog_rect, 2, border_radius=5)
                quality_text = font_quality.render(f"Síla týmu: {quality}", True, YELLOW)
                screen.blit(quality_text, (dialog_rect.x + 5, dialog_rect.y + 5))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if menu_rect.collidepoint(event.pos):
                    return

# Hlavní menu
# Funkce pro získání TOP 10 hráčů z databáze
def get_top_players():
    """ Načte TOP 10 hráčů podle nejvyššího dosaženého kapitálu. """
    try:
        db = connect_db()
        cursor = db.cursor()

        # Výběr top 10 hráčů podle maximálního dosaženého kapitálu
        cursor.execute("SELECT username, MAX(balance) FROM betlandia_users GROUP BY username ORDER BY MAX(balance) DESC LIMIT 10")
        top_players = cursor.fetchall()

        cursor.close()
        db.close()
        return top_players  # Vrací seznam [(username, max_balance), ...]
    except mysql.connector.Error as err:
        print(f"❌ Chyba při načítání TOP 10 hráčů: {err}")
        return []  # V případě chyby vrátíme prázdný seznam


# Hlavní menu s tabulkou TOP 10 hráčů
import time



# Globální proměnné pro notifikace
notification_text = None
notification_time = 0

def main_menu():
    global logged_in_user, notification_text, notification_time

    running = True
    while running:
        screen.blit(main_menu_bg, (0, 0))

        # Nadpis hry
        draw_gradient_text(screen, "BETLANDIA", big_font, (250, 30, 250), (255, 69, 0), (WIDTH // 2, HEIGHT // 5))

        # **Notifikace** – pokud existuje a neuplynuly 3 sekundy
        if notification_text and time.time() - notification_time < 3:
            notif_surface = pygame.Surface((500, 50))
            notif_surface.fill((50, 50, 50))  # Tmavé pozadí notifikace
            pygame.draw.rect(notif_surface, (255, 140, 0), notif_surface.get_rect(), 2)  # Oranžový okraj
            notif_text = large_font.render(notification_text, True, (255, 140, 0))  # Oranžová barva textu
            screen.blit(notif_surface, (WIDTH // 2 - 250, 20))
            screen.blit(notif_text, (WIDTH // 2 - notif_text.get_width() // 2, 30))

        # **Definice tlačítek**
        button_width, button_height = 300, 70
        bet_rect = pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT // 2 - 80, button_width, button_height)
        roster_rect = pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT // 2 + 10, button_width, button_height)
        login_rect = pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT // 2 + 100, button_width, button_height)
        quit_rect = pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT // 2 + 190, button_width, button_height)
        

        # **Vykreslení tlačítek**
        draw_button(screen, bet_rect, "Sázet", large_font, (0, 153, 76), WHITE, shadow_color=(0, 102, 51))
        draw_button(screen, roster_rect, "Seznam", large_font, BLUE, WHITE)

        # **Přihlášení/Odhlášení – dynamická barva**
        login_color = (204, 0, 0) if logged_in_user else (255, 140, 0)
        login_text = "Odhlásit se" if logged_in_user else "Přihlášení"
        draw_button(screen, login_rect, login_text, large_font, login_color, WHITE)

        draw_button(screen, quit_rect, "Zpět na plochu", large_font, (204, 0, 0), WHITE, shadow_color=(153, 0, 0))

        # **🛠 Zobrazení TOP 10 hráčů**
        top_players = get_top_players()  # Načte data z databáze
        draw_top_players_table(screen, top_players)  # Vykreslí tabulku

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if login_rect.collidepoint(event.pos):
                    if logged_in_user:
                        # ✅ Nastavení notifikace při odhlášení
                        notification_text = f"Uživatel {logged_in_user} se odhlásil."
                        notification_time = time.time()
                        print(f"❌ {logged_in_user} se odhlásil.")
                        logged_in_user = None
                    else:
                        prev_user = login_screen()  # Přihlášení
                        if prev_user:
                            logged_in_user = prev_user
                            # ✅ Nastavení notifikace při přihlášení
                            notification_text = f"Uživatel {logged_in_user} se přihlásil."
                            notification_time = time.time()
                            print(f"✅ {logged_in_user} se přihlásil.")
                elif bet_rect.collidepoint(event.pos):
                    display_matches()
                elif roster_rect.collidepoint(event.pos):
                    display_teams()
                elif quit_rect.collidepoint(event.pos):
                    running = False

# 🛠 **Funkce pro vykreslení tabulky TOP 10 hráčů**
def draw_top_players_table(surface, top_players):
    """ Vykreslí tabulku s TOP 10 hráči na pravé straně menu. """
    table_x, table_y = WIDTH - 350, HEIGHT // 3  # Umístění tabulky
    table_width, table_height = 300, 400  # Velikost tabulky

    # 🟦 **Vykreslení pozadí tabulky**
    table_rect = pygame.Rect(table_x, table_y, table_width, table_height)
    pygame.draw.rect(surface, (50, 50, 50), table_rect, border_radius=15)
    pygame.draw.rect(surface, WHITE, table_rect, 3, border_radius=15)

    # 🟦 **Nadpis tabulky**
    title_text = large_font.render("TOP 10 Hráčů", True, RED)
    surface.blit(title_text, (table_x + 50, table_y + 15))

    # 🟦 **Zobrazení seznamu hráčů**
    y_offset = table_y + 60  # Startovní pozice prvního hráče
    for i, (username, balance) in enumerate(top_players):
        player_text = small_font.render(f"{i+1}. {username}: ${balance}", True, WHITE)
        surface.blit(player_text, (table_x + 20, y_offset))
        y_offset += 30  # Posun na další řádek

# 🛠 **Funkce pro získání TOP 10 hráčů z databáze**
def get_top_players():
    """ Načte TOP 10 hráčů podle nejvyššího dosaženého kapitálu. """
    try:
        db = connect_db()
        cursor = db.cursor()

        # Výběr top 10 hráčů podle nejvyššího kapitálu
        cursor.execute("SELECT username, balance FROM betlandia_users ORDER BY balance DESC LIMIT 10")
        top_players = cursor.fetchall()

        cursor.close()
        db.close()
        return top_players  # Vrací seznam [(username, balance), ...]
    except mysql.connector.Error as err:
        print(f"❌ Chyba při načítání TOP 10 hráčů: {err}")
        return []  # V případě chyby vrátíme prázdný seznam


if __name__ == "__main__":
    main_menu()

#& "g:/win32app/Portable Python-3.10.5 x64/App/Python/python.exe" -m venv venv
#Set-ExecutionPolicy -Scope CurrentUser
#poté zadej 0
#.\venv\Scripts\activate
#pip install mysql-connector-python
#pip install pygame
#-------------------------------------------------------
#python -m venv venv
#.venv\Scripts\activate
#pip install mysql-connector-python
#pip install pygame


#-----------------------------------------------------