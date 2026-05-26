// ==========================================
// Файл: static/js/modules/socket.js
// Справка: README.md → Веб-морда / WebSocket
// Задача: WebSocket соединение и приём сообщений
// Комментарий: подключается к серверу, получает историю и обновления
// Зависит от: socket.io (глобальная), модуль messages.js
// Вызывается из: main.js
// ==========================================

import { appendMessage } from './messages.js';

let socket = null;

/**
 * Устанавливает WebSocket соединение
 */
export function connectSocket() {
    if (socket && socket.connected) {
        console.log('Socket already connected');
        return;
    }
    
    socket = io();
    
    socket.on('message_history', (msgs) => {
        const container = document.getElementById('messages');
        if (!container) return;
        container.innerHTML = '';
        if (msgs && msgs.length) {
            msgs.forEach(msg => appendMessage(msg));
        } else {
            container.innerHTML = '<div style="color: var(--text-secondary);">Нет сообщений</div>';
        }
    });
    
    socket.on('message_updated', (msg) => {
        if (msg) appendMessage(msg);
    });
    
    socket.on('connect', () => {
        console.log('Socket connected');
    });
    
    socket.on('disconnect', () => {
        console.log('Socket disconnected');
    });
    
    socket.on('connect_error', (err) => {
        console.error('Socket connection error:', err);
    });
}

/**
 * Отключает WebSocket соединение
 */
export function disconnectSocket() {
    if (socket) {
        socket.disconnect();
        socket = null;
    }
}

/**
 * Возвращает текущий socket (для прямого использования при необходимости)
 * @returns {Object|null} socket или null
 */
export function getSocket() {
    return socket;
}
