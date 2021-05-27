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

    @commands.command(aliases=["botdev", "certdev", "giveroles"])
    async def roles(self, ctx):
        """Gives bot devs their roles"""
        
        res = await _request("GET", ctx, f"/api/users/{ctx.author.id}")
        if res[0] == 404:
            embed = Embed(title = "No Profile Found", description = "You have not even logged in even once on Fates List!", color = Color.red())
            await ctx.send(embed = embed)
            return
    
        embed = Embed(title = "Roles Given", description = "These are the roles you have got on Fates List", color = Color.blue())
    
        i = 1
        success, failed = 0, 0
        keys = (("bot_developer", "main_botdevrole", "You are not a bot developer"), ("certified_developer", "main_certdevrole", "You do not have any certified bots"))  # keep comment here for github
        for key in keys:
            role = key[0].replace('_', ' ').title()
            if not res[1][key[0]]:
                embed.add_field(name = role, value = f":x: Not going to give you the {role} role because: *{key[2]}*")
                failed += 1
                continue
            servers = await _get(ctx, ctx.bot, [key[1]])
            await ctx.author.add_roles(ctx.guild.get_role(servers.get(key[1])))
            embed.add_field(name = role, value = f":white_check_mark: Gave you the {role} role")
            success += 1
        
        embed.add_field(name = "Success", value = str(success))
        embed.add_field(name = "Failed", value = str(failed))
        await ctx.send(embed = embed)

    @commands.command()
    async def catid(self, ctx):
        """Returns the category ID of a channel"""
        if ctx.channel.category: 
            return await ctx.send(str(ctx.channel.category.id)) 
        return await ctx.send("No category attached to this channel")  
