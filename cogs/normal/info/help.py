import json

from nextcord import Embed
from nextcord.ext import commands

from core.decorators import check_permissions

class Help(commands.Cog):
    command_name = "help"
    
    # Get commands.json 
    with open("core/commands.json", "r") as commands_json:
        command_info = json.load(commands_json)["commands"][command_name]

    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.command(name = command_name,
                    usage=command_info['usage'],
                    aliases=command_info['aliases'],
                    description=command_info['description']
    )
    @commands.guild_only()
    @commands.cooldown(1, 1, commands.BucketType.member)
    @check_permissions
    async def help(self, ctx:commands.Context, command_name:str=None):
        # If general help page (commands list) is asked by user
        if command_name is None:
            # Create embed
            embed = Embed(
                title='Commandes',
                color=0xffffff
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
            await ctx.reply(embed=embed)

        # If user asked help for a specific command
        else:
            # If command requested no exist
            if command_name not in self.bot.commands_doc["commands"]:
                await ctx.reply(f"La commande `{command_name}` n'existe pas :(\nUtilisez la commande `help` pour obtenir la liste des commandes disponibles")
            # If command requested exists
            else:
                # Define command's info
                command = self.bot.commands_doc["categories"][command_name]

                # Create embed
                embed = Embed(
                    title=f"Commande {command_name}",
                    color=0xffffff
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
                for arg in command['args']: field_args_value += f"\n\> **{arg['name']}**: {arg['description']}"
                embed.add_field(
                    name='Arguments',
                    value=field_args_value,
                    inline=False
                )

                # Set embed footer
                embed.set_footer(text="<argument recquis> [argument falcultatif]")

                # Send embed
                await ctx.reply(embed=embed)


def setup(bot:commands.Bot):
    bot.add_cog(Help(bot))
