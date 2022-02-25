import json
import locale
import time

import nextcord
from core.infractions_manager import infractions_manager
from nextcord import Embed
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
        infractions_manager.warn(member_id=member.id,
                                    moderator_id=ctx.author.id,
                                    timestamp=time.time(),
                                    reason=reason)
        
        await ctx.reply('Member warned')


def setup(bot:commands.Bot):
    bot.add_cog(Warn(bot))
