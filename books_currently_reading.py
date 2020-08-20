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


def transfer_to_books_read(book_id):
    sql = "INSERT INTO books_read (title, author, user_id, genre, pages) SELECT title, author, user_id, genre, " \
          "pages FROM books_currently_reading " \
          "WHERE book_id =:book_id "
    db.session.execute(sql, {"book_id": book_id})
    db.session.commit()
    return True


def update_page_number(current_page, book_id):
    sql = "UPDATE books_currently_reading SET current_page=:current_page WHERE book_id=:book_id"
    db.session.execute(sql, {"current_page": current_page, "book_id": book_id})
    db.session.commit()
    db.session.commit()
    return True


def update_summary(summary, book_id):
    sql = "UPDATE books_currently_reading SET plot_summary=:plot_summary WHERE book_id=:book_id"
    db.session.execute(sql, {"plot_summary": summary, "book_id": book_id})
    db.session.commit()
    return True


def delete_book(book_id):
    sql = "DELETE FROM books_currently_reading WHERE book_id=:book_id"
    db.session.execute(sql, {"book_id": book_id})
    db.session.commit()
    return True


def books_currently_read_by_users():
    sql2 = "SELECT DISTINCT TITLE from books_currently_reading"
    result2 = db.session.execute(sql2)
    title_list = result2.fetchall()
    return title_list