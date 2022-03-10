import json
import locale
import time

import discord

from core.decorators import check_permissions
from core.infractions_manager import Infraction, InfractionEmbedBuilder
from discord import Embed, User
from discord.ext import commands

# Set local time
locale.setlocale(locale.LC_TIME,'')

class Warn(commands.Cog):
    command_name = "warn"
    
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
    @commands.has_permissions(kick_members=True)
    @commands.cooldown(1, 1, commands.BucketType.member)
    @check_permissions
    async def warn(self, ctx:commands.Context, member:User, *, reason:str=None):
        member_ = await ctx.guild.fetch_member(member.id)
        # check if member is banned
        try:
            await ctx.guild.fetch_ban(member_)
            # no error : is banned

            await self.bot.replyOrSend(
                message=ctx.message,
                embed=Embed(
                    description='un membre banni ne peut pas être warn !',
                    color=self.bot.settings["defaultColors"]["error"]
                )
            )
            return # stop command
        except:
            # error : is not banned
            # continue command
            pass

        # check if member is muted
        muted_role_id = self.bot.settings["moderation-muted-role"]
        muted_role = discord.utils.find(lambda r: r.id == muted_role_id, ctx.guild.roles)
        if muted_role in member_.roles:
            await self.bot.replyOrSend(
                message=ctx.message,
                embed=Embed(
                    description='un membre mute ne peut pas être warn !',
                    color=self.bot.settings["defaultColors"]["error"]
                )
            )
            return # stop command

        # Check if reason is too long
        if (reason is not None) and (len(reason) > 200):
            # send warning
            await self.bot.replyOrSend(
                message=ctx.message,
                embed=Embed(
                    description='La raison du warn ne peut excéder 200 caractères !',
                    color=self.bot.settings["defaultColors"]["error"]
                )
            )
        
        else: # reason is good
            # Create infraction
            infraction_without_id=Infraction(
                id=None,
                member_id=member.id,
                moderator_id=ctx.author.id,
                action='warn',
                timestamp=time.time(),
                reason=reason
            )

            # Add warn to database
            infraction = self.bot.infractions_manager.addInfraction(infraction=infraction_without_id)
            
            # Send confirmation message
            confirmation_message = await self.bot.replyOrSend(
                message=ctx.message,
                embed=Embed(
                    description=f"✅ `Infraction #{infraction.id}` {member.mention} a été warn !",
                    color=self.bot.settings["defaultColors"]["confirmation"]
                )
            )
            try: await confirmation_message.delete(delay=2) # delete confirmation message after 2 seconds
            except: pass

            # Get warn count
            member_infractions = self.bot.infractions_manager.getInfractions(member_id=infraction.member_id)
            count = self.bot.infractions_manager.calculInfractions(infractions=member_infractions)['warn']
            # Try to send an embed to member
            try:
                # build embed
                builder = InfractionEmbedBuilder(infraction) # define embed builder
                builder.addAction()
                builder.addActionCount(count)
                builder.addReason()
                builder.addWarning(self.bot.settings['automoderation']['warns-for-sanction'])
                builder.setColor(self.bot.settings["defaultColors"]["sanction"])
                builder.author = ctx.author
                builder.build()
                embed = builder.embed # get embed
                
                if member.dm_channel is None: await member.create_dm() # create dm
                await member.dm_channel.send(embed=embed) # send embed
            except: pass

            # Build embed to log infraction
            builder = InfractionEmbedBuilder(infraction) # define embed builder
            builder.addMember(member)
            builder.addAction()
            builder.addActionCount(count)
            builder.addReason()
            builder.setColor(self.bot.settings["defaultColors"]["sanction"])
            builder.author = ctx.author
            builder.build()
            embed = builder.embed # get embed
            await self.bot.infractions_manager.logInfraction(embed) # send embed in log channel

        # check if member must be banned/muted
        await self.bot.infractions_manager.checkWarnsForSanction(member.id)
        
        # Try to delete command
        try: await ctx.message.delete()
        except: pass

def setup(bot:commands.Bot):
    bot.add_cog(Warn(bot))
