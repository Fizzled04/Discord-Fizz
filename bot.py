import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix = '>', case_insensitive=True, intents=intents)


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
    try:
        await client.unload_extension(f'cogs.{extension}')
        await client.load_extension(f'cogs.{extension}')
        await ctx.send(f'Reloaded {extension}')
    except:
        await ctx.send(f'Failed to reload {extension}')

@client.event
async def setup_hook():
    await load_extensions()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')


@client.event
async def on_command_error(ctx, error):
    await ctx.send(f'Error: {error}')

client.run(TOKEN)