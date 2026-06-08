// ==========================================
// Файл: static/js/quotes.js
// Справка: README.md → Веб-морда / Цитаты
// Задача: управление цитатами (добавление, просмотр)
// Комментарий: исправлены пути на /api/quotes/add, /api/quotes/list, добавлены проверки
// Зависит от: ui.js (showToast), helpers.js (escapeHtml)
// Вызывается из: main.js (импорт)
// ==========================================

import { showToast } from './ui.js';
import { escapeHtml } from './helpers.js';

export async function fetchQuotes() {
    const quotesList = document.getElementById('quotes-list');
    if (!quotesList) return;
    
    quotesList.innerHTML = '<li style="color: var(--text-secondary);">⏳ Загрузка...</li>';
    
    try {
        const resp = await fetch('/api/quotes/list');
        const data = await resp.json();
        
        if (data.quotes && data.quotes.length) {
            quotesList.innerHTML = data.quotes.map(q => `<li>${escapeHtml(q.substring(0, 200))}${q.length > 200 ? '...' : ''}</li>`).join('');
        } else {
            quotesList.innerHTML = '<li style="color: var(--text-secondary);">📜 Нет цитат. Добавьте первую.</li>';
        }
    } catch (e) {
        console.error('Ошибка загрузки цитат:', e);
        quotesList.innerHTML = '<li style="color: #f00;">❌ Ошибка загрузки цитат</li>';
        showToast('❌ Ошибка загрузки цитат: ' + e.message, 'error');
    }
}

export async function addQuote() {
    const quoteInput = document.getElementById('new-quote');
    if (!quoteInput) {
        showToast('❌ Элемент new-quote не найден на странице', 'error');
        return;
    }
    
    const text = quoteInput.value.trim();
    if (!text) {
        showToast('📝 Введите текст цитаты', 'info');
        return;
    }
    
    // Блокируем кнопку на время отправки
    const addButton = document.querySelector('#quotes-card button[onclick="addQuote()"]');
    if (addButton) {
        addButton.disabled = true;
        addButton.textContent = '⏳ Добавление...';
    }
    
    try {
        const resp = await fetch('/api/quotes/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ quote: text })
        });
        const data = await resp.json();
        
        if (data.status === 'ok') {
            showToast('✅ Цитата добавлена', 'success');
            quoteInput.value = '';
            // Перезагружаем список цитат
            await fetchQuotes();
        } else {
            showToast('❌ Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch (e) {
        showToast('❌ Ошибка: ' + e.message, 'error');
    } finally {
        if (addButton) {
            addButton.disabled = false;
            addButton.textContent = '➕ Добавить цитату';
        }
    }
}

// Функция для удаления цитаты (если API поддерживает)
export async function deleteQuote(index) {
    if (!confirm('Удалить эту цитату?')) return;
    
    try {
        const resp = await fetch(`/api/quotes/delete/${index}`, { method: 'DELETE' });
        const data = await resp.json();
        
        if (data.status === 'ok') {
            showToast('✅ Цитата удалена', 'success');
            await fetchQuotes();
        } else {
            showToast('❌ Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch (e) {
        showToast('❌ Ошибка: ' + e.message, 'error');
    }
}
