

class MessengerComponent {
  constructor() {
    this.currentChatId = null;
    this.ws = null;
    this.messages = [];
    this.typingTimeout = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  async init() {
    await this.loadChats();
    this.setupEventListeners();
    this.connectWebSocket();
  }

  async loadChats() {
    try {
      const chats = await api.get('/messenger/chats');
      this.renderChatList(chats);
    } catch (error) {
      console.error('Failed to load chats:', error);
      this.showError(i18n.t('errors.networkError'));
    }
  }

  renderChatList(chats) {
    const container = document.querySelector('.chat-list');
    if (!container) return;

    if (!chats || chats.length === 0) {
      container.innerHTML = `
        <div class="messenger-empty">
          <p data-i18n="messenger.noChats">${i18n.t('messenger.noChats')}</p>
        </div>
      `;
      return;
    }

    container.innerHTML = chats.map(chat => `
      <div class="chat-item ${chat.id === this.currentChatId ? 'active' : ''}" 
           data-chat-id="${chat.id}" 
           onclick="messenger.selectChat(${chat.id})">
        <div class="chat-item-avatar">
          <div class="avatar avatar-md">
            ${chat.avatar_url 
              ? `<img src="${chat.avatar_url}" alt="${chat.name}" class="avatar-image">`
              : `<span class="avatar-placeholder">${this.getInitials(chat.name)}</span>`
            }
            ${chat.is_online ? '<span class="avatar-status avatar-status-online"></span>' : ''}
          </div>
        </div>
        <div class="chat-item-content">
          <div class="chat-item-header">
            <span class="chat-item-name truncate">${this.escapeHtml(chat.name)}</span>
            <span class="chat-item-time">${this.formatTime(chat.last_message_time)}</span>
          </div>
          <div class="chat-item-preview truncate">
            ${chat.last_message ? this.escapeHtml(chat.last_message) : i18n.t('messenger.startChat')}
          </div>
        </div>
        ${chat.unread_count > 0 ? `<span class="chat-item-unread">${chat.unread_count}</span>` : ''}
      </div>
    `).join('');

    i18n.applyTranslations();
  }

  async selectChat(chatId) {
    if (this.currentChatId === chatId) return;

    this.currentChatId = chatId;
    
    document.querySelectorAll('.chat-item').forEach(item => {
      item.classList.toggle('active', parseInt(item.dataset.chatId) === chatId);
    });

    await this.loadMessages(chatId);
    this.scrollToBottom();
  }

  async loadMessages(chatId) {
    try {
      this.messages = await api.get(`/messenger/chats/${chatId}/messages`);
      this.renderMessages();
    } catch (error) {
      console.error('Failed to load messages:', error);
      this.showError(i18n.t('errors.networkError'));
    }
  }

  renderMessages() {
    const container = document.querySelector('.messages-container');
    if (!container) return;

    if (!this.messages || this.messages.length === 0) {
      container.innerHTML = `
        <div class="messenger-empty">
          <p data-i18n="messenger.startChat">${i18n.t('messenger.startChat')}</p>
        </div>
      `;
      return;
    }

    let lastSenderId = null;

    container.innerHTML = this.messages.map(msg => {
      const isSent = msg.sender_id === this.currentUserId;
      const showAvatar = msg.sender_id !== lastSenderId;
      lastSenderId = msg.sender_id;

      return `
        <div class="message ${isSent ? 'sent' : ''}">
          ${!isSent && showAvatar ? `
            <div class="message-avatar">
              <div class="avatar avatar-sm">
                ${msg.sender_avatar 
                  ? `<img src="${msg.sender_avatar}" alt="" class="avatar-image">`
                  : `<span class="avatar-placeholder">${this.getInitials(msg.sender_name)}</span>`
                }
              </div>
            </div>
          ` : (!isSent ? '<div style="width: 40px;"></div>' : '')}
          
          <div class="message-content">
            <div class="message-bubble">
              <p class="message-text">${this.escapeHtml(msg.content)}</p>
            </div>
            <div class="message-meta">
              <span class="message-time">${this.formatMessageTime(msg.created_at)}</span>
              ${isSent ? this.getMessageStatusIcon(msg.status) : ''}
            </div>
          </div>
        </div>
      `;
    }).join('');

    i18n.applyTranslations();
  }

  async sendMessage(content) {
    if (!content.trim() || !this.currentChatId) return;

    const messageData = {
      chat_id: this.currentChatId,
      content: content.trim(),
    };

    try {
      const newMessage = await api.post('/messenger/messages', messageData);
      this.messages.push(newMessage);
      this.renderMessages();
      this.scrollToBottom();
      
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({
          type: 'new_message',
          data: newMessage
        }));
      }

      document.querySelector('.message-input').value = '';
      this.stopTyping();
    } catch (error) {
      console.error('Failed to send message:', error);
      this.showError(i18n.t('errors.networkError'));
    }
  }

  connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.handleWebSocketMessage(data);
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }
  }

  handleWebSocketMessage(data) {
    switch (data.type) {
      case 'new_message':
        if (data.message.chat_id === this.currentChatId) {
          this.messages.push(data.message);
          this.renderMessages();
          this.scrollToBottom();
        }
        this.loadChats();
        break;

      case 'typing':
        this.showTypingIndicator(data.user_id);
        break;

      case 'stop_typing':
        this.hideTypingIndicator(data.user_id);
        break;

      case 'online':
        this.updateUserStatus(data.user_id, true);
        break;

      case 'offline':
        this.updateUserStatus(data.user_id, false);
        break;
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
      setTimeout(() => this.connectWebSocket(), delay);
    }
  }

  startTyping() {
    if (!this.currentChatId) return;

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'typing',
        chat_id: this.currentChatId
      }));
    }
  }

  stopTyping() {
    if (!this.currentChatId) return;

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'stop_typing',
        chat_id: this.currentChatId
      }));
    }

    clearTimeout(this.typingTimeout);
  }

  setupEventListeners() {
    const input = document.querySelector('.message-input');
    const sendBtn = document.querySelector('.message-send-btn');

    if (input) {
      input.addEventListener('input', () => {
        this.startTyping();
        
        clearTimeout(this.typingTimeout);
        this.typingTimeout = setTimeout(() => this.stopTyping(), 2000);
      });

      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this.sendMessage(input.value);
        }
      });
    }

    if (sendBtn) {
      sendBtn.addEventListener('click', () => {
        if (input) {
          this.sendMessage(input.value);
        }
      });
    }

    const searchInput = document.querySelector('.messenger-search .form-input');
    if (searchInput) {
      searchInput.addEventListener('input', debounce((e) => {
        this.searchChats(e.target.value);
      }, 300));
    }
  }

  async searchChats(query) {
    if (!query.trim()) {
      await this.loadChats();
      return;
    }

    try {
      const chats = await api.get(`/messenger/chats/search?q=${encodeURIComponent(query)}`);
      this.renderChatList(chats);
    } catch (error) {
      console.error('Search failed:', error);
    }
  }

  scrollToBottom() {
    const container = document.querySelector('.messages-container');
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }

  formatTime(timestamp) {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    
    if (isToday) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
  }

  formatMessageTime(timestamp) {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  getMessageStatusIcon(status) {
    const icons = {
      sent: '✓',
      delivered: '✓✓',
      read: '✓✓'
    };
    return `<span class="message-status">${icons[status] || ''}</span>`;
  }

  getInitials(name) {
    if (!name) return '?';
    const parts = name.trim().split(' ');
    if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
    return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
  }

  escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  showError(message) {
    console.error(message);
  }

  destroy() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    clearTimeout(this.typingTimeout);
  }
}

const messenger = new MessengerComponent();

function debounce(func, wait = 300) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

document.addEventListener('DOMContentLoaded', () => {
  messenger.init();
});

window.addEventListener('beforeunload', () => {
  messenger.destroy();
});
