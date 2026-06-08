// ==========================================
// Файл: static/js/ui.js
// Справка: README.md → Веб-морда / UI
// Задача: toast-уведомления, анимации, визуальные эффекты
// Комментарий: автоматическое создание контейнера, fallback на alert
// Зависит от: visuals.css
// Вызывается из: main.js (импорт)
// ==========================================

// Конфигурация
const DEFAULT_DURATION = 3000;
const ERROR_DURATION = 5000;

// Иконки для разных типов уведомлений
const icons = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️',
    debug: '🐛'
};

// Цвета для разных типов (если CSS не подключён)
const colors = {
    success: '#34c759',
    error: '#ff3b30',
    warning: '#ff9500',
    info: '#007aff',
    debug: '#86868b'
};

/**
 * Показывает всплывающее уведомление (toast)
 * @param {string} message - Текст уведомления
 * @param {string} type - Тип: 'success', 'error', 'warning', 'info', 'debug'
 * @param {number} duration - Длительность показа в мс (по умолчанию 3000)
 */
export function showToast(message, type = 'info', duration = DEFAULT_DURATION) {
    if (!message) return;
    
    // Получаем или создаём контейнер для уведомлений
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 10px;
            pointer-events: none;
        `;
        document.body.appendChild(container);
    }
    
    // Создаём элемент уведомления
    const toast = document.createElement('div');
    const icon = icons[type] || icons.info;
    const color = colors[type] || colors.info;
    
    toast.className = `toast toast-${type}`;
    toast.style.cssText = `
        background: rgba(30, 30, 35, 0.95);
        backdrop-filter: blur(10px);
        color: white;
        padding: 12px 20px;
        border-radius: 12px;
        font-size: 14px;
        font-family: -apple-system, 'SF Pro Text', sans-serif;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        border-left: 4px solid ${color};
        display: flex;
        align-items: center;
        gap: 10px;
        pointer-events: auto;
        animation: slideIn 0.3s ease;
        max-width: 350px;
        word-break: break-word;
    `;
    
    toast.innerHTML = `<span style="font-size: 18px;">${icon}</span><span>${escapeHtml(message)}</span>`;
    
    container.appendChild(toast);
    
    // Удаляем уведомление через указанное время
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            if (toast.parentNode) toast.remove();
        }, 300);
    }, type === 'error' ? ERROR_DURATION : duration);
}

/**
 * Простой escape для HTML (чтобы не подключать helpers.js ради одной функции)
 * @param {string} str - Строка для экранирования
 * @returns {string} Экранированная строка
 */
function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>]/g, function(m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}

// Добавляем CSS-анимации, если их нет в visuals.css
(function addAnimations() {
    if (document.getElementById('toast-animations')) return;
    
    const style = document.createElement('style');
    style.id = 'toast-animations';
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
})();

// Экспортируем также функцию для быстрого вызова (для консоли)
window.showToast = showToast;
