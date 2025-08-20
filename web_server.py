"""
Flask web server for the Discord AI Chatbot web interface.
Provides a modern web UI for interacting with the AI chatbot.
"""

from flask import Flask, render_template, jsonify, request, session, send_from_directory
import os
from datetime import datetime
import logging
from config import config
from flask_cors import CORS

# Provider SDKs
from openai import OpenAI
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Enable CORS for API routes (allow React dev server to call Flask APIs)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Store conversation history (in production, use a proper database)
conversation_history = {}

# Initialize AI providers (server-side only)
openai_client = None
if config.ai_provider == 'openai':
    openai_client = OpenAI(api_key=config.openai_api_key)
elif config.ai_provider == 'gemini':
    genai.configure(api_key=config.gemini_api_key)

@app.route('/')
def index():
    """Main page route (serves the classic Jinja UI)."""
    try:
        current_time = datetime.now().strftime("%I:%M %p")
        return render_template('index.html', current_time=current_time)
    except Exception as e:
        logger.error(f"Error rendering index page: {e}")
        return "Error loading page", 500

# Optional: Serve built React app (production) if available
REACT_BUILD_DIR = os.path.join(os.path.dirname(__file__), 'frontend', 'dist')

@app.route('/app')
def serve_react_index():
    """Serve the React SPA if it's built (visit /app)."""
    index_path = os.path.join(REACT_BUILD_DIR, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(REACT_BUILD_DIR, 'index.html')
    return (
        "React build not found. Run 'cd frontend && npm install && npm run build' first.",
        404,
    )

@app.route('/assets/<path:filename>')
def serve_react_assets(filename: str):
    """Serve static assets for the built React app."""
    if os.path.exists(os.path.join(REACT_BUILD_DIR, 'assets', filename)):
        return send_from_directory(os.path.join(REACT_BUILD_DIR, 'assets'), filename)
    return "Not found", 404

@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint for chat functionality."""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        user_id = session.get('user_id', 'anonymous')
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Store user message
        if user_id not in conversation_history:
            conversation_history[user_id] = []
        
        conversation_history[user_id].append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Generate AI response via OpenAI (with fallback)
        ai_response = generate_ai_response(user_id, message)
        
        # Store AI response
        conversation_history[user_id].append({
            'role': 'ai',
            'content': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"Chat message processed for user {user_id}")
        
        return jsonify({
            'response': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in chat API: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/status')
def status():
	"""API endpoint for bot status."""
	try:
		# Check if Discord bot is running (simulate for now)
		discord_status = 'online'  # Replace with actual Discord bot status check
		ai_status = 'online'
		
		return jsonify({
			'discord': discord_status,
			'provider': config.ai_provider,
			'model': config.openai_model if config.ai_provider == 'openai' else config.gemini_model,
			'ai_status': ai_status,
			'timestamp': datetime.now().isoformat()
		})
		
	except Exception as e:
		logger.error(f"Error in status API: {e}")
		return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/stats')
def stats():
	"""API endpoint for bot statistics."""
	try:
		total_messages = sum(len(conv) for conv in conversation_history.values())
		unique_users = len(conversation_history)
		
		return jsonify({
			'total_messages': total_messages,
			'unique_users': unique_users,
			'timestamp': datetime.now().isoformat()
		})
		
	except Exception as e:
		logger.error(f"Error in stats API: {e}")
		return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/history')
def history():
	"""API endpoint for conversation history."""
	try:
		user_id = session.get('user_id', 'anonymous')
		user_history = conversation_history.get(user_id, [])
		
		return jsonify({
			'history': user_history,
			'timestamp': datetime.now().isoformat()
		})
		
	except Exception as e:
		logger.error(f"Error in history API: {e}")
		return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/clear-history', methods=['POST'])
def clear_history():
	"""API endpoint for clearing conversation history."""
	try:
		user_id = session.get('user_id', 'anonymous')
		
		if user_id in conversation_history:
			del conversation_history[user_id]
		
		logger.info(f"History cleared for user {user_id}")
		
		return jsonify({
			'message': 'History cleared successfully',
			'timestamp': datetime.now().isoformat()
		})
		
	except Exception as e:
		logger.error(f"Error in clear history API: {e}")
		return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
	"""API endpoint for user settings."""
	try:
		user_id = session.get('user_id', 'anonymous')
		
		if request.method == 'GET':
			# Return current settings
			user_settings = get_user_settings(user_id)
			return jsonify(user_settings)
		
		elif request.method == 'POST':
			# Update settings
			data = request.get_json()
			update_user_settings(user_id, data)
			
			logger.info(f"Settings updated for user {user_id}")
			
			return jsonify({
				'message': 'Settings updated successfully',
				'timestamp': datetime.now().isoformat()
			})
			
	except Exception as e:
		logger.error(f"Error in settings API: {e}")
		return jsonify({'error': 'Internal server error'}), 500

def _build_messages(user_id: str, current_message: str) -> list:
	"""Build messages array with system prompt and recent history."""
	messages = [
		{
			"role": "system",
			"content": (
				"You are a helpful AI assistant in a Discord/web app. "
				"Be concise, friendly, and accurate."
			),
		}
	]
	# include last 10 exchanges if available
	history = conversation_history.get(user_id, [])[-20:]
	for item in history:
		role = 'assistant' if item.get('role') == 'ai' else item.get('role', 'user')
		content = item.get('content', '')
		if content:
			messages.append({"role": role, "content": content})
	messages.append({"role": "user", "content": current_message})
	return messages


def generate_ai_response(user_id: str, message: str) -> str:
	"""Generate AI response using the configured provider (OpenAI or Gemini)."""
	messages = _build_messages(user_id, message)

	try:
		if config.ai_provider == 'openai':
			model = (getattr(config, 'openai_model', None) or 'gpt-4o-mini').strip()
			resp = openai_client.chat.completions.create(
				model=model,
				messages=messages,
				max_tokens=800,
				temperature=0.7,
			)
			text = (resp.choices[0].message.content or '').strip()
			if text:
				return text
			raise RuntimeError('Empty response from OpenAI')

		elif config.ai_provider == 'gemini':
			model_name = (getattr(config, 'gemini_model', None) or 'gemini-1.5-flash').strip()
			# Flatten messages to a single prompt with simple speaker tags
			system_instructions = ""
			history_parts = []
			for m in messages:
				role = m.get('role')
				content = m.get('content', '')
				if role == 'system':
					system_instructions = content
				elif role == 'user':
					history_parts.append(f"User: {content}")
				elif role == 'assistant':
					history_parts.append(f"Assistant: {content}")
			prompt = "\n".join([p for p in history_parts if p])

			model = genai.GenerativeModel(model_name=model_name, system_instruction=system_instructions or None)
			result = model.generate_content(prompt)
			text = (getattr(result, 'text', None) or '').strip()
			if text:
				return text
			# Fallback extraction from candidates if needed
			if hasattr(result, 'candidates') and result.candidates:
				parts = []
				for cand in result.candidates:
					try:
						parts.append(cand.content.parts[0].text)
					except Exception:
						continue
				text = "\n".join([p for p in parts if p]).strip()
				if text:
					return text
			raise RuntimeError('Empty response from Gemini')

		else:
			raise ValueError(f"Unsupported AI provider: {config.ai_provider}")

	except Exception as e:
		logger.error(f"AI error via provider {config.ai_provider}: {e}")
		hint = " Verify API keys, model names, and outbound network connectivity."
		return "The AI service is currently unavailable." + hint

def get_user_settings(user_id):
	"""Get user settings (placeholder implementation)."""
	# In production, load from database
	return {
		'bot_name': 'Discord AI Bot',
		'response_style': 'friendly',
		'openai_model': 'gpt-4',
		'response_length': 'medium',
		'memory_enabled': True,
		'typing_indicator': True,
		'auto_scroll': True
	}

def update_user_settings(user_id, settings):
	"""Update user settings (placeholder implementation)."""
	# In production, save to database
	logger.info(f"Settings updated for user {user_id}: {settings}")
	pass

@app.errorhandler(404)
def not_found(error):
	"""Handle 404 errors."""
	return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
	"""Handle 500 errors."""
	logger.error(f"Internal server error: {error}")
	return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
	try:
		# Check if configuration is valid
		if not config.is_valid:
			logger.error("Invalid configuration. Please check your environment variables.")
			exit(1)
		
		logger.info("Starting Discord AI Chatbot web server...")
		
		# Run the Flask app
		app.run(
			host='0.0.0.0',
			port=5000,
			debug=False,  # Set to False in production
			threaded=True
		)
		
	except Exception as e:
		logger.error(f"Failed to start web server: {e}")
		exit(1)
