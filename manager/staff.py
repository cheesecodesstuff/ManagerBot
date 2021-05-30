from .core import ServerEnum, _is_staff, _cog_check, _tokens_missing, _ban_unban, _iamstaff, _get, _log, MiniContext
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
        """Shhhh... Secret staff command to gain access to the staff server"""
        return await _iamstaff(ctx)

    @commands.command()
    async def ban(self, ctx, bot: User, *, reason: Optional[str] = None):
        """Bans a bot from the list"""
        return await _ban_unban(ctx, bot, reason, True)

    @commands.command()
    async def unban(self, ctx, bot: User):
        """Unbans a bot from the list"""
        return await _ban_unban(ctx, bot, "", False)
    
    @commands.command()
    async def certify(self, ctx, bot: User):
        """Certifies a bot on the list"""
        return await _certify_uncertify(ctx, bot, True)
    
    @commands.command()
    async def uncertify(self, ctx, bot: User):
        """Uncertifies a bot on the list"""
        return await _certify_uncertify(ctx, bot, False)
        
        
    @commands.command()
    async def allowbot(self, ctx, bot: User):
        """Shhhhh.... secret command to allow adding a bot to the staff server"""
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
    async def on_message(self, message):
        # Anti log spam
        servers = await _get(message.guild.owner, self.bot, ["log_channel"])
        log_channel = servers.get("log_channel")
        if message.author.id != message.guild.me.id and message.channel.id == log_channel:
            await message.delete()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        servers = await _get(member.guild.owner, self.bot, ["staff", "testing", "test_botsrole", "test_staffrole", "main", "main_botsrole"])
        if member.bot:
            if member.guild.id == servers.get("main"):
                await member.add_roles(member.guild.get_role(servers.get("main_botsrole")))
                await _log(MiniContext(member, self.bot), f"Bot **{member.name}#{member.discriminator}** has joined the main server, hopefully after being properly tested...")
            elif member.guild.id == servers.get("testing"):
                await member.add_roles(member.guild.get_role(servers.get("test_botsrole")))
                await _log(MiniContext(member, self.bot), f"Bot **{member.name}#{member.discriminator}** has joined the testing server, good luck...")
            elif not self.whitelist.get(member.id) and member.guild.id == servers.get("staff"):
                await member.kick(reason = "Unauthorized Bot")
            else:
                del self.whitelist[member.id]
        else:
            if member.guild.id == servers.get("testing"):
                staff = await _is_staff(ctx, member.id, 2)
                if staff[0]:
                    await member.add_roles(member.guild.get_role(servers.get("test_staffrole")))
