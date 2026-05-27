// ==========================================
// Файл: static/js/ui.js
// Справка: README.md → Веб-морда / UI
// Задача: toast-уведомления, анимации, визуальные эффекты
// Комментарий: использует visuals.css
// Зависит от: visuals.css
// Вызывается из: main.js (импорт)
// ==========================================

export function showToast(message, type='info', duration=3000) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}
