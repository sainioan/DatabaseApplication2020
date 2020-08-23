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
    sql = "SELECT book_id, title, author FROM bookstoread WHERE user_id=:user_id ORDER BY title"
    result = db.session.execute(sql, {"user_id": user_id})
    db.session.commit()
    bookList = result.fetchall()
    return bookList


def get_book_id(title):
    sql = "SELECT book_id FROM bookstoread WHERE " \
          "title=:title"
    result = db.session.execute(sql, {"title": title})
    db.session.commit()
    id = result.fetchone()
    return id


def delete_book(book_id):
    sql = "DELETE FROM bookstoread WHERE book_id=:book_id"
    db.session.execute(sql, {"book_id": book_id})
    db.session.commit()
    return True


def transfer(book_id):
    sql = "INSERT INTO books_currently_reading (title, author, user_id) SELECT title, author, user_id FROM bookstoread WHERE book_id =:book_id"
    db.session.execute(sql, {"book_id": book_id})
    db.session.commit()
    return True