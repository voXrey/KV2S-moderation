import json

from core.decorators import check_permissions
from discord import Embed
from discord.ext import commands
from dislash import ButtonStyle, Button, ActionRow
from dislash.interactions.message_interaction import MessageInteraction
from core.infractions_manager import InfractionEmbedBuilder

class RemoveInfraction(commands.Cog):
    command_name = "remove-infraction"
    
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
    async def remove_infraction(self, ctx:commands.Context, infraction_id:int):
        # Get infraction
        infraction = self.bot.infractions_manager.getInfraction(infraction_id=infraction_id)

        # If infraction not exists
        if infraction is None:
            msg = await self.bot.replyOrSend(
                message=ctx.message,
                content="Cette infraction n'existe pas"
            )
            try: await msg.delete(delay=3) # try to delete msg after 3 seconds
            except: pass

        # If infraction exists
        else:
            # Request confirmation
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
                custom_id="remove_infraction"
            )

            ### create no button
            no_button = Button(
                style=ButtonStyle.red,
                label="non",
                custom_id="no_remove_infraction"
            )

            ## create row to stock buttons
            row = ActionRow(
                yes_button,
                no_button
            )

            ## send embed
            confirmation_message = await self.bot.replyOrSend(
                message=ctx.message,
                content="Êtes-vous sûr de vouloir supprimer cette infraction ?",
                embed = embed,
                components=[row]
            )

            ## add callbacks
            on_click = confirmation_message.create_click_listener(timeout=120) # timeout of 120 seconds

            @on_click.matching_id("no_remove_infraction")
            async def on_no_remove_infra(inter:MessageInteraction):
                """No remove infraction"""
                if inter.author._user == ctx.author._user:
                    try: await inter.message.delete() # delete first message
                    except: pass
                    msg = await self.bot.replyOrSend(
                        message=ctx.message,
                        embed=Embed(
                        description=f"L'infraction `#{infraction_id}` n'a pas été supprimée",
                        color=self.bot.settings["defaultColors"]["cancel"]
                        )
                    )
                    try: await msg.delete(delay=3) # delete msg after 3 seconds
                    except: pass

            @on_click.matching_id("remove_infraction")
            async def on_remove_infra(interaction:MessageInteraction):
                """Remove infraction"""
                if interaction.author._user == ctx.author._user:
                    try: await interaction.message.delete() # delete first message
                    except: pass
                    self.bot.infractions_manager.deleteInfraction(infraction_id=infraction_id)
                    msg = await self.bot.replyOrSend(
                        message=ctx.message,
                        embed=Embed(
                        description=f"L'infraction `#{infraction_id}` a été supprimée",
                        color=self.bot.settings["defaultColors"]["confirmation"]
                        )
                    )
                    try: await msg.delete(delay=3) # delete msg after 3 seconds
                    except: pass

            @on_click.timeout
            async def on_timeout():
                try: await confirmation_message.delete()
                except: pass

            # Delete messages
            try: await ctx.message.delete()
            except: pass


        

def setup(bot:commands.Bot):
    bot.add_cog(RemoveInfraction(bot))
