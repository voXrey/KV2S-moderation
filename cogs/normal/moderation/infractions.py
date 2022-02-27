import json

import nextcord
from core.decorators import check_permissions
from core.infractions_manager import infractions_manager
from nextcord.ext import commands

# Get commands.json 
with open("core/commands.json", "r") as commands_json:
    data = json.load(commands_json)
    categories = data["categories"]
    commands_ = data["commands"]

class Infractions(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.command_name = "infractions"

    @commands.command(name = "infractions",
                    usage=commands_['infractions']['usage'],
                    aliases=commands_['infractions']['aliases'],
                    description=commands_['infractions']['description']
    )
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.cooldown(1, 1, commands.BucketType.member)
    @check_permissions
    async def infractions(self, ctx:commands.Context, member:nextcord.User):
        # Get infractions
        infractions = infractions_manager.getInfractions(member_id=member.id)

        # Create infractions pages
        embeds = await infractions_manager.createEmbedsWithInfractions(member_id=member.id, infractions=infractions, bot=self.bot)

        # Send embeds
        for embed in embeds:
            await ctx.reply(embed=embed)

def setup(bot:commands.Bot):
    bot.add_cog(Infractions(bot))
