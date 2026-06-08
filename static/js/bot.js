// ==========================================
// Файл: static/js/bot.js
// Справка: README.md → Веб-морда / Управление ботом
// Задача: управление ботом (режимы, пинг, Алиса, настроение)
// Комментарий: исправлены URL для совместимости с сервером
// Зависит от: ui.js (showToast)
// Вызывается из: main.js (импорт)
// ==========================================

import { showToast } from './ui.js';

export async function setMode(mode) {
    try {
        const resp = await fetch('/api/set_mode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: mode })
        });
        const data = await resp.json();
        if (data.status === 'ok') {
            const modeSpan = document.getElementById('current-mode');
            if (modeSpan) modeSpan.textContent = mode;
            showToast(`Режим изменён на ${mode}`, 'success');
        } else {
            showToast('Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch(e) {
        showToast('Ошибка: ' + e.message, 'error');
    }
}

export async function setMood(mood) {
    try {
        const resp = await fetch('/api/set_mood', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mood: mood })
        });
        const data = await resp.json();
        if (data.status === 'ok') {
            const moodNames = {
                'artist': 'Художник',
                'admin': 'Администратор',
                'poet': 'Поэт',
                'engineer': 'Инженер'
            };
            const moodSpan = document.getElementById('current-mood');
            if (moodSpan) moodSpan.textContent = moodNames[mood] || mood;
            showToast('Настроение: ' + (moodNames[mood] || mood), 'success');
        } else {
            showToast('Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch(e) {
        showToast('Ошибка: ' + e.message, 'error');
    }
}

export async function togglePing() {
    try {
        const resp = await fetch('/api/toggle_ping', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await resp.json();
        if (data.status === 'ok') {
            showToast(data.message || 'Пинг переключён', 'success');
        } else {
            showToast('❌ Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
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

export async function fetchMode() {
    try {
        const resp = await fetch('/api/state');
        const data = await resp.json();
        if (data.mode) {
            const modeSpan = document.getElementById('current-mode');
            if (modeSpan) modeSpan.textContent = data.mode;
        }
    } catch(e) {
        console.error('Ошибка загрузки режима:', e);
    }
}

export async function fetchMood() {
    try {
        const resp = await fetch('/api/get_mood');
        const data = await resp.json();
        if (data.mood) {
            const moodNames = {
                'artist': 'Художник',
                'admin': 'Администратор',
                'poet': 'Поэт',
                'engineer': 'Инженер'
            };
            const moodSpan = document.getElementById('current-mood');
            if (moodSpan) moodSpan.textContent = moodNames[data.mood] || data.mood;
        }
    } catch(e) {
        console.error('Ошибка загрузки настроения:', e);
    }
}
