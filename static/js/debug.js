// ==========================================
// Файл: static/js/debug.js
// Справка: README.md → Веб-морда / Дебаггер
// Задача: дебаггер (логи, аудит, индекс)
// Комментарий: функции fetchDebugLogs, sendDebugReport, runAudit, showAuditStatus, showDebugIndex
// Зависит от: ui.js (showToast)
// Вызывается из: main.js (импорт)
// ==========================================

import { showToast } from './ui.js';

export async function fetchDebugLogs() {
    const reportDiv = document.getElementById('debug-report');
    reportDiv.innerHTML = '⏳ Загрузка логов...';
    
    try {
        const resp = await fetch('/api/debug/logs');
        const data = await resp.json();
        reportDiv.innerHTML = `<pre style="max-height: 300px; overflow-y: auto; background: #f8f8fa; padding: 1rem; border-radius: 12px;">${escapeHtml(JSON.stringify(data, null, 2))}</pre>`;
    } catch(e) {
        showToast('❌ Ошибка загрузки логов: ' + e.message, 'error');
    }
}

export async function sendDebugReport() {
    const reportDiv = document.getElementById('debug-report');
    reportDiv.innerHTML = '⏳ Отправка отчёта...';
    
    try {
        const resp = await fetch('/api/debug/send_report', { method: 'POST' });
        const data = await resp.json();
        if (data.status === 'ok') {
            reportDiv.innerHTML = '✅ Отчёт отправлен в Telegram';
        } else {
            showToast('❌ Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch(e) {
        showToast('❌ Ошибка: ' + e.message, 'error');
    }
}

export async function runAudit() {
    const resultDiv = document.getElementById('audit-result');
    resultDiv.innerHTML = '⏳ Аудит запущен...';
    
    try {
        const resp = await fetch('/api/audit/run', { method: 'POST' });
        const data = await resp.json();
        if (data.status === 'ok') {
            resultDiv.innerHTML = '✅ Аудит завершён. Проверьте README.md';
        } else {
            showToast('❌ Ошибка аудита: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch(e) {
        showToast('❌ Ошибка: ' + e.message, 'error');
    }
}

export async function showAuditStatus() {
    const resultDiv = document.getElementById('audit-result');
    resultDiv.innerHTML = '⏳ Загрузка статуса...';
    
    try {
        const resp = await fetch('/api/audit/status');
        const data = await resp.json();
        if (data.status === 'ok') {
            resultDiv.innerHTML = `<pre style="max-height: 300px; overflow-y: auto; background: #f8f8fa; padding: 1rem; border-radius: 12px;">${escapeHtml(JSON.stringify(data, null, 2))}</pre>`;
        } else {
            showToast('❌ Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch(e) {
        showToast('❌ Ошибка: ' + e.message, 'error');
    }
}

export async function showDebugIndex() {
    const resultDiv = document.getElementById('index-result');
    resultDiv.innerHTML = '⏳ Загрузка индекса...';
    
    try {
        const resp = await fetch('/api/debug/index');
        const data = await resp.json();
        if (data.status === 'ok') {
            resultDiv.innerHTML = `<pre style="max-height: 300px; overflow-y: auto; background: #f8f8fa; padding: 1rem; border-radius: 12px;">${escapeHtml(JSON.stringify(data, null, 2))}</pre>`;
        } else {
            showToast('❌ Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch(e) {
        showToast('❌ Ошибка: ' + e.message, 'error');
    }
}
