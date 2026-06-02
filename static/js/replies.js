// ==========================================
// Файл: static/js/replies.js
// Справка: README.md → Веб-морда / Ответы
// Задача: ответы и комментарии к сообщениям
// Комментарий: исправлены пути на /api/replies/...
// Зависит от: ui.js (showToast)
// Вызывается из: main.js (импорт)
// ==========================================

import { showToast } from './ui.js';

export function initReplies() {
    document.addEventListener('DOMContentLoaded', () => {
        // Инициализация — пустая, позже можно добавить
    });
}

window.sendReply = async function() {
    const text = document.getElementById('reply-text').value.trim();
    const msgId = document.getElementById('reply-target-id')?.value;
    if (!text) return;
    try {
        const resp = await fetch('/api/replies/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, reply_to: msgId })
        });
        const data = await resp.json();
        if (data.status === 'ok') {
            showToast('Ответ отправлен', 'success');
            document.getElementById('reply-text').value = '';
        } else {
            showToast('Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch(e) {
        showToast('Ошибка: ' + e.message, 'error');
    }
};

window.closeReply = function() {
    document.getElementById('reply-area').classList.add('hidden');
};

window.sendComment = async function() {
    const text = document.getElementById('comment-text').value.trim();
    if (!text) return;
    try {
        const resp = await fetch('/api/replies/comment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        const data = await resp.json();
        if (data.status === 'ok') {
            showToast('Комментарий отправлен', 'success');
            document.getElementById('comment-text').value = '';
        } else {
            showToast('Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch(e) {
        showToast('Ошибка: ' + e.message, 'error');
    }
};

window.closeComment = function() {
    document.getElementById('comment-area').classList.add('hidden');
};
