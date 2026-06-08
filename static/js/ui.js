// ==========================================
// Файл: static/js/ui.js
// Справка: README.md → Веб-морда / UI
// Задача: toast-уведомления, анимации, визуальные эффекты
// Комментарий: добавлены полезные функции: confirmDialog, showLoading, hideLoading, showModal, closeModal
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

// ==========================================
// TOAST УВЕДОМЛЕНИЯ
// ==========================================

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

// ==========================================
// ДИАЛОГ ПОДТВЕРЖДЕНИЯ
// ==========================================

/**
 * Показывает диалог подтверждения с кастомными кнопками
 * @param {string} message - Текст сообщения
 * @param {string} confirmText - Текст кнопки подтверждения
 * @param {string} cancelText - Текст кнопки отмены
 * @returns {Promise<boolean>} - Promise, который разрешается в true/false
 */
export function confirmDialog(message, confirmText = 'Да', cancelText = 'Нет') {
    return new Promise((resolve) => {
        // Создаём затемнение
        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(4px);
            z-index: 10001;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: -apple-system, 'SF Pro Text', sans-serif;
        `;
        
        // Создаём диалоговое окно
        const dialog = document.createElement('div');
        dialog.style.cssText = `
            background: var(--card-bg, #ffffff);
            border-radius: 20px;
            padding: 24px;
            max-width: 400px;
            width: 90%;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
            border: 1px solid var(--border, rgba(0, 0, 0, 0.1));
        `;
        
        dialog.innerHTML = `
            <div style="margin-bottom: 20px; font-size: 16px; line-height: 1.4;">${escapeHtml(message)}</div>
            <div style="display: flex; gap: 12px; justify-content: flex-end;">
                <button id="confirm-cancel" style="
                    padding: 8px 16px;
                    border-radius: 10px;
                    border: 1px solid var(--border, #ccc);
                    background: transparent;
                    cursor: pointer;
                ">${escapeHtml(cancelText)}</button>
                <button id="confirm-ok" style="
                    padding: 8px 16px;
                    border-radius: 10px;
                    border: none;
                    background: var(--accent, #007aff);
                    color: white;
                    cursor: pointer;
                ">${escapeHtml(confirmText)}</button>
            </div>
        `;
        
        overlay.appendChild(dialog);
        document.body.appendChild(overlay);
        
        // Обработчики
        const okBtn = dialog.querySelector('#confirm-ok');
        const cancelBtn = dialog.querySelector('#confirm-cancel');
        
        const cleanup = (result) => {
            if (overlay.parentNode) overlay.remove();
            resolve(result);
        };
        
        okBtn.onclick = () => cleanup(true);
        cancelBtn.onclick = () => cleanup(false);
        overlay.onclick = (e) => {
            if (e.target === overlay) cleanup(false);
        };
    });
}

// ==========================================
// ИНДИКАТОРЫ ЗАГРУЗКИ
// ==========================================

let loadingOverlay = null;

/**
 * Показывает индикатор загрузки на весь экран
 * @param {string} message - Текст загрузки
 */
export function showLoading(message = 'Загрузка...') {
    hideLoading();
    
    loadingOverlay = document.createElement('div');
    loadingOverlay.id = 'loading-overlay';
    loadingOverlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(8px);
        z-index: 10002;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        gap: 16px;
        font-family: -apple-system, 'SF Pro Text', sans-serif;
        color: white;
    `;
    
    const spinner = document.createElement('div');
    spinner.style.cssText = `
        width: 48px;
        height: 48px;
        border: 4px solid rgba(255, 255, 255, 0.3);
        border-top-color: white;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    `;
    
    const text = document.createElement('div');
    text.textContent = message;
    text.style.fontSize = '16px';
    
    loadingOverlay.appendChild(spinner);
    loadingOverlay.appendChild(text);
    document.body.appendChild(loadingOverlay);
    
    // Добавляем анимацию, если её нет
    if (!document.getElementById('loading-animation')) {
        const style = document.createElement('style');
        style.id = 'loading-animation';
        style.textContent = `@keyframes spin { to { transform: rotate(360deg); } }`;
        document.head.appendChild(style);
    }
}

/**
 * Скрывает индикатор загрузки
 */
export function hideLoading() {
    if (loadingOverlay && loadingOverlay.parentNode) {
        loadingOverlay.remove();
        loadingOverlay = null;
    }
}

// ==========================================
// МОДАЛЬНЫЕ ОКНА
// ==========================================

let currentModal = null;

/**
 * Показывает модальное окно с произвольным содержимым
 * @param {string|HTMLElement} content - Содержимое (HTML строка или DOM элемент)
 * @param {string} title - Заголовок окна
 */
export function showModal(content, title = 'Информация') {
    closeModal();
    
    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(4px);
        z-index: 10003;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: -apple-system, 'SF Pro Text', sans-serif;
    `;
    
    const modal = document.createElement('div');
    modal.style.cssText = `
        background: var(--card-bg, #ffffff);
        border-radius: 20px;
        max-width: 600px;
        width: 90%;
        max-height: 80vh;
        overflow-y: auto;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
        border: 1px solid var(--border, rgba(0, 0, 0, 0.1));
    `;
    
    modal.innerHTML = `
        <div style="
            padding: 16px 20px;
            border-bottom: 1px solid var(--border, rgba(0, 0, 0, 0.1));
            display: flex;
            justify-content: space-between;
            align-items: center;
        ">
            <strong style="font-size: 18px;">${escapeHtml(title)}</strong>
            <button id="modal-close" style="
                background: transparent;
                border: none;
                font-size: 24px;
                cursor: pointer;
                color: var(--text-secondary, #666);
            ">×</button>
        </div>
        <div id="modal-body" style="padding: 20px;"></div>
    `;
    
    const bodyDiv = modal.querySelector('#modal-body');
    if (typeof content === 'string') {
        bodyDiv.innerHTML = content;
    } else if (content instanceof HTMLElement) {
        bodyDiv.appendChild(content);
    }
    
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
    currentModal = overlay;
    
    const closeBtn = modal.querySelector('#modal-close');
    closeBtn.onclick = closeModal;
    overlay.onclick = (e) => {
        if (e.target === overlay) closeModal();
    };
}

/**
 * Закрывает текущее модальное окно
 */
export function closeModal() {
    if (currentModal && currentModal.parentNode) {
        currentModal.remove();
        currentModal = null;
    }
}

// ==========================================
// УПРАВЛЕНИЕ КНОПКАМИ
// ==========================================

/**
 * Блокирует кнопку на время выполнения операции
 * @param {HTMLElement} button - Кнопка
 * @param {string} loadingText - Текст во время загрузки
 * @param {Function} callback - Функция, которая выполнится после разблокировки
 */
export async function withLoading(button, loadingText = '⏳ Загрузка...', callback) {
    if (!button) return;
    const originalText = button.textContent;
    const originalDisabled = button.disabled;
    
    button.disabled = true;
    button.textContent = loadingText;
    
    try {
        await callback();
    } finally {
        button.disabled = originalDisabled;
        button.textContent = originalText;
    }
}

// ==========================================
// ВСПОМОГАТЕЛЬНЫЕ
// ==========================================

/**
 * Простой escape для HTML
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

// Добавляем CSS-анимации, если их нет
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

// Экспортируем функции в глобальную область для использования из HTML
window.showToast = showToast;
window.confirmDialog = confirmDialog;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.showModal = showModal;
window.closeModal = closeModal;
