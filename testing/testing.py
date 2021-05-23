from redbot.core import commands
from redbot.core import Config
import aiohttp
from aiohttp_requests import requests
from pydantic import BaseModel

class BotTesting(commands.Cog):
    def __init__(self):
        self.config = Config.get_conf(self, identifier=101010101018382847473829)
        default_global = {
            "site_url": "https://fateslist.xyz",
            "manager_key": None,
            "ratelimit_bypass_key": None
        }
        self.config.register_global(**default_global)

    async def _request(self, method, url, **kwargs):
        manager_key = self.config.manager_key()
        ratelimit_bypass_key = self.config.ratelimit_bypass_key()
        site_url = self.config.site_url()
        if "headers" in kwargs.keys():
            headers = kwargs["headers"]
        else:
            headers = {}
        headers["Authorization"] = manager_key
        headers["FatesList-RateLimitBypass"] = ratelimit_bypass_key
        f = eval(f"requests.{method.lower()}")
        return await f(url = site_url + url, json = kwargs.get("json"), headers = headers, timeout = kwargs.get("timeout"))
   
    # Copy this from Fates
    class StaffMember(BaseModel):
        """Represents a staff member in Fates List""" 
        name: str
        id: int
        perm: int
        staff_id: int

    async def _is_staff(self, id, min_perm):
        json = (await self._requests("GET", f"/api/admin/is_staff?user_id={id}&min_perm={min_perm}")).json()
        return [json["staff"], json["perm"], self.StaffMember(**json["sm"])]
