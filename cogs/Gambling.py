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
from datetime import datetime, timedelta

def _save():
    with open('amounts.json', 'w') as f:
        json.dump(amounts, f)

amounts = {}
daily_cooldowns = {}

def generate_random_slot(elements):
    #creates a board
    random.shuffle(elements)
    board = [elements[i:i+3] for i in range(0, 9, 3)]
    return board

def generate_losing_slot(elements):
    #ensures board is losing
    def is_valid(board):
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2]:
                return False
            if board[0][i] == board[1][i] == board[2][i]:
                return False
        if board[0][0] == board[1][1] == board[2][2]:
            return False
        if board[0][2] == board[1][1] == board[2][0]:
            return False
        return True

    while True:
        #repeatedly generates boards until one is losing
        random.shuffle(elements)
        board = [elements[i:i+3] for i in range(0, 9, 3)]
        if is_valid(board):
            return board    

def generate_winning_slot(elements, winningSymbol):
    def fill_board(board, elements):
        idx = 0
        for i in range(3):
            for j in range(3):
                if board[i][j] is None:
                    board[i][j] = elements[idx]
                    idx += 1
        return board

    def is_losing_board(board, winningSymbol):
        #ensures board is losing besides the desired symbol
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] and board[i][0] != winningSymbol:
                return False
            if board[0][i] == board[1][i] == board[2][i] and board[0][i] != winningSymbol:
                return False
        if board[0][0] == board[1][1] == board[2][2] and board[0][0] != winningSymbol:
            return False
        if board[0][2] == board[1][1] == board[2][0] and board[0][2] != winningSymbol:
            return False
        return True

    elements = [e for e in elements if e != winningSymbol]

    winningPositions = [
        [(0, 0), (0, 1), (0, 2)],
        [(1, 0), (1, 1), (1, 2)],
        [(2, 0), (2, 1), (2, 2)],
        [(0, 0), (1, 0), (2, 0)],
        [(0, 1), (1, 1), (2, 1)],
        [(0, 2), (1, 2), (2, 2)],
        [(0, 0), (1, 1), (2, 2)],
        [(0, 2), (1, 1), (2, 0)] 
    ]

    while True:
        board = [[None, None, None], [None, None, None], [None, None, None]]

        winningPosition = random.choice(winningPositions)
        for pos in winningPosition:
            board[pos[0]][pos[1]] = winningSymbol

        board = fill_board(board, elements[:])

        if is_losing_board(board, winningSymbol):
            return board

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
        super().__init__(timeout=30)
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
        new_embed.set_author(name=self.ctx.message.author, icon_url=self.ctx.author.avatar.url)
        await interaction.response.edit_message(embed=new_embed)
        self.stop()

    async def on_timeout(self):
        await self.ctx.send(f"<@{self.other_id}> did not respond in time.", ephemeral=True)


#Blackjack view + logic
class BlackjackView(View):
    def __init__(self, ctx, main_id, amount):
        super().__init__(timeout=90)
        self.ctx = ctx
        self.main_id = main_id
        self.amount = amount
        self.result = None
        self.hitChecker = False
        self.splitChecker = False
        
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
        self.playerHands = [{}]
        self.currentHand = 0
        self.splitCount = 0
        self.handResults = []

        amounts[main_id] -= self.amount
        
        
        for _ in range(2):
                card, value = deal_card(self.blackjackDeck)
                self.playerHands[0][card] = value
                card, value = deal_card(self.blackjackDeck)
                self.dealerHand[card] = value

        self.dealerHandStrHidden = " ".join([deckDict[card]])
        self.update_hand_strings()

        self.embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStrHidden}<:blank:1244303337315369073>\n\nPlayer: {self.playerHandMainStr}", color=discord.Color.blue())
        self.embed.set_author(name=self.ctx.message.author, icon_url=self.ctx.author.avatar.url)
        playerMainCurrentValue = calculate_hand_value(self.playerHands[0])
        delearCurrentValue = calculate_hand_value(self.dealerHand)
        
        if(playerMainCurrentValue == 21):
            if(delearCurrentValue != 21):
                payout = round(self.amount*3/2)
                self.embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStr}\n\nPlayer: {self.playerHandMainStr} \n\nYou got blackjack! You've been paid out **{payout+self.amount}** chips!", color=discord.Color.gold())
                self.embed.set_author(name=self.ctx.message.author, icon_url=self.ctx.author.avatar.url)
                amounts[self.main_id] += payout+self.amount
            else:
                self.embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStr}\n\nPlayer: {self.playerHandMainStr} \n\nYou both got blackjack! You've recieved your chips back.", color=discord.Color.blue())
                self.embed.set_author(name=self.ctx.message.author, icon_url=self.ctx.author.avatar.url)
                amounts[self.main_id] += self.amount
            self.stop()
        elif(delearCurrentValue == 21):
            self.embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStr}\n\nPlayer: {self.playerHandMainStr} \n\nSorry, the dealer got blackjack, you lost.", color=discord.Color.red())
            self.embed.set_author(name=self.ctx.message.author, icon_url=self.ctx.author.avatar.url)
            self.stop()

    def update_hand_strings(self):
        self.dealerHandStr = " ".join([deckDict[card] for card in self.dealerHand])
        self.playerHandMainStr = " ".join([deckDict[card] for card in self.playerHands[self.currentHand]])
        self.playerHandStrings = [" ".join([deckDict[card] for card in hand]) for hand in self.playerHands]

    def is_soft_17(self, hand):
        value = sum(hand.values())
        return value == 17 and any(card.startswith('A') and hand[card] == 11 for card in hand)
    
    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def green_button(self, interaction: discord.Interaction, button: Button):
        await self.process_choice(interaction, "hit")
    @discord.ui.button(label="Stand", style=discord.ButtonStyle.red)
    async def grey_button(self, interaction: discord.Interaction, button: Button):
        await self.process_choice(interaction, "stand")
    @discord.ui.button(label="Double", style=discord.ButtonStyle.blurple)
    async def red_button(self, interaction: discord.Interaction, button: Button):
        await self.process_choice(interaction, "double")
    async def process_choice(self, interaction: discord.Interaction, choice: str):
        if int(interaction.user.id) != int(self.main_id):
            await interaction.response.send_message("You are not the one playing!", ephemeral=True)
            return
        self.result = choice
            
        
        if(self.result == "hit"):
            await self.handle_hit(interaction)
        
        elif(self.result == "stand"):
            await self.handle_stand(interaction)
        
        elif(self.result == "double"):
            await self.handle_double(interaction)
        
            
    
    async def handle_hit(self, interaction: discord.Interaction):
        card, value = deal_card(self.blackjackDeck)
        self.playerHands[self.currentHand][card] = value
        self.update_hand_strings()
        playerMainCurrentValue = calculate_hand_value(self.playerHands[self.currentHand])
        
        if(playerMainCurrentValue > 21):
            new_embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStrHidden}<:blank:1244303337315369073>\n\nPlayer: {self.playerHandStrings[self.currentHand]}\n\nYou **BUSTED** and have lost your chips.", color=discord.Color.red())
            self.stop()
        else:
            new_embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStrHidden}<:blank:1244303337315369073>\n\nPlayer: {self.playerHandStrings[self.currentHand]}", color=discord.Color.blue())
        self.hitChecker = True
        new_embed.set_author(name=self.ctx.message.author, icon_url=self.ctx.author.avatar.url)
        await interaction.response.edit_message(embed=new_embed)

    async def handle_stand(self, interaction: discord.Interaction):
        
        self.handResults.append(self.playerHands[self.currentHand])
        
        new_embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStr}\n\nPlayer: {self.playerHandStrings[self.currentHand]}", color=discord.Color.blue())
        dealerCurrentValue = calculate_hand_value(self.dealerHand)
        playerMainCurrentValue = calculate_hand_value(self.playerHands[self.currentHand])
        await self.dealer_turn()
        dealerCurrentValue = calculate_hand_value(self.dealerHand)
        if(dealerCurrentValue < playerMainCurrentValue or dealerCurrentValue > 21):
            new_embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStr}\n\nPlayer: {self.playerHandStrings[self.currentHand]}\n\nCongratulations you **WON** you've been paid out **{self.amount*2}** chips!", color=discord.Color.green())
            amounts[self.main_id] += self.amount*2
            self.stop()
        elif(dealerCurrentValue > playerMainCurrentValue):
            new_embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStr}\n\nPlayer: {self.playerHandStrings[self.currentHand]}\n\nYou **LOST** and have lost your chips.", color=discord.Color.red())
            self.stop()
        else:
            new_embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStr}\n\nPlayer: {self.playerHandStrings[self.currentHand]}\n\nYou **TIED** and have recieved your chips back.", color=discord.Color.blue())
            amounts[self.main_id] += self.amount
            self.stop()
        new_embed.set_author(name=self.ctx.message.author, icon_url=self.ctx.author.avatar.url)
        await interaction.response.edit_message(embed=new_embed)

    async def handle_double(self, interaction: discord.Interaction):
        if(amounts[self.main_id] < self.amount):
            await interaction.response.send_message("You can not afford to double.", ephemeral=True)
            return
        elif(self.hitChecker == False):
            amounts[self.main_id] -= self.amount
            self.amount *= 2
            card, value = deal_card(self.blackjackDeck)
            self.playerHands[self.currentHand][card] = value
            self.update_hand_strings()
            playerMainCurrentValue = calculate_hand_value(self.playerHands[self.currentHand])
            
            if(playerMainCurrentValue > 21):
                new_embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStrHidden}<:blank:1244303337315369073>\n\nPlayer: {self.playerHandStrings[self.currentHand]}\n\nYou **BUSTED** and have lost your chips.", color=discord.Color.red())
                self.stop()
            else:
                new_embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStr}\n\nPlayer: {self.playerHandStrings[self.currentHand]}", color=discord.Color.blue())
                await self.dealer_turn()
                dealerCurrentValue = calculate_hand_value(self.dealerHand)
                if(dealerCurrentValue < playerMainCurrentValue or dealerCurrentValue > 21):
                    new_embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStr}\n\nPlayer: {self.playerHandStrings[self.currentHand]}\n\nCongratulations you **WON** you've been paid out **{self.amount*2}** chips!", color=discord.Color.green())
                    amounts[self.main_id] += self.amount*2
                    self.stop()
                elif(dealerCurrentValue > playerMainCurrentValue):
                    new_embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStr}\n\nPlayer: {self.playerHandStrings[self.currentHand]}\n\nYou **LOST** and have lost your chips.", color=discord.Color.red())
                    self.stop()
                else:
                    new_embed = discord.Embed(title="Blackjack | Fizz Casino", description=f"Dealer: {self.dealerHandStr}\n\nPlayer: {self.playerHandStrings[self.currentHand]}\n\nYou **TIED** and have recieved your chips back.", color=discord.Color.blue())
                    amounts[self.main_id] += self.amount
                    self.stop()
            new_embed.set_author(name=self.ctx.message.author, icon_url=self.ctx.author.avatar.url)
            await interaction.response.edit_message(embed=new_embed)
        else:
            await interaction.response.send_message("You have already hit, you cannot double.", ephemeral=True)
            return

    async def dealer_turn(self):
        dealerCurrentValue = calculate_hand_value(self.dealerHand)

        while dealerCurrentValue < 17 or self.is_soft_17(self.dealerHand):
            card, value = deal_card(self.blackjackDeck)
            self.dealerHand[card] = value
            dealerCurrentValue = calculate_hand_value(self.dealerHand)
        self.update_hand_strings()    
        
    async def on_timeout(self):
        await self.ctx.send(f"You did not respond in time, you have lost your chips.", ephemeral=True)
                
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
    async def balance(self, ctx, user: discord.User = None):
        user = user or ctx.message.author
        id = str(user.id)
        if id not in amounts:
            amounts[id] = 500
            _save()
        
        await ctx.send(f"{user.mention} has **{amounts[id]}** chips.", ephemeral=True)
        
        
    @commands.hybrid_command()
    async def pay(self, ctx, amount: int, other: discord.Member):
        main_id = str(ctx.message.author.id)
        other_id = str(other.id)
        if main_id not in amounts:
            amounts[main_id] = 500
        if other_id not in amounts:
            amounts[other_id] = 500
        if amounts[main_id] < amount:
            await ctx.send("You can't afford this transaction", ephemeral=True)
        else:
            amounts[main_id] -= amount
            amounts[other_id] += amount
            await ctx.send(f"You've successfully sent **{amount}** chips to <@{other_id}>")
        _save()

    
    #Daily payout command section
    @commands.hybrid_command()
    async def daily(self, ctx):
        main_id = str(ctx.message.author.id)
        if main_id not in amounts:
            amounts[main_id] = 500
        
        now = datetime.now()
        if(main_id in daily_cooldowns):
            lastClaimTime = daily_cooldowns[main_id]
            nextClaimTime = lastClaimTime + timedelta(days=1)
            remaining_time = nextClaimTime - now
            hours, remainder = divmod(int(remaining_time.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            await ctx.send(f"You have already claimed your daily reward. Please try again in {hours} hours and {minutes} minutes.", ephemeral=True)
            return

        amounts[main_id] += 150
        daily_cooldowns[main_id] = now
        await ctx.send(f"You've recieved **150** chips! You can claim your daily again in 24 hours.", ephemeral=True)
    
    #Coinflip command section
    @commands.hybrid_command()
    async def coinflip(self, ctx, amount: int, opponent: discord.Member):
        main_id = str(ctx.message.author.id)
        other_id = str(opponent.id)
        
        if main_id not in amounts:
            amounts[main_id] = 500
        if other_id not in amounts:
            amounts[other_id] = 500
        
        if amounts[main_id] < amount:
            await ctx.send("You can't afford this coinflip", ephemeral=True)
            return
        elif amounts[other_id] < amount:
            await ctx.send(f"<@{other_id}> can't afford this bet", ephemeral=True)
            return
        else:
            embed = discord.Embed(title="Coinflip | Fizz Casino", description=f"<@{other_id}> You've been challenged to a coinflip for **{amount}** chips!\nPlease pick a side if you wish to accept.", color=discord.Color.blue())
            embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar.url)
            view = CoinflipView(ctx, main_id, other_id, amount)
            msg = await ctx.send(embed=embed, view=view)
            await view.wait()
             
            if view.result:
                chosen_side = random.choice(["blue", "red"])
                asyncio.create_task(self.delayed_edit_coinflip(ctx, msg, main_id, other_id, amount, chosen_side, view.result))

    #Coinflip delay
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
            newest_embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar.url)
            await msg.edit(embed=newest_embed)
            _save()


    #Blackjack Command section
    @commands.hybrid_command()
    async def blackjack(self, ctx, amount: int):
        main_id = str(ctx.message.author.id)
        
        if main_id not in amounts:
            amounts[main_id] = 500
        
        if amounts[main_id] < amount:
            await ctx.send("You can't afford this bet", ephemeral=True)
            return
        
        else:
            embed = discord.Embed(title="Blackjack | Fizz Casino", description="Dealing...", color=discord.Color.blue())
            embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar.url)
            msg = await ctx.send(embed=embed)
            view = BlackjackView(ctx, main_id, amount)
            await msg.edit(embed=view.embed, view=view)
            await view.wait()
            _save()
    
    
    #Slot Command section
    @commands.hybrid_command()
    async def slots(self, ctx, amount: int):
        main_id = str(ctx.message.author.id)
        
        if main_id not in amounts:
            amounts[main_id] = 500
        
        if amount < 5: 
            await ctx.send("You must bet atleast **5** chips", ephemeral=True)
            return
            
        elif amounts[main_id] < amount:
            await ctx.send("You can't afford this bet", ephemeral=True)
            return
        
        else:
            slotSymbols = [":broccoli:", ":carrot:", ":grapes:", ":banana:", ":cherries:"]
            elements = (slotSymbols * 2)[:9]
            amounts[main_id] -= amount
            currentBoard = generate_random_slot(elements)
            embed = discord.Embed(title="Slots | Fizz Casino", description=f"{currentBoard[0][0]} {currentBoard[0][1]} {currentBoard[0][2]}\n{currentBoard[1][0]} {currentBoard[1][1]} {currentBoard[1][2]}\n{currentBoard[2][0]} {currentBoard[2][1]} {currentBoard[2][2]}", color=discord.Color.blue())
            embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar.url)
            msg = await ctx.send(embed=embed)
            for _ in range(5):
                await asyncio.sleep(.35)
                currentBoard = generate_random_slot(elements)
                new_embed = discord.Embed(title="Slots | Fizz Casino", description=f"{currentBoard[0][0]} {currentBoard[0][1]} {currentBoard[0][2]}\n{currentBoard[1][0]} {currentBoard[1][1]} {currentBoard[1][2]}\n{currentBoard[2][0]} {currentBoard[2][1]} {currentBoard[2][2]}", color=discord.Color.blue())
                new_embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar.url)
                await msg.edit(embed=new_embed)
            
            randomNum = random.randint(1, 1000)
            
            if randomNum <= 675:
                currentBoard = generate_losing_slot(elements)
                finalSlot = currentBoard 
                for _ in range(4):
                    await asyncio.sleep(.35)
                    currentBoard = generate_random_slot(elements)
                    new_embed = discord.Embed(title="Slots | Fizz Casino", description=f"{finalSlot[0][0]} {currentBoard[0][1]} {currentBoard[0][2]}\n{finalSlot[1][0]} {currentBoard[1][1]} {currentBoard[1][2]}\n{finalSlot[2][0]} {currentBoard[2][1]} {currentBoard[2][2]}", color=discord.Color.blue())
                    new_embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar.url)
                    await msg.edit(embed=new_embed)
                for _ in range(4):
                    await asyncio.sleep(.35)
                    currentBoard = generate_random_slot(elements)
                    new_embed = discord.Embed(title="Slots | Fizz Casino", description=f"{finalSlot[0][0]} {finalSlot[0][1]} {currentBoard[0][2]}\n{finalSlot[1][0]} {finalSlot[1][1]} {currentBoard[1][2]}\n{finalSlot[2][0]} {finalSlot[2][1]} {currentBoard[2][2]}", color=discord.Color.blue())
                    new_embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar.url)
                    await msg.edit(embed=new_embed)    
                new_embed = discord.Embed(title="Slots | Fizz Casino", description=f"{finalSlot[0][0]} {finalSlot[0][1]} {finalSlot[0][2]}\n{finalSlot[1][0]} {finalSlot[1][1]} {finalSlot[1][2]}\n{finalSlot[2][0]} {finalSlot[2][1]} {finalSlot[2][2]}\nYou **LOST** your **{amount}** chips", color=discord.Color.red())
                new_embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar.url)
                await msg.edit(embed=new_embed)
                 
            elif randomNum <= 800:
                winningSymbol = ":broccoli:"
                winningBoard = generate_winning_slot(elements, winningSymbol)
                for _ in range(4):
                    await asyncio.sleep(.35)
                    currentBoard = generate_random_slot(elements)
                    new_embed = discord.Embed(title="Slots | Fizz Casino", description=f"{winningBoard[0][0]} {currentBoard[0][1]} {currentBoard[0][2]}\n{winningBoard[1][0]} {currentBoard[1][1]} {currentBoard[1][2]}\n{winningBoard[2][0]} {currentBoard[2][1]} {currentBoard[2][2]}", color=discord.Color.blue())
                    new_embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar.url)
                    await msg.edit(embed=new_embed)
                for _ in range(4):
                    await asyncio.sleep(.35)
                    currentBoard = generate_random_slot(elements)
                    new_embed = discord.Embed(title="Slots | Fizz Casino", description=f"{winningBoard[0][0]} {winningBoard[0][1]} {currentBoard[0][2]}\n{winningBoard[1][0]} {winningBoard[1][1]} {currentBoard[1][2]}\n{winningBoard[2][0]} {winningBoard[2][1]} {currentBoard[2][2]}", color=discord.Color.blue())
                    new_embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar.url)
                    await msg.edit(embed=new_embed)    
                new_embed = discord.Embed(title="Slots | Fizz Casino", description=f"{winningBoard[0][0]} {winningBoard[0][1]} {winningBoard[0][2]}\n{winningBoard[1][0]} {winningBoard[1][1]} {winningBoard[1][2]}\n{winningBoard[2][0]} {winningBoard[2][1]} {winningBoard[2][2]}\nYou **WON** half of your chips(**{round(amount/2)}**) back!", color=discord.Color.yellow())
                new_embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar.url)
                await msg.edit(embed=new_embed)
                
                amounts[main_id] += round(amount/2)
           
            elif randomNum <= 930:
                winningSymbol = ":carrot:"
                winningBoard = generate_winning_slot(elements, winningSymbol)
                for _ in range(4):
                    await asyncio.sleep(.35)
                    currentBoard = generate_random_slot(elements)
                    new_embed = discord.Embed(title="Slots | Fizz Casino", description=f"{winningBoard[0][0]} {currentBoard[0][1]} {currentBoard[0][2]}\n{winningBoard[1][0]} {currentBoard[1][1]} {currentBoard[1][2]}\n{winningBoard[2][0]} {currentBoard[2][1]} {currentBoard[2][2]}", color=discord.Color.blue())
                    new_embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar.url)
                    await msg.edit(embed=new_embed)
                for _ in range(4):
                    await asyncio.sleep(.35)
                    currentBoard = generate_random_slot(elements)
                    new_embed = discord.Embed(title="Slots | Fizz Casino", description=f"{winningBoard[0][0]} {winningBoard[0][1]} {currentBoard[0][2]}\n{winningBoard[1][0]} {winningBoard[1][1]} {currentBoard[1][2]}\n{winningBoard[2][0]} {winningBoard[2][1]} {currentBoard[2][2]}", color=discord.Color.blue())
                    new_embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar.url)
                    await msg.edit(embed=new_embed)    
                new_embed = discord.Embed(title="Slots | Fizz Casino", description=f"{winningBoard[0][0]} {winningBoard[0][1]} {winningBoard[0][2]}\n{winningBoard[1][0]} {winningBoard[1][1]} {winningBoard[1][2]}\n{winningBoard[2][0]} {winningBoard[2][1]} {winningBoard[2][2]}\nYou **WON** **{amount*2}** chips!", color=discord.Color.green())
                new_embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar.url)
                await msg.edit(embed=new_embed)
                
                amounts[main_id] += amount*2
            
            elif randomNum <= 970:
                winningSymbol = ":grapes:"
                winningBoard = generate_winning_slot(elements, winningSymbol)
                for _ in range(4):
                    await asyncio.sleep(.35)
                    currentBoard = generate_random_slot(elements)
                    new_embed = discord.Embed(title="Slots | Fizz Casino", description=f"{winningBoard[0][0]} {currentBoard[0][1]} {currentBoard[0][2]}\n{winningBoard[1][0]} {currentBoard[1][1]} {currentBoard[1][2]}\n{winningBoard[2][0]} {currentBoard[2][1]} {currentBoard[2][2]}", color=discord.Color.blue())
                    new_embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar.url)
                    await msg.edit(embed=new_embed)
                for _ in range(4):
                    await asyncio.sleep(.35)
                    currentBoard = generate_random_slot(elements)
                    new_embed = discord.Embed(title="Slots | Fizz Casino", description=f"{winningBoard[0][0]} {winningBoard[0][1]} {currentBoard[0][2]}\n{winningBoard[1][0]} {winningBoard[1][1]} {currentBoard[1][2]}\n{winningBoard[2][0]} {winningBoard[2][1]} {currentBoard[2][2]}", color=discord.Color.blue())
                    new_embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar.url)
                    await msg.edit(embed=new_embed)    
                new_embed = discord.Embed(title="Slots | Fizz Casino", description=f"{winningBoard[0][0]} {winningBoard[0][1]} {winningBoard[0][2]}\n{winningBoard[1][0]} {winningBoard[1][1]} {winningBoard[1][2]}\n{winningBoard[2][0]} {winningBoard[2][1]} {winningBoard[2][2]}\nYou **WON** **{amount*5}** chips!", color=discord.Color.green())
                new_embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar.url)
                await msg.edit(embed=new_embed)
                
                amounts[main_id] += amount*5
            
            elif randomNum <= 990:
                winningSymbol = ":banana:"
                winningBoard = generate_winning_slot(elements, winningSymbol)
                for _ in range(4):
                    await asyncio.sleep(.35)
                    currentBoard = generate_random_slot(elements)
                    new_embed = discord.Embed(title="Slots | Fizz Casino", description=f"{winningBoard[0][0]} {currentBoard[0][1]} {currentBoard[0][2]}\n{winningBoard[1][0]} {currentBoard[1][1]} {currentBoard[1][2]}\n{winningBoard[2][0]} {currentBoard[2][1]} {currentBoard[2][2]}", color=discord.Color.blue())
                    new_embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar.url)
                    await msg.edit(embed=new_embed)
                for _ in range(4):
                    await asyncio.sleep(.35)
                    currentBoard = generate_random_slot(elements)
                    new_embed = discord.Embed(title="Slots | Fizz Casino", description=f"{winningBoard[0][0]} {winningBoard[0][1]} {currentBoard[0][2]}\n{winningBoard[1][0]} {winningBoard[1][1]} {currentBoard[1][2]}\n{winningBoard[2][0]} {winningBoard[2][1]} {currentBoard[2][2]}", color=discord.Color.blue())
                    new_embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar.url)
                    await msg.edit(embed=new_embed)    
                new_embed = discord.Embed(title="Slots | Fizz Casino", description=f"{winningBoard[0][0]} {winningBoard[0][1]} {winningBoard[0][2]}\n{winningBoard[1][0]} {winningBoard[1][1]} {winningBoard[1][2]}\n{winningBoard[2][0]} {winningBoard[2][1]} {winningBoard[2][2]}\nYou **WON** **{amount*10}** chips!", color=discord.Color.green())
                new_embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar.url)
                await msg.edit(embed=new_embed)
                
                amounts[main_id] += amount*10
            
            else:
                winningSymbol = ":cherries:"
                winningBoard = generate_winning_slot(elements, winningSymbol)
                for _ in range(4):
                    await asyncio.sleep(.35)
                    currentBoard = generate_random_slot(elements)
                    new_embed = discord.Embed(title="Slots | Fizz Casino", description=f"{winningBoard[0][0]} {currentBoard[0][1]} {currentBoard[0][2]}\n{winningBoard[1][0]} {currentBoard[1][1]} {currentBoard[1][2]}\n{winningBoard[2][0]} {currentBoard[2][1]} {currentBoard[2][2]}", color=discord.Color.blue())
                    new_embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar.url)
                    await msg.edit(embed=new_embed)
                for _ in range(4):
                    await asyncio.sleep(.35)
                    currentBoard = generate_random_slot(elements)
                    new_embed = discord.Embed(title="Slots | Fizz Casino", description=f"{winningBoard[0][0]} {winningBoard[0][1]} {currentBoard[0][2]}\n{winningBoard[1][0]} {winningBoard[1][1]} {currentBoard[1][2]}\n{winningBoard[2][0]} {winningBoard[2][1]} {currentBoard[2][2]}", color=discord.Color.blue())
                    new_embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar.url)
                    await msg.edit(embed=new_embed)    
                new_embed = discord.Embed(title="Slots | Fizz Casino", description=f"{winningBoard[0][0]} {winningBoard[0][1]} {winningBoard[0][2]}\n{winningBoard[1][0]} {winningBoard[1][1]} {winningBoard[1][2]}\n{winningBoard[2][0]} {winningBoard[2][1]} {winningBoard[2][2]}\nYou **WON** **{amount*25}** chips!", color=discord.Color.purple())
                new_embed.set_author(name=ctx.message.author, icon_url=ctx.author.avatar.url)
                await msg.edit(embed=new_embed)
                amounts[main_id] += amount*25

            _save()

async def setup(client):
    await client.add_cog(Gambling(client))