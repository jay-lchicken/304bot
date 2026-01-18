import discord
import os
import traceback

from discord import Interaction
from discord._types import ClientT
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('TOKEN')
TEST_GUILD_ID = 1461946310092390462
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


class ModalButtonView(discord.ui.View):
    @discord.ui.button(label="Fill up the form!", style=discord.ButtonStyle.green)
    async def button_clicked(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(WhoDidYouMeetModal())


class WhoDidYouMeetModal(discord.ui.Modal, title="Who Did You Meet?"):
    name = discord.ui.TextInput(label="Name", placeholder="Who Did You Meet?")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"You met: {self.name.value}", ephemeral=True)


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
    name="hi",
    description="Say hi",
    guild=discord.Object(id=TEST_GUILD_ID),
)
async def hi_slash(interaction: discord.Interaction):
    await interaction.response.send_message("Did you meet anyone?", view=ModalButtonView())


bot.run(TOKEN)

