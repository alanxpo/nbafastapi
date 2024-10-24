from flask import Flask, jsonify
from flask_cors import CORS  # Importar CORS
from nba_api.live.nba.endpoints import scoreboard
import json

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

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
