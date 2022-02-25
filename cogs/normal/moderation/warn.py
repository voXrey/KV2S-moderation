import json
import locale
import time

import nextcord
from core.infractions_manager import infractions_manager
from nextcord.ext import commands

# Set local time
locale.setlocale(locale.LC_TIME,'')


# Get commands.json 
with open("core/commands.json", "r") as commands_json:
    data = json.load(commands_json)
    categories = data["categories"]
    commands_ = data["commands"]

class Warn(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.command(name = "warn",
                    usage=commands_['warn']['usage'],
                    aliases=commands_['warn']['aliases'],
                    description=commands_['warn']['description']
    )
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.cooldown(1, 1, commands.BucketType.member)
    async def warn(self, ctx:commands.Context, member:nextcord.Member, *, reason:str=None):
        # Add warn to database
        infraction_id = infractions_manager.warn(member_id=member.id,
                                    moderator_id=ctx.author.id,
                                    timestamp=time.time(),
                                    reason=reason)
        
        # Send confirmation message
        confirmation_message = await ctx.reply(f"✅ `Infraction {infraction_id}` {member.mention} a été warn !")
        # Delete confirmation message
        await confirmation_message.delete(delay=0.5)
        
        # Try to send message to member
        try:
            infraction = infractions_manager.getInfraction(infraction_id=infraction_id)
            embed = await infraction.getEmbed(self.bot)
            if member.dm_channel is None:
                await member.create_dm()
            await member.dm_channel.send(embed=embed)

        except Exception as e:
            print(e)

def setup(bot:commands.Bot):
    bot.add_cog(Warn(bot))
