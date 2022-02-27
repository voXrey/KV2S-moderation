from functools import wraps

def check_permissions(func):
    @wraps(func)
    async def inner(cog, ctx, *args, **kwargs):
        """
        Decorator to check if member has all permissions required to execute a command
        
        Parameters:
        cog (nextcord.ext.commands.Cog) : cog of the command
        ctx (nextcord.Context) : command's context
        """
        member_permissions = ctx.author.guild_permissions # get member's permissions
        member_permissions_strings = [permission[0] for permission in member_permissions if permission[1]] # get permissions name if member has this permission
        permissions_required = cog.command_info["permissions"] # get permissions required in the json

        result = all(elem in member_permissions_strings for elem in permissions_required) # check if all permissions required are in member's permissions
        if result: await func(cog, ctx, *args, **kwargs) # execute command if member have required permissions
        else:
            command_list = [f"`{permission_string}`" for permission_string in permissions_required]
            await ctx.reply(f"Vous n'avez pas la permission d'exécuter cette commande !\nLes permissions requises pour exécuter cette commande sont :\n{', '.join(command_list)}")
    return inner
