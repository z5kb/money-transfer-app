import datetime

class PaypalTransaction:
    def __init__(self, transaction_id, user_id, amount, status="in progress", timestamp=None):
        self.__id = transaction_id
        self.__user_id = user_id
        self.__amount = amount
        self.__status = status
        self.__timestamp = timestamp

    def get_id(self):
        return self.__id

    def get_user_id(self):
        return self.__user_id

    def get_amount(self):
        return self.__amount

    def get_status(self):
        return self.__status

    def get_timestamp(self):
        return self.__timestamp

    def set_status(self, new_status):
        self.__status = new_status
