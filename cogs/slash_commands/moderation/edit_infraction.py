import json

from core.decorators import check_slash_permissions
from core.infractions_manager import InfractionEmbedBuilder
from discord import Embed
from discord.ext import commands
from dislash import (ActionRow, Button, ButtonStyle, Option, SlashInteraction,
                     cooldown, guild_only, slash_command)
from dislash.interactions.message_interaction import MessageInteraction


class SlashEditInfraction(commands.Cog):
    command_name = "edit-infraction"
    
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
    async def edit_infraction(self, inter:SlashInteraction, infraction:int, *, raison:str=None):
        infraction_id = infraction # change var name (because of slash command argument name)
        infraction_reason = raison # change var name

        # Get infraction
        infraction = self.bot.infractions_manager.getInfraction(infraction_id=infraction_id)

        # If infraction not exists
        if infraction is None:
            # send warning
            await inter.respond(
                content="Cette infraction n'existe pas"
            )
            try: await inter.delete_after(delay=3) # try to delete interaction after 3 seconds
            except: pass

        # If infraction exists
        else:
            # Requiest confirmation
            ## Build embed
            builder = InfractionEmbedBuilder(infraction) # define embed builder
            builder.addMember(await self.bot.fetch_user(infraction.member_id))
            builder.addAction()
            builder.addReason()
            builder.setColor(self.bot.settings["defaultColors"]["sanction"])
            builder.author = await self.bot.fetch_user(infraction.moderator_id)
            builder.build()
            embed = builder.embed # get embed

            ## Create buttons
            ### create yes button
            yes_button = Button(
                style=ButtonStyle.green,
                label="oui",
                custom_id="edit_infraction"
            )
            
            ### create no button
            no_button = Button(
                style=ButtonStyle.red,
                label="non",
                custom_id="no_edit_infraction"
            )
           
            ## create row to stock buttons
            row = ActionRow(
                yes_button,
                no_button
            )

            ## send embed
            await inter.respond(
                content="Êtes-vous sûr de vouloir modifier cette infraction ?",
                embed = embed,
                components=[row]
            )
            confirmation_message = await inter.fetch_initial_response()

            ## add callbacks
            on_click = confirmation_message.create_click_listener(timeout=120)

            @on_click.matching_id("no_edit_infraction")
            async def on_no_edit_infra(interaction:MessageInteraction):
                """No edit infraction"""
                if interaction.author._user == inter.author._user:
                    try: await interaction.message.delete() # delete first message
                    except: pass

                    await interaction.create_response(
                        embed=Embed(
                        description=f"L'infraction `#{infraction_id}` n'a pas été modifié",
                        color=self.bot.settings["defaultColors"]["cancel"]
                        )
                    )
                    msg = await interaction.fetch_initial_response()
                    
                    try: await msg.delete(delay=3) # delete interaction after 3 seconds
                    except: pass

            @on_click.matching_id("edit_infraction")
            async def on_edit_infra(interaction:MessageInteraction):
                """Edit infraction"""
                if interaction.author._user == inter.author._user:
                    try: await interaction.message.delete() # delete first message
                    except: pass
                    infraction.reason = infraction_reason
                    self.bot.infractions_manager.editInfraction(infraction=infraction)
                    
                    await interaction.create_response(
                        embed=Embed(
                        description=f"L'infraction `#{infraction_id}` a été modifié",
                        color=self.bot.settings["defaultColors"]["confirmation"]
                        )
                    )
                    msg = await interaction.fetch_initial_response()

                    try: await msg.delete(delay=3) # delete msg after 3 seconds
                    except: pass

def setup(bot:commands.Bot):
    bot.add_cog(SlashEditInfraction(bot))
