import json
import locale
import time

from core.decorators import check_slash_permissions
import discord
from core.infractions_manager import Infraction, InfractionEmbedBuilder
from discord import Embed, Member
from discord.ext import commands
from dislash import (Option, SlashInteraction, cooldown, guild_only,
                     slash_command)

# Set local time
locale.setlocale(locale.LC_TIME,'')

class SlashMute(commands.Cog):
    command_name = "mute"
    
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
    async def mute(self, inter:SlashInteraction, membre:Member, *, raison:str=None):
        member = membre # change var name (because of slash commands)
        reason = raison # change var name

        # Check if reason is too long
        if (reason is not None) and (len(reason) > 200):
            await inter.respond(
                embed=Embed(
                    description='La raison ddu mute ne peut excéder 200 caractères !',
                    color=self.bot.settings["defaultColors"]["error"]
                )
            )
        
        # Check if member is muted
        muted_role_id = self.bot.settings["moderation-muted-role"]
        muted_role = discord.utils.find(lambda r: r.id == muted_role_id, inter.guild.roles)
        if muted_role in member.roles:
            await inter.respond(
                embed=Embed(
                    description="Ce membre est déjà mute !",
                    color=self.bot.settings["defaultColors"]["error"]
                )
            )
            try: await inter.delete_after(delay=3) # delete interaction after 3 seconds
            except: pass
            finally: return

        # Mute member
        await member.add_roles(muted_role)

        # Create infraction
        infraction_without_id=Infraction(
            id=None,
            member_id=member.id,
            moderator_id=inter.author.id,
            action='mute',
            timestamp=time.time(),
            reason=reason
        )

        # Add unban to database
        infraction = self.bot.infractions_manager.addInfraction(infraction=infraction_without_id)
        
        # Send confirmation message
        await inter.respond(
            embed=Embed(
                description=f"✅ `Infraction #{infraction.id}` {member.mention} a été mute !",
                color=self.bot.settings["defaultColors"]["confirmation"]
            )
        )
        try: await inter.delete_after(delay=2) # Delete interaction after 2 seconds
        except: pass

        # Send embeds
        member_infractions = self.bot.infractions_manager.getInfractions(member_id=infraction.member_id)
        count = self.bot.infractions_manager.calculInfractions(infractions=member_infractions)["mute"]
        # Try to send an embed to member
        try:
            # build embed
            builder = InfractionEmbedBuilder(infraction) # define embed builder
            builder.addAction()
            builder.addActionCount(count)
            builder.addReason()
            builder.setColor(self.bot.settings["defaultColors"]["sanction"])
            builder.author = inter.author
            builder.build()
            embed = builder.embed # get embed
            
            if member.dm_channel is None: await member.create_dm() # create dm
            await member.dm_channel.send(embed=embed) # send embed
        except: pass

        # Build embed to send in log channel
        builder = InfractionEmbedBuilder(infraction) # define embed builder
        builder.addMember(member)
        builder.addAction()
        builder.addActionCount(count)
        builder.addReason()
        builder.setColor(self.bot.settings["defaultColors"]["sanction"])
        builder.author = inter.author
        builder.build()
        embed = builder.embed # get embed
        await self.bot.infractions_manager.logInfraction(embed) # send embed in log channel

def setup(bot:commands.Bot):
    bot.add_cog(SlashMute(bot))
