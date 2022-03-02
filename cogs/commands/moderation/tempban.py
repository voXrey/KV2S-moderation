import json
import locale
import time

from core.helpers import letterToFrenchWord
from core.decorators import check_permissions
from core.infractions_manager import Infraction, InfractionEmbedBuilder
from nextcord import Embed, User
from nextcord.ext import commands
from datetime import datetime

# Set local time
locale.setlocale(locale.LC_TIME,'')

class TempBan(commands.Cog):
    command_name = "tempban"
    
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
    async def tempban(self, ctx:commands.Context, member:User, duration:str=None, *, reason:str=None):
        # Check duration
        if (duration is not None) and (len(duration) > 1) and (duration[-1] in self.bot.settings["letters-duration"]) and (duration[:-1].isnumeric()):
            
            # Check if member is banned
            try:
                await ctx.guild.fetch_ban(member)
                # no error : member is already banned
                await self.bot.replyOrSend(
                    message=ctx.message,
                    embed=Embed(
                        description='Ce membre est déjà banni !',
                        color=self.bot.settings["defaultColors"]["error"]
                    )
                )
                return # to stop command
            except:
                # member is not banned
                pass # continue command
            
            # Check if reason is too long
            if (reason is not None) and (len(reason) > 200):
                await self.bot.replyOrSend(
                    message=ctx.message,
                    embed=Embed(
                        description='La raison du tempban ne peut excéder 200 caractères !',
                        color=self.bot.settings["defaultColors"]["error"]
                    )
                )
            
            else:
                duration_timestamp = self.bot.infractions_manager.timestampFromDuration(duration)
                end_timestamp = time.time()+duration_timestamp

                # Create infraction
                infraction_without_id=Infraction(
                    id=None,
                    member_id=member.id,
                    moderator_id=ctx.author.id,
                    action='ban',
                    timestamp=time.time(),
                    end_timestamp=end_timestamp,
                    duration_string=duration,
                    reason=reason
                )

                # Add ban to database
                infraction = self.bot.infractions_manager.addInfraction(infraction=infraction_without_id)
                
                # Send confirmation message
                confirmation_message = await self.bot.replyOrSend(
                    message=ctx.message,
                    embed=Embed(
                        description=f"✅ `Infraction #{infraction.id}` {member.mention} a été banni du serveur pour **{duration[:-1]} {letterToFrenchWord(letter=duration[-1], number=int(duration[:-1]))}** !",
                        color=self.bot.settings["defaultColors"]["confirmation"]
                    )
                )
                try: await confirmation_message.delete(delay=2) # Delete confirmation message after 2 seconds
                except: pass

                # Send embeds
                member_infractions = self.bot.infractions_manager.getInfractions(member_id=infraction.member_id)
                count = self.bot.infractions_manager.calculInfractions(infractions=member_infractions)["ban"]
                ## Try to send message to member
                try:
                    builder = InfractionEmbedBuilder(infraction) # define embed builder
                    builder.addAction()
                    builder.addDurationString()
                    builder.addActionCount(count)
                    builder.addReason()
                    builder.setColor(self.bot.settings["defaultColors"]["sanction"])
                    builder.author = ctx.author
                    builder.build()
                    embed = builder.embed # get embed
                    
                    if member.dm_channel is None: await member.create_dm() # create dm with member
                    await member.dm_channel.send(embed=embed) # send embed to member
                except: pass

                # Build embed to send in log channels
                builder = InfractionEmbedBuilder(infraction) # define embed builder
                builder.addMember(member)
                builder.addAction()
                builder.addDurationString()
                builder.addActionCount(count)
                builder.addReason()
                builder.setColor(self.bot.settings["defaultColors"]["sanction"])
                builder.author = ctx.author
                builder.build()
                embed = builder.embed # get embed
                await self.bot.infractions_manager.logInfraction(embed) # send embed in log channel

                # Ban member
                await ctx.guild.ban(user=member, reason=reason)
        else:
            await self.bot.replyOrSend(
                message=ctx.message,
                embed=Embed(
                    description=f"""La durée fournie n'est pas valide !
                                    Voici comment fournir une durée valide: [nombre][lettre]
                                    `s` : secondes
                                    `m` : minutes
                                    `h` : heures
                                    `j` et `d` : jours
                                    `M` : mois
                                    `a` et `y` : années
                                    """,
                    color=self.bot.settings["defaultColors"]["error"]
                )
                .set_footer(text="Seuls les mois et les minutes sont sensibles aux majuscules")
            )

        # Delete command
        await ctx.message.delete()

def setup(bot:commands.Bot):
    bot.add_cog(TempBan(bot))
