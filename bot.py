import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
intents.message_content = True

client = commands.Bot(command_prefix = '>', case_insensitive=True, intents=intents, help_command=None)

async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await client.load_extension(f'cogs.{filename[:-3]}')
                print(f'Successfully loaded {filename}')
            except Exception as e:
                print(f'Failed to load {filename}: {e}')


@client.command()
async def reload(ctx, extension):
    if ctx.author.id == 333034815995510784:
        try:
            await client.unload_extension(f'cogs.{extension}')
            await client.load_extension(f'cogs.{extension}')
            await ctx.send(f'Reloaded {extension}')
        except:
            await ctx.send(f'Failed to reload {extension}')
    else:
        ctx.send("Sorry only developers can use this command", ephemeral=True)
@client.event
async def setup_hook():
    await load_extensions()
    await client.tree.sync()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')


class Help(View):
    def __init__(self, ctx):
        super().__init__(timeout=180)  # Timeout for the view
        self.ctx = ctx
        self.main_id = self.ctx.author.id
        self.page = 0
        self.embeds = self.help_embeds()
    
    def help_embeds(self):
        embeds = [
            discord.Embed(title="Help | Fizz Casino", description="Welcome to the Fizz Casino help book!\nBelow you will find a glossary of what each page contains!\n1. This Page!\n2. General Commands\n3. Coinflipping\n4. Blackjack\n5. Slots\n\nYou will start with **500** chips, happy gambling!", color=discord.Color.blue()).set_footer(text="1/5"),
            discord.Embed(title="Help | Fizz Casino", description="General Commands, this section will contain the self explanitory commands!\n\n**/balance** --- This command shows you your balance of chips\n\n**/pay (amount) (@user)** --- This does what youd expect, it pays a user chips from your bank\n\n**/daily** --- This command allows you to collect 150 chips daily, it resets at 12am CST.", color=discord.Color.blue()).set_footer(text="2/5"),
            discord.Embed(title="Help | Fizz Casino", description="Coinflip(30 seconds to respond! You will be refunded)\n**/coinflip (amount) (@user)**\n\nOne of the most basic forms of gambling, in order to use this command you will challenge and opposing user, this user will be given the choice of which side of the coin they want, one of these sides will be chosen at random, winner takes all!", color=discord.Color.blue()).set_footer(text="3/5"),
            discord.Embed(title="Help | Fizz Casino", description="Blackjack(90 seconds to finish playing or you lose your chips!)\n**/blackjack (amount)**\n\nThis ones a little more complicated than coinflipping, to begin, face cards(King, Queen, Jack) are all worth 10, and Aces are worth 1 or 11 depending on which is better for your hand. In this game you and a dealer are dealt 2 cards each, with one of the dealers being hidden. Your goal is to be as close to 21 as possible, you achieve this through hitting(recieving another card) to get as close to 21 as possible without going over and then standing(ending your turn and passing to the dealer). You are also given the option to Double, doubling will double your bet and you will recieve one card, then you are forced to stand. On the dealers turn, he is forced to hit at 16 and below, but he is also forced to hit on a soft seventeen(an example of this is a 6 and Ace or a 2, 4, and Ace). The winner is determined by whoever is closest to 21 without going over, a tie results in you recieving your chips back. In the circumstance in which the Dealer or you get 21 with your starting two cards the game will end immediately, if you got 21 you will be paid out 3/2, meaning you get a little extra than winning normally, if the dealer gets 21 you lose your chips, and if you both recieved 21 you tie and recieve your chips back.", color=discord.Color.blue()).set_footer(text="4/5"),
            discord.Embed(title="Help | Fizz Casino", description="Slots\n**/slots (amount)**\n\nA little less wordy than the blackjack command, but I will be explaining how you win and the payouts. Firstly, you need a minimum bet size of **5**. In order to win at slots you must match 3 symbols either horizontally or diagonally, the symbol will determine on the amount earned, these payouts will be listed below:\n:broccoli: .5x\n:carrot: 2x\n:grapes: 5x\n:banana: 10x\n:cherries: 25x", color=discord.Color.blue()).set_footer(text="5/5"),
        ]
        return embeds
    
    @discord.ui.button(label="Prev", style=discord.ButtonStyle.blurple)
    async def grey_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.main_id:
            await interaction.response.send_message("This is not your help page. To get your own type /help", ephemeral=True)
            return
        if self.page > 0:
            self.page -= 1
            await interaction.response.edit_message(embed=self.embeds[self.page], view=self)
    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple)
    async def green_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.main_id:
            await interaction.response.send_message("This is not your help page. To get your own type /help", ephemeral=True)
            return
        if self.page < len(self.embeds) - 1:
            self.page += 1
            await interaction.response.edit_message(embed=self.embeds[self.page], view=self)
        
        
@client.hybrid_command(name="help")
async def help(ctx):
    view = Help(ctx)
    await ctx.send(embed=view.embeds[0], view=view)


@client.event
async def on_command_error(ctx, error):
    await ctx.send(f'Error: {error}')

client.run(TOKEN)