from db import db
from flask import session


def user_id():
    return session.get("user_id", 0)


def new_book(title, author, comment, rating, user_id, genre, pages, plot_summary):
    sql = "INSERT INTO books_read (title,author,comment, rating, user_id, genre, pages, plot_summary) VALUES (:title,:author, " \
          ":comment, :rating, " \
          ":user_id, :genre, :pages, :plot_summary)"
    db.session.execute(sql, {"title": title, "author": author, "comment": comment, "rating": rating, "user_id": user_id,
                             "genre": genre, "pages": pages, "plot_summary": plot_summary})
    db.session.commit()
    return True


def check_book(user_id, title):
    sql = "SELECT title FROM books_read WHERE user_id = :user_id AND title = :title"
    return db.session.execute(sql,{"user_id": user_id, "title": title})


def show(user_id):
    sql = "SELECT book_id, title, author, comment, rating, user_id, genre, pages, plot_summary FROM books_read WHERE " \
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


def update_comment(comment, book_id):
    sql = "UPDATE books_read SET comment=:comment WHERE book_id=:book_id"
    db.session.execute(sql, {"comment": comment, "book_id": book_id})
    db.session.commit()
    return True


def update_genre(genre, book_id):
    sql = "UPDATE books_read SET genre=:genre WHERE book_id=:book_id"
    db.session.execute(sql, {"genre": genre, "book_id": book_id})
    db.session.commit()
    return True


def count_books_read_by_user():
    sql = "SELECT username, user_id, count(user_id) FROM books_read LEFT JOIN users ON users.id = books_read.user_id " \
          "GROUP BY books_read.user_id, users.username "
    result = db.session.execute(sql)
    count_list = result.fetchall()
    return count_list


def books_read_by_users():
    sql3 = "SELECT DISTINCT TITLE from books_read"
    result3 = db.session.execute(sql3)
    read_books = result3.fetchall()
    return read_books

