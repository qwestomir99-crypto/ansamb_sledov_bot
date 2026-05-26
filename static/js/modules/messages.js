// ==========================================
// Файл: static/js/modules/messages.js
// Справка: README.md → Веб-морда / Сообщения
// Задача: отображение сообщений, ответы, комментарии
// Комментарий: работает с API /send_reply и /api/vk/comment, /api/tg/comment
// Зависит от: utils.js (escapeHtml)
// Вызывается из: socket.js, admin.html (кнопки)
// ==========================================

import { escapeHtml } from './utils.js';

let currentReply = null;
let currentComment = null;

/**
 * Добавляет сообщение в ленту
 * @param {Object} msg - сообщение
 */
export function appendMessage(msg) {
    const container = document.getElementById('messages');
    if (!container) return;
    
    if (container.innerHTML === '<div style="color: var(--text-secondary);">Загрузка...</div>' || 
        container.innerHTML === '<div style="color: var(--text-secondary);">Нет сообщений</div>') {
        container.innerHTML = '';
    }
    
    const div = document.createElement('div');
    let sourceClass = '';
    if (msg.source === 'telegram') sourceClass = 'message-telegram';
    else if (msg.source === 'vk') sourceClass = 'message-vk';
    div.className = `message ${sourceClass} ${msg.own ? 'own' : ''}`;
    
    const sourceName = msg.source === 'telegram' ? '📱 Telegram' : (msg.source === 'admin' ? '🤖 Админ' : '📘 VK');
    const sender = msg.sender || msg.username || 'unknown';
    const time = msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString() : new Date().toLocaleTimeString();
    
    const chatId = msg.chat_id || msg.user_id || '';
    const postId = msg.post_id || '';
    
    div.innerHTML = `
        <div><strong>${escapeHtml(sourceName)} | ${escapeHtml(sender)}</strong></div>
        <div>${escapeHtml(msg.text || '')}</div>
        <small>${escapeHtml(time)}</small>
        <div class="message-actions" style="margin-top: 8px;">
            <button onclick="window.openReply('${escapeHtml(String(chatId))}', '${msg.source}', '${escapeHtml(sender)}')">💬 Ответить</button>
            <button onclick="window.openComment('${escapeHtml(String(postId || chatId))}', '${msg.source}')">✏️ Комментировать</button>
        </div>
    `;
    container.prepend(div);
}

/**
 * Открывает панель ответа на сообщение
 * @param {string} chatId - ID чата
 * @param {string} source - источник ('telegram' или 'vk')
 * @param {string} sender - имя отправителя
 */
export function openReply(chatId, source, sender) {
    currentReply = { chatId: chatId, source: source };
    const replyArea = document.getElementById('reply-area');
    const replyText = document.getElementById('reply-text');
    if (replyArea) replyArea.classList.remove('hidden');
    if (replyText) replyText.placeholder = `Ответ для ${sender}...`;
    if (replyText) replyText.focus();
}

/**
 * Закрывает панель ответа
 */
export function closeReply() {
    currentReply = null;
    const replyArea = document.getElementById('reply-area');
    const replyText = document.getElementById('reply-text');
    if (replyArea) replyArea.classList.add('hidden');
    if (replyText) replyText.value = '';
}

/**
 * Отправляет ответ на сообщение
 */
export async function sendReply() {
    if (!currentReply) return;
    const text = document.getElementById('reply-text')?.value.trim();
    if (!text) return;
    
    const response = await fetch('/send_reply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            chat_id: currentReply.chatId,
            text: text,
            source: currentReply.source
        })
    });
    const data = await response.json();
    if (data.status === 'ok') {
        appendMessage({
            source: 'admin',
            text: text,
            timestamp: new Date().toISOString(),
            own: true
        });
        closeReply();
    } else {
        alert('Ошибка: ' + (data.error || 'неизвестная'));
    }
}

/**
 * Открывает панель комментария к посту
 * @param {string} postId - ID поста
 * @param {string} platform - платформа ('telegram' или 'vk')
 */
export function openComment(postId, platform) {
    currentComment = { postId: postId, platform: platform };
    const commentArea = document.getElementById('comment-area');
    const commentText = document.getElementById('comment-text');
    if (commentArea) commentArea.classList.remove('hidden');
    if (commentText) commentText.placeholder = `Комментарий к посту ${postId}...`;
    if (commentText) commentText.focus();
}

/**
 * Закрывает панель комментария
 */
export function closeComment() {
    currentComment = null;
    const commentArea = document.getElementById('comment-area');
    const commentText = document.getElementById('comment-text');
    if (commentArea) commentArea.classList.add('hidden');
    if (commentText) commentText.value = '';
}

/**
 * Отправляет комментарий к посту
 */
export async function sendComment() {
    if (!currentComment) return;
    const text = document.getElementById('comment-text')?.value.trim();
    if (!text) return;
    
    let url = '/api/comment';
    if (currentComment.platform === 'vk') {
        url = '/api/vk/comment';
    } else if (currentComment.platform === 'telegram') {
        url = '/api/tg/comment';
    }
    
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            post_id: currentComment.postId,
            text: text,
            chat_id: currentComment.postId
        })
    });
    const data = await response.json();
    if (data.status === 'ok') {
        appendMessage({
            source: 'admin',
            text: `💬 Комментарий: ${text}`,
            timestamp: new Date().toISOString(),
            own: true
        });
        closeComment();
    } else {
        alert('Ошибка: ' + (data.error || 'неизвестная'));
    }
}

// Глобальные функции для onclick из HTML
window.openReply = openReply;
window.openComment = openComment;
window.sendReply = sendReply;
window.sendComment = sendComment;
