// ==========================================
// Файл: static/js/modules/quotes.js
// Справка: README.md → Веб-морда / Цитаты
// Задача: управление цитатами (добавление, обновление списка)
// Комментарий: работает с API /api/add_quote
// Зависит от: fetchState (из modes.js)
// Вызывается из: admin.html (кнопка "➕ Добавить цитату")
// ==========================================

import { fetchState } from './modes.js';

/**
 * Добавляет новую цитату
 */
export async function addQuote() {
    const quoteInput = document.getElementById('new-quote');
    const quote = quoteInput?.value.trim();
    
    if (!quote) {
        alert("Введите текст цитаты");
        return;
    }
    
    try {
        const response = await fetch('/api/add_quote', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ quote: quote })
        });
        
        const data = await response.json();
        
        if (data.status === 'ok') {
            if (quoteInput) quoteInput.value = '';
            // Обновляем список цитат
            await fetchState();
        } else {
            alert('Ошибка: ' + (data.error || 'неизвестная'));
        }
    } catch (e) {
        console.error('Ошибка добавления цитаты:', e);
        alert('Ошибка сети при добавлении цитаты');
    }
}

// Глобальная функция для onclick из HTML
window.addQuote = addQuote;
