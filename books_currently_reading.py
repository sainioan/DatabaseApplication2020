from db import db
from flask import session


def user_id():
    return session.get("user_id", 0)


def new_book(title, author, genre, plot_summary, current_page, pages, user_id):
    sql = "INSERT INTO books_currently_reading (title,author, genre, plot_summary, current_page, pages, user_id) VALUES (:title,:author, :genre, :plot_summary, :current_page, :pages, " \
          ":user_id) "
    db.session.execute(sql, {"title": title, "author": author, "genre": genre, "plot_summary": plot_summary,
                             "current_page": current_page, "pages": pages, "user_id": user_id})
    db.session.commit()
    return True


def show(user_id):
    sql = "SELECT book_id, title, author, genre, plot_summary,current_page, pages, user_id, CAST(round(cast(" \
          "current_page::float / pages::float as numeric)*100, 2) AS INTEGER)AS percentage FROM books_currently_reading WHERE " \
          "user_id=:user_id ORDER BY title ASC "
    result = db.session.execute(sql, {"user_id": user_id})
    db.session.commit()
    my_current_book_list = result.fetchall()
    return my_current_book_list


def get_book_id(title):
    sql = "SELECT book_id FROM books_currently_reading WHERE " \
          "title=:title"
    result = db.session.execute(sql, {"title": title})
    db.session.commit()
    id = result.fetchone()
    return id


def transfer_to_books_read(user_id, book_id):
    sql = "INSERT INTO books_read (title, author, user_id) SELECT title, author, user_id FROM books_currently_reading WHERE " \
          "books_currently_reading.book_id=:book_id"
    db.session.execute(sql, {"user_id": user_id, "book_id": book_id})
    db.session.commit()
    return True


def update_pageNumber(user_id, current_page):
    sql = "UPDATE books_currently_reading SET current_page=? WHERE book_id = ?"
    result = db.session.execute(sql, {"user_id": user_id, "current_page": current_page})
    db.session.commit()
