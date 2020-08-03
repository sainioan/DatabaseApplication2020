from db import db
from flask import session


def user_id():
    return session.get("user_id", 0)


def new(title, author, user_id):
    sql = "INSERT INTO bookstoread (title,author,user_id) VALUES (:title,:author,:user_id)"
    db.session.execute(sql, {"title": title, "author": author, "user_id": user_id})
    db.session.commit()
    return True


