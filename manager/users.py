from .core import _cog_check, _request, _get, ServerEnum, Status
from redbot.core import commands
from discord import Embed, User, Color
from http import HTTPStatus
from typing import Optional

class User(commands.Cog):
    """Commands made specifically for users to use"""
    def __init__(self, bot):
        self.bot = bot
    
    async def cog_check(self, ctx): 
        return await _cog_check(ctx, ServerEnum.MAIN_SERVER)

    @commands.command()
    async def botdev(self, ctx):
        """Gives you the Bot Developer role"""
        res = _request("GET", ctx, f"/api/users/{ctx.author.id}")
        if res[0] == 404:
            await ctx.send("You have not even logged in even once on Fates List!")
            return
        if not res[1]["bot_developer"]:
            await ctx.send("You have no eligible bots (your bot is not verified and/or does not belong to you as a owner or extra owner)")
            return
        servers = await _get(ctx, ctx.bot, ["main_botdevrole"])
        await ctx.author.add_roles(ctx.guild.get_role(servers.get("main_botdevrole")))
        return await ctx.send("Gave you the role!")
