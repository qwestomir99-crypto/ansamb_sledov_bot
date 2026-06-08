// ==========================================
// Файл: static/js/main.js
// Справка: README.md → Веб-морда / Точка входа
// Задача: инициализация всех модулей веб-морды
// Комментарий: импортирует все функции из модулей, добавлена защита от ошибок
// Зависит от: socket.js, replies.js, posts.js, bot.js, quotes.js, debug.js, ui.js, helpers.js, dialogue.js, drafts.js, mail.js, uploads.js
// Вызывается из: templates/index.html
// ==========================================

// Импорт модулей
import { initSocket } from './socket.js';
import { initReplies } from './replies.js';
import { createPost, sendPost, createPostWithMedia } from './posts.js';
import { setMode, setMood, togglePing, toggleAlice, fetchMode, fetchMood } from './bot.js';
import { addQuote } from './quotes.js';
import { fetchDebugLogs, sendDebugReport, runAudit, showAuditStatus, showDebugIndex } from './debug.js';
import { showToast } from './ui.js';
import { escapeHtml } from './helpers.js';
import { initDialogue } from './dialogue.js';
import { initDrafts } from './drafts.js';
import { initMail } from './mail.js';
import { initUploads } from './uploads.js';

// ==========================================
// ГЛОБАЛЬНЫЕ ФУНКЦИИ ДЛЯ HTML-КНОПОК
// ==========================================
window.createPost = createPost;
window.sendPost = sendPost;
window.createPostWithMedia = createPostWithMedia;
window.setMode = setMode;
window.setMood = setMood;
window.togglePing = togglePing;
window.toggleAlice = toggleAlice;
window.addQuote = addQuote;
window.fetchDebugLogs = fetchDebugLogs;
window.sendDebugReport = sendDebugReport;
window.runAudit = runAudit;
window.showAuditStatus = showAuditStatus;
window.showDebugIndex = showDebugIndex;
window.showToast = showToast;
window.escapeHtml = escapeHtml;
window.fetchMode = fetchMode;
window.fetchMood = fetchMood;

// ==========================================
// ИНИЦИАЛИЗАЦИЯ МОДУЛЕЙ С ЗАЩИТОЙ ОТ ОШИБОК
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    // Функция-обёртка для безопасной инициализации
    const safeInit = (initFn, name) => {
        try {
            if (typeof initFn === 'function') {
                initFn();
                console.log(`✅ ${name} инициализирован`);
            } else {
                console.warn(`⚠️ ${name} не является функцией`);
            }
        } catch (e) {
            console.error(`❌ Ошибка инициализации ${name}:`, e);
        }
    };
    
    // Инициализируем модули, которые не требуют обязательного наличия элементов
    safeInit(initSocket, 'Socket');
    safeInit(initReplies, 'Replies');
    safeInit(initDialogue, 'Dialogue');
    safeInit(initDrafts, 'Drafts');
    safeInit(initMail, 'Mail');
    safeInit(initUploads, 'Uploads');
    
    // Загружаем текущее состояние (режим и настроение)
    if (typeof fetchMode === 'function') {
        fetchMode().catch(e => console.warn('Ошибка загрузки режима:', e));
    }
    if (typeof fetchMood === 'function') {
        fetchMood().catch(e => console.warn('Ошибка загрузки настроения:', e));
    }
    
    // Обновляем состояние каждые 60 секунд
    setInterval(() => {
        if (typeof fetchMode === 'function') fetchMode().catch(e => console.warn(e));
        if (typeof fetchMood === 'function') fetchMood().catch(e => console.warn(e));
    }, 60000);
    
    console.log('🔥 Веб-морда Ансамбля Следов 6 загружена');
});
