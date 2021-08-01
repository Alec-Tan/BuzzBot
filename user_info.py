class UserInfo:
    """Contains the info of a user and their birthday"""
    def __init__(self, user_id, user_name, guild_id, guild_name, month, day):
        self.user_id = user_id
        self.user_name = user_name
        self.guild_id = guild_id
        self.guild_name = guild_name
        self.month = month
        self.day = day