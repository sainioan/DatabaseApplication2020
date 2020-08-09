from flask import session

from db import db


def user_id():
    return session.get("user_id", 0)


def new(title, author, user_id):
    sql = "INSERT INTO bookstoread (title,author,user_id) VALUES (:title,:author,:user_id)"
    db.session.execute(sql, {"title": title, "author": author, "user_id": user_id})
    db.session.commit()
    return True

def show(user_id):
    sql = "SELECT * FROM bookstoread WHERE user_id=:user_id ORDER BY title ASC"
    result = db.session.execute(sql, {"user_id": user_id})
    db.session.commit()
    bookList = result.fetchall()
    return bookList

