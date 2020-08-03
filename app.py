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

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

import users
import booksToRead

load_dotenv()

API_KEY = os.environ['API_KEY']

title = "Becoming"
author = "Michelle+Obama"
endPoint = "https://api.nytimes.com/svc/books/v3/lists/current/hardcover-fiction.json?api-key=" + API_KEY
endpoint2 = "https://api.nytimes.com/svc/books/v3/reviews.json?title=" + title + "&api-key=" + API_KEY

endpoint3 = "https://api.nytimes.com/svc/books/v3/reviews.json?author=" + author + "&api-key=" + API_KEY
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
    message = bookList[i]['title'] + ", " + bookList[i]['author'] + ",  Description: " + bookList[i][
        'description'] + " "
    titles.append(message)

parsed2 = json.loads(data2)
parsed3 = json.loads(data3)
results = parsed2["results"]
results2 = parsed3["results"]
summary = results[0].get('summary')
summary2 = results2[0].get('summary')


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        session['username'] = request.form['username']
        username = request.form["username"]
        password = request.form["password"]
    try:
        if users.login(username, password):
            return redirect("/home")

        else:

            return render_template("error.html", message="Wrong username or password")
    except Exception as e:
        print(e)


@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")


@app.route("/signUp", methods=["get", "post"])
def register():
    if request.method == "GET":
        return render_template("signup.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.register(username, password):
            return redirect("/")
        else:
            return render_template("error.html", message="Error signing up")


@app.route("/bestsellers")
def bestsellers():
    return render_template("books.html", message="Howdy!", items=titles)


@app.route("/")
def apiReview():
    return (summary)


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/apiReview_author")
def apiReview2():
    return (summary2)

@app.route("/booksToReadList")
def showBooks():
    user_id = booksToRead.user_id()
    myList = booksToRead.show(user_id)
    bookList = []
    for i in range(len(myList)):
        message = str(myList[i])[1:-1]
        message2 = message.replace("'", "")
        message3 = message2.replace(",", " by ")
        print(message3)
        bookList.append(message3)
    return render_template("booksToReadList.html", items=bookList)

@app.route("/newBook", methods=["get", "post"])
def add():
    if request.method == "GET":
        return render_template("newBook.html", items=titles,)
    if request.method == "POST":
        title = str(request.form["title"])
        author = str(request.form["author"])
        user_id = int(booksToRead.user_id())
        print(user_id)
        booksToRead.new(title, author, user_id)
        db.session.commit()
        return redirect("/home")
    else:
        return render_template("error.html", message="Error adding a book")


# @app.route("/books")
# def apiBooks():
#     return jsonify({'Book List': titles})


#
# def apiBooks():
#     return (parsed)

if __name__ == "__main__":
    app.run(debug=True)
