from flask import Flask, render_template, request, redirect, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from itsdangerous import json
from werkzeug.security import generate_password_hash
from roles_required import roles_required
import paypalrestsdk

app = Flask(__name__)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "todo-this-really-needs-to-be-changed"
psql = SQLAlchemy(app)

from user import User
from transaction import Transaction
from paypal_transaction import PaypalTransaction
from database import Database

db = Database()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"

paypalrestsdk.configure({
    "mode": "sandbox",  # sandbox or live
    "client_id": "AZEzumjaGOMv3kcWIMPP3Aqg4EjSfTLXL8A60tqpQpTy0u2LCG427HZmqPvXKQYa6_hxd6VL6CPDsHTB",
    "client_secret": "EI3471ARxvtpdAm8OEPr5_l2lGXb9Csir-DlhJYKMVw5Vk7N-tu0XweE3pEGLHO3uRvCCbRPl-Ql3_16"})


@app.route("/")
def root():
    return render_template("root.html")


@app.route("/h", methods=["GET"])
@login_required
@roles_required(("user",))
def home_get():
    # # add a string to the list which classifies whether the current user is the initiator of the offer or not
    # transactions = db.get_transactions_of_current_user(current_user)
    #
    # # check which user is initiator
    # for t in transactions:
    #     if current_user.get_id() == t[2]:
    #         t.append("current user is initiator")
    #     else:
    #         t.append("current user is not initiator")
    #
    # # replace user's ids with emails
    # for t in transactions:
    #     t[2] = db.get_user_email_by_id(t[2])
    #     t[3] = db.get_user_email_by_id(t[3])
    return render_template("home.html", user=current_user)


@app.route("/h/settings", methods=["GET"])
@login_required
@roles_required(("user",))
def settings_get():
    return render_template("settings.html", user=current_user)


@app.route("/h/settings", methods=["POST"])
@login_required
@roles_required(("user",))
def settings_post():
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
    return render_template("admin.html", user=current_user)


@app.route("/a/u", methods=["GET"])
@login_required
@roles_required(("admin",))
def admin_users_get():
    return render_template("admin_users.html")


@app.route("/a/t", methods=["GET"])
@login_required
@roles_required(("admin",))
def admin_transactions_get():
    return render_template("admin_transactions.html")


@app.route("/a/p", methods=["GET"])
@login_required
@roles_required(("admin",))
def admin_paypal_transactions_get():
    return render_template("admin_paypal_transactions.html")


@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]

    if not email or not password:
        return "Email and password can't be empty"

    user = db.get_user_by_email(email)
    if user is None:
        flash("User does not exist")
        return redirect("/login")

    if not user.verify_password(password):
        flash("Wrong password")
        return redirect("/login")

    login_user(user)
    if user.get_role() == "user":
        return redirect("/h")
    return redirect("/a")


@app.route("/register", methods=["GET"])
def register_get():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register_post():
    if not request.form["email"] or not request.form["password"]:
        flash("Username and password should be filled")
        return redirect("/register")

    email = request.form["email"]
    password = generate_password_hash(request.form["password"])
    user = User(db.get_users_count(), email, password, "user", 0)

    if db.get_user_by_email(email) is not None:
        flash("User already exists")
        return redirect("/register")

    login_user(user)
    db.add_user(user)
    return redirect("/h")


@app.route("/api/users", methods=["GET"])
@login_required
def api_get_users():
    response = app.response_class(
        response=json.dumps(db.get_users_of_current_user(current_user), indent=4),
        status=200,
        mimetype="application/json"
    )
    return response


@app.route("/api/paypal_transactions", methods=["GET"])
@login_required
def api_get_paypal_transactions():
    response = app.response_class(
        response=json.dumps(db.get_paypal_transactions_as_list_of_current_user(current_user), indent=4),
        status=200,
        mimetype="application/json"
    )
    return response


@app.route("/api/a/users", methods=["GET"])
@login_required
@roles_required(("admin",))
def api_admin_get_users():
    response = app.response_class(
        response=json.dumps(db.get_users(), indent=4),
        status=200,
        mimetype="application/json"
    )
    return response


@app.route("/api/a/transactions", methods=["GET"])
@login_required
@roles_required(("admin",))
def api_admin_get_transactions():
    response = app.response_class(
        response=json.dumps(db.get_transactions(), indent=4),
        status=200,
        mimetype="application/json"
    )
    return response


@app.route("/api/a/paypal_transactions", methods=["GET"])
@login_required
@roles_required(("admin",))
def api_admin_get_paypal_transactions():
    response = app.response_class(
        response=json.dumps(db.get_paypal_transactions(), indent=4),
        status=200,
        mimetype="application/json"
    )
    return response


@app.route("/api/a/delete_user", methods=["POST"])
@login_required
@roles_required(("admin",))
def api_admin_delete_user():
    try:
        user_id = request.form["user_id"]

        if db.get_user_by_id(user_id) is None:
            return "user does not exist"

        db.delete_user_by_id(user_id)
    except:
        return "error in post request"
    return redirect("/a/u")


@app.route("/api/a/update_user", methods=["POST"])
@login_required
@roles_required(("admin",))
def api_admin_update_user():
    try:
        user_id = request.form["user_id"]
        new_email = request.form["new_email"]
        new_pass = request.form["new_pass"]
        new_balance = request.form["new_balance"]
        new_role = request.form["new_role"]

        # make sure input is provided
        assert user_id is not None
        assert new_email is not None
        assert new_balance is not None
        assert new_role is not None

        # update user
        new_user = db.get_user_by_id(user_id)
        new_user.set_email(new_email)
        new_user.set_balance(new_balance)
        new_user.set_role(new_role)

        if new_pass:
            new_user.set_password(generate_password_hash(new_pass))

        # commit changes to db
        db.update_user(new_user)
    except:
        return "error in post request"
    return redirect("/a/u")


@app.route("/api/a/freeze_user", methods=["POST"])
@login_required
@roles_required(("admin",))
def api_admin_freeze_user():
    try:
        user_id = request.form["user_id"]
        assert user_id is not None

        user = db.get_user_by_id(user_id)
        assert user is not None

        # update user's role
        user.set_role("frozen")

        # commit changes to db
        db.update_user(user)
        db.freeze_user_open_transactions(user)
    except:
        return "error in post request"
    return redirect("/a/u")


@app.route("/api/a/unfreeze_user", methods=["POST"])
@login_required
@roles_required(("admin",))
def api_admin_unfreeze_user():
    try:
        user_id = request.form["user_id"]
        assert user_id is not None

        user = db.get_user_by_id(user_id)
        assert user is not None

        # update user's role
        user.set_role("user")

        # commit changes to db
        db.update_user(user)
        db.unfreeze_user_transactions(user)
    except:
        return "error in post request"
    return redirect("/a/u")


@app.route("/api/transactions", methods=["GET"])
@login_required
def api_get_transactions():
    response = app.response_class(
        response=json.dumps(db.get_transactions_of_current_user(current_user), indent=4),
        status=200,
        mimetype="application/json"
    )
    return response


@app.route("/api/a/freeze_transaction", methods=["POST"])
@login_required
@roles_required(("admin",))
def api_admin_freeze_transaction():
    try:
        transaction_id = request.form["transaction_id"]
        assert transaction_id is not None

        transaction = db.get_transaction_by_id(transaction_id)
        assert transaction is not None

        # update transaction's status
        if transaction.get_status() != "open":
            return "The transaction is not open and you can not freeze it."
        transaction.set_status("frozen")

        # commit changes to db
        db.freeze_transaction(transaction)
    except:
        return "error in post request"
    return redirect("/a/t")


@app.route("/api/a/unfreeze_transaction", methods=["POST"])
@login_required
@roles_required(("admin",))
def api_admin_unfreeze_transaction():
    try:
        transaction_id = request.form["transaction_id"]
        assert transaction_id is not None

        transaction = db.get_transaction_by_id(transaction_id)
        assert transaction is not None

        # update transaction's status
        if transaction.get_status() != "frozen":
            return "The transaction is not open and you can not unfreeze it."
        transaction.set_status("open")

        # commit changes to db
        db.freeze_transaction(transaction)
    except:
        return "error in post request"
    return redirect("/a/t")


@app.route("/api/create_transaction", methods=["POST"])
@login_required
def api_create_transaction():
    try:
        user1_change = request.form["change_in_balance"]
        try:
            user2_id = request.form["user2_id"]
        except:
            flash("Please select the user you want to transfer money with.")
            return redirect("/h")
    except:
        return "error in post request"

    if "." in user1_change:
        parsed_user1_change = user1_change.split(".")
        if len(parsed_user1_change[1]) > 2:
            flash("You can only enter a number with two digits after the decimal point.")
            return redirect("/h")

    try:
        assert type(float(user1_change)) is float
    except:
        flash(user1_change + " is not a valid number")
        return redirect("/h")

    try:
        assert type(int(user2_id)) is int
        assert db.get_user_by_id(user2_id) is not None
    except:
        return "error in post request"

    user2_change = str(-float(user1_change))
    t = Transaction(db.get_transactions_count(), "open", current_user.get_id(), user2_id, user1_change, user2_change)

    if db.get_user_by_id(current_user.get_id()).get_balance() + float(user1_change) < 0:
        flash("You don't have enough money to create this transaction.")
        return redirect("/h")

    db.create_transaction(t)
    return redirect("/h")


# TODO check if the user is accepting his own transaction
# TODO add asserts
@app.route("/api/complete_transaction", methods=["POST"])
@login_required
def api_complete_transaction(answer=None):
    try:
        if answer is None:
            answer = request.form["answer"]
    except:
        return redirect("/h")

    # parse the input data; first element is the answer (accept or reject), the second
    # is the transaction id
    parsed_answer = answer.split(";", 1)

    transaction = db.get_transaction_by_id(parsed_answer[1])

    # check if the initiator is trying to accept his own transfer
    if current_user.get_id() == transaction.get_user1_id() and parsed_answer[0] == "accept":
        flash("You can't accept a transaction you initiated.")
        return redirect("/h")

    # check if the transaction is open
    if transaction.get_status() != "open":
        if transaction.get_status() == "frozen":
            flash("This transaction has been frozen. Contact an administrator if you think this is a mistake.")
        else:
            flash("You can't accept a transaction which is not open.")
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


@app.route("/h/paypal")
@login_required
def paypal():
    return render_template("paypal.html")


@app.route("/api/payment", methods=["POST"])
@login_required
def paypal_start_payment():
    try:
        temp = request.form["0"]
        amount = str(float(temp))

        p = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"},
            "redirect_urls": {
                "return_url": "http://localhost:3000/payment/execute",
                "cancel_url": "http://localhost:3000/"},
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "add money",
                        "sku": "Add money to your balance",
                        "price": amount,
                        "currency": "EUR",
                        "quantity": 1}]},
                "amount": {
                    "total": amount,
                    "currency": "EUR"},
                "description": "This is the payment transaction description."}]})
        if p.create():
            print("Payment success")
            t = PaypalTransaction(db.get_paypal_transactions_count(), current_user.get_id(), amount)
            db.add_paypal_transaction(t)
            print("committed to db")
        else:
            print(p.error)
        return jsonify({"paymentID": p.id})
    except:
        return "error"


@app.route("/api/execute", methods=["POST"])
@login_required
def paypal_execute_payment():
    success = False
    print(request.form["paymentID"])
    p = paypalrestsdk.Payment.find(request.form["paymentID"])
    if p.execute({"payer_id": request.form["payerID"]}):
        print("Execute success")
        success = True

        # update transaction
        t = db.get_latest_paypal_transaction_by_user_id(current_user.get_id())
        t.set_status("completed")
        db.update_paypal_transaction(t)

        # update user
        old_balance = current_user.get_balance()
        current_user.set_balance(old_balance + t.get_amount())
        db.update_user(current_user)
    else:
        print(p.error)
    return jsonify({"success": success})


@app.route("/unauthorized", methods=["GET"])
@login_required
def unauthorized():
    if current_user.get_role() == "frozen":
        return render_template("frozen.html")
    return render_template("unauthorized.html")


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def user_loader(user_id):
    return db.get_user_by_id(user_id)


if __name__ == "__main__":
    app.run()
