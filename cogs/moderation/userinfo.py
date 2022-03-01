import json

from core.decorators import check_permissions
from nextcord import ButtonStyle, Embed, Member, Interaction
from nextcord.ext import commands
from nextcord.ui import Button, View

class UserInfo(commands.Cog):
    command_name = "userinfo"
    
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
    async def userinfo(self, ctx:commands.Context, member:Member=None):
        # Set member
        if member is None: member = ctx.author

        # Get infractions and counts
        infractions = self.bot.infractions_manager.getInfractions(member_id=member.id)
        counts = self.bot.infractions_manager.calculInfractions(infractions)

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
        roles_mentions = [role.mention for role in member.roles if role != ctx.guild.default_role]
        if roles_mentions == []: roles_string = "Aucun rôle"
        else: roles_string = " ".join(roles_mentions)
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

        ## Set author who is the member
        embed.set_author(
            name=f"{member} ({member.id})",
            icon_url=member.display_avatar.url
        )

        ## Set footer (counts)
        footer_counts_strings = [f"{infraction_action}: {counts[infraction_action]}" for infraction_action in counts]
        embed.set_footer(
            text="Infractions: "+' | '.join(footer_counts_strings)
        )

        # Create view's buttons
        infra_button = Button(
            style=ButtonStyle.secondary,
            label="Voir les infractions",
            custom_id="send_infractions"
        )
        async def infra_callback(interaction:Interaction):
            if interaction.user == ctx.author._user:
                await ctx.invoke(self.bot.get_command('infractions'), member)
        infra_button.callback = infra_callback

        id_button = Button(
            style=ButtonStyle.secondary,
            label="id",
            custom_id="send_id"
        )
        async def id_callback(interaction:Interaction):
            if interaction.user == ctx.author._user:
                try: await ctx.reply(member.id)
                except: await ctx.send(member.id)
        id_button.callback = id_callback

        view = View()
        view.add_item(infra_button)
        view.add_item(id_button)

        # Send embed
        try:
            await ctx.reply(
                embed=embed,
                view=view
            )
        except:
            await ctx.send(
                embed=embed,
                view=view
            )

def setup(bot:commands.Bot):
    bot.add_cog(UserInfo(bot))
