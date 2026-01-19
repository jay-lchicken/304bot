import discord

from db import insert_connection_row


class ModalButtonView(discord.ui.View):
    def __init__(self, names: list[str], database_url: str | None):
        super().__init__(timeout=180)
        self.names = names
        self.database_url = database_url
        self.selected_name: str | None = None

        options = [
            discord.SelectOption(label=name, value=name)
            for name in names
        ]

        self.name_select = discord.ui.Select(
            placeholder="Choose who you met",
            min_values=1,
            max_values=1,
            options=options
        )
        self.name_select.callback = self.on_select
        self.add_item(self.name_select)
        self.submit_button = discord.ui.Button(
            label="Submit",
            style=discord.ButtonStyle.green,
        )
        self.submit_button.callback = self.button_clicked
        self.add_item(self.submit_button)

    async def on_select(self, interaction: discord.Interaction):
        self.selected_name = self.name_select.values[0]
        await interaction.response.defer()

    async def button_clicked(self, interaction: discord.Interaction):
        if self.selected_name is None:
            await interaction.response.send_message(
                "Please select a name from the dropdown first.",
                ephemeral=True,
            )
            return
        await interaction.response.send_modal(
            WhoDidYouMeetModal(self.selected_name, self.database_url)
        )
        self.submit_button.disabled = True
        self.name_select.disabled = True
        await interaction.edit_original_response(view=self)


class WhoDidYouMeetModal(discord.ui.Modal, title="Who Did You Meet?"):
    def __init__(self, selected_name: str, database_url: str | None):
        super().__init__(timeout=300)
        self.selected_name = selected_name
        self.database_url = database_url

        self.details = discord.ui.TextInput(
            label=f"Anything about {self.selected_name}?",
            required=False,
        )
        self.add_item(self.details)

    async def on_submit(self, interaction: discord.Interaction):
        username = interaction.user.name
        details = self.details.value.strip() if self.details.value else None

        if not self.database_url:
            await interaction.response.send_message(
                "DATABASE_URL is not set. Please configure it before submitting.",
                ephemeral=True,
            )
            return

        try:
            await insert_connection_row(
                self.database_url,
                username,
                self.selected_name,
                details,
            )
        except Exception as exc:
            await interaction.response.send_message(
                f"Failed to save your response: {exc}",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"You met: {self.selected_name}",
            ephemeral=True,
        )
