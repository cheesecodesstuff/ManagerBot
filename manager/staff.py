from .core import ServerEnum, _is_staff, _cog_check, _tokens_missing, _ban_unban, _iamstaff
from redbot.core import commands
from discord import Embed, User, Color
from http import HTTPStatus
from typing import Optional

class Staff(commands.Cog):
    """Commands to handle staff on the staff server"""
    def __init__(self, bot):
        self.bot = bot
        
    async def cog_check(self, ctx):
        return await _cog_check(ctx, ServerEnum.STAFF_SERVER)
    
    @commands.command(aliases=["ias", "imstaff", "is"])
    async def iamstaff(self, ctx):
        return await _iamstaff(ctx)

    @commands.command()
    async def ban(self, ctx, bot: User, *, reason: Optional[str] = None):
        """Bans a bot from the list"""
        return await _ban_unban(ctx, bot, reason, True)

    @commands.command()
    async def unban(self, ctx, bot: User):
        """unban a bot from the list"""
        return await _ban_unban(ctx, bot, "", False)
