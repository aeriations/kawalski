import os

from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

client = commands.Bot(command_prefix="!", self_bot=True)

@client.event
async def on_ready():
    print(f"""
        READY ->
          CLIENT: {client.user}
          PREFIX: !
    """)

async def load_cogs():
    for file_name in os.listdir('src/disc/cogs'):
        if file_name.endswith('.py'):
            cog = f'disc.cogs.{file_name[:-3]}'
            try:
                await client.load_extension(cog)
            except Exception as e:
                print(f"{e}")

async def main():
    async with client:
        await load_cogs()
        await client.start(TOKEN)

#asyncio run main