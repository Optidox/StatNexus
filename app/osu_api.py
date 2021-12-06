import os
from urllib.parse import uuid64
from uuid import uuid4
import base64
import six
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import time
from flask import session, g
from app import app, db


def _make_auth_headers():
    auth_header = base64.b64encode(six.text_type(os.environ.get('OSU_CLIENT_ID')
                                                 + ':' + os.environ.get('OSU_CLIENT_SECRET')).encode('ascii'))
    return {'Authorization': 'Basic %s' % auth_header.decode('ascii')}


def _refresh_token():
    headers = _make_auth_headers()
    payload = {'grant_type': 'refresh_token',
               'refresh_token': g.current_user.refresh_token}

    response = requests.post('https://osu.ppy.sh/oauth/token', data=payload, headers=headers)
    token_json = response.json()
    g.current_user.access_token = token_json['access_token']
    g.current_user.expiration_time = int(token_json['expires_in']) + int(time.time())
    db.session.commit()


def make_auth_url():
    state = str(uuid4())
    session['state_hash'] = generate_password_hash(state, 'sha256')
    params = {
        'client_id': os.environ.get('OSU_CLIENT_ID'),
        'scope': 'identify',
        'redirect_uri': os.environ.get('OSU_REDIRECT_URI'),
        'state': state,
        'response_type': 'code'
    }

    url = 'https://osu.ppy.sh/oauth/authorize?' + urlencode(params)
    return url


def check_state(state):
    state_hash = session['state_hash']
    session.pop('state_hash')
    return check_password_hash(state_hash, state)