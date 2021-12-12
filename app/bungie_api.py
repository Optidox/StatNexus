from app import app, db
from app.auth import check_token
from app.models import Bungie
from flask_login import current_user
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
    return Bungie.query.get(current_user.id).access_token

def _get_membership_data():
    response = requests.get('https://www.bungie.net/Platform/User/GetMembershipsForCurrentUser/', headers=_get_headers())
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

def get_historical_stats():
    char_data = _get_character_ids()
    base_url = 'https://www.bungie.net/Platform/Destiny2/' + str(char_data[0][0]) + '/Account/' + str(char_data[0][1]) \
               + '/Character/'
    for character in char_data[1]:
        url = base_url + str(character) + '/Stats/'
        response = requests.get(url, headers=_get_headers())
        output = open("chars.json", "a")
        output.write(json.dumps(response.json(), indent=4))

    output.close()
