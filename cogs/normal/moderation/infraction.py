import json

from core.infractions_manager import infractions_manager
from nextcord.ext import commands

from core.decorators import check_permissions

# Get commands.json 
with open("core/commands.json", "r") as commands_json:
    data = json.load(commands_json)
    categories = data["categories"]
    commands_ = data["commands"]

class Infraction(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.command_name = "infraction"

    @commands.command(name = "infraction",
                    usage=commands_['infraction']['usage'],
                    aliases=commands_['infraction']['aliases'],
                    description=commands_['infraction']['description']
    )
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.cooldown(1, 1, commands.BucketType.member)
    @check_permissions
    async def infraction(self, ctx:commands.Context, infraction_id:int):
        # Get infraction
        infraction = infractions_manager.getInfraction(infraction_id=infraction_id)

        # If infraction not exists
        if infraction is None:
            msg = await ctx.reply("Cette infraction n'existe pas")
            return await msg.delete(delay=3)

        # Send embed if infraction exists
        else:
            # Get infraction embed
            embed = await infraction.getSimpleEmbed(self.bot)
            await ctx.reply(embed=embed)

def setup(bot:commands.Bot):
    bot.add_cog(Infraction(bot))
