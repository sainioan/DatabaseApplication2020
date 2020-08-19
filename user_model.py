from db import db
from sqlalchemy.sql import text


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(144), nullable=False)
    password = db.Column(db.String(144), nullable=False)
    admin = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role

    def get_id(self):
        return self.id

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True


