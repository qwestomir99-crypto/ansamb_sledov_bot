// ==========================================
// Файл: static/js/quotes.js
// Справка: README.md → Веб-морда / Цитаты
// Задача: управление цитатами (добавление)
// Комментарий: функции addQuote
// Зависит от: ui.js (showToast)
// Вызывается из: main.js (импорт)
// ==========================================

import { showToast } from './ui.js';

export async function addQuote() {
    const text = document.getElementById('new-quote').value.trim();
    if (!text) return;
    
    try {
        const resp = await fetch('/api/add_quote', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });
        const data = await resp.json();
        if (data.status === 'ok') {
            document.getElementById('new-quote').value = '';
            // Перезагружаем список цитат
            const quotesResp = await fetch('/api/get_quotes');
            const quotesData = await quotesResp.json();
            const quotesList = document.getElementById('quotes-list');
            quotesList.innerHTML = '';
            quotesData.quotes.forEach(q => {
                const li = document.createElement('li');
                li.textContent = q;
                quotesList.appendChild(li);
            });
        } else {
            showToast('Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch(e) {
        showToast('Ошибка: ' + e.message, 'error');
    }
}
