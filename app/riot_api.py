from app import app, db
from app.auth import check_token
from app.models import League
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
    with open("app/static/json/champion.json") as json_file:
        champs = json.load(json_file)
        for champ, info in champs['data'].items():
            if info['key'] == str(id):
                return info['name']

def get_league_stats(name):
    id = _get_summoner_id(name)
    response = requests.get('https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/' + id,
                             headers=_api_header())
    ranked_stats = response.json()
    response = requests.get('https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/' + id, headers=_api_header())
    champ_stats = response.json()
    user_stats = {
        'Summoner Name' : name,
        'Most Played Champions' : '{0}, {1}, {2}'.format(_get_champ_name_from_id(champ_stats[0]['championId']),
                                                         _get_champ_name_from_id(champ_stats[1]['championId']),
                                                         _get_champ_name_from_id(champ_stats[2]['championId'])),
    }

    #Fix order by doing lookup with stat as substring
    for mode in ranked_stats:
        name = 'Solo/Duo ' if 'SOLO' in mode['queueType'] else 'Flex '
        user_stats[name + 'Rank'] = '{0} {1} {2} LP'.format(mode['tier'], mode['rank'], mode['leaguePoints'])
        user_stats[name + 'W/L'] = '{0}W {1}L'.format(mode['wins'], mode['losses'])
        user_stats[name + 'Win %'] = '{}%'.format(round((mode['wins'] / (mode['losses'] + mode['wins']) * 100), 1))

    return user_stats

def get_league_profile_card():
    stats = get_league_stats(League.query.get(current_user.id).username)
    if 'Solo/Duo Rank' in stats:
        return { 'stats':
                     { 'Solo/Duo Rank': stats['Solo/Duo Rank'],
                       'Solo/Duo W/L': stats['Solo/Duo W/L'],
                       'Solo/Duo Win %': stats['Solo/Duo Win %'] }}
    elif 'Flex Rank' in stats:
        return { 'stats':
                     { 'Flex Rank'  : stats['Flex Rank'],
                       'Flex W/L'   : stats['Flex W/L'],
                       'Flex Win %' : stats['Flex Win %'] }}
    else:
        return {'stats':
                     {'Summoner Name': League.query.get(current_user.id).username,
                      'Most Played Champions' : stats['Most Played Champions'],
                      'Play a ranked mode' : 'Get more stats LoL'}}
