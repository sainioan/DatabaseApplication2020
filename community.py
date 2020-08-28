from flask import url_for, flash, g, render_template, redirect, request, session
import requests
import os

from routes import login_required

from app import app
from utils import books_currently_reading, books_read, future_books, users
import routes
import json
from dotenv import load_dotenv
from user_model import User
from db import db

load_dotenv()


@app.route("/stats")
@login_required
def community():
    admin = users.is_admin(users.user_id())
    user_count = User.query.count()
    count_list = books_read.count_books_read_by_user()
    title_list = books_currently_reading.books_currently_read_by_users()
    b_list = []
    for i in range(len(title_list)):
        message = str(title_list[i])[1:-1]
        message2 = message.replace("'", "")
        message3 = message2.replace(",", "")
        b_list.append(message3)
    read_books = books_read.books_read_by_users()
    readb_list = []
    for i in range(len(read_books)):
        message = str(read_books[i])[1:-1]
        message2 = message.replace("'", "")
        message3 = message2.replace(",", "")
        readb_list.append(message3)

    sql1 = "SELECT link_id, title, url from links"
    result1 = db.session.execute(sql1)
    link_list = result1.fetchall()

    sql2 = "SELECT book_id, title, string_agg(comment, ', 'ORDER BY comment) AS comment_list, rating, username, " \
           "user_id FROM public_books_read LEFT JOIN users ON users.id = public_books_read.user_id GROUP BY 1, users.username, " \
           "public_books_read.user_id, public_books_read.rating, public_books_read.book_id ORDER BY (rating IS NULL), rating DESC"
    result2 = db.session.execute(sql2)
    db.session.commit()
    read_books_comments = result2.fetchall()
    return render_template("community.html", admin=admin, items=count_list, books=b_list, read_books=readb_list,
                           count=user_count,
                           links=link_list, comments=read_books_comments)


# admin function for deleting a link
@app.route("/delete_link/<link_id>", methods=["GET"])
@login_required
def delete_link(link_id):
    sql = "DELETE FROM links WHERE link_id=:link_id"
    db.session.execute(sql, {"link_id": link_id})
    db.session.commit()
    return redirect(url_for("community"))


# admin function for deleting a public review
@app.route("/delete_review/<book_id>", methods=["GET"])
@login_required
def delete_review(book_id):
    sql = "DELETE FROM public_books_read WHERE book_id=:book_id"
    db.session.execute(sql, {"book_id": book_id})
    db.session.commit()
    return redirect(url_for("community"))