from .core import ServerEnum, _is_staff, _cog_check, _tokens_missing
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
        staff = await _is_staff(ctx, ctx.author.id, 2)
        if not staff[0]:
            await ctx.author.send("You are not a Fates List Staff Member. You will hence be kicked from the staff server!")
            await ctx.author.kick()
            return
        servers = await ctx.bot.get_shared_api_tokens("fateslist-si")
        if not servers.get("ag_role"):
            await ctx.send(_token_missing("ag_role"))
        staff_ag = int(servers.get("ag_role"))
        await ctx.author.add_roles( ctx.guild.get_role(staff_ag), ctx.guild.get_role(int(staff[2].staff_id)) )
