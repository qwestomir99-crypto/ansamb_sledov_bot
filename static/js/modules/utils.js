// ==========================================
// Файл: static/js/modules/utils.js
// Справка: README.md → Веб-морда / Утилиты
// Задача: общие вспомогательные функции
// Комментарий: используется всеми модулями веб-морды
// Зависит от: нет
// Вызывается из: modules/*.js
// ==========================================

/**
 * Экранирует HTML-спецсимволы для безопасной вставки в DOM
 * @param {string} text - текст для экранирования
 * @returns {string} экранированный текст
 */
export function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Форматирует дату в локальное время
 * @param {string} isoString - дата в ISO формате
 * @returns {string} отформатированное время (ЧЧ:ММ:СС)
 */
export function formatTime(isoString) {
    if (!isoString) return new Date().toLocaleTimeString();
    const date = new Date(isoString);
    return date.toLocaleTimeString();
}

/**
 * Показывает временное всплывающее сообщение
 * @param {string} message - текст сообщения
 * @param {string} type - тип ('success', 'error', 'info')
 * @param {number} duration - длительность показа в мс
 */
export function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: ${type === 'success' ? '#34c759' : type === 'error' ? '#ff3b30' : '#007aff'};
        color: white;
        padding: 10px 16px;
        border-radius: 12px;
        font-size: 0.85rem;
        z-index: 1000;
        animation: fadeInOut ${duration}ms ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    `;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.remove();
    }, duration);
}

/**
 * Задержка (промис-таймаут)
 * @param {number} ms - миллисекунды
 * @returns {Promise} промис, который резолвится через ms мс
 */
export function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Копирует текст в буфер обмена
 * @param {string} text - текст для копирования
 * @returns {Promise<boolean>} успех операции
 */
export async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('Скопировано', 'success', 1500);
        return true;
    } catch (e) {
        console.error('Ошибка копирования:', e);
        showToast('Не удалось скопировать', 'error', 1500);
        return false;
    }
}

/**
 * Загружает JSON с сервера с обработкой ошибок
 * @param {string} url - URL запроса
 * @param {Object} options - опции fetch
 * @returns {Promise<Object>} результат запроса
 */
export async function fetchJSON(url, options = {}) {
    try {
        const response = await fetch(url, options);
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || data.message || `HTTP ${response.status}`);
        }
        return data;
    } catch (e) {
        console.error(`[fetchJSON] ${url}:`, e);
        throw e;
    }
}
