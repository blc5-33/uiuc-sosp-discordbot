from discord.ext import commands
from mcstatus import JavaServer

class MinecraftBot(commands.Bot):
    def __init__(self, 
                #  SERVER_UNSET_MESSAGE="No Minecraft server has been set yet!",
                #  minecraft_java_server=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.SERVER_UNSET_MESSAGE = "No Minecraft server has been set yet!"
        self.SERVER_CONNECT_FAIL_MESSAGE = "Could not connect to that address's Minecraft server!"
        self.minecraft_java_server: JavaServer = None
    
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
