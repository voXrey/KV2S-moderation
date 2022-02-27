import json

from core.decorators import check_permissions
from core.infractions_manager import infractions_manager
from nextcord.ext import commands

class EditInfraction(commands.Cog):
    command_name = "edit-infraction"
    
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
    async def edit_infraction(self, ctx:commands.Context, infraction_id:int, *, infraction_reason:str=None):
        # Get infraction
        infraction = infractions_manager.getInfraction(infraction_id=infraction_id)

        # If infraction not exists
        if infraction is None:
            msg = await ctx.reply("Cette infraction n'existe pas")
            try: await msg.delete(delay=3)
            except: pass

        # If infraction exists
        else:
            # Request confirmation
            confirmation_message = await ctx.reply(
                content="Êtes-vous sûr de vouloir modifier cette infraction ? (oui/non)",
                embed=await infraction.getSimpleEmbed(self.bot)
            )

            ## Wait confirmation
            def check(m): return (m.channel==ctx.channel) and (m.author == ctx.author)
            message_response = await self.bot.wait_for('message', check=check, timeout=120) # wait confirmation message
            
            response = message_response.content.lower()
            if response == "oui":
                infraction.reason = infraction_reason
                infractions_manager.editInfraction(infraction=infraction)
                msg = await ctx.reply(f"L'infraction `#{infraction_id}` a été modifiée")
                try: await msg.delete(delay=3)
                except: pass
            else:
                msg = await ctx.reply("L'infraction n'a pas été modifiée")
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
    bot.add_cog(EditInfraction(bot))
