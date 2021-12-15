from app import app, db
from app.auth import check_token
from app.models import Bungie
from app.helpers import add_commas
from flask_login import current_user
from flask import redirect, url_for
import os
import requests
import json

def _auth_header():
    return {"Authorization": "Bearer {0}".format(_get_access_token())}

def _api_header():
    return {"X-API-Key": os.environ.get('BUNGIE_API_KEY')}

def _get_headers():
    return _auth_header() | _api_header()

def _get_access_token():
    check_token('bungie')
    user = Bungie.query.get(current_user.id)
    if user is not None:
        return user.access_token
    return redirect(url_for('destiny'))

def _get_membership_data():
    response = requests.get('https://www.bungie.net/Platform/User/GetMembershipsForCurrentUser/', 
                             headers=_get_headers())
    data = response.json()
    mem_type = data['Response']['destinyMemberships'][0]['membershipType']
    mem_id = data['Response']['destinyMemberships'][0]['membershipId']
    return mem_type, mem_id

def _get_character_ids():
    mem_data = _get_membership_data()
    url = 'https://www.bungie.net/Platform/Destiny2/' + str(mem_data[0]) + '/Profile/' + str(mem_data[1]) + \
          '/?components=100'
    response = requests.get(url, headers=_get_headers())
    return mem_data, response.json()['Response']['profile']['data']['characterIds']

def _get_historical_stats():
    char_data = _get_character_ids()
    chars_json = []
    base_url = 'https://www.bungie.net/Platform/Destiny2/' + str(char_data[0][0]) + '/Account/' + str(char_data[0][1]) \
               + '/Character/'
    for character in char_data[1]:
        url = base_url + str(character) + '/Stats/'
        response = requests.get(url, headers=_get_headers())
        chars_json.append(response.json()['Response'])

    return chars_json

def get_destiny_stats():
    chars = _get_historical_stats()
    stat_list = {'Time Played': 0,
                 'Strike Clears': 0,
                 'Raid Clears': 0,
                 'Crucible Matches': 0,
                 'PvE Kills': 0,
                 'PvP Kills': 0,
                 'PvE Assists': 0,
                 'PvP Assists': 0,
                 'PvE Deaths': 0,
                 'PvP Deaths': 0,
                 'PvE KDR': 0.0,
                 'PvP KDR': 0.0,
                 'PvE KDA': 0.0,
                 'PvP KDA': 0.0,
                 'PvE Efficiency': 0.0,
                 'PvP Efficiency': 0.0,
                 'PvE Time Played': 0,
                 'PvP Time Played': 0}

    for stats in chars:
        pvp     = stats['allPvP'].get('allTime')
        pve     = stats['allPvE'].get('allTime')
        raids   = stats['raid'].get('allTime')
        strikes = stats['allStrikes'].get('allTime')
        if pvp:
            stat_list['Crucible Matches'] += int(pvp['activitiesEntered']['basic']['value'])
            stat_list['PvP Assists']      += int(pvp['assists']['basic']['value'])
            stat_list['PvP Kills']        += int(pvp['kills']['basic']['value'])
            stat_list['PvP Deaths']       += int(pvp['deaths']['basic']['value'])
            stat_list['Time Played']      += int(pvp['secondsPlayed']['basic']['value'])
            stat_list['PvP Time Played']  += int(pvp['secondsPlayed']['basic']['value'])
        if pve:
            stat_list['PvE Assists']      += int(pve['assists']['basic']['value'])
            stat_list['PvE Kills']        += int(pve['kills']['basic']['value'])
            stat_list['PvE Deaths']       += int(pve['deaths']['basic']['value'])
            stat_list['Time Played']      += int(pve['secondsPlayed']['basic']['value'])
            stat_list['PvE Time Played']  += int(pve['secondsPlayed']['basic']['value'])
        if raids:
            stat_list['Raid Clears']      += int(raids['activitiesCleared']['basic']['value'])
        if strikes:
            stat_list['Strike Clears']    += int(strikes['activitiesCleared']['basic']['value'])

    # If somehow someone has 0 deaths, there will be a DB0 error here
    stat_list['PvP KDR']         = round(stat_list['PvP Kills'] / stat_list['PvP Deaths'], 3)
    stat_list['PvP KDA']         = round((stat_list['PvP Kills'] + (stat_list['PvP Assists'] / 2))
                                        / stat_list['PvP Deaths'], 3)
    stat_list['PvP Efficiency']  = round((stat_list['PvP Kills'] + stat_list['PvP Assists'])
                                        / stat_list['PvP Deaths'], 3)
    stat_list['PvE KDR']         = round(stat_list['PvE Kills'] / stat_list['PvE Deaths'], 3)
    stat_list['PvE KDA']         = round((stat_list['PvE Kills'] + (stat_list['PvE Assists'] / 2))
                                        / stat_list['PvE Deaths'], 3)
    stat_list['PvE Efficiency']  = round((stat_list['PvE Kills'] + stat_list['PvE Assists'])
                                        / stat_list['PvE Deaths'], 3)
    stat_list['PvP Time Played'] = str(stat_list['PvP Time Played'] // 3600) + ' hrs ' \
                                   + str((stat_list['PvP Time Played'] // 60) % 60) + ' mins'
    stat_list['PvE Time Played'] = str(stat_list['PvE Time Played'] // 3600) + ' hrs ' \
                                   + str((stat_list['PvE Time Played'] // 60) % 60) + ' mins'
    stat_list['Time Played']     = str(stat_list['Time Played'] // 3600) + ' hrs ' \
                                   + str((stat_list['Time Played'] // 60) % 60) + ' mins'
    
    for stat, value in stat_list.items():
        stat_list[stat] = add_commas(value) if 'Time' not in stat else value

    return stat_list

def get_destiny_profile_card():
    stats = get_destiny_stats()
    return { 'stats':
                 { 'PvP KDA': stats['PvP KDA'],
                   'PvE KDA': stats['PvE KDA'],
                   'Time Played': stats['Time Played'] }}
