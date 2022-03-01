import json
import locale
import time

from core.decorators import check_permissions
from core.infractions_manager import Infraction, InfractionEmbedBuilder
from nextcord import Embed, User
from nextcord.ext import commands

# Set local time
locale.setlocale(locale.LC_TIME,'')

class UnBan(commands.Cog):
    command_name = "unban"
    
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
    @commands.has_permissions(ban_members=True)
    @commands.cooldown(1, 1, commands.BucketType.member)
    @check_permissions
    async def unban(self, ctx:commands.Context, member:User, *, reason:str=None):
        # Check if member is banned
        try:
            await ctx.guild.fetch_ban(member)
            # member is banned
            
            # Check if reason is too long
            if (reason is not None) and (len(reason) > 200):
                try:
                    msg = await ctx.reply(embed=Embed(
                        description='La raison de l\'unban ne peut excéder 200 caractères !',
                        color=self.bot.settings["defaultColors"]["error"]
                        )
                    )
                except:
                    msg = await ctx.send(embed=Embed(
                        description='La raison de l\'unban ne peut excéder 200 caractères !',
                        color=self.bot.settings["defaultColors"]["error"]
                        )
                    )
                try: await msg.delete(delay=3)
                except: pass
            
            else:
                # Create infraction
                infraction_without_id=Infraction(
                    id=None,
                    member_id=member.id,
                    moderator_id=ctx.author.id,
                    action='unban',
                    timestamp=time.time(),
                    reason=reason
                )

                # Add unban to database
                infraction = self.bot.infractions_manager.addInfraction(infraction=infraction_without_id)
                
                # Send confirmation message
                try:
                    confirmation_message = await ctx.reply(
                    embed=Embed(
                        description=f"✅ `Infraction #{infraction.id}` {member.mention} a été unban du serveur !",
                        color=self.bot.settings["defaultColors"]["confirmation"]
                    )
                )
                except:
                    confirmation_message = await ctx.send(
                    embed=Embed(
                        description=f"✅ `Infraction #{infraction.id}` {member.mention} a été unban du serveur !",
                        color=self.bot.settings["defaultColors"]["confirmation"]
                    )
                )
                # Delete confirmation message
                try: await confirmation_message.delete(delay=1.5)
                except: pass

                # Send embed in log channel
                builder = InfractionEmbedBuilder(infraction)
                builder.addMember(member)
                builder.addAction()
                builder.addReason()
                builder.setColor(self.bot.settings["defaultColors"]["cancel-sanction"])
                builder.author = ctx.author
                builder.build()
                embed = builder.embed
                await self.bot.infractions_manager.logInfraction(embed)

                # Unban user
                await ctx.guild.unban(member)
        except:
            # member is not banned
            try:
                msg = await ctx.reply(embed=Embed(
                    description='Cet utilisateur n\'est pas banni du serveur !',
                    color=self.bot.settings["defaultColors"]["error"]
                    )
                )
            except:
                msg = await ctx.send(embed=Embed(
                    description='Cet utilisateur n\'est pas banni du serveur !',
                    color=self.bot.settings["defaultColors"]["error"]
                    )
                )
            try: await msg.delete(delay=3)
            except: pass

        # Delete command
        await ctx.message.delete()


def setup(bot:commands.Bot):
    bot.add_cog(UnBan(bot))
