import discord
import requests
from discord.ext import commands, tasks
from user_info import UserInfo
from birthday_channel_info import BirthdayChannelInfo
import database_functions as db
from datetime import datetime

help_file = 'help_message.txt'
months_dict = {'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6, 'july': 7,
               'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12}
saved_day = datetime.today().day    # used to check if the day has changed to check for birthdays

intents = discord.Intents.default()
intents.members = True  # need to enable member intents in order to use bot's get_user() function
bot = commands.Bot(command_prefix=['!buzz ', '!b '], intents=intents)
bot.remove_command('help')  # have to remove so that I can put my own help command


@bot.event
async def on_ready():
    print('Ready!')


@bot.command()
async def help(ctx):
    try:
        with open(help_file) as f:
            help_message = f.read()
    except OSError as e:
        print(e.strerror)
        return
    await ctx.send(help_message)


@bot.command()
async def emote(ctx):
    desired_emote = ctx.message.content[len(ctx.prefix) + len(ctx.invoked_with):].strip()
    url = f"https://api.frankerfacez.com/v1/emotes?q={desired_emote}&sensitive=false&sort=count-desc" \
          f"&high_dpi=off&page=1&per_page=50"
    r = requests.get(url)
    data = r.json()

    final_url = "https:"
    if len(data["emoticons"]) == 0:
        await ctx.reply("Something went wrong! That emote may not exist.")
        return
    else:
        emoteLinks = data["emoticons"][0]["urls"]
        if len(emoteLinks) > 0:
            if "2" in emoteLinks:
                final_url += emoteLinks["2"]
            elif "4" in emoteLinks:
                final_url += emoteLinks["4"]
            else:
                final_url += emoteLinks["1"]
            #await ctx.send(final_url)
        else:
            await ctx.reply("Something went wrong! That emote may not exist.")
            return

    # creating a webhook in the text channel to make it appear as if the user sent the emote
    await ctx.message.delete()
    webhook = await ctx.channel.create_webhook(name=ctx.author.name, reason="Used for emote command")
    await webhook.send(final_url, avatar_url=ctx.author.avatar_url)
    await webhook.delete()


@bot.command()
async def dog(ctx):
    words = ctx.message.content.strip().split()

    # check to see if user inputted arguments past "(prefix) dog"
    if len(words) == 2: # "(prefix) dog"
        r = requests.get("https://dog.ceo/api/breeds/image/random")
        data = r.json()
        if data["status"] == "success":
            await ctx.send(data["message"])
        else:   # api failed to get a random image
            await ctx.reply("Getting a random image of a dog failed. There may be issues with the API.")
    else:   # user inputted too many arguments
        await ctx.reply("I could not understand this command. You may have entered too many arguments.")


@bot.command()
async def dog_breed(ctx):
    # first, need to check if the user actually entered a breed after the command
    if len(ctx.message.content.strip()) == len(ctx.prefix) + len(ctx.invoked_with):
        await ctx.reply("You did not enter a breed after your message.")
    elif len(ctx.message.content) > 50:   # don't want to search for a dog breed too long on the api
        await ctx.reply("Sorry, the dog breed you entered is too long.")
    else:   # search for breed and send link to image if found
        breed = ctx.message.content[len(ctx.prefix) + len(ctx.invoked_with):].strip()
        url = f"https://dog.ceo/api/breed/{breed}/images/random"
        r = requests.get(url)
        data = r.json()
        if data["status"] == "success":
            await ctx.send(data["message"])
        else:
            await ctx.reply(f"Failed to get a random image of a **{breed}**. The breed **{breed}** may not be "
                            f"supported by the API.")


@bot.command()
async def cat(ctx):
    words = ctx.message.content.strip().split()

    # check to see if user inputted arguments past "(prefix) cat"
    if len(words) == 2: # get a random picture of a cat and send in same channel
        r = requests.get("https://api.thecatapi.com/v1/images/search")
        data = r.json()
        if "url" in data[0]:
            await ctx.send(data[0]["url"])
        else:   # failed to get a random image
            await ctx.reply("Failed to get a random image of a cat")
    else: # user inputted too many arguments
        await ctx.reply("I could not understand this command. You may have entered too many arguments.")


@bot.command()
async def cat_breed(ctx):
    # first, need to check if the user actually entered a breed after the command
    if len(ctx.message.content.strip()) == len(ctx.prefix) + len(ctx.invoked_with):
        await ctx.reply("You did not enter a breed after your message.")
    elif len(ctx.message.content) > 50:   # don't want to search for a cat breed too long on the api
        await ctx.reply("Sorry, the cat breed you entered is too long.")
    else:
        # searching for the breed and getting its breed_id
        breed = ctx.message.content[len(ctx.prefix) + len(ctx.invoked_with):].strip()
        url = f"https://api.thecatapi.com/v1/breeds/search?q={breed}"
        r = requests.get(url)
        data = r.json()

        # checking if breed could be found
        if len(data) > 0:  # cat breed exists, get breed id then get image of breed
            breed_id = data[0]["id"]
            new_url = f"https://api.thecatapi.com/v1/images/search?breed_id={breed_id}"
            r = requests.get(new_url)
            data = r.json()

            # checking if searching for the breed_id returned an image
            if len(data) > 0:  # call returned information about the breed
                await ctx.send(data[0]["url"])
            else:  # call did not return info about the breed
                await ctx.reply(f"Failed to get a random image of a **{breed}**. The breed **{breed}** may not be "
                                f"supported.")
        else:   # breed could not be found
            await ctx.reply(f"Failed to get a random image of a **{breed}**. The breed **{breed}** may not be "
                            f"supported.")


@bot.command()
async def set_birthday_channel(ctx):
    """
    Command that allow a user to set a birthday channel for the current guild.

    This channel is where birthday messages will be sent for this specific guild.
    The user must mention the desired channel.
    Example usage: "(prefix) set_birthday_channel #birthdays"

    :param ctx: Represents the context in which a command is being invoked under.
    """

    words = ctx.message.content.strip().split()

    if len(words) == 3:  # user entered a correct number of inputs
        channel_list = ctx.message.channel_mentions

        if len(channel_list) == 0:  # user did not properly mention a channel
            await ctx.reply('It looks like you did not mention a channel. Ex: "!buzz set_birthday_channel '
                            '#birthday_channel"')
        else:   # user properly mentioned a channel
            bday_channel = channel_list[0]
            if type(bday_channel) == discord.TextChannel:
                # attempt to insert the birthday channel's info into the database
                bday_channel_info = BirthdayChannelInfo(bday_channel.guild.id, bday_channel.guild.name,
                                                        bday_channel.id, bday_channel.name)
                if db.insert_birthday_channel(bday_channel_info):
                    await ctx.reply(f"Set {bday_channel.mention} as this server's birthday channel")
                else:
                    await ctx.reply("Something went wrong - failed to insert into the database")
            else:
                await ctx.reply("It looks like the channel you mentioned is not a text channel")
    elif len(words) == 2:  # user only entered "(prefix) set_bday_channel"
        await ctx.reply('Please mention a channel after the command.'
                        'Ex: "!buzz set_birthday_channel #birthday_channel"')


@bot.command()
async def birthday_channel(ctx):
    """
    Command that replies with the birthday channel currently set for the specific guild.

    :param ctx: Represents the context in which a command is being invoked under.
    """

    words = ctx.message.content.strip().split()

    # check to see if user message contains more than just "(prefix) birthday_channel"
    if len(words) > 2:
        await ctx.reply('You may have entered too many arguments. Example usage: "!buzz birthday_channel"')
        return

    # query the database to get the id of the guild's birthday channel if can be found,
    birthday_channel_id = db.get_birthday_channel_id(ctx.guild.id)
    if birthday_channel_id == -1:
        await ctx.reply("This server does not have a birthday channel set")
        return

    # get the corresponding birthday channel
    found_channel = bot.get_channel(birthday_channel_id)
    if found_channel is None:   # channel couldn't be found, was possibly deleted
        await ctx.reply("This server does not have a birthday channel set")
        return

    await ctx.reply(f"The birthday channel is currently set to {found_channel.mention}")


@bot.command()
async def remove_birthday_channel(ctx):
    """
    Command that deletes the birthday channel currently set for the specific guild.

    :param ctx: Represents the context in which a command is being invoked under.
    """
    words = ctx.message.content.strip().split()

    # check to see if user message contains more than just "(prefix) remove_birthday_channel"
    if len(words) > 2:
        await ctx.reply('You may have entered too many arguments. Example usage: "!buzz remove_birthday_channel"')
        return

    # attempt to delete this guild's birthday channel
    if db.delete_birthday_channel(ctx.guild.id):
        await ctx.reply("Removed this server's birthday channel")
    else:
        await ctx.reply("This server does not have a birthday channel set")



@bot.command()
async def set_birthday(ctx):
    """
    Command that allows a user to set their birthday.

    :param ctx: Represents the context in which a command is being invoked under.
    """

    words = ctx.message.content.strip().split()
    incorrect_format_msg = 'You may have entered an incorrect format or an invalid date. ' \
                           'Example usage: "!b set_birthday 5/23" or "!b set_birthday may 23"'

    # check to see if the user entered a correct number of inputs to set a birthday
    if len(words) == 3:  # user entered an input such as "(prefix) set_birthday 3/14"
        # check to see if the user entered a valid input for their birthday
        month_and_day = words[2].split('/')
        if len(month_and_day) == 2:  # correct format for the month and day using a / character
            if month_and_day[0].isdigit() and month_and_day[1].isdigit():  # if month and day are numbers
                month = int(month_and_day[0])
                day = int(month_and_day[1])
                if date_is_valid(month, day):
                    # attempt to insert the user's birthday into the database
                    user_info = UserInfo(ctx.author.id, ctx.author.name, ctx.guild.id, ctx.guild.name, month, day)
                    if db.insert_birthday(user_info):
                        await ctx.reply(f'Set {words[2]} as your birthday.')
                    else:
                        await ctx.reply('Something went wrong - failed to insert into the database')
                    return
        # if user's input of month and date were not in an expected format
        await ctx.reply(incorrect_format_msg)
    elif len(words) == 4:    # user entered an input such as "(prefix) set_birthday march 14"
        # check to see if the user entered a valid input for their birthday
        if words[2].lower() in months_dict and words[3].isdigit():  # if user entered correct month and a digit for day
            month = months_dict[words[2].lower()]
            day = int(words[3])
            if date_is_valid(month, day):
                # attempt to insert the user's birthday into the database
                user_info = UserInfo(ctx.author.id, ctx.author.name, ctx.guild.id, ctx.guild.name, month, day)
                if db.insert_birthday(user_info):
                    await ctx.reply(f'Set {month}/{day} as your birthday.')
                else:
                    await ctx.reply('Something went wrong - failed to insert into the database')
                return

        # if user's input of month and date were not in an expected format
        await ctx.reply(incorrect_format_msg)
    elif len(words) == 2:  # user only entered "(prefix) set_birthday"
        await ctx.reply('Please enter a month and day. Ex: "!b set_birthday 5/23" or "!b set_birthday may 23"')
    else:   # user entered too many arguments
        await ctx.reply('You may have entered too many arguments. Example usage:'
                        ' "!b set_birthday 5/23" or "!b set_birthday may 23""')


# checks to see if a given month and day are valid
def date_is_valid(month, day):
    try:
        test_date = datetime(2020, int(month), int(day))
        return True
    except ValueError:
        return False


@bot.command()
async def birthday(ctx):
    words = ctx.message.content.strip().split()

    if len(words) > 2:  # if user message contains more than just "(prefix) birthday"
        await ctx.reply('You may have entered too many arguments. Example usage: "!buzz birthday"')
    else:   # read the users file to try to find the user's birthday
        try:
            with open(users_file) as f:
                data = f.readlines()
        except OSError as e:
            print(e.strerror)
            return

        user_index = find_user_index(data, ctx.author.id, ctx.guild.id)
        if user_index != -1:    # if user and their birthday were found in file
            pieces = data[user_index].strip().split(',')
            month = pieces[4]
            day = pieces[5]
            await ctx.reply(f'Your birthday is currently set to {month}/{day}')
        else:   # user and their birthday not found in file
            await ctx.reply('Your birthday is not currently set')


@bot.command()
async def remove_birthday(ctx):
    words = ctx.message.content.strip().split()

    if len(words) > 2:  # if user message contains more than just "(prefix) remove_birthday"
        await ctx.reply('You may have entered too many arguments. Example usage: "!buzz remove_birthday"')
    else:   # need to search file to see for user and remove if found
        try:
            with open(users_file) as f:
                data = f.readlines()
        except OSError as e:
            print(e.strerror)
            return

        user_index = find_user_index(data, ctx.author.id, ctx.guild.id)
        if user_index != -1:    # if user and their birthday were found in file
            data.pop(user_index)
            with open(users_file, 'w') as f:
                f.writelines(data)
            await ctx.reply("Successfully removed your birthday")
        else:   # user not found
            await ctx.reply("You did not have a birthday set previously")


@tasks.loop(seconds=5.0)
async def check_for_birthdays():
    global saved_day
    today = datetime.today()

    if today.day != saved_day:  # this means that the day has changed
        saved_day = today.day

        # read the users file and guilds file so that we can check for birthdays after
        try:
            with open(users_file) as f:
                f.readline()    # get past header
                users_data = f.readlines()
            with open(guilds_file) as f:
                f.readline()  # get past header
                guilds_data = f.readlines()
        except OSError as e:
            print(e.strerror)
            return

        # search through the users file and send messages for each user birthday in corresponding birthday channels
        for line in users_data:
            user_pieces = line.strip().split(',')
            if int(user_pieces[4]) == today.month and int(user_pieces[5]) == today.day:
                user_id = user_pieces[1]
                user = bot.get_user(int(user_id))
                guild_id = user_pieces[3]
                guild_index = find_guild_index(guilds_data, guild_id)
                guild_pieces = guilds_data[guild_index].strip().split(',')
                bday_channel_id = guild_pieces[3]
                bday_channel = bot.get_channel(int(bday_channel_id))
                if user is None:    # user couldn't be found, possibly deleted
                    continue
                if bday_channel is None:    # channel couldn't be found, possibly deleted
                    continue

                # if the bot is allowed to send messages to the bday_channel, send birthday message
                if bday_channel.permissions_for(bday_channel.guild.me).send_messages:
                    await bday_channel.send(f'Happy birthday {user.mention}!')


check_for_birthdays.start()
# bot.run('BOT TOKEN HERE)
