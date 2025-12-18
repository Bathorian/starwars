from flask import Flask, render_template, request, g
import sqlite3

app = Flask(__name__)
DATABASE = 'starwars.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    query = request.args.get('q', '').strip()
    return render_template('index.html', query=query)

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return render_template('results.html', results={}, query=query)
    
    db = get_db()
    results = {}
    resources = {
        'people': ['name'],
        'films': ['title'],
        'planets': ['name'],
        'species': ['name'],
        'vehicles': ['name'],
        'starships': ['name']
    }
    
    for resource, fields in resources.items():
        search_results = []
        for field in fields:
            rows = db.execute(f"SELECT id, {field} AS display_name FROM {resource} WHERE {field} LIKE ?", (f'%{query}%',)).fetchall()
            search_results.extend(rows)
        if search_results:
            results[resource] = search_results
            
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('_results_partial.html', results=results, query=query)
            
    return render_template('results.html', results=results, query=query)

@app.route('/resource/<type>/<int:id>')
def detail(type, id):
    query = request.args.get('q', '').strip()
    db = get_db()
    resource = db.execute(f"SELECT * FROM {type} WHERE id = ?", (id,)).fetchone()
    if not resource:
        return "Not Found", 404
    
    # Basic info
    data = dict(resource)
    
    # Handle relationships based on type
    related = {}
    
    if type == 'people':
        # Homeworld
        hw = db.execute("SELECT id, name FROM planets WHERE id = ?", (data['homeworld_id'],)).fetchone()
        related['homeworld'] = hw
        # Films
        films = db.execute("""
            SELECT f.id, f.title FROM films f
            JOIN film_people fp ON f.id = fp.film_id
            WHERE fp.person_id = ?
        """, (id,)).fetchall()
        related['films'] = films
    
    elif type == 'films':
        # Characters
        chars = db.execute("""
            SELECT p.id, p.name FROM people p
            JOIN film_people fp ON p.id = fp.person_id
            WHERE fp.film_id = ?
        """, (id,)).fetchall()
        related['people'] = chars
        # Planets
        planets = db.execute("""
            SELECT pl.id, pl.name FROM planets pl
            JOIN film_planets fpl ON pl.id = fpl.planet_id
            WHERE fpl.film_id = ?
        """, (id,)).fetchall()
        related['planets'] = planets
        
    elif type == 'planets':
        # Residents
        residents = db.execute("SELECT id, name FROM people WHERE homeworld_id = ?", (id,)).fetchall()
        related['people'] = residents
        # Films
        films = db.execute("""
            SELECT f.id, f.title FROM films f
            JOIN film_planets fp ON f.id = fp.film_id
            WHERE fp.planet_id = ?
        """, (id,)).fetchall()
        related['films'] = films

    elif type == 'species':
        # Homeworld
        if data['homeworld_id']:
            hw = db.execute("SELECT id, name FROM planets WHERE id = ?", (data['homeworld_id'],)).fetchone()
            related['homeworld'] = hw
        # People
        people = db.execute("""
            SELECT p.id, p.name FROM people p
            JOIN species_people sp ON p.id = sp.person_id
            WHERE sp.species_id = ?
        """, (id,)).fetchall()
        related['people'] = people
        # Films
        films = db.execute("""
            SELECT f.id, f.title FROM films f
            JOIN film_species fs ON f.id = fs.film_id
            WHERE fs.species_id = ?
        """, (id,)).fetchall()
        related['films'] = films

    elif type == 'vehicles':
        # Pilots
        pilots = db.execute("""
            SELECT p.id, p.name FROM people p
            JOIN vehicle_pilots vp ON p.id = vp.person_id
            WHERE vp.vehicle_id = ?
        """, (id,)).fetchall()
        related['people'] = pilots
        # Films
        films = db.execute("""
            SELECT f.id, f.title FROM films f
            JOIN film_vehicles fv ON f.id = fv.film_id
            WHERE fv.vehicle_id = ?
        """, (id,)).fetchall()
        related['films'] = films

    elif type == 'starships':
        # Pilots
        pilots = db.execute("""
            SELECT p.id, p.name FROM people p
            JOIN starship_pilots sp ON p.id = sp.person_id
            WHERE sp.starship_id = ?
        """, (id,)).fetchall()
        related['people'] = pilots
        # Films
        films = db.execute("""
            SELECT f.id, f.title FROM films f
            JOIN film_starships fs ON f.id = fs.film_id
            WHERE fs.starship_id = ?
        """, (id,)).fetchall()
        related['films'] = films

    # Add more relationships for other types as needed
    
    return render_template('detail.html', type=type, data=data, related=related, query=query)

if __name__ == '__main__':
    app.run(debug=True)
