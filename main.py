import os

import discord
from discord.ext import commands

import config 

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("%"),
    owner_ids=config.OWNER_IDS,
    intents=discord.Intents(
        guilds=True, members=True, voice_states=True,
        messages=True, reactions=True, emojis=True
    )
)

# bot variables
bot.OK_EMOJI = "sadcatthumbsup:758224306362253323"

initial_extensions = (
    'jishaku',
    'cogs.classcord',
)

for exntension in initial_extensions:
    bot.load_extension(exntension)

@bot.event
async def on_ready():
    print(f"{bot.user.name}: Online")

bot.run(config.TOKEN)
