// ==========================================
// Файл: static/js/modules/modes.js
// Справка: README.md → Веб-морда / Режимы
// Задача: управление режимами бота (утро/день/вечер/ночь) и пингом
// Комментарий: работает с API /api/set_mode, /api/state, /api/toggle_ping
// Зависит от: utils.js (escapeHtml для цитат)
// Вызывается из: main.js, admin.html (кнопки)
// ==========================================

import { escapeHtml } from './utils.js';

/**
 * Устанавливает режим бота
 * @param {string} mode - режим ('утро', 'день', 'вечер', 'ночь')
 */
export async function setMode(mode) {
    try {
        const response = await fetch('/api/set_mode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: mode })
        });
        const data = await response.json();
        if (data.status === 'ok') {
            const modeSpan = document.getElementById('current-mode');
            if (modeSpan) modeSpan.innerText = mode;
        } else {
            console.error('Ошибка установки режима:', data.error);
        }
    } catch (e) {
        console.error('Ошибка сети:', e);
    }
}

/**
 * Загружает текущее состояние бота (режим и цитаты)
 */
export async function fetchState() {
    try {
        const response = await fetch('/api/state');
        const data = await response.json();
        if (data.mode) {
            const modeSpan = document.getElementById('current-mode');
            if (modeSpan) modeSpan.innerText = data.mode;
        }
        if (data.quotes && data.quotes.length) {
            const quotesList = document.getElementById('quotes-list');
            if (quotesList) {
                quotesList.innerHTML = data.quotes.map(q => `<li>${escapeHtml(q)}</li>`).join('');
            }
        }
    } catch(e) {
        console.error('Ошибка загрузки состояния:', e);
    }
}

/**
 * Переключает пинг бота
 */
export async function togglePing() {
    try {
        const response = await fetch('/api/toggle_ping', { method: 'POST' });
        const data = await response.json();
        alert(data.message || 'Пинг переключён');
    } catch (e) {
        console.error('Ошибка переключения пинга:', e);
        alert('Ошибка переключения пинга');
    }
}

/**
 * Загружает текущее настроение агента
 */
export async function fetchMood() {
    try {
        const response = await fetch('/api/get_mood');
        const data = await response.json();
        if (data.mood) {
            const moodNames = { 'artist': 'Художник', 'admin': 'Администратор', 'poet': 'Поэт', 'engineer': 'Инженер' };
            const moodSpan = document.getElementById('current-mood');
            if (moodSpan) moodSpan.innerText = moodNames[data.mood] || data.mood;
        }
    } catch(e) {
        console.error('Ошибка загрузки настроения:', e);
    }
}

/**
 * Устанавливает настроение агента
 * @param {string} mood - настроение ('artist', 'admin', 'poet', 'engineer')
 */
export async function setMood(mood) {
    try {
        const response = await fetch('/api/set_mood', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mood: mood })
        });
        const data = await response.json();
        if (data.status === 'ok') {
            const moodNames = { 'artist': 'Художник', 'admin': 'Администратор', 'poet': 'Поэт', 'engineer': 'Инженер' };
            const moodSpan = document.getElementById('current-mood');
            if (moodSpan) moodSpan.innerText = moodNames[mood] || mood;
        }
    } catch (e) {
        console.error('Ошибка установки настроения:', e);
    }
}

// Глобальные функции для onclick из HTML
window.setMode = setMode;
window.togglePing = togglePing;
window.setMood = setMood;
