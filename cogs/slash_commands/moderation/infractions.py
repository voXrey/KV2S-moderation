import json

from core.decorators import check_slash_permissions
import discord
from discord.ext import commands
from dislash import (Option, SlashInteraction, cooldown, guild_only,
                     slash_command)


class SlashInfractions(commands.Cog):
    command_name = "infractions"
    
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
    @check_slash_permissions
    async def infractions(self, inter:SlashInteraction, membre:discord.User=None):
        member = membre # change var name (because of slash commands)

        # use author as member if member is not given
        if member is None: member = inter.author
        
        # Get infractions
        infractions = self.bot.infractions_manager.getInfractions(member_id=member.id)

        # Create infractions pages
        embeds = await self.bot.infractions_manager.createEmbedsWithInfractions(member_id=member.id, infractions=infractions, bot=self.bot)

        # Send embeds
        await inter.respond(
            embeds=embeds
        )

def setup(bot:commands.Bot):
    bot.add_cog(SlashInfractions(bot))
