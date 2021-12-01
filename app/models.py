from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    League = db.relationship('League', backref='id', lazy=True)
    Destiny = db.relationship('Destiny', backref='id', lazy=True)
    Osu = db.relationship('Osu', backref='id', lazy=True)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class League(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True,)
    access_token = db.Column(db.String(256))
    refresh_token = db.Column(db.String(256))
    expiration_time = db.Column(db.Integer)


class Destiny(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True,)
    access_token = db.Column(db.String(256))
    refresh_token = db.Column(db.String(256))
    expiration_time = db.Column(db.Integer)


class Osu(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True,)
    access_token = db.Column(db.String(256))
    refresh_token = db.Column(db.String(256))
    expiration_time = db.Column(db.Integer)
