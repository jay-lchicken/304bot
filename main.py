import discord
import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from db import (
    fetch_connection_rows,
    fetch_distinct_usernames_between,
    insert_connection_row,
)
load_dotenv()
TOKEN = os.getenv('TOKEN')
TEST_GUILD_ID = os.getenv('TEST_GUILD_ID')
DATABASE_URL = os.getenv("DATABASE_URL")
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


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
    description="Submit who you met this week",
    guild=discord.Object(id=TEST_GUILD_ID),
)
@app_commands.describe(
    met_name="Name of the person you met",
    details="Optional details about the meeting",
)
async def bonding_checkin(
    interaction: discord.Interaction,
    met_name: str,
    details: str | None = None,
):
    await interaction.response.defer(ephemeral=True)

    if not DATABASE_URL:
        await interaction.followup.send(
            "DATABASE_URL is not set. Please configure it before submitting.",
            ephemeral=True,
        )
        return

    cleaned_details = details.strip() if details else None
    try:
        await insert_connection_row(
            DATABASE_URL,
            interaction.user.name,
            met_name,
            cleaned_details,
        )
    except Exception as exc:
        await interaction.followup.send(
            f"Failed to save your response: {exc}",
            ephemeral=True,
        )
        return

    await interaction.followup.send(
        f"Recorded: you met {met_name}.",
        ephemeral=True,
    )

@bot.tree.command(
    name="bonding-checkresponses",
    description="Only Exco can use this",
    guild=discord.Object(id=TEST_GUILD_ID),
)
@app_commands.checks.has_role("EXCO")
async def check_responses(interaction: discord.Interaction):
    guild = interaction.guild
    members = guild.members
    names = [m.display_name for m in members[:25]]
    print(names)

    await interaction.response.defer(ephemeral=True)

    if not DATABASE_URL:
        await interaction.followup.send(
            "DATABASE_URL is not set. Please configure it before checking responses.",
            ephemeral=True,
        )
        return
    try:
        rows = await fetch_connection_rows(DATABASE_URL)
    except Exception as exc:
        await interaction.followup.send(
            f"Failed to fetch responses: {exc}",
            ephemeral=True,
        )
        return
    if not rows:
        await interaction.followup.send("No responses yet.", ephemeral=True)
        return
    lines = ""
    for username, met_name, details, date_added in rows:
        details_text = f" - {details}" if details else ""
        lines+= f"{date_added:%Y-%m-%d %H:%M} | {username} met {met_name}{details_text} \n"

    await interaction.followup.send(
        f"Total responses: {len(rows)}",
        ephemeral=True,
    )
    await interaction.followup.send(lines, ephemeral=True)
@check_responses.error
async def check_responses_error(interaction, error):
    if isinstance(error, app_commands.MissingRole):
        await interaction.response.send_message("You need the Exco role.", ephemeral=True)


@bot.tree.command(
    name="bonding-missing",
    description="Show members missing this week's submissions",
    guild=discord.Object(id=TEST_GUILD_ID),
)
@app_commands.checks.has_role("EXCO")
async def bonding_missing(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    if not DATABASE_URL:
        await interaction.followup.send(
            "DATABASE_URL is not set. Please configure it before checking missing submissions.",
            ephemeral=True,
        )
        return

    sgt = ZoneInfo("Asia/Singapore")
    now_sgt = datetime.now(sgt)
    week_start_sgt = datetime(
        now_sgt.year,
        now_sgt.month,
        now_sgt.day,
        tzinfo=sgt,
    ) - timedelta(days=now_sgt.weekday())
    week_start_utc = week_start_sgt.astimezone(timezone.utc)
    now_utc = datetime.now(timezone.utc)

    try:
        submitted_usernames = await fetch_distinct_usernames_between(
            DATABASE_URL,
            week_start_utc,
            now_utc,
        )
    except Exception as exc:
        await interaction.followup.send(
            f"Failed to fetch submissions: {exc}",
            ephemeral=True,
        )
        return

    guild = interaction.guild
    members = guild.members
    missing_members = [
        member for member in members
        if member.name not in submitted_usernames
    ]

    if not missing_members:
        await interaction.followup.send(
            "Everyone has submitted at least once this week.",
            ephemeral=True,
        )
        return

    names = sorted(member.display_name for member in missing_members)
    lines = "\n".join(f"- {name}" for name in names)

    await interaction.followup.send(
        f"Missing this week (SGT): {len(names)}",
        ephemeral=True,
    )
    await interaction.followup.send(lines, ephemeral=True)


@bonding_missing.error
async def bonding_missing_error(interaction, error):
    if isinstance(error, app_commands.MissingRole):
        await interaction.response.send_message("You need the Exco role.", ephemeral=True)
bot.run(TOKEN)
