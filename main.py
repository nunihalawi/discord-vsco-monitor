from urllib import response
import requests
from bs4 import BeautifulSoup
import time
import discord
import asyncio
from discord.ext import commands
import datetime
import json

bot = commands.Bot(command_prefix='$')

s = requests.Session()

with open("settings.json") as f:
    settings = json.load(f)

with open("users.json") as f:
    data = json.load(f)
    
def updatejson(user, id):
    data[user] = id
    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)

def removejson(user):
    del data[user]
    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)
        

async def executeWebhook(username, image_link, id):
    embed = discord.Embed(title=f"{username} just posted! ", color=0xDCD0FF)
    embed.add_field(name="URLs", value=f'[Post](https://vsco.co/{username}/media/{id})\n[Profile](https://vsco.co/{username}/gallery)', inline=False)
    embed.set_image(url=image_link)
    embed.set_footer(text=f"{datetime.datetime.now()}")
    channel = bot.get_channel(int(settings["monitor_channel"]))

    await channel.send(embed=embed)

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "cache-control": "max-age=0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    "sec-ch-ua": '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"'
}

async def getting_recent():
    print(f'Fetching Recent Posts | {time.time()}')
    for entry in data:
        response = s.get(
            f'https://vsco.co/{entry}/gallery',   
            headers=headers
        )

        soup = BeautifulSoup(response.text, 'html.parser')

        # get the value inside of the tag with the attribute property="og:image"
        image_url = soup.find('meta', property='og:image')['content']
        id = image_url.split('/')[-2]
        
        #checking if the most recent post ID matches the last ID that the bot fetched

        if data[entry] == "null":
            updatejson(entry, id)
            await executeWebhook(entry, image_url, id)
        else:
            if data[entry] != id:
                updatejson(entry, id)
                await executeWebhook(entry, image_url, id)
        print(f"Fetching {entry} | {time.time()}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    while True:
        await getting_recent()
        await asyncio.sleep(5)

@bot.command()
async def addprofile(ctx, arg):
    #adding profile to users.json for bot to loop through
    updatejson(arg, "null")
    await ctx.send(f'{arg} has been added to the database!')

@bot.command()
async def removeprofile(ctx, arg):
    removejson(arg)
    await ctx.send(f'{arg} has been removed from the database!')

@bot.command()
async def profiles(ctx):
    #listing all usernames in users.json
    await ctx.send('\n'.join([x for x in data]))

bot.run(settings["bot_token"])