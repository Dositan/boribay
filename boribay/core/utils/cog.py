from discord.ext import commands


class Cog(commands.Cog, metaclass=commands.CogMeta):
    """The customized cog instance for Boribay.

    All cogs of this bot will be of this type.

    This class inherits from `discord.ext.commands.Cog`.
    """

    def __str__(self):
        return f'{self.icon} {self.__class__.__name__}'
