import json
import locale
import time

from core.decorators import check_permissions
from core.infractions_manager import Infraction, InfractionEmbedBuilder
from discord import Embed, User
from discord.ext import commands

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
        # Check if member is banned with a try
        try:
            await ctx.guild.fetch_ban(member)
            # member is banned (no error)
            
            # Check if reason is too long
            if (reason is not None) and (len(reason) > 200):
                msg = await self.bot.replyOrSend(
                    message=ctx.message,
                    embed=Embed(
                        description='La raison de l\'unban ne peut excéder 200 caractères !',
                        color=self.bot.settings["defaultColors"]["error"]
                    )
                )

            else: # reason is good
                # Unban user
                await ctx.guild.unban(member)

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
                confirmation_message = await self.bot.replyOrSend(
                    message=ctx.message,
                    embed=Embed(
                        description=f"✅ `Infraction #{infraction.id}` {member.mention} a été unban du serveur !",
                        color=self.bot.settings["defaultColors"]["confirmation"]
                    )
                )
                try: await confirmation_message.delete(delay=2) # Delete confirmation message after 2 seconds
                except: pass

                # Build embed to send in log channel
                builder = InfractionEmbedBuilder(infraction) # define embed builder
                builder.addMember(member)
                builder.addAction()
                builder.addReason()
                builder.setColor(self.bot.settings["defaultColors"]["cancel"])
                builder.author = ctx.author
                builder.build()
                embed = builder.embed # get embed
                await self.bot.infractions_manager.logInfraction(embed) # send embed in log channel

        except:
            # member is not banned
            msg = await self.bot.replyOrSend(
                message=ctx.message,
                embed=Embed(
                    description='Cet utilisateur n\'est pas banni du serveur !',
                    color=self.bot.settings["defaultColors"]["error"]
                    )
            )
            try: await msg.delete(delay=3) # delete msg after 3 seconds
            except: pass

        # Delete command
        await ctx.message.delete()

def setup(bot:commands.Bot):
    bot.add_cog(UnBan(bot))
