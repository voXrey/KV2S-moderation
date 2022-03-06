from turtle import color
from discord import Embed
from discord.ext import tasks
from discord.ext.commands import Bot, Cog


class CheckBanned(Cog):
    def __init__(self, bot:Bot):
        self.bot = bot
        self.time = float(bot.settings["moderation-update-time"])
        self.check_banned.change_interval(seconds=self.time)
        self.check_banned.start()

    def cog_unload(self) -> None:
        self.check_banned.cancel()
        return super().cog_unload()

    @tasks.loop()
    async def check_banned(self):
        guild = await self.bot.fetch_guild(914554436926447636)
        members = self.bot.infractions_manager.membersToUnban()
        
        for member_id in members:
            # check if member is banned
            user = await self.bot.fetch_user(member_id)
            isbanned = False
            try:
                await guild.fetch_ban(user)
                isbanned = True
            except: pass

            # unban member if he is banned
            if isbanned:
                try:
                    await guild.unban(user)
                    await self.bot.infractions_manager.logInfraction(
                        Embed(
                            title="Unban automatique",
                            description=f"`{user}` a été unban (Infraction `#{members[member_id]}`)",
                            color=self.bot.settings["defaultColors"]["cancel"]
                        )
                            .set_author(name=self.bot.user, icon_url=self.bot.user.avatar_url)
                    )
                except Exception as e:
                    print(e)
            
def setup(bot:Bot):
    bot.add_cog(CheckBanned(bot))
