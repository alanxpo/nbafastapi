from http.server import BaseHTTPRequestHandler
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import json
import time

# Caché simple (en una implementación real, usa una solución de caché distribuida)
cache = {}

def get_player_id(player_name: str):
    player_dict = players.find_players_by_full_name(player_name)
    if player_dict:
        return player_dict[0]['id']
    return None

def get_player_stats(player_id: int, season: str, season_type: str):
    cache_key = f"{player_id}_{season}_{season_type}"
    if cache_key in cache:
        return cache[cache_key]

    gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=season, season_type_all_star=season_type)
    gamelog_df = gamelog.get_data_frames()[0]
    stats = gamelog_df[['GAME_DATE', 'MATCHUP', 'PTS', 'REB', 'AST', 'BLK', 'STL', 'MIN', 'WL']].to_dict(orient='records')
    
    cache[cache_key] = stats
    return stats

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/player-stats':
            player_name = "Joel Embiid"
            season = "2023-24"
            season_type = "Regular Season"

            start_time = time.time()

            player_id = get_player_id(player_name)
            if not player_id:
                self.send_error(404, f"No se encontró al jugador: {player_name}")
                return

            try:
                stats = get_player_stats(player_id, season, season_type)
            except Exception as e:
                self.send_error(500, str(e))
                return

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode())

            print(f"Tiempo de ejecución: {time.time() - start_time} segundos")
        else:
            self.send_error(404)
