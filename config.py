import os

from dotenv import load_dotenv

load_dotenv('.env')

TELE_TOKEN = os.getenv("TELE_TOKEN")
RAPIDAPI_TOKEN = os.getenv("RAPIDAPI_TOKEN")

FOOTBALL_API_HEADERS = {
    'X-RapidAPI-Key': RAPIDAPI_TOKEN,
    'X-RapidAPI-Host': 'api-football-v1.p.rapidapi.com'
}

LEAGUE_DICT_PATH = 'memory/leagues.json'
TEAM_DICT_PATH = 'memory/teams.json'
