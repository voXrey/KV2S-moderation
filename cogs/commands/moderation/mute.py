import json
import locale
import time

from core.decorators import check_permissions
from core.infractions_manager import Infraction, InfractionEmbedBuilder
from discord import Embed, Member
from discord.ext import commands
import discord

# Set local time
locale.setlocale(locale.LC_TIME,'')

class Mute(commands.Cog):
    command_name = "mute"
    
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
    @commands.has_permissions(ban_members=True)
    @commands.cooldown(1, 1, commands.BucketType.member)
    @check_permissions
    async def mute(self, ctx:commands.Context, member:Member, *, reason:str=None):
        # Check if reason is too long
        if (reason is not None) and (len(reason) > 200):
            return await self.bot.replyOrSend(
                message=ctx.message,
                embed=Embed(
                    description='La raison ddu mute ne peut excéder 200 caractères !',
                    color=self.bot.settings["defaultColors"]["error"]
                )
            )
        
        # Check if member is muted
        muted_role_id = self.bot.settings["moderation-muted-role"]
        muted_role = discord.utils.find(lambda r: r.id == muted_role_id, ctx.guild.roles)
        if muted_role in member.roles:
            msg = await self.bot.replyOrSend(
                message=ctx.message,
                embed=Embed(
                    description="Ce membre est déjà mute !",
                    color=self.bot.settings["defaultColors"]["error"]
                )
            )
            try: await msg.delete(delay=3) # delete msg after 3 seconds
            except: pass
            finally: return

        # Mute member
        await member.add_roles(muted_role)

        # Create infraction
        infraction_without_id=Infraction(
            id=None,
            member_id=member.id,
            moderator_id=ctx.author.id,
            action='mute',
            timestamp=time.time(),
            reason=reason
        )

        # Add unban to database
        infraction = self.bot.infractions_manager.addInfraction(infraction=infraction_without_id)
        
        # Send confirmation message
        confirmation_message = await self.bot.replyOrSend(
            message=ctx.message,
            embed=Embed(
                description=f"✅ `Infraction #{infraction.id}` {member.mention} a été mute !",
                color=self.bot.settings["defaultColors"]["confirmation"]
            )
        )
        try: await confirmation_message.delete(delay=2) # Delete confirmation message after 2 seconds
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
            builder.author = ctx.author
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
        builder.author = ctx.author
        builder.build()
        embed = builder.embed # get embed
        await self.bot.infractions_manager.logInfraction(embed) # send embed in log channel

        # Delete command
        await ctx.message.delete()

def setup(bot:commands.Bot):
    bot.add_cog(Mute(bot))
