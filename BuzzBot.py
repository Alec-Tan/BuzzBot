import discord
import requests
from discord.ext import commands, tasks

bot = commands.Bot(command_prefix=['!buzz ', '!b '])
bot.remove_command('help')  # have to remove so that I can put my own help command


@bot.event
async def on_ready():
    print('Ready!')


@bot.command()
async def help(ctx):
    helpMsg = f'BuzzBot can use two prefixes: "!buzz" and "!b" \n**!buzz help** - Sends this help message \n**!buzz ' \
              f'emote (emote)** - Use to search for and send an emote from FrankerFaceZ. Example: "!buzz emote YEP"' \
              f' \n**!buzz dog** - Sends an image of a random dog \n**!buzz dog (breed)** - Sends a random image of a' \
              f' specific dog breed . Example: "!buzz dog shiba" \n**!buzz cat** - Sends an image of a random cat' \
              f' \n**!buzz cat (breed)** - Sends a random image of a specific cat breed. Example: "!buzz cat bengal"'
    await ctx.send(helpMsg)


@bot.command()
async def emote(ctx):
    desiredEmote = ctx.message.content[len(ctx.prefix) + len(ctx.invoked_with):].strip()
    url = f"https://api.frankerfacez.com/v1/emotes?q={desiredEmote}&sensitive=false&sort=count-desc" \
          f"&high_dpi=off&page=1&per_page=50"
    r = requests.get(url)
    data = r.json()

    finalURL = "https:"
    if len(data["emoticons"]) == 0:
        await ctx.reply("Something went wrong! That emote may not exist.")
        return
    else:
        emoteLinks = data["emoticons"][0]["urls"]
        if len(emoteLinks) > 0:
            if "2" in emoteLinks:
                finalURL += emoteLinks["2"]
            elif "4" in emoteLinks:
                finalURL += emoteLinks["4"]
            else:
                finalURL += emoteLinks["1"]
            #await ctx.send(finalURL)
        else:
            await ctx.reply("Something went wrong! That emote may not exist.")
            return

    # creating a webhook in the text channel to make it appear as if the user sent the emote
    await ctx.message.delete()
    webhook = await ctx.channel.create_webhook(name=ctx.author.name, reason="Used for emote command")
    await webhook.send(finalURL, avatar_url=ctx.author.avatar_url)
    await webhook.delete()


@bot.command()
async def dog(ctx):
    words = ctx.message.content.strip().split()

    # checking if command wants a random dog or a specific breed
    if len(words) == 2: # user wants random dog
        r = requests.get("https://dog.ceo/api/breeds/image/random")
        data = r.json()
        if data["status"] == "success":
            await ctx.send(data["message"])
        else:   # api failed to get a random image
            await ctx.reply("Getting a random image of a dog failed. There may be issues with the API.")
    elif len(words) == 3:   # user wants a specific breed of dog
        breed = words[2]
        url = f"https://dog.ceo/api/breed/{breed}/images/random"
        r = requests.get(url)
        data = r.json()
        if data["status"] == "success":
            await ctx.send(data["message"])
        else:
            await ctx.reply(f"Getting a random image of a **{breed}** failed. The breed **{breed}** may not be "
                            f"supported.")
    else:   # user inputted too many arguments
        await ctx.reply("I could not understand this command. You may have entered too many arguments.")


@bot.command()
async def cat(ctx):
    words = ctx.message.content.strip().split()

    # checking if command wants a random cat or a specific breed
    if len(words) == 2: # user wants a random cat
        r = requests.get("https://api.thecatapi.com/v1/images/search")
        data = r.json()
        if "url" in data[0]:
            await ctx.send(data[0]["url"])
        else:   # failed to get a random image
            await ctx.reply("Failed to get a random image of a cat")
    elif len(words) == 3:   # user wants a specific breed
        # searching for the breed and getting its breed_id
        breed = words[2]
        url = f"https://api.thecatapi.com/v1/breeds/search?q={breed}"
        r = requests.get(url)
        data = r.json()

        # checking if breed could be found
        if len(data) > 0:   # breed exists, get an image of it
            breed_id = data[0]["id"]
            new_url = f"https://api.thecatapi.com/v1/images/search?breed_id={breed_id}"
            r = requests.get(new_url)
            data = r.json()

            # checking if searching for the breed_id returned an image
            if len(data) > 0:   # call returned information about the breed
                await ctx.send(data[0]["url"])
            else:   # call did not return info about the breed
                await ctx.reply(f"Failed to get a random image of a **{breed}**. The breed **{breed}** may not be "
                                f"supported.")
        else:   # breed could not be found
            await ctx.reply(f"Failed to get a random image of a **{breed}**. The breed **{breed}** may not be "
                            f"supported.")
    else: # user inputted too many arguments
        await ctx.reply("I could not understand this command. You may have entered too many arguments.")


bot.run('BOT TOKEN HERE')
