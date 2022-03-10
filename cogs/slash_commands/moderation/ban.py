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

class SlashBan(commands.Cog):
    command_name = "ban"
    
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
    async def ban(self, inter:SlashInteraction, membre:User, *, raison:str=None):
        member = membre # change var name (because of slash commands)
        reason = raison # change var name

        # Check if member is banned
        try:
            await inter.guild.fetch_ban(member)
            # no error : member is already banned
            await inter.respond(
                embed=Embed(
                    description='Ce membre est déjà banni !',
                    color=self.bot.settings["defaultColors"]["error"]
                )
            )
            return # to stop command

        except:
            # member is not banned
            pass # continue command
            
        # Check if reason is too long
        if (reason is not None) and (len(reason) > 200):
            # Send warning
            await inter.respond(
                embed=Embed(
                    description='La raison du ban ne peut excéder 200 caractères !',
                    color=self.bot.settings["defaultColors"]["error"]
                )
            )
        
        else:
            # Create infraction
            infraction_without_id=Infraction(
                id=None,
                member_id=member.id,
                moderator_id=inter.author.id,
                action='ban',
                timestamp=time.time(),
                reason=reason
            )

            # Add ban to database
            infraction = self.bot.infractions_manager.addInfraction(infraction=infraction_without_id)
            
            # Send confirmation message
            await inter.respond(
                embed=Embed(
                    description=f"✅ `Infraction #{infraction.id}` {member.mention} a été ban du serveur !",
                    color=self.bot.settings["defaultColors"]["confirmation"]
                )
            )
            try: await inter.delete_after(delay=2) # Delete interaction after 2 seconds
            except: pass

            # Get action counts
            member_infractions = self.bot.infractions_manager.getInfractions(member_id=infraction.member_id)
            count = self.bot.infractions_manager.calculInfractions(infractions=member_infractions)['ban']
            # Try to send embed to member
            try:
                # Build embed
                builder = InfractionEmbedBuilder(infraction) # define embed builder
                builder.addAction()
                builder.addActionCount(count)
                builder.addReason()
                builder.setColor(self.bot.settings["defaultColors"]["sanction"])
                builder.author = inter.author
                builder.build()
                embed = builder.embed # get embed
                
                if member.dm_channel is None: await member.create_dm() # create dm
                await member.dm_channel.send(embed=embed) # send dm
            except: pass

            builder = InfractionEmbedBuilder(infraction)
            builder.addMember(member)
            builder.addAction()
            builder.addActionCount(count)
            builder.addReason()
            builder.setColor(self.bot.settings["defaultColors"]["sanction"])
            builder.author = inter.author
            builder.build()
            embed = builder.embed
            await self.bot.infractions_manager.logInfraction(embed) # send embed in log channel

            # Ban member
            await inter.guild.ban(user=member, reason=reason)

def setup(bot:commands.Bot):
    bot.add_cog(SlashBan(bot))
