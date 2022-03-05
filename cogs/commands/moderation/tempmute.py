import json
import locale
import time


from core.helpers import letterToFrenchWord
from core.decorators import check_permissions
from core.infractions_manager import Infraction, InfractionEmbedBuilder
from nextcord import Embed, User, Member
from nextcord.ext import commands
from datetime import datetime
import nextcord

# Set local time
locale.setlocale(locale.LC_TIME,'')

class TempMute(commands.Cog):
    command_name = "tempmute"
    
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
    async def tempmute(self, ctx:commands.Context, member:Member, duration:str=None, *, reason:str=None):
        # Check duration
        if (duration is not None) and (len(duration) > 1) and (duration[-1] in self.bot.settings["letters-duration"]) and (duration[:-1].isnumeric()):
            
            # Check if reason is too long
            if (reason is not None) and (len(reason) > 200):
                await self.bot.replyOrSend(
                    message=ctx.message,
                    embed=Embed(
                        description='La raison du tempmute ne peut excéder 200 caractères !',
                        color=self.bot.settings["defaultColors"]["error"]
                    )
                )

            # Check if member is muted
            muted_role_id = self.bot.settings["moderation-muted-role"]
            muted_role = nextcord.utils.find(lambda r: r.id == muted_role_id, ctx.guild.roles)
            if muted_role in member.roles:
                msg = await self.bot.replyOrSend(
                    message=ctx.message,
                    embed=Embed(
                        description="Ce membre est déjà mute !",
                        color=self.bot.settings["defaultColors"]["error"]
                    )
                )
                try: await msg.delete(delay=3) # delete msg after 3 seconds
                except: pass
                finally: return # to stop command
            # Member is not muted

            # Mute member
            await member.add_roles(muted_role)
            
            duration_timestamp = self.bot.infractions_manager.timestampFromDuration(duration)
            end_timestamp = time.time()+duration_timestamp

            # Create infraction
            infraction_without_id=Infraction(
                id=None,
                member_id=member.id,
                moderator_id=ctx.author.id,
                action='mute',
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
                    description=f"✅ `Infraction #{infraction.id}` {member.mention} a été mute pour **{duration[:-1]} {letterToFrenchWord(letter=duration[-1], number=int(duration[:-1]))}** !",
                    color=self.bot.settings["defaultColors"]["confirmation"]
                )
            )
            try: await confirmation_message.delete(delay=2) # Delete confirmation message after 2 seconds
            except: pass

            # Send embeds
            member_infractions = self.bot.infractions_manager.getInfractions(member_id=infraction.member_id)
            count = self.bot.infractions_manager.calculInfractions(infractions=member_infractions)["mute"]
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
    bot.add_cog(TempMute(bot))
