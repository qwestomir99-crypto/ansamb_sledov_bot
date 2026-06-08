// ==========================================
// Файл: static/js/replies.js
// Справка: README.md → Веб-морда / Ответы
// Задача: ответы и комментарии к сообщениям
// Комментарий: исправлены пути на /api/replies/..., добавлены open/close функции
// Зависит от: ui.js (showToast), helpers.js (escapeHtml)
// Вызывается из: main.js (импорт)
// ==========================================

import { showToast } from './ui.js';
import { escapeHtml } from './helpers.js';

export function initReplies() {
    // Инициализация не требуется, все функции уже на window
    // Убираем лишний DOMContentLoaded, инициализация идёт из main.js
    console.log('✅ Replies модуль готов');
}

// Глобальные переменные для хранения контекста ответа/комментария
window.currentReply = null;   // { chatId, source, sender }
window.currentComment = null; // { postId, platform }

// ==========================================
// ОТВЕТ НА СООБЩЕНИЕ
// ==========================================
window.openReply = function(chatId, source, sender) {
    window.currentReply = { chatId: chatId, source: source, sender: sender };
    const replyArea = document.getElementById('reply-area');
    const replyText = document.getElementById('reply-text');
    
    if (replyArea) replyArea.classList.remove('hidden');
    if (replyText) {
        replyText.placeholder = `Ответ для ${escapeHtml(sender)}...`;
        replyText.focus();
    }
    console.log(`📝 Открыта форма ответа для ${source} chatId=${chatId}`);
};

window.closeReply = function() {
    window.currentReply = null;
    const replyArea = document.getElementById('reply-area');
    const replyText = document.getElementById('reply-text');
    if (replyArea) replyArea.classList.add('hidden');
    if (replyText) replyText.value = '';
};

window.sendReply = async function() {
    if (!window.currentReply) {
        showToast('Нет активного сообщения для ответа', 'error');
        return;
    }
    
    const replyText = document.getElementById('reply-text');
    if (!replyText) {
        showToast('Элемент reply-text не найден', 'error');
        return;
    }
    
    const text = replyText.value.trim();
    if (!text) {
        showToast('Введите текст ответа', 'info');
        return;
    }
    
    // Блокируем кнопку на время отправки
    const sendBtn = document.querySelector('#reply-area button[onclick="sendReply()"]');
    if (sendBtn) {
        sendBtn.disabled = true;
        sendBtn.textContent = '⏳ Отправка...';
    }
    
    try {
        const resp = await fetch('/send_reply', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                chat_id: window.currentReply.chatId,
                text: text,
                source: window.currentReply.source
            })
        });
        const data = await resp.json();
        
        if (data.status === 'ok') {
            showToast('✅ Ответ отправлен', 'success');
            window.closeReply();
        } else {
            showToast('❌ Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch (e) {
        showToast('❌ Ошибка: ' + e.message, 'error');
    } finally {
        if (sendBtn) {
            sendBtn.disabled = false;
            sendBtn.textContent = '📤 Отправить ответ';
        }
    }
};

// ==========================================
// КОММЕНТАРИЙ К ПОСТУ
// ==========================================
window.openComment = function(postId, platform) {
    window.currentComment = { postId: postId, platform: platform };
    const commentArea = document.getElementById('comment-area');
    const commentText = document.getElementById('comment-text');
    
    if (commentArea) commentArea.classList.remove('hidden');
    if (commentText) {
        commentText.placeholder = `Комментарий к посту ${escapeHtml(postId)}...`;
        commentText.focus();
    }
    console.log(`✏️ Открыта форма комментария для ${platform} postId=${postId}`);
};

window.closeComment = function() {
    window.currentComment = null;
    const commentArea = document.getElementById('comment-area');
    const commentText = document.getElementById('comment-text');
    if (commentArea) commentArea.classList.add('hidden');
    if (commentText) commentText.value = '';
};

window.sendComment = async function() {
    if (!window.currentComment) {
        showToast('Нет активного поста для комментария', 'error');
        return;
    }
    
    const commentText = document.getElementById('comment-text');
    if (!commentText) {
        showToast('Элемент comment-text не найден', 'error');
        return;
    }
    
    const text = commentText.value.trim();
    if (!text) {
        showToast('Введите текст комментария', 'info');
        return;
    }
    
    // Определяем URL в зависимости от платформы
    let url = '/api/comment';
    if (window.currentComment.platform === 'vk') {
        url = '/api/vk/comment';
    } else if (window.currentComment.platform === 'telegram') {
        url = '/api/tg/comment';
    }
    
    // Блокируем кнопку на время отправки
    const sendBtn = document.querySelector('#comment-area button[onclick="sendComment()"]');
    if (sendBtn) {
        sendBtn.disabled = true;
        sendBtn.textContent = '⏳ Отправка...';
    }
    
    try {
        const resp = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                post_id: window.currentComment.postId,
                text: text,
                chat_id: window.currentComment.postId
            })
        });
        const data = await resp.json();
        
        if (data.status === 'ok') {
            showToast('✅ Комментарий отправлен', 'success');
            window.closeComment();
        } else {
            showToast('❌ Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch (e) {
        showToast('❌ Ошибка: ' + e.message, 'error');
    } finally {
        if (sendBtn) {
            sendBtn.disabled = false;
            sendBtn.textContent = '✏️ Отправить комментарий';
        }
    }
};
