from redbot.core import commands
from redbot.core import Config
import aiohttp
from pydantic import BaseModel
from aenum import IntEnum
from discord import Embed, User, Color
from http import HTTPStatus
from typing import Optional, Union
from redbot.core.utils.menus import menu, prev_page, next_page, close_menu
from copy import deepcopy
import datetime

class RequestFailed(Exception):
    def __init__(self, string):
        super().__init__(string)

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
    async with aiohttp.ClientSession() as sess:
        f = getattr(sess, method.lower())
        async with f(fateslist_data.get("site_url") + url, json = kwargs.get("json"), headers = headers, timeout = kwargs.get("timeout")) as res:
            if res.status == 401:
                await ctx.send("**Request Failed**\nGiven API Keys are invalid! nPlease set the needed keys using `[p]set api fateslist manager,MANAGER_KEY rl,RATELIMIT_BYPASS_KEY site_url,SITE_URL`")
                raise RequestFailed("Invalid API Keys")
            elif res.status == 429:
                await ctx.send("**Request Failed**\nThis bot is being ratelimited by the Fates List API. Is your ratelimit bypass key correct?")
                raise RequestFailed("Ratelimited")
            elif res.status == 422:
                await ctx.send("**Request Failed**\nThis API Endpoint returned a 422. This usually means that either the bot or API must be updated and reloaded. Try asking the owners on the staff server to update the bot and restart the site.")
                raise RequestFailed(f"{url} returned 422")
            elif res.status == 500:
                await ctx.send("**Request Failed**\nThis API Endpoint returned a 500 (Internal Server Error). Please ask for support on the staff server, pinging the owners")
                raise RequestFailed(f"Internal Server Error at {url}")
            res_json = await res.json()
            return res.status, res_json
   
# Copy this from Fates
class StaffMember(BaseModel):
    """Represents a staff member in Fates List""" 
    name: str
    id: Union[str, int]
    perm: int
    staff_id: Union[str, int]

class MiniContext():
    """Mini Context to satisy some commands"""
    def __init__(self, member, bot):
        self.author = member
        self.bot = bot
        self.guild = member.guild

    async def send(self, *args, **kwargs):
        return await self.author.send(*args, **kwargs)
    async def kick(self, *args, **kwargs):
        return await self.author.kick(*args, **kwargs)
    async def ban(self, *args, **kwargs):
        return await self.author.ban(*args, **kwargs)

# Update with latest fates code
class ServerEnum(IntEnum):
    TEST_SERVER = 0
    STAFF_SERVER = 1
    MAIN_SERVER = 2
    TEST_STAFF_SERVER = 3
    COMMON = 4

class Status(IntEnum):
    """Status object (See https://docs.fateslist.xyz/basics/basic-structures#status for more information)"""
    _init_ = 'value __doc__'
    unknown = 0, "Unknown"
    online = 1, "Online"
    offline = 2, "Offline"
    idle = 3, "Idle"
    dnd = 4, "Do Not Disturb"

class UserState(IntEnum):
    _init_ = 'value __doc__'
    normal = 0, "Normal"
    global_ban = 1, "Global Ban"
    login_ban = 2, "Login Ban"
    pedit_ban = 3, "Profile Edit Ban"
    ddr_ban = 4, "Data Deletion Request Ban"
    
# end Fates code
    
async def _is_staff(ctx, user_id: int, min_perm: int = 2):
    res = await _request("GET", ctx, f"/api/admin/is_staff?user_id={user_id}&min_perm={min_perm}")
    res = res[1]
    return res["staff"], res["perm"], StaffMember(**res["sm"])

def _tokens_missing(failed, key = "fateslist-si"): 
    if key == "fateslist-si":
        type = "server info"
        set = "testing,TESTING_SERVER_ID staff,STAFF_SERVER_ID log_channel,STAFF_LOGCHANNEL ag_role,STAFF_SERVER_GRANTED_ROLE main,MAIN_SERVER_ID test_botsrole,TEST_SERVER_BOTSROLE main_botsrole,MAIN_SERVER_BOTSROLE test_staffrole,TEST_SERVER_STAFFROLE main_botdevrole,MAIN_SERVER_BOTDEVROLE main_certdevrole,MAIN_SERVER_CERTDEVROLE"
    elif key == "fateslist":
        type = "API Tokens"
        set = "manager,MANAGER_KEY rl,RATELIMIT_BYPASS_KEY site_url,SITE_URL"
    return f"**Error**\nPlease set {type} using `[p]set api {key} {set}`\n\n**Failed**\n{' '.join(failed)}"

async def _get(inform, bot, lst, intify: bool = True):
    servers = await bot.get_shared_api_tokens("fateslist-si")
    failed = []
    for key in lst:
        if not servers.get(key):
            failed.append(key)
        else:
            try:
                if intify:
                    servers[key] = int(servers[key])
            except:
                failed.append(key)
    if failed:       
        await inform.send(_tokens_missing(failed))
        raise ValueError(f"Too many missing keys! ({failed})")
    return servers

async def _log(ctx, message):
    servers = await _get(ctx.guild.owner, ctx.bot, ["log_channel"])
    log_channel = servers.get("log_channel")                                                   
    channel = ctx.bot.get_channel(log_channel)
    await channel.send(message)                 

async def _cog_check(ctx, state: ServerEnum):
    """Creates a check for a cog"""
    if ctx.message.content.lower().startswith(f"{ctx.prefix}help"):
        return True # Avoid the spam that is "This command can only be run in the XYZ server"
    servers = await _get(ctx, ctx.bot, ["testing", "staff", "main"])
    embed = None
    if state == ServerEnum.TEST_SERVER and ctx.guild.id != servers.get("testing"):
        embed = Embed(title = "Testing Server Only!", description = "This command can only be used on the testing server", color = Color.red())
    elif state == ServerEnum.STAFF_SERVER and ctx.guild.id != servers.get("staff"):
        embed = Embed(title = "Staff Server Only!", description = "This command can only be used on the staff server", color = Color.red())
    elif state == ServerEnum.MAIN_SERVER and ctx.guild.id != servers.get("main"):
        embed = Embed(title = "Main Server Only!", description = "This command can only be used on the main server", color = Color.red())
    elif state == ServerEnum.TEST_STAFF_SERVER and (ctx.guild.id != servers.get("staff") and ctx.guild.id != servers.get("testing")):
        embed = Embed(title = "Staff Or Testing Server Only!", description = "This command can only be used on the staff server or the testing server", color = Color.red())
    if embed:
        await ctx.send(embed = embed)
        return False
    return True

async def _queue(ctx):
    queue = await _request("GET", ctx, "/api/bots/admin/queue")
    queue_json = queue[1]
    base_embed = Embed(title = "Bots In Queue", description = "These are the bots in the Fates List Queue. Be sure to review them from top to bottom, ignoring Fates List bots")
    base_embed.add_field(name="Credits", value = "skylarr#6666 - For introducing me to redbot and hosting Fates List\nNotDraper#6666 - For helping me through a variety of bugs in the bot")
    base_embed.set_thumbnail(url = str(ctx.guild.icon_url))
    embeds = [] # List of queue bot embeds
    i, e = 1, 0 # i is global bot counter, e is local bot counter, always between 0 and 3
    for bot in queue_json["bots"]: # Get all bots in 5 different embeds based on base_embed
        if e == 3 or i == 1: # Check if we are locally at the next 4 sum (0, 1, 2, 3 is 4 bots) or if the global counter is 1 (first embed set)
            embed = deepcopy(base_embed)
            embeds.append(embed)
            e = 0
        embed.insert_field_at(e, name = f"{i}. {bot['user']['username']}#{bot['user']['disc']} ({bot['user']['id']})", value = f"This bot has a status of **{Status(bot['user']['status']).__doc__}** and a prefix of **{bot['prefix']}** -> [Invite Bot]({bot['invite']})\n\n**Description:** {bot['description']}\n​")
        i += 1
        e += 1
    if not embeds:
        embed = deepcopy(base_embed)
        embed.insert_field_at(0, name = "No Bots In Queue!", value = "There are no bots in queue! Just relax :)")
        return await ctx.send(embed = embed)
    return await menu(ctx, embeds, {"⏮️": prev_page, "❌": close_menu, "⏭️": next_page}, timeout = 45)

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
    elif op.endswith("e"):
        op = op[:-1]
    elif op.endswith("y"):
        op = op.replace("y", "i")
    if not res[1]["done"]:
        embed = Embed(title = f"{opt} Failed", description = f"This bot could not be {op.lower()}ed by you...", color = Color.red())
        embed.add_field(name = "Reason", value = res[1]["reason"])
        embed.add_field(name = "Status Code", value = f"{res[0]} ({HTTPStatus(res[0]).phrase})")
        await ctx.send(embed = embed)
        return
    embed = Embed(title = f"{op}ed", description = f"This bot has been {op.lower()}ed. {succ}. This is important")
    if res[1]["reason"]:
        embed.add_field(name = "Additional", value = res[1]["reason"])
    embed.add_field(name = "Status Code", value = f"{res[0]} ({HTTPStatus(res[0]).phrase})")
    await ctx.send(embed = embed)
    await _log(ctx, f"{target.name}#{target.discriminator} has been {op.lower()}ed by {ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id})")
    if kick:
        member = ctx.guild.get_member(target.id)
        if member.top_role.position >= ctx.me.top_role.position:
            await ctx.send("I could not kick this member as they have a higher role than me.")
            return
        await member.kick(reason = f"Kicked as bot {op.lower()}ed")
       
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

async def _certify_uncertify(ctx, bot: User, certify: bool):
    if not bot.bot:
        await ctx.send("That isn't a bot. Please make sure you are pinging a bot or specifying a Bot ID")
        return
    op = "Certify" if certify else "Uncertofu"
    certify_res = await _request("PATCH", ctx, f"/api/bots/admin/{bot.id}/certify", json = {"mod": str(ctx.author.id), "certify": certify, "reason": reason})
    return await _handle(ctx, bot, op, certify_res)

async def _profile(ctx, user):
    """Gets the users profile, sends a message and returns None if not found"""
    if user.bot:
        embed = Embed(title = "No Profile Found", description = "Bots can't *have* profiles", color = Color.red())
        await ctx.send(embed = embed)
        return None
    res = await _request("GET", ctx, f"/api/users/{user.id}")
    if res[0] == 404:
        embed = Embed(title = "No Profile Found", description = "You have not even logged in even once on Fates List!", color = Color.red())
        await ctx.send(embed = embed)
        return None
    return res[1]

class __PIDRecorder():
    """Internal function to record worker PIDs"""
    def __init__(self):
        self.pids = []
    def get(self, pid):
        try:
            return self.pids.index(pid) + 1
        except ValueError:
            self.pids.append(pid)
            self.pids.sort()
            return len(self.pids)

__pidrec = __PIDRecorder()
 
# usage: (_d, _h, _m, _s, _mils, _mics) = tdTuple(td)
def __tdTuple(td:datetime.timedelta) -> tuple:
    def _t(t, n):
        if t < n: return (t, 0)
        v = t//n
        return (t -  (v * n), v)
    (s, h) = _t(td.seconds, 3600)
    (s, m) = _t(s, 60)    
    return (td.days, h, m, s)

async def _blstats(ctx):
    try:
        res = await _request("GET", ctx, f"/api/blstats")
    except Exception as exc:
        res = [502, {"uptime": 0, "pid": 0, "up": False, "dup": False, "bot_count": "Unknown", "bot_count_total": "Unknown", "error": f"{type(exc).__name__}: {exc}"}]
    embed = Embed(title = "Bot List Stats", description = "Fates List Stats")
    upd = __tdTuple(datetime.timedelta(seconds = res[1]['uptime']))
    uptime = f"{upd[0]} days, {upd[1]} hours, {upd[2]} minutes, {upd[3]} seconds"
    embed.add_field(name = "Uptime", value = uptime)
    embed.add_field(name = "Worker PID", value = str(res[1]["pid"]))
    embed.add_field(name = "Recorded Worker", value = str(__pidrec.get(res[1]["pid"])))  
    embed.add_field(name = "UP?", value = str(res[1]["up"]))
    embed.add_field(name = "Discord UP (dup)?", value = str(res[1]["dup"]))
    embed.add_field(name = "Bot Count", value = str(res[1]["bot_count"]))
    embed.add_field(name = "Bot Count (Total)", value = str(res[1]["bot_count_total"]))
    embed.add_field(name = "Errors", value = res[1]["error"] if res[1].get("error") else "No errors fetching stats from API")
    return embed
