from .core import _is_staff, _cog_check, _request, ServerEnum, Status
from redbot.core import commands
from discord import Embed

class BotTesting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await _cog_check(ctx, self.bot, ServerEnum.TEST_SERVER)

    @commands.command()
    async def queue(self, ctx):
        """Get all bots in queue"""
        queue_json = await _request("GET", ctx, self.bot, "/api/bots/admin/queue")
        embed = Embed(title = "Bots In Queue", description = "These are the bots in the Fates List Queue. Be sure to review them from top to bottom, ignoring Fates List bots")
        i = 1
        for bot in queue_json["bots"]:
            embed.add_field(name = f"{i}. {bot['username']}#{bot['disc']} ({bot['id']})", value = f"This bot has a status of {Status(bot['status']).__doc__}: [Invite Bot]({bot['meta']['invite']})")
        embed.set_thumbnail(url = str(ctx.guild.icon_url))
        return await ctx.send(embed = embed)
