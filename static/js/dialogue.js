// ==========================================
// Файл: static/js/dialogue.js
// Справка: README.md → Веб-морда / Диалог с агентом
// Задача: отправка сообщений агенту и отображение истории
// Комментарий: исправлен путь на /api/agent/ask, убрана двойная инициализация
// Зависит от: helpers.js, ui.js
// Вызывается из: main.js (импорт)
// ==========================================

import { escapeHtml } from './helpers.js';
import { showToast } from './ui.js';

export function initDialogue() {
    const input = document.getElementById('chat-input');
    const history = document.getElementById('chat-history');
    
    if (!input || !history) {
        console.error('dialogue.js: не найдены элементы chat-input или chat-history');
        return;
    }
    
    window.sendToAgent = async function() {
        const message = input.value.trim();
        if (!message) return;
        
        // Добавляем сообщение пользователя в историю
        const userMessageDiv = document.createElement('div');
        userMessageDiv.style.textAlign = 'right';
        userMessageDiv.style.margin = '5px 0';
        userMessageDiv.innerHTML = `<strong>Вы:</strong> ${escapeHtml(message)}`;
        history.appendChild(userMessageDiv);
        history.scrollTop = history.scrollHeight;
        
        input.value = '';
        
        try {
            const resp = await fetch('/api/agent/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });
            const data = await resp.json();
            const answer = data.response || data.reply || 'Нет ответа от агента.';
            
            const agentMessageDiv = document.createElement('div');
            agentMessageDiv.style.textAlign = 'left';
            agentMessageDiv.style.margin = '5px 0';
            agentMessageDiv.innerHTML = `<strong>Агент:</strong> ${escapeHtml(answer)}`;
            history.appendChild(agentMessageDiv);
            history.scrollTop = history.scrollHeight;
        } catch (e) {
            showToast('Ошибка связи с агентом: ' + e.message, 'error');
            // Добавляем сообщение об ошибке в историю
            const errorDiv = document.createElement('div');
            errorDiv.style.textAlign = 'left';
            errorDiv.style.margin = '5px 0';
            errorDiv.style.color = 'var(--error, #ff3b30)';
            errorDiv.innerHTML = `<strong>⚠️ Ошибка:</strong> ${escapeHtml(e.message)}`;
            history.appendChild(errorDiv);
            history.scrollTop = history.scrollHeight;
        }
    };
}
