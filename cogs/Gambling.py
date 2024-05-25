import discord
from discord import client
from discord.ext import commands
from discord.ext.commands import Bot
from discord.utils import get
from discord.ui import Button, View
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

#Coinflip class

class CoinflipView(View):
    def __init__(self, ctx, main_id, other_id, amount):
        super().__init__(timeout=30)  # Timeout for the view
        self.ctx = ctx
        self.main_id = main_id
        self.other_id = other_id
        self.amount = amount
        self.result = None

    @discord.ui.button(label="Blue", style=discord.ButtonStyle.primary)
    async def blue_button(self, interaction: discord.Interaction, button: Button):
        await self.process_choice(interaction, "blue")

    @discord.ui.button(label="Red", style=discord.ButtonStyle.danger)
    async def red_button(self, interaction: discord.Interaction, button: Button):
        await self.process_choice(interaction, "red")

    async def process_choice(self, interaction: discord.Interaction, choice: str):
        if int(interaction.user.id) != int(self.other_id):
            await interaction.response.send_message("You are not the one accepting the coinflip!", ephemeral=True)
            return
        
        self.result = choice
        new_embed = discord.Embed(title="Coinflip | Fizz Casino", description=f"<@{self.other_id}> Has accepted! They have chosen **{self.result}**!", color=discord.Color.blue())
        await interaction.response.edit_message(embed=new_embed)
        self.stop()

    async def on_timeout(self):
        await self.ctx.send(f"{self.ctx.guild.get_member(self.other_id).mention} did not respond in time.")



class Gambling(commands.Cog):
    def __init__(self, client):
       self.client = client

    #Load money section

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

    #General Command Section for moneys

    @commands.hybrid_command()
    async def balance(self, ctx):
        id = str(ctx.message.author.id)
        if id not in amounts:
            amounts[id] = 50
        
        await ctx.send("You have {} Sheckles.".format(amounts[id]))

    @commands.hybrid_command()
    async def pay(self, ctx, amount: int, other: discord.Member):
        main_id = str(ctx.message.author.id)
        other_id = str(other.id)
        if main_id not in amounts:
            amounts[main_id] = 50
        if other_id not in amounts:
            amounts[other_id] = 50
        if amounts[main_id] < amount:
            await ctx.send("You can't afford this transaction")
        else:
            amounts[main_id] -= amount
            amounts[other_id] += amount
            await ctx.send("Transaction complete")
        _save()

    
    #Coinflip command section
    
    @commands.hybrid_command()
    async def coinflip(self, ctx, amount: int, opponent: discord.Member):
        main_id = str(ctx.message.author.id)
        other_id = str(opponent.id)
        
        if main_id not in amounts:
            amounts[main_id] = 50
        if other_id not in amounts:
            amounts[other_id] = 50
        
        if amounts[main_id] < amount:
            embed = discord.Embed(title="Coinflip | Fizz Casino", description=f"You can't afford this coinflip", color=discord.Color.red())
            await ctx.send(embed=embed)
            return
        elif amounts[other_id] < amount:
            embed = discord.Embed(title="Coinflip | Fizz Casino", description=f"<@{other_id}> can't afford this coinflip", color=discord.Color.red())
            await ctx.send(embed=embed)
            return
        else:
            embed = discord.Embed(title="Coinflip | Fizz Casino", description=f"<@{other_id}> You've been challenged to a coinflip for **{amount}** sheckles! Please pick a side if you wish to accept.", color=discord.Color.blue())
            view = CoinflipView(ctx, main_id, other_id, amount)
            msg = await ctx.send(embed=embed, view=view)
            await view.wait()
            
            if view.result:
                chosen_side = random.choice(["blue", "red"])
                time.sleep(3)
                if chosen_side == view.result:
                    newest_embed = discord.Embed(title="Coinflip | Fizz Casino", description=f"The coin had landed on **{chosen_side}**. <@{other_id}> won! They have earned **{amount*2}** sheckles!", color=discord.Color.blue())
                    amounts[main_id] -= amount
                    amounts[other_id] += amount
                else:
                    newest_embed = discord.Embed(title="Coinflip | Fizz Casino", description=f"The coin had landed on **{chosen_side}**. <@{main_id}> won! They have earned **{amount*2}** sheckles!", color=discord.Color.blue())
                    await msg.edit(embed=newest_embed)
                    amounts[main_id] += amount
                    amounts[other_id] -= amount

async def setup(client):
    await client.add_cog(Gambling(client))