import discord
from mcstatus import JavaServer

server = JavaServer.lookup("vanilla.casual-craft.com")

status = server.status()
print(f"The server has {status.players.online} players")
