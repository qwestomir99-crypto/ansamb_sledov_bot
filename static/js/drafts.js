// ==========================================
// Файл: static/js/drafts.js
// Справка: README.md → Веб-морда / Черновики
// Задача: управление черновиками
// Комментарий: исправлены пути на /api/drafts/...
// Зависит от: ui.js (showToast)
// Вызывается из: main.js (импорт)
// ==========================================

import { showToast } from './ui.js';

export function initDrafts() {
    // Инициализация черновиков при загрузке
    document.addEventListener('DOMContentLoaded', () => {
        loadDrafts();
    });
}

async function loadDrafts() {
    try {
        const resp = await fetch('/api/drafts/list');
        const data = await resp.json();
        const listDiv = document.getElementById('drafts-list');
        if (data.drafts && data.drafts.length) {
            listDiv.innerHTML = data.drafts.map(draft =>
                `<div style="padding: 0.5rem; border-bottom: 1px solid var(--border);">
                    <strong>${escapeHtml(draft.title)}</strong><br>
                    <small>${escapeHtml(draft.content)}</small><br>
                    <button onclick="deleteDraft('${draft.id}')">Удалить</button>
                </div>`
            ).join('');
        } else {
            listDiv.innerHTML = 'Нет черновиков.';
        }
    } catch(e) {
        showToast('Ошибка загрузки черновиков: ' + e.message, 'error');
    }
}

window.saveDraft = async function() {
    const title = document.getElementById('draft-title').value.trim();
    const content = document.getElementById('draft-content').value.trim();
    if (!title || !content) {
        showToast('Заголовок и содержание обязательны', 'error');
        return;
    }
    try {
        const resp = await fetch('/api/drafts/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, content })
        });
        const data = await resp.json();
        if (data.status === 'ok') {
            showToast('Черновик сохранён', 'success');
            document.getElementById('draft-title').value = '';
            document.getElementById('draft-content').value = '';
            loadDrafts();
        } else {
            showToast('Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch(e) {
        showToast('Ошибка: ' + e.message, 'error');
    }
};

window.deleteDraft = async function(id) {
    if (!confirm('Удалить черновик?')) return;
    try {
        const resp = await fetch(`/api/drafts/delete/${id}`, { method: 'DELETE' });
        const data = await resp.json();
        if (data.status === 'ok') {
            loadDrafts();
        } else {
            showToast('Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch(e) {
        showToast('Ошибка: ' + e.message, 'error');
    }
};
