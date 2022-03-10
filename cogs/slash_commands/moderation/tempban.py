import json
import locale
import time

from core.decorators import check_slash_permissions
from core.helpers import letterToFrenchWord
from core.infractions_manager import Infraction, InfractionEmbedBuilder
from discord import Embed, User
from discord.ext import commands
from dislash import (Option, SlashInteraction, cooldown, guild_only,
                     slash_command)

# Set local time
locale.setlocale(locale.LC_TIME,'')

class SlashTempBan(commands.Cog):
    command_name = "tempban"
    
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
    async def tempban(self, inter:SlashInteraction, membre:User, duree:str=None, *, raison:str=None):
        member = membre # change var name (because of slash commands)
        duration = duree # change var name
        reason = raison # change var name
        # Check duration
        if (duration is not None) and (len(duration) > 1) and (duration[-1] in self.bot.settings["letters-duration"]) and (duration[:-1].isnumeric()):
            
            # Check if member is banned
            try:
                await inter.guild.fetch_ban(member)
                # no error : member is already banned
                await inter.respond(
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
                await inter.respond(
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
                    moderator_id=inter.author.id,
                    action='ban',
                    timestamp=time.time(),
                    end_timestamp=end_timestamp,
                    duration_string=duration,
                    reason=reason
                )

                # Add ban to database
                infraction = self.bot.infractions_manager.addInfraction(infraction=infraction_without_id)
                
                # Send confirmation message
                await inter.respond(
                    embed=Embed(
                        description=f"✅ `Infraction #{infraction.id}` {member.mention} a été banni du serveur pour **{duration[:-1]} {letterToFrenchWord(letter=duration[-1], number=int(duration[:-1]))}** !",
                        color=self.bot.settings["defaultColors"]["confirmation"]
                    )
                )
                try: await inter.delete_after(delay=2) # Delete interaction after 2 seconds
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
                    builder.author = inter.author
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
                builder.author = inter.author
                builder.build()
                embed = builder.embed # get embed
                await self.bot.infractions_manager.logInfraction(embed) # send embed in log channel

                # Ban member
                await inter.guild.ban(user=member, reason=reason)
        else:
            await inter.respond(
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

def setup(bot:commands.Bot):
    bot.add_cog(SlashTempBan(bot))
