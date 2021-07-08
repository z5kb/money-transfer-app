import time

from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from itsdangerous import json
from werkzeug.security import generate_password_hash
from roles_required import roles_required
from flask_qrcode import QRcode

app = Flask(__name__)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "todo-this-really-needs-to-be-changed"
psql = SQLAlchemy(app)
QRcode(app)

from user import User
from transaction import Transaction
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


@app.route("/h/settings", methods=["GET"])
@login_required
@roles_required(("user",))
def settings_get():
    return render_template("settings.html", user=current_user)


@app.route("/h/settings", methods=["POST"])
@login_required
@roles_required(("user",))
def settings_post():
    user = None
    new_email = None
    new_pass = None

    try:
        action = request.form["action"]

        if action == "update profile":
            # get data from form
            new_email = request.form["new_email"]
            new_pass = request.form["new_pass"]

            # update user
            user = current_user
            user.set_email(new_email)
            user.set_password(generate_password_hash(new_pass))

            # commit changes to db
            db.update_user(user)
    except:
        flash("error processing your request")
        return redirect("/h")
    return redirect("/h/settings")


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

    user = db.get_user_by_email(name)
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

    if db.get_user_by_email(name) is not None:
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


@login_required
@app.route("/api/create_transaction", methods=["POST"])
def api_create_transaction():
    try:
        user1_change = request.form["change_in_balance"]
        user2_id = request.form["user2_id"]
    except:
        return "An answer to the transaction is expected"

    user2_change = str(-float(user1_change))
    t = Transaction(db.get_transactions_count(), "open", current_user.get_id(), user2_id, user1_change, user2_change)

    if db.get_user_by_id(current_user.get_id()).get_balance() + float(user1_change) < 0:
        flash("You don't have enough money to create this transaction.")
        return redirect("/h")

    db.create_transaction(t)
    return redirect("/h")


# TODO add asserts
@login_required
@app.route("/api/complete_transaction", methods=["POST"])
def api_complete_transaction(answer=None):
    try:
        if answer is None:
            answer = request.form["answer"]
    except:
        return redirect("/h")

    # parse the input data; first element is the answer (accept or reject), the second
    # is the transaction id
    parsed_answer = answer.split(";", 1)

    # check if the initiator is trying to accept his own transfer
    if current_user.get_id() == db.get_transaction(parsed_answer[1]).get_user1_id() and parsed_answer == "accept":
        flash("You can't accept your own transfer.")
        return redirect("/h")

    # compete transaction
    if db.complete_transaction(parsed_answer[0], parsed_answer[1]):
        if parsed_answer[0] == "accept":
            flash("Transaction completed.")
        elif parsed_answer[0] == "reject":
            flash("Transaction rejected.")
    else:
        flash("Transaction failed. Do you have enough money?")
    return redirect("/h")


# TODO remove/move asserts
@login_required
@app.route("/api/qr/<string:key>", methods=["GET"])
def api_qr_complete_transaction(key):
    # parse the input data; first element is the answer (accept or reject), the second
    # is the transaction id
    parsed_answer = key.split(";", 1)
    try:
        assert parsed_answer[0] == "accept" or parsed_answer[0] == "reject"
        assert isinstance(db.get_transaction(parsed_answer[1]), Transaction)
        api_complete_transaction(key)
    except:
        return "error"
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
