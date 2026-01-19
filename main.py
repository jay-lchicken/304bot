from tkinter.font import names

import discord
import os
import traceback
from discord import app_commands
from discord import Interaction
from discord._types import ClientT
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('TOKEN')
TEST_GUILD_ID = os.getenv('TEST_GUILD_ID')
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

class ModalButtonView(discord.ui.View):
    def __init__(self, names: list[str]):
        super().__init__(timeout=180)
        self.names = names
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
        self.name_select.callback = self.on_select  # bind callback
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
            WhoDidYouMeetModal(self.selected_name)
        )
        self.submit_button.disabled = True
        self.name_select.disabled = True
        await interaction.edit_original_response(view=self)


class WhoDidYouMeetModal(discord.ui.Modal, title="Who Did You Meet?"):
    def __init__(self, selected_name: str):
        super().__init__(timeout=300)
        self.selected_name = selected_name

        self.details = discord.ui.TextInput(
            label=f"Anything about {self.selected_name}?",
            required=False,
        )
        self.add_item(self.details)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"You met: {self.selected_name}",
            ephemeral=True,
        )


@bot.event
async def on_ready():
    await bot.wait_until_ready()

    guild = discord.Object(id=TEST_GUILD_ID)
    synced = await bot.tree.sync(guild=guild)
    print(f"Synced {len(synced)} commands to guild {TEST_GUILD_ID}")
    print(f"Logged in as {bot.user}")


@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")


@bot.command()
async def kyle(ctx):
    await ctx.send("hiiiiii kylee!")


@bot.command()
async def joshua(ctx):
    await ctx.send("hiiiiii joshua!")


@bot.command()
async def hi(ctx):
    await ctx.send("hi!")


@bot.command(name="members")
@commands.guild_only()
async def list_members(ctx: commands.Context):
    guild = ctx.guild
    members = guild.members
    total = len(members)

    first_20_names = [m.display_name for m in members[:20]]
    names_text = ", ".join(first_20_names) if first_20_names else "No members found."

    await ctx.send(f"Total members: {total}\nFirst 20: {names_text}")
@bot.tree.command(
    name="bonding-checkin",
    description="Only Exco can use this",
    guild=discord.Object(id=TEST_GUILD_ID),
)
@app_commands.checks.has_role("Exco")
async def hi_slash(interaction: discord.Interaction):
    guild = interaction.guild
    members = guild.members
    names = [m.display_name for m in members[:25]]
    print(names)


    await interaction.response.send_message("Who did you meet this week?", view=ModalButtonView(names), ephemeral=False)
@hi_slash.error
async def hi_slash_error(interaction, error):
    if isinstance(error, app_commands.MissingRole):
        await interaction.response.send_message("You need the Exco role.", ephemeral=True)
bot.run(TOKEN)

