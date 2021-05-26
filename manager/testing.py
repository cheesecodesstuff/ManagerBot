from .core import _cog_check, _request, _queue, _claim_unclaim_requeue, _approve_deny, ServerEnum, Status
from redbot.core import commands
from discord import Embed, User, Color
from http import HTTPStatus
from typing import Optional

class BotTesting(commands.Cog):
    """Commands for queueing, testing and approving bots"""
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await _cog_check(ctx, ServerEnum.TEST_SERVER)

    @commands.command(aliases=["q", "pending"])
    async def queue(self, ctx):
        """Get all bots in queue"""
        return await _queue(ctx)

    @commands.command()
    async def claim(self, ctx, bot: User):
        """Claims a bot. This is **REQUIRED**"""
        return await _claim_unclaim_requeue(ctx, bot, 0)
        
    @commands.command()
    async def unclaim(self, ctx, bot: User):
        """Unclaims a bot so other reviewers can test it"""
        return await _claim_unclaim_requeue(ctx, bot, 2)
    
    @commands.command()
    async def approve(self, ctx, bot: User, *, feedback: Optional[str] = None):
        """Approves a bot. You must claim the bot first"""
        return await _approve_deny(ctx, bot, feedback, True)

    @commands.command()
    async def deny(self, ctx, bot: User, *, feedback: Optional[str] = None):
        """Denies a bot. You must claim the bot first"""
        return await _approve_deny(ctx, bot, feedback, False)
