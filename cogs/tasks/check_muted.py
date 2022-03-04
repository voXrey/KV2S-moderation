from turtle import color
from nextcord import Embed
import nextcord
from nextcord.ext import tasks
from nextcord.ext.commands import Bot, Cog
from core.infractions_manager import InfractionEmbedBuilder


class CheckMuted(Cog):
    def __init__(self, bot:Bot):
        self.bot = bot
        self.time = float(bot.settings["moderation-update-time"])
        self.check_muted.change_interval(seconds=self.time)
        self.check_muted.start()

    def cog_unload(self) -> None:
        self.check_muted.cancel()
        return super().cog_unload()

    @tasks.loop()
    async def check_muted(self):
        guild = await self.bot.fetch_guild(914554436926447636)
        muted_role_id = self.bot.settings["moderation-muted-role"]
        muted_role = nextcord.utils.find(lambda r: r.id == muted_role_id, guild.roles)
        members = self.bot.infractions_manager.membersToUnmute()
        
        for member_id in members:
            # check if member is in the guild
            try: 
                member = await guild.fetch_member(member_id)
                # no error : member is in guild
            except:
                # error : member is not in guild
                continue

            # check if member has muted role
            if muted_role in member.roles:
                try:
                    await member.remove_roles(muted_role)
                    await self.bot.infractions_manager.logInfraction(
                        Embed(
                            title="Unmute automatique",
                            description=f"`{member}` a été unmute (Infraction `#{members[member_id]}`)",
                            color=self.bot.settings["defaultColors"]["cancel"]
                        )
                            .set_author(name=self.bot.user, icon_url=self.bot.user.display_avatar.url)
                    )
                except Exception as e:
                    print(e)

def setup(bot:Bot):
    bot.add_cog(CheckMuted(bot))
