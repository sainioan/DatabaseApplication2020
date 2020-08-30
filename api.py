from flask import url_for, flash, g, render_template, redirect, request, session
import requests
import os

from routes import login_required

from app import app
from utils import books_currently_reading, books_read, future_books, users
import routes
import json
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.environ["API_KEY"]
end_point = "https://api.nytimes.com/svc/books/v3/lists/current/hardcover-fiction.json?api-key=" + API_KEY
response = requests.get(end_point)
data = response.text
parsed = json.loads(data)
parsed_results = parsed["results"]
book_list = parsed_results.get("books")


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


@app.route("/summary", methods=["get", "post"])
@login_required
def api_review():
    if request.method == "GET":
        return render_template("search_by_title.html")
    if request.method == "POST":
        title = str(request.form.get("title"))
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