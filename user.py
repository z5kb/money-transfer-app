from werkzeug.security import check_password_hash
from app import psql


class User(psql.Model):
    __tablename__ = 'Users'

    id = psql.Column(psql.Integer, primary_key=True)
    name = psql.Column(psql.String())
    password = psql.Column(psql.String())

    def __init__(self, name, password):
        self.__name = name
        self.__password = password

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def get_name(self):
        return self.__name

    def get_password(self):
        return self.__password

    def verify_password(self, password):
        return check_password_hash(self.__password, password)

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.__name
