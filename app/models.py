from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alt_id = db.Column(db.Unicode(256), unique=True, nullable=False)
    email = db.Column(db.String(320), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    League = db.relationship('League', backref='league_id', lazy=True)
    Bungie = db.relationship('Bungie', backref='destiny_id', lazy=True)
    Osu = db.relationship('Osu', backref='osu_id', lazy=True)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.alt_id


@login.user_loader
def load_user(uid):
    return User.query.filter_by(alt_id=uid).first()


class League(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    username = db.Column(db.String(16))


class Bungie(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    access_token = db.Column(db.String(2048))
    refresh_token = db.Column(db.String(1024))
    expiration_time = db.Column(db.Integer)


class Osu(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    access_token = db.Column(db.String(2048))
    refresh_token = db.Column(db.String(1024))
    expiration_time = db.Column(db.Integer)
