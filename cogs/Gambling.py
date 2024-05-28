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

def deal_card(deck):
    card = random.choice(list(deck.keys()))
    value = deck.pop(card)
    return card, value

def calculate_hand_value(hand):
    value = sum(hand.values())
    num_aces = sum(1 for card in hand if card[0] == 'A')
    while value > 21 and num_aces:
        value -= 10
        num_aces -= 1
    return value

deckDict = {'Ah':'<:Ah:1244289577053851759>', 'Ad':'<:Ad:1244289575745228894>', 'As':'<:As:1244289573605867551>', 'Ac':'<:Ac:1244289574428217486>',
            'Kh':'<:Kh:1244289715801427998>', 'Kd':'<:Kd:1244289714790465587>', 'Ks':'<:Ks:1244289712219230289>', 'Kc':'<:Kc:1244289713532309586>',
            'Qh':'<:Qh:1244289763046068375>', 'Qd':'<:Qd:1244289761875853393>', 'Qs':'<:Qs:1244289759061475400>', 'Qc':'<:Qc:1244289759984095344>',
            'Jh':'<:Jh:1244289673489289268>', 'Jd':'<:Jd:1244289686357278821>', 'Js':'<:Js:1244289672608354406>', 'Jc':'<:Jc:1244289687628021910>',
            '10h':'<:10h:1244289537903951873>', '10d':'<:10d:1244289537115557909>', '10s':'<:10s:1244289534884053143>', '10c':'<:10c:1244289536079691786>',
            '9h':'<:9h:1244289511748407529>', '9d':'<:9d:1244289509877743707>', '9s':'<:9s:1244289507956756583>', '9c':'<:9c:1244289508971909121>',
            '8h':'<:8h:1244289420354519101>', '8d':'<:8d:1244289419150753842>', '8s':'<:8s:1244289416680177757>', '8c':'<:8c:1244289417930215494>',
            '7h':'<:7h:1244289283624407040>', '7d':'<:7d:1244289384954462319>', '7s':'<:7s:1244289397063422039>', '7c':'<:7c:1244289279941935197>',
            '6h':'<:6h:1244289275902693427>', '6d':'<:6d:1244289275256897607>', '6s':'<:6s:1244289358811500686>', '6c':'<:6c:1244289274191286383>',
            '5h':'<:5h:1244289272060710922>', '5d':'<:5d:1244289271079370823>', '5s':'<:5s:1244289272786452541>', '5c':'<:5c:1244289270147973160>',
            '4h':'<:4h:1244289222525976617>', '4d':'<:4d:1244289223876673536>', '4s':'<:4s:1244070752076959876>', '4c':'<:4c:1244289196043010199>',
            '3h':'<:3h:1244289173024800819>', '3d':'<:3d:1244289149448749107>', '3s':'<:3s:1244289182067855411>', '3c':'<:3c:1244070756917444648>',
            '2h':'<:2h:1244070755151646880>', '2d':'<:2d:1244070754325364818>', '2s':'<:2s:1244070756061548604>', '2c':'<:2c:1244070752983191593>'
            }

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
        await self.ctx.send(f"<@{self.other_id}> did not respond in time.")


class BlackjackView(View):
    def __init__(self, ctx, main_id, amount):
        super().__init__(timeout=90)  # Timeout for the view
        self.ctx = ctx
        self.main_id = main_id
        self.amount = amount
        self.result = None
    
        self.blackjackDeck = {
                            'Ah':11, 'Ad':11, 'As':11, 'Ac':11,
                            'Kh':10, 'Kd':10, 'Ks':10, 'Kc':10,
                            'Qh':10, 'Qd':10, 'Qs':10, 'Qc':10,
                            'Jh':10, 'Jd':10, 'Js':10, 'Jc':10,
                            '10h':10, '10d':10, '10s':10, '10c':10,
                            '9h':9, '9d':9, '9s':9, '9c':9,
                            '8h':8, '8d':8, '8s':8, '8c':8,
                            '7h':7, '7d':7, '7s':7, '7c':7,
                            '6h':6, '6d':6, '6s':6, '6c':6,
                            '5h':5, '5d':5, '5s':5, '5c':5,
                            '4h':4, '4d':4, '4s':4, '4c':4,
                            '3h':3, '3d':3, '3s':3, '3c':3,
                            '2h':2, '2d':2, '2s':2, '2c':2
                            }

        self.dealerHand = {}
        self.playerMainHand = {}

        for _ in range(2):
                card, value = deal_card(self.blackjackDeck)
                self.playerMainHand[card] = value
                card, value = deal_card(self.blackjackDeck)
                self.dealerHand[card] = value

        self.dealerHandStr = " ".join([deckDict[card] for card in self.dealerHand])
        self.dealerHandStrHidden = " ".join([deckDict[card]])
        self.playerHandMainStr = " ".join([deckDict[card] for card in self.playerMainHand])

        self.embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStrHidden}<:blank:1244303337315369073>\n\nPlayer: {self.playerHandMainStr}", color=discord.Color.blue())
        
        playerMainCurrentValue = calculate_hand_value(self.playerMainHand)
        delearCurrentValue = calculate_hand_value(self.dealerHand)
        
        if(playerMainCurrentValue == 21):
            if(delearCurrentValue != 21):
                payout = round(self.amount*3/2)
                self.embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStr}\n\nPlayer: {self.playerHandMainStr} \n\nYou got blackjack! You've been paid out **{payout}** chips!", color=discord.Color.gold())
                amounts[self.main_id] += payout+self.amount
            else:
                self.embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStr}\n\nPlayer: {self.playerHandMainStr} \n\nYou both got blackjack! You've recieved your chips back.", color=discord.Color.blue())
                amounts[self.main_id] += self.amount
            self.stop()
        elif(delearCurrentValue == 21):
            self.embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStr}\n\nPlayer: {self.playerHandMainStr} \n\nSorry, the dealer got blackjack, you lost.", color=discord.Color.red())
            self.stop()

    def is_soft_17(self, hand):
        value = sum(hand.values())
        return value == 17 and any(card.startswith('A') and hand[card] == 11 for card in hand)
    
    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def green_button(self, interaction: discord.Interaction, button: Button):
        await self.process_choice(interaction, "hit")
    @discord.ui.button(label="Stand", style=discord.ButtonStyle.grey)
    async def grey_button(self, interaction: discord.Interaction, button: Button):
        await self.process_choice(interaction, "stand")
    @discord.ui.button(label="Double", style=discord.ButtonStyle.red)
    async def red_button(self, interaction: discord.Interaction, button: Button):
        await self.process_choice(interaction, "double")
    @discord.ui.button(label="Split", style=discord.ButtonStyle.blurple)
    async def blurple_button(self, interaction: discord.Interaction, button: Button):
        await self.process_choice(interaction, "split")
    async def process_choice(self, interaction: discord.Interaction, choice: str):
        if int(interaction.user.id) != int(self.main_id):
            await interaction.response.send_message("You are not the one playing!", ephemeral=True)
            return
        self.result = choice
        if(self.result == "hit"):
            card, value = deal_card(self.blackjackDeck)
            self.playerMainHand[card] = value
            self.playerHandMainStr += f" {deckDict[card]}" 
            playerMainCurrentValue = calculate_hand_value(self.playerMainHand)
            if(playerMainCurrentValue > 21):
                new_embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStrHidden}<:blank:1244303337315369073>\n\nPlayer: {self.playerHandMainStr}\n\nYou **BUSTED** and have lost your chips.", color=discord.Color.red())
                self.stop()
            else:
                new_embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStrHidden}<:blank:1244303337315369073>\n\nPlayer: {self.playerHandMainStr}", color=discord.Color.blue())
        elif(self.result == "stand"):
            new_embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStr}\n\nPlayer: {self.playerHandMainStr}", color=discord.Color.blue())
            dealerCurrentValue = calculate_hand_value(self.dealerHand)
            playerMainCurrentValue = calculate_hand_value(self.playerMainHand)
            while(dealerCurrentValue < 17 | self.is_soft_17(self.dealerHand)):
                card, value = deal_card(self.blackjackDeck)
                self.dealerHand[card] = value
                self.dealerHandStr += f" {deckDict[card]}"
                dealerCurrentValue = calculate_hand_value(self.dealerHand)
                new_embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStr}\n\nPlayer: {self.playerHandMainStr}", color=discord.Color.blue())
            dealerCurrentValue = calculate_hand_value(self.dealerHand)
            if(dealerCurrentValue < playerMainCurrentValue or dealerCurrentValue > 21):
                new_embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStr}\n\nPlayer: {self.playerHandMainStr}\n\nCongratulations you **WON** you've been paid out **{self.amount}** chips!", color=discord.Color.green())
                self.stop()
            elif(dealerCurrentValue > playerMainCurrentValue):
                new_embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStr}\n\nPlayer: {self.playerHandMainStr}\n\nYou **LOST** and have lost your chips.", color=discord.Color.red())
                self.stop()
            else:
                new_embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStr}\n\nPlayer: {self.playerHandMainStr}\n\nYou **TIED** and have recieved your chips back.", color=discord.Color.blue())
                self.stop()
        elif(self.result == "double"):
            card, value = deal_card(self.blackjackDeck)
            self.playerMainHand[card] = value
            self.playerHandMainStr += f" {deckDict[card]}"
            playerMainCurrentValue = calculate_hand_value(self.playerMainHand)
            if(playerMainCurrentValue > 21):
                new_embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStrHidden}<:blank:1244303337315369073>\n\nPlayer: {self.playerHandMainStr}\n\nYou **BUSTED** and have lost your chips.", color=discord.Color.red())
                self.stop()
            else:
                new_embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStr}\n\nPlayer: {self.playerHandMainStr}", color=discord.Color.blue())
                dealerCurrentValue = calculate_hand_value(self.dealerHand)
                while(dealerCurrentValue < 17 or self.is_soft_17(self.dealerHand)):
                    card, value = deal_card(self.blackjackDeck)
                    self.dealerHand[card] = value
                    self.dealerHandStr += f" {deckDict[card]}"
                    dealerCurrentValue = calculate_hand_value(self.dealerHand)
                    new_embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStr}\n\nPlayer: {self.playerHandMainStr}", color=discord.Color.blue())
                dealerCurrentValue = calculate_hand_value(self.dealerHand)
                if(dealerCurrentValue < playerMainCurrentValue or dealerCurrentValue > 21):
                    new_embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStr}\n\nPlayer: {self.playerHandMainStr}\n\nCongratulations you **WON** you've been paid out **{self.amount*2}** chips!", color=discord.Color.green())
                    print(dealerCurrentValue)
                    self.stop()
                elif(dealerCurrentValue > playerMainCurrentValue):
                    new_embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStr}\n\nPlayer: {self.playerHandMainStr}\n\nYou **LOST** and have lost your chips.", color=discord.Color.red())
                    self.stop()
                else:
                    new_embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStr}\n\nPlayer: {self.playerHandMainStr}\n\nYou **TIED** and have recieved your chips back.", color=discord.Color.blue())
                    self.stop()
        
        await interaction.response.edit_message(embed=new_embed)
    async def on_timeout(self):
        amounts[self.main_id] += self.amount
        await self.ctx.send(f"<@{self.main_id}> did not respond in time, you have been refunded your chips.")
        


class Gambling(commands.Cog):
    def __init__(self, client):
       self.client = client

    #Load money section

class Gambling(commands.Cog):
    def __init__(self, client):
       self.client = client

    def cog_load(self):
        global amounts
        if os.path.exists('amounts.json'):
            try:
                with open('amounts.json') as f:
                    amounts = json.load(f)
                    print("Loaded amounts from JSON: ", amounts)
            except json.JSONDecodeError:
                print("Could not read the JSON file")
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
            _save()
        
        await ctx.send("You have {} chips.".format(amounts[id]))
        
        
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
            await ctx.send("You've successfully sent {amount} chips to <@{other_id}>")
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
            embed = discord.Embed(title="Coinflip | Fizz Casino", description=f"<@{other_id}> You've been challenged to a coinflip for **{amount}** chips!\nPlease pick a side if you wish to accept.", color=discord.Color.blue())
            view = CoinflipView(ctx, main_id, other_id, amount)
            msg = await ctx.send(embed=embed, view=view)
            await view.wait()
             
            if view.result:
                chosen_side = random.choice(["blue", "red"])
                asyncio.create_task(self.delayed_edit_coinflip(ctx, msg, main_id, other_id, amount, chosen_side, view.result))
            
    async def delayed_edit_coinflip(self, ctx, msg, main_id, other_id, amount, chosen_side, result):
        await asyncio.sleep(3)
        if chosen_side == result:
            newest_embed = discord.Embed(title="Coinflip | Fizz Casino", description=f"The coin had landed on **{chosen_side}**.\n<@{other_id}> won! They have earned **{amount*2}** chips!", color=discord.Color.blue())
            amounts[main_id] -= amount
            amounts[other_id] += amount
        else:
            newest_embed = discord.Embed(title="Coinflip | Fizz Casino", description=f"The coin had landed on **{chosen_side}**.\n<@{main_id}> won! They have earned **{amount*2}** chips!", color=discord.Color.blue())
            amounts[main_id] += amount
            amounts[other_id] -= amount
        
        await msg.edit(embed=newest_embed)
        _save()

    #Blackjack Command section
    
    @commands.hybrid_command()
    async def blackjack(self, ctx, amount: int):
        main_id = str(ctx.message.author.id)
        
        if main_id not in amounts:
            amounts[main_id] = 50
        
        if amounts[main_id] < amount:
            embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"You can't afford this bet", color=discord.Color.red())
            await ctx.send(embed=embed)
            return
        
        else:
            embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealing...", color=discord.Color.blue())
            embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar.url)
            msg = await ctx.send(embed=embed)
            view = BlackjackView(ctx, main_id, amount)
            await msg.edit(embed=view.embed, view=view)
            await view.wait()

async def setup(client):
    await client.add_cog(Gambling(client))