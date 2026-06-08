// ==========================================
// Файл: static/js/helpers.js
// Справка: README.md → Веб-морда / Вспомогательные
// Задача: общие вспомогательные функции
// Комментарий: escapeHtml, debounce, formatDate, truncate и другие утилиты
// Зависит от: нет
// Вызывается из: main.js (импорт)
// ==========================================

/**
 * Экранирует HTML-спецсимволы для безопасной вставки в DOM
 * @param {string} text - Текст для экранирования
 * @returns {string} Экранированный текст
 */
export function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Форматирует дату в локальный формат
 * @param {string|Date} date - Дата для форматирования
 * @param {boolean} withTime - Показывать время или только дату
 * @returns {string} Отформатированная дата
 */
export function formatDate(date, withTime = true) {
    if (!date) return '';
    const d = typeof date === 'string' ? new Date(date) : date;
    if (isNaN(d.getTime())) return '';
    
    const day = d.getDate().toString().padStart(2, '0');
    const month = (d.getMonth() + 1).toString().padStart(2, '0');
    const year = d.getFullYear();
    const time = withTime ? ` ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}` : '';
    
    return `${day}.${month}.${year}${time}`;
}

/**
 * Обрезает строку до заданной длины и добавляет многоточие
 * @param {string} str - Исходная строка
 * @param {number} maxLength - Максимальная длина
 * @returns {string} Обрезанная строка
 */
export function truncate(str, maxLength = 100) {
    if (!str) return '';
    if (str.length <= maxLength) return str;
    return str.substring(0, maxLength) + '...';
}

/**
 * Debounce (задержка вызова функции)
 * @param {Function} func - Функция для вызова
 * @param {number} delay - Задержка в миллисекундах
 * @returns {Function} Обёрнутая функция с debounce
 */
export function debounce(func, delay = 300) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

/**
 * Генерирует случайный ID (для временных элементов)
 * @returns {string} Случайный ID
 */
export function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substring(2);
}

/**
 * Проверяет, является ли значение валидным непустым
 * @param {any} value - Проверяемое значение
 * @returns {boolean} true если значение не null, не undefined и не пустая строка
 */
export function isValidValue(value) {
    return value !== null && value !== undefined && value !== '';
}

/**
 * Безопасно получает элемент по ID
 * @param {string} id - ID элемента
 * @returns {HTMLElement|null} Элемент или null
 */
export function getElementSafe(id) {
    return document.getElementById(id);
}

/**
 * Добавляет класс элементу с проверкой на существование
 * @param {string} id - ID элемента
 * @param {string} className - Имя класса
 */
export function addClassSafe(id, className) {
    const el = document.getElementById(id);
    if (el) el.classList.add(className);
}

/**
 * Удаляет класс элемента с проверкой на существование
 * @param {string} id - ID элемента
 * @param {string} className - Имя класса
 */
export function removeClassSafe(id, className) {
    const el = document.getElementById(id);
    if (el) el.classList.remove(className);
}
