// ==========================================
// Файл: static/js/modules/debug.js
// Справка: README.md → Веб-морда / Дебаггер
// Задача: логи, аудит, индекс (просмотр и управление)
// Комментарий: работает с API /api/debug/*, /api/audit/*
// Зависит от: utils.js (escapeHtml)
// Вызывается из: admin.html (кнопки дебаггера)
// ==========================================

import { escapeHtml } from './utils.js';

/**
 * Показывает последние логи (100 строк)
 */
export async function fetchDebugLogs() {
    const container = document.getElementById('debug-report');
    if (!container) return;
    
    container.innerHTML = '<div style="color: var(--accent);">⏳ Загрузка...</div>';
    
    try {
        const response = await fetch('/api/debug/logs?limit=100');
        const data = await response.json();
        
        if (data.logs && data.logs.length) {
            let html = '<details><summary>🐛 Логи (' + data.logs.length + ')</summary><pre>';
            data.logs.forEach(log => {
                html += `[${log.level}] ${log.module} | ${escapeHtml(log.message)}\n`;
            });
            html += '</pre></details>';
            container.innerHTML = html;
        } else {
            container.innerHTML = '<div style="color: var(--text-secondary);">Логов нет</div>';
        }
    } catch(e) {
        console.error('Ошибка загрузки логов:', e);
        container.innerHTML = '<div style="color: #f00;">❌ Ошибка загрузки логов</div>';
    }
}

/**
 * Отправляет отчёт с логами в Telegram
 */
export async function sendDebugReport() {
    const container = document.getElementById('debug-report');
    if (!container) return;
    
    container.innerHTML = '<div style="color: var(--accent);">⏳ Отправка...</div>';
    
    try {
        const response = await fetch('/api/debug/send', { method: 'POST' });
        const data = await response.json();
        
        if (data.status === 'ok') {
            container.innerHTML = '<div style="color: var(--success);">✅ Отчёт отправлен в Telegram</div>';
        } else {
            container.innerHTML = '<div style="color: #f00;">❌ Ошибка: ' + escapeHtml(data.message || 'неизвестная') + '</div>';
        }
    } catch(e) {
        console.error('Ошибка отправки отчёта:', e);
        container.innerHTML = '<div style="color: #f00;">❌ Ошибка отправки</div>';
    }
    
    setTimeout(() => {
        if (container.innerHTML.includes('✅') || container.innerHTML.includes('❌')) {
            container.innerHTML = '';
        }
    }, 5000);
}

/**
 * Запускает аудит (проверка REDMI-шапок, библиотеки, импортов)
 */
export async function runAudit() {
    const container = document.getElementById('audit-result');
    if (!container) return;
    
    container.innerHTML = '<div style="color: var(--accent);">⏳ Запуск аудита...</div>';
    
    try {
        const response = await fetch('/api/audit/run', { method: 'POST' });
        const data = await response.json();
        
        if (data.status === 'ok') {
            let html = '<details><summary>✅ Аудит выполнен</summary><pre>';
            html += JSON.stringify(data.results, null, 2);
            html += '</pre></details>';
            container.innerHTML = html;
        } else {
            container.innerHTML = `<div style="color: #f00;">❌ Ошибка: ${data.message}</div>`;
        }
    } catch(e) {
        console.error('Ошибка запуска аудита:', e);
        container.innerHTML = '<div style="color: #f00;">❌ Ошибка запуска аудита</div>';
    }
}

/**
 * Показывает статус последнего аудита
 */
export async function showAuditStatus() {
    const container = document.getElementById('audit-result');
    if (!container) return;
    
    container.innerHTML = '<div style="color: var(--accent);">⏳ Загрузка...</div>';
    
    try {
        const response = await fetch('/api/audit/status');
        const data = await response.json();
        
        if (data.audit_exists) {
            let html = '<details><summary>📊 Статус аудита</summary>';
            html += `<p>Последний аудит: ${data.last_audit || 'никогда'}</p>`;
            if (data.results) {
                html += '<pre>' + JSON.stringify(data.results, null, 2) + '</pre>';
            }
            html += '</details>';
            container.innerHTML = html;
        } else {
            container.innerHTML = '<div style="color: var(--text-secondary);">Аудит ещё не запускался</div>';
        }
    } catch(e) {
        console.error('Ошибка загрузки статуса аудита:', e);
        container.innerHTML = '<div style="color: #f00;">❌ Ошибка загрузки статуса</div>';
    }
}

/**
 * Показывает индекс (базу знаний) из debug_index.json
 */
export async function showDebugIndex() {
    const container = document.getElementById('index-result');
    if (!container) return;
    
    container.innerHTML = '<div style="color: var(--accent);">⏳ Загрузка...</div>';
    
    try {
        const response = await fetch('/api/audit/index');
        const data = await response.json();
        
        if (data.status === 'ok') {
            let html = '<details><summary>🗂️ Индекс (база знаний)</summary>';
            html += '<pre>' + JSON.stringify(data.index, null, 2) + '</pre>';
            html += '</details>';
            container.innerHTML = html;
        } else {
            container.innerHTML = `<div style="color: #f00;">❌ Ошибка: ${data.message}</div>`;
        }
    } catch(e) {
        console.error('Ошибка загрузки индекса:', e);
        container.innerHTML = '<div style="color: #f00;">❌ Ошибка загрузки индекса</div>';
    }
}

// Глобальные функции для onclick из HTML
window.fetchDebugLogs = fetchDebugLogs;
window.sendDebugReport = sendDebugReport;
window.runAudit = runAudit;
window.showAuditStatus = showAuditStatus;
window.showDebugIndex = showDebugIndex;
