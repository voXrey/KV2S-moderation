import json

from discord import Embed
from discord.ext import commands
from dislash import (Option, SlashInteraction, cooldown, guild_only,
                     slash_command)


class SlashHelp(commands.Cog):
    command_name = "help"
    
    # Get commands.json 
    with open("core/commands.json", "r") as commands_json:
        command_info = json.load(commands_json)["commands"][command_name]

    options = []
    for arg in command_info["args"]:
        options.append(Option(
            name=arg["name"],
            description=arg["description"],
            type=arg["type"],
            required=arg["required"]
        ))

    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @slash_command(name=command_info['usage'],
                    description=command_info['description'],
                    options=options,
                    guild_ids=[914554436926447636] # TODO: Delete guild_ids
    )
    @guild_only()
    @cooldown(1, 1, commands.BucketType.member)
    async def help(self, inter:SlashInteraction, commande:str=None):
        # If general help page (commands list) is asked by user
        if commande is None:
            # Create embed
            embed = Embed(
                title='Commandes',
                color=self.bot.settings["defaultColors"]["neutral"]
            )

            # Set fields (1 field by categorie)
            for categorie, categorie_info in self.bot.commands_doc["categories"].items():
                # get commands of the current categorie
                categorie_commands = []
                for command,command_info in self.bot.commands_doc["commands"].items():
                    if command_info['categorie']==categorie: categorie_commands.append(command_info)
                if len(categorie_commands) == 0: continue # no display categorie if havn't command

                value = " ".join([f"`{command_info['usage']}`" for command_info in categorie_commands]) # prepare field's value
                embed.add_field(name=categorie_info["name"], value=value, inline=False) # add field to embed

            # Send embed
            await inter.create_response(embed=embed)

        # If user asked help for a specific command
        else:
            # If command requested no exist
            if commande not in self.bot.commands_doc["commands"]:
                await inter.respond(content=f"La commande `{commande}` n'existe pas :(\nUtilisez la commande `help` pour obtenir la liste des commandes disponibles")
            # If command requested exists
            else:
                # Define command's info
                command = self.bot.commands_doc["commands"][commande]

                # Create embed
                embed = Embed(
                    title=f"Commande {commande}",
                    color=self.bot.settings["defaultColors"]["neutral"]
                )

                # Set args string
                args = []
                for arg in command['args']:
                    if arg['required']: args.append(f"<{arg['name']}>")
                    else: args.append(f"[{arg['name']}]")
                args_string = ' '.join(args)
                # Create embed's field for command's usage
                field_usage_value = f"> `{command['usage']} {args_string}`"
                embed.add_field(
                    name='Utilisation',
                    value=field_usage_value,
                    inline=False
                )

                # Create embed's field for command's arguments info
                field_args_value = ""
                for arg in command['args']: field_args_value += f"\n> **{arg['name']}**: {arg['description']}"
                embed.add_field(
                    name='Arguments',
                    value=field_args_value,
                    inline=False
                )

                # Set embed footer
                embed.set_footer(text="<argument requis> [argument falcultatif]")

                # Send embed
                await inter.create_response(embed=embed)


def setup(bot:commands.Bot):
    bot.add_cog(SlashHelp(bot))
