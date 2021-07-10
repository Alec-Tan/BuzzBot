# BuzzBot
![Buzz image](https://i.imgur.com/GFrJMOQ.png)

## About
BuzzBot is a personal discord bot. Currently, it can send twitch emotes from FrankerFaceZ, send birthday messages, and send images of dogs and cats.

## Emotes
With the emote command, you can search any emote available on FrankerFaceZ, and BuzzBot will delete your message and make it appear as if you sent the emote. Unfortunately, FFZ's API does not seem to support gif emotes at the moment.

![Emote example](https://i.imgur.com/VfQgUtS.png)

## Birthdays
BuzzBot also handles birthdays and sends birthday messages.

### Setting a birthday channel

This is where birthday messages will be sent in the current discord server.

![Setting birthday channel example](https://i.imgur.com/zG9nTLd.png)

### Setting your birthday
You can format your birthday in 2 ways.

![Setting birthday example 1](https://i.imgur.com/w20mTTt.png) &nbsp;&nbsp;&nbsp; ![Setting birthday example 2](https://i.imgur.com/qZP69o8.png)

### Birthday message!

![Birthday message example](https://i.imgur.com/z4GhjCj.png)

## Animal Images
BuzzBot can also send random images or specific breeds of cats and dogs.

![Random cat example](https://i.imgur.com/OGALYgf.png)

![Specific cat breed example](https://i.imgur.com/UoVxk7r.png)

## Commands
BuzzBot can use two prefixes: "!buzz" and "!b"

**!b help** - Sends a help message

**!b emote X** - Use to search for and send X emote from FrankerFaceZ. This does not support gif emotes. Example: "!b emote YEP"

**!b dog** - Sends an image of a random dog. Example: "!b dog"

**!b dog_breed X** - Sends a random image of a dog of breed X. Example: "!b dog_breed shiba"

**!b cat** - Sends an image of a random cat. Example: "!b cat"

**!b cat_breed X** - Sends a random image of a cat of breed X. Example: "!b cat_breed bengal"

**!b set_birthday_channel X** - Sets the current server's birthday channel to X. This is where birthday messages will be sent. Make sure to properly mention the channel. Example: "!b set_birthday_channel #birthdays"

**!b birthday_channel** - Sends the current birthday channel set for this server. Example: "!b birthday_channel"

**!b remove_birthday_channel** - Removes the current birthday channel set for this server. Example: "!b remove_birthday_channel"

**!b set_birthday DATE** - Sets your birthday for this server. Examples: "!b set_birthday 7/16" or "!b set_birthday july 16"

**!b birthday** - Sends your current birthday set for this server. Example: "!b birthday"

**!b remove_birthday** - Removes your birthday set for this server. Example: "!b remove_birthday"
