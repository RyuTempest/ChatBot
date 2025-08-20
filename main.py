"""
Main entry point for the Discord AI Chatbot.
Handles bot initialization, cog loading, and error handling.
"""

import discord
from discord.ext import commands
import asyncio
import logging
import sys
from pathlib import Path

from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class DiscordAIBot(commands.Bot):
    """Main Discord AI Chatbot class."""
    
    def __init__(self):
        """Initialize the Discord bot."""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix="!",  # Fallback prefix (slash commands are primary)
            intents=intents,
            help_command=None  # We'll implement our own help command
        )
        
        logger.info("Discord AI Bot initialized")
    
    async def setup_hook(self):
        """Setup hook called when the bot is starting up."""
        try:
            # Load the chat cog
            await self.load_extension("cogs.chat")
            logger.info("Chat cog loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load chat cog: {e}")
            sys.exit(1)
    
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f"Bot is ready! Logged in as {self.user}")
        logger.info(f"Bot ID: {self.user.id}")
        logger.info(f"Connected to {len(self.guilds)} guild(s)")
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name="AI Chat | /help"
            )
        )
    
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """Global error handler for command errors."""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore command not found errors
        
        logger.error(f"Command error in {ctx.command}: {error}")
        
        # Send user-friendly error message
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ I don't have the required permissions to execute this command.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ This command is on cooldown. Try again in {error.retry_after:.2f} seconds.")
        else:
            await ctx.send("❌ An error occurred while executing this command. Please try again later.")
    
    async def on_guild_join(self, guild: discord.Guild):
        """Called when the bot joins a new guild."""
        logger.info(f"Joined new guild: {guild.name} (ID: {guild.id})")
        
        # Try to sync commands for the new guild
        try:
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logger.info(f"Synced commands for guild: {guild.name}")
        except Exception as e:
            logger.error(f"Failed to sync commands for guild {guild.name}: {e}")
    
    async def on_guild_remove(self, guild: discord.Guild):
        """Called when the bot leaves a guild."""
        logger.info(f"Left guild: {guild.name} (ID: {guild.id})")

async def main():
    """Main function to run the bot."""
    try:
        # Validate configuration
        if not config.is_valid:
            logger.error("Invalid configuration. Please check your environment variables.")
            sys.exit(1)
        
        # Create and run the bot
        bot = DiscordAIBot()
        
        # Run the bot
        async with bot:
            await bot.start(config.discord_token)
            
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())
