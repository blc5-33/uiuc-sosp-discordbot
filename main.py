import discord
from discord.ext import commands
import minecraftbot
from mcstatus import JavaServer

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
        await ctx.send(f"There are **{status.players.online}/{status.players.max}** players online on `{bot.server_ip()}`")
    else:
        await ctx.send(bot.SERVER_CONNECT_FAIL_MESSAGE)


class PlanView(discord.ui.View):
    def __init__(self, creator_id: int, info: str = "", **kwargs):
        super().__init__(**kwargs)
        self.creator_id = creator_id
        self.info = info
        self.interested_players: set[int] = set()


    @discord.ui.button(style=discord.ButtonStyle.green, label="I'm Interested!")

    async def interested(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id not in self.interested_players:
            self.interested_players.add(interaction.user.id)
            await interaction.response.send_message(
                content="You have been marked as interested for this plan.\nYou will be pinged at the start of the plan.",
                ephemeral=True,delete_after=15)
        else:
            await interaction.response.send_message(
                content="You are already interested!",
                ephemeral=True,delete_after=6)
            
        
    @discord.ui.button(style=discord.ButtonStyle.red, label="I'm No Longer Interested...")

    async def not_interested(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id in self.interested_players:
            self.interested_players.remove(interaction.user.id)
            await interaction.response.send_message(
                content="You are no longer interested for this plan.",
                ephemeral=True,delete_after=15)
        else:
            await interaction.response.send_message(
                content="You are already not interested!",
                ephemeral=True,delete_after=6)


    @discord.ui.button(style=discord.ButtonStyle.blurple, label="Start Plan")

    async def start(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id == self.creator_id:
            # TODO: Find a way to ping all interested users.
            await interaction.response.send_message(
                content=f"The event \"{self.info}\" has started!")
            self.stop()
        else:
            await interaction.response.send_message(
                content="You don't have permission to do that.",
                ephemeral=True,delete_after=6)
    

    @discord.ui.button(style=discord.ButtonStyle.grey, label="Cancel Plan")

    async def cancel(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id == self.creator_id:
            await interaction.response.send_message(
                content=f"The event \"{self.info}\" has been cancelled.")
            self.stop()
        else:
            await interaction.response.send_message(
                content="You don't have permission to do that.",
                ephemeral=True,delete_after=6)
            

@bot.command()
async def plan(ctx: Context, action: str, *tokens):
    if action == "create":
        message = " ".join(tokens)
        plan_view = PlanView(ctx.author.id, info=message, timeout=None)
        view_message = await ctx.send(content=f"{message}", view=plan_view)
        await plan_view.wait()
        await view_message.delete()

    # maybe another action: |view| all current ongoing plans?


from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot.run(BOT_TOKEN)

