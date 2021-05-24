from redbot.core import commands
from redbot.core import Config
import aiohttp
from aiohttp_requests import requests
from pydantic import BaseModel
from aenum import IntEnum

class RequestFailed(Exception):
    def __init__(self, string):
        super.__init__(string)

async def _request(method, ctx, bot, url, **kwargs):
    fateslist_data = await bot.get_shared_api_tokens("fateslist")
    failed = []
    for k in ["manager", "rl", "site_url"]:
        if fateslist_data.get(k) is None:
            failed.append(k)
    if failed:
        await ctx.send(_token_missing(key = "fateslist", failed = failed))
        raise RequestFailed(" ".join(failed))
    if "headers" in kwargs.keys():
        headers = kwargs["headers"]
    else:
        headers = {}
    headers["Authorization"] = fateslist_data.get("manager")
    headers["FatesList-RateLimitBypass"] = fateslist_data.get("rl")
    headers["FL-API-Version"] = "2"
    f = eval(f"requests.{method.lower()}")
    res = await f(fateslist_data.get("site_url") + url, json = kwargs.get("json"), headers = headers, timeout = kwargs.get("timeout"))
    if res.status == 401:
        await ctx.send("**Request Failed**\nGiven API Keys are invalid! nPlease set the needed keys using `[p]set api fateslist manager,MANAGER_KEY rl,RATELIMIT_BYPASS_KEY site_url,SITE_URL`")
        raise RequestFailed("Invalid API Keys")
    res_json = await res.json()
    return res.status, res_json
   
# Copy this from Fates
class StaffMember(BaseModel):
    """Represents a staff member in Fates List""" 
    name: str
    id: int
    perm: int
    staff_id: int

class ServerEnum(IntEnum):
    TEST_SERVER = 0
    STAFF_SERVER = 1
    COMMON = 2

class Status(IntEnum):
    """Status object (See https://docs.fateslist.xyz/basics/basic-structures#status for more information)"""
    _init_ = 'value __doc__'
    unknown = 0, "Unknown"
    online = 1, "Online"
    offline = 2, "Offline"
    idle = 3, "Idle"
    dnd = 4, "Do Not Disturb"


def _tokens_missing(failed, key = "fateslist-si"): 
    if key == "fateslist-si":
        type = "server info"
        set = "testing,TESTING_SERVER_ID staff,STAFF_SERVER_ID log_channel,STAFF_LOGCHANNEL"
    elif key == "fateslist":
        type = "API Tokens"
        set = "manager,MANAGER_KEY rl,RATELIMIT_BYPASS_KEY site_url,SITE_URL"
    return f"**Error**\nPlease set {type} using `[p]set api {key} {set}`\n\n**Failed**\n{' '.join(failed)}"
    
async def _log(ctx, message):
    servers = await bot.get_shared_api_tokens("fateslist-si")
    log_channel = servers.get("log_channel")
    if not log_channel:
        await ctx.send(_token_missing(["log_channel"]))                                                              
    channel = ctx.bot.get_channel(int(log_channel))
    await channel.send(message)                 
                                   
async def _cog_check(ctx, bot, state: ServerEnum):
    """Creates a check for a cog"""
    servers = await bot.get_shared_api_tokens("fateslist-si")
    failed = []
    for k in ["testing", "staff"]:
        if not servers.get(k):
            failed.append(k)
    if not servers or failed:
        await ctx.send(_token_missing(failed))
        return False
    if state == ServerEnum.TEST_SERVER and ctx.guild.id != int(servers.get("testing")):
        await ctx.send("This command can only be used on the testing server")
        return False
    elif state == ServerEnum.STAFF_SERVER and ctx.guild.id != int(servers.get("staff")):
        await ctx.send("This command can only be used on the staff server")
        return False
    return True
