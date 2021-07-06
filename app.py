import time

from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from itsdangerous import json
from werkzeug.security import generate_password_hash
from roles_required import roles_required

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
@roles_required(("user",))
def home_get():
    # add a string to the list which classifies whether the current user is the initiator of the offer or not
    transactions = db.get_transactions_of_current_user(current_user)
    for t in transactions:
        if current_user.get_id() == t[2]:
            t.append("current user is initiator")
        else:
            t.append("current user is not initiator")

    return render_template("home.html", user=current_user, transactions=transactions)


@app.route("/a", methods=["GET"])
@login_required
@roles_required(("admin",))
def admin_get():
    return "page has no template"


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

    if not user.verify_password(password):
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
        flash("Username and password should be filled")
        return redirect("/register")

    name = request.form["username"]
    password = generate_password_hash(request.form["password"])
    user = User(db.get_users_count(), name, password, "user", 0)

    if db.get_user_by_name(name) is not None:
        flash("User already exists")
        return redirect("/register")

    db.add_user(user)
    login_user(user)
    return redirect("/h")


@login_required
@app.route("/api/users", methods=["GET"])
def api_get_users():
    response = app.response_class(
        response=json.dumps(db.get_users(current_user), indent=4),
        status=200,
        mimetype="application/json"
    )
    return response


@login_required
@app.route("/api/transactions", methods=["GET"])
def api_get_transactions():
    response = app.response_class(
        response=json.dumps(db.get_transactions_of_current_user(current_user), indent=4),
        status=200,
        mimetype="application/json"
    )
    return response


# @login_required
# @app.route("/api/create_transaction", methods=["POST"])
# def api_create_transaction():
#     try:
#         answer = request.form["answer"]
#         print(answer)
#     except:
#         return "An answer to the transaction is expected"
#
#     parsed_answer = answer.split(";", 1)
#     db.complete_transaction(parsed_answer[0], parsed_answer[1])
#     return redirect("/h")


@login_required
@app.route("/api/complete_transaction", methods=["POST"])
def api_complete_transaction():
    try:
        answer = request.form["answer"]
    except:
        return redirect("/h")

    # parse the input data; first element is the answer (accept or reject), the second
    # is the transaction id
    parsed_answer = answer.split(";", 1)

    # check if the initiator is trying to accept his own transfer
    if current_user.get_id() == db.get_transaction(parsed_answer[1]).get_user1_id() and parsed_answer == "accept":
        return redirect("/h")

    # compete transaction
    db.complete_transaction(parsed_answer[0], parsed_answer[1])
    return redirect("/h")


# @login_required
# @app.route("/api/ping", methods=["GET"])
# def ping():
#     user = db.get_user_by_id(current_user.get_id())
#     answer = []
#     if user.has_to_reload_page():
#         answer.append("reload")
#     else:
#         answer.append("do not reload")
#
#     response = app.response_class(
#         response=json.dumps(answer, indent=4),
#         status=200,
#         mimetype="application/json"
#     )
#
#     return response


@login_required
@app.route("/unauthorized", methods=["GET"])
def unauthorized():
    return render_template("unauthorized.html")


@login_required
@app.route("/logout", methods=["GET"])
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def user_loader(user_id):
    return db.get_user_by_id(user_id)


if __name__ == "__main__":
    app.run()
