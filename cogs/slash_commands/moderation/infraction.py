import json

from core.decorators import check_slash_permissions
from core.infractions_manager import InfractionEmbedBuilder
from discord import Embed
from discord.ext import commands
from dislash import (Option, SlashInteraction, cooldown, guild_only,
                     slash_command)


class SlashInfraction(commands.Cog):
    command_name = "infraction"

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
    async def infraction(self, inter:SlashInteraction, infraction:int):
        infraction_id = infraction # change var name (because of slash command argument)

        # Get infraction
        infraction = self.bot.infractions_manager.getInfraction(infraction_id=infraction_id)

        # If infraction not exists
        if infraction is None:
            await inter.create_response(embed=Embed(
                description="Cette infraction n'existe pas",
                color=self.bot.settings["defaultColors"]["error"]
            ))
            msg = await inter.fetch_initial_response()
            try: await msg.delete(delay=3)
            except: pass

        # Send embed if infraction exists
        else:
            # Get infraction embed
            builder = InfractionEmbedBuilder(infraction) # define embed builder
            builder.addMember(await self.bot.fetch_user(infraction.member_id))
            builder.addAction()
            builder.addReason()
            builder.setColor(self.bot.settings["defaultColors"]["sanction"])
            builder.author = await self.bot.fetch_user(infraction.moderator_id)
            builder.build()
            embed = builder.embed # get embed
            
            await inter.create_response(embed=embed)

def setup(bot:commands.Bot):
    bot.add_cog(SlashInfraction(bot))
