import datetime
from nextcord import Color, Embed, DefaultAvatar
import nextcord.ext.commands
from core.database import Database

class Infraction:
    def __init__(self, id, member_id, moderator_id, action, timestamp, end_timestamp, reason):
        self.id = id
        self.member_id = member_id
        self.moderator_id = moderator_id
        self.action = action
        self.timestamp = timestamp
        self.end_timestamp = end_timestamp
        self.reason = reason

    async def getSimpleEmbed(self, bot:nextcord.ext.commands.Bot):
        infractions_manager = InfractionsManager()

        description=""

        # Add member
        try:
            member = await bot.fetch_user(self.member_id)
            description+=f"**Membre:** {member} ({self.member_id})"
        except:
            description+=f"**Membre:** ({self.member_id})"

        # Add action
        description+=f"\n**Action:** {self.action}"

        # Add action compteur
        member_infractions = infractions_manager.getInfractions(member_id=self.member_id)
        count = infractions_manager.calculInfractions(infractions=member_infractions)
        description+=f"\n**Nombre de {self.action}:** {count[self.action]}"

        # Add reason
        if self.reason is None: reason = "Aucune raison donnée"
        else: reason = self.reason
        description+=f"\n**Raison:** {reason}"

        # Create embed
        embed = Embed(
            description=description,
            timestamp=datetime.datetime.fromtimestamp(self.timestamp),
            color=0xffffff
        )

        # Add moderator
        try:
            moderator = await bot.fetch_user(self.moderator_id)
            embed.set_author(name=moderator, icon_url=moderator.avatar.url)
        except:
            embed.set_author(name=self.moderator_id, icon_url=DefaultAvatar(Color.blurple))

        # Add infraction id
        embed.set_footer(text=f"Infraction #{self.id}")
        
        # Return the simple embed
        return embed

class InfractionsManager:
    def __init__(self):
        pass

    def deleteInfraction(self, infraction_id:int):
        database = Database()
        database.execute('DELETE FROM infractions WHERE infraction_id = ?', [infraction_id])

    def editInfraction(self, infraction:Infraction):
        database = Database()
        database.execute(
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

    def calculInfractions(self, infractions:list[Infraction]):
        result = {'warn': 0, 'mute':0, 'kick':0, 'ban':0}
        for infraction in infractions: result[infraction.action] += 1
        return result

    async def createEmbedsWithInfractions(self, member_id, infractions:list[Infraction], bot):
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

            # Create embed
            embed = Embed(
                description='\n\n'.join(infractions_strings),
                color=0xffffff
            )
            
            # Add member
            try:
                member = await bot.fetch_user(member_id)
                embed.set_author(name=member, icon_url=member.avatar.url)
            except:
                embed.set_author(name=f"({member_id})", icon_url=DefaultAvatar(Color.blurple))

            # Add total of infractions
            infractions_actions_count = self.calculInfractions(infractions=infractions)
            footer_infractions_strings = [f"{infraction_action}: {infractions_actions_count[infraction_action]}" for infraction_action in infractions_actions_count]
            embed.set_footer(text=' | '.join(footer_infractions_strings))

            embeds.append(embed)
        
        # Return embeds list
        return embeds

    def getInfraction(self, infraction_id):
        database = Database()
        result = database.fetchone('SELECT member_id, moderator_id, action, timestamp, end_timestamp, reason FROM infractions WHERE infraction_id = ?',
                                    [infraction_id])
        if result is not None:
            return Infraction(
                id=infraction_id,
                member_id=result[0],
                moderator_id=result[1],
                action=result[2],
                timestamp=result[3],
                end_timestamp=result[4],
                reason=result[5]
            )
        else: return None

    def getInfractions(self, member_id):
        database = Database()
        results = database.fetchall(
            'SELECT infraction_id, moderator_id, action, timestamp, end_timestamp, reason FROM infractions WHERE member_id = ?',
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
                reason=result[5]
            )
            for result in results
        ]

    def warn(self, member_id, moderator_id, timestamp, reason):
        database = Database()
        database.execute(sql="INSERT INTO infractions(member_id, moderator_id, action, timestamp, reason) VALUES(?, ?, ?, ?, ?)",
                            args=[member_id, moderator_id, 'warn', timestamp, reason])
        return database.cur.lastrowid
    
    def kick(self, member_id, moderator_id, timestamp, reason):
        database = Database()
        database.execute(sql="INSERT INTO infractions(member_id, moderator_id, action, timestamp, reason) VALUES(?, ?, ?, ?, ?)",
                            args=[member_id, moderator_id, 'kick', timestamp, reason])
        return database.cur.lastrowid

infractions_manager = InfractionsManager()