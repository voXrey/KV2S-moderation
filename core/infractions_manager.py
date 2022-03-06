import datetime
import time

import discord
from core.helpers import letterToFrenchWord
from discord import Embed, Member, User
from discord.ext import commands
from core.database import Database
from core.helpers import letterToFrenchWord

class Infraction:
    def __init__(self, id:int, member_id:int, moderator_id:int, action:str, timestamp:int, end_timestamp:int=None, duration_string=None, reason:str=None):
        self.id = id
        self.member_id = member_id
        self.moderator_id = moderator_id
        self.action = action
        self.timestamp = timestamp
        self.end_timestamp = end_timestamp
        self.duration_string = duration_string
        self.reason = reason

class InfractionEmbedBuilder:
    def __init__(self, infraction:Infraction):
        self.infraction = infraction
        self.embed = Embed(timestamp=datetime.datetime.fromtimestamp(infraction.timestamp))
        self.description = []
        self.color = None
        self.author = None
    
    def addReason(self):
        """
        Add reason to embed description
        """
        reason = self.infraction.reason
        if reason is None: reason = "Aucune raison donnée"

        self.description.append(f"**Raison:** {reason}")

    def addAction(self):
        """
        Add action to embed description
        """
        self.description.append(f"**Action:** {self.infraction.action}")
    
    def addMember(self, member:User=None):
        """
        Add member to embed description
        """
        if member is not None: self.description.append(f"**Membre:** {member} ({member.id})")
        else: self.description.append(f"**Membre:** ({self.infraction.member_id})")

    def addActionCount(self, action_count:int):
        """
        Add action count to embed description
        """
        self.description.append(f"**Nombre de {self.infraction.action.replace('temp', '')}:** {action_count}")

    def addWarning(self, warnsforban_count:int):
        """
        Add warning to advert how many warns are required to be banned
        """
        self.description.append(f"**Attention** Vous serez sanctionné après 3, 5 et 10 warns !")

    def addDurationString(self):
        """
        Add duration of infraction if is a temporary infraction
        """
        duration_string = self.infraction.duration_string
        letter = duration_string[-1]
        number = int(duration_string[:-1])
        if duration_string is not None:
            word = letterToFrenchWord(letter, number)
            self.description.append(f"**Durée:** `{number} {word}`")

    def setColor(self, color:int):
        """
        Stock embed color
        """
        self.color = color

    def buildDescription(self):
        """
        Build embed description
        """
        self.embed.description = '\n'.join(self.description)

    def buildAuthor(self):
        """
        Build embed author
        """
        if self.author is not None: self.embed.set_author(name=self.author, icon_url=self.author.avatar_url)
        else: self.embed.set_author(name=f"({self.infraction.moderator_id})")
    
    def buildFooter(self):
        """
        Build footer
        """
        self.embed.set_footer(text=f"Infraction #{self.infraction.id}")

    def buildColor(self):
        """
        Build embed color
        """
        self.embed.color = self.color

    def build(self):
        """
        Build all embed
        """
        self.buildAuthor()
        self.buildDescription()
        self.buildFooter()
        self.buildColor()

class InfractionsManager:
    def __init__(self, bot:commands.Bot):
        self.database = Database()
        self.bot = bot

    def deleteInfraction(self, infraction_id:int):
        """
        Delete infraction
        
        Parameters:
        infraction_id (int): id of infraction to delete
        """
        self.database.execute('DELETE FROM infractions WHERE infraction_id = ?', [infraction_id])

    def editInfraction(self, infraction:Infraction):
        """
        Edit an infraction
        
        Paramters:
        infraction (Infraction): infraction to edit
        """
        self.database.execute(
            """UPDATE infractions
                SET member_id = ?,
                    moderator_id = ?,
                    action = ?,
                    timestamp = ?,
                    end_timestamp = ?,
                    reason = ?
                WHERE
                    infraction_id = ?
            """,
            [
                infraction.member_id,
                infraction.moderator_id,
                infraction.action,
                infraction.timestamp,
                infraction.end_timestamp,
                infraction.reason,
                infraction.id
            ])

    def calculInfractions(self, infractions:list[Infraction]) -> dict[str:int]:
        """
        Calcul how many have infractions of action in an infractions list
        
        Parameters:
        infractions (list[Infraction]): the list of infractions
        
        Returns:
        dict[str:int]: number of infractions (value) for each action (key)
        """
        result = {'warn': 0, 'mute':0, 'kick':0, 'ban':0}
        for infraction in infractions:
            action = infraction.action.replace('temp', "")
            if action in result: result[action] += 1
        return result

    async def createEmbedsWithInfractions(self, member_id:int, infractions:list[Infraction], bot:commands.Bot):
        embeds = [] # Embeds list
        infractions_count = len(infractions) # Number of infractions
        infractions_by_page = 8 # Number of infractions by page/embed
        embeds_count = (infractions_count//(infractions_by_page+1))+1 # Number of embeds
        
        for i in range(1, embeds_count+1):
            # Create infractions list to add to embed description
            infractions_strings = []

            infractions_embed_count = 1
            for infraction_idex in range((i-1)*infractions_by_page, ((i-1)*infractions_by_page)+infractions_by_page):
                if infraction_idex >= infractions_count: break
                
                infraction = infractions[infraction_idex]

                # Define reason
                if infraction.reason is None: reason = "Aucune raison donnée"
                else: reason = infraction.reason

                # Add infraction
                infractions_strings.append(f"**Infraction #{infraction.id} - {infraction.action}**\n{reason}")
                infractions_embed_count += 1

            # Add default description user avec not infraction
            if infractions_strings == []: infractions_strings.append("Ce membre n'a aucune infraction")

            # Create embed
            embed = Embed(
                description='\n\n'.join(infractions_strings),
                color=bot.settings["defaultColors"]["userinfo"]
            )
            
            # Add member
            if member_id == bot.user.id: # if user is the bot
                member = bot.user
                embed.set_author(name=member, icon_url=member.avatar_url)
            else:
                try:
                    member = await bot.fetch_user(member_id)
                    embed.set_author(name=member, icon_url=member.avatar_url)
                except:
                    embed.set_author(name=f"({member_id})", icon_url=bot.user.default_avatar_url)

            # Add total of infractions
            infractions_actions_count = self.calculInfractions(infractions=infractions)
            footer_infractions_strings = [f"{infraction_action}: {infractions_actions_count[infraction_action]}" for infraction_action in infractions_actions_count]
            embed.set_footer(text=' | '.join(footer_infractions_strings))

            embeds.append(embed)
        
        # Return embeds list
        return embeds

    def getInfraction(self, infraction_id) -> Infraction:
        """
        Get infraction
        
        Parameters:
        infraction_id (int): infraction's id
        
        Returns:
        Infraction: infraction with this id
        None: if infraction not exists
        """
        result = self.database.fetchone('SELECT member_id, moderator_id, action, timestamp, end_timestamp, duration_string, reason FROM infractions WHERE infraction_id = ?',
                                    [infraction_id])
        if result is not None:
            return Infraction(
                id=infraction_id,
                member_id=result[0],
                moderator_id=result[1],
                action=result[2],
                timestamp=result[3],
                end_timestamp=result[4],
                duration_string=result[5],
                reason=result[6]
            )
        else: return None

    def getInfractions(self, member_id:int) -> list[Infraction]:
        """
        Get all member's infractions
        
        Parameters:
        member_id (int): member's id
        
        Returns:
        list[Infraction]: list of member's infractions
        """
        results = self.database.fetchall(
            'SELECT infraction_id, moderator_id, action, timestamp, end_timestamp, duration_string, reason FROM infractions WHERE member_id = ?',
            [member_id]
        )
        return [
            Infraction(
                id=result[0],
                member_id=member_id,
                moderator_id=result[1],
                action=result[2],
                timestamp=result[3],
                end_timestamp=result[4],
                duration_string=result[5],
                reason=result[6]
            )
            for result in results
        ]

    def addInfraction(self, infraction:Infraction) -> Infraction:
        """
        Add infraction to database
        
        Parameters:
        infraction (Infraction): new infraction without id
        
        Returns:
        Infraction: new infraction with id
        """
        if infraction.action in ['ban', 'mute', 'unban', 'unmute']:
            member_infractions = self.getInfractions(infraction.member_id)
            for member_infraction in member_infractions:
                self.endInfraction(member_infraction.id)

        infraction_id = self.database.execute(
            sql="INSERT INTO infractions(member_id, moderator_id, action, timestamp, end_timestamp, reason) VALUES(?, ?, ?, ?, ?, ?)",
            args=[
                infraction.member_id,
                infraction.moderator_id,
                infraction.action,
                infraction.timestamp,
                infraction.end_timestamp,
                infraction.reason
            ]
        )
        infraction.id = infraction_id
        return infraction

    async def logInfraction(self, infraction_embed:Embed):
        try: await self.bot.mychannels['moderation-logs'].send(embed=infraction_embed)
        except Exception as e: print(e)

    def timestampFromDuration(self, duration:str):
        """
        Get a timestamp
        """
        letter = duration[-1]
        n = int(duration[:-1])

        return n*self.bot.settings["letters-duration"][letter]

    def endInfraction(self, infraction_id):
        self.database.execute(
            """UPDATE infractions
                SET ended = 1
                WHERE
                    infraction_id = ?
            """,
            args=[infraction_id]
        )

    def membersToUnban(self):
        """
        Get list of members to unban who are in db
        
        Returns:
        list[int]: list of members'id to unban
        """
        # Get all last bans (no ended) where duration is finished (end_timestamp < time.time())
        results = self.database.fetchall(
            sql="""SELECT infraction_id, member_id FROM infractions
                        WHERE
                            action = ?
                            AND ended = ?
                            AND end_timestamp < ?
                """,
            args=[
                'ban',
                0,
                time.time()
            ]
        )

        # Create dict to stock members to unban
        members = {}
        for result in results:
            infraction_id = result[0]
            member_id = result[1]
            
            members[member_id] = infraction_id # add to dict
            self.endInfraction(infraction_id) # end infraction

        return members
    
    def membersToUnmute(self):
        """
        Get list of members to unmute who are in db
        
        Returns:
        list[int]: list of members'id to unmute
        """
        # Get all last mutes (no ended) where duration is finished (end_timestamp < time.time())
        results = self.database.fetchall(
            sql="""SELECT infraction_id, member_id FROM infractions
                        WHERE
                            action = ?
                            AND ended = ?
                            AND end_timestamp < ?
                """,
            args=[
                'mute',
                0,
                time.time()
            ]
        )

        # Create dict to stock members to unban
        members = {}
        for result in results:
            infraction_id = result[0]
            member_id = result[1]
            
            members[member_id] = infraction_id # add to dict
            self.endInfraction(infraction_id) # end infraction

        return members
    
    async def checkWarnsForSanction(self, member_id):
        # get member's infractions
        member_infractions = self.getInfractions(member_id=member_id)
        counts = self.calculInfractions(infractions=member_infractions)
        warn_count = counts['warn']

        # create default infractionn
        default_infraction = Infraction(
            id=None,
            member_id=member_id,
            moderator_id=self.bot.user.id,
            action=None,
            timestamp=time.time(),
            end_timestamp=None,
            duration_string=None,
            reason=None
        )

        # get guild and member
        guild = await self.bot.fetch_guild(self.bot.settings["guild_id"])
        member = await guild.fetch_member(member_id)
        
        # test if member must to be muted/banned
        if warn_count == 1:
            duration_string = "2j"
            default_infraction.action = "mute"
            default_infraction.duration_string = duration_string
            default_infraction. end_timestamp = self.timestampFromDuration(duration_string) + default_infraction.timestamp
            default_infraction.reason = "Mute automatique 2 jours après 3 warns"
            
            # add infraction
            infraction = self.addInfraction(infraction=default_infraction)

            # check if member is in the guild
            muted_role_id = self.bot.settings["moderation-muted-role"]
            muted_role = discord.utils.find(lambda r: r.id == muted_role_id, guild.roles)

            try:
                member = await guild.fetch_member(member_id)
                # no error : member is in guild

                # check if member has muted role
                if muted_role not in member.roles:
                    try: await member.add_roles(muted_role)
                    except Exception as e: print(e)
                
                # send embed to member
                builder = InfractionEmbedBuilder(infraction) # define embed builder
                builder.addMember(member)
                builder.addAction()
                builder.addDurationString()
                builder.addReason()
                builder.setColor(self.bot.settings["defaultColors"]["sanction"])
                builder.author = self.bot.user
                builder.build()
                embed = builder.embed # get embed
                if member.dm_channel is None: await member.create_dm() # create dm with member
                await member.dm_channel.send(embed=embed) # send embed to member

            except:
                # error : member is not in guild
                pass

            finally:
                # Build embed to send in log channels
                builder = InfractionEmbedBuilder(infraction) # define embed builder
                builder.addMember(member)
                builder.addAction()
                builder.addDurationString()
                builder.addReason()
                builder.setColor(self.bot.settings["defaultColors"]["sanction"])
                builder.author = self.bot.user
                builder.build()
                embed = builder.embed # get embed
                await self.logInfraction(embed) # send embed in log channel
                
        elif warn_count == 5:
            duration_string = "3j"
            default_infraction.action = "ban"
            default_infraction.duration_string = duration_string
            default_infraction. end_timestamp = self.timestampFromDuration(duration_string) + default_infraction.timestamp
            default_infraction.reason = "Ban automatique 3 jours après 5 warns"

            # add infraction
            infraction = self.addInfraction(infraction=default_infraction)

            # Build embed to send in log channels
            builder = InfractionEmbedBuilder(infraction) # define embed builder
            builder.addMember(member)
            builder.addAction()
            builder.addDurationString()
            builder.addReason()
            builder.setColor(self.bot.settings["defaultColors"]["sanction"])
            builder.author = self.bot.user
            builder.build()
            embed = builder.embed # get embed
            await self.logInfraction(embed) # send embed in log channel

            # Build and send embed to member if he is in guild
            try:
                member = await guild.fetch_member(member_id)
                builder = InfractionEmbedBuilder(infraction) # define embed builder
                builder.addMember(member)
                builder.addAction()
                builder.addDurationString()
                builder.addReason()
                builder.setColor(self.bot.settings["defaultColors"]["sanction"])
                builder.author = self.bot.user
                builder.build()
                embed = builder.embed # get embed
                if member.dm_channel is None: await member.create_dm() # create dm with member
                await member.dm_channel.send(embed=embed) # send embed to member
            except: pass

            # Ban member
            await guild.ban(user=member, reason=infraction.reason)
    
        elif warn_count == 10:
            duration_string = "7j"
            default_infraction.action = "ban"
            default_infraction.duration_string = duration_string
            default_infraction. end_timestamp = self.timestampFromDuration(duration_string) + default_infraction.timestamp
            default_infraction.reason = "Ban automatique 7 jours après 10 warns"

            # add infraction
            infraction = self.addInfraction(infraction=default_infraction)

            # Build embed to send in log channels
            builder = InfractionEmbedBuilder(infraction) # define embed builder
            builder.addMember(member)
            builder.addAction()
            builder.addDurationString()
            builder.addReason()
            builder.setColor(self.bot.settings["defaultColors"]["sanction"])
            builder.author = self.bot.user
            builder.build()
            embed = builder.embed # get embed
            await self.logInfraction(embed) # send embed in log channel

            # Build and send embed to member if he is in guild
            try:
                member = await guild.fetch_member(member_id)
                builder = InfractionEmbedBuilder(infraction) # define embed builder
                builder.addMember(member)
                builder.addAction()
                builder.addDurationString()
                builder.addReason()
                builder.setColor(self.bot.settings["defaultColors"]["sanction"])
                builder.author = self.bot.user
                builder.build()
                embed = builder.embed # get embed
                if member.dm_channel is None: await member.create_dm() # create dm with member
                await member.dm_channel.send(embed=embed) # send embed to member
            except: pass

            # Ban member
            await guild.ban(user=member, reason=infraction.reason)
        
        else: return # stop function
        
