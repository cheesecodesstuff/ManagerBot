from .testing import BotTesting

def setup(bot):
    bot.add_cog(BotTesting(bot))
