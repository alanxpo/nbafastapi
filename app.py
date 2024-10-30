from flask import Flask, request, jsonify
from flask_cors import CORS  # Importar CORS
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
from nba_api.live.nba.endpoints import scoreboard
import pandas as pd
import json

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

headers = {
    'Host': 'stats.nba.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://stats.nba.com/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

# Función para obtener el ID del jugador por nombre
def get_player_id(player_name):
    player_dict = players.find_players_by_full_name(player_name)
    if player_dict:
        return player_dict[0]['id']
    return None

# Función para obtener las estadísticas del jugador
def get_player_stats(player_id, season, season_type):
    gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=season, season_type_all_star=season_type,headers=headers,
        timeout=10)
    gamelog_df = gamelog.get_data_frames()[0]
    return gamelog_df

# Endpoint que recibe el nombre del jugador, la temporada y el tipo de temporada
@app.route('/player-stats', methods=['GET'])
def player_stats():
    # Obtener los parámetros de la solicitud
    player_name = request.args.get('name')
    season = request.args.get('season')
    season_type = request.args.get('season_type', 'Regular Season')  # Valor por defecto: temporada regular

    # Validar que los parámetros necesarios están presentes
    if not player_name or not season:
        return jsonify({'error': 'Por favor proporcione el nombre del jugador y la temporada.'}), 400

    # Obtener el ID del jugador
    player_id = get_player_id(player_name)
    if not player_id:
        return jsonify({'error': f'No se encontró al jugador: {player_name}'}), 404

    # Obtener las estadísticas del jugador
    try:
        player_stats_df = get_player_stats(player_id, season, season_type)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Mostrar todos los juegos
    all_games = player_stats_df

    # Convertir el DataFrame a diccionario para devolver como JSON
    stats_json = all_games[['GAME_DATE', 'MATCHUP', 'PTS', 'REB', 'AST', 'BLK', 'STL', 'MIN', 'WL']].to_dict(orient='records')

    return jsonify(stats_json)

@app.route('/')
def home():
    return "Bienvenido al Live NBA Scoreboard API"

@app.route('/live_scores', methods=['GET'])
def live_scores():
    try:
        # Obtener el marcador en vivo desde nba_api
        games_scoreboard = scoreboard.ScoreBoard()
        games_data = games_scoreboard.get_dict()  # Convertir a dict

        # Extraer la información relevante del scoreboard
        live_scores = []
        for game in games_data['scoreboard']['games']:
            home_leader = game.get('gameLeaders', {}).get('homeLeaders', {})
            away_leader = game.get('gameLeaders', {}).get('awayLeaders', {})

            game_info = {
                'gameId': game['gameId'],
                'homeTeam': game['homeTeam']['teamName'],
                'awayTeam': game['awayTeam']['teamName'],
                'homeScore': game['homeTeam']['score'],
                'awayScore': game['awayTeam']['score'],
                'status': game['gameStatusText'],
                'homeLeader': {
                    'name': home_leader.get('name', 'N/A'),
                    'points': home_leader.get('points', 0),
                    'rebounds': home_leader.get('rebounds', 0),
                    'assists': home_leader.get('assists', 0)
                },
                'awayLeader': {
                    'name': away_leader.get('name', 'N/A'),
                    'points': away_leader.get('points', 0),
                    'rebounds': away_leader.get('rebounds', 0),
                    'assists': away_leader.get('assists', 0)
                }
            }
            live_scores.append(game_info)

        return jsonify(live_scores)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


