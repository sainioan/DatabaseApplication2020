from flask import Flask, jsonify, redirect, config, url_for
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
import mybooks

load_dotenv()

API_KEY = os.environ['API_KEY']
end_point = "https://api.nytimes.com/svc/books/v3/lists/current/hardcover-fiction.json?api-key=" + API_KEY
response = requests.get(end_point)
data = response.text
parsed = json.loads(data)
parsed_results = parsed["results"]
book_list = parsed_results.get('books')
titles = []


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

    for i in range(len(book_list)):
        message = book_list[i]['title'] + ", " + book_list[i]['author'] + ",  Description: " + book_list[i][
            'description'] + " "
        titles.append(message)
    return render_template("books.html", message="Current Bestsellers:", items=titles)


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/summary", methods=["get", "post"])
def apiReview():

    if request.method == "GET":
        return render_template("searchByTitle.html", items=titles)
    if request.method == "POST":
        title = str(request.form["title"])
    endpoint2 = "https://api.nytimes.com/svc/books/v3/reviews.json?title=" + title + "&api-key=" + API_KEY
    response2 = requests.get(endpoint2)
    data2 = response2.text
    parsed2 = json.loads(data2)
    results = parsed2["results"]
    if(results):
        length = len(results)
        print(results)
        list = []
        links = []
        for i in range(length):
            message = results[i]['book_title'] + ": " + results[i]['summary']
            list.append(message)
        for i in range(length):
            message = results[i]['url']
            links.append(message)
        print(links)
        return render_template("summaryByTitle.html", title=title, items=list, links=links)

    else:
        return render_template("error_title.html", message= title + " not found")


@app.route("/summary2", methods=["get", "post"])
def apiReview2():

    if request.method == "GET":
        return render_template("searchByAuthor.html", items=titles)
    if request.method == "POST":
        firstname = str(request.form["firstname"])
        lastname = str(request.form["lastname"])
        author = str(firstname+ "+"+ lastname)
        authorname = str(firstname + " " + lastname)
        endpoint3 = "https://api.nytimes.com/svc/books/v3/reviews.json?author=" + author + "&api-key=" + API_KEY
        response3 = requests.get(endpoint3)
        data3 = response3.text
        parsed3 = json.loads(data3)
        results2 = parsed3["results"]
        length = len(results2)
        print(results2)
        list = []
        links = []
        for i in range(length):
            message = results2[i]['book_title'] + ": " + results2[i]['summary']
            list.append(message)
        for i in range(length):
            message = results2[i]['url']
            links.append(message)
        print(links)
        return  render_template("summaryByAuthor.html", author = authorname, items=list, links=links)

@app.route("/booksToReadList")
def showBooks():
    user_id = booksToRead.user_id()
    myList = booksToRead.show(user_id)
    bookList = []
    for i in range(len(myList)):
        message = str(myList[i])[1:-1]
        message2 = message.replace("'", "")
        message3 = message2.replace(",", " by ")
        bookList.append(message3)
    return render_template("booksToReadList.html", items=bookList)

@app.route("/myBooks")
def showmybooks():
    user_id = mybooks.user_id()
    mybookList = mybooks.show(user_id)
    bookList = []
    for i in range(len(mybookList)):
       message = str(mybookList[i])[1:-1]
       print(message)
       message2 = message.split("', ")
       message2 = [item.replace("'", "") for item in message2]
       bookList.append(message2)
    return render_template("mybooks.html", items=bookList)


@app.route("/newBook", methods=["get", "post"])
def add():
    if request.method == "GET":
        return render_template("newBook.html", items=titles )
    if request.method == "POST":
        title = str(request.form["title"])
        author = str(request.form["author"])
        user_id = int(booksToRead.user_id())
        booksToRead.new(title, author, user_id)
        db.session.commit()
        return redirect("/home")
    else:
        return render_template("error.html", message="Error adding a book")


@app.route("/addBook", methods=["get", "post"])
def addBook():
    if request.method == "GET":
        return render_template("addBook.html")
    if request.method == "POST":

        title = str(request.form["title"])
        author = str(request.form["author"])
        comment = str(request.form.get("comment"))
        rating = str(request.form.get("rating"))
        user_id = int(mybooks.user_id())
        mybooks.newBook(title, author, comment, rating, user_id)
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
