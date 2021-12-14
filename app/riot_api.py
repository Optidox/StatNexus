from app import app, db
from app.auth import check_token
from app.models import Bungie
from flask_login import current_user
import os
import urllib.parse
import requests
import json

def _api_header():
    return {"X-Riot-Token": os.environ.get('RIOT_API_KEY')}

def _get_summoner_id(name):
    response = requests.get('https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' 
            + urllib.parse.quote(name), headers=_api_header())
    return response.json()['id']

def _get_champ_name_from_id(id):
    with open('static/json/champion.json') as json_file:
        champs = json.load(json_file)
        for champ, info in champs['data']:
            if info['key'] == id:
                return info['name']

def get_league_stats(name):
    id = _get_summoner_id(name)
    response = requests.get('https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/' + id,
                             headers=_api_header())
    ranked_stats = response.json()
    response = requests.get('https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/' + id, headers=_api_header())
    champ_stats = response.json()
    print(json.dumps(champ_stats, indent=4))
    user_stats = {
        'Summoner Name' : ranked_stats[0]['summonerName'],
        'Most Played Champions' : '{0}, {1}, {2}'.format(_get_champ_name_from_id(champ_stats[0]['championId']),
                                                         _get_champ_name_from_id(champ_stats[1]['championId']),
                                                         _get_champ_name_from_id(champ_stats[2]['championId'])),
    }

    #Fix order by doing lookup with stat as substring
    for mode in ranked_stats:
        name = 'Solo/Duo ' if 'SOLO' in mode['queueType'] else 'Flex '
        user_stats[name + 'rank'] = '{0} {1} {2} LP'.format(mode['tier'], mode['rank'], mode['leaguePoints'])
        user_stats[name + 'wins/losses'] = '{0}W {1}L'.format(mode['wins'], mode[losses])
        user_stats[name + 'win %'] = '{}%'.format(round((mode['wins'] / mode['losses']) * 100, 1))

    return user_stats
