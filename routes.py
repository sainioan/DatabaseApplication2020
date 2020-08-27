from functools import wraps
from flask import url_for, flash
from flask import g, render_template, redirect, request, session
import json
import requests
import os
from dotenv import load_dotenv
from flask_login import LoginManager
from app import app

app.secret_key = os.getenv("SECRET_KEY")

from utils import books_currently_reading, books_read, future_books, users

login_manager = LoginManager()
login_manager.init_app(app)

from user_model import User
from db import db


# new version of bookdatabase herokuapp:tsoha-books
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


load_dotenv()

API_KEY = os.environ["API_KEY"]
end_point = "https://api.nytimes.com/svc/books/v3/lists/current/hardcover-fiction.json?api-key=" + API_KEY
response = requests.get(end_point)
data = response.text
parsed = json.loads(data)
parsed_results = parsed["results"]
book_list = parsed_results.get("books")



@app.route("/")
def index():
    return render_template("index.html")


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


@app.route("/bestsellers")
@login_required
def bestsellers():
    if g.user is None:
        return redirect(url_for("index"))
    else:
        titles = []
        images = []
        for i in range(len(book_list)):
            message = book_list[i]["title"] + ", " + book_list[i]["author"] + ",  Description: " + book_list[i][
                "description"] + " "
            titles.append(message)
            images.append(book_list[i]["book_image"])
        return render_template("bestseller_list.html", message="Current Bestsellers:", items=titles, images=images)


@app.route("/home")
@login_required
def home():
    return render_template("home.html")


@app.route("/home_admin")
@login_required
def home_admin():
    user_list = users.get_users()
    admin = users.is_admin(users.user_id())
    return render_template("home_admin.html", user_list=user_list, admin=admin)


@app.route("/summary", methods=["get", "post"])
@login_required
def api_review():
    if request.method == "GET":
        return render_template("search_by_title.html")
    if request.method == "POST":
        title = str(request.form["title"])
    endpoint2 = "https://api.nytimes.com/svc/books/v3/reviews.json?title=" + title + "&api-key=" + API_KEY
    response2 = requests.get(endpoint2)
    data2 = response2.text
    parsed2 = json.loads(data2)
    results = parsed2["results"]
    if (results):
        length = len(results)
        list = []
        links = []
        for i in range(length):
            message = results[i]["book_title"] + ": " + results[i]["summary"]
            list.append(message)
        for i in range(length):
            message = results[i]["url"]
            links.append(message)
        return render_template("summary_by_title.html", title=title, items=list, links=links)

    else:
        return render_template("error_title.html", message=title + " not found")


@app.route("/summary2", methods=["get", "post"])
@login_required
def api_review2():
    if request.method == "GET":
        return render_template("search_by_author.html")
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
                message = results2[i]["book_title"] + ": " + results2[i]["summary"]
                list.append(message)
            for i in range(length):
                message = results2[i]["url"]
                links.append(message)
            return render_template("summary_by_author.html", author=authorname, items=list, links=links)
        else:
            return render_template("error_title.html", message=authorname + " not found")


@app.route("/books_to_read_list")
@login_required
def show_books():
    user_id = future_books.user_id()
    my_list = future_books.show(user_id)
    return render_template("future_reading_list.html", items=my_list)


@app.route("/my_current_books")
@login_required
def show_my_current_books():
    user_id = books_currently_reading.user_id()
    my_current_book_list = books_currently_reading.show(user_id)
    return render_template("my_current_books.html", items=my_current_book_list)


@app.route("/my_books_read")
@login_required
def show_my_books():
    user_id = books_read.user_id()
    my_book_list = books_read.show(user_id)
    return render_template("my_books_read.html", items=my_book_list)


@app.route("/my_current_books/delete/<book_id>", methods=["GET"])
@login_required
def my_current_books_delete(book_id):
    books_currently_reading.delete_book(book_id)
    return redirect(url_for("show_my_current_books"))


@app.route("/future_book_list/delete/<book_id>", methods=["GET"])
@login_required
def my_future_reading_list_books_delete(book_id):
    future_books.delete_book(book_id)
    return redirect(url_for("show_books"))


@app.route("/future_book_list/transfer/<book_id>", methods=["GET"])
@login_required
def my_future_reading_list_transfer(book_id):
    future_books.transfer(book_id)
    future_books.delete_book(book_id)
    flash("Item successfully moved to Currently-Reading List and deleted from your Future Reading List.", "success")
    return redirect("/my_current_books")


@app.route("/delete_user/<id>", methods=["GET"])
@login_required
def delete_user(id):
    users.delete_user(id)
    return redirect(url_for("home_admin"))


@app.route("/delete_link/<id>", methods=["GET"])
@login_required
def delete_link(id):
    sql = "DELETE FROM links WHERE link_id=:id"
    db.session.execute(sql, {"link_id": id})
    db.session.commit()
    return redirect(url_for("community"))


@app.route("/delete_review/<book_id>", methods=["GET"])
@login_required
def delete_review(book_id):
    sql = "DELETE FROM public_books_read WHERE book_id=:book_id"
    db.session.execute(sql, {"book_id": book_id})
    db.session.commit()
    return redirect(url_for("community"))


@app.route("/my_current_books/update/<book_id>", methods=["get", "post"])
@login_required
def my_current_books_update_current_page(book_id):
    if request.method == "GET":
        return render_template("current_page_update.html", id=book_id)
    if request.method == "POST":
        try:
            current_page = int(request.form.get("current_page"))
            pages = int(books_currently_reading.page_count(book_id)[0])
            if pages < current_page:
                return render_template("error.html",
                                       message="Page Count must be greater than or equal to current page.")
            books_currently_reading.update_page_number(current_page, book_id)
            return redirect("/my_current_books")
        except ValueError:
            return render_template("error.html", message="Current page must be a number.")


@app.route("/my_current_books/update_page_count/<book_id>", methods=["get", "post"])
@login_required
def my_current_books_update_page_count(book_id):
    if request.method == "GET":
        return render_template("page_count_update.html", id=book_id)
    if request.method == "POST":
        try:
            pages = int(request.form.get("pages"))
            books_currently_reading.update_pages(pages, book_id)
            return redirect("/my_current_books")
        except ValueError:
            return render_template("error.html", message="Page count must be a number.")


@app.route("/my_current_books/update_summary/<book_id>", methods=["get", "post"])
@login_required
def my_current_books_update_summary(book_id):
    if request.method == "GET":
        return render_template("summary_update.html", id=book_id)
    if request.method == "POST":
        summary = str(request.form.get("summary"))
        books_currently_reading.update_summary(summary, book_id)
        return redirect("/my_current_books")


@app.route("/my_books_read/update_comment/<book_id>", methods=["get", "post"])
@login_required
def my_books_read_update_comment(book_id):
    if request.method == "GET":
        return render_template("comment_update.html", id=book_id)
    if request.method == "POST":
        comment = request.form.get("comment")
        books_read.update_comment(comment, book_id)
        return redirect("/my_books_read")


@app.route("/my_books_read/update_genre/<book_id>", methods=["get", "post"])
@login_required
def my_books_read_update_genre(book_id):
    if request.method == "GET":
        return render_template("genre_update.html", id=book_id)
    if request.method == "POST":
        genre = request.form.get("genre")
        books_read.update_genre(genre, book_id)
        return redirect("/my_books_read")


@app.route("/my_current_books/update_genre/<book_id>", methods=["get", "post"])
@login_required
def my_books_current_books_update_genre(book_id):
    if request.method == "GET":
        return render_template("genre_update_current.html", id=book_id)
    if request.method == "POST":
        genre = request.form.get("genre")

        books_currently_reading.update_genre(genre, book_id)
        return redirect("/my_current_books")


@app.route("/my_books_read/update_rating/<book_id>", methods=["get", "post"])
@login_required
def my_books_read_update_rating(book_id):
    if request.method == "GET":
        return render_template("rating_update.html", id=book_id)
    if request.method == "POST":
        rating = request.form.get("rating")
        books_read.update_rating(rating, book_id)
        return redirect("/my_books_read")


@app.route("/my_books_read/update_summary/<book_id>", methods=["get", "post"])
@login_required
def my_books_read_update_summary(book_id):
    if request.method == "GET":
        return render_template("summary_update.html", id=book_id)
    if request.method == "POST":
        plot_summary = request.form.get("summary")
        sql = "UPDATE books_read SET plot_summary=:plot_summary WHERE book_id=:book_id"
        db.session.execute(sql, {"plot_summary": plot_summary, "book_id": book_id})
        db.session.commit()
        return redirect("/my_books_read")


@app.route("/my_current_books/completed/<book_id>", methods=["get"])
@login_required
def my_current_books_completed(book_id):
    books_currently_reading.transfer_to_books_read(book_id)
    books_currently_reading.delete_book(book_id)
    flash("Item successfully moved to Books-Read List and deleted from your Current Reading List.", "success")
    return redirect("/my_books_read")


@app.route("/my_books_read/share/<book_id>", methods=["get"])
@login_required
def my_books_read_share(book_id):
    books_read.share(book_id)
    flash("Book successfully shared with the community!", "success")
    return redirect("/my_books_read")


@app.route("/new_book", methods=["get", "post"])
@login_required
def add_future_book():
    if request.method == "GET":
        return render_template("add_future_book.html")
    if request.method == "POST":
        title = str(request.form["title"])
        author = str(request.form["author"])
        user_id = future_books.user_id()
        if not title:
            return render_template("error.html", message="Title missing.")
        row = future_books.check_book(user_id, title)
        if row.rowcount == 1:
            return render_template("error.html", message="You've already entered this book")
        if not author:
            return render_template("error.html", message="Author missing.")
        user_id = int(future_books.user_id())
        future_books.new(title, author, user_id)
        return redirect("/books_to_read_list")
    else:
        return render_template("error.html", message="Error adding a book")


@app.route("/add_book", methods=["get", "post"])
@login_required
def add_read_book():
    if request.method == "GET":
        return render_template("add_read_book.html")
    if request.method == "POST":
        title = str(request.form["title"])
        author = str(request.form["author"])
        comment = str(request.form.get("comment"))
        rating = request.form.get("rating")
        genre = str(request.form.get("comment"))
        pages = request.form.get("pages")
        summary = request.form.get("summary")
        user_id = books_read.user_id()
        if not title:
            return render_template("error.html", message="'Title' missing.")
        row = books_read.check_book(user_id, title)
        if row.rowcount == 1:
            return render_template("error.html", message="You've already entered this book")
        if not author:
            return render_template("error.html", message="'Author' missing.")
        if not pages:
            return render_template("error.html", message="'Pages' missing.")
        user_id = int(books_read.user_id())
        books_read.new_book(title, author, comment, rating, user_id, genre, pages, summary)
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
        user_id = books_currently_reading.user_id()
        if not title:
            return render_template("error.html", message="Title missing.")
        row = books_currently_reading.check_book(user_id, title)
        if row.rowcount == 1:
            return render_template("error.html", message="You've already entered this book")
        if not author:
            return render_template("error.html", message="Author missing.")
        plot_summary = str(request.form.get("plot_summary"))
        genre = str(request.form.get("genre"))
        try:
            current_page = request.form.get("current_page")
            if not current_page:
                return render_template("error.html", message="Current Page missing.")
        except ValueError:
            return render_template("error.html", message="Current Page must be a number.")
        try:
            pages = request.form.get("pages")
            if not pages:
                return render_template("error.html", message="Page Count missing.")
        except ValueError:
            return render_template("error.html", message="Page must be a number.")
        user_id = int(books_currently_reading.user_id())
        books_currently_reading.new_book(title, author, genre, plot_summary, current_page, pages, user_id)
        return redirect("/my_current_books")
    else:
        return render_template("error.html", message="Error adding a book")


@app.route("/add_link", methods=["get", "post"])
@login_required
def add_link():
    if request.method == "GET":
        return render_template("add_link.html")
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
        return redirect("/home")


@app.route("/links")
@login_required
def show_links():
    sql = "SELECT title, url from links"
    result = db.session.execute(sql)
    link_list = result.fetchall()
    return render_template("links.html", links=link_list)


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

    sql1 = "SELECT title, url from links"
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
