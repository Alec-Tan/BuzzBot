import discord
import requests
from discord.ext import commands, tasks
from datetime import datetime

help_file = 'help_message.txt'
guilds_file = 'guilds.csv'
users_file = 'users.csv'
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
    words = ctx.message.content.strip().split()

    # attempt to get the channel id of the user's mentioned channel
    if len(words) == 3:  # user entered a correct number of inputs
        channel_list = ctx.message.channel_mentions
        if len(channel_list) == 0:  # user did not properly mention a channel
            await ctx.reply('It looks like you did not mention a channel. Ex: "!buzz set_bday_channel '
                            '#birthday_channel"')
        else:   # user properly mentioned a channel
            bday_channel = channel_list[0]
            if type(bday_channel) == discord.TextChannel:
                write_birthday_channel(guilds_file, ctx.guild, bday_channel)
                await ctx.reply(f"Set {bday_channel.mention} as this server's birthday channel")
            else:
                await ctx.reply("It looks like the channel you mentioned is not a text channel")
    elif len(words) == 2: # user only entered "(prefix) set_bday_channel"
        await ctx.reply('Please mention a channel after the command. Ex: "!buzz set_bday_channel #birthday_channel"')


# helper function for set_bday_channel
# writes the guild name, guild id, bday channel name, and bday channel id to guilds_file (csv)
def write_birthday_channel(file, guild, bday_channel):
    guild_name = guild.name
    guild_id = guild.id
    bday_channel_name = bday_channel.name
    bday_channel_id = bday_channel.id

    # read guilds_file and put its lines in data. add next line character to header as well
    try:
        with open(file) as f:
            data = f.readlines()
            if len(data) > 0:
                data[0] = data[0].strip() + '\n'    # add next line character to the header if it doesn't have it
    except OSError as e:
        print(e.strerror)
        return

    # check to see if the guild is already in guilds_file
    guild_index = find_guild_index(data, guild_id)
    # if the guild's id was found in guilds_file, edit the guild's info
    if guild_index != -1:
        found_guild = data[guild_index].strip().split(',')
        found_guild[0] = guild_name
        found_guild[2] = bday_channel_name
        found_guild[3] = str(bday_channel_id)
        data[guild_index] = ','.join(found_guild) + '\n'
    else:   # if the guild does not already exist in guilds_file, need to add it as a new line
        data.append(','.join([guild_name, str(guild_id), bday_channel_name, str(bday_channel_id)]) + '\n')

    # write to new guilds_file
    with open(file, 'w') as f:
        f.writelines(data)     # no need to worry about new line characters since already added them


# searches for a guild in a list of lines and returns the index. if the guild couldn't be found, returns -1
def find_guild_index(lines_list, guild_id):
    for i in range(len(lines_list)):
        pieces = lines_list[i].strip().split(',')
        if len(pieces) != 4:    # if the line has more or less values than it should
            return -1
        else:
            if pieces[1] == str(guild_id):
                return i
    return -1



@bot.command()
async def birthday_channel(ctx):
    words = ctx.message.content.strip().split()
    if len(words) > 2:  # if user message contains more than just "(prefix) bday_channel"
        await ctx.reply('You may have entered too many arguments. Example usage: "!buzz bday_channel"')
        return
    else:   # read the guilds file to try to find the guild's birthday channel
        try:
            with open(guilds_file) as f:
                data = f.readlines()
        except OSError as e:
            print(e.strerror)
            return

        guild_index = find_guild_index(data, ctx.guild.id)
        if guild_index != -1:    # guild was found in the guilds file
            pieces = data[guild_index].strip().split(',')
            bday_channel_id = pieces[3]
            found_channel = bot.get_channel(int(bday_channel_id))
            if found_channel is None:   # channel couldn't be found, was possibly deleted
                await ctx.reply("This server does not have a birthday channel set")
                return
            await ctx.reply(f"The birthday channel is currently set to {found_channel.mention}")
        else:   # guild was not found in guilds file
            await ctx.reply("This server does not have a birthday channel set")


@bot.command()
async def remove_birthday_channel(ctx):
    words = ctx.message.content.strip().split()
    if len(words) > 2:  # if user message contains more than just "(prefix) remove_bday_channel"
        await ctx.reply('You may have entered too many arguments. Example usage: "!buzz remove_bday_channel"')
        return
    else:   # read the guilds file to see if the guild already has a birthday channel set
        try:
            with open(guilds_file) as f:
                data = f.readlines()
        except OSError as e:
            print(e.strerror)
            return

        guild_index = find_guild_index(data, ctx.guild.id)
        if guild_index != -1:    # guild was found in the guilds file, remove from file
            data.pop(guild_index)
            with open(guilds_file, 'w') as f:
                f.writelines(data)
            await ctx.reply(f"Removed this server's birthday channel")
        else:   # guild was not found in guilds file
            await ctx.reply("This server does not have a birthday channel set")


# searches for a user in a list of lines and returns the index. if the user couldn't be found, returns -1
# the same user can be in the file multiple times if they are entered with different guilds
def find_user_index(lines_list, user_id, guild_id):
    for i in range(len(lines_list)):
        pieces = lines_list[i].strip().split(',')
        if len(pieces) != 6:    # if the line has more or less values than it should
            return -1
        else:
            if pieces[1] == str(user_id) and pieces[3] == str(guild_id):
                return i
    return -1


@bot.command()
async def set_birthday(ctx):
    words = ctx.message.content.strip().split()
    incorrect_format_msg = 'You may have entered an incorrect format or an invalid date. ' \
                           'Example usage: "!b set_birthday 5/23" or "!b set_birthday may 23"'

    # check to see if the user entered a correct number of inputs to set a birthday
    if len(words) == 3:  # user entered an input such as "(prefix) set_birthday 3/14"
        month_and_day = words[2].split('/')
        if len(month_and_day) == 2:     # correct format for the month and day using a / character
            if month_and_day[0].isdigit() and month_and_day[1].isdigit():   # if month and day are numbers
                month = month_and_day[0]
                day = month_and_day[1]
                if date_is_valid(month, day):
                    write_birthday(users_file, ctx.author, ctx.guild, month, day)
                    await ctx.reply(f'Set {words[2]} as your birthday.')
                    return
        # if user's input of month and date were not in an expected format
        await ctx.reply(incorrect_format_msg)
    elif len(words) == 4:    # user entered an input such as "(prefix) set_birthday march 14"
        if words[2].lower() in months_dict and words[3].isdigit():  # if user entered correct month and a digit for day
            month = months_dict[words[2].lower()]
            day = int(words[3])
            if date_is_valid(month, day):
                write_birthday(users_file, ctx.author, ctx.guild, month, day)
                await ctx.reply(f'Set {months_dict[words[2].lower()]}/{words[3]} as your birthday.')
                return
        # if user's input of month and date were not in an expected format
        await ctx.reply(incorrect_format_msg)
    elif len(words) == 2:  # user only entered "(prefix) set_birthday"
        await ctx.reply('Please enter a month and day. Ex: "!b set_birthday 5/23" or "!b set_birthday may 23"')
    else:   # user entered too many arguments
        await ctx.reply('You may have entered too many arguments. Example usage:'
                        ' "!b set_birthday 5/23" or "!b set_birthday may 23""')


# helper function for set_birthday(). writes
def write_birthday(file, user, guild, month, day):
    user_name = user.name
    user_id = user.id
    guild_name = guild.name
    guild_id = guild.id

    # read users_file and put its lines in data. add next line character to header as well
    try:
        with open(file) as f:
            data = f.readlines()
            if len(data) > 0:
                data[0] = data[0].strip() + '\n'  # add next line character to the header if it doesn't have it
    except OSError as e:
        print(e.strerror)
        return

    # check to see if the user is already in users_file
    user_index = find_user_index(data, user_id, guild_id)
    # if the user's id was found in users_file, edit the guild's info
    if user_index != -1:
        found_user = data[user_index].strip().split(',')
        found_user[0] = user_name
        found_user[2] = guild_name
        found_user[3] = str(guild_id)
        found_user[4] = str(month)
        found_user[5] = str(day)
        data[user_index] = ','.join(found_user) + '\n'
    else:  # if the user does not already exist in users_file, need to add it as a new line
        data.append(','.join([user_name, str(user_id), guild_name, str(guild_id), str(month), str(day)]) + '\n')

    # write to new users_file
    with open(file, 'w') as f:
        f.writelines(data)  # no need to worry about new line characters since already added them


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
