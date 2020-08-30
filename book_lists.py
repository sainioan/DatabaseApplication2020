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


# FUTURE BOOKS:
# function for rendering the logged in user's future book list
@app.route("/books_to_read_list")
@login_required
def show_books():
    user_id = users.user_id()
    my_list = future_books.show(user_id)
    admin = users.is_admin(users.user_id())
    return render_template("future_reading_list.html", items=my_list, admin=admin)


# function for adding a book to the user's future book list
@app.route("/new_book", methods=["get", "post"])
@login_required
def add_future_book():
    if request.method == "GET":
        admin = users.is_admin(users.user_id())
        return render_template("add_future_book.html", admin=admin)
    if request.method == "POST":
        title = str(request.form["title"])
        author = str(request.form["author"])
        user_id = users.user_id()
        if not title:
            return render_template("error.html", message="Title missing.")
        row = future_books.check_book(user_id, title)
        if row.rowcount == 1:
            return render_template("error.html", message="You've already entered this book")
        if not author:
            return render_template("error.html", message="Author missing.")
        user_id = users.user_id()
        future_books.new(title, author, user_id)
        return redirect("/books_to_read_list")
    else:
        return render_template("error.html", message="Error adding a book")


# function for moving a book from the user's future book list to currently reading list
@app.route("/future_book_list/transfer/<book_id>", methods=["GET"])
@login_required
def my_future_reading_list_transfer(book_id):
    future_books.transfer(book_id)
    future_books.delete_book(book_id)
    flash("Item successfully moved to Currently-Reading List and deleted from your Future Reading List.", "success")
    return redirect("/my_current_books")


# function for deleting a book from the user's future book list
@app.route("/future_book_list/delete/<book_id>", methods=["GET"])
@login_required
def my_future_reading_list_books_delete(book_id):
    future_books.delete_book(book_id)
    return redirect(url_for("show_books"))


# CURRENT BOOKS
# function for rendering the user's currently reading list
@app.route("/my_current_books")
@login_required
def show_my_current_books():
    user_id = users.user_id()
    my_current_book_list = books_currently_reading.show(user_id)
    admin = users.is_admin(users.user_id())
    return render_template("my_current_books.html", items=my_current_book_list, admin=admin)


# function for adding a book to user's currently reading list
@app.route("/add_current_book", methods=["get", "post"])
@login_required
def add_current_book():
    if request.method == "GET":
        admin = users.is_admin(users.user_id())
        return render_template("add_current_book.html", admin=admin)
    if request.method == "POST":
        title = str(request.form["title"])
        author = str(request.form["author"])
        user_id = users.user_id()
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
        user_id = users.user_id()
        books_currently_reading.new_book(title, author, genre, plot_summary, current_page, pages, user_id)
        return redirect("/my_current_books")
    else:
        return render_template("error.html", message="Error adding a book")


# function for editing the genre field of a book from the user's currently reading list.
@app.route("/my_current_books/update_genre/<book_id>", methods=["get", "post"])
@login_required
def my_books_current_books_update_genre(book_id):
    if request.method == "GET":
        admin = users.is_admin(users.user_id())
        return render_template("genre_update_current.html", id=book_id, admin=admin)
    if request.method == "POST":
        genre = request.form.get("genre")
        books_currently_reading.update_genre(genre, book_id)
        return redirect("/my_current_books")


# function for editing the summary field of a book from the user's currently reading list.
@app.route("/my_current_books/update_summary/<book_id>", methods=["get", "post"])
@login_required
def my_current_books_update_summary(book_id):
    if request.method == "GET":
        admin = users.is_admin(users.user_id())
        return render_template("summary_update.html", id=book_id, admin=admin)
    if request.method == "POST":
        summary = str(request.form.get("summary"))
        books_currently_reading.update_summary(summary, book_id)
        return redirect("/my_current_books")


# function for editing the current page field of a book from the user's currently reading list.
@app.route("/my_current_books/update/<book_id>", methods=["get", "post"])
@login_required
def my_current_books_update_current_page(book_id):
    if request.method == "GET":
        admin = users.is_admin(users.user_id())
        return render_template("current_page_update.html", id=book_id, admin=admin)
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


# function for editing the page count field of a book from the user's currently reading list.
@app.route("/my_current_books/update_page_count/<book_id>", methods=["get", "post"])
@login_required
def my_current_books_update_page_count(book_id):
    if request.method == "GET":
        admin = users.is_admin(users.user_id())
        return render_template("page_count_update.html", id=book_id, admin=admin)
    if request.method == "POST":
        try:
            pages = int(request.form.get("pages"))
            books_currently_reading.update_pages(pages, book_id)
            return redirect("/my_current_books")
        except ValueError:
            return render_template("error.html", message="Page count must be a number.")


# function for moving a book from the user's currently reading list to the books-read list.
@app.route("/my_current_books/completed/<book_id>", methods=["get"])
@login_required
def my_current_books_completed(book_id):
    books_currently_reading.transfer_to_books_read(book_id)
    books_currently_reading.delete_book(book_id)
    flash("Item successfully moved to Books-Read List and deleted from your Current Reading List.", "success")
    return redirect("/my_books_read")


# function for deleting a book from the user's currently reading list
@app.route("/my_current_books/delete/<book_id>", methods=["GET"])
@login_required
def my_current_books_delete(book_id):
    books_currently_reading.delete_book(book_id)
    return redirect(url_for("show_my_current_books"))


# READ BOOKS
# function for rendering the user's books read list
@app.route("/my_books_read")
@login_required
def show_my_books():
    user_id = users.user_id()
    my_book_list = books_read.show(user_id)
    admin = users.is_admin(users.user_id())
    return render_template("my_books_read.html", items=my_book_list, admin=admin)


# function for adding a book to the user's read books list
@app.route("/add_book", methods=["get", "post"])
@login_required
def add_read_book():
    if request.method == "GET":
        admin = users.is_admin(users.user_id())
        return render_template("add_read_book.html", admin=admin)
    if request.method == "POST":
        title = str(request.form["title"])
        author = str(request.form["author"])
        comment = str(request.form.get("comment"))
        rating = request.form.get("rating")
        genre = str(request.form.get("comment"))
        pages = request.form.get("pages")
        summary = request.form.get("summary")
        user_id = users.user_id()
        if not title:
            return render_template("error.html", message="'Title' missing.")
        row = books_read.check_book(user_id, title)
        if row.rowcount == 1:
            return render_template("error.html", message="You've already entered this book")
        if not author:
            return render_template("error.html", message="'Author' missing.")
        if not pages:
            return render_template("error.html", message="'Pages' missing.")
        user_id = users.user_id()
        books_read.new_book(title, author, comment, rating, user_id, genre, pages, summary)
        return redirect("/my_books_read")
    else:
        return render_template("error.html", message="Error adding a book")


# function for editing the comment field of a book from the user's books read list.
@app.route("/my_books_read/update_comment/<book_id>", methods=["get", "post"])
@login_required
def my_books_read_update_comment(book_id):
    if request.method == "GET":
        admin = users.is_admin(users.user_id())
        return render_template("comment_update.html", id=book_id, admin=admin)
    if request.method == "POST":
        comment = request.form.get("comment")
        books_read.update_comment(comment, book_id)
        return redirect("/my_books_read")


# function for editing the genre field of a book from the user's books read list.
@app.route("/my_books_read/update_genre/<book_id>", methods=["get", "post"])
@login_required
def my_books_read_update_genre(book_id):
    if request.method == "GET":
        admin = users.is_admin(users.user_id())
        return render_template("genre_update.html", id=book_id, admin=admin)
    if request.method == "POST":
        genre = request.form.get("genre")
        books_read.update_genre(genre, book_id)
        return redirect("/my_books_read")


# function for editing the rating field of a book from the user's books read list.
@app.route("/my_books_read/update_rating/<book_id>", methods=["get", "post"])
@login_required
def my_books_read_update_rating(book_id):
    if request.method == "GET":
        admin = users.is_admin(users.user_id())
        return render_template("rating_update.html", id=book_id, admin=admin)
    if request.method == "POST":
        rating = request.form.get("rating")
        books_read.update_rating(rating, book_id)
        return redirect("/my_books_read")


# function for editing the summary field of a book from the user's books read list.
@app.route("/my_books_read/update_summary/<book_id>", methods=["get", "post"])
@login_required
def my_books_read_update_summary(book_id):
    if request.method == "GET":
        admin = users.is_admin(users.user_id())
        return render_template("summary_update_books_read.html", id=book_id, admin=admin)
    if request.method == "POST":
        plot_summary = request.form.get("summary")
        books_read.update_summary(plot_summary, book_id)
        return redirect("/my_books_read")


# function for sharing a review (title, author, comment, and rating) with the app user community
@app.route("/my_books_read/share/<book_id>", methods=["get"])
@login_required
def my_books_read_share(book_id):
    books_read.share(book_id)
    flash("Book successfully shared with the community!", "success")
    return redirect("/my_books_read")