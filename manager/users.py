from .core import _cog_check, _request, ServerEnum, Status
from redbot.core import commands
from discord import Embed, User, Color
from http import HTTPStatus
from typing import Optional

class User(commands.Cog):
    """Commands made specifically for users to use"""
    
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
