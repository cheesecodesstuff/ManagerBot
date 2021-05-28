from .core import _cog_check, _request, _get, _profile, _blstats, ServerEnum, Status, UserState
from redbot.core import commands, tasks
from discord import Embed, User, Color, Member
from http import HTTPStatus
from typing import Optional

class User(commands.Cog):
    """Commands made specifically for users to use"""
    def __init__(self, bot):
        self.bot = bot
        self.statloop.start()
    
    @tasks.loop(minutes = 5)
    async def statloop(self):
        servers = await _get(self.bot.guilds[0].owner, self.bot, "log_channel")
        log_channel = servers.get("log_channel")
        ctx = MiniContext(self.bot.guilds[0].owner, self.bot)
        stats = await _blstats(ctx)
        channel = self.bot.get_channel(log_channel)
        await channel.send(embed = embed)
    
    def cog_unload(self):
        self.statloop.cancel()
    
    async def cog_check(self, ctx):
        if ctx.command.name in ("roles",):
            return await _cog_check(ctx, ServerEnum.MAIN_SERVER)
        return await _cog_check(ctx, ServerEnum.COMMON)

    @commands.command(aliases=["botdev", "certdev", "giveroles"])
    async def roles(self, ctx, target: Optional[Member] = None):
        """Gives bot devs their roles. **MAIN SERVER ONLY**"""
        target = target if target else ctx.author
        profile = await _profile(ctx, target)
        if not profile:
            return 
        
        embed = Embed(title = "Roles Given", description = "These are the roles you have got on Fates List", color = Color.blue())
    
        i = 1
        success, failed = 0, 0
        keys = (("bot_developer", "main_botdevrole", "You are not a bot developer"), ("certified_developer", "main_certdevrole", "You do not have any certified bots"))  # keep comment here for github
        for key in keys:
            role = key[0].replace('_', ' ').title()
            if not profile[key[0]]:
                embed.add_field(name = role, value = f":x: Not going to give you the {role} role because: *{key[2]}*")
                failed += 1
                continue
            servers = await _get(ctx, ctx.bot, [key[1]])
            await target.add_roles(ctx.guild.get_role(servers.get(key[1])))
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

    @commands.command()
    async def stats(self, ctx):
        embed = await _blstats(ctx)
        await ctx.send(embed = embed)
    
    @commands.command()
    async def profile(self, ctx, user: Optional[User] = None):
        """Gets a users profile (Not yet done)"""
        target = user if user else ctx.author
        profile = await _profile(ctx, target)
        if not profile:
            return
        embed = Embed(title = f"{target}'s Profile", description = "Here is your profile")
        
        # Base fields
        embed.add_field(name = "User ID", value = profile['id'])
        embed.add_field(name = "Username", value = profile['username'])
        embed.add_field(name = "Discriminator/Tag", value = profile['disc'])
        embed.add_field(name = "Avatar", value = profile['avatar'])
        embed.add_field(name = "Description", value = profile['profile']['description'])
        embed.add_field(name = "Defunct", value = profile['defunct'])
        embed.add_field(name = "Status", value = f"{profile['status']} ({Status(profile['status']).__doc__})")
        embed.add_field(name = "State", value = f"{profile['profile']['state']} ({UserState(profile['profile']['state']).__doc__})")
        embed.add_field(name = "CSS", value = profile['profile']['css'] if profile['profile']['css'] else "No custom user CSS set")
        
        await ctx.send(embed = embed)
