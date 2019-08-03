from flask import Flask, flash, redirect, url_for, session, logging, request, render_template
# if flask-mysqldb cannot be installed on macOSX, try first;
#   $brew install mysql
# if doesn't still work
#   $export PATH=$PATH:/usr/local/mysql/bin
# then;
#   $pip install flask-mysqldb
from flask_mysqldb import MySQL 
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

#user registration form
class RegisterForm(Form):
    name = StringField("İsim Soyisim", validators = [validators.Length(min = 4, max = 25)])
    username = StringField("Kullanıcı Adı", validators = [validators.Length(min = 5, max = 35)])
    email = StringField("E-mail Adresi", validators = [validators.Email(message = "Lütfen geçerli bir e-mail adresi giriniz!")])
    password = PasswordField("Parola", validators = [
        validators.DataRequired("Lütfen bir parola belirleyin!"),
        validators.EqualTo(fieldname = "confirm", message = "Parolanız uyuşmuyor!")
    ])
    confirm = PasswordField("Parola Doğrula")


app = Flask(__name__)
app.secret_key = "fkblog"

#mysql configurations
app.config["MYSQL_HOST"] = "localhost"
#app.config["MYSQL_PORT"] = "80"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "fkblog"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

#
mysql = MySQL(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/articles/<string:id>")
def detail(id):
    return "Article ID: " + id

#Kayıt ol sayfası
@app.route("/register",methods = ["GET","POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(form.password.data)
        #password = form.password.data


        cursor = mysql.connection.cursor()
        query = "insert into users(name, email, username, password) values(%s,%s,%s,%s)"
        cursor.execute(query,(name, email, username, password))
        mysql.connection.commit()
        cursor.close()

        flash(message = "Kayıt başarıyla tamamlandı!", category = "success")

        return redirect(location = url_for("index"))
    else:
        return render_template("register.html", form = form)

#Login sayfası
@app.route("/login", methods = ["GET","POST"])
def login():
    return render_template("login.html")

if __name__ == "__main__":
    app.run("0.0.0.0", debug = True)