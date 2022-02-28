import json
import locale
import time

from core.decorators import check_permissions
from core.infractions_manager import Infraction
from nextcord import Embed, User
from nextcord.ext import commands

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
        # Check if reason is too long
        if (reason is not None) and (len(reason) > 200):
            try:
                msg = await ctx.reply(embed=Embed(
                description='La raison du warn ne peut excéder 200 caractères !',
                color=self.bot.settings["defaultColors"]["error"]
                )
            )
            except:
                msg = await ctx.send(embed=Embed(
                description='La raison du warn ne peut excéder 200 caractères !',
                color=self.bot.settings["defaultColors"]["error"]
                )
            )
            try: await msg.delete(delay=3)
            except: pass
         
        else:
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
            try:
                confirmation_message = await ctx.reply(
                embed=Embed(
                    description=f"✅ `Infraction #{infraction.id}` {member.mention} a été warn !",
                    color=self.bot.settings["defaultColors"]["confirmation"]
                    )
                )
            except:
                confirmation_message = await ctx.send(
                embed=Embed(
                    description=f"✅ `Infraction #{infraction.id}` {member.mention} a été warn !",
                    color=self.bot.settings["defaultColors"]["confirmation"]
                    )
                )
            # Delete confirmation message
            try: await confirmation_message.delete(delay=1.5)
            except: pass

            # Try to send message to member
            try:
                embed = await self.bot.infractions_manager.createInfractionEmbed(self.bot, infraction)
                if member.dm_channel is None: await member.create_dm()
                await member.dm_channel.send(embed=embed)
            except Exception as e:
                print(e)

        # Delete command
        try: await ctx.message.delete()
        except: pass

def setup(bot:commands.Bot):
    bot.add_cog(Warn(bot))
