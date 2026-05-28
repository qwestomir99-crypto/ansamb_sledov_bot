// ==========================================
// Файл: static/js/main.js
// Справка: README.md → Веб-морда / Точка входа
// Задача: инициализация всех модулей веб-морды
// Комментарий: импортирует все функции из модулей
// Зависит от: socket.js, replies.js, posts.js, bot.js, quotes.js, debug.js, ui.js, helpers.js, dialogue.js, drafts.js, mail.js, uploads.js
// Вызывается из: templates/admin.html
// ==========================================

import { initSocket } from './socket.js';
import { initReplies } from './replies.js';
import { createPost, sendPost, createPostWithMedia } from './posts.js';
import { setMode, togglePing, toggleAlice } from './bot.js';
import { addQuote } from './quotes.js';
import { fetchDebugLogs, sendDebugReport, runAudit, showAuditStatus, showDebugIndex } from './debug.js';
import { showToast } from './ui.js';
import { escapeHtml } from './helpers.js';
import { initDialogue } from './dialogue.js';
import { initDrafts } from './drafts.js';
import { initMail } from './mail.js';
import { initUploads } from './uploads.js';

// Подключаем глобальные переменные для доступа из HTML
window.createPost = createPost;
window.sendPost = sendPost;
window.createPostWithMedia = createPostWithMedia;
window.setMode = setMode;
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

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    initSocket();
    initReplies();
    initDialogue();
    initDrafts();
    initMail();
    initUploads();
});
