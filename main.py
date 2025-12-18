import requests
import sqlite3
import json
import re

BASE_URL = "https://swapi.info/api"
RESOURCES = ['planets', 'people', 'films', 'species', 'vehicles', 'starships']
DB_NAME = "starwars.db"

def extract_id(url):
    if not url or not isinstance(url, str):
        return None
    match = re.search(r'/(\d+)/?$', url)
    return int(match.group(1)) if match else None

def fetch_data(resource):
    print(f"Fetching data for {resource}...")
    response = requests.get(f"{BASE_URL}/{resource}")
    response.raise_for_status()
    return response.json()

def setup_database(conn):
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")

    # Drop existing tables and junction tables
    tables = ['film_people', 'film_planets', 'film_starships', 'film_vehicles', 'film_species', 
              'species_people', 'starship_pilots', 'vehicle_pilots',
              'films', 'people', 'planets', 'species', 'vehicles', 'starships']
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")

    # Create Core Tables
    cursor.execute("""
        CREATE TABLE planets (
            id INTEGER PRIMARY KEY,
            name TEXT,
            rotation_period TEXT,
            orbital_period TEXT,
            diameter TEXT,
            climate TEXT,
            gravity TEXT,
            terrain TEXT,
            surface_water TEXT,
            population TEXT,
            created TEXT,
            edited TEXT,
            url TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE people (
            id INTEGER PRIMARY KEY,
            name TEXT,
            height TEXT,
            mass TEXT,
            hair_color TEXT,
            skin_color TEXT,
            eye_color TEXT,
            birth_year TEXT,
            gender TEXT,
            homeworld_id INTEGER,
            created TEXT,
            edited TEXT,
            url TEXT,
            FOREIGN KEY (homeworld_id) REFERENCES planets(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE films (
            id INTEGER PRIMARY KEY,
            title TEXT,
            episode_id INTEGER,
            opening_crawl TEXT,
            director TEXT,
            producer TEXT,
            release_date TEXT,
            created TEXT,
            edited TEXT,
            url TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE species (
            id INTEGER PRIMARY KEY,
            name TEXT,
            classification TEXT,
            designation TEXT,
            average_height TEXT,
            skin_colors TEXT,
            hair_colors TEXT,
            eye_colors TEXT,
            average_lifespan TEXT,
            language TEXT,
            homeworld_id INTEGER,
            created TEXT,
            edited TEXT,
            url TEXT,
            FOREIGN KEY (homeworld_id) REFERENCES planets(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE vehicles (
            id INTEGER PRIMARY KEY,
            name TEXT,
            model TEXT,
            manufacturer TEXT,
            cost_in_credits TEXT,
            length TEXT,
            max_atmosphering_speed TEXT,
            crew TEXT,
            passengers TEXT,
            cargo_capacity TEXT,
            consumables TEXT,
            vehicle_class TEXT,
            created TEXT,
            edited TEXT,
            url TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE starships (
            id INTEGER PRIMARY KEY,
            name TEXT,
            model TEXT,
            manufacturer TEXT,
            cost_in_credits TEXT,
            length TEXT,
            max_atmosphering_speed TEXT,
            crew TEXT,
            passengers TEXT,
            cargo_capacity TEXT,
            consumables TEXT,
            hyperdrive_rating TEXT,
            MGLT TEXT,
            starship_class TEXT,
            created TEXT,
            edited TEXT,
            url TEXT
        )
    """)

    # Create Junction Tables
    cursor.execute("""
        CREATE TABLE film_people (
            film_id INTEGER,
            person_id INTEGER,
            PRIMARY KEY (film_id, person_id),
            FOREIGN KEY (film_id) REFERENCES films(id),
            FOREIGN KEY (person_id) REFERENCES people(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE film_planets (
            film_id INTEGER,
            planet_id INTEGER,
            PRIMARY KEY (film_id, planet_id),
            FOREIGN KEY (film_id) REFERENCES films(id),
            FOREIGN KEY (planet_id) REFERENCES planets(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE film_starships (
            film_id INTEGER,
            starship_id INTEGER,
            PRIMARY KEY (film_id, starship_id),
            FOREIGN KEY (film_id) REFERENCES films(id),
            FOREIGN KEY (starship_id) REFERENCES starships(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE film_vehicles (
            film_id INTEGER,
            vehicle_id INTEGER,
            PRIMARY KEY (film_id, vehicle_id),
            FOREIGN KEY (film_id) REFERENCES films(id),
            FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE film_species (
            film_id INTEGER,
            species_id INTEGER,
            PRIMARY KEY (film_id, species_id),
            FOREIGN KEY (film_id) REFERENCES films(id),
            FOREIGN KEY (species_id) REFERENCES species(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE species_people (
            species_id INTEGER,
            person_id INTEGER,
            PRIMARY KEY (species_id, person_id),
            FOREIGN KEY (species_id) REFERENCES species(id),
            FOREIGN KEY (person_id) REFERENCES people(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE starship_pilots (
            starship_id INTEGER,
            person_id INTEGER,
            PRIMARY KEY (starship_id, person_id),
            FOREIGN KEY (starship_id) REFERENCES starships(id),
            FOREIGN KEY (person_id) REFERENCES people(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE vehicle_pilots (
            vehicle_id INTEGER,
            person_id INTEGER,
            PRIMARY KEY (vehicle_id, person_id),
            FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
            FOREIGN KEY (person_id) REFERENCES people(id)
        )
    """)
    conn.commit()

def populate_resource(conn, resource, data):
    cursor = conn.cursor()
    print(f"Populating {resource}...")
    
    for item in data:
        item_id = extract_id(item['url'])
        
        if resource == 'planets':
            cursor.execute("""
                INSERT INTO planets (id, name, rotation_period, orbital_period, diameter, climate, gravity, terrain, surface_water, population, created, edited, url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (item_id, item.get('name'), item.get('rotation_period'), item.get('orbital_period'), item.get('diameter'), item.get('climate'), item.get('gravity'), item.get('terrain'), item.get('surface_water'), item.get('population'), item.get('created'), item.get('edited'), item.get('url')))
            
        elif resource == 'people':
            cursor.execute("""
                INSERT INTO people (id, name, height, mass, hair_color, skin_color, eye_color, birth_year, gender, homeworld_id, created, edited, url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (item_id, item.get('name'), item.get('height'), item.get('mass'), item.get('hair_color'), item.get('skin_color'), item.get('eye_color'), item.get('birth_year'), item.get('gender'), extract_id(item.get('homeworld')), item.get('created'), item.get('edited'), item.get('url')))
            
        elif resource == 'films':
            cursor.execute("""
                INSERT INTO films (id, title, episode_id, opening_crawl, director, producer, release_date, created, edited, url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (item_id, item.get('title'), item.get('episode_id'), item.get('opening_crawl'), item.get('director'), item.get('producer'), item.get('release_date'), item.get('created'), item.get('edited'), item.get('url')))
            
        elif resource == 'species':
            cursor.execute("""
                INSERT INTO species (id, name, classification, designation, average_height, skin_colors, hair_colors, eye_colors, average_lifespan, language, homeworld_id, created, edited, url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (item_id, item.get('name'), item.get('classification'), item.get('designation'), item.get('average_height'), item.get('skin_colors'), item.get('hair_colors'), item.get('eye_colors'), item.get('average_lifespan'), item.get('language'), extract_id(item.get('homeworld')), item.get('created'), item.get('edited'), item.get('url')))
            
        elif resource == 'vehicles':
            cursor.execute("""
                INSERT INTO vehicles (id, name, model, manufacturer, cost_in_credits, length, max_atmosphering_speed, crew, passengers, cargo_capacity, consumables, vehicle_class, created, edited, url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (item_id, item.get('name'), item.get('model'), item.get('manufacturer'), item.get('cost_in_credits'), item.get('length'), item.get('max_atmosphering_speed'), item.get('crew'), item.get('passengers'), item.get('cargo_capacity'), item.get('consumables'), item.get('vehicle_class'), item.get('created'), item.get('edited'), item.get('url')))
            
        elif resource == 'starships':
            cursor.execute("""
                INSERT INTO starships (id, name, model, manufacturer, cost_in_credits, length, max_atmosphering_speed, crew, passengers, cargo_capacity, consumables, hyperdrive_rating, MGLT, starship_class, created, edited, url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (item_id, item.get('name'), item.get('model'), item.get('manufacturer'), item.get('cost_in_credits'), item.get('length'), item.get('max_atmosphering_speed'), item.get('crew'), item.get('passengers'), item.get('cargo_capacity'), item.get('consumables'), item.get('hyperdrive_rating'), item.get('MGLT'), item.get('starship_class'), item.get('created'), item.get('edited'), item.get('url')))

    conn.commit()

def populate_junctions(conn, resource, data):
    cursor = conn.cursor()
    print(f"Populating junctions for {resource}...")
    
    for item in data:
        item_id = extract_id(item['url'])
        
        if resource == 'films':
            for url in item.get('characters', []):
                cursor.execute("INSERT OR IGNORE INTO film_people (film_id, person_id) VALUES (?, ?)", (item_id, extract_id(url)))
            for url in item.get('planets', []):
                cursor.execute("INSERT OR IGNORE INTO film_planets (film_id, planet_id) VALUES (?, ?)", (item_id, extract_id(url)))
            for url in item.get('starships', []):
                cursor.execute("INSERT OR IGNORE INTO film_starships (film_id, starship_id) VALUES (?, ?)", (item_id, extract_id(url)))
            for url in item.get('vehicles', []):
                cursor.execute("INSERT OR IGNORE INTO film_vehicles (film_id, vehicle_id) VALUES (?, ?)", (item_id, extract_id(url)))
            for url in item.get('species', []):
                cursor.execute("INSERT OR IGNORE INTO film_species (film_id, species_id) VALUES (?, ?)", (item_id, extract_id(url)))
                
        elif resource == 'species':
            for url in item.get('people', []):
                cursor.execute("INSERT OR IGNORE INTO species_people (species_id, person_id) VALUES (?, ?)", (item_id, extract_id(url)))
                
        elif resource == 'starships':
            for url in item.get('pilots', []):
                cursor.execute("INSERT OR IGNORE INTO starship_pilots (starship_id, person_id) VALUES (?, ?)", (item_id, extract_id(url)))
                
        elif resource == 'vehicles':
            for url in item.get('pilots', []):
                cursor.execute("INSERT OR IGNORE INTO vehicle_pilots (vehicle_id, person_id) VALUES (?, ?)", (item_id, extract_id(url)))

    conn.commit()

def main():
    conn = sqlite3.connect(DB_NAME)
    setup_database(conn)
    
    all_data = {}
    
    # First pass: Fetch and populate main tables
    for resource in RESOURCES:
        try:
            data = fetch_data(resource)
            all_data[resource] = data
            populate_resource(conn, resource, data)
        except Exception as e:
            print(f"Error processing {resource}: {e}")
            
    # Second pass: Populate junction tables
    for resource, data in all_data.items():
        try:
            populate_junctions(conn, resource, data)
        except Exception as e:
            print(f"Error populating junctions for {resource}: {e}")
            
    conn.close()
    print("Relational database created and populated successfully.")

if __name__ == "__main__":
    main()