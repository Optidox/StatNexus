import os
from urllib.parse import urlencode
from uuid import uuid4
import base64
import six
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import time
from flask import session, g, redirect, url_for
from flask_login import current_user
from app.models import Osu, Bungie
from app import app, db


def _make_auth_headers(api):
    if api == 'bungie':
        auth_header = base64.b64encode(six.text_type(os.environ.get('BUNGIE_CLIENT_ID')
                                                    + ':' + os.environ.get('BUNGIE_CLIENT_SECRET')).encode('ascii'))
    if api == 'osu':
        auth_header = base64.b64encode(six.text_type(os.environ.get('OSU_CLIENT_ID')
                                                     + ':' + os.environ.get('OSU_CLIENT_SECRET')).encode('ascii'))
    return {'Authorization': 'Basic %s' % auth_header.decode('ascii')}


def _refresh_token(api):
    if api == 'osu':
        data = Osu.query.get(current_user.id)
        payload = { 'grant_type': 'refresh_token',
                    'client_id': os.environ.get('OSU_CLIENT_ID'),
                    'client_secret': os.environ.get('OSU_CLIENT_SECRET'),
                    'refresh_token': data.refresh_token }
        response = requests.post('https://osu.ppy.sh/oauth/token', data=payload)
        token_json = response.json()

    elif api == 'bungie':
        data = Bungie.query.get(current_user.id)
        payload = { 'grant_type': 'refresh_token',
                    'refresh_token': data.refresh_token }
        response = requests.post('https://www.bungie.net/platform/app/oauth/token/', data=payload, headers=_make_auth_headers())
        token_json = response.json()
        
    if 'access_token' in token_json:
        data.access_token = token_json['access_token']
        data.expiration_time = int(token_json['expires_in']) + int(time.time())
    else:
        db.session.delete(data)
        db.session.commit()
        return redirect(url_for('destiny'))
            
    db.session.commit()


def make_auth_url(api):
    state = str(uuid4())
    session['state_hash'] = generate_password_hash(state, 'sha256')
    if api == 'osu':
        params = {
            'client_id': os.environ.get('OSU_CLIENT_ID'),
            'scope': 'identify',
            'redirect_uri': os.environ.get('OSU_REDIRECT_URI'),
            'state': state,
            'response_type': 'code'
        }

        url = 'https://osu.ppy.sh/oauth/authorize?' + urlencode(params)
    elif api == 'bungie':
        params = {
            'client_id': os.environ.get('BUNGIE_CLIENT_ID'),
            'state': state,
            'response_type': 'code'
        }

        url = 'https://www.bungie.net/en/OAuth/Authorize?' + urlencode(params)
    return url


# if multiple requests ever use this synchronously it will break
def check_state(state):
    state_hash = session['state_hash']
    session.pop('state_hash')
    return check_password_hash(state_hash, state)


def get_tokens(code, api):
    if api == 'osu':
        payload = {'grant_type': 'authorization_code',
                   'client_id': os.environ.get('OSU_CLIENT_ID'),
                   'client_secret': os.environ.get('OSU_CLIENT_SECRET'),
                   'code': code,
                   'redirect_uri': os.environ.get('OSU_REDIRECT_URI')}

        response = requests.post('https://osu.ppy.sh/oauth/token', data=payload)
    elif api == 'bungie':
        payload = {
            'grant_type': 'authorization_code',
            'code': code,
        }

        response = requests.post('https://www.bungie.net/platform/app/oauth/token/', data=payload, headers=_make_auth_headers())

    token_json = response.json()

    return {'access_token': token_json['access_token'],
            'refresh_token': token_json['refresh_token'],
            'expires_in': token_json['expires_in']}


def check_token(api):
    if api == 'osu':
        if Osu.query.get(current_user.id).expiration_time <= int(time.time()):
            _refresh_token('osu')
    elif api == 'bungie':
        if Bungie.query.get(current_user.id).expiration_time <= int(time.time()):
            _refresh_token('bungie')
