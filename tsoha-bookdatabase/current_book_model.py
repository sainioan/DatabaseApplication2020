from db import db
from sqlalchemy.sql import text


class Current_Book(db.Model):
    __tablename__ = "books_currently_reading"

    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(244), nullable=False)
    author = db.Column(db.String(144), nullable=False)
    genre = db.Column(db.String(244), nullable=True)
    plot_summary = db.Column(db.String(144), nullable=True)
    current_page = db.Column(db.Integer, nullable=True)
    pages = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, nullable=False)

    def __init__(self, title, author, genre, plot_summary, current_page, pages, user_id):
        self.title = title
        self.author = author
        self.genre = genre
        self.plot_summary = plot_summary
        self.current_page = current_page
        self.pages = pages
        self.user_id = user_id
