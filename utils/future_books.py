from db import db


def new(title, author, user_id):
    sql = "INSERT INTO bookstoread (title,author,user_id) VALUES (:title,:author,:user_id)"
    db.session.execute(sql, {"title": title, "author": author, "user_id": user_id})
    db.session.commit()


def check_book(user_id, title):
    sql = "SELECT title FROM bookstoread WHERE user_id = :user_id AND title = :title"
    return db.session.execute(sql,{"user_id": user_id, "title": title})


def show(user_id):
    sql = "SELECT book_id, title, author FROM bookstoread WHERE user_id=:user_id ORDER BY title"
    result = db.session.execute(sql, {"user_id": user_id})
    db.session.commit()
    bookList = result.fetchall()
    return bookList


def delete_book(book_id):
    sql = "DELETE FROM bookstoread WHERE book_id=:book_id"
    db.session.execute(sql, {"book_id": book_id})
    db.session.commit()


def transfer(book_id):
    sql = "INSERT INTO books_currently_reading (title, author, user_id) SELECT title, author, user_id FROM " \
          "bookstoread WHERE book_id =:book_id "
    db.session.execute(sql, {"book_id": book_id})
    db.session.commit()
