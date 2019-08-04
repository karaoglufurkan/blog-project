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
from functools import wraps

#login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash(message="Lütfen giriş yapın!", category="danger")
            return redirect(url_for("login"))
    return decorated_function

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

class LoginForm(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Parola")


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

        cursor = mysql.connection.cursor()
        query = "insert into users(name, email, username, password) values(%s,%s,%s,%s)"
        cursor.execute(query,(name, email, username, password))
        mysql.connection.commit()
        cursor.close()

        flash(message = "Kayıt başarıyla tamamlandı!", category = "success")

        return redirect(location = url_for("login"))
    else:
        return render_template("register.html", form = form)

#Login sayfası
@app.route("/login", methods = ["GET","POST"])
def login():
    form = LoginForm(request.form)

    if request.method == "POST":
        username = form.username.data
        password_entered = form.password.data

        cursor = mysql.connection.cursor()
        query = "select * from users where username = %s"
        result = cursor.execute(query,(username,))

        if result > 0:
            data = cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_entered, real_password):
                flash(message="Başarıyla giriş yapıldı!", category="success")
                
                #session started
                session["logged_in"] = True
                session["username"] = username
                
                return redirect(url_for("dashboard"))
            else:
                flash(message="Parolanızı yanlış girdiniz!", category="danger")
                return redirect(url_for("login"))
        else:
            flash(message="Böyle bir kullanıcı bulunamadı!", category="danger")
            return redirect(url_for("login"))
    return render_template("login.html", form = form)

@app.route("/logout", methods = ["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

#makale ekleme
@app.route("/addarticle", methods = ["GET", "POST"])
@login_required
def addarticle():
    form = ArticleForm(request.form)

    if request.method == "POST" and form.validate():
        title = form.title.data
        content = form.content.data

        cursor = mysql.connection.cursor()
        query = "insert into articles(title, author, content) values(%s, %s, %s)"
        cursor.execute(query,(title, session["username"], content))
        mysql.connection.commit()
        cursor.close()
        
        flash(message="Makale başarıyla eklendi!", category="success")
        return redirect(url_for("dashboard"))

    return render_template("addarticle.html", form = form)

#makale form
class ArticleForm(Form):
    title = StringField("Makale Başlığı", validators = [validators.length(min=5, max=100)])
    content = TextAreaField("Makale İçeriği", validators = [validators.length(min=10, max=500)])
    
if __name__ == "__main__":
    app.run("0.0.0.0", debug = True)
    app.run()