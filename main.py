from dotenv import load_dotenv
import os
from mcstatus import JavaServer
import discord
from discord.ext import commands

load_dotenv()

# Type aliases
Context = commands.Context

class MinecraftBot(commands.Bot):
    def __init__(self, 
                #  SERVER_UNSET_MESSAGE="No Minecraft server has been set yet!",
                #  minecraft_java_server=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.SERVER_UNSET_MESSAGE = "No Minecraft server has been set yet!"
        self.minecraft_java_server = None

    def current_server_ip(self) -> str:
        if self.minecraft_java_server:
            address = self.minecraft_java_server.address
            return f"{address.host.split('_tcp.')[-1]}:{address.port}"


# Intents - what the bot is meant to do
# At the moment I have everything enabled since this is my first bot. As I develop my program,
# I am going to reduce intents to just what I need.
intents = discord.Intents.all()
bot = MinecraftBot(command_prefix="/mc ", intents=intents)

# This command decorator/annotation, the bot will recognize this as a command
# Async = not at time of function call. Need to |await| before sending context.
# A context is pretty much the context around when the command was executed
# - can include info about user who called it, time, and other info
# - check Discord's documentation for more info
@bot.command()
async def setserver(ctx: Context, mcServerName: str):
    bot.minecraft_java_server = JavaServer.lookup(mcServerName)
    try:
        bot.minecraft_java_server.status()
    except:
        await ctx.send(f"Could not connect to that address's Minecraft server!")
        return
    await ctx.send(f"Set associated Minecraft server to `{bot.current_server_ip()}`")

@bot.command()
async def getserver(ctx: Context):
    if bot.minecraft_java_server:
        await ctx.send(f"Associated Minecraft server IP is `{bot.current_server_ip()}`")
    else:
        await ctx.send(bot.SERVER_UNSET_MESSAGE)

@bot.command()
async def online(ctx: Context):
    if bot.minecraft_java_server:
        status = bot.minecraft_java_server.status()
        await ctx.send(f"There are **{status.players.online}/{status.players.max}** players online on `{bot.current_server_ip()}`")
    else:
        await ctx.send(bot.SERVER_UNSET_MESSAGE)


BOT_TOKEN = os.getenv("BOT_TOKEN")
bot.run(BOT_TOKEN)

