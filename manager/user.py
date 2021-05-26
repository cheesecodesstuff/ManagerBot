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
        """Gives bot devs the Bot Developer role"""
        res = await _request("GET", ctx, f"/api/users/{ctx.author.id}")
        if res[0] == 404:
            await ctx.send("You have not even logged in even once on Fates List!")
            return
    
        embed = Embed(title = "Roles Given", description = "These are the roles you have got")
    
        i = 1
        success, failed = 0, 0
        keys = (("bot_developer", "main_botdevrole", "You are not a bot developer"), ("certified_developer", "main_certdevrole", "You do not have any certified bots"))  # keep comment here for github
        for key in keys:
            role = key[0].replace('_', ' ').title()
            if not res[1][key[0]]:
                embed.add_field(name = role, value = f":X: Not going to give you {role} because: {key[2]}")
                failed += 1
                continue
            servers = await _get(ctx, ctx.bot, [key[1]])
            await ctx.author.add_roles(ctx.guild.get_role(servers.get(key[1])))
            embed.add_field(name = role, value = f":white_checkmark: Gave you the {role} role")
            success += 1
        
        embed.add_field(name = "Success", value = str(success))
        embed.add_field(name = "Failed", value = str(failed))
        await ctx.send(embed = embed)
