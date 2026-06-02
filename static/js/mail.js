// ==========================================
// Файл: static/js/mail.js
// Справка: README.md → Веб-морда / Почта
// Задача: управление почтой (отправка, получение)
// Комментарий: исправлены пути на /api/mail/...
// Зависит от: ui.js (showToast)
// Вызывается из: main.js (импорт)
// ==========================================

import { showToast } from './ui.js';

export function initMail() {
    document.addEventListener('DOMContentLoaded', () => {
        loadInbox();
    });
}

async function loadInbox() {
    try {
        const resp = await fetch('/api/mail/inbox');
        const data = await resp.json();
        const inboxDiv = document.getElementById('mail-inbox');
        if (data.emails && data.emails.length) {
            inboxDiv.innerHTML = data.emails.map(email =>
                `<div style="padding: 0.5rem; border-bottom: 1px solid var(--border);">
                    <strong>${escapeHtml(email.from)}</strong><br>
                    <small>${escapeHtml(email.subject)}</small>
                </div>`
            ).join('');
        } else {
            inboxDiv.innerHTML = 'Нет писем.';
        }
    } catch(e) {
        showToast('Ошибка загрузки почты: ' + e.message, 'error');
    }
}

window.sendMail = async function() {
    const to = document.getElementById('mail-to').value.trim();
    const subject = document.getElementById('mail-subject').value.trim();
    const body = document.getElementById('mail-body').value.trim();
    if (!to || !subject || !body) {
        showToast('Все поля обязательны', 'error');
        return;
    }
    try {
        const resp = await fetch('/api/mail/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ to, subject, body })
        });
        const data = await resp.json();
        if (data.status === 'ok') {
            showToast('Письмо отправлено', 'success');
            document.getElementById('mail-to').value = '';
            document.getElementById('mail-subject').value = '';
            document.getElementById('mail-body').value = '';
        } else {
            showToast('Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch(e) {
        showToast('Ошибка: ' + e.message, 'error');
    }
};
