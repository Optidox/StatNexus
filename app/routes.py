from app import app, db
from flask import render_template, flash, redirect, url_for, request, abort, session
from app.forms import LoginForm, RegistrationForm, LeagueForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Osu, Bungie, League
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash
from app.auth import make_auth_url, check_state, get_tokens
from app.osu_api import get_osu_stats, get_osu_profile_card
from app.bungie_api import get_destiny_stats, get_destiny_profile_card
from app.riot_api import get_league_stats
from urllib3.exceptions import TimeoutError
import requests
import time


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    return render_template('index.html', logform=LoginForm(), regform=RegistrationForm())


@app.route('/profile')
@login_required
def profile():
    user_games = {
                    'Destiny 2': {
                        "logo_path": "../static/images/destiny_icon.png",
                        "path": "destiny",
                    },
                    'League of Legends': {
                        "logo_path": "../static/images/league_of_legends_icon.png",
                        "path": "league",
                    },
                    'osu!': {
                        "logo_path": "../static/images/osu_icon.png",
                        "path": "osu",
                    }
    }
    if Osu.query.get(current_user.id) is not None:
        user_games['osu!'] = user_games['osu!'] | get_osu_profile_card()
    if Bungie.query.get(current_user.id) is not None:
        user_games['Destiny 2'] = user_games['Destiny 2'] | get_destiny_profile_card()
    return render_template('profile.html', username=current_user.username, game_data=user_games)


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/league', methods=['GET', 'POST'])
@login_required
def league():
    form = LeagueForm()
    if form.validate_on_submit():
        new_league = League(id=current_user.id, username=form.username.data)
        db.session.add(new_league)
        db.session.commit()
        return redirect(url_for('league'))
    if League.query.get(current_user.id) is None:
        return render_template('league.html', form=form)

    game_data = {
        "name": "League of Legends",
        "logo_path": "../static/images/league_of_legends_icon.png",
    }

    return render_template('game.html',
                           game_data=game_data,
                           stat_data=get_league_stats(League.query.get(current_user.id).username))


@app.route('/destiny')
@login_required
def destiny():
    if Bungie.query.get(current_user.id) is None:
        return redirect(url_for('bungie_login'))
    
    game_data = {
                    "name": "Destiny 2",
                    "logo_path": "../static/images/destiny_icon.png",
                }
    return render_template('game.html', game_data=game_data, stat_data=get_destiny_stats())


@app.route('/osu')
@login_required
def osu():
    if Osu.query.get(current_user.id) is None:
        return redirect(url_for('osu_login'))

    game_data = {
        'name': 'osu!',
        'logo_path': '../static/images/osu_icon.png'
    }
    return render_template('game.html', game_data=game_data, stat_data=get_osu_stats())


@app.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    regform = RegistrationForm()
    logform = LoginForm()
    if logform.validate_on_submit():
        user = User.query.filter_by(username=logform.username.data).first()
        if user is None or not user.check_password(logform.password.data):
            flash('Invalid Username or Password')
            return redirect(url_for('index'))
        login_user(user, remember=logform.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('profile')
        print(next_page)
        session.permanent = True
        return redirect(next_page)
    return render_template('index.html', logform=logform, regform=regform)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    regform = RegistrationForm()
    logform = LoginForm()
    if regform.validate_on_submit():
        user = User(username=regform.username.data, alt_id=generate_password_hash(regform.username.data, 'sha256'),
                    email=regform.email.data)
        user.set_password(regform.password.data)
        db.session.add(user)
        db.session.commit()
        try:
            response = requests.get('https://statnexusmailer.herokuapp.com/?email=' + regform.email.data + '&subject=StatNexus%20Registration&text=Thank%20you%20for%20signing%20up%20for%20StatNexus%21')
        except Exception as e:
            pass
        return redirect(url_for('index'))
    return render_template('index.html', logform=logform, regform=regform)


@app.route('/osulogin', methods=['GET', 'POST'])
@login_required
def osu_login():
    return redirect(make_auth_url('osu'))


@app.route('/osucallback')
def osu_callback():
    if request.args.get('error') is not None:
        return redirect(url_for('profile'))
    state = request.args.get('state', '')
    if not check_state(state):
        abort(403)
    token_info = get_tokens(request.args.get('code'), 'osu')
    expiration_time = int(token_info['expires_in']) + int(time.time())
    access_token = token_info['access_token']
    refresh_token = token_info['refresh_token']
    if Osu.query.get(current_user.id) is None:
        new_osu = Osu(id=current_user.id,
                      access_token=access_token,
                      refresh_token=refresh_token,
                      expiration_time=expiration_time)
        db.session.add(new_osu)
    else:
        updated_osu = Osu.query.get(current_user.id)
        updated_osu.access_token = access_token
        updated_osu.refresh_token = refresh_token
        updated_osu.expiration_time = expiration_time
    db.session.commit()
    return redirect(url_for('profile'))


@app.route('/bungielogin', methods=['GET', 'POST'])
@login_required
def bungie_login():
    return redirect(make_auth_url('bungie'))


@app.route('/bungiecallback')
def bungie_callback():
    state = request.args.get('state', '')
    if not check_state(state):
        abort(403)
    token_info = get_tokens(request.args.get('code'), 'bungie')
    expiration_time = int(token_info['expires_in']) + int(time.time())
    access_token = token_info['access_token']
    refresh_token = token_info['refresh_token']
    if Bungie.query.get(current_user.id) is None:
        new_bungie = Bungie(id=current_user.id,
                      access_token=access_token,
                      refresh_token=refresh_token,
                      expiration_time=expiration_time)
        db.session.add(new_bungie)
    else:
        updated_bungie = Bungie.query.get(current_user.id)
        updated_bungie.access_token = access_token
        updated_bungie.refresh_token = refresh_token
        updated_bungie.expiration_time = expiration_time
    db.session.commit()
    return redirect(url_for('profile'))
