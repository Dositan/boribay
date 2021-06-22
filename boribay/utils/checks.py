from re import search

from discord.ext import commands


async def check_guild_perms(ctx, perms: dict, *, check=all):
    if await ctx.bot.is_owner(ctx.author):
        return True

    if not ctx.guild:
        return False

    resolved = ctx.author.guild_permissions
    return check(getattr(resolved, name, None) == value for name, value in perms.items())


def is_mod():
    """
    The method to check whether the message author has a moderator permissions.
    """
    async def predicate(ctx):
        return await check_guild_perms(ctx, {'manage_guild': True})

    return commands.check(predicate)


def beta_command():
    async def predicate(ctx):
        if ctx.author.id not in ctx.bot.owner_ids:
            raise commands.CheckFailure(
                f'Command `{ctx.command}` is currently in beta-testing'
                ' and cannot be executed now.'
            )
            return False
        return True

    return commands.check(predicate)


def is_valid_alias(name: str) -> bool:
    """A quick alias name validness check.

    Parameters
    ----------
    name : str
        The name of the alias to check.

    Returns
    -------
    bool
        True - if the name passed all checks, otherwise False.
    """
    return not bool(search(r'\s', name)) and name.isprintable()