// ==========================================
// Файл: static/js/helpers.js
// Справка: README.md → Веб-морда / Вспомогательные
// Задача: общие вспомогательные функции
// Комментарий: escapeHtml и другие утилиты
// Зависит от: нет
// Вызывается из: main.js (импорт)
// ==========================================

export function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
