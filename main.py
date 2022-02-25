import os
import nextcord
from nextcord.ext import commands
import json
from os.path import join

# Get config.json
with open("config.json", "r") as config:
    data = json.load(config)
    # Set token and prefix
    TOKEN = data["TOKEN"]
    PREFIX = data["PREFIX"]


intents = nextcord.Intents.all()
bot = commands.Bot(
    intents=intents,
    command_prefix=commands.when_mentioned_or(PREFIX)
    )

@bot.event
async def on_ready():
    """
    The code in this even is executed when the bot is ready
    """
    print(f"Logged in as {bot.user}")
    print("-------------------")

# Remove default help command to create personnal help command
bot.remove_command('help')

def load_commands(command_type: str) -> None:
    for command_categorie in os.listdir(f"./cogs/{command_type}"):
        for file in os.listdir(join(f"./cogs/{command_type}", command_categorie)):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    bot.load_extension(f"cogs.{command_type}.{command_categorie}.{extension}")
                    print(f"Loaded extension '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    print(f"Failed to load extension {extension}\n{exception}")

if __name__ == "__main__":
    """
    This will automatically load slash commands and normal commands located in their respective folder.
    
    If you want to remove slash commands, which is not recommended due to the Message Intent being a privileged intent, you can remove the loading of slash commands below.
    """
    #load_commands("slash")
    load_commands("normal")

@bot.event
async def on_message(message: nextcord.Message) -> None:
    """
    The code in this event is executed every time someone sends a message, with or without the prefix
    :param message: The message that was sent.
    """
    if message.author == bot.user or message.author.bot: return
    await bot.process_commands(message)

bot.run(TOKEN)