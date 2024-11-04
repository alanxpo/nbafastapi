import requests
import pandas as pd
from typing import Dict, Any
from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS
import json
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for the app

class NBAStats:
    BASE_URL = "https://stats.nba.com/stats/"
    
    # Diccionario de jugadores conocidos y sus IDs
    KNOWN_PLAYERS = {
        'lebron james': 2544,
        'stephen curry': 201939,
        'kevin durant': 201142,
        'luka doncic': 1629029,
        'giannis antetokounmpo': 203507,
        'nikola jokic': 203999,
        'joel embiid': 203954,
        'jayson tatum': 1628369,
        'ja morant': 1629630,
        'devin booker': 1626164,
        'trae young': 1629027,
        'donovan mitchell': 1628378,
        'anthony davis': 203076,
        'damian lillard': 203081,
        'jimmy butler': 202710,
        'paul george': 202331,
        'kawhi leonard': 202695,
        'kyrie irving': 202681,
        'anthony edwards': 1630162,
        'shai gilgeous alexander': 1628983,
        'victor wembanyama': 1641705
    }
    
    HEADERS = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Host': 'stats.nba.com',
        'Origin': 'https://www.nba.com',
        'Referer': 'https://www.nba.com/',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def normalize_name(self, name: str) -> str:
        """Normaliza el nombre del jugador para la búsqueda"""
        # Convierte a minúsculas y elimina espacios extra
        return re.sub(r'\s+', ' ', name.lower().strip())

    def find_player_id(self, player_name: str) -> int:
        """Busca el ID del jugador usando el diccionario de jugadores conocidos"""
        normalized_name = self.normalize_name(player_name)
        
        # Búsqueda exacta
        if normalized_name in self.KNOWN_PLAYERS:
            return self.KNOWN_PLAYERS[normalized_name]
        
        # Búsqueda parcial
        for known_name, player_id in self.KNOWN_PLAYERS.items():
            if normalized_name in known_name or known_name in normalized_name:
                return player_id
        
        return None

    def get_player_info(self, player_id: int) -> Dict[str, Any]:
        """Obtiene información básica del jugador"""
        endpoint = "commonplayerinfo"
        params = {
            'PlayerID': player_id,
            'LeagueID': '00'
        }

        try:
            response = self.session.get(
                f"{self.BASE_URL}{endpoint}",
                params=params,
                timeout=30,
                allow_redirects=False
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener información del jugador: {e}")
            return {}

    def get_player_game_logs(self, player_id: int, season: str = "2023-24", last_n_games: int = 10) -> pd.DataFrame:
        """Obtiene estadísticas de los últimos N juegos de un jugador"""
        endpoint = "playergamelog"
        params = {
            'PlayerID': player_id,
            'Season': season,
            'SeasonType': 'Regular Season',
            'LastNGames': last_n_games
        }

        try:
            response = self.session.get(
                f"{self.BASE_URL}{endpoint}",
                params=params,
                timeout=30,
                allow_redirects=False
            )
            response.raise_for_status()
            data = response.json()
            
            headers = data['resultSets'][0]['headers']
            rows = data['resultSets'][0]['rowSet']
            df = pd.DataFrame(rows, columns=headers)
            
            df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
            
            columns_of_interest = [
                'GAME_DATE', 'MATCHUP', 'WL',
                'MIN', 'PTS', 'FGM', 'FGA', 'FG_PCT',
                'FG3M', 'FG3A', 'FG3_PCT',
                'FTM', 'FTA', 'FT_PCT',
                'REB', 'AST', 'STL', 'BLK', 'TOV'
            ]
            
            return df[columns_of_interest]
            
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener estadísticas del jugador: {e}")
            return pd.DataFrame()

# Instancia global de NBAStats
nba_stats = NBAStats()

@app.route('/player/stats', methods=['GET'])
def get_player_stats():
    player_name = request.args.get('name')
    if not player_name:
        return jsonify({'error': 'Se requiere el nombre del jugador'}), 400
    
    # Buscar ID del jugador usando el nuevo método
    player_id = nba_stats.find_player_id(player_name)
    if not player_id:
        return jsonify({'error': 'Jugador no encontrado. Asegúrate de escribir el nombre completo correctamente.'}), 404
    
    # Obtener información del jugador
    player_info = nba_stats.get_player_info(player_id)
    if not player_info:
        return jsonify({'error': 'No se pudo obtener información del jugador'}), 500
    
    player_name = player_info['resultSets'][0]['rowSet'][0][3]
    
    # Obtener los últimos 10 juegos
    game_logs = nba_stats.get_player_game_logs(player_id, last_n_games=10)
    if game_logs.empty:
        return jsonify({'error': 'No se encontraron estadísticas recientes'}), 404
    
    # Convertir DataFrame a formato JSON
    game_logs['GAME_DATE'] = game_logs['GAME_DATE'].dt.strftime('%Y-%m-%d')
    games_list = game_logs.to_dict('records')
    
    response = {
        'player_name': player_name,
        'last_10_games': games_list
    }
    
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
