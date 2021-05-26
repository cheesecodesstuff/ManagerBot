from redbot.core import commands
from redbot.core import Config
import aiohttp
from aiohttp_requests import requests
from pydantic import BaseModel
from aenum import IntEnum
from discord import Embed, User, Color
from http import HTTPStatus
from typing import Optional, Union

class RequestFailed(Exception):
    def __init__(self, string):
        super.__init__(string)

async def _request(method, ctx, url, **kwargs):
    fateslist_data = await ctx.bot.get_shared_api_tokens("fateslist")
    failed = []
    for k in ["manager", "rl", "site_url"]:
        if fateslist_data.get(k) is None:
            failed.append(k)
    if failed:
        await ctx.send(_tokens_missing(key = "fateslist", failed = failed))
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
    id: Union[str, int]
    perm: int
    staff_id: Union[str, int]

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

async def _is_staff(ctx, user_id: int, min_perm: int = 2):
    res = await _request("GET", ctx, f"/api/admin/is_staff?user_id={user_id}&min_perm={min_perm}")
    res = res[1]
    return res["staff"], res["perm"], StaffMember(**res["sm"])

def _tokens_missing(failed, key = "fateslist-si"): 
    if key == "fateslist-si":
        type = "server info"
        set = "testing,TESTING_SERVER_ID staff,STAFF_SERVER_ID log_channel,STAFF_LOGCHANNEL ag_role,STAFF_SERVER_GRANTED_ROLE main,MAIN_SERVER_ID test_botsrole,TEST_SERVER_BOTSROLE main_botsrole,MAIN_SERVER_BOTSROLE test_staffrole,TEST_SERVER_STAFFROLE"
    elif key == "fateslist":
        type = "API Tokens"
        set = "manager,MANAGER_KEY rl,RATELIMIT_BYPASS_KEY site_url,SITE_URL"
    return f"**Error**\nPlease set {type} using `[p]set api {key} {set}`\n\n**Failed**\n{' '.join(failed)}"
    
async def _log(ctx, message):
    servers = await ctx.bot.get_shared_api_tokens("fateslist-si")
    log_channel = servers.get("log_channel")
    if not log_channel:
        await ctx.send(_tokens_missing(["log_channel"]))                                                              
    channel = ctx.bot.get_channel(int(log_channel))
    await channel.send(message)                 
                                   
async def _cog_check(ctx, state: ServerEnum):
    """Creates a check for a cog"""
    if ctx.message.content.lower().startswith(f"{ctx.prefix}help"):
        return True # Avoid the spam that is "This command can only be run in the XYZ server"
    servers = await ctx.bot.get_shared_api_tokens("fateslist-si")
    failed = []
    for k in ["testing", "staff"]:
        if not servers.get(k):
            failed.append(k)
    if not servers or failed:
        await ctx.send(_tokens_missing(failed))
        return False
    if state == ServerEnum.TEST_SERVER and ctx.guild.id != int(servers.get("testing")):
        embed = Embed(title = "Testing Server Only!", description = "This command can only be used on the testing server", color = Color.red())
        await ctx.send(embed = embed)
        return False
    elif state == ServerEnum.STAFF_SERVER and ctx.guild.id != int(servers.get("staff")):
        embed = Embed(title = "Staff Server Only!", description = "This command can only be used on the staff server", color = Color.red())
        await ctx.send(embed = embed)
        return False
    return True

async def _queue(ctx):
    queue = await _request("GET", ctx, "/api/bots/admin/queue")
    queue_json = queue[1]
    embed = Embed(title = "Bots In Queue", description = "These are the bots in the Fates List Queue. Be sure to review them from top to bottom, ignoring Fates List bots")
    i = 1
    for bot in queue_json["bots"]:
        embed.add_field(name = f"{i}. {bot['user']['username']}#{bot['user']['disc']} ({bot['user']['id']})", value = f"This bot has a status of **{Status(bot['user']['status']).__doc__}** and a prefix of **{bot['prefix']}** -> [Invite Bot]({bot['invite']})\n\n**Description:** {bot['description']}\n​")
        i += 1
    embed.add_field(name="Credits", value = "skylarr#6666 - For introducing me to redbot and hosting Fates List\nNotDraper#6666 - For helping me through a variety of bugs in the bot")
    embed.set_thumbnail(url = str(ctx.guild.icon_url))
    return await ctx.send(embed = embed)

async def _iamstaff(ctx):
    staff = await _is_staff(ctx, ctx.author.id, 2)
    if not staff[0]:
        try:
            msg = "You are not a Fates List Staff Member. You will hence be kicked from the staff server!"
            await ctx.send(msg)
            await ctx.author.send(msg)
            await ctx.author.kick()
        except:
            await ctx.send("I've failed to kick this member. Staff, please kick this member now!")
        return
    servers = await ctx.bot.get_shared_api_tokens("fateslist-si")
    if not servers.get("ag_role"):
        await ctx.send(_tokens_missing(["ag_role"]))
        return
    staff_ag = int(servers.get("ag_role"))
    await ctx.author.add_roles( ctx.guild.get_role(staff_ag), ctx.guild.get_role(int(staff[2].staff_id)) )
    await ctx.send("Welcome home, master!")

async def _handle(ctx, target: User, op: str, res: dict, succ = "Feel free to relax", kick: Optional[bool] = False):
    opt = op
    if op.endswith("n"):
        op += "n" # Double n
    if not res[1]["done"]:
        embed = Embed(title = f"{opt} Failed", description = f"This bot could not be {op.replace('y', 'i').lower()}ed by you...", color = Color.red())
        embed.add_field(name = "Reason", value = res[1]["reason"])
        embed.add_field(name = "Status Code", value = f"{res[0]} ({HTTPStatus(res[0]).phrase})")
        await ctx.send(embed = embed)
        return
    embed = Embed(title = f"{op.replace('y', 'i')}ed", description = f"This bot has been {op.replace('y', 'i').lower()}ed. {succ}. This is important")
    if res[1]["reason"]:
        embed.add_field(name = "Additional", value = res[1]["reason"])
    embed.add_field(name = "Status Code", value = f"{res[0]} ({HTTPStatus(res[0]).phrase})")
    await ctx.send(embed = embed)
    await _log(ctx, f"{target.name}#{target.discriminator} has been {op.replace('y', 'i').lower()}ed by {ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id})")
    if kick:
        member = ctx.guild.get_member(target.id)
        if member.top_role.position >= ctx.me.top_role.position:
            await ctx.send("I could not kick this member as they have a higher role than me.")
            return
        await member.kick(reason = f"Kicked as bot {op.replace('y', 'i').lower()}ed")
       
# TODO: Put this in core as it will be used in other places
async def _claim_unclaim_requeue(ctx, bot: User, t: int):
    """Claims, unclaims or requeues a bot, takes integer t with either 0 for claim, 1 for requeue (not yet done) or 2 for unclaim"""
    if t == 0:
        op = "Claim" # Action
        succ = "Use +unclaim when you don't want it anymore" # Success message
    elif t == 2:
        op = "Unclaim"
        succ = "Use +claim to start retesting the bot." 
    if not bot.bot:
        await ctx.send("That isn't a bot. Please make sure you are pinging a bot or specifying a Bot ID")
        return
    claim_res = await _request("PATCH", ctx, f"/api/bots/admin/{bot.id}/under_review", json = {"mod": str(ctx.author.id), "requeue": t})
    return await _handle(ctx, bot, op, claim_res, succ)
    
async def _approve_deny(ctx, bot: User, feedback: str, approve: bool):
    if not bot.bot:
        await ctx.send("That isn't a bot. Please make sure you are pinging a bot or specifying a Bot ID")
        return
    op = "Approve" if approve else "Deny"
    approve_res = await _request("PATCH", ctx, f"/api/bots/admin/{bot.id}/queue", json = {"mod": str(ctx.author.id), "approve": approve, "feedback": feedback})
    return await _handle(ctx, bot, op, approve_res, kick = True)

async def _ban_unban(ctx, bot: User, reason: str, ban: bool):
    if not bot.bot:
        await ctx.send("That isn't a bot. Please make sure you are pinging a bot or specifying a Bot ID")
        return
    op = "Ban" if ban else "Unban"
    ban_res = await _request("PATCH", ctx, f"/api/bots/admin/{bot.id}/ban", json = {"mod": str(ctx.author.id), "ban": ban, "reason": reason})
    return await _handle(ctx, bot, op, ban_res)
