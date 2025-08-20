# 🤖 Discord AI Chatbot with Web Interface

A feature-rich Discord bot powered by OpenAI's GPT models (or Gemini) that provides intelligent chat responses. It also includes a modern web interface for interacting with the bot outside of Discord.

## ✨ Features

- **AI-Powered Chat**: Supports OpenAI and Gemini AI providers for intelligent, context-aware responses
- **Discord Slash Commands**: Modern and intuitive command interface for Discord users
- **Web Interface**: A responsive web UI for interacting with the chatbot
- **Conversation Memory**: Remembers user-specific conversation history for better context
- **Customizable AI Models**: Choose from a variety of OpenAI and Gemini models
- **Settings Management**: Easily configure bot preferences and API settings
- **Error Handling**: Comprehensive error handling with detailed logs
- **Extensible Design**: Modular structure for adding new features or AI providers

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Discord Bot Token
- OpenAI or Gemini API Key
- Admin access to a Discord server

### 1. Clone the Repository

Download the project to your local machine:

```bash
git clone https://github.com/your-username/discord-ai-chatbot.git
cd discord-ai-chatbot
```

### 2. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Edit `.env` and add your credentials:

```env
DISCORD_TOKEN=your_discord_bot_token
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5
```

### 4. Run the Bot

**Discord Bot**:
```bash
python bot.py
```

**Web Interface**:
```bash
python app.py
```

The web interface will be available at: http://localhost:5000

## 🏗️ Project Structure

```
discord-ai-chatbot/
├── bot.py              # Discord bot main file
├── app.py              # Web interface application
├── requirements.txt    # Python dependencies
├── .env.example       # Example environment variables
├── static/            # Web assets (CSS, JS)
├── templates/         # HTML templates
├── logs/             # Log files
└── README.md         # This file
```

## 📚 Commands

### Discord Slash Commands

- `/chat [message]`: Chat with the AI assistant
  - Example: `/chat What's the weather like today?`
- `/clear`: Clear your conversation history with the bot
- `/help`: Display help information and available commands

## 🔧 Setup Instructions

### Creating a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application and add a bot
3. Copy the bot token and add it to your `.env` file
4. Enable the following intents under "Privileged Gateway Intents":
   - Message Content Intent
   - Server Members Intent
5. Save changes

### Adding the Bot to Your Server

1. Go to the "OAuth2" → "URL Generator" section
2. Select "bot" under scopes and assign the following permissions:
   - Send Messages
   - Use Slash Commands
   - Read Message History
   - Embed Links
   - Attach Files
3. Copy the generated URL, open it in your browser, and invite the bot to your server

### Getting OpenAI or Gemini API Keys

- **OpenAI**: Visit the [OpenAI Platform](https://platform.openai.com/api-keys) to generate an API key
- **Gemini**: Refer to the [Gemini documentation](https://ai.google.dev/gemini-api/docs/api-key) for API key setup

## 🔍 Troubleshooting

### Common Issues

- **Bot doesn't respond**:
  - Ensure the bot has the correct permissions
  - Verify the bot is online and connected to Discord
  - Check the logs in `bot.log`

- **API errors**:
  - Ensure your API key is valid and has sufficient credits
  - Verify the AI model name in the `.env` file

- **Environment variable errors**:
  - Ensure the `.env` file exists and is correctly configured

### Logs

Detailed logs are saved in `bot.log`. Use these logs to debug issues such as:
- Bot startup errors
- API response issues
- Command execution details

## 📝 Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DISCORD_TOKEN` | Discord bot token | - | Yes |
| `OPENAI_API_KEY` | OpenAI API key | - | Yes |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4` | No |
| `GEMINI_API_KEY` | Gemini API key | - | No |
| `GEMINI_MODEL` | Gemini model to use | `gemini-1.5` | No |

## 🚀 Deployment

### Local Development

Run the bot and web interface locally:

```bash
# Terminal 1 - Discord Bot
python bot.py

# Terminal 2 - Web Interface
python app.py
```

### Production Deployment

For production, consider:
- Using a process manager like `systemd` or `PM2`
- Running the web server with a production WSGI server like Gunicorn
- Setting up a reverse proxy (e.g., Nginx) for the web interface

## 🤝 Contributing

Contributions are welcome! You can help by:
- Reporting bugs
- Suggesting new features
- Submitting pull requests
- Improving documentation

## 📄 License

This project is open source and available under the [MIT License](LICENSE).