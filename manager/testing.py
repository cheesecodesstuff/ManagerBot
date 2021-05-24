from .core import _cog_check, _request, ServerEnum, Status
from redbot.core import commands
from discord import Embed, Member, Color
from http import HTTPStatus

class BotTesting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await _cog_check(ctx, self.bot, ServerEnum.TEST_SERVER)

    @commands.command(aliases=["q", "pending"])
    async def queue(self, ctx):
        """Get all bots in queue"""
        queue_json = await _request("GET", ctx, self.bot, "/api/bots/admin/queue")[1]
        embed = Embed(title = "Bots In Queue", description = "These are the bots in the Fates List Queue. Be sure to review them from top to bottom, ignoring Fates List bots")
        i = 1
        for bot in queue_json["bots"]:
            embed.add_field(name = f"{i}. {bot['user']['username']}#{bot['user']['disc']} ({bot['user']['id']})", value = f"This bot has a status of **{Status(bot['user']['status']).__doc__}** and a prefix of **{bot['prefix']}** -> [Invite Bot]({bot['invite']})\n\n**Description:** {bot['description']}\n​")
            i += 1
        embed.add_field(name="Credits", value = "skylarr#6666 - For introducing me to redbot amd hosting Fates List\nNotDraper#6666 - For helping me through a variety of bugs in the bot")
        embed.set_thumbnail(url = str(ctx.guild.icon_url))
        return await ctx.send(embed = embed)

    @commands.command()
    async def claim(self, ctx, bot: Member):
        """Claims a bot. This requires you to be staff and is checked on our API"""
        if not bot.bot:
            await ctx.send("That isn't a bot. Please make sure you are pinging a bot")
            return
        claim_res = await _reauest("PATCH", ctx, self.bot, f"/api/bots/admin/{bot.id}/under_review", json = {"mod": str(ctx.author.id), "requeue": False})
        if not claim_res[1]["done"]:
            embed = Embed(title = "Claim Failed" description = f"This bot could not be claimed by you...", color = Color.red())
            embed.add_field(name = "Reason", value = claim_res[1]["reason"])
            embed.add_field(name = "Status Code", value = f"{claim_res[0]} ({HTTPStatus(claim_res[0]).phrase}")
            await ctx.send(embed = embed)
        embed = Embed(title = "Claimed", description = "This bot has been claimed. Use +unclaim when you don't want it anymore")
        await ctx.send(embed = embed)
