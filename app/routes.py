from app import app
from flask import render_template


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

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