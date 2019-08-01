from flask import Flask, flash,redirect, url_for, session, logging, request, render_template
#if flask-mysqldb cannot be installed on macOSX, try first; 
# $brew install mysql 
# if doesn't still work
# $export PATH=$PATH:/usr/local/mysql/bin
#then;
# $pip install flask-mysqldb
from flask_mysqldb import MySQL 
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "fkblog"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)




@app.route("/")
def index():
    articles = [
        {"id":1, "title":"Deneme1", "content":"Deneme1 icerik"},
        {"id":2, "title":"Deneme2", "content":"Deneme2 icerik"},
        {"id":3, "title":"Deneme3", "content":"Deneme3 icerik"}
    ]

    return render_template("index.html", articles = articles)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/articles/<string:id>")
def detail(id):
    return "Article ID: " + id


if __name__ == "__main__":
    app.run("0.0.0.0", debug = True)