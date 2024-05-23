import discord
from discord import client
from discord.ext import commands
from discord.ext.commands import Bot
from discord.utils import get
import random
import json
import os
import asyncio
import time

def _save():
    print(f"Saving amounts to {'amounts.json'}: {amounts}")
    with open('amounts.json', 'w') as f:
        json.dump(amounts, f)

amounts = {}

class Gambling(commands.Cog):
    def __init__(self, client):
       self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        global amounts
        if os.path.exists('amounts.json'):
            try:
                with open('amounts.json') as f:
                    amounts = json.load(f)
                    print("Loaded amounts from JSON: ", amounts)
            except json.JSONDecoder:
                print("Could not read the json")
                amounts = {}
        else:
            print("JSON file not found, initializing empty amounts")
            amounts = {}

    @commands.command()
    async def register(self, ctx):
        id = str(ctx.message.author.id)
        if id not in amounts:
            amounts[id] = 50
            await ctx.send("You now have an account with the Fizz Casino enjoy your stay and happy gambling.")
            _save()
        else:
            await ctx.send("You already have an account.")

    @commands.command()
    async def balance(self, ctx):
        id = str(ctx.message.author.id)
        if id in amounts:
            await ctx.send("You have {} Sheckles.".format(amounts[id]))
        else:
            await ctx.send("You do not have an account with the Fizz Casino")

    @commands.command()
    async def pay(self, ctx, amount: int, other: discord.Member):
        main_id = str(ctx.message.author.id)
        other_id = str(other.id)
        if main_id not in amounts:
            await ctx.send("You do not have an account with the Fizz Casino")
        elif other_id not in amounts:
            await ctx.send(f"<@{other.id}> doesn't have an account with the Fizz Casino")
        elif amounts[main_id] < amount:
            await ctx.send("You can't afford this transaction")
        else:
            amounts[main_id] -= amount
            amounts[other_id] += amount
            await ctx.send("Transaction complete")
        _save()

    @commands.command()
    async def coinflip(self, ctx, amount: int, other: discord.Member, choice):
        main_id = str(ctx.message.author.id)
        other_id = str(other.id)
        if choice == "h":
            player1 = "heads"
            player2 = "tails"
        else:
            player1 = "tails"
            player2 = "heads"
        if main_id not in amounts:
            await ctx.send("You do not have an account with the Fizz Casino")
        elif other_id not in amounts:
            await ctx.send(f"<@{other_id}> doesn't have an account with the Fizz Casino")
        elif amounts[main_id] < amount:
            await ctx.send("You can't afford this coinflip")
        elif amounts[other_id] < amount:
            await ctx.send(f"<@{other_id}> can't afford this coinflip")
        else:
            sent_message = await ctx.send(f"<@{ctx.message.author.id}> chose {player1}. Do you accept this coinflip? (yes/no)")
            number = 1
            while number == 1:
                try:
                    res = await self.client.wait_for(
                    "message",
                    check=lambda x: x.channel.id == ctx.channel.id
                    and other.id == x.author.id
                    and x.content.lower() == "yes"
                    or x.conetent.lower() == "no",
                    timeout = 10,
                    )
                    if res.content.lower() == "yes":
                        await ctx.send(f"<@{other_id}> has accepted the coinflip")
                        time.sleep(1)
                        if random.choice([0,1]) == 1:
                            embed = discord.Embed(title="Coinflip | Fizz Casino", description=f"The coin has landed **HEADS**")
                            await ctx.send(embed=embed)
                            if player1 == "heads":
                                await ctx.send(f"<@{main_id}> has won the coinflip")
                                amounts[main_id] += amount
                                amounts[other_id] -= amount
                            else:
                                await ctx.send(f"<@{other_id}> has won the coinflip")
                                amounts[main_id] -= amount
                                amounts[other_id] += amount
                        else:
                            embed = discord.Embed(title="Coinflip | Fizz Casino", description=f"The coin has landed **TAILS**")
                            await ctx.send(embed=embed)
                            if player1 == "tails":
                                await ctx.send(f"<@{main_id}> has won the coinflip")
                                amounts[main_id] += amount
                                amounts[other_id] -= amount
                            else:
                                await ctx.send(f"<@{other_id}> has won the coinflip")
                                amounts[main_id] -= amount
                                amounts[other_id] += amount

                    elif res.content.lower() == "no":
                        await ctx.send(f"<@{other_id}> has declined the coinflip")
                        number = 0
                except asyncio.TimeoutError:
                    number = 0
        _save()

async def setup(client):
    await client.add_cog(Gambling(client))