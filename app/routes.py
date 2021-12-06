from app import app, db
from flask import render_template, flash, redirect, url_for, request, abort, session
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user
from app.models import User
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash
from app.osu_api import make_auth_url, check_state, get_tokens
import time


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/profile')
def profile():
    user_games = [
                    {
                        "name": "Destiny 2",
                        "logo_path": "../static/images/destiny_icon.png",
                        "stat1_title": "PVP KDA",
                        "stat2_title": "PVE KDA",
                        "stat1_info": "1.07",
                        "stat2_info": "3.09",
                    },
                    {
                        "name": "League of Legends",
                        "logo_path": "../static/images/league_of_legends_icon.png",
                        "stat1_title": "Stat 1",
                        "stat2_title": "Stat 2",
                        "stat1_info": "Stat info",
                        "stat2_info": "Stat info",
                    },
                    {
                        "name": "OSU",
                        "logo_path": "../static/images/osu_icon.png",
                        "stat1_title": "Stat 1",
                        "stat2_title": "Stat 2",
                        "stat1_info": "Stat info",
                        "stat2_info": "Stat info",
                    },
                ]
    username = "my_user"

    return render_template('profile.html', username = username, game_data = user_games)


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/league')
def league():
    return render_template('league.html')


@app.route('/destiny')
def destiny():
    game_data = {
                    "name": "Destiny 2",
                    "logo_path": "../static/images/destiny_icon.png",
                }
    stat_data = [
                    { 
                        "stat_title": "PVP KDA",
                        "stat_info": "1.07",
                    },
                    { 
                        "stat_title": "PVP KDA",
                        "stat_info": "3.75",
                    },
                    { 
                        "stat_title": "Vault of Glass Clears",
                        "stat_info": "14",
                    },
                    { 
                        "stat_title": "Last Wish Clears",
                        "stat_info": "15",
                    },
                    { 
                        "stat_title": "Garden of Salvation Clears",
                        "stat_info": "6",
                    },
                ]
                
    return render_template('game.html', game_data = game_data, stat_data = stat_data)


@app.route('/osu')
def osu():
    return render_template('osu.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    print(login)
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid Username or Password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        print(next_page)
        session.permanent = True
        return redirect(next_page)
    return render_template('temp_login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, alt_id=generate_password_hash(form.username.data, 'sha256'),
                    email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/osulogin', methods=['GET', 'POST'])
def osu_login():
    return redirect(make_auth_url())


@app.route('/osucallback')
def osu_callback():
    state = request.args.get('state', '')
    if not check_state(state):
        abort(403)
    token_info = get_tokens(request.args.get('code'))
    expiration_time = int(token_info['expires_in']) + int(time.time())
