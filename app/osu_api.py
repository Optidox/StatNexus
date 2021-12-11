from app import app, db
from app.auth import check_token
from app.models import Osu
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

def format_osu_stats():
    stat_list = []
    user_json = _get_user()
    stat_json = user_json['statistics']
    stat_list.append({ 'stat_title': 'Username', 'stat_info': user_json['username']})
    stat_list.append({ 'stat_title': 'Level', 'stat_info': stat_json['level']['current']})
    stat_list.append({ 'stat_title': 'Ranked Score', 'stat_info': stat_json['ranked_score']})
    stat_list.append({ 'stat_title': 'pp', 'stat_info': stat_json['pp']})
    stat_list.append({ 'stat_title': 'Global Rank', 'stat_info': stat_json['global_rank']})
    stat_list.append({ 'stat_title': 'Country Rank', 'stat_info': stat_json['country_rank']})
    stat_list.append({ 'stat_title': 'Accuracy', 'stat_info': str(stat_json['hit_accuracy']) + '%'})
    stat_list.append({ 'stat_title': 'Max Combo', 'stat_info': stat_json['maximum_combo']})
    stat_list.append({ 'stat_title': 'Play Count', 'stat_info': stat_json['play_count']})
    stat_list.append({ 'stat_title': 'Play Time', 'stat_info': str(stat_json['play_time'] // 3600) + ' hrs ' + str((stat_json['play_time'] // 60) % 60) + ' mins'})
    stat_list.append({ 'stat_title': 'Total Score', 'stat_info': stat_json['total_score']})
    stat_list.append({ 'stat_title': 'Total Hits', 'stat_info': stat_json['total_hits']})
    return stat_list
