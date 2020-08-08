from db import db
from flask import session


def user_id():
    return session.get("user_id", 0)


def new_book(title, author, comment, rating, user_id):
    sql = "INSERT INTO books_read (title,author,comment, rating, user_id) VALUES (:title,:author, :comment, :rating, " \
          ":user_id) "
    db.session.execute(sql, {"title": title, "author": author, "comment": comment, "rating":rating, "user_id": user_id})
    db.session.commit()
    return True


def show(user_id):
    sql = "SELECT title,author, comment, rating  FROM books_read WHERE user_id=:user_id ORDER BY rating DESC"
    result = db.session.execute(sql, {"user_id": user_id})
    db.session.commit()
    mybooklist = result.fetchall()
    return mybooklist
