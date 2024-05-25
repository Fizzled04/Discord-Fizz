import discord
import praw
from discord.ext import commands
from discord.ext.commands import Bot
import random
from dotenv import load_dotenv
import os

load_dotenv()
REDDIT_ID = os.getenv('REDDIT_ID')
REDDIT_SECRET = os.getenv('REDDIT_SECRET')
REDDIT_AGENT = os.getenv('REDDIT_AGENT')

reddit = praw.Reddit(client_id = REDDIT_ID,
                     client_secret = REDDIT_SECRET,
                     user_agent = REDDIT_AGENT,
                     check_for_async = False)

class Reddit(commands.Cog):

    def __init__(self, client):
        self.client = client


    @commands.hybrid_command(name = "reddit")
    async def reddit(self, ctx, value):
        subreddit = reddit.subreddit(value)
        all_subs = []

        hot = subreddit.hot(limit = 50)
        for submission in hot:
            all_subs.append(submission)
        
        random_sub = random.choice(all_subs)

        name = random_sub.title        
        url = random_sub.url
        
        em = discord.Embed(title = name)
        try:

                if hasattr(random_sub, 'post_hint') and random_sub.post_hint == 'image':
                    em.set_image(url = url)

                elif random_sub.is_video:
                    print("The post has an embedded video.")
                    em.add_field(name="Video", value=f"[Watch here]({random_sub.url})", inline=False)

                elif random_sub.media:
                    await ctx.send(url)
                    return

                if random_sub.selftext:
                    em.add_field(name="Text Content", value=random_sub.selftext, inline=False)

                await ctx.send(embed = em)

            
        except discord.HTTPException as e:
            if e.code == 50035:
                await ctx.send("Error: The text content is too long to display.")
            else:
                await ctx.send(f"An unexpected error occurred: {e}")
    
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

async def setup(client):
    await client.add_cog(Reddit(client))