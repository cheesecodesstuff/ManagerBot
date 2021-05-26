from .core import ServerEnum, _is_staff, _cog_check, _tokens_missing, _ban_unban, _iamstaff
from redbot.core import commands
from discord import Embed, User, Color
from http import HTTPStatus
from typing import Optional
import asyncio

class Staff(commands.Cog):
    """Commands to handle the staff server"""
    def __init__(self, bot):
        self.bot = bot
        self.whitelist = {} # Staff Server Bot Protection
        
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

    @commands.command()
    async def whitelist(self, ctx, bot: User):
        staff = await _is_staff(ctx, ctx.author.id, 4)
        if not staff[0]:
            return await ctx.send("You cannot temporarily whitelist this member as you are not an admin")
        self.whitelist[bot.id] = True
        await ctx.send("Temporarily whitelisted for one minute")
        await asyncio.sleep(60)
        try:
            del self.whitelist[bot.id]
        except:
            pass
        await ctx.send("Unwhitelisted bot again")


    @commands.Cog.listener()
    async def on_member_join(self, member):
        servers = await ctx.bot.get_shared_api_tokens("fateslist-si")
        failed = []
        for key in ["staff", "testing", "test_botsrole", "test_staffrole", "main", "main_botsrole"]:
            if not servers.get(key):
                failed.append(key)
        if failed:       
            await member.guild.owner.send(_tokens_missing(failed))
            return
        if member.bot:
            if member.guild.id == servers.get("main"):
                await member.add_roles(member.guild.get_role(servers.get("main_botsrole")))
            elif member.guild.id == test_server:
                await member.add_roles(member.guild.get_role(test_botsrole))
            elif not self.whitelist.get(member.id):
                await member.kick(reason = "Unauthorized Bot")
            else:
                del self.whitelist[member.id]
        else:
            staff = is_staff(staff_roles, client.get_guild(main_server).get_member(member.id).roles, 2)
            if staff[0]:
                await member.add_roles(member.guild.get_role(test_staffrole))
