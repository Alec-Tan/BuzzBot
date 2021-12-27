import os
from dotenv import load_dotenv
import discord
import requests
from discord.ext import commands, tasks
from user_info import UserInfo
from birthday_channel_info import BirthdayChannelInfo
import database_functions as db
from datetime import datetime

load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
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
    """Command that sends a help message displaying all of the bot's commands."""
    embed = discord.Embed(
        title="Commands",
        color=discord.Colour.gold()
    )

    try:
        with open(help_file) as f:
            help_message = f.read()
            embed.description = help_message
            await ctx.send(embed=embed)
    except OSError as e:
        print(e.strerror)


@bot.command()
async def emote(ctx):
    """
    Command that searches for and sends an emote from FrankerFaceZ.

    The user's message will be deleted, and the bot will use a webhook to make it appear as if the user sent
    the emote.
    Example usage: "(prefix) emote PepeHands"
    """

    # Use the API to search for the emote.
    desired_emote = ctx.message.content[len(ctx.prefix) + len(ctx.invoked_with):].strip()
    url = f"https://api.frankerfacez.com/v1/emotes?q={desired_emote}&sensitive=false&sort=count-desc" \
          f"&high_dpi=off&page=1&per_page=50"
    r = requests.get(url)
    data = r.json()

    # Get the url for the emote's image if found.
    final_url = "https:"
    if len(data["emoticons"]) == 0:
        await ctx.reply("Something went wrong! That emote may not exist.")
        return
    else:
        emoteLinks = data["emoticons"][0]["urls"]
        # Check if any urls for the emote were returned.
        if len(emoteLinks) > 0:
            # Choosing which image size we want.
            if "2" in emoteLinks:
                final_url += emoteLinks["2"]
            elif "4" in emoteLinks:
                final_url += emoteLinks["4"]
            else:
                final_url += emoteLinks["1"]
        else:
            await ctx.reply("Something went wrong! That emote may not exist.")
            return

    # Creating a webhook in the text channel to make it appear as if the user sent the emote.
    await ctx.message.delete()
    webhook = await ctx.channel.create_webhook(name=ctx.author.name, reason="Used for emote command")
    await webhook.send(final_url, avatar_url=ctx.author.avatar_url)
    await webhook.delete()


@bot.command()
async def dog(ctx):
    """
    Command that sends a random image of a dog.

    Example usage: "(prefix) dog"
    """

    words = ctx.message.content.strip().split()

    # Make sure user did not input anything more than "(prefix) dog"
    if len(words) == 2:
        r = requests.get("https://dog.ceo/api/breeds/image/random")
        data = r.json()
        if data["status"] == "success":
            await ctx.send(data["message"])
        else:
            await ctx.reply("Getting a random image of a dog failed. There may be issues with the API.")
    else:
        await ctx.reply("I could not understand this command. You may have entered too many arguments.")


@bot.command()
async def dog_breed(ctx):
    """
    Command that sends the user a random image of a specific dog breed.

    Example usage: "(prefix) dog_breed shiba"
    """

    # First, need to check if the user actually entered a breed after the command.
    if len(ctx.message.content.strip()) == len(ctx.prefix) + len(ctx.invoked_with):
        await ctx.reply("You did not enter a breed after your message.")
    elif len(ctx.message.content) > 50:   # Don't want to search for a dog breed too long on the API.
        await ctx.reply("Sorry, the dog breed you entered is too long.")
    else:
        # Search for the breed and send link to image if found.
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
    """
    Command that sends a random image of a cat.

    Example usage: "(prefix) cat"
    """
    
    words = ctx.message.content.strip().split()

    # Make sure user did not input anything more than "(prefix) cat"
    if len(words) == 2:
        # Get a random picture of a cat and send the image.
        r = requests.get("https://api.thecatapi.com/v1/images/search")
        data = r.json()
        if "url" in data[0]:
            await ctx.send(data[0]["url"])
        else:
            await ctx.reply("Failed to get a random image of a cat")
    else:
        await ctx.reply("I could not understand this command. You may have entered too many arguments.")


@bot.command()
async def cat_breed(ctx):
    """
    Command that sends the user a random image of a specific cat breed.

    Example usage: "(prefix) cat_breed bengal"
    """
    
    # First, need to check if the user actually entered a breed after the command.
    if len(ctx.message.content.strip()) == len(ctx.prefix) + len(ctx.invoked_with):
        await ctx.reply("You did not enter a breed after your message.")
    elif len(ctx.message.content) > 50:   # Don't want to search for a cat breed too long on the api,
        await ctx.reply("Sorry, the cat breed you entered is too long.")
    else:
        # Search for the breed and get its breed_id.
        breed = ctx.message.content[len(ctx.prefix) + len(ctx.invoked_with):].strip()
        url = f"https://api.thecatapi.com/v1/breeds/search?q={breed}"
        r = requests.get(url)
        data = r.json()

        # Check if breed could be found.
        if len(data) > 0:
            # Cat breed exists, get its breed id.
            breed_id = data[0]["id"]
            new_url = f"https://api.thecatapi.com/v1/images/search?breed_id={breed_id}"
            r = requests.get(new_url)
            data = r.json()

            # Check if searching for the breed_id returned an image.
            if len(data) > 0:
                await ctx.send(data[0]["url"])
            else:
                await ctx.reply(f"Failed to get a random image of a **{breed}**. The breed **{breed}** may not be "
                                f"supported.")
        else:  # Breed could not be found.
            await ctx.reply(f"Failed to get a random image of a **{breed}**. The breed **{breed}** may not be "
                            f"supported.")


@bot.command()
async def set_birthday_channel(ctx):
    """
    Command that allow a user to set a birthday channel for the current guild.

    This channel is where birthday messages will be sent for this specific guild.
    The user must mention the desired channel.
    Example usage: "(prefix) set_birthday_channel #birthdays"
    """

    words = ctx.message.content.strip().split()

    # Check if user entered an incorrect number of inputs
    if len(words) <= 2:  # User only entered "(prefix) set_birthday_channel"
        await ctx.reply('Please mention a channel after the command.'
                        'Ex: "!buzz set_birthday_channel #birthdays"')
        return
    elif len(words) > 3:
        await ctx.reply('You entered too many inputs. Ex: "!buzz set_birthday_channel #birthdays"')
        return

    # User entered a correct number of inputs. Insert birthday into the database.
    channel_list = ctx.message.channel_mentions
    # Check if user did not properly mention a channel.
    if len(channel_list) == 0:
        await ctx.reply('It looks like you did not mention a channel. Ex: "!buzz set_birthday_channel #birthdays"')
    else:
        bday_channel = channel_list[0]
        if type(bday_channel) == discord.TextChannel:
            # Attempt to insert the birthday channel's info into the database.
            bday_channel_info = BirthdayChannelInfo(bday_channel.guild.id, bday_channel.guild.name,
                                                    bday_channel.id, bday_channel.name)
            if db.insert_birthday_channel(bday_channel_info):
                await ctx.reply(f"Set {bday_channel.mention} as this server's birthday channel")
            else:
                await ctx.reply("Something went wrong - failed to insert into the database")
        else:
            await ctx.reply("It looks like the channel you mentioned is not a text channel")



@bot.command()
async def birthday_channel(ctx):
    """
    Command that replies with the birthday channel currently set for the specific guild.

    Example usage: "(prefix) birthday_channel"
    """

    words = ctx.message.content.strip().split()

    # Check to see if user message contains more than just "(prefix) birthday_channel"
    if len(words) > 2:
        await ctx.reply('You may have entered too many arguments. Example usage: "!buzz birthday_channel"')
        return

    # Query the database to get the id of the guild's birthday channel if it can be found.
    birthday_channel_id = db.get_birthday_channel_id(ctx.guild.id)

    # Check if the guild has a birthday channel in the database.
    if birthday_channel_id != -1:
        found_channel = bot.get_channel(birthday_channel_id)
        if found_channel is not None:
            await ctx.reply(f"The birthday channel is currently set to {found_channel.mention}")
        else:  # Channel couldn't be found, was possibly deleted.
            await ctx.reply("This server does not have a birthday channel set")
    else:
        await ctx.reply("This server does not have a birthday channel set")




@bot.command()
async def remove_birthday_channel(ctx):
    """
    Command that deletes the birthday channel currently set for the specific guild.

    Example usage: "(prefix) remove_birthday_channel"
    """
    words = ctx.message.content.strip().split()

    # Check to see if user message contains more than just "(prefix) remove_birthday_channel"
    if len(words) > 2:
        await ctx.reply('You may have entered too many arguments. Example usage: "!buzz remove_birthday_channel"')
        return

    # Attempt to delete this guild's birthday channel.
    if db.delete_birthday_channel(ctx.guild.id):
        await ctx.reply("Removed this server's birthday channel")
    else:
        await ctx.reply("This server does not have a birthday channel set")



@bot.command()
async def set_birthday(ctx):
    """
    Command that allows a user to set their birthday.

    Example usage: "(prefix) set_birthday 12/31" or "(prefix) set_birthday december 31"
    """

    words = ctx.message.content.strip().split()

    # Check to see if the user entered an incorrect number of inputs to set a birthday
    if len(words) <= 2:  # User only entered "(prefix) set_birthday"
        await ctx.reply('Please enter a month and day. Ex: "!b set_birthday 5/12" or "!b set_birthday may 12"')
        return
    elif len(words) > 4:   # User entered too many arguments
        await ctx.reply('You may have entered too many arguments. Example usage:'
                        ' "!b set_birthday 5/12" or "!b set_birthday may 12""')
        return

    # User entered correct number of inputs. Check to see if they entered a valid birthday.
    month = -1
    day = -1
    if len(words) == 3:  # User entered an input such as "(prefix) set_birthday 3/14"
        month_and_day = words[2].split('/')
        if len(month_and_day) == 2:  # Correct format for the month and day using a / character.
            if month_and_day[0].isdigit() and month_and_day[1].isdigit():  # Month and day are digits.
                month = int(month_and_day[0])
                day = int(month_and_day[1])
    elif len(words) == 4:    # User entered an input such as "(prefix) set_birthday march 14"
        if words[2].lower() in months_dict and words[3].isdigit():  # User entered correct month and a digit for day.
            month = months_dict[words[2].lower()]
            day = int(words[3])

    if date_is_valid(month, day):
        # Attempt to insert the user's birthday into the database.
        user_info = UserInfo(ctx.author.id, ctx.author.name, ctx.guild.id, ctx.guild.name, month, day)
        if db.insert_birthday(user_info):
            await ctx.reply(f'Set {month}/{day} as your birthday.')
        else:
            await ctx.reply('Something went wrong - failed to insert into the database')
    else:
        await ctx.reply('You may have entered an incorrect format or an invalid date. '
                        'Example usage: "!b set_birthday 5/12" or "!b set_birthday may 12"')


def date_is_valid(month, day):
    """
    Checks to see if a given month and day make a valid date.

    :param int month:
    :param int day:
    :return: bool that represents if the date is valid
    """

    try:
        test_date = datetime(2020, int(month), int(day))
        return True
    except ValueError:
        return False


@bot.command()
async def birthday(ctx):
    """
    Command that allows a user to see what their birthday is currently set to.

    Example usage: "(prefix) birthday"
    """

    words = ctx.message.content.strip().split()

    # Check to see if user message contains more than just "(prefix) birthday"
    if len(words) > 2:
        await ctx.reply('You may have entered too many arguments. Example usage: "!buzz birthday"')
        return

    # Attempt to get the user's birthday from the database
    user_birthday = db.get_birthday(ctx.author.id, ctx.guild.id)
    if user_birthday != (-1, -1):
        await ctx.reply(f'Your birthday is currently set to {user_birthday[0]}/{user_birthday[1]}')
    else:
        await ctx.reply('Your birthday is not currently set')


@bot.command()
async def remove_birthday(ctx):
    """
    Command that allows a user to remove their birthday set for the current guild.

    Example usage: "(prefix) remove_birthday"
    """
    words = ctx.message.content.strip().split()

    # Check if user message contains more than just "(prefix) remove_birthday"
    if len(words) > 2:
        await ctx.reply('You may have entered too many arguments. Example usage: "!buzz remove_birthday"')
        return

    # Attempt to delete the user's birthday from the database
    if db.delete_birthday(ctx.author.id, ctx.guild.id):
        await ctx.reply("Successfully removed your birthday")
    else:
        await ctx.reply("You did not have a birthday set previously")


@tasks.loop(seconds=5.0)
async def check_for_birthdays():
    """
    Loop that checks for any birthdays today.

    If the day has changed (12:00 am), the function will query the database to get all users with birthdays today
    and will attempt to send birthday messages.
    """

    global saved_day
    today = datetime.today()

    # Check to see if the day has changed. If so, get all users with birthdays today and send messages.
    if today.day != saved_day:
        saved_day = today.day

        # Query the database to get all of the users that have birthdays today,
        birthdays_list = db.get_birthdays_today()
        # Attempt to send birthday messages for each user.
        for user_birthday in birthdays_list:
            user_id = user_birthday[0]
            birthday_channel_id = user_birthday[1]
            user = bot.get_user(user_id)
            channel = bot.get_channel(birthday_channel_id)

            if user is None:  # User couldn't be found, possibly deleted.
                continue
            if channel is None:  # Channel couldn't be found, possibly deleted.
                continue

            # Send birthday messages if the bot has permissions to send messages in the birthday channel.
            if channel.permissions_for(channel.guild.me).send_messages:
                await channel.send(f'Happy birthday {user.mention}!')

db.create_tables()  # create the database tables if they do not exist
check_for_birthdays.start()
bot.run(BOT_TOKEN)