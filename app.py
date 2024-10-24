from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import pandas as pd


### Create FastAPI instance with custom docs and openapi url
app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las fuentes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Endpoint que recibe el nombre del jugador, la temporada y el tipo de temporada
@app.get("/api/py/player-stats")
def player_stats(
    player_name: str = Query(..., alias="name"), 
    season: str = Query(...), 
    season_type: str = Query('Regular Season')
):
    # Obtener el ID del jugador
    player_id = get_player_id(player_name)
    if not player_id:
        raise HTTPException(status_code=404, detail=f"No se encontró al jugador: {player_name}")

    # Obtener las estadísticas del jugador
    try:
        player_stats_df = get_player_stats(player_id, season, season_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Mostrar todos los juegos
    all_games = player_stats_df

    # Convertir el DataFrame a diccionario para devolver como JSON
    stats_json = all_games[['GAME_DATE', 'MATCHUP', 'PTS', 'REB', 'AST', 'BLK', 'STL', 'MIN', 'WL']].to_dict(orient='records')

    return stats_json
