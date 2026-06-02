// ==========================================
// Файл: static/js/uploads.js
// Справка: README.md → Веб-морда / Загрузка
// Задача: загрузка файлов на сервер
// Комментарий: исправлен путь на /api/uploads/upload
// Зависит от: ui.js (showToast)
// Вызывается из: main.js (импорт)
// ==========================================

import { showToast } from './ui.js';

export function initUploads() {
    document.addEventListener('DOMContentLoaded', () => {
        // Можно добавить инициализацию
    });
}

window.uploadToYouTube = async function() {
    // Заглушка — позже реализуем
    showToast('Функция загрузки на YouTube в разработке', 'info');
};
