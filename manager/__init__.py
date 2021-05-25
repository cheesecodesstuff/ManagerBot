from .testing import BotTesting
from .staff import Staff

def setup(bot):
    bot.add_cog(BotTesting(bot))
    bot.add_cog(Staff(bot))
