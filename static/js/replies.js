// ==========================================
// Файл: static/js/replies.js
// Справка: README.md → Веб-морда / Ответы
// Задача: ответы на сообщения и комментарии
// Комментарий: функции openReply, sendReply, openComment, sendComment
// Зависит от: ui.js (showToast)
// Вызывается из: main.js (импорт)
// ==========================================

import { showToast } from './ui.js';

let currentReplyChatId = null;
let currentReplySource = null;

export function initReplies() {
    // Инициализация (если нужна)
}

export function openReply(chatId, source) {
    currentReplyChatId = chatId;
    currentReplySource = source;
    document.getElementById('reply-area').classList.remove('hidden');
    document.getElementById('reply-text').focus();
    document.getElementById('comment-area').classList.add('hidden');
}

export function closeReply() {
    document.getElementById('reply-area').classList.add('hidden');
    currentReplyChatId = null;
    currentReplySource = null;
}

export async function sendReply() {
    const text = document.getElementById('reply-text').value.trim();
    if (!text) return;
    
    try {
        const resp = await fetch('/send_reply', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                chat_id: currentReplyChatId,
                text: text,
                source: currentReplySource
            })
        });
        const data = await resp.json();
        if (data.status === 'ok') {
            document.getElementById('reply-text').value = '';
            closeReply();
        } else {
            showToast('Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch(e) {
        showToast('Ошибка отправки: ' + e.message, 'error');
    }
}

export function openComment(chatId) {
    currentReplyChatId = chatId;
    document.getElementById('comment-area').classList.remove('hidden');
    document.getElementById('comment-text').focus();
    document.getElementById('reply-area').classList.add('hidden');
}

export function closeComment() {
    document.getElementById('comment-area').classList.add('hidden');
    currentReplyChatId = null;
}

export async function sendComment() {
    const text = document.getElementById('comment-text').value.trim();
    if (!text) return;
    
    try {
        const resp = await fetch('/api/vk/comment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                peer_id: currentReplyChatId,
                text: text
            })
        });
        const data = await resp.json();
        if (data.status === 'ok') {
            document.getElementById('comment-text').value = '';
            closeComment();
        } else {
            showToast('Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch(e) {
        showToast('Ошибка комментария: ' + e.message, 'error');
    }
}
