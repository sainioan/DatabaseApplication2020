from functools import wraps
from flask import Flask, jsonify, redirect, config, url_for, flash
from flask import g, render_template, redirect, request, session
import json
import requests
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from os import getenv
from flask_login import LoginManager, current_user

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

import booksToRead
import books_read
import users
import books_currently_reading

login_manager = LoginManager()
login_manager.init_app(app)

from user_model import User
from book_model import Book

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)


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
            return redirect(url_for('login', next=request.url))
        if g.user == {"name": "Guest"}:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


load_dotenv()

API_KEY = os.environ['API_KEY']
end_point = "https://api.nytimes.com/svc/books/v3/lists/current/hardcover-fiction.json?api-key=" + API_KEY
response = requests.get(end_point)
data = response.text
parsed = json.loads(data)
parsed_results = parsed["results"]
book_list = parsed_results.get('books')
titles = []
images = []


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
            if "user_id" in session:
                flash(username + " logged in", "success")
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
    session.pop('user_id', None)
    return redirect("/")


@app.route("/signUp", methods=["get", "post"])
def register():
    if request.method == "GET":
        return render_template("signup.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.register(username, password):
            flash("user created", "msg")
            return redirect("/")
        else:
            return render_template("error.html", message="Error signing up")


@app.route("/bestsellers")
@login_required
def bestsellers():
    if g.user is None:
        return redirect(url_for('index'))
    else:
        for i in range(len(book_list)):
            message = book_list[i]['title'] + ", " + book_list[i]['author'] + ",  Description: " + book_list[i][
                'description'] + " "
            titles.append(message)
            images.append(book_list[i]['book_image'])
        return render_template("books.html", message="Current Bestsellers:", items=titles, images=images)


@app.route("/home")
@login_required
def home():
    return render_template("home.html")


@app.route("/summary", methods=["get", "post"])
@login_required
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
    if (results):
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
        return render_template("error_title.html", message=title + " not found")


@app.route("/summary2", methods=["get", "post"])
@login_required
def apiReview2():
    if request.method == "GET":
        return render_template("searchByAuthor.html", items=titles)
    if request.method == "POST":
        firstname = str(request.form["firstname"])
        lastname = str(request.form["lastname"])
        author = str(firstname + "+" + lastname)
        authorname = str(firstname + " " + lastname)
        endpoint3 = "https://api.nytimes.com/svc/books/v3/reviews.json?author=" + author + "&api-key=" + API_KEY
        response3 = requests.get(endpoint3)
        data3 = response3.text
        parsed3 = json.loads(data3)
        results2 = parsed3["results"]
        if results2:
            length = len(results2)
            list = []
            links = []
            for i in range(length):
                message = results2[i]['book_title'] + ": " + results2[i]['summary']
                list.append(message)
            for i in range(length):
                message = results2[i]['url']
                links.append(message)
            return render_template("summaryByAuthor.html", author=authorname, items=list, links=links)
        else:
            return render_template("error_title.html", message=authorname + " not found")


@app.route("/booksToReadList")
@login_required
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
@login_required
def showmybooks():
    user_id = books_read.user_id()
    mybookList = books_read.show(user_id)
    bookList = []
    for i in range(len(mybookList)):
        message = str(mybookList[i])[1:-1]
        print(message)
        message2 = message.split("', ")
        message2 = [item.replace("'", "") for item in message2]
        bookList.append(message2)
    return render_template("mybooks.html", items=bookList)


@app.route("/my_current_books")
@login_required
def show_my_current_books():
    user_id = books_currently_reading.user_id()
    my_current_book_list = books_currently_reading.show(user_id)
    bookList = []
    for i in range(len(my_current_book_list )):
        message = str(my_current_book_list [i])[1:-1]
        print(message)
        message2 = message.split("', ")
        message2 = [item.replace("'", "") for item in message2]
        bookList.append(message2)
    return render_template("my_current_books.html", items=bookList)


@app.route('/myBooks/delete/<int:id>')
@login_required
def delete(id):
    book_id = id
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('delete done.')
    return redirect(url_for('home'))


@app.route("/newBook", methods=["get", "post"])
@login_required
def add():
    if request.method == "GET":
        return render_template("newBook.html", items=titles)
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
@login_required
def addBook():
    if request.method == "GET":
        return render_template("addBook.html")
    if request.method == "POST":

        title = str(request.form["title"])
        author = str(request.form["author"])
        comment = str(request.form.get("comment"))
        rating = request.form["rating"]
        rating = str(rating)
        user_id = int(books_read.user_id())
        books_read.new_book(title, author, comment, rating, user_id)
        db.session.commit()
        return redirect("/home")
    else:
        return render_template("error.html", message="Error adding a book")


@app.route("/add_current_book", methods=["get", "post"])
@login_required
def add_current_book():
    if request.method == "GET":
        return render_template("add_current_book.html")
    if request.method == "POST":
        title = str(request.form["title"])
        author = str(request.form["author"])
        plot_summary = str(request.form.get("plot_summary"))
        genre = str(request.form.get("genre"))
        current_page = int(request.form.get("current_page"))
        pages = int(request.form.get("pages"))
        user_id = int(books_currently_reading.user_id())
        books_currently_reading.new_book(title, author, genre, plot_summary, current_page, pages, user_id)
        db.session.commit()
        return redirect("/home")
    else:
        return render_template("error.html", message="Error adding a book")


if __name__ == "__main__":
    app.run(debug=True)
