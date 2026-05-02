from flask import Flask, render_template, jsonify
import requests
import json
import os

app = Flask(__name__)
app.secret_key = 'INSERT YOUR OWN APP SECRET KEY' # Make sure to put a random string here in production

HA_URL = "http://192.168.1.93:8123"
HA_TOKEN = "INSERT YOUR OWN HA TOKEN"

CACHE_FILE = 'ha_cache.json'

# --- Cache Helper Functions ---
def load_cache():
    """Loads the last known states from the local JSON file."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache_data):
    """Saves the current states to the local JSON file."""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache_data, f)
    except Exception as e:
        print(f"Failed to write cache: {e}")

# Load the cache into memory when the server starts
LAST_KNOWN_STATE = load_cache()
# ------------------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/ha/<path:entity_id>')
def ha_proxy(entity_id):
    try:
        # Try to get fresh data from Home Assistant
        res = requests.get(
            f"{HA_URL}/api/states/{entity_id}",
            headers={"Authorization": f"Bearer {HA_TOKEN}"},
            timeout=5
        )
        res.raise_for_status() # Force an exception if HA returns a 404 or 500 error
        data = res.json()
        
        # If successful, update our memory dictionary and save it to the file
        LAST_KNOWN_STATE[entity_id] = data
        save_cache(LAST_KNOWN_STATE)
        
        return jsonify(data), 200
        
    except requests.exceptions.RequestException as e:
        # HA is down, timed out, or returning an error!
        # Check if we have this specific entity saved in our cache
        if entity_id in LAST_KNOWN_STATE:
            print(f"HA fetch failed for {entity_id}. Serving cached data.")
            cached_data = LAST_KNOWN_STATE[entity_id]
            return jsonify(cached_data), 200
        else:
            # We have no fresh data AND no cached data. Return a safe fallback.
            return jsonify({"state": "0", "error": "No connection and no cache"}), 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3333, debug=True)
