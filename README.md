# Star Wars Search Engine

A Flask-based search engine for the Star Wars universe, powered by data from [swapi.info](https://swapi.info/).

## Why this won't work on GitHub Pages
GitHub Pages is a **static** hosting service. It only serves HTML, CSS, and JavaScript files directly to the browser. It **cannot** run Python code or host a SQLite database.

Since this application uses:
1. **Flask (Python)**: To handle requests and routing.
2. **SQLite**: To store and query the Star Wars data.

It requires a server-side environment to function.

## How to deploy this application

To make this app available online, you should use a platform that supports Python/Flask. Here are some popular options:

### 1. Render (Recommended)
1. Create a free account on [Render](https://render.com/).
2. Connect your GitHub repository.
3. Create a new "Web Service".
4. Use the following settings:
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements.txt; python main.py`
   - **Start Command**: `gunicorn app:app`

### 2. PythonAnywhere
Excellent for Flask apps and supports SQLite perfectly.

### 3. Railway / Fly.io
Other great alternatives for hosting dynamic applications.

## Local Setup
If you want to run it locally:
1. Install dependencies: `pip install -r requirements.txt`
2. Populate the database (if not already done): `python main.py`
3. Run the app: `python app.py`
4. Open `http://127.0.0.1:5000` in your browser.