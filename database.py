from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash

from user import User
from transaction import Transaction

db_string = "postgresql://telebidPractice:telebidPractice@localhost"
db = create_engine(db_string)


# TODO replace id with UUID in all tables
class Database:
    def __init__(self):
        db.execute("DROP TABLE IF EXISTS Transactions;")
        db.execute("DROP TABLE IF EXISTS Users;")
        db.execute("DROP TYPE IF EXISTS role_enum;")
        db.execute("CREATE TYPE role_enum AS ENUM ('user', 'admin', 'frozen');")
        db.execute("CREATE TABLE IF NOT EXISTS Users ("
                   "id serial not null primary key,"
                   "email varchar(20) unique,"
                   "password varchar(128),"
                   "role role_enum default 'user',"
                   "balance float CHECK(balance >= 0) default 10,"
                   "has_to_reload_page bool default false"
                   ");")

        user1 = User(1, '1st', generate_password_hash('1'), "user", 0)
        self.add_user(user1)
        user2 = User(2, '2nd', generate_password_hash('2'), "user", 5)
        self.add_user(user2)
        user3 = User(3, '3rd', generate_password_hash('3'), "user", 8)
        self.add_user(user3)
        user4 = User(4, '4th', generate_password_hash('4'), "user", 9)
        self.add_user(user4)

        # user1 is the initiator of the transfer, user2 is the receiver
        db.execute("DROP TYPE IF EXISTS transaction_status_enum;")
        db.execute("CREATE TYPE transaction_status_enum AS ENUM ('open', 'closed', 'frozen', 'failed');")
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

    @staticmethod
    def add_user(user):
        statement = "INSERT INTO Users(email, password, balance) VALUES('{}', '{}', {});"\
            .format(user.get_email(), user.get_password(), user.get_balance())
        db.execute(statement)

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

    # TODO change this (returning lists of users' data, not users)
    @staticmethod
    def get_users(current_user):
        rows = db.execute("SELECT * FROM Users;")

        users = []
        for r in rows:
            if current_user.get_email() != r[1]:
                users.append([r[0], r[1]])
        return users

    @staticmethod
    def update_user_balance(user):
        db.execute("UPDATE Users SET balance = {}, has_to_reload_page = 'true' WHERE id = {};"
                   .format(user.get_balance(), user.get_id()))
        return True

    @staticmethod
    def get_transaction(transaction_id):
        rows = db.execute("SELECT * FROM Transactions WHERE id = {};".format(transaction_id))

        for r in rows:
            return Transaction(r[0], r[1], r[2], r[3], r[4], r[5])
        return None

    @staticmethod
    def get_transactions_of_current_user(current_user):
        rows = db.execute("SELECT * FROM Transactions WHERE user1_id = {} OR user2_id = {} ORDER BY id DESC;"
                          .format(current_user.get_id(), current_user.get_id()))

        transactions = []
        for r in rows:
            transactions.append([r[0], r[1], r[2], r[3], r[4], r[5]])
        return transactions

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
            transaction = Database.get_transaction(transaction_id)
            user1 = Database.get_user_by_id(transaction.get_user1_id())
            user2 = Database.get_user_by_id(transaction.get_user2_id())

            # update users' money balances
            user1.set_balance(user1.get_balance() + transaction.get_user1_change())
            user2.set_balance(user2.get_balance() + transaction.get_user2_change())

            # validate new money balances balances
            if user1.get_balance() < 0 or user2.get_balance() < 0:
                return False

            # push changes to DB
            Database.update_user_balance(user1)
            Database.update_user_balance(user2)

        # close transaction
        db.execute("UPDATE Transactions SET status = 'closed' WHERE id = {};".format(transaction_id))
        return True

    @staticmethod
    def update_user(new_user):
        db.execute("UPDATE Users SET email = '{}', password = '{}' WHERE id = {};"
                   .format(new_user.get_email(), new_user.get_password(), new_user.get_id()))

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
