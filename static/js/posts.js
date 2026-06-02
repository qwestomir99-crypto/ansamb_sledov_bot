// ==========================================
// Файл: static/js/posts.js
// Справка: README.md → Веб-морда / Посты
// Задача: создание постов в Telegram и VK
// Комментарий: исправлены пути (теперь /api/posts/...)
// Зависит от: ui.js (showToast)
// Вызывается из: main.js (импорт)
// ==========================================

import { showToast } from './ui.js';

export function createPost(platform) {
    const text = prompt(`Введите текст поста для ${platform === 'telegram' ? 'Telegram' : 'VK'}:`);
    if (!text) return;
    
    fetch('/api/posts/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ platform: platform, text: text })
    })
    .then(resp => resp.json())
    .then(data => {
        if (data.status === 'ok') {
            showToast(`✅ Пост опубликован в ${platform === 'telegram' ? 'Telegram' : 'VK'}`, 'success');
        } else {
            showToast('❌ Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    })
    .catch(e => showToast('Ошибка: ' + e.message, 'error'));
}

export async function sendPost() {
    const text = document.getElementById('post-text').value.trim();
    if (!text) return;
    
    const statusSpan = document.getElementById('post-status');
    statusSpan.textContent = '⏳ Отправка...';
    
    try {
        const resp = await fetch('/api/posts/vk', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });
        const data = await resp.json();
        if (data.status === 'ok') {
            statusSpan.innerHTML = `✅ <a href="${data.url}" target="_blank">Пост опубликован</a>`;
            document.getElementById('post-text').value = '';
        } else {
            showToast('❌ ' + (data.error || 'Ошибка'), 'error');
        }
    } catch(e) {
        showToast('❌ Ошибка: ' + e.message, 'error');
    }
}
