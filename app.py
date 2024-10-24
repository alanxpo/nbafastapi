from flask import Flask, jsonify
from flask_cors import CORS
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import pandas as pd

# Crear instancia de Flask
app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

# Función para obtener el ID del jugador por nombre
def get_player_id(player_name: str):
    player_dict = players.find_players_by_full_name(player_name)
    if player_dict:
        return player_dict[0]['id']
    return None

# Función para obtener las estadísticas del jugador
def get_player_stats(player_id: int, season: str, season_type: str):
    gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=season, season_type_all_star=season_type)
    gamelog_df = gamelog.get_data_frames()[0]
    return gamelog_df

# Endpoint que muestra las estadísticas de Joel Embiid
@app.route("/api/py/player-stats", methods=["GET"])
def player_stats():
    # Valores fijos para Joel Embiid
    player_name = "Joel Embiid"
    season = "2023-24"
    season_type = "Regular Season"

    # Obtener el ID del jugador
    player_id = get_player_id(player_name)
    if not player_id:
        return jsonify({"error": f"No se encontró al jugador: {player_name}"}), 404

    # Obtener las estadísticas del jugador
    try:
        player_stats_df = get_player_stats(player_id, season, season_type)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Convertir el DataFrame a diccionario para devolver como JSON
    stats_json = player_stats_df[['GAME_DATE', 'MATCHUP', 'PTS', 'REB', 'AST', 'BLK', 'STL', 'MIN', 'WL']].to_dict(orient='records')

    return jsonify(stats_json)

if __name__ == "__main__":
    app.run(debug=True)
