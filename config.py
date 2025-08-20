"""
Configuration module for the Discord AI Chatbot.
Loads environment variables and provides configuration settings.
"""

import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

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

class Config:
    """Configuration class for the Discord AI Chatbot."""
    
    def __init__(self):
        """Initialize configuration with environment variables."""
        self.discord_token = os.getenv('DISCORD_TOKEN')

        # AI provider selection: 'openai' or 'gemini'
        self.ai_provider = (os.getenv('AI_PROVIDER', 'openai') or 'openai').strip().lower()

        # OpenAI configuration
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

        # Gemini configuration
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.gemini_model = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
        
        # Validate required configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate that required configuration is present."""
        if not self.discord_token:
            logger.error("DISCORD_TOKEN is not set in environment variables")
            raise ValueError("DISCORD_TOKEN is required")
        
        # Normalize provider
        if self.ai_provider not in ('openai', 'gemini'):
            logger.warning(f"Invalid AI_PROVIDER '{self.ai_provider}', falling back to 'openai'")
            self.ai_provider = 'openai'

        # Provider-specific validation
        if self.ai_provider == 'openai':
            if not self.openai_api_key:
                logger.error("OPENAI_API_KEY is not set in environment variables")
                raise ValueError("OPENAI_API_KEY is required for AI_PROVIDER=openai")

            valid_openai_models = [
                'gpt-4o-mini', 'gpt-4o', 'gpt-4.1-mini', 'gpt-4.1',
                'gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo', 'gpt-3.5-turbo-16k'
            ]
            if self.openai_model not in valid_openai_models:
                logger.warning(f"Invalid OpenAI model '{self.openai_model}', falling back to 'gpt-4o-mini'")
                self.openai_model = 'gpt-4o-mini'
            logger.info(f"Configuration loaded. Provider: openai, Model: {self.openai_model}")

        elif self.ai_provider == 'gemini':
            if not self.gemini_api_key:
                logger.error("GEMINI_API_KEY is not set in environment variables")
                raise ValueError("GEMINI_API_KEY is required for AI_PROVIDER=gemini")

            valid_gemini_models = [
                'gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-1.0-pro', 'gemini-1.5-flash-8b'
            ]
            if self.gemini_model not in valid_gemini_models:
                logger.warning(f"Invalid Gemini model '{self.gemini_model}', falling back to 'gemini-1.5-flash'")
                self.gemini_model = 'gemini-1.5-flash'
            logger.info(f"Configuration loaded. Provider: gemini, Model: {self.gemini_model}")
    
    @property
    def is_valid(self) -> bool:
        """Check if configuration is valid."""
        if self.ai_provider == 'openai':
            return bool(self.discord_token and self.openai_api_key)
        if self.ai_provider == 'gemini':
            return bool(self.discord_token and self.gemini_api_key)
        return False

# Global configuration instance
config = Config()
