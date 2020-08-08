from db import db
from sqlalchemy.sql import text


class Book(db.Model):
    __tablename__ = "mybooks"

    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(244), nullable=False)
    author = db.Column(db.String(144), nullable=False)
    comment = db.Column(db.String(244), nullable=True)
    rating = db.Column(db.String(144), nullable=True)
    user_id = db.Column(db.Integer, nullable=False)

    def __init__(self, title, author, comment, rating, user_id):
        self.title = title
        self.author = author
        self.comment = comment
        self.rating = rating
        self.user_id = user_id
