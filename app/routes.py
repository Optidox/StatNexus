from app import app
from flask import render_template


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/profile')
def profile():
    return "Hello, User!"

@app.route('/contact')
def contact():
    return "contact"

@app.route('/league')
def league():
    return "league"

@app.route('/destiny')
def destiny():
    return "leagues"

@app.route('/osu')
def osu():
    return "osu"
