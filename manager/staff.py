from .core import ServerEnum, _is_staff, _cog_check, _tokens_missing, _ban_unban
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
            try:
                msg = "You are not a Fates List Staff Member. You will hence be kicked from the staff server!"
                await ctx.send(msg)
                await ctx.author.send(msg)
                await ctx.author.kick()
            except:
                await ctx.send("I've failed to kick this member. Staff, please kick this member now!")
            return
        servers = await ctx.bot.get_shared_api_tokens("fateslist-si")
        if not servers.get("ag_role"):
            await ctx.send(_tokens_missing(["ag_role"]))
            return
        staff_ag = int(servers.get("ag_role"))
        await ctx.author.add_roles( ctx.guild.get_role(staff_ag), ctx.guild.get_role(int(staff[2].staff_id)) )
        await ctx.send("Welcome home, master!")

    @commands.command()
    async def ban(self, ctx, bot: User, *, reason: Optional[str] = None):
        """Bans a bot from the list"""
        return await _ban_unban(ctx, bot, reason, True)
