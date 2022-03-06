import json

from core.decorators import check_permissions
from discord import Embed, Member
from discord.ext import commands

class UserPerms(commands.Cog):
    command_name = "userperms"
    
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
    async def userperms(self, ctx:commands.Context, member:Member=None):
        # If member is not given use author
        if member is None: member = ctx.author
        
        # Create list of member's permissions
        permissions_info = self.bot.getJsonData('core/perms_info.json') # get permissions info
        member_permissions = [permission[0] for permission in member.guild_permissions if permission[1]] # get member permissions
        permissions = [permissions_info['traductions'][permission] for permission in member_permissions] # traduce permissions to french

        if 'administrator' in member_permissions: permissions_string = permissions_info['traductions']['administrator'] # resume permissions for administrators
        else: permissions_string = '\n'.join(permissions) # create str

        # Create embed
        embed = Embed(
            description=permissions_string,
            color=self.bot.settings["defaultColors"]["userinfo"]
        )

        # Set author (member)
        embed.set_author(
            name=member,
            icon_url=member.avatar_url
        )

        # Send embed
        await self.bot.replyOrSend(
            message=ctx.message,
            embed=embed
        )

def setup(bot:commands.Bot):
    bot.add_cog(UserPerms(bot))
