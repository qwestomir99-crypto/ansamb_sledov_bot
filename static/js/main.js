// ==========================================
// Файл: static/js/main.js
// Справка: README.md → Веб-морда / Точка входа
// Задача: инициализация всех модулей веб-морды
// Комментарий: импортирует и запускает модули после загрузки DOM
// Зависит от: modules/socket.js, modules/modes.js
// Вызывается из: templates/admin.html (type="module")
// ==========================================

import { connectSocket } from './modules/socket.js';
import { fetchState, fetchMood } from './modules/modes.js';

/**
 * Инициализирует веб-морду: подключает WebSocket и загружает начальные данные
 */
function init() {
    connectSocket();
    fetchState();
    fetchMood();
    
    // Обновляем состояние каждые 60 секунд
    setInterval(() => {
        fetchState();
        fetchMood();
    }, 60000);
}

// Запускаем инициализацию после полной загрузки DOM
document.addEventListener("DOMContentLoaded", init);
