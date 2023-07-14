import discord
from discord.ext import commands
import minecraftbot
from mcstatus import JavaServer

from typing import Self

Context = commands.Context

# Intents - what the bot is meant to do
# At the moment I have everything enabled since this is my first bot.
# Maybe in the future as I develop my program, I am going to reduce intents to just what I need.
intents = discord.Intents.all()
bot = minecraftbot.MinecraftBot(command_prefix="/mc ", intents=intents)

# This command decorator/annotation, the bot will recognize this as a command
# Async = not at time of function call. Need to |await| before sending context.
# A context is pretty much the context around when the command was executed
# - can include info about user who called it, time, and other info
# - check Discord's documentation for more info
@bot.command()
async def setserver(ctx: Context, mcServerName: str):
    prev = bot.minecraft_java_server
    bot.minecraft_java_server = JavaServer.lookup(mcServerName)
    if not bot.server_is_online():
        await ctx.send(bot.SERVER_CONNECT_FAIL_MESSAGE)
        bot.minecraft_java_server = prev
        return
    await ctx.send(f"Set associated Minecraft server to `{bot.server_ip()}`")

@bot.command()
async def getserver(ctx: Context):
    if not bot.server_is_set():
        await ctx.send(bot.SERVER_UNSET_MESSAGE)
    elif bot.server_is_online():
        await ctx.send(f"Associated Minecraft server IP is `{bot.server_ip()}`")
    else:
        await ctx.send(bot.SERVER_CONNECT_FAIL_MESSAGE)

@bot.command()
async def online(ctx: Context):
    if not bot.server_is_set():
        await ctx.send(bot.SERVER_UNSET_MESSAGE)
    elif bot.server_is_online():
        status = bot.minecraft_java_server.status()
        await ctx.send(f"""There are **{status.players.online}/{status.players.max}** players 
                       online on `{bot.server_ip()}`""")
    else:
        await ctx.send(bot.SERVER_CONNECT_FAIL_MESSAGE)

import planview
from datetime import datetime

@bot.command()
async def plan(ctx: Context, action: str, *tokens):
    await ctx.message.delete()
    if action == "create":
        message = " ".join(tokens)
        embed = discord.Embed(color=discord.Color.green(), title=message, timestamp=datetime.now()) \
                .set_footer(text="Minecraft Looking For Group Bot") \
                .set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar) \
                .set_thumbnail(url="https://static.wikia.nocookie.net/minecraft_gamepedia/images/a/a4/Grass_Block_%28item%29_BE5.png/revision/latest?cb=20200901112517") \
                .add_field(name="Interested Players:", value="No interested players yet... Be the first!", inline=False)
        plan_view = planview.PlanView(ctx.author.id, embed=embed, timeout=None)
        view_message = await ctx.send(view=plan_view, embed=embed)
        plan_view.set_message(view_message)

        await plan_view.wait()
        # Only way I could figure out how to ping people, not ideal. Ideal would be doing it
        # inside of the PlanView class
        if plan_view.interested_players:
            await ctx.send(content=plan_view.interested_players_string, delete_after=0.1)

    # maybe another action: |view| all current ongoing plans?


from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot.run(BOT_TOKEN)

