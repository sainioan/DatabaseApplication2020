from flask import Flask, jsonify, redirect, config
from flask import render_template, request, session
import json
import requests
from flask_sqlalchemy import SQLAlchemy

import os
from dotenv import load_dotenv
from os import getenv
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

db = SQLAlchemy(app)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

import users

load_dotenv()

API_KEY = os.environ['API_KEY']

title = "Becoming"
author = "Michelle+Obama"
endPoint ="https://api.nytimes.com/svc/books/v3/lists/current/hardcover-fiction.json?api-key="+ API_KEY
endpoint2 = "https://api.nytimes.com/svc/books/v3/reviews.json?title=" +title + "&api-key=" +API_KEY

endpoint3 = "https://api.nytimes.com/svc/books/v3/reviews.json?author=" + author + "&api-key=" +API_KEY
response = requests.get(endPoint)
response2 = requests.get(endpoint2)
response3 = requests.get(endpoint3)

data = response.text
data2 = response2.text
data3 = response3.text

parsed = json.loads(data)
parsedResults = parsed["results"]
bookList = parsedResults.get('books')
titles = []
for i in range(len(bookList)):

    message = "Title: " + bookList[i]['title'] +", Author: " + bookList[i]['author'] + "  Description: " + bookList[i]['description'] + " "
    titles.append(message)

parsed2 = json.loads(data2)
parsed3 = json.loads(data3)
results = parsed2["results"]
results2 = parsed3["results"]
summary =results[0].get('summary')
summary2 =results2[0].get('summary')




class BaseConfig(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
db.init_app(app)
if config is None:
    app.config.from_object(config.BaseConfig)
else:
    app.config.from_object(config)
@app.route("/")
def index():
    return render_template("index.html")
# @app.route("/login")
# def login():
#     return render_template("login.html")
# @app.route("/signUp")
# def singUp():
#     return render_template("signup.html")
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        session['username'] = request.form['username']
        username = request.form["username"]
        password = request.form["password"]
    try:
        if users.login(username,password):
            return redirect("/")

        else:

            return render_template("error.html",message="Wrong username or password")
    except Exception as e:
        print(e)
@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")

@app.route("/signUp", methods=["get","post"])
def register():
    if request.method == "GET":
        return render_template("signup.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.register(username,password):
            return redirect("/")
        else:
            return render_template("error.html",message="Error signing up")
@app.route("/bestsellers")
def bestsellers():
    return render_template("books.html", message="Howdy!", items=titles)
@app.route("/books")
def apiBooks():
    return jsonify({'Book List': titles})
@app.route("/")
def apiReview():
    return(summary)
@app.route("/apiReview_author")
def apiReview2():
    return(summary2)

def apiBooks():
    return (parsed)
if __name__ == "__main__":
    app.run(debug=True)

