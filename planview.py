import discord
from typing import Self

class PlanView(discord.ui.View):
    def __init__(self, creator_id: int, embed: discord.Embed, message: discord.Message = None, **kwargs):
        super().__init__(**kwargs)
        self.creator_id = creator_id
        self.embed = embed
        self.message = message
        self.interested_players = set()
        self._NONE_INTERESTED_MSG = self.embed.fields[0].value if self.embed.fields else ""
        self.interested_players_string = self._NONE_INTERESTED_MSG

    async def _update_embed(self) -> Self:
        """
        Edits the embed/associated message after a presumably updated interested player set.
        TODO: Current implementation may be inefficient? O(n) every time somebody is interested
    """
        name = "Interested Players:"
        self.interested_players_string = "" if self.interested_players else self._NONE_INTERESTED_MSG
        for i, player_id in enumerate(self.interested_players):
            self.interested_players_string += \
                f"{', ' if i != 0 else ''}<@{player_id}>"

        if self.embed.fields:
            self.embed.set_field_at(0, name=name, value=self.interested_players_string, inline=False)
        else:
            self.embed.add_field(name=name, value=self.interested_players_string, inline=False)
        
        if self.message:
            await self.message.edit(view=self, embed=self.embed)
        return self
    
    def set_message(self, message: discord.Message) -> Self:
        self.message = message
        return self
    
    async def add_interested_player(self, player_id: int) -> Self:
        # self.interested_players_string += \
        #     f"{', ' if self.interested_players else ''}{player.display_name}"
        self.interested_players.add(player_id)
        return await self._update_embed()
    
    async def remove_interested_player(self, player_id: int) -> Self:
        self.interested_players.remove(player_id)
        return await self._update_embed()

    @discord.ui.button(style=discord.ButtonStyle.green, label="I'm Interested!")

    async def interested(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id == self.creator_id:
            await interaction.response.send_message(
                content="Action failed. Plan creator is already assumed to be interested in their own plan.",
                ephemeral=True,delete_after=6)
            
        elif interaction.user.id not in self.interested_players:
            await self.add_interested_player(interaction.user.id)
            await interaction.response.send_message(
                content="You have been marked as interested for this plan.\nYou will be pinged at the start of the plan.",
                ephemeral=True,delete_after=10)
        else:
            await interaction.response.send_message(
                content="You are already interested!",
                ephemeral=True,delete_after=6)
            
        
    @discord.ui.button(style=discord.ButtonStyle.red, label="I'm No Longer Interested...")

    async def not_interested(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id in self.interested_players:
            await self.remove_interested_player(interaction.user.id)            
            await interaction.response.send_message(
                content="You are no longer interested for this plan.",
                ephemeral=True,delete_after=10)
        else:
            await interaction.response.send_message(
                content="You are already not interested!",
                ephemeral=True,delete_after=6)


    @discord.ui.button(style=discord.ButtonStyle.blurple, label="Start Plan")

    async def start(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id == self.creator_id:
            if not self.interested_players:
                await interaction.response.send_message(
                    content="You can't start a plan that has nobody interested!"
                        "\nIf you created the plan by accident, consider cancelling the plan.",
                    ephemeral=True,delete_after=10)
                return
            
            self.embed.clear_fields()
            self.embed.description = \
                f"Hey <@{self.creator_id}> and {self.interested_players_string}!\nThe event has started!"

            await interaction.response.send_message(embed=self.embed)
            await self.message.delete()
            self.stop()
        else:
            await interaction.response.send_message(
                content="You don't have permission to do that.",
                ephemeral=True,delete_after=6)
    

    @discord.ui.button(style=discord.ButtonStyle.grey, label="Cancel Plan")

    async def cancel(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id == self.creator_id:
            self.embed.clear_fields()
            self.embed.description = "**This plan has been canceled.**"
                # f"""Hey {' '.join([f'<@{user}>' for user in self.interested_players])}!
            await interaction.response.send_message(embed=self.embed)
            await self.message.delete()
            self.stop()
        else:
            await interaction.response.send_message(
                content="You don't have permission to do that.",
                ephemeral=True,delete_after=6)
            