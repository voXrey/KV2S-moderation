import json
from os import listdir

from discord import Embed, Intents, Message
from discord.ext import commands
from dislash import  InteractionClient, Component
from core.infractions_manager import InfractionsManager


class Bot(commands.Bot):
    def __init__(self, description=None, **options):
        self.config = self.getConfig() # set bot config
        self.settings = self.getSettings() # set bot settings
        self.commands_doc = self.getCommands() # set commands doc

        self.infractions_manager = InfractionsManager(bot=self) # set infraction manager

        self.prefix = self.config["PREFIX"]
        command_prefix = commands.when_mentioned_or(self.prefix) # set command prefix
        intents = Intents.all() # set bot intents (all)

        super().__init__(command_prefix=command_prefix, help_command=None, intents=intents, description=description, **options) # init commands.Bot
        
        self.load_commands("commands") # load commands
        self.load_commands("slash_commands") # load slash commands
        self.load_tasks() # load tasks
        
        self.inter_client = InteractionClient(self) # create inter client to use dislash features


    async def replyOrSend(self, message:Message, content:str=None, embed:Embed=None, components:list[Component]=None):
        """
        Try to reply to message, if an error is occured, try to send a message in the message's channels
        
        Parameters:
        message (Message): message to reply
        content (str): message content to send
        action_row (ActionRow): message's action row
        
        Returns:
        Message: message sent
        """
        msg = None
        try: # try to reply
            msg = await message.reply(
                content=content,
                embed=embed,
                components=components
            )
        except: # if reply didn't worked
            try: # try to send message in the message's channel
                msg = await message.channel.send(
                    content=content,
                    embed=embed,
                    components=components
                )
            except Exception as e: print(e)
        return msg

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

    def load_commands(self, command_type:str) -> None:
        """
        Load normal or slash commands
        """
        if command_type in ["commands", "slash_commands"]:
            for command_categorie in listdir(f"./cogs/{command_type}"): # for each commands categorie
                for file in listdir(f"./cogs/{command_type}/{command_categorie}"): # for each file in command categorie
                    # check if file is a python file
                    if file.endswith(".py"):
                        extension = file[:-3]
                        try: # try to load extension/command
                            self.load_extension(f"cogs.{command_type}.{command_categorie}.{extension}")
                            print(f"Loaded {command_type} '{extension}'")
                        except Exception as e:
                            exception = f"{type(e).__name__}: {e}"
                            print(f"Failed to load {command_type} {extension}\n{exception}")
    
    def load_tasks(self) -> None:
        """
        Load tasks
        """
        for file in listdir(f"./cogs/tasks"): # for each file in tasks folder
            # check if file is a python file
            if file.endswith(".py"):
                extension = file[:-3]
                try: # try to load extension/tasks
                    self.load_extension(f"cogs.tasks.{extension}")
                    print(f"Loaded tasks '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    print(f"Failed to load tasks {extension}\n{exception}")

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
        if message.author == self.user or message.author.bot: return
        await self.process_commands(message)
 

if __name__ == "__main__":
    bot = Bot() # create bot

    bot.run(bot.config["TOKEN"]) # run bot with the token in bot config
