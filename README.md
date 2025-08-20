# 🤖 Discord AI Chatbot

A powerful Discord bot powered by OpenAI's GPT-4 (or GPT-3.5) that provides intelligent chat responses using slash commands.

## ✨ Features

- **AI-Powered Chat**: Intelligent responses using OpenAI's latest language models
- **Slash Commands**: Modern Discord slash command interface
- **Web Interface**: Beautiful, responsive web UI for desktop and mobile
- **Conversation Memory**: Remembers conversation context for each user
- **Smart Message Splitting**: Automatically splits long responses to fit Discord's limits
- **Real-time Chat**: Live chat interface with typing indicators and smooth animations
- **Dashboard**: Comprehensive statistics and system monitoring
- **Settings Management**: Customizable bot preferences and API configurations
- **Error Handling**: Comprehensive error handling and user-friendly error messages
- **Logging**: Detailed logging for debugging and monitoring
- **Production Ready**: Clean, modular code structure with proper error handling

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Discord Bot Token
- OpenAI API Key
- Discord Server (where you have admin permissions)

### 1. Clone or Download

Download this project to your local machine.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Setup

1. Copy `env.example` to `.env`:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` and add your tokens:
   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4
   ```

### 4. Run the Bot

**Discord Bot:**
```bash
python main.py
```

**Web Interface:**
```bash
python web_server.py
```

The web interface will be available at: http://localhost:5000

## 🔧 Setup Instructions

### Creating a Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section
4. Click "Add Bot"
5. Copy the bot token (you'll need this for the `.env` file)
6. Under "Privileged Gateway Intents", enable:
   - Message Content Intent
   - Server Members Intent
7. Save changes

### Bot Permissions

Your bot needs these permissions:
- Send Messages
- Use Slash Commands
- Read Message History
- Embed Links
- Attach Files

### Adding Bot to Your Server

1. Go to the "OAuth2" → "URL Generator" section
2. Select "bot" under scopes
3. Select the permissions listed above
4. Copy the generated URL and open it in your browser
5. Select your server and authorize the bot

### Getting OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Go to "API Keys" section
4. Create a new API key
5. Copy the key (you'll need this for the `.env` file)

## 📚 Commands

### `/chat [message]`
Chat with the AI assistant. The bot will respond with intelligent, contextual responses.

**Example:**
```
/chat What's the weather like today?
```

### `/clear`
Clear your conversation history with the AI. Useful for starting fresh conversations.

### `/help`
Display help information and available commands.

## 🏗️ Project Structure

```
chatbot/
├── main.py              # Main bot entry point
├── config.py            # Configuration and environment variables
├── cogs/
│   ├── __init__.py      # Package initialization
│   └── chat.py          # Chat functionality cog
├── web_server.py        # Flask web server for web interface
├── static/              # Web interface assets
│   ├── css/
│   │   └── style.css    # Modern CSS styles
│   └── js/
│       └── app.js       # Interactive JavaScript
├── templates/           # HTML templates
│   └── index.html       # Main web interface
├── requirements.txt      # Python dependencies
├── env.example          # Environment variables template
├── start.bat            # Windows script to start Discord bot
├── start_web.bat        # Windows script to start web interface
├── README.md            # This file
└── bot.log              # Log file (created when bot runs)
```

## 🔍 Troubleshooting

### Common Issues

**Bot doesn't respond to commands:**
- Check if the bot has the correct permissions
- Ensure slash commands are synced (check bot logs)
- Verify the bot is online and connected

**OpenAI API errors:**
- Check your API key is correct
- Ensure you have sufficient API credits
- Check if the API key has the correct permissions

**Environment variable errors:**
- Make sure `.env` file exists and is in the project root
- Verify all required variables are set
- Check for typos in variable names

### Logs

The bot creates detailed logs in `bot.log`. Check this file for:
- Bot startup information
- Command execution logs
- Error details
- API response information

## 🚀 Deployment

### Local Development

**Discord Bot:**
```bash
python main.py
```

**Web Interface:**
```bash
python web_server.py
```

### Production Deployment
For production deployment, consider:
- Using a process manager like PM2 or systemd
- Setting up proper logging rotation
- Using environment variables instead of `.env` files
- Running behind a reverse proxy if needed
- Using a production WSGI server like Gunicorn for the web interface

### Docker (Optional)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

## 📝 Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DISCORD_TOKEN` | Discord bot token | - | Yes |
| `OPENAI_API_KEY` | OpenAI API key | - | Yes |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4` | No |

### Supported OpenAI Models
- `gpt-4` (recommended)
- `gpt-4-turbo`
- `gpt-3.5-turbo`
- `gpt-3.5-turbo-16k`

## 🤝 Contributing

Feel free to contribute to this project by:
- Reporting bugs
- Suggesting new features
- Submitting pull requests
- Improving documentation

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Review the bot logs in `bot.log`
3. Ensure all dependencies are installed correctly
4. Verify your environment variables are set properly

## 🔄 Updates

To update the bot:
1. Download the latest version
2. Update your `.env` file if needed
3. Restart the bot

---

**Happy chatting! 🤖💬**
