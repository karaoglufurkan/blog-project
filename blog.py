from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/")
def hello():
    return "hello world!"

@app.route("/index")
def index():
    article = dict()
    article["title"] = "Deneme"
    article["body"] = "Deneme123"
    article["author"] = "Furkan Karaoğlu"

    return render_template("index.html", article = article )

if __name__ == "__main__":
    app.run("0.0.0.0", debug = True)