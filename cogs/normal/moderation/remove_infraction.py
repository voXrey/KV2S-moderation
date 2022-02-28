import json

from core.decorators import check_permissions
from nextcord import Embed
from nextcord.ext import commands

class RemoveInfraction(commands.Cog):
    command_name = "remove-infraction"
    
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
    async def remove_infraction(self, ctx:commands.Context, infraction_id:int):
        # Get infraction
        infraction = self.bot.infractions_manager.getInfraction(infraction_id=infraction_id)

        # If infraction not exists
        if infraction is None:
            try: msg = await ctx.reply("Cette infraction n'existe pas")
            except: msg = await ctx.send("Cette infraction n'existe pas")
            try: await msg.delete(delay=3)
            except: pass

        # If infraction exists
        else:
            # Request confirmation
            try:
                confirmation_message = await ctx.reply(
                content="Êtes-vous sûr de vouloir supprimer cette infraction ? (oui/non)",
                embed = await self.bot.infractions_manager.createInfractionEmbed(self.bot, infraction)
            )
            except:
                confirmation_message = await ctx.send(
                content="Êtes-vous sûr de vouloir supprimer cette infraction ? (oui/non)",
                embed = await self.bot.infractions_manager.createInfractionEmbed(self.bot, infraction)
            )

            ## Wait confirmation
            def check(m): return (m.channel==ctx.channel) and (m.author == ctx.author)
            message_response = await self.bot.wait_for('message', check=check, timeout=120) # wait confirmation message
            
            response = message_response.content.lower()
            if response == "oui":
                self.bot.infractions_manager.deleteInfraction(infraction_id=infraction_id)
                try:
                    msg = await ctx.reply(
                    embed=Embed(
                        description=f"L'infraction `#{infraction_id}` a été supprimée",
                        color=self.bot.settings["defaultColors"]["confirmation"]
                    )
                )
                except:
                    msg = await ctx.send(
                    embed=Embed(
                        description=f"L'infraction `#{infraction_id}` a été supprimée",
                        color=self.bot.settings["defaultColors"]["confirmation"]
                    )
                )
                try: await msg.delete(delay=3)
                except: pass
            else:
                try: msg = await ctx.reply("L'infraction n'a pas été supprimée")
                except: msg = await ctx.send("L'infraction n'a pas été supprimée")
                try: await msg.delete(delay=3)
                except: pass

            # Delete messages
            try: await ctx.message.delete()
            except: pass
            try: await confirmation_message.delete()
            except: pass
            try: await message_response.delete()
            except: pass


        

def setup(bot:commands.Bot):
    bot.add_cog(RemoveInfraction(bot))
