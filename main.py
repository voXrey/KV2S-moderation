from json import load
import json
from os import listdir
from os.path import join

from nextcord import Intents, Message
from nextcord.ext import commands

from core.infractions_manager import InfractionsManager


class Bot(commands.Bot):
    def __init__(self, description=None, **options):
        #self.remove_command('help') # remove default help command to add personal help command with cogs
        self.config = self.getConfig() # set bot config
        self.settings = self.getSettings() # set bot settings
        self.commands_doc = self.getCommands() # set commands doc
        self.infractions_manager = InfractionsManager(bot=self) # set infraction manager

        self.prefix = self.config["PREFIX"]
        command_prefix = commands.when_mentioned_or(self.prefix) # set command prefix
        intents = Intents.all() # set bot intents (all)

        super().__init__(command_prefix=command_prefix, help_command=None, intents=intents, description=description, **options) # init commands.Bot

        self.load_commands() # load commands

    def getJsonData(self, filepath:str) -> dict:
        """
        Get json file data
        
        Parameters:
        filepath (str): file's path
        
        Returns:
        dict: file's data
        """
        with open(filepath, "r", encoding='utf-8') as file:
            return json.load(file)

    def getConfig(self) -> dict:
        """
        Get bot config
        
        Returns:
        dict: Returning config data
        """
        with open("config.json", "r", encoding='utf-8') as config:
            return json.load(config)

    def getCommands(self) -> dict:
        """
        Get commands data
        
        Returns:
        dict: Returning commands data
        """
        with open("core/commands.json", "r", encoding='utf-8') as commands:
            return json.load(commands)

    def getSettings(self) -> dict:
        """
        Get settings data
        
        Returns:
        dict: Returning settings data
        """
        with open("data/settings.json", "r", encoding='utf-8') as settings:
            return json.load(settings)
    
    def setSetting(self, setting:str, subsetting:str=None, new_data=None) -> None:
        """
        Set new value to a setting
        
        Parameters:
        setting (str) : setting to change value
        subseeting (str) : subsetting (setting in settings list) to change value
        new_data (any) : new value of setting
        """
        data = self.getSettings()
        with open("data/settings.json", "w", encoding='utf-8') as settings:
            if subsetting is not None: data[setting][subsetting] = new_data
            else: data[setting] = new_data
            json.dump(data, settings, indent=4)

    def load_commands(self) -> None:
        """
        Load normal or slash commands
        """
        for command_categorie in listdir(f"./cogs"): # for each commands categorie
            for file in listdir(f"./cogs/{command_categorie}"): # for each file in command categorie
                # check if file is a python file
                if file.endswith(".py"):
                    extension = file[:-3]
                    try: # try to load extension/command
                        self.load_extension(f"cogs.{command_categorie}.{extension}")
                        print(f"Loaded command '{extension}'")
                    except Exception as e:
                        exception = f"{type(e).__name__}: {e}"
                        print(f"Failed to load command {extension}\n{exception}")

    async def on_ready(self) -> None:
        """
        The code in this even is executed when the bot is ready
        """
        # get mychannels
        self.mychannels = {}
        for channel_name,channel_id in self.settings['channels'].items():
            if channel_id is not None: self.mychannels[channel_name] = await self.fetch_channel(channel_id)

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
