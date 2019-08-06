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

#article form
class ArticleForm(Form):
    title = StringField("Makale Başlığı", validators = [validators.length(min=5, max=100)])
    content = TextAreaField("Makale İçeriği", validators = [validators.length(min=10)])

#login form
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

mysql = MySQL(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

#Makale Sayfası
@app.route("/articles")
def articles():
    cursor = mysql.connection.cursor()
    query = "select * from articles"
    result = cursor.execute(query)

    if result > 0:
        articles = cursor.fetchall()

        return render_template("articles.html", articles = articles)
    else:
        return render_template("articles.html")

#register page
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

#Login page
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

#Article detail page
@app.route("/article/<string:id>")
def  article(id):
    cursor = mysql.connection.cursor()
    query = "select * from articles where id = %s"
    result = cursor.execute(query,(id),)

    if result > 0:
        article = cursor.fetchone()
        return render_template("article.html", article = article)
    else:
        return render_template("article.html")

#delete an article
@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor = mysql.connection.cursor()
    query = "select * from articles where (id = %s and author = %s)"
    result = cursor.execute(query,(id, session["username"]))

    if result > 0:
        query2 = "delete from articles where id = %s"
        cursor.execute(query2,(id,))
        mysql.connection.commit()
        flash(message="Makale başarıyla silindi", category="success")
        return redirect(url_for("dashboard"))
    else:
        flash(message="Böyle bir makale yok veya silmeye yetkiniz yok!",category="danger")
        return redirect(url_for("index"))

#update an article
@app.route("/edit/<string:id>", methods=["GET", "POST"])
@login_required
def update(id):
    if request.method == "GET":
        cursor = mysql.connection.cursor()
        query = "select * from articles where id=%s and author=%s"
        result = cursor.execute(query,(id,session["username"]))
        
        if result == 0:
            flash("Böyle bir makale yok ya da bu işleme yetkiniz yok!", "danger")
            return redirect(url_for("index"))
        else:
            article = cursor.fetchone()
            form = ArticleForm()
            form.title.data = article["title"]
            form.content.data = article["content"]

            return render_template("update.html", form = form)
    else:
        form = ArticleForm(request.form)
        title = form.title.data
        content = form.content.data
        
        cursor = mysql.connection.cursor()
        query = "update articles set title = %s, content = %s where id = %s"
        cursor.execute(query,(title, content, id))
        mysql.connection.commit()

        flash("Makale başarıyla güncellendi!","success")
        return redirect(url_for("dashboard"))


@app.route("/logout", methods = ["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    cursor = mysql.connection.cursor()
    query = "select * from articles where author = %s"
    result = cursor.execute(query,(session["username"],))

    if result > 0:
        articles = cursor.fetchall()
        return render_template("dashboard.html", articles=articles)
    else:
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
    
if __name__ == "__main__":
    app.run("0.0.0.0", debug = True)
    app.run()

