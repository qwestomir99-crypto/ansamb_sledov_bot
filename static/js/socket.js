// ==========================================
// Файл: static/js/socket.js
// Справка: README.md → Веб-морда / WebSocket
// Задача: работа с Socket.IO (сообщения, история)
// Комментарий: инициализация сокета, обработка событий
// Зависит от: helpers.js (escapeHtml)
// Вызывается из: main.js (импорт)
// ==========================================

import { escapeHtml } from './helpers.js';

const socket = io();

export function initSocket() {
    socket.on('message_history', function(messages) {
        renderMessages(messages);
    });

    socket.on('message_updated', function(data) {
        const messagesDiv = document.getElementById('messages');
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message-item';
        
        let icon = '📨';
        if (data.source === 'telegram') icon = '✈️';
        else if (data.source === 'vk') icon = '📘';
        else if (data.source === 'admin') icon = '👤';
        
        const time = data.timestamp ? new Date(data.timestamp).toLocaleTimeString() : '';
        
        msgDiv.innerHTML = `
            <div class="message-header">
                <span class="message-source">${icon} ${data.source || 'неизвестно'}</span>
                <span class="message-time">${time}</span>
            </div>
            <div class="message-text">${escapeHtml(data.text || '')}</div>
            ${data.chat_id ? `<div class="message-chat-id">ID: ${data.chat_id}</div>` : ''}
            <div class="message-actions">
                ${data.source === 'telegram' || data.source === 'vk' ? 
                    `<button onclick="openReply('${data.chat_id}', '${data.source}')">✏️ Ответить</button>` : ''}
                ${data.source === 'vk' ? 
                    `<button onclick="openComment('${data.chat_id}')">💬 Комментарий</button>` : ''}
            </div>
        `;
        
        while (messagesDiv.children.length > 100) {
            messagesDiv.removeChild(messagesDiv.firstChild);
        }
        messagesDiv.appendChild(msgDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    });
}

function renderMessages(messages) {
    const messagesDiv = document.getElementById('messages');
    messagesDiv.innerHTML = '';
    
    if (!messages || messages.length === 0) {
        messagesDiv.innerHTML = '<div style="color: var(--text-secondary); padding: 1rem;">Сообщений пока нет</div>';
        return;
    }
    
    messages.forEach(data => {
        let icon = '📨';
        if (data.source === 'telegram') icon = '✈️';
        else if (data.source === 'vk') icon = '📘';
        else if (data.source === 'admin') icon = '👤';
        
        const time = data.timestamp ? new Date(data.timestamp).toLocaleTimeString() : '';
        
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message-item';
        msgDiv.innerHTML = `
            <div class="message-header">
                <span class="message-source">${icon} ${data.source || 'неизвестно'}</span>
                <span class="message-time">${time}</span>
            </div>
            <div class="message-text">${escapeHtml(data.text || '')}</div>
            ${data.chat_id ? `<div class="message-chat-id">ID: ${data.chat_id}</div>` : ''}
            <div class="message-actions">
                ${data.source === 'telegram' || data.source === 'vk' ? 
                    `<button onclick="openReply('${data.chat_id}', '${data.source}')">✏️ Ответить</button>` : ''}
                ${data.source === 'vk' ? 
                    `<button onclick="openComment('${data.chat_id}')">💬 Комментарий</button>` : ''}
            </div>
        `;
        messagesDiv.appendChild(msgDiv);
    });
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

export { socket };
