import json
import requests
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pokemon.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Creature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    height = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)     
    types = db.Column(db.Text(300), nullable=False)
    stats = db.Column(db.Text(300), nullable=False)

class PokemonReader:
    BASE_URL = "https://pokeapi.co/api/v2/pokemon"

    def fetch_as_dict(self, name_or_id: str):
        url = f"{self.BASE_URL}/{name_or_id}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return {
                    'id': data['id'],
                    'name': data['name'],
                    'height': data['height'],
                    'weight': data['weight'],
                    'types': [t['type']['name'] for t in data['types']],
                    'stats': {s['stat']['name']: s['base_stat'] for s in data['stats']}
                }
        except requests.exceptions.ConnectionError:
            print("Error: unable to connect. Check your internet connection.")
        except requests.exceptions.Timeout:
            print("Error: the server did not respond in time (timeout).")
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e.response.status_code} — Pokemon '{name_or_id}' not found.")
        except requests.exceptions.RequestException as e:
            print(f"Unexpected network error: {e}")
        except KeyError as e:
            print(f"Error: unexpected API response structure — missing key: {e}")
        return None

@app.route('/')
def index():
    creatures = Creature.query.all()
    return render_template('index.html', creatures=creatures)

@app.route('/add', methods=['GET', 'POST'])
def add_pokemon():
    error = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip().lower()
        if not name:
            error = "Please enter a Pokémon name."
            return render_template('add.html', error=error)

        reader = PokemonReader()
        data = reader.fetch_as_dict(name)
        if data is None:
            error = f"Pokémon '{name}' not found or network error."
            return render_template('add.html', error=error)

        if Creature.query.get(data['id']):
            error = f"Pokémon '{data['name']}' (ID #{data['id']}) already exists."
            return render_template('add.html', error=error)

        new_creature = Creature(
            id=data['id'],
            name=data['name'],
            height=data['height'],
            weight=data['weight'],
            types=json.dumps(data['types']),
            stats=json.dumps(data['stats'])
        )
        db.session.add(new_creature)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add.html', error=error)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_pokemon(id):
    creature = Creature.query.get_or_404(id)
    error = None
    if request.method == 'POST':
        try:
            creature.height = int(request.form['height'])
            creature.weight = int(request.form['weight'])
            if request.form.get('types'):
                json.loads(request.form['types']) 
                creature.types = request.form['types']
            if request.form.get('stats'):
                json.loads(request.form['stats'])
                creature.stats = request.form['stats']
            db.session.commit()
            return redirect(url_for('index'))
        except (ValueError, json.JSONDecodeError) as e:
            error = f"Invalid data: {e}"

    current_types = json.dumps(json.loads(creature.types), indent=2)
    current_stats = json.dumps(json.loads(creature.stats), indent=2)
    return render_template('edit.html', creature=creature,
                           current_types=current_types,
                           current_stats=current_stats,
                           error=error)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_pokemon(id):
    creature = Creature.query.get_or_404(id)
    db.session.delete(creature)
    db.session.commit()

    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

if __name__ == '__main__':
    app.run(debug=True)