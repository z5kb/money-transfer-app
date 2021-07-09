class Transaction:
    def __init__(self, transaction_id, status, user1_id, user2_id, user1_change, user2_change):
        self.__id = transaction_id
        self.__status = status
        self.__user1_id = user1_id
        self.__user2_id = user2_id
        self.__user1_change = user1_change
        self.__user2_change = user2_change

    def get_id(self):
        return self.__id

    def get_status(self):
        return self.__status

    def get_user1_id(self):
        return self.__user1_id

    def get_user2_id(self):
        return self.__user2_id

    def get_user1_change(self):
        return self.__user1_change

    def get_user2_change(self):
        return self.__user2_change

    def set_status(self, new_status):
        self.__status = new_status
