from werkzeug.security import check_password_hash


class User:
    def __init__(self, user_id, email, password, role, balance, has_to_reload_page=False):
        self.__id = user_id
        self.__email = email
        self.__password = password
        self.__role = role
        self.__balance = balance
        self.__has_to_reload_page = has_to_reload_page

    def get_email(self):
        return self.__email

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
        return self.__id

    def get_role(self):
        return self.__role

    def get_balance(self):
        return self.__balance

    def set_balance(self, new_balance):
        self.__balance = new_balance

    def has_to_reload_page(self):
        return self.__has_to_reload_page
