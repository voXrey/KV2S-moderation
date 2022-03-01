import json

from nextcord.ext import commands

from core.decorators import check_permissions
from core.infractions_manager import InfractionEmbedBuilder

class Infraction(commands.Cog):
    command_name = "infraction"

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
    @commands.has_permissions(kick_members=True)
    @commands.cooldown(1, 1, commands.BucketType.member)
    @check_permissions
    async def infraction(self, ctx:commands.Context, infraction_id:int):
        # Get infraction
        infraction = self.bot.infractions_manager.getInfraction(infraction_id=infraction_id)

        # If infraction not exists
        if infraction is None:
            msg = await self.bot.replyOrSend(
                message=ctx.message,
                content="Cette infraction n'existe pas"
            )
            try: await msg.delete(delay=3)
            except: pass

        # Send embed if infraction exists
        else:
            # Get infraction embed
            builder = InfractionEmbedBuilder(infraction) # define embed builder
            builder.addMember(await self.bot.fetch_user(infraction.member_id))
            builder.addAction()
            builder.addReason()
            builder.setColor(self.bot.settings["defaultColors"]["sanction"])
            builder.author = await self.bot.fetch_user(infraction.moderator_id)
            builder.build()
            embed = builder.embed # get embed
            
            await self.bot.replyOrSend(
                message=ctx.message,
                embed=embed
            )

        # delete command
        try: await ctx.message.delete()
        except: pass

def setup(bot:commands.Bot):
    bot.add_cog(Infraction(bot))
