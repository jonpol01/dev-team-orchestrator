"""
Minimal Discord bot that forwards $team/$ralph commands to the n8n webhook.
Runs locally — no public URL needed.

Usage:
    pip install discord.py aiohttp
    export DISCORD_BOT_TOKEN="your-bot-token"
    python bot.py
"""

import os
import discord
import aiohttp

DISCORD_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")
WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL", "http://127.0.0.1:5678/webhook/4d673d7b-404c-4f90-8d16-298e98d41bf1")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Bot connected as {client.user}")
    print(f"Forwarding to: {WEBHOOK_URL}")


@client.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.strip()
    if not (content.startswith("$team") or content.startswith("$ralph")):
        return

    payload = {
        "content": content,
        "channelId": str(message.channel.id),
        "author": {"username": message.author.name},
        "guildId": str(message.guild.id) if message.guild else None,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(WEBHOOK_URL, json=payload) as resp:
                if resp.status == 200:
                    await message.add_reaction("👍")
                else:
                    await message.add_reaction("❌")
                    print(f"Webhook returned {resp.status}: {await resp.text()}")
    except Exception as e:
        await message.add_reaction("❌")
        print(f"Error: {e}")


if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("Set DISCORD_BOT_TOKEN environment variable")
        exit(1)
    client.run(DISCORD_TOKEN)
