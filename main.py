import os
import nextcord
from nextcord.ext import commands
import json

# Get config.json
with open("config.json", "r") as config:
    data = json.load(config)
    # Set token and prefix
    TOKEN = data["TOKEN"]
    PREFIX = data["PREFIX"]


intents = nextcord.Intents.all()
client = commands.Bot(
    intents=intents,
    command_prefix=commands.when_mentioned_or(PREFIX)
    )

@client.event
async def on_ready():
    """
    The code in this even is executed when the bot is ready
    """
    print(f"Logged in as {client.user}")
    print("-------------------")

def load_commands(command_type: str) -> None:
    for file in os.listdir(f"./cogs/{command_type}"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                client.load_extension(f"cogs.{command_type}.{extension}")
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
    #load_commands("normal")

@client.event
async def on_message(message: nextcord.Message) -> None:
    """
    The code in this event is executed every time someone sends a message, with or without the prefix
    :param message: The message that was sent.
    """
    if message.author == client.user or message.author.bot: return
    await client.process_commands(message)

client.run(TOKEN)