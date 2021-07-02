from sqlalchemy import create_engine

from user import User

db_string = "postgresql://telebidPractice:telebidPractice@localhost"
db = create_engine(db_string)


class Database:
    def __init__(self):
        db.execute("DROP TABLE IF EXISTS Users;")
        db.execute("CREATE TABLE IF NOT EXISTS Users ("
                   "id serial not null primary key,"
                   "name varchar(20) unique,"
                   "password varchar(128)"
                   ")")

    @staticmethod
    def add_user(user):
        statement = "INSERT INTO Users(name, password) VALUES('{}', '{}')".format(user.get_name(), user.get_password())
        db.execute(statement)

    @staticmethod
    def get_user_by_name(name):
        rows = db.execute("SELECT * FROM Users WHERE name = '{}'".format(name))

        for row in rows:
            return User(row[1], row[2])
        return None
