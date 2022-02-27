from functools import wraps

def check_permissions(func):
    @wraps(func)
    async def inner(cog, ctx, *args, **kwargs):
        member_permissions = ctx.author.guild_permissions
        member_permissions_strings = [permission[0] for permission in member_permissions if permission[1]]
        permissions_required = cog.bot.commands_info["commands"][cog.command_name]["permissions"]

        result = all(elem in member_permissions_strings for elem in permissions_required)
        if result: await func(cog, ctx, *args, **kwargs)
        else:
            command_list = [f"`{permission_string}`" for permission_string in permissions_required]
            await ctx.reply(f"Vous n'avez pas la permission d'exécuter cette commande !\nLes permissions requises pour exécuter cette commande sont :\n{', '.join(command_list)}")
    return inner
