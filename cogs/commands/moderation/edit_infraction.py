import json

from core.decorators import check_permissions
from core.infractions_manager import InfractionEmbedBuilder
from discord import Embed
from discord.ext import commands
from dislash import Button, ButtonStyle, ActionRow
from dislash.interactions.message_interaction import MessageInteraction

class EditInfraction(commands.Cog):
    command_name = "edit-infraction"
    
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
    async def edit_infraction(self, ctx:commands.Context, infraction_id:int, *, infraction_reason:str=None):
        # Get infraction
        infraction = self.bot.infractions_manager.getInfraction(infraction_id=infraction_id)

        # If infraction not exists
        if infraction is None:
            # send warning
            msg = await self.bot.replyorSend(
                message=ctx.message,
                content="Cette infraction n'existe pas"
            )
            try: await msg.delete(delay=3) # try to send warning after 3 seconds
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
            confirmation_message = await self.bot.replyOrSend(
                message=ctx.message,
                content="Êtes-vous sûr de vouloir modifier cette infraction ?",
                embed = embed,
                components=[row]
            )

            ## add callbacks
            on_click = confirmation_message.create_click_listener(timeout=120)

            @on_click.matching_id("no_edit_infraction")
            async def on_no_edit_infra(interaction:MessageInteraction):
                """No edit infraction"""
                if interaction.author._user == ctx.author._user:
                    try: await interaction.message.delete() # delete first message
                    except: pass
                    msg = await self.bot.replyOrSend(
                        message=ctx.message,
                        embed=Embed(
                        description=f"L'infraction `#{infraction_id}` n'a pas été modifié",
                        color=self.bot.settings["defaultColors"]["cancel"]
                        )
                    )
                    try: await msg.delete(delay=3) # delete msg after 3 seconds
                    except: pass

            @on_click.matching_id("edit_infraction")
            async def on_edit_infra(interaction:MessageInteraction):
                """Edit infraction"""
                if interaction.author._user == ctx.author._user:
                    try: await interaction.message.delete() # delete first message
                    except: pass
                    infraction.reason = infraction_reason
                    self.bot.infractions_manager.editInfraction(infraction=infraction)
                    msg = await self.bot.replyOrSend(
                        message=ctx.message,
                        embed=Embed(
                        description=f"L'infraction `#{infraction_id}` a été modifié",
                        color=self.bot.settings["defaultColors"]["confirmation"]
                        )
                    )
                    try: await msg.delete(delay=3) # delete msg after 3 seconds
                    except: pass

            # Delete messages
            try: await ctx.message.delete() # delete command
            except: pass


        

def setup(bot:commands.Bot):
    bot.add_cog(EditInfraction(bot))
