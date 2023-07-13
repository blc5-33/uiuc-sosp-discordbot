from dotenv import load_dotenv
import os
from mcstatus import JavaServer
import discord
from discord.ext import commands

# Type aliases
Context = commands.Context

class MinecraftBot(commands.Bot):
    def __init__(self, 
                #  SERVER_UNSET_MESSAGE="No Minecraft server has been set yet!",
                #  minecraft_java_server=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.SERVER_UNSET_MESSAGE = "No Minecraft server has been set yet!"
        self.SERVER_CONNECT_FAIL_MESSAGE = "Could not connect to that address's Minecraft server!"
        self.minecraft_java_server = None
    
    def server_is_set(self) -> bool:
        return self.minecraft_java_server

    def server_is_online(self) -> bool:
        if self.server_is_set():
            try:
                self.minecraft_java_server.status()
            except:
                return False
            return True
        
        return False
    
    def server_ip(self) -> str:
        """
        Returns the IP address\n
        MUST check `server_is_online()` before calling this function.
        """
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
        await ctx.send(f"There are **{status.players.online}/{status.players.max}** players online on `{bot.server_ip()}`")
    else:
        await ctx.send(bot.SERVER_CONNECT_FAIL_MESSAGE)


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot.run(BOT_TOKEN)

