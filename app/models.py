from app import db


class User(db.Model):
    id = db.Column(db.Integerg, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return '<User {}>'.format(self.username)