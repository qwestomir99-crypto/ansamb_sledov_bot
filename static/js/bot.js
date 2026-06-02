// ==========================================
// Файл: static/js/bot.js
// Справка: README.md → Веб-морда / Управление ботом
// Задача: управление ботом (режимы, пинг, Алиса)
// Комментарий: исправлены пути на /api/modes/set, /api/ping, /api/alice/toggle
// Зависит от: ui.js (showToast)
// Вызывается из: main.js (импорт)
// ==========================================

import { showToast } from './ui.js';

export async function setMode(mode) {
    try {
        const resp = await fetch('/api/modes/set', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: mode })
        });
        const data = await resp.json();
        if (data.status === 'ok') {
            document.getElementById('current-mode').textContent = mode;
        } else {
            showToast('Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch(e) {
        showToast('Ошибка: ' + e.message, 'error');
    }
}

export async function togglePing() {
    try {
        const resp = await fetch('/api/ping', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await resp.json();
        if (data.status === 'ok') {
            showToast('✅ Бот отвечает: ' + data.message, 'success');
        } else {
            showToast('❌ Бот не отвечает: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch(e) {
        showToast('Ошибка: ' + e.message, 'error');
    }
}

export async function toggleAlice() {
    try {
        const resp = await fetch('/api/alice/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await resp.json();
        if (data.status === 'ok') {
            showToast(`Алиса ${data.enabled ? 'включена ✅' : 'выключена ❌'}`, 'success');
        } else {
            showToast('Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch(e) {
        showToast('Ошибка: ' + e.message, 'error');
    }
}
