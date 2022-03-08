import json

from core.decorators import check_slash_permissions
from discord import Embed, Member
from discord.ext import commands
from dislash import (ActionRow, Button, ButtonStyle, Option, SlashInteraction,
                     cooldown, guild_only, slash_command)
from dislash.interactions.message_interaction import MessageInteraction


class SlashUserInfo(commands.Cog):
    command_name = "userinfo"
    
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
    async def userinfo(self, inter:SlashInteraction, membre:Member=None):
        # Use author if member is not given
        if membre is None: member = inter.guild.get_member(inter.author.id)
        else: member = membre # change var's name to have personal var and not name in commands.json

        # Count how many member have infractions
        infractions = self.bot.infractions_manager.getInfractions(member_id=member.id) # get member's infractions
        counts = self.bot.infractions_manager.calculInfractions(infractions) # count each infraction

        # Create embed
        embed = Embed(
            description=f"Voici les informations concernant l'utilisateur `{member}`",
            color=self.bot.settings["defaultColors"]["userinfo"]
        )

        ## Add fields
        ### Add member's mention field
        embed.add_field(
            name="Mention",
            value=member.mention
        )
        ### Add member's roles field
        roles_mentions = [role.mention for role in member.roles if role != inter.guild.default_role] # create member's roles list and ignore everyone
        if roles_mentions == []: roles_string = "Aucun rôle" # use default str for members with no role
        else: roles_string = " ".join(roles_mentions) # create str from list
        embed.add_field(
            name="Rôles",
            value=roles_string
        )
        ### Add member's join datetime
        embed.add_field(
            name="A rejoint le serveur",
            value=member.joined_at.strftime("Le %A %d %B %Y")
        )
        ### Add date of creation of member's account
        embed.add_field(
            name="A créé son compte",
            value=member.created_at.strftime("Le %A %d %B %Y")
        )

        ## Set author (member)
        embed.set_author(
            name=f"{member} ({member.id})",
            icon_url=member.avatar_url
        )

        ## Set footer (counts)
        footer_counts_strings = [f"{infraction_action}: {counts[infraction_action]}" for infraction_action in counts]
        embed.set_footer(
            text="Infractions: "+' | '.join(footer_counts_strings)
        )

        # Create buttons
        ## create button to see member's infractions
        infra_button = Button(
            style=ButtonStyle.secondary,
            label="Voir les infractions",
            custom_id="send_infractions"
        )

        ## create button to send member's id
        id_button = Button(
            style=ButtonStyle.secondary,
            label="id",
            custom_id="send_id"
        )

        ## create row to stock buttons
        row = ActionRow(
            infra_button,
            id_button
        )

        ## Send embed
        await inter.create_response(embed=embed, components=[row])
        response = await inter.fetch_initial_response()

        ## add callbacks
        on_click = response.create_click_listener(timeout=120) # timeout of 120 seconds
        @on_click.matching_id("send_infractions")
        async def on_infra_button(inter:MessageInteraction):
            """Execute 'infractions' command"""
            if inter.author._user == inter.author._user:
                infra_button.disabled = True
                row = ActionRow(
                    infra_button,
                    id_button
                )
                await response.edit(components=[row])
                # Get infractions
                infractions = self.bot.infractions_manager.getInfractions(member_id=member.id)

                # Create infractions pages
                embeds = await self.bot.infractions_manager.createEmbedsWithInfractions(member_id=member.id, infractions=infractions, bot=self.bot)

                # Send embeds
                await inter.create_response(embeds=embeds)

            try: await inter.create_response()
            except: pass

        @on_click.matching_id("send_id")
        async def on_id_button(inter:MessageInteraction):
            if inter.author._user == inter.author._user:
                id_button.disabled = True
                row = ActionRow(
                    infra_button,
                    id_button
                )
                await response.edit(components=[row])
                await inter.create_response(
                    content=member.id
                )
                
        @on_click.timeout
        async def on_timeout():
            try: await response.edit(components=[])
            except: pass

def setup(bot:commands.Bot):
    bot.add_cog(SlashUserInfo(bot))
