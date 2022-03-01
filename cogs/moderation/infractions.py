import json

import nextcord
from core.decorators import check_permissions
from nextcord.ext import commands

class Infractions(commands.Cog):
    command_name = "infractions"
    
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
    async def infractions(self, ctx:commands.Context, member:nextcord.User=None):
        # use author as member if member is not given
        if member is None: member = ctx.author
        
        # Get infractions
        infractions = self.bot.infractions_manager.getInfractions(member_id=member.id)

        # Create infractions pages
        embeds = await self.bot.infractions_manager.createEmbedsWithInfractions(member_id=member.id, infractions=infractions, bot=self.bot)

        # Send embeds
        await self.bot.replyOrSend(
                message=ctx.message,
                embeds=embeds
        )

def setup(bot:commands.Bot):
    bot.add_cog(Infractions(bot))
