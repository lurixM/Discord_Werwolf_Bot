import discord


class Game:

    # Yes, null-reference, I'm a bad person, I know.
    __name_id__ = None
    __user_list = []

    def __init__(self, category: discord.CategoryChannel, user_list: list):
        self.__name_id__ = category
        self.__user_list = user_list

    def get_channel(self):
        return self.__name_id__

    def get_user_list(self):
        return self.__user_list
