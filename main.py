from json import load
from os import listdir
from os.path import join

from nextcord import Intents, Message
from nextcord.ext import commands


class Bot(commands.Bot):
    def __init__(self, description=None, **options) -> None:
        #self.remove_command('help') # remove default help command to add personal help command with cogs
        self.config = self.getConfig() # set bot config
        self.commands_info = self.getCommands() # set commands info

        command_prefix = commands.when_mentioned_or(self.config["PREFIX"]) # set command prefix
        intents = Intents.all() # set bot intents (all)

        super().__init__(command_prefix=command_prefix, help_command=None, intents=intents, description=description, **options)

        self.load_commands("normal") # load normal commands

    def getConfig(self) -> dict:
        """
        Get bot config
        
        Returns:
        dict: Returning config data
        """
        with open("config.json", "r") as config:
            return load(config)

    def getCommands(self) -> dict:
        """
        Get commands data
        
        Returns:
        dict: Returning commands data
        """
        with open("/data/commands.json", "r") as commands:
            return load(commands)

    def load_commands(self, command_type: str) -> None:
        """
        Load normal or slash commands
        
        Parameters:
        command_type (str) : Type of commands to load (normal/slash)
        """
        for command_categorie in listdir(f"./cogs/{command_type}"): # for each commands categorie in normal/slash commands
            for file in listdir(join(f"./cogs/{command_type}", command_categorie)): # for each file in command categorie
                # check if file is a python file
                if file.endswith(".py"):
                    extension = file[:-3]
                    try: # try to load extension/command
                        self.load_extension(f"cogs.{command_type}.{command_categorie}.{extension}")
                        print(f"Loaded command '{extension}'")
                    except Exception as e:
                        exception = f"{type(e).__name__}: {e}"
                        print(f"Failed to load command {extension}\n{exception}")

    async def on_ready(self) -> None:
        """
        The code in this even is executed when the bot is ready
        """
        print(f"Logged in as {bot.user}")
        print("-------------------")

    async def on_message(self, message: Message) -> None:
        """
        The code in this event is executed every time someone sends a message, with or without the prefix
        :param message: The message that was sent.
        """
        if message.author == bot.user or message.author.bot: return
        await bot.process_commands(message)
    
if __name__ == "__main__":
    bot = Bot() # create bot
    bot.run(bot.config["TOKEN"]) # run bot with the token in bot config
