"""
Main entry point for the Discord bot.
"""
import asyncio
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger('discord')

# Load environment variables
load_dotenv()

class QuranBot(commands.Bot):
    """
    A scalable Python Discord bot project.
    """
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or('!'),
            intents=discord.Intents.default(),
            help_command=None
        )

    async def setup_hook(self):
        """
        Setup hook to automatically load all cogs from the `cogs/` directory.
        """
        # Ensure cogs directory exists
        if not os.path.exists('./cogs'):
            os.makedirs('./cogs')
            
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and not filename.startswith('__'):
                cog_name = f'cogs.{filename[:-3]}'
                try:
                    await self.load_extension(cog_name)
                    logger.info(f"Loaded cog: {cog_name}")
                except Exception as e:
                    logger.exception(f"Failed to load cog {cog_name}")

        # Sync the app commands with Discord.
        await self.tree.sync()
        logger.info("Application commands synced.")

    async def on_ready(self):
        """
        Event triggered when the bot is ready.
        """
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info("------")


def main():
    """
    Main function to run the bot.
    """
    token = os.getenv('DISCORD_TOKEN')
    if not token or token == 'your_token_here':
        logger.error("Please set a valid DISCORD_TOKEN in the environment variables.")
        return

    bot = QuranBot()
    bot.run(token)


if __name__ == '__main__':
    main()
