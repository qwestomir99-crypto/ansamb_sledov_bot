// ==========================================
// Файл: static/js/uploads.js
// Справка: README.md → Веб-морда / Загрузка на YouTube
// Задача: загрузка видео на YouTube через веб-морду
// Зависит от: ui.js (showToast)
// Вызывается из: main.js (импорт)
// ==========================================

import { showToast } from './ui.js';

export function initUploads() {
    // Инициализация при загрузке страницы
}

window.uploadToYouTube = async function() {
    const fileUrl = prompt('Введите URL видео для загрузки на YouTube:');
    if (!fileUrl) return;
    
    const title = prompt('Название видео:', 'Видео из Ансамбля');
    if (!title) return;
    
    const description = prompt('Описание видео (необязательно):', '');
    
    try {
        showToast('⏳ Загрузка на YouTube...', 'info');
        
        const resp = await fetch('/api/youtube_upload/upload', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                file_url: fileUrl,
                title: title,
                description: description
            })
        });
        
        const data = await resp.json();
        
        if (data.status === 'ok') {
            showToast(`✅ Видео загружено! ID: ${data.video_id}`, 'success');
            document.getElementById('youtube-upload-status').innerHTML = 
                `✅ Загружено: <a href="https://youtube.com/watch?v=${data.video_id}" target="_blank">youtube.com/watch?v=${data.video_id}</a>`;
        } else if (resp.status === 401) {
            showToast('Требуется авторизация. Открываю страницу входа...', 'info');
            window.open('/api/youtube_upload/authorize', '_blank');
        } else {
            showToast('❌ Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch(e) {
        showToast('❌ Ошибка: ' + e.message, 'error');
    }
};
