# Pokémon Creature Loader: Flask Web App

A small full-stack web application that pulls live data from the public [PokéAPI](https://pokeapi.co/), normalizes it, and stores it in a local SQLite database. Users can browse, add, edit and delete Pokémon through a clean server-rendered interface.

Built as a final project for my Programming 2 course, it shows how I structure a Python web app around clear separation of concerns.

## Features

- **Browse** all saved Pokémon (ID, name, height, weight, types, base stats)
- **Add** a Pokémon by typing only its name or ID; the app fetches and saves the rest automatically
- **Edit** the stored data of an existing Pokémon
- **Delete** entries, with a confirmation prompt
- **Error handling** for unknown Pokémon, network failures and timeouts, with feedback shown to the user
- **Custom 404 page**

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3 |
| Web framework | Flask |
| Database | SQLite |
| ORM | Flask-SQLAlchemy / SQLAlchemy |
| Migrations | Flask-Migrate (Alembic) |
| HTTP client | `requests` |
| Templating | Jinja2 (HTML) |

## Architecture (MVT)

The project follows the **Model–View–Template** pattern, with each concern kept separate:

- **Model**: the `Creature` SQLAlchemy model (`id`, `name`, `height`, `weight`, `types`, `stats`). Types and stats are stored as serialized JSON.
- **View**: Flask routes (`/`, `/add`, `/edit/<id>`, `/delete/<id>`) that handle the request flow.
- **Template**: Jinja2 pages (`index.html`, `add.html`, `edit.html`, `404.html`).
- **HTTP Reader**: a dedicated `PokemonReader` class that calls the PokéAPI and returns a clean dictionary. It never writes to the database, so API logic and persistence stay decoupled.

## What This Project Demonstrates

- Consuming a **third-party REST API** with timeouts and layered exception handling (`ConnectionError`, `Timeout`, `HTTPError`, `KeyError`)
- Turning raw JSON into a **normalized data structure** before it reaches the database
- **CRUD operations** with the SQLAlchemy ORM
- **Database versioning** with Alembic migrations
- Safe use of **HTTP methods**: destructive actions go through `POST`, not `GET`
- Clean, readable code with separation between HTTP, database and rendering logic

## Getting Started

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

# 2. Create a virtual environment and install dependencies
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Initialize the database
flask --app dbPokemon db upgrade

# 4. Run the app
python dbPokemon.py
```

Then open **http://127.0.0.1:5000** in your browser.

## Project Structure

```
├── dbPokemon.py          # Flask app, model, reader and routes
├── requirements.txt
├── templates/
│   ├── index.html        # Pokémon list
│   ├── add.html          # Add form
│   ├── edit.html         # Edit form
│   └── 404.html          # Error page
└── migrations/           # Alembic migration scripts
```

## Possible Improvements

- Add CSS styling and a responsive layout
- Display types and stats in a readable format instead of raw JSON
- Add server-side validation and handling of duplicate entries
- Add search, pagination and sorting
- Add automated tests (pytest) and Docker support

## About Me

I'm a developer focused on Python and web development, open to internships and junior roles. Feel free to reach out.

📧 pblancato@stevejobs.academy
