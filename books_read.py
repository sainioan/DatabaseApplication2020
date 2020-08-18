from db import db
from flask import session


def user_id():
    return session.get("user_id", 0)


def new_book(title, author, comment, rating, user_id, genre, pages):
    sql = "INSERT INTO books_read (title,author,comment, rating, user_id, genre, pages) VALUES (:title,:author, " \
          ":comment, :rating, " \
          ":user_id, :genre, :pages)"
    db.session.execute(sql, {"title": title, "author": author, "comment": comment, "rating": rating, "user_id": user_id,
                             "genre": genre, "pages": pages})
    db.session.commit()
    return True


def show(user_id):
    sql = "SELECT book_id, title, author, comment, rating, user_id FROM books_read WHERE " \
          "user_id=:user_id  " \
          "ORDER BY (rating IS NULL), rating DESC"
    result = db.session.execute(sql, {"user_id": user_id})
    db.session.commit()
    my_book_list = result.fetchall()
    return my_book_list


def share(book_id):
    sql = "INSERT INTO public_books_read (title, author, comment, rating, user_id) SELECT title, author, comment, rating, user_id FROM books_read WHERE " \
          "books_read.book_id=:book_id"
    db.session.execute(sql, {"book_id": book_id})
    db.session.commit()
    return True
