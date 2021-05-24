from .core import _is_staff, _cog_check, _request, ServerEnum
from redbot.core import commands

class BotTesting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await _cog_check(ctx, self.bot, ServerEnum.TEST_SERVER)

    @commands.command()
    async def queue(self, ctx):
        """Get all bots in queue"""
        queue_json = await _request("GET", ctx, bot, "/api/queue")
        return await ctx.send(f"{queue_json}")
