// ==========================================
// Файл: static/js/debug.js
// Справка: README.md → Веб-морда / Дебаггер
// Задача: дебаггер (логи, аудит, индекс)
// Комментарий: исправлены пути на /api/audit/..., добавлен импорт escapeHtml
// Зависит от: ui.js (showToast), helpers.js (escapeHtml)
// Вызывается из: main.js (импорт)
// ==========================================

import { showToast } from './ui.js';
import { escapeHtml } from './helpers.js';

export async function fetchDebugLogs() {
    const reportDiv = document.getElementById('debug-report');
    if (!reportDiv) return;
    reportDiv.innerHTML = '⏳ Загрузка логов...';
    
    try {
        const resp = await fetch('/api/audit/logs?limit=100');
        const data = await resp.json();
        if (data.logs && data.logs.length) {
            let html = '<details><summary>🐛 Логи (' + data.logs.length + ')</summary><pre style="max-height: 300px; overflow-y: auto; background: #f8f8fa; padding: 1rem; border-radius: 12px;">';
            data.logs.forEach(log => {
                html += `[${log.level}] ${log.module} | ${escapeHtml(log.message)}\n`;
            });
            html += '</pre></details>';
            reportDiv.innerHTML = html;
        } else {
            reportDiv.innerHTML = '<div style="color: var(--text-secondary);">Логов нет</div>';
        }
    } catch(e) {
        reportDiv.innerHTML = '<div style="color: #f00;">❌ Ошибка загрузки логов</div>';
        showToast('❌ Ошибка загрузки логов: ' + e.message, 'error');
    }
}

export async function sendDebugReport() {
    const reportDiv = document.getElementById('debug-report');
    if (!reportDiv) return;
    reportDiv.innerHTML = '⏳ Отправка отчёта...';
    
    try {
        const resp = await fetch('/api/audit/send_report', { method: 'POST' });
        const data = await resp.json();
        if (data.status === 'ok') {
            reportDiv.innerHTML = '✅ Отчёт отправлен в Telegram';
            showToast('✅ Отчёт отправлен в Telegram', 'success');
        } else {
            reportDiv.innerHTML = '<div style="color: #f00;">❌ Ошибка отправки отчёта</div>';
            showToast('❌ Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch(e) {
        reportDiv.innerHTML = '<div style="color: #f00;">❌ Ошибка отправки отчёта</div>';
        showToast('❌ Ошибка: ' + e.message, 'error');
    }
}

export async function runAudit() {
    const resultDiv = document.getElementById('audit-result');
    if (!resultDiv) return;
    resultDiv.innerHTML = '⏳ Аудит запущен...';
    
    try {
        const resp = await fetch('/api/audit/run', { method: 'POST' });
        const data = await resp.json();
        if (data.status === 'ok') {
            resultDiv.innerHTML = '<div style="color: var(--success);">✅ Аудит завершён. Проверьте README.md</div>';
            showToast('✅ Аудит завершён', 'success');
        } else {
            resultDiv.innerHTML = '<div style="color: #f00;">❌ Ошибка аудита</div>';
            showToast('❌ Ошибка аудита: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch(e) {
        resultDiv.innerHTML = '<div style="color: #f00;">❌ Ошибка запуска аудита</div>';
        showToast('❌ Ошибка: ' + e.message, 'error');
    }
}

export async function showAuditStatus() {
    const resultDiv = document.getElementById('audit-result');
    if (!resultDiv) return;
    resultDiv.innerHTML = '⏳ Загрузка статуса...';
    
    try {
        const resp = await fetch('/api/audit/status');
        const data = await resp.json();
        if (data.audit_exists) {
            let html = '<details><summary>📊 Статус аудита</summary>';
            html += `<p>Последний аудит: ${data.last_audit || 'никогда'}</p>`;
            if (data.results) {
                html += '<pre style="max-height: 300px; overflow-y: auto; background: #f8f8fa; padding: 1rem; border-radius: 12px;">' + JSON.stringify(data.results, null, 2) + '</pre>';
            }
            html += '</details>';
            resultDiv.innerHTML = html;
        } else {
            resultDiv.innerHTML = '<div style="color: var(--text-secondary);">Аудит ещё не запускался</div>';
        }
    } catch(e) {
        resultDiv.innerHTML = '<div style="color: #f00;">❌ Ошибка загрузки статуса</div>';
        showToast('❌ Ошибка: ' + e.message, 'error');
    }
}

export async function showDebugIndex() {
    const resultDiv = document.getElementById('index-result');
    if (!resultDiv) return;
    resultDiv.innerHTML = '⏳ Загрузка индекса...';
    
    try {
        const resp = await fetch('/api/audit/index');
        const data = await resp.json();
        if (data.status === 'ok') {
            let html = '<details><summary>🗂️ Индекс (база знаний)</summary>';
            html += '<pre style="max-height: 300px; overflow-y: auto; background: #f8f8fa; padding: 1rem; border-radius: 12px;">' + JSON.stringify(data.index, null, 2) + '</pre>';
            html += '</details>';
            resultDiv.innerHTML = html;
        } else {
            resultDiv.innerHTML = '<div style="color: #f00;">❌ Ошибка: ' + escapeHtml(data.message || 'неизвестная ошибка') + '</div>';
            showToast('❌ Ошибка: ' + (data.message || 'неизвестная ошибка'), 'error');
        }
    } catch(e) {
        resultDiv.innerHTML = '<div style="color: #f00;">❌ Ошибка загрузки индекса</div>';
        showToast('❌ Ошибка: ' + e.message, 'error');
    }
}
