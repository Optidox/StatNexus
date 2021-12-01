from app import app
from flask import render_template, flash, redirect
from app.forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'iamauser'}
    return render_template('index.html', user=user)


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/league')
def league():
    return render_template('league.html')


@app.route('/destiny')
def destiny():
    return render_template('destiny.html')


@app.route('/osu')
def osu():
    return render_template('osu.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect('/index')
    return render_template('temp_login.html', form=form)