from .testing import BotTesting
from .staff import Staff
from .user import User

def setup(bot):
    bot.add_cog(BotTesting(bot))
    bot.add_cog(Staff(bot))
    bot.add_cog(User(bot))
