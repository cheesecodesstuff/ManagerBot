from redbot.core import commands

class Setup(commands.Cog):
    """Setup manager cog"""

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def setup(self, ctx):
        """Setup instructions"""
        await ctx.send(f"""
                This command was made in the case that something happens to me or if someone else gets control of Fates List. Like the rest of Fates List, we **do not support self hosting any part of our infrastucture (which is also very difficult).** Fates List is open source for auditing purposes and to gain trust, privacy and security for our users.

                **Setup Manager Bot**
                
                1. Run `{ctx.prefix}set api fateslist manager,MANAGER_KEY rl,RATELIMIT_BYPASS_KEY site_url,SITE_URL`
                2. Run `{ctx.prefix}set api fateslist-si testing,TESTING_SERVER_ID staff,STAFF_SERVER_ID log_channel,STAFF_LOGCHANNEL ag_role,STAFF_SERVER_GRANTED_ROLE`
                3. Install the manager cog using: `{ctx.prefix}cog install fates manager`
                
                It is recommended to install hider from https://github.com/Flame442/FlameCogs and hide uneeded commands especially from core. Unload all cogs other than downloader and remove third party cogs so they dont steal API Tokens
            """
        )
