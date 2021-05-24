from .core import _is_staff, _cog_check, _request, ServerEnum
from redbot.core import commands

class BotTesting(commands.Cog):
    async def cog_check(self, ctx):
        return await _cog_check(ctx, self.bot, ServerEnum.TESTING_SERVER)

    @commands.command()
    async def testman(self, ctx):
        return await ctx.send("I work!!!")
