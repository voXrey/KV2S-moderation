import json
import locale
import time

from core.decorators import check_slash_permissions
from core.infractions_manager import Infraction, InfractionEmbedBuilder
from discord import Embed, User
from discord.ext import commands
from dislash import (Option, SlashInteraction, cooldown, guild_only,
                     slash_command)

# Set local time
locale.setlocale(locale.LC_TIME,'')

class SlashUnBan(commands.Cog):
    command_name = "unban"
    
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
    @check_slash_permissions
    async def unban(self, inter:SlashInteraction, membre:User, *, raison:str=None):
        member = membre # change var name (because of slash commands)
        reason = raison # change var name
        
        # Check if member is banned with a try
        try:
            await inter.guild.fetch_ban(member)
            # member is banned (no error)
            
            # Check if reason is too long
            if (reason is not None) and (len(reason) > 200):
                await inter.respond(
                    embed=Embed(
                        description='La raison de l\'unban ne peut excéder 200 caractères !',
                        color=self.bot.settings["defaultColors"]["error"]
                    )
                )

            else: # reason is good
                # Unban user
                await inter.guild.unban(member)

                # Create infraction
                infraction_without_id=Infraction(
                    id=None,
                    member_id=member.id,
                    moderator_id=inter.author.id,
                    action='unban',
                    timestamp=time.time(),
                    reason=reason
                )

                # Add unban to database
                infraction = self.bot.infractions_manager.addInfraction(infraction=infraction_without_id)
                
                # Send confirmation message
                await inter.respond(
                    embed=Embed(
                        description=f"✅ `Infraction #{infraction.id}` {member.mention} a été unban du serveur !",
                        color=self.bot.settings["defaultColors"]["confirmation"]
                    )
                )
                try: await inter.delete_after(delay=2) # Delete interaction message after 2 seconds
                except: pass

                # Build embed to send in log channel
                builder = InfractionEmbedBuilder(infraction) # define embed builder
                builder.addMember(member)
                builder.addAction()
                builder.addReason()
                builder.setColor(self.bot.settings["defaultColors"]["cancel"])
                builder.author = inter.author
                builder.build()
                embed = builder.embed # get embed
                await self.bot.infractions_manager.logInfraction(embed) # send embed in log channel

        except:
            # member is not banned
            await inter.respond(
                embed=Embed(
                    description='Cet utilisateur n\'est pas banni du serveur !',
                    color=self.bot.settings["defaultColors"]["error"]
                )
            )
            try: await inter.delete_after(delay=3) # delete interaction after 3 seconds
            except: pass

def setup(bot:commands.Bot):
    bot.add_cog(SlashUnBan(bot))
