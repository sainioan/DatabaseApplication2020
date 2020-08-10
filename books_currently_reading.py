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
    sql = "SELECT * FROM books_currently_reading WHERE " \
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


#
# def show_percentage(user_id):
#     sql = "SELECT current_page,pages, count(current_page)* 100/ pages as percentage  FROM books_currently_reading " \
#           "WHERE user_id=:user_id"
#     result = db.session.execute(sql, {"user_id": user_id})
#     db.session.commit()
#     my_current_book_list = result.fetchall()
#     return my_current_book_list


def update_pageNumber(user_id, current_page):
    sql = "UPDATE books_currently_reading SET current_page=? WHERE book_id = ?"
    result = db.session.execute(sql, {"user_id": user_id, "current_page": current_page})
    db.session.commit()
