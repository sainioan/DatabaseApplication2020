from db import db
from flask import session


def user_id():
    return session.get("user_id", 0)
def newBook(title, author, comment, rating, user_id):
    sql = "INSERT INTO mybooks (title,author,comment, rating, user_id) VALUES (:title,:author, :comment, :rating, :user_id)"
    db.session.execute(sql, {"title": title, "author": author, "comment": comment, "rating":rating, "user_id": user_id})
    db.session.commit()
    return True

def new(title, author, comment, rating, img, user_id):
    sql = "INSERT INTO mybooks (title,author,comment, rating, img, user_id) VALUES (:title,:author, :comment, :rating, :img, :user_id)"
    db.session.execute(sql, {"title": title, "author": author, "comment": comment, "rating":rating, "img": img, "user_id": user_id})
    db.session.commit()
    return True

def show(user_id):
    sql = "SELECT title,author, comment, rating  FROM mybooks WHERE user_id=:user_id"
    result = db.session.execute(sql, {"user_id": user_id})
    db.session.commit()
    mybooklist = result.fetchall()
    return mybooklist
