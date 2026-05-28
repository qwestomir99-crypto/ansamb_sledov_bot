// ==========================================
// Файл: static/js/uploads.js
// Справка: README.md → Веб-морда / Загрузка видео
// Задача: загрузка видео на YouTube
// Комментарий: использует /api/youtube_upload/upload
// Зависит от: ui.js (showToast)
// Вызывается из: main.js (импорт)
// ==========================================

import { showToast } from './ui.js';

export function initUploads() {
    // Инициализация (если нужна)
}

window.uploadToYouTube = async function() {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'video/*';
    fileInput.onchange = async function() {
        const file = fileInput.files[0];
        if (!file) return;
        
        const formData = new FormData();
        formData.append('video', file);
        
        try {
            const resp = await fetch('/api/youtube_upload/upload', {
                method: 'POST',
                body: formData
            });
            const data = await resp.json();
            if (data.status === 'ok') {
                showToast('✅ Видео загружено на YouTube!', 'success');
            } else {
                showToast('❌ Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
            }
        } catch (e) {
            showToast('❌ Ошибка: ' + e.message, 'error');
        }
    };
    fileInput.click();
};
