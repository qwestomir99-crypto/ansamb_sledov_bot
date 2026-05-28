// ==========================================
// Файл: static/js/mail.js
// Справка: README.md → Веб-морда / Почта
// Задача: интерфейс для чтения и отправки писем в веб-морде
// Комментарий: использует /api/mail/inbox и /api/mail/send
// Зависит от: ui.js (showToast), helpers.js (escapeHtml)
// Вызывается из: main.js (импорт)
// ==========================================

import { showToast } from './ui.js';
import { escapeHtml } from './helpers.js';

export function initMail() {
    loadInbox();
}

async function loadInbox() {
    const container = document.getElementById('mail-inbox');
    try {
        const resp = await fetch('/api/mail/inbox');
        const emails = await resp.json();
        if (!emails.length) {
            container.innerHTML = '<p style="color: var(--text-secondary);">Нет писем</p>';
            return;
        }
        container.innerHTML = emails.map(e => `
            <div class="email-item">
                <div><strong>${escapeHtml(e.from)}</strong></div>
                <div>${escapeHtml(e.subject)}</div>
                <div style="font-size: 0.8rem; color: var(--text-secondary);">${escapeHtml(e.date)}</div>
                <div>${escapeHtml(e.body)}...</div>
            </div>
        `).join('');
    } catch (e) {
        showToast('Ошибка загрузки писем', 'error');
    }
}

window.sendMail = async function() {
    const to = document.getElementById('mail-to').value;
    const subject = document.getElementById('mail-subject').value;
    const body = document.getElementById('mail-body').value;
    if (!to || !subject || !body) {
        showToast('Заполните все поля', 'warning');
        return;
    }
    try {
        await fetch('/api/mail/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ to, subject, body })
        });
        showToast('Письмо отправлено', 'success');
        document.getElementById('mail-to').value = '';
        document.getElementById('mail-subject').value = '';
        document.getElementById('mail-body').value = '';
        loadInbox();
    } catch (e) {
        showToast('Ошибка отправки письма', 'error');
    }
};
