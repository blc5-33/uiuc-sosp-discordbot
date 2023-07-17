from discord import Embed
from discord import Color
from discord import File
from discord.ext import commands

from mcstatus import JavaServer
from datetime import datetime
import base64
import logging

class MinecraftBot(commands.Bot):
    def __init__(self, 
                #  SERVER_UNSET_MESSAGE="No Minecraft server has been set yet!",
                #  minecraft_java_server=None,
                 **kwargs):
        super().__init__(**kwargs)
        self._SERVER_UNSET_MESSAGE = "No Minecraft server has been set yet!"
        self._SERVER_CONNECT_FAIL_MESSAGE = "Could not connect to that address's Minecraft server!"
        self.minecraft_java_server: JavaServer = None

        # Fill in `timestamp`, author information, title
        self._template_embed = \
            Embed(color=Color.green(), title="Insert text here") \
                .set_footer(text="Minecraft Looking For Group Bot") \
                .set_thumbnail(url="https://static.wikia.nocookie.net/minecraft_gamepedia/images/a/a4/Grass_Block_%28item%29_BE5.png/revision/latest?cb=20200901112517")
                # .add_field(name="Interested Players:", value="No interested players yet... Be the first!", inline=False)
        
        self.server_icon: File = self.update_icon('')
        self.SERVER_UNSET_EMBED = \
            self.template_embed(title=self._SERVER_UNSET_MESSAGE) \
            .set_thumbnail(url="https://static.wikia.nocookie.net/minecraft_gamepedia/images/9/9e/Barrier_%28held%29_JE2_BE2.png/revision/latest?cb=20221216145252")
        self.SERVER_CONNECT_FAIL_EMBED = \
            self.template_embed(title=self._SERVER_CONNECT_FAIL_MESSAGE) \
            .set_thumbnail(url="https://static.wikia.nocookie.net/minecraft_gamepedia/images/9/9e/Barrier_%28held%29_JE2_BE2.png/revision/latest?cb=20221216145252")
        
    
    def template_embed(self, *, title="Insert text here") -> Embed:
        rv = self._template_embed.copy()
        rv.timestamp = datetime.now()
        rv.title = title
        return rv
    
    def update_icon(self, filename: str) -> File:
        try:
            decoded = base64.b64decode(self.minecraft_java_server.status().icon.removeprefix("data:image/png;base64,"))
            with open("server-icon.png", "wb") as write_file:
                write_file.write(decoded)
            read_file = open("server-icon.png", "rb")
            self.server_icon = File(read_file, filename=filename)
            read_file.close()
        except:
            # logging.error("Error creating server icon! Defaulting to question mark...")
            default_file = open("default-icon.png", "rb")
            self.server_icon = File(default_file)
            default_file.close()
        return self.server_icon

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
        return f"{address.host.split('_tcp.')[-1]}{'' if address.port == 25565 else ':' + str(address.port)}"
