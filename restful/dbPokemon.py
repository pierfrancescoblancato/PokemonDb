import json
import requests
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Inizializzazione
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
    types = db.Column(db.Text, nullable=False)
    stats = db.Column(db.Text, nullable=False)

class PokemonReader:
    def fetch_as_dict(self, name_or_id: str):
        url = f"https://pokeapi.co/api/v2/pokemon/{name_or_id.lower().strip()}"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status() 
            
            data = response.json()
            
            types = []
            for t in data['types']:
                types.append(t['type']['name'])
                
            stats = {}        
            for stats_item in data['stats']:
                stats[stats_item['stat']['name']] = stats_item['base_stat']
                
            return {
                'id': data['id'],
                'name': data['name'],
                'height': data['height'],
                'weight': data['weight'],
                'types': types,
                'stats': stats
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

# Rotte
@app.route('/')
def index():
    creatures = Creature.query.all()
    return render_template('index.html', creatures=creatures)

@app.route('/add', methods=['GET', 'POST'])
def add_pokemon():
    error_message = None
    if request.method == 'POST':
        name = request.form['name'].strip().lower()
        
        reader = PokemonReader()
        data = reader.fetch_as_dict(name)
        
        if data:
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
        else:
            error_message = f"Cannot find Pokémon '{name}' or network error."
            
    return render_template('add.html', creature=None, error=error_message)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_pokemon(id):
    creature = Creature.query.get_or_404(id)
    if request.method == 'POST':
        creature.height = int(request.form['height'])
        creature.weight = int(request.form['weight'])
        
        creature.types = request.form.get('types', '')
        creature.stats = request.form.get('stats', '')
        
        db.session.commit()
        return redirect(url_for('index'))
        
    return render_template('edit.html', creature=creature)

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