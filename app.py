from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash

app = Flask(__name__)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "todo-this-really-needs-to-be-changed"
psql = SQLAlchemy(app)

from user import User
from database import Database

db = Database()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"


@app.route("/")
def root():
    return render_template("root.html")


@app.route("/h", methods=["GET"])
@login_required
def home_get():
    return render_template("home.html", user=current_user)


@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():
    name = request.form["username"]
    password = request.form["password"]

    if not name or not password:
        return "Username and password can't be empty"

    user = db.get_user_by_name(name)
    if user is None:
        flash("User does not exist")
        return redirect("/login")

    if user.get_password() != generate_password_hash(password):
        flash("Wrong password")
        return redirect("/login")

    login_user(user)
    return redirect("/h")


@app.route("/register", methods=["GET"])
def register_get():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register_post():
    if not request.form["username"] or not request.form["password"]:
        return "Username and password can't be empty"

    name = request.form["username"]
    password = generate_password_hash(request.form["password"])
    user = User(name, password)

    db.add_user(user)
    login_user(user)
    return redirect("/h")


@login_required
@app.route("/logout", methods=["GET"])
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def user_loader(user_id):
    return db.get_user_by_name(user_id)


if __name__ == "__main__":
    app.run()
