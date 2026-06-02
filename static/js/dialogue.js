// ==========================================
// Файл: static/js/dialogue.js
// Справка: README.md → Веб-морда / Диалог с агентом
// Задача: отправка сообщений агенту и отображение истории
// Комментарий: исправлен путь на /api/agent/ask
// Зависит от: helpers.js, ui.js
// Вызывается из: main.js (импорт)
// ==========================================

import { escapeHtml } from './helpers.js';
import { showToast } from './ui.js';

export function initDialogue() {
    const input = document.getElementById('chat-input');
    const history = document.getElementById('chat-history');
    
    window.sendToAgent = async function() {
        const message = input.value.trim();
        if (!message) return;
        
        // Добавляем сообщение пользователя в историю
        history.innerHTML += `<div style="text-align: right; margin: 5px 0;"><strong>Вы:</strong> ${escapeHtml(message)}</div>`;
        input.value = '';
        history.scrollTop = history.scrollHeight;
        
        try {
            const resp = await fetch('/api/agent/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });
            const data = await resp.json();
            const answer = data.response || 'Нет ответа.';
            history.innerHTML += `<div style="text-align: left; margin: 5px 0;"><strong>Агент:</strong> ${escapeHtml(answer)}</div>`;
            history.scrollTop = history.scrollHeight;
        } catch (e) {
            showToast('Ошибка связи с агентом: ' + e.message, 'error');
        }
    };
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    initDialogue();
});
