import discord
from discord import client
from discord.ext import commands
from discord.ext.commands import Bot
from discord.utils import get

class Startup(commands.Cog):

    def __init__(self, client):
        self.client = client


    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.change_presence(status=discord.Status.online, activity=discord.Game("with the odds"))

async def setup(client):
    await client.add_cog(Startup(client))