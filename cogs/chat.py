"""
Chat cog for the Discord AI Chatbot.
Handles AI chat commands and interactions.
"""

import discord
from discord import app_commands
from discord.ext import commands
import openai
import google.generativeai as genai
import asyncio
import logging
from typing import Optional
import re

from config import config

logger = logging.getLogger(__name__)

class ChatCog(commands.Cog):
    """Cog for handling AI chat functionality."""
    
    def __init__(self, bot: commands.Bot):
        """Initialize the ChatCog."""
        self.bot = bot
        self.openai_client = None
        self.gemini_model = None
        if config.ai_provider == 'openai':
            self.openai_client = openai.AsyncOpenAI(api_key=config.openai_api_key)
        elif config.ai_provider == 'gemini':
            genai.configure(api_key=config.gemini_api_key)
            # Use non-async Google SDK; we'll run calls in executor
            self.gemini_model = genai.GenerativeModel(model_name=config.gemini_model)
        self.conversation_history = {}  # Store conversation history per user
        self.max_history_length = 10    # Maximum conversation history length per user
        
        # Discord character limits
        self.max_message_length = 2000
        self.max_embed_length = 6000
        
        logger.info("ChatCog initialized successfully")
    
    async def _get_ai_response(self, user_id: int, message: str) -> str:
        """
        Get AI response from OpenAI API.
        
        Args:
            user_id: Discord user ID for conversation history
            message: User's message
            
        Returns:
            AI response text
        """
        try:
            # Build conversation context
            messages = self._build_conversation_context(user_id, message)
            
            # Call provider-specific API
            if config.ai_provider == 'openai':
                response = await self.openai_client.chat.completions.create(
                    model=config.openai_model,
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7,
                    timeout=30
                )
                ai_response = response.choices[0].message.content.strip()
            elif config.ai_provider == 'gemini':
                loop = asyncio.get_event_loop()
                # Build prompt from messages
                system_instructions = ""
                parts = []
                for m in messages:
                    role = m.get('role')
                    content = m.get('content', '')
                    if role == 'system':
                        system_instructions = content
                    elif role == 'user':
                        parts.append(f"User: {content}")
                    elif role == 'assistant':
                        parts.append(f"Assistant: {content}")
                prompt = "\n".join(parts)

                # Gemini SDK is sync; run in thread
                def _gen():
                    model = genai.GenerativeModel(
                        model_name=config.gemini_model,
                        system_instruction=system_instructions or None
                    )
                    result = model.generate_content(prompt)
                    text = (getattr(result, 'text', None) or '').strip()
                    if text:
                        return text
                    if hasattr(result, 'candidates') and result.candidates:
                        collected = []
                        for cand in result.candidates:
                            try:
                                collected.append(cand.content.parts[0].text)
                            except Exception:
                                continue
                        return "\n".join([p for p in collected if p]).strip()
                    return ""

                ai_response = await loop.run_in_executor(None, _gen)
                if not ai_response:
                    raise RuntimeError('Empty response from Gemini')
            else:
                raise ValueError(f"Unsupported AI provider: {config.ai_provider}")
            
            # Update conversation history
            self._update_conversation_history(user_id, message, ai_response)
            
            logger.info(f"AI response generated for user {user_id}")
            return ai_response
            
        except openai.RateLimitError:
            logger.error(f"OpenAI rate limit exceeded for user {user_id}")
            return "I'm experiencing high traffic right now. Please try again in a moment."
            
        except openai.APITimeoutError:
            logger.error(f"OpenAI API timeout for user {user_id}")
            return "The AI service is taking longer than expected. Please try again."
            
        except openai.APIError as e:
            logger.error(f"OpenAI API error for user {user_id}: {e}")
            return "I'm experiencing technical difficulties. Please try again later."
            
        except Exception as e:
            logger.error(f"Unexpected error in AI response for user {user_id}: {e}")
            return "An unexpected error occurred. Please try again later."
    
    def _build_conversation_context(self, user_id: int, current_message: str) -> list:
        """
        Build conversation context for OpenAI API.
        
        Args:
            user_id: Discord user ID
            current_message: Current user message
            
        Returns:
            List of message dictionaries for OpenAI API
        """
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant in a Discord server. Be concise, friendly, and helpful. Keep responses under 2000 characters when possible."
            }
        ]
        
        # Add conversation history if available
        if user_id in self.conversation_history:
            for msg in self.conversation_history[user_id]:
                messages.append(msg)
        
        # Add current message
        messages.append({
            "role": "user",
            "content": current_message
        })
        
        return messages
    
    def _update_conversation_history(self, user_id: int, user_message: str, ai_response: str):
        """
        Update conversation history for a user.
        
        Args:
            user_id: Discord user ID
            user_message: User's message
            ai_response: AI's response
        """
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        # Add user message and AI response
        self.conversation_history[user_id].extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": ai_response}
        ])
        
        # Trim history if too long
        if len(self.conversation_history[user_id]) > self.max_history_length * 2:
            self.conversation_history[user_id] = self.conversation_history[user_id][-self.max_history_length * 2:]
    
    def _format_response(self, response: str) -> list[str]:
        """
        Format AI response to fit Discord's character limits.
        
        Args:
            response: Raw AI response
            
        Returns:
            List of formatted message parts
        """
        if len(response) <= self.max_message_length:
            return [response]
        
        # Split response into chunks
        parts = []
        current_part = ""
        
        # Split by sentences first
        sentences = re.split(r'(?<=[.!?])\s+', response)
        
        for sentence in sentences:
            if len(current_part) + len(sentence) + 1 <= self.max_message_length:
                current_part += (sentence + " ").strip()
            else:
                if current_part:
                    parts.append(current_part.strip())
                current_part = sentence + " "
        
        # Add remaining part
        if current_part:
            parts.append(current_part.strip())
        
        return parts
    
    @app_commands.command(
        name="chat",
        description="Chat with the AI assistant"
    )
    @app_commands.describe(
        message="Your message to the AI"
    )
    async def chat_command(
        self,
        interaction: discord.Interaction,
        message: str
    ):
        """
        Slash command to chat with the AI.
        
        Args:
            interaction: Discord interaction object
            message: User's message
        """
        try:
            # Defer response if it might take time
            await interaction.response.defer(thinking=True)
            
            # Get AI response
            ai_response = await self._get_ai_response(interaction.user.id, message)
            
            # Format response for Discord
            response_parts = self._format_response(ai_response)
            
            # Send response
            if len(response_parts) == 1:
                await interaction.followup.send(response_parts[0])
            else:
                # Send multiple messages if response is too long
                for i, part in enumerate(response_parts):
                    if i == 0:
                        await interaction.followup.send(part)
                    else:
                        await interaction.channel.send(part)
                
                await interaction.followup.send("Response split into multiple messages due to length.")
            
            logger.info(f"Chat command executed successfully for user {interaction.user.id}")
            
        except Exception as e:
            logger.error(f"Error in chat command for user {interaction.user.id}: {e}")
            await interaction.followup.send("An error occurred while processing your request. Please try again.")
    
    @app_commands.command(
        name="clear",
        description="Clear your conversation history with the AI"
    )
    async def clear_command(self, interaction: discord.Interaction):
        """Clear conversation history for the user."""
        try:
            user_id = interaction.user.id
            
            if user_id in self.conversation_history:
                del self.conversation_history[user_id]
                await interaction.response.send_message("Your conversation history has been cleared! 🗑️")
                logger.info(f"Conversation history cleared for user {user_id}")
            else:
                await interaction.response.send_message("You don't have any conversation history to clear.")
                
        except Exception as e:
            logger.error(f"Error in clear command for user {interaction.user.id}: {e}")
            await interaction.response.send_message("An error occurred while clearing your history. Please try again.")
    
    @app_commands.command(
        name="help",
        description="Show help information about the AI chatbot"
    )
    async def help_command(self, interaction: discord.Interaction):
        """Show help information."""
        embed = discord.Embed(
            title="🤖 AI Chatbot Help",
            description="Welcome to the AI Chatbot! Here's how to use it:",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="💬 `/chat`",
            value="Chat with the AI assistant. Just type your message!",
            inline=False
        )
        
        embed.add_field(
            name="🗑️ `/clear`",
            value="Clear your conversation history with the AI",
            inline=False
        )
        
        embed.add_field(
            name="❓ `/help`",
            value="Show this help message",
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Features",
            value="• AI-powered responses using OpenAI\n• Conversation memory\n• Automatic message splitting for long responses\n• Error handling and logging",
            inline=False
        )
        
        footer = "Powered by OpenAI" if config.ai_provider == 'openai' else "Powered by Google Gemini"
        embed.set_footer(text=footer)
        
        await interaction.response.send_message(embed=embed)
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Called when the cog is ready."""
        logger.info("ChatCog is ready!")

async def setup(bot: commands.Bot):
    """Setup function for the cog."""
    await bot.add_cog(ChatCog(bot))
