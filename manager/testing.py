from .core import _cog_check, _request, _claim_unclaim_requeue, ServerEnum, Status
from redbot.core import commands
from discord import Embed, User, Color
from http import HTTPStatus

class BotTesting(commands.Cog):
    """Commands for queueing, testing and approving bots"""
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await _cog_check(ctx, ServerEnum.TEST_SERVER)

    @commands.command(aliases=["q", "pending"])
    async def queue(self, ctx):
        """Get all bots in queue"""
        queue = await _request("GET", ctx, "/api/bots/admin/queue")
        queue_json = queue[1]
        embed = Embed(title = "Bots In Queue", description = "These are the bots in the Fates List Queue. Be sure to review them from top to bottom, ignoring Fates List bots")
        i = 1
        for bot in queue_json["bots"]:
            embed.add_field(name = f"{i}. {bot['user']['username']}#{bot['user']['disc']} ({bot['user']['id']})", value = f"This bot has a status of **{Status(bot['user']['status']).__doc__}** and a prefix of **{bot['prefix']}** -> [Invite Bot]({bot['invite']})\n\n**Description:** {bot['description']}\n​")
            i += 1
        embed.add_field(name="Credits", value = "skylarr#6666 - For introducing me to redbot and hosting Fates List\nNotDraper#6666 - For helping me through a variety of bugs in the bot")
        embed.set_thumbnail(url = str(ctx.guild.icon_url))
        return await ctx.send(embed = embed)

    @commands.command()
    async def claim(self, ctx, bot: User):
        """Claims a bot. This is **REQUIRED**"""
        return await _claim_unclaim_requeue(ctx, bot, 0)
        
    @commands.command()
    async def unclaim(self, ctx, bot: User):
        """Unclaims a bot so other reviewers can test it"""
        return await _claim_unclaim_requeue(ctx, bot, 2)
    
