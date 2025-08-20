// Discord AI Chatbot Web Interface JavaScript

class DiscordAIBot {
    constructor() {
        this.currentView = 'chat';
        this.conversationHistory = [];
        this.settings = this.loadSettings();
        this.isTyping = false;
        this.typingTimeout = null;
        
        this.initializeEventListeners();
        this.loadConversationHistory();
        this.updateStats();
        this.startStatusCheck();
    }

    // Initialize event listeners
    initializeEventListeners() {
        // Chat input handling
        const chatInput = document.getElementById('chatInput');
        const sendButton = document.getElementById('sendButton');

        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        chatInput.addEventListener('input', () => {
            this.adjustTextareaHeight(chatInput);
        });

        // Auto-resize textarea
        this.adjustTextareaHeight(chatInput);
    }

    // Adjust textarea height based on content
    adjustTextareaHeight(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    // Send message functionality
    async sendMessage() {
        const chatInput = document.getElementById('chatInput');
        const message = chatInput.value.trim();
        
        if (!message) return;

        // Disable input and button
        chatInput.disabled = true;
        const sendButton = document.getElementById('sendButton');
        sendButton.disabled = true;

        // Add user message to chat
        this.addMessageToChat('user', message);
        
        // Clear input
        chatInput.value = '';
        this.adjustTextareaHeight(chatInput);

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Call backend API
            const response = await this.callAIApi(message);
            
            // Remove typing indicator
            this.hideTypingIndicator();
            
            // Add AI response to chat
            this.addMessageToChat('ai', response);
            
            // Update conversation history
            this.conversationHistory.push(
                { role: 'user', content: message, timestamp: new Date() },
                { role: 'ai', content: response, timestamp: new Date() }
            );
            
            // Save to localStorage
            this.saveConversationHistory();
            
            // Update stats
            this.updateStats();
            
            // Show success toast
            this.showToast('Message sent successfully!', 'success');
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.showToast('Error sending message. Please try again.', 'error');
        } finally {
            // Re-enable input and button
            chatInput.disabled = false;
            sendButton.disabled = false;
            chatInput.focus();
        }
    }

    // Real AI API call to Flask backend
    async callAIApi(message) {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        if (!res.ok) {
            const text = await res.text().catch(() => '');
            throw new Error(`API error ${res.status}: ${text}`);
        }
        const data = await res.json();
        if (!data || (!data.response && !data.error)) {
            throw new Error('Invalid API response');
        }
        if (data.error) {
            throw new Error(data.error);
        }
        return data.response;
    }

    // Add message to chat interface
    addMessageToChat(role, content) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const timestamp = new Date().toLocaleTimeString();
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                ${role === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>'}
            </div>
            <div class="message-content">
                <div class="message-text">${this.escapeHtml(content)}</div>
                <div class="message-time">${timestamp}</div>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        
        // Auto-scroll to bottom
        if (this.settings.autoScroll) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    // Escape HTML to prevent XSS
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Show typing indicator
    showTypingIndicator() {
        if (!this.settings.typingIndicator) return;
        
        const chatMessages = document.getElementById('chatMessages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message';
        typingDiv.id = 'typingIndicator';
        
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        
        chatMessages.appendChild(typingDiv);
        
        // Auto-scroll to bottom
        if (this.settings.autoScroll) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    // Hide typing indicator
    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    // Navigation functions
    showView(viewName) {
        // Hide all views
        const views = ['chatView', 'dashboardView', 'historyView', 'settingsView'];
        views.forEach(view => {
            document.getElementById(view).style.display = 'none';
        });
        
        // Show selected view
        document.getElementById(viewName + 'View').style.display = 'block';
        
        // Update navigation active state
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Find and activate the corresponding nav item
        const navItem = document.querySelector(`[onclick="show${viewName.charAt(0).toUpperCase() + viewName.slice(1)}()"]`);
        if (navItem) {
            navItem.classList.add('active');
        }
        
        this.currentView = viewName.toLowerCase();
        
        // Load view-specific content
        this.loadViewContent(viewName);
    }

    // Load content for specific views
    loadViewContent(viewName) {
        switch (viewName.toLowerCase()) {
            case 'dashboard':
                this.loadDashboardData();
                break;
            case 'history':
                this.loadHistoryData();
                break;
            case 'settings':
                this.loadSettingsData();
                break;
        }
    }

    // Load dashboard data
    loadDashboardData() {
        // Simulate loading dashboard statistics
        setTimeout(() => {
            document.getElementById('dashboardMessages').textContent = Math.floor(Math.random() * 50) + 10;
            document.getElementById('dashboardUsers').textContent = Math.floor(Math.random() * 20) + 5;
            document.getElementById('dashboardUptime').textContent = Math.floor(Math.random() * 24) + 1 + 'h';
            document.getElementById('dashboardResponseTime').textContent = Math.floor(Math.random() * 1000) + 200 + 'ms';
            
            // Load recent activity
            this.loadRecentActivity();
        }, 500);
    }

    // Load recent activity
    loadRecentActivity() {
        const recentActivity = document.getElementById('recentActivity');
        const activities = [
            'User asked about AI capabilities',
            'Bot responded to technical question',
            'New user joined the chat',
            'Settings updated successfully',
            'Conversation history cleared'
        ];
        
        let html = '<div style="display: flex; flex-direction: column; gap: 0.5rem;">';
        activities.forEach(activity => {
            html += `
                <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem; background: var(--background-secondary); border-radius: var(--border-radius);">
                    <div class="status-dot" style="background: var(--success-color);"></div>
                    <span>${activity}</span>
                </div>
            `;
        });
        html += '</div>';
        
        recentActivity.innerHTML = html;
    }

    // Load history data
    loadHistoryData() {
        const historyList = document.getElementById('historyList');
        
        if (this.conversationHistory.length === 0) {
            historyList.innerHTML = '<p style="color: var(--text-secondary);">No conversation history found.</p>';
            return;
        }
        
        let html = '<div style="display: flex; flex-direction: column; gap: 1rem;">';
        
        // Group conversations by date
        const groupedConversations = this.groupConversationsByDate();
        
        Object.keys(groupedConversations).forEach(date => {
            html += `<h4 style="color: var(--text-secondary); margin-bottom: 0.5rem;">${date}</h4>`;
            
            groupedConversations[date].forEach(conversation => {
                html += `
                    <div style="background: var(--background-tertiary); padding: 1rem; border-radius: var(--border-radius); border: 1px solid var(--border-color);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span style="font-weight: 600; color: var(--primary-color);">${conversation.role === 'user' ? 'You' : 'AI'}</span>
                            <span style="font-size: 0.75rem; color: var(--text-muted);">${conversation.timestamp.toLocaleTimeString()}</span>
                        </div>
                        <p style="color: var(--text-primary);">${this.escapeHtml(conversation.content)}</p>
                    </div>
                `;
            });
        });
        
        html += '</div>';
        historyList.innerHTML = html;
    }

    // Group conversations by date
    groupConversationsByDate() {
        const grouped = {};
        
        this.conversationHistory.forEach(conversation => {
            const date = conversation.timestamp.toLocaleDateString();
            if (!grouped[date]) {
                grouped[date] = [];
            }
            grouped[date].push(conversation);
        });
        
        return grouped;
    }

    // Load settings data
    loadSettingsData() {
        // Populate settings form with current values
        document.getElementById('botName').value = this.settings.botName || 'CHATBOT';
        document.getElementById('responseStyle').value = this.settings.responseStyle || 'friendly';
        document.getElementById('openaiModel').value = this.settings.openaiModel || 'gpt-4';
        document.getElementById('responseLength').value = this.settings.responseLength || 'medium';
        
        // Update toggle switches
        this.updateToggleSwitch('memoryToggle', this.settings.memoryEnabled);
        this.updateToggleSwitch('typingToggle', this.settings.typingIndicator);
        this.updateToggleSwitch('scrollToggle', this.settings.autoScroll);
    }

    // Update toggle switch state
    updateToggleSwitch(toggleId, isActive) {
        const toggle = document.getElementById(toggleId);
        if (toggle) {
            if (isActive) {
                toggle.classList.add('active');
            } else {
                toggle.classList.remove('active');
            }
        }
    }

    // Toggle setting
    toggleSetting(settingName) {
        this.settings[settingName] = !this.settings[settingName];
        
        // Update UI
        const toggleId = settingName.replace(/([A-Z])/g, (match) => match.charAt(0).toUpperCase() + match.slice(1).toLowerCase()) + 'Toggle';
        this.updateToggleSwitch(toggleId, this.settings[settingName]);
        
        // Save settings
        this.saveSettings();
        
        // Show toast
        this.showToast(`${settingName.replace(/([A-Z])/g, ' $1').trim()} ${this.settings[settingName] ? 'enabled' : 'disabled'}`, 'success');
    }

    // Save settings
    saveSettings() {
        this.settings.botName = document.getElementById('botName').value;
        this.settings.responseStyle = document.getElementById('responseStyle').value;
        this.settings.openaiModel = document.getElementById('openaiModel').value;
        this.settings.responseLength = document.getElementById('responseLength').value;
        
        localStorage.setItem('discordAIBotSettings', JSON.stringify(this.settings));
        this.showToast('Settings saved successfully!', 'success');
    }

    // Load settings from localStorage
    loadSettings() {
        const defaultSettings = {
            botName: 'CHATBOT',
            responseStyle: 'friendly',
            openaiModel: 'gpt-4',
            responseLength: 'medium',
            memoryEnabled: true,
            typingIndicator: true,
            autoScroll: true
        };
        
        const savedSettings = localStorage.getItem('discordAIBotSettings');
        if (savedSettings) {
            return { ...defaultSettings, ...JSON.parse(savedSettings) };
        }
        
        return defaultSettings;
    }

    // Save conversation history
    saveConversationHistory() {
        localStorage.setItem('discordAIBotHistory', JSON.stringify(this.conversationHistory));
    }

    // Load conversation history
    loadConversationHistory() {
        const savedHistory = localStorage.getItem('discordAIBotHistory');
        if (savedHistory) {
            this.conversationHistory = JSON.parse(savedHistory).map(item => ({
                ...item,
                timestamp: new Date(item.timestamp)
            }));
        }
    }

    // Update statistics
    updateStats() {
        document.getElementById('totalMessages').textContent = this.conversationHistory.length;
        
        const uniqueUsers = new Set(this.conversationHistory.filter(item => item.role === 'user').map(item => item.timestamp.toDateString())).size;
        document.getElementById('activeUsers').textContent = uniqueUsers;
    }

    // Start status check
    startStatusCheck() {
        // Poll status every 30 seconds
        setInterval(() => {
            this.updateBotStatus();
        }, 30000);
        
        // Initial status check
        this.updateBotStatus();
    }

    // Update bot status by calling API
    async updateBotStatus() {
        const botStatus = document.getElementById('botStatus');
        if (!botStatus) return;
        const statusTextEl = botStatus.querySelector('span');
        try {
            const res = await fetch('/api/status');
            if (!res.ok) throw new Error('status api');
            const data = await res.json();
            const online = data && data.discord === 'online';
            botStatus.className = online ? 'status-indicator status-online' : 'status-indicator status-offline';
            if (statusTextEl) statusTextEl.textContent = online ? 'Online' : 'Offline';
        } catch (e) {
            botStatus.className = 'status-indicator status-offline';
            if (statusTextEl) statusTextEl.textContent = 'Offline';
        }
    }

    // Show toast notification
    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        toastContainer.appendChild(toast);
        
        // Show toast
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Hide and remove toast
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // Clear conversation history
    clearHistory() {
        if (confirm('Are you sure you want to clear your conversation history? This action cannot be undone.')) {
            this.conversationHistory = [];
            this.saveConversationHistory();
            this.updateStats();
            this.showToast('Conversation history cleared!', 'success');
            
            // Clear chat messages (keep welcome message)
            const chatMessages = document.getElementById('chatMessages');
            const welcomeMessage = chatMessages.querySelector('.message:first-child');
            chatMessages.innerHTML = '';
            chatMessages.appendChild(welcomeMessage);
        }
    }

    // Clear all history
    clearAllHistory() {
        if (confirm('Are you sure you want to clear ALL conversation history? This action cannot be undone.')) {
            this.conversationHistory = [];
            this.saveConversationHistory();
            this.updateStats();
            this.showToast('All conversation history cleared!', 'success');
            this.loadHistoryData();
        }
    }

    // Export chat
    exportChat() {
        if (this.conversationHistory.length === 0) {
            this.showToast('No conversation history to export.', 'warning');
            return;
        }
        
        const exportData = {
            exportDate: new Date().toISOString(),
            totalMessages: this.conversationHistory.length,
            conversations: this.conversationHistory
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chatbot-export-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showToast('Chat exported successfully!', 'success');
    }
}

// Global functions for HTML onclick handlers
function showChat() {
    window.bot.showView('chat');
}

function showDashboard() {
    window.bot.showView('dashboard');
}

function showHistory() {
    window.bot.showView('history');
}

function showSettings() {
    window.bot.showView('settings');
}

function sendMessage() {
    window.bot.sendMessage();
}

function clearHistory() {
    window.bot.clearHistory();
}

function clearAllHistory() {
    window.bot.clearAllHistory();
}

function exportChat() {
    window.bot.exportChat();
}

function toggleSetting(settingName) {
    window.bot.toggleSetting(settingName);
}

function saveSettings() {
    window.bot.saveSettings();
}

// Initialize the bot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.bot = new DiscordAIBot();
    
    // Add loading overlay styles
    const style = document.createElement('style');
    style.textContent = `
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
        }
        
        .loading-content {
            background: var(--background-floating);
            padding: 2rem;
            border-radius: var(--border-radius);
            border: 1px solid var(--border-color);
            text-align: center;
            color: var(--text-primary);
        }
        
        .loading-content p {
            margin-top: 1rem;
            color: var(--text-secondary);
        }
    `;
    document.head.appendChild(style);
});
