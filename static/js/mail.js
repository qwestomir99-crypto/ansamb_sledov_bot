// ==========================================
// Файл: static/js/mail.js
// Справка: README.md → Веб-морда / Почта
// Задача: управление почтой (отправка, получение)
// Комментарий: исправлены пути на /api/mail/..., добавлен импорт escapeHtml
// Зависит от: ui.js (showToast), helpers.js (escapeHtml)
// Вызывается из: main.js (импорт)
// ==========================================

import { showToast } from './ui.js';
import { escapeHtml } from './helpers.js';

export function initMail() {
    // Проверяем, есть ли почтовый блок на странице
    const inboxDiv = document.getElementById('mail-inbox');
    if (!inboxDiv) {
        // Почта не используется на этой странице — просто выходим
        return;
    }
    
    // Загружаем письма при инициализации
    loadInbox();
    
    // Можно добавить кнопку обновления, если её нет
    const refreshBtn = document.getElementById('mail-refresh');
    if (refreshBtn) {
        refreshBtn.onclick = () => loadInbox();
    }
}

async function loadInbox() {
    const inboxDiv = document.getElementById('mail-inbox');
    if (!inboxDiv) return;
    
    inboxDiv.innerHTML = '<div style="color: var(--text-secondary);">⏳ Загрузка...</div>';
    
    try {
        const resp = await fetch('/api/mail/inbox');
        const data = await resp.json();
        
        if (data.emails && data.emails.length) {
            let html = '';
            for (const email of data.emails) {
                const dateStr = email.date ? new Date(email.date).toLocaleString() : '';
                html += `
                    <div style="padding: 0.75rem; border-bottom: 1px solid var(--border); margin-bottom: 0.5rem;">
                        <div><strong>📧 ${escapeHtml(email.from)}</strong></div>
                        <div><strong>Тема:</strong> ${escapeHtml(email.subject)}</div>
                        ${dateStr ? `<div><small>📅 ${escapeHtml(dateStr)}</small></div>` : ''}
                        <details style="margin-top: 0.5rem;">
                            <summary style="cursor: pointer; color: var(--accent);">📄 Показать текст</summary>
                            <div style="margin-top: 0.5rem; padding: 0.5rem; background: var(--bg); border-radius: 8px;">
                                ${escapeHtml(email.body || email.message || 'Нет текста')}
                            </div>
                        </details>
                    </div>
                `;
            }
            inboxDiv.innerHTML = html;
        } else {
            inboxDiv.innerHTML = '<div style="color: var(--text-secondary);">📭 Нет писем</div>';
        }
    } catch(e) {
        console.error('Ошибка загрузки почты:', e);
        inboxDiv.innerHTML = '<div style="color: #f00;">❌ Ошибка загрузки почты</div>';
        showToast('Ошибка загрузки почты: ' + e.message, 'error');
    }
}

// Функция для ручного обновления (можно вызвать из кнопки)
window.refreshMail = function() {
    loadInbox();
};

window.sendMail = async function() {
    const toInput = document.getElementById('mail-to');
    const subjectInput = document.getElementById('mail-subject');
    const bodyInput = document.getElementById('mail-body');
    
    if (!toInput || !subjectInput || !bodyInput) {
        showToast('Элементы формы не найдены на странице', 'error');
        return;
    }
    
    const to = toInput.value.trim();
    const subject = subjectInput.value.trim();
    const body = bodyInput.value.trim();
    
    if (!to || !body) {
        showToast('Получатель и текст сообщения обязательны', 'error');
        return;
    }
    
    const sendBtn = document.querySelector('#mail-panel button[onclick="sendMail()"]');
    if (sendBtn) {
        sendBtn.disabled = true;
        sendBtn.textContent = '⏳ Отправка...';
    }
    
    try {
        const resp = await fetch('/api/mail/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ to, subject, body })
        });
        const data = await resp.json();
        
        if (data.status === 'ok') {
            showToast('✅ Письмо отправлено', 'success');
            toInput.value = '';
            subjectInput.value = '';
            bodyInput.value = '';
        } else {
            showToast('❌ Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch(e) {
        showToast('❌ Ошибка: ' + e.message, 'error');
    } finally {
        if (sendBtn) {
            sendBtn.disabled = false;
            sendBtn.textContent = '📤 Отправить';
        }
    }
};
