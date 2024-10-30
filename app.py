from flask import Flask, jsonify
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players

app = Flask(__name__)

def get_jayson_tatum_last_5_games():
    # Buscar el ID de Jayson Tatum
    player = players.find_players_by_full_name("Jayson Tatum")[0]
    player_id = player["id"]

    # Obtener el registro de juegos de Jayson Tatum
    game_log = playergamelog.PlayerGameLog(player_id=player_id, season='2022-23')
    games = game_log.get_data_frames()[0]

    # Seleccionar los últimos 5 juegos
    last_5_games = games.head(5)

    # Extraer datos relevantes de los últimos 5 juegos
    game_data = []
    for _, row in last_5_games.iterrows():
        game_info = {
            "game_date": row["GAME_DATE"],
            "matchup": row["MATCHUP"],
            "points": row["PTS"],
            "rebounds": row["REB"],
            "assists": row["AST"],
            "steals": row["STL"],
            "blocks": row["BLK"],
            "field_goal_percentage": row["FG_PCT"] * 100,
            "three_point_percentage": row["FG3_PCT"] * 100,
            "free_throw_percentage": row["FT_PCT"] * 100
        }
        game_data.append(game_info)
    
    return game_data

@app.route('/', methods=['GET'])
def jayson_last_5_games():
    stats = get_jayson_tatum_last_5_games()
    return jsonify(stats)

if __name__ == '__main__':
    app.run()
