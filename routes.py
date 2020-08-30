from functools import wraps
from flask import url_for, flash, g, render_template, redirect, request, session
import json
import requests
import os
from dotenv import load_dotenv
from flask_login import LoginManager
from app import app

app.secret_key = os.getenv("SECRET_KEY")

from utils import books_currently_reading, books_read, future_books, users
import auth

login_manager = LoginManager()
login_manager.init_app(app)

from user_model import User
from db import db


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.before_request
def load_user():
    if "user_id" in session:
        user = User.query.filter_by(id=session["user_id"]).first()
        g.user = user
    else:
        user = {"name": "Guest"}
    g.user = user


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login", next=request.url))
        if g.user == {"name": "Guest"}:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function

import api
from community import community
import book_lists
load_dotenv()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/home")
@login_required
def home():
    admin = users.is_admin(users.user_id())
    return render_template("home.html", admin=admin)


@app.route("/home_admin")
@login_required
def home_admin():
    user_list = users.get_users()
    admin = users.is_admin(users.user_id())
    return render_template("home_admin.html", user_list=user_list, admin=admin)


@app.route("/delete_user/<id>", methods=["GET"])
@login_required
def delete_user(id):
    users.delete_user(id)
    return redirect(url_for("home_admin"))


@app.route("/add_link", methods=["get", "post"])
@login_required
def add_link():
    if request.method == "GET":
        admin = users.is_admin(users.user_id())
        return render_template("add_link.html", admin=admin)
    if request.method == "POST":
        title = str(request.form.get("title"))
        url = str(request.form.get("url"))
        if not title:
            return render_template("error.html", message="Title missing.")
        if not url:
            return render_template("error.html", message="Url missing.")
        sql = "INSERT into links(title, url) VALUES (:title,:url)"
        db.session.execute(sql, {"title": title, "url": url})
        db.session.commit()
        flash("Link added successfully!", "success")
        return redirect("/home")




