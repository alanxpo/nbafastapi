const express = require('express');
const axios = require('axios');
const cors = require('cors');
const app = express();
app.use(cors());  // Enable CORS for the app

app.get("/", (req, res) => res.send("Express on Vercel"));

class NBAStats {
    static BASE_URL = "https://stats.nba.com/stats/";

    // Dictionary of known players and their IDs
    static KNOWN_PLAYERS = {
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
    };

    static HEADERS = {
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
    };

    normalizeName(name) {
        // Normalize player name for search
        return name.toLowerCase().trim().replace(/\s+/g, ' ');
    }

    findPlayerId(playerName) {
        const normalizedName = this.normalizeName(playerName);

        // Exact search
        if (NBAStats.KNOWN_PLAYERS[normalizedName]) {
            return NBAStats.KNOWN_PLAYERS[normalizedName];
        }

        // Partial search
        for (const [knownName, playerId] of Object.entries(NBAStats.KNOWN_PLAYERS)) {
            if (normalizedName.includes(knownName) || knownName.includes(normalizedName)) {
                return playerId;
            }
        }

        return null;
    }

    async getPlayerInfo(playerId) {
        const endpoint = "commonplayerinfo";
        const params = {
            PlayerID: playerId,
            LeagueID: '00'
        };

        try {
            const response = await axios.get(`${NBAStats.BASE_URL}${endpoint}`, {
                headers: NBAStats.HEADERS,
                params: params,
                timeout: 30000
            });
            return response.data;
        } catch (error) {
            console.error(`Error getting player info: ${error}`);
            return {};
        }
    }

    async getPlayerGameLogs(playerId, season = "2023-24", lastNGames = 10) {
        const endpoint = "playergamelog";
        const params = {
            PlayerID: playerId,
            Season: season,
            SeasonType: 'Regular Season',
            LastNGames: lastNGames
        };

        try {
            const response = await axios.get(`${NBAStats.BASE_URL}${endpoint}`, {
                headers: NBAStats.HEADERS,
                params: params,
                timeout: 30000
            });
            const data = response.data;

            const headers = data.resultSets[0].headers;
            const rows = data.resultSets[0].rowSet;
            const gameLogs = rows.map(row => {
                const log = {};
                headers.forEach((header, index) => {
                    log[header] = row[index];
                });
                return log;
            });

            return gameLogs.map(log => ({
                ...log,
                GAME_DATE: new Date(log.GAME_DATE).toISOString().split('T')[0] // Format date
            }));
        } catch (error) {
            console.error(`Error getting player game logs: ${error}`);
            return [];
        }
    }
}

const nbaStats = new NBAStats();

app.get('/player/stats', async (req, res) => {
    const playerName = req.query.name;
    if (!playerName) {
        return res.status(400).json({ error: 'Se requiere el nombre del jugador' });
    }

    // Find player ID using the new method
    const playerId = nbaStats.findPlayerId(playerName);
    if (!playerId) {
        return res.status(404).json({ error: 'Jugador no encontrado. Asegúrate de escribir el nombre completo correctamente.' });
    }

    // Get player info
    const playerInfo = await nbaStats.getPlayerInfo(playerId);
    if (!playerInfo) {
        return res.status(500).json({ error: 'No se pudo obtener información del jugador' });
    }

    const playerNameFromInfo = playerInfo.resultSets[0].rowSet[0][3];

    // Get last 10 games
    const gameLogs = await nbaStats.getPlayerGameLogs(playerId, "2023-24", 10);
    if (gameLogs.length === 0) {
        return res.status(404).json({ error: 'No se encontraron estadísticas recientes' });
    }

    const response = {
        player_name: playerNameFromInfo,
        last_10_games: gameLogs
    };

    return res.json(response);
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
// End of Selection
