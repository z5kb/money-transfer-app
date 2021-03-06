from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash

from user import User
from transaction import Transaction
from paypal_transaction import PaypalTransaction

db_string = "postgresql://telebidPractice:telebidPractice@localhost"
db = create_engine(db_string)


class Database:
    def __init__(self):
        db.execute("DROP TABLE IF EXISTS Transactions;")
        db.execute("DROP TABLE IF EXISTS PaypalTransactions;")
        db.execute("DROP TABLE IF EXISTS Users;")
        db.execute("DROP TYPE IF EXISTS user_role_enum;")
        db.execute("CREATE TYPE user_role_enum AS ENUM ('user', 'admin', 'frozen');")
        db.execute("CREATE TABLE IF NOT EXISTS Users ("
                   "id serial not null primary key,"
                   "email varchar(20) unique,"
                   "password varchar(128),"
                   "role user_role_enum default 'user',"
                   "balance float CHECK(balance >= 0) default 10,"
                   "has_to_reload_page bool default false"
                   ");")

        user1 = User(1, 'first@fake.org', generate_password_hash('1'), "user", 15.45)
        self.add_user(user1)
        user2 = User(2, 'second@fake.org', generate_password_hash('2'), "user", 5)
        self.add_user(user2)
        user3 = User(3, 'third@fake.org', generate_password_hash('3'), "user", 8)
        self.add_user(user3)
        user4 = User(4, 'fourth@fake.org', generate_password_hash('4'), "user", 9)
        self.add_user(user4)
        admin1 = User(5, 'a', generate_password_hash('a'), "admin", 0)
        self.add_user(admin1)

        # user1 is the initiator of the transfer, user2 is the receiver
        db.execute("DROP TYPE IF EXISTS transaction_status_enum;")
        db.execute("CREATE TYPE transaction_status_enum AS ENUM ('open', 'accepted', 'rejected', 'frozen');")
        db.execute("CREATE TABLE IF NOT EXISTS Transactions ("
                   "id serial not null primary key,"
                   "status transaction_status_enum default 'open',"
                   "user1_id int not null,"
                   "user2_id int not null,"
                   "user1_change float not null,"
                   "user2_change float not null,"
                   "FOREIGN KEY(user1_id) REFERENCES Users(id),"
                   "FOREIGN KEY(user2_id) REFERENCES Users(id)"
                   ");")
        db.execute("INSERT INTO Transactions(user1_id, user2_id, user1_change, user2_change) VALUES(1, 2, 5, -5);")
        db.execute("INSERT INTO Transactions(user1_id, user2_id, user1_change, user2_change) VALUES(2, 1, 5, -5);")

        # create table for the PayPal transactions
        db.execute("DROP TYPE IF EXISTS paypal_transactions_status_enum;")
        db.execute("CREATE TYPE paypal_transactions_status_enum AS ENUM ('failed', 'completed', 'in progress');")
        db.execute("CREATE TABLE IF NOT EXISTS PaypalTransactions ("
                   "id serial not null primary key,"
                   "user_id int not null,"
                   "amount float not null,"
                   "status paypal_transactions_status_enum,"
                   "timestamp timestamp default current_timestamp,"
                   "FOREIGN KEY(user_id) REFERENCES Users(id),"
                   "paypal_id text"
                   ");")
        db.execute("INSERT INTO PaypalTransactions(user_id, amount, status) VALUES(1, 1.36, 'completed');")
        db.execute("INSERT INTO PaypalTransactions(user_id, amount, status) VALUES(1, 2.73, 'completed');")
        db.execute("INSERT INTO PaypalTransactions(user_id, amount, status) VALUES(1, 345, 'completed');")

        # prepare statements
        # db.execute("PREPARE close_transaction(transaction_status_enum, int) AS "
        #            "UPDATE Transactions SET status = $1 WHERE id = $2;")

    @staticmethod
    def add_user(user):
        db.execute("INSERT INTO Users(email, password, balance, role) VALUES('{}', '{}', {}, '{}');"
                   .format(user.get_email(), user.get_password(), user.get_balance(), user.get_role()))
        return True

    @staticmethod
    def get_user_by_email(email):
        rows = db.execute("SELECT * FROM Users WHERE email = '{}';".format(email))

        for r in rows:
            return User(r[0], r[1], r[2], r[3], r[4])
        return None

    @staticmethod
    def get_user_by_id(user_id):
        rows = db.execute("SELECT * FROM Users WHERE id = {};".format(user_id))

        for r in rows:
            return User(r[0], r[1], r[2], r[3], r[4])
        return None

    @staticmethod
    def get_users_as_list():
        rows = db.execute("SELECT * FROM Users ORDER BY id;")

        users = []
        for r in rows:
            if r[3] == "user" or r[3] == "frozen":
                users.append([r[0], r[1], r[3], r[4]])
        return users

    @staticmethod
    def get_users_of_current_user(current_user):
        rows = db.execute("SELECT * FROM Users;")

        users = []
        for r in rows:
            if current_user.get_email() != r[1] and r[3] == "user":
                users.append([r[0], r[1]])
        return users

    @staticmethod
    def update_user_balance(user):
        db.execute("UPDATE Users SET balance = {}, has_to_reload_page = 'true' WHERE id = {};"
                   .format(user.get_balance(), user.get_id()))
        return True

    @staticmethod
    def get_transaction_by_id(transaction_id):
        rows = db.execute("SELECT * FROM Transactions WHERE id = {};".format(transaction_id))

        for r in rows:
            return Transaction(r[0], r[1], r[2], r[3], r[4], r[5])
        return None

    @staticmethod
    def get_transactions():
        rows = db.execute("SELECT * FROM Transactions ORDER BY id;")

        transactions = []
        for r in rows:
            transactions.append([r[0], r[1], r[2], r[3], r[4], r[5]])
        return transactions

    @staticmethod
    def get_transactions_of_current_user(current_user):
        rows = db.execute("SELECT * FROM Transactions WHERE user1_id = {} OR user2_id = {} ORDER BY id DESC;"
                          .format(current_user.get_id(), current_user.get_id()))

        transactions = []
        for r in rows:
            if current_user.get_id() == r[2]:
                transactions.append([r[0], r[1], r[2], Database.get_user_email_by_id(r[3]), r[4], r[5], "== user1"])
            elif current_user.get_id() == r[3]:
                transactions.append([r[0], r[1], Database.get_user_email_by_id(r[2]), r[3], r[4], r[5], "!= user1"])
        return transactions

    @staticmethod
    def get_user_email_by_id(u_id):
        rows = db.execute("SELECT email FROM Users WHERE id = {};"
                          .format(u_id))

        for r in rows:
            return r[0]
        return None

    @staticmethod
    def create_transaction(t):
        db.execute("INSERT INTO Transactions(user1_id, user2_id, user1_change, user2_change) VALUES({}, {}, {}, {})"
                   .format(t.get_user1_id(), t.get_user2_id(), t.get_user1_change(), t.get_user2_change()))
        return True

    @staticmethod
    def complete_transaction(action, transaction_id):
        # validate the data from the HTML form
        if action != "accept" and action != "reject":
            return False
        elif action == "accept":
            # get the data needed for the transfer
            transaction = Database.get_transaction_by_id(transaction_id)
            user1 = Database.get_user_by_id(transaction.get_user1_id())
            user2 = Database.get_user_by_id(transaction.get_user2_id())

            # update users' money balances
            user1.set_balance(round(user1.get_balance() + transaction.get_user1_change(), 2))
            user2.set_balance(round(user2.get_balance() + transaction.get_user2_change(), 2))

            # validate new money balances balances
            if user1.get_balance() < 0 or user2.get_balance() < 0:
                return False

            # push changes to DB
            Database.update_user_balance(user1)
            Database.update_user_balance(user2)

        # close transaction
        db.execute("UPDATE Transactions SET status = '{}' WHERE id = {};".format(action + "ed", transaction_id))

        # try:
        #     print("in try")
        #     db.execute("EXECUTE close_transaction('{}', {})".format(action + "ed", int(transaction_id)))
        # except Exception as e:
        #     print("in except: " + str(e))
        #     db.execute("PREPARE close_transaction(transaction_status_enum, int) AS "
        #                "UPDATE Transactions SET status = $1 WHERE id = $2;")
        #     db.execute("EXECUTE close_transaction('{}', {})".format(action + "ed", int(transaction_id)))
        # print("outside of try-except")

        return True

    @staticmethod
    def freeze_transaction(transaction):
        db.execute("UPDATE Transactions SET status = '{}' WHERE id = {};"
                   .format(transaction.get_status(), transaction.get_id()))
        return True

    @staticmethod
    def delete_user_by_id(user_id):
        # delete user's transactions
        Database.delete_user_transactions_by_user_id(user_id)
        Database.delete_user_paypal_transactions_by_user_id(user_id)

        db.execute("DELETE FROM Users WHERE id = {};".format(user_id))
        return True

    @staticmethod
    def update_user(new_user):
        db.execute("UPDATE Users SET email = '{}', password = '{}', role = '{}', balance = {} WHERE id = {};"
                   .format(new_user.get_email(), new_user.get_password(), new_user.get_role(),
                           new_user.get_balance(), new_user.get_id()))
        return True

    @staticmethod
    def delete_user_transactions_by_user_id(user_id):
        db.execute("DELETE FROM Transactions WHERE user1_id = {} OR user2_id = {};"
                   .format(user_id, user_id))
        return True

    @staticmethod
    def delete_user_paypal_transactions_by_user_id(user_id):
        db.execute("DELETE FROM PaypalTransactions WHERE user_id = {};"
                   .format(user_id))
        return True

    @staticmethod
    def freeze_user_open_transactions(user):
        db.execute("UPDATE Transactions SET status = '{}' WHERE (user1_id = {} OR user2_id = {}) AND status = '{}';"
                   .format("frozen", user.get_id(), user.get_id(), "open"))
        return True

    @staticmethod
    def unfreeze_user_transactions(user):
        db.execute("UPDATE Transactions SET status = '{}' WHERE (user1_id = {} OR user2_id = {}) AND status = '{}';"
                   .format("open", user.get_id(), user.get_id(), "frozen"))
        return True

    @staticmethod
    def get_paypal_transaction_by_id(t_id):
        rows = db.execute("SELECT * FROM PaypalTransactions WHERE id = {};"
                          .format(t_id))
        for r in rows:
            return PaypalTransaction(r[0], r[1], r[2], r[3])
        return None

    @staticmethod
    def get_paypal_transactions_as_list_of_current_user(current_user):
        rows = db.execute("SELECT * FROM PaypalTransactions WHERE user_id = {} ORDER BY timestamp DESC;"
                          .format(current_user.get_id()))

        transactions = []
        for r in rows:
            transactions.append([r[2], r[3], str(r[4]), r[5]])
        return transactions

    @staticmethod
    def get_paypal_transactions():
        rows = db.execute("SELECT * FROM PaypalTransactions ORDER BY timestamp DESC;")

        transactions = []
        for r in rows:
            transactions.append([r[0], r[1], r[2], r[3], str(r[4]), r[5]])
        return transactions

    @staticmethod
    def get_latest_paypal_transaction_by_user_id(u_id):
        rows = db.execute("SELECT * FROM PaypalTransactions WHERE user_id = {} ORDER BY timestamp DESC;"
                          .format(u_id))
        for r in rows:
            return PaypalTransaction(r[0], r[1], r[2], r[3], r[4])
        return None

    @staticmethod
    def add_paypal_transaction(t):
        db.execute("INSERT INTO PaypalTransactions(user_id, amount, status) VALUES({}, {}, '{}');"
                   .format(t.get_user_id(), t.get_amount(), t.get_status()))
        return True

    @staticmethod
    def update_paypal_transaction(t):
        db.execute("UPDATE PaypalTransactions "
                   "SET user_id = {}, amount = {}, status = '{}', paypal_id = '{}' "
                   "WHERE id = {};"
                   .format(t.get_user_id(), t.get_amount(), t.get_status(), t.get_paypal_id(), t.get_id()))
        return True

    @staticmethod
    def get_users_count():
        rows = db.execute("SELECT COUNT(id) FROM Users;")

        for r in rows:
            return r[0]
        return None

    @staticmethod
    def get_transactions_count():
        rows = db.execute("SELECT COUNT(id) FROM Transactions;")

        for r in rows:
            return r[0]
        return None

    @staticmethod
    def get_paypal_transactions_count():
        rows = db.execute("SELECT COUNT(id) FROM PaypalTransactions;")

        for r in rows:
            return r[0]
        return None
