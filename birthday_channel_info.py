class BirthdayChannelInfo:
    """Contains the birthday channel set for a specific guild"""
    def __init__(self, guild_id, guild_name, birthday_channel_id, birthday_channel_name):
        self.guild_id = guild_id
        self.guild_name = guild_name
        self.birthday_channel_id = birthday_channel_id
        self.birthday_channel_name = birthday_channel_name