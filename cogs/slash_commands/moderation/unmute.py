import json
import locale
import time

import discord
from core.decorators import check_slash_permissions
from core.infractions_manager import Infraction, InfractionEmbedBuilder
from discord import Embed, Member
from discord.ext import commands
from dislash import (Option, SlashInteraction, cooldown, guild_only,
                     slash_command)

# Set local time
locale.setlocale(locale.LC_TIME,'')

class SlashUnMute(commands.Cog):
    command_name = "unmute"
    
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
    async def unmute(self, inter:SlashInteraction, membre:Member, *, raison:str=None):
        reason = raison # change var name (because of slash commands)
        member = membre # change var name

        # Check if reason is too long
        if (reason is not None) and (len(reason) > 200):
            return await inter.respond(
                embed=Embed(
                    description='La raison de l\'unmute ne peut excéder 200 caractères !',
                    color=self.bot.settings["defaultColors"]["error"]
                )
            )
        
        # Check if member is muted
        muted_role_id = self.bot.settings["moderation-muted-role"]
        muted_role = discord.utils.find(lambda r: r.id == muted_role_id, inter.guild.roles)
        if muted_role not in member.roles:
            await inter.respond(
                embed=Embed(
                    description="Ce membre n'est pas mute !",
                    color=self.bot.settings["defaultColors"]["error"]
                )
            )

            try: await inter.delete_after(delay=3) # delete interaction after 3 seconds
            except: pass
            finally: return
            
        # Unmute member
        await member.remove_roles(muted_role)

        # Create infraction
        infraction_without_id=Infraction(
            id=None,
            member_id=member.id,
            moderator_id=inter.author.id,
            action='unmute',
            timestamp=time.time(),
            reason=reason
        )

        # Add unmute to database
        infraction = self.bot.infractions_manager.addInfraction(infraction=infraction_without_id)
        
        # Send confirmation message
        await inter.respond(
            embed=Embed(
                description=f"✅ `Infraction #{infraction.id}` {member.mention} a été unmute !",
                color=self.bot.settings["defaultColors"]["confirmation"]
            )
        )
        try: await inter.delete_after(delay=2) # Delete interaction message after 2 seconds
        except: pass

        # Try to send an embed to member
        try:
            # build embed
            builder = InfractionEmbedBuilder(infraction) # define embed builder
            builder.addAction()
            builder.addReason()
            builder.setColor(self.bot.settings["defaultColors"]["cancel"])
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
        builder.addReason()
        builder.setColor(self.bot.settings["defaultColors"]["cancel"])
        builder.author = inter.author
        builder.build()
        embed = builder.embed # get embed
        await self.bot.infractions_manager.logInfraction(embed) # send embed in log channel


def setup(bot:commands.Bot):
    bot.add_cog(SlashUnMute(bot))
