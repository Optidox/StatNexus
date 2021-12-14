from app import app, db
from app.auth import check_token
from app.models import Osu
from app.helpers import add_commas
from flask_login import current_user
import os
import requests
import json

def _auth_header():
    return {"Authorization": "Bearer {0}".format(_get_access_token())}

def _get_access_token():
    check_token('osu')
    return Osu.query.get(current_user.id).access_token

def _get_user():
    response = requests.get('https://osu.ppy.sh/api/v2/me', headers=_auth_header())
    return response.json()

def get_osu_stats():
    user_json = _get_user()
    stat_json = user_json['statistics']
    return { 'Username'    : user_json['username'],
             'Level'       : str(stat_json['level']['current']) 
                             + '.' + str(stat_json['level']['progress']),
             'Ranked Score': add_commas(stat_json['ranked_score']),
             'pp'          : add_commas(stat_json['pp']),
             'Global Rank' : add_commas(stat_json['global_rank']),
             'Country Rank': add_commas(stat_json['country_rank']),
             'Accuracy'    : str(stat_json['hit_accuracy']) + '%',
             'Max Combo'   : add_commas(stat_json['maximum_combo']),
             'Play Count'  : add_commas(stat_json['play_count']),
             'Play Time'   : str(stat_json['play_time'] // 3600) + ' hrs '
                             + str((stat_json['play_time'] // 60) % 60) + ' mins',
             'Total Score' : add_commas(stat_json['total_score']),
             'Total Hits'  : add_commas(stat_json['total_hits'])}

def get_osu_profile_card():
    user_json = _get_user()
    stat_json = user_json['statistics']
    return { 'stats' :
                 {  'Global Rank': add_commas(stat_json['global_rank']),
                    'pp': add_commas(stat_json['pp']),
                    'Play Time': str(stat_json['play_time'] // 3600) + ' hrs ' 
                               + str((stat_json['play_time'] // 60) % 60) + ' mins' }}
