// ==========================================
// Файл: static/js/socket.js
// Справка: README.md → Веб-морда / WebSocket
// Задача: работа с Socket.IO (сообщения, история)
// Комментарий: инициализация сокета, обработка событий, исправлены вызовы openReply/openComment
// Зависит от: helpers.js (escapeHtml)
// Вызывается из: main.js (импорт)
// ==========================================

import { escapeHtml } from './helpers.js';

let socket = null;
let isConnected = false;

export function initSocket() {
    const messagesDiv = document.getElementById('messages');
    if (!messagesDiv) {
        console.warn('⚠️ Элемент #messages не найден, Socket инициализация пропущена');
        return;
    }
    
    try {
        socket = io();
        
        socket.on('connect', () => {
            isConnected = true;
            console.log('🔌 Socket.IO подключён');
        });
        
        socket.on('disconnect', () => {
            isConnected = false;
            console.log('🔌 Socket.IO отключён');
        });
        
        socket.on('message_history', (messages) => {
            renderMessages(messages);
        });
        
        socket.on('message_updated', (data) => {
            appendMessage(data);
        });
        
        socket.on('connect_error', (error) => {
            console.error('❌ Socket.IO ошибка подключения:', error);
        });
        
    } catch (e) {
        console.error('❌ Ошибка инициализации Socket.IO:', e);
    }
}

function renderMessages(messages) {
    const messagesDiv = document.getElementById('messages');
    if (!messagesDiv) return;
    
    messagesDiv.innerHTML = '';
    
    if (!messages || messages.length === 0) {
        messagesDiv.innerHTML = '<div style="color: var(--text-secondary); padding: 1rem;">📭 Сообщений пока нет</div>';
        return;
    }
    
    // Ограничиваем количество отображаемых сообщений (последние 100)
    const recentMessages = messages.slice(-100);
    
    for (const msg of recentMessages) {
        const msgDiv = createMessageElement(msg);
        messagesDiv.appendChild(msgDiv);
    }
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function appendMessage(data) {
    const messagesDiv = document.getElementById('messages');
    if (!messagesDiv) return;
    
    // Убираем заглушку "Нет сообщений", если она есть
    if (messagesDiv.innerHTML.includes('Сообщений пока нет')) {
        messagesDiv.innerHTML = '';
    }
    
    const msgDiv = createMessageElement(data);
    messagesDiv.appendChild(msgDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function createMessageElement(data) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message-item';
    
    let icon = '📨';
    let sourceClass = '';
    
    if (data.source === 'telegram') {
        icon = '✈️';
        sourceClass = 'message-telegram';
    } else if (data.source === 'vk') {
        icon = '📘';
        sourceClass = 'message-vk';
    } else if (data.source === 'admin') {
        icon = '👤';
        sourceClass = 'message-own';
    }
    
    msgDiv.className = `message-item ${sourceClass}`;
    
    const time = data.timestamp ? new Date(data.timestamp).toLocaleTimeString() : new Date().toLocaleTimeString();
    const sender = data.sender || data.username || data.from || 'unknown';
    const chatId = data.chat_id || data.user_id || '';
    const postId = data.post_id || data.chat_id || '';
    
    msgDiv.innerHTML = `
        <div class="message-header" style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span class="message-source"><strong>${icon} ${escapeHtml(data.source || 'unknown')}</strong> | ${escapeHtml(sender)}</span>
            <span class="message-time" style="font-size: 0.7rem; color: var(--text-secondary);">${escapeHtml(time)}</span>
        </div>
        <div class="message-text" style="margin: 5px 0;">${escapeHtml(data.text || '')}</div>
        ${chatId ? `<div class="message-chat-id" style="font-size: 0.7rem; color: var(--text-secondary);">🆔 ID: ${escapeHtml(chatId)}</div>` : ''}
        <div class="message-actions" style="margin-top: 8px; display: flex; gap: 8px;">
            ${data.source === 'telegram' || data.source === 'vk' ? 
                `<button onclick="window.openReply('${escapeHtml(String(chatId))}', '${data.source}', '${escapeHtml(sender)}')" style="font-size: 0.7rem; padding: 4px 8px;">💬 Ответить</button>` : ''}
            ${data.source === 'vk' && postId ? 
                `<button onclick="window.openComment('${escapeHtml(String(postId))}', 'vk')" style="font-size: 0.7rem; padding: 4px 8px;">✏️ Комментировать</button>` : ''}
        </div>
    `;
    
    return msgDiv;
}

export { socket, isConnected };
