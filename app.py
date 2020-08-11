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
from sqlalchemy import text

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

import books_to_read
import books_read
import users
import books_currently_reading

login_manager = LoginManager()
login_manager.init_app(app)

from user_model import User
from book_model import Book
from current_book__model import Current_Book

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


@app.route("/sign_up", methods=["get", "post"])
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
def api_review():
    if request.method == "GET":
        return render_template("search_by_title.html", items=titles)
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
        return render_template("summary_by_title.html", title=title, items=list, links=links)

    else:
        return render_template("error_title.html", message=title + " not found")


@app.route("/summary2", methods=["get", "post"])
@login_required
def api_review2():
    if request.method == "GET":
        return render_template("search_by_author.html", items=titles)
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
            return render_template("summary_by_author.html", author=authorname, items=list, links=links)
        else:
            return render_template("error_title.html", message=authorname + " not found")


@app.route("/books_to_read_list")
@login_required
def show_books():
    user_id = books_to_read.user_id()
    my_list = books_to_read.show(user_id)
    return render_template("books_to_read_list.html", items=my_list)


@app.route("/my_books_read")
@login_required
def show_my_books():
    user_id = books_read.user_id()
    mybookList = books_read.show(user_id)
    return render_template("my_books.html", items=mybookList)


@app.route("/my_current_books")
@login_required
def show_my_current_books():
    user_id = books_currently_reading.user_id()
    my_current_book_list = books_currently_reading.show(user_id)
    print(my_current_book_list)
    return render_template("my_current_books.html", items=my_current_book_list)


@app.route('/my_current_books/delete/<book_id>', methods=["GET"])
@login_required
def my_current_books_delete(book_id):
    sql = "DELETE FROM books_currently_reading WHERE book_id=:book_id"
    db.session.execute(sql, {"book_id": book_id})
    db.session.commit()
    return redirect(url_for('show_my_current_books'))


@app.route('/books_to_read_list/delete/<book_id>', methods=["GET"])
@login_required
def my_reading_list_books_delete(book_id):
    sql = "DELETE FROM bookstoread WHERE book_id=:book_id"
    db.session.execute(sql, {"book_id": book_id})
    db.session.commit()
    return redirect(url_for('show_books'))


@app.route('/my_current_books/update/<book_id>', methods=["get", "post"])
@login_required
def my_current_books_update(book_id):

    if request.method == "GET":
        return render_template("current_page_update.html", id=book_id)
    if request.method == "POST":
        current_page = int(request.form.get("current_page"))
        sql = "UPDATE books_currently_reading SET current_page=:current_page WHERE book_id=:book_id"
        db.session.execute(sql, {"current_page": current_page, "book_id": book_id})
        db.session.commit()
        user_id = books_currently_reading.user_id()
        my_current_book_list = books_currently_reading.show(user_id)
        return render_template("my_current_books.html", items=my_current_book_list)


@app.route("/new_book", methods=["get", "post"])
@login_required
def add():
    if request.method == "GET":
        return render_template("new_book.html", items=titles)
    if request.method == "POST":
        title = str(request.form["title"])
        author = str(request.form["author"])
        if not title:
            return render_template("error.html", message="A required field (title or author) missing.")
            author = str(request.form["author"])
        if not author:
            return render_template("error.html", message="A required field (title or author) missing.")
        user_id = int(books_to_read.user_id())
        books_to_read.new(title, author, user_id)
        db.session.commit()
        return redirect("/books_to_read_list")
    else:
        return render_template("error.html", message="Error adding a book")


@app.route("/add_book", methods=["get", "post"])
@login_required
def add_book():
    if request.method == "GET":
        return render_template("add_book.html")
    if request.method == "POST":
        if request.method == "POST":
            title = str(request.form["title"])
            author = str(request.form["author"])
            if not title:
                return render_template("error.html", message="A required field (title or author) missing.")
                author = str(request.form["author"])
            if not author:
                return render_template("error.html", message="A required field (title or author) missing.")
        comment = str(request.form.get("comment"))
        rating = request.form["rating"]
        rating = str(rating)
        user_id = int(books_read.user_id())
        books_read.new_book(title, author, comment, rating, user_id)
        db.session.commit()
        return redirect("/my_books_read")
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
        if not title:
            return render_template("error.html", message="A required field (title or author) missing.")
            author = str(request.form["author"])
        if not author:
            return render_template("error.html", message="A required field (title or author) missing.")
        plot_summary = str(request.form.get("plot_summary"))
        genre = str(request.form.get("genre"))
        current_page = int(request.form.get("current_page"))
        pages = int(request.form.get("pages"))
        user_id = int(books_currently_reading.user_id())
        books_currently_reading.new_book(title, author, genre, plot_summary, current_page, pages, user_id)
        db.session.commit()
        return redirect("/my_current_books")
    else:
        return render_template("error.html", message="Error adding a book")


@app.route("/stats")
@login_required
def get_statistics():
    user_count = User.query.count()
    sql = "SELECT username, user_id, count(user_id) FROM books_read LEFT JOIN users ON users.id = books_read.user_id " \
          "GROUP BY books_read.user_id, users.username "
    result = db.session.execute(sql)
    count_list = result.fetchall()
    sql2 = "SELECT DISTINCT TITLE from books_currently_reading"
    result2 = db.session.execute(sql2)
    title_list = result2.fetchall()
    b_list = []
    for i in range(len(title_list)):
        message = str(title_list[i])[1:-1]
        message2 = message.replace("'", "")
        message3 = message2.replace(",", "")
        b_list.append(message3)
    return render_template("statistics.html", items=count_list, books=b_list, count=user_count)


if __name__ == "__main__":
    app.run(debug=True)
