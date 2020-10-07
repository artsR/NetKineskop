from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from netkineskop import db, login



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __str__(self):
        return f''


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tag = db.Column(db.String(64))
    color = db.Column(db.String(6))

    def __str__(self):
        return f'{tag}'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
