// ==========================================
// Файл: static/js/posts.js
// Справка: README.md → Веб-морда / Посты
// Задача: создание постов в Telegram и VK
// Комментарий: исправлены пути (теперь /api/posts/...), добавлены проверки элементов
// Зависит от: ui.js (showToast)
// Вызывается из: main.js (импорт)
// ==========================================

import { showToast } from './ui.js';

export async function createPost(platform) {
    const text = prompt(`Введите текст поста для ${platform === 'telegram' ? 'Telegram' : 'VK'}:`);
    if (!text) return;
    
    try {
        const resp = await fetch('/api/posts/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ platform: platform, text: text })
        });
        const data = await resp.json();
        
        if (data.status === 'ok') {
            showToast(`✅ Пост опубликован в ${platform === 'telegram' ? 'Telegram' : 'VK'}`, 'success');
        } else {
            showToast('❌ Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch (e) {
        showToast('❌ Ошибка: ' + e.message, 'error');
    }
}

export async function sendPost() {
    const postText = document.getElementById('post-text');
    const statusSpan = document.getElementById('post-status');
    
    if (!postText) {
        showToast('❌ Элемент post-text не найден на странице', 'error');
        return;
    }
    
    const text = postText.value.trim();
    if (!text) {
        showToast('📝 Введите текст поста', 'info');
        return;
    }
    
    if (!statusSpan) {
        showToast('❌ Элемент post-status не найден на странице', 'error');
        return;
    }
    
    const originalText = statusSpan.textContent;
    statusSpan.textContent = '⏳ Отправка...';
    
    try {
        const resp = await fetch('/api/posts/vk', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });
        const data = await resp.json();
        
        if (data.status === 'ok') {
            statusSpan.innerHTML = `✅ <a href="${data.url}" target="_blank" style="color: var(--success);">Пост опубликован</a>`;
            postText.value = '';
            // Скрываем сообщение через 5 секунд
            setTimeout(() => {
                if (statusSpan) statusSpan.textContent = '';
            }, 5000);
        } else {
            statusSpan.textContent = '';
            showToast('❌ ' + (data.error || 'Ошибка публикации'), 'error');
        }
    } catch (e) {
        statusSpan.textContent = originalText;
        showToast('❌ Ошибка: ' + e.message, 'error');
    }
}

export async function createPostWithMedia(platform, mediaUrl, caption = '') {
    /**
     * Создаёт пост с медиа (фото, видео) в Telegram или VK
     * @param {string} platform - 'telegram' или 'vk'
     * @param {string} mediaUrl - URL медиафайла
     * @param {string} caption - Подпись к посту
     */
    if (!mediaUrl) {
        showToast('❌ Не указан URL медиафайла', 'error');
        return;
    }
    
    try {
        const resp = await fetch('/api/posts/create_with_media', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ platform, media_url: mediaUrl, caption })
        });
        const data = await resp.json();
        
        if (data.status === 'ok') {
            showToast(`✅ Пост с медиа опубликован в ${platform === 'telegram' ? 'Telegram' : 'VK'}`, 'success');
        } else {
            showToast('❌ Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch (e) {
        showToast('❌ Ошибка: ' + e.message, 'error');
    }
}
