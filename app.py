from flask import Flask, jsonify
from flask import render_template, request
import json
import requests
from flask_sqlalchemy import SQLAlchemy

import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# API_KEY = os.environ['API_KEY']
API_KEY = "7DG90jdg5dL3xUQqtNHfrfb2xwaEU4R9"
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
app.config["SQLALCHEMY_DATABASE_URI"] = "jdbc:postgresql://localhost:5432/postgres"
db = SQLAlchemy(app)
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/login")
def login():
    return render_template("login.html")
@app.route("/signUp")
def singUp():
    return render_template("signup.html")
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

