import json

from discord import Embed, Member
from discord.ext import commands
from dislash import (Option, SlashInteraction, cooldown, guild_only,
                     slash_command)


class UserPerms(commands.Cog):
    command_name = "userperms"
    
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
    async def userperms(self, inter:SlashInteraction, membre:Member=None):
        # Use author if member is not given
        if membre is None: member = inter.guild.get_member(inter.author.id)
        else: member = membre # change var's name to have personal var and not name in commands.json

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
        await inter.create_response(embed=embed)

def setup(bot:commands.Bot):
    bot.add_cog(UserPerms(bot))
