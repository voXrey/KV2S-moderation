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

    async def getEmbed(self, bot:nextcord.ext.commands.Bot):
        description=""

        # Add member
        try:
            member = await bot.fetch_user(self.member_id)
            description+=f"**Membre:** {member} ({self.member_id})"
        except:
            description+=f"**Membre:** ({self.member_id})"

        # Add action
        description+=f"\n**Action:** {self.action}"

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
        embed.set_footer(text=self.id)
        

class InfractionsManager:
    def __init__(self):
        pass

    def getInfractionEmbed(self, infraction_id):
        description=""

        embed = Embed(
            title=f"Infraction {infraction_id}",
            description=description,
            color=0xffffff
        )
    def getInfraction(self, infraction_id):
        pass
    def warn(self, member_id, moderator_id, timestamp, reason):
        database = Database()
        database.execute(sql="INSERT INTO infractions(member_id, moderator_id, action, timestamp, reason) VALUES(?, ?, ?, ?, ?)",
                            args=[member_id, moderator_id, 'warn', timestamp, reason])

infractions_manager = InfractionsManager()