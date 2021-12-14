from app import app, db
from app.auth import check_token
from app.models import Bungie
from flask_login import current_user
import os
import requests
import json

def _api_header():
    return {"X-Riot-Token": os.environ.get('RIOT_API_KEY')}

def _get_summoner_id(name):
    response = requests.get('https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + name,
                            headers=_api_header())
    return response.json()['id']

def get_league_stats(name):
    id = _get_summoner_id(name)
    response = requests.get('https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/' + id,
                             headers=_api_header())
    ranked_stats = response.json()
    print(json.dumps(ranked_stats, indent=4))
    response = requests.get('https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/' + id)
    champ_stats = response.json()
    print(json.dumps(champ_stats, indent=4))
