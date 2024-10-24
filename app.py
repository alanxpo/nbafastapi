from flask import Flask, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Simulated cache (in a real scenario, use a proper caching solution)
cache = {}

def get_cached_data(key, expiry_minutes=60):
    if key in cache:
        data, timestamp = cache[key]
        if datetime.now() - timestamp < timedelta(minutes=expiry_minutes):
            return data
    return None

def set_cached_data(key, data):
    cache[key] = (data, datetime.now())

@app.route("/api/py/player-stats", methods=["GET"])
def player_stats():
    player_name = "Joel Embiid"
    season = "2023-24"
    season_type = "Regular Season"

    cache_key = f"{player_name}_{season}_{season_type}"
    cached_data = get_cached_data(cache_key)

    if cached_data:
        return jsonify(cached_data)

    # Simulated data (replace this with actual API call in a separate function)
    stats_json = [
        {"GAME_DATE": "2023-10-30", "MATCHUP": "PHI vs. POR", "PTS": 35, "REB": 15, "AST": 7, "BLK": 2, "STL": 1, "MIN": 36, "WL": "W"},
        {"GAME_DATE": "2023-11-01", "MATCHUP": "PHI @ WAS", "PTS": 29, "REB": 12, "AST": 5, "BLK": 3, "STL": 0, "MIN": 33, "WL": "W"},
    ]

    set_cached_data(cache_key, stats_json)
    return jsonify(stats_json)

if __name__ == "__main__":
    app.run(debug=True)
