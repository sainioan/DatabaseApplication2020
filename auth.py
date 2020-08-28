from flask import url_for, flash, g, render_template, redirect, request, session
import requests
import os
from app import app
from utils import books_currently_reading, books_read, future_books, users
import routes

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        session["username"] = request.form.get("username")
        username = request.form.get("username")
        password = request.form.get("password")
    try:
        if not username:
            return render_template("error.html", message="username missing")
        if not password:
            return render_template("error.html", message="password missing")
        if users.login(username, password):
            if "user_id" in session:
                flash(username + " logged in", "success")
                admin = users.is_admin(users.user_id())
                if admin:
                    return redirect(url_for("home_admin"))
                else:
                    return redirect("/home")
        else:
            flash("You are not logged in.", "danger")
            return render_template("error.html", message="Wrong username or password")
    except Exception as e:
        print(e)


@app.route("/logout")
def logout():
    if "user_id" in session:
        flash("You have been logged out", "info")
    users.logout()
    session.pop("user_id", None)
    return redirect("/")


@app.route("/sign_up", methods=["get", "post"])
def register():
    if request.method == "GET":
        return render_template("signup.html")
    if request.method == "POST":
        username = request.form.get("username")
        if not username or username == "":
            return render_template("error.html", message="username missing")
        user_check = users.user_check(username)
        # Check if username already exist, if the username is correct length, etc.
        if user_check:
            return render_template("error.html", message="username already exist")
        elif len(request.form.get("username")) < 3:
            return render_template("error.html", message="username too short")
        elif len(request.form.get("username")) > 16:
            return render_template("error.html", message="username too long")
        elif not request.form.get("password"):
            return render_template("error.html", message="must provide password")
        elif len(request.form.get("password")) < 3:
            return render_template("error.html", message="password too short")
        elif len(request.form.get("password")) > 16:
            return render_template("error.html", message="password too long")
        elif not request.form.get("confirmation"):
            return render_template("error.html", message="must confirm password")
        elif not request.form.get("password") == request.form.get("confirmation"):
            return render_template("error.html", message="passwords didn't match")
        username = request.form["username"]
        password = request.form["password"]
        if users.register(username, password):
            flash("user created", "msg")
            return redirect("/")
        else:
            return render_template("error.html", message="Error signing up")
