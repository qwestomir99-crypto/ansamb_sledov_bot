// ==========================================
// Файл: static/js/drafts.js
// Справка: README.md → Веб-морда / Черновики
// Задача: интерфейс для управления черновиками в веб-морде
// Комментарий: создание, просмотр, редактирование, публикация черновиков
// Зависит от: ui.js (showToast)
// Вызывается из: main.js (импорт)
// ==========================================

import { showToast } from './ui.js';

export function initDrafts() {
    loadDraftsList();
}

async function loadDraftsList() {
    const container = document.getElementById('drafts-list');
    try {
        const resp = await fetch('/api/drafts/list');
        const drafts = await resp.json();
        if (!drafts.length) {
            container.innerHTML = '<p style="color: var(--text-secondary);">Нет черновиков</p>';
            return;
        }
        container.innerHTML = drafts.map(d => `
            <div class="draft-item">
                <strong>${escapeHtml(d.title)}</strong>
                <p>${escapeHtml(d.content.slice(0, 100))}...</p>
                <button onclick="editDraft(${d.id})">✏️ Редактировать</button>
                <button onclick="publishDraft(${d.id}, 'telegram')">📱 Telegram</button>
                <button onclick="publishDraft(${d.id}, 'vk')">📘 VK</button>
                <button onclick="deleteDraft(${d.id})">🗑️ Удалить</button>
            </div>
        `).join('');
    } catch (e) {
        showToast('Ошибка загрузки черновиков', 'error');
    }
}

window.editDraft = async function(id) {
    const resp = await fetch(`/api/drafts/get/${id}`);
    const draft = await resp.json();
    document.getElementById('draft-title').value = draft.title;
    document.getElementById('draft-content').value = draft.content;
    document.getElementById('draft-id').value = draft.id;
};

window.deleteDraft = async function(id) {
    if (!confirm('Удалить черновик?')) return;
    try {
        await fetch(`/api/drafts/delete/${id}`, { method: 'POST' });
        showToast('Черновик удалён', 'success');
        loadDraftsList();
    } catch (e) {
        showToast('Ошибка удаления', 'error');
    }
};

window.saveDraft = async function() {
    const title = document.getElementById('draft-title').value;
    const content = document.getElementById('draft-content').value;
    const id = document.getElementById('draft-id').value;
    if (!title || !content) {
        showToast('Заполните заголовок и текст', 'warning');
        return;
    }
    try {
        if (id) {
            await fetch(`/api/drafts/update/${id}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, content })
            });
        } else {
            await fetch('/api/drafts/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, content })
            });
        }
        showToast('Черновик сохранён', 'success');
        document.getElementById('draft-title').value = '';
        document.getElementById('draft-content').value = '';
        document.getElementById('draft-id').value = '';
        loadDraftsList();
    } catch (e) {
        showToast('Ошибка сохранения', 'error');
    }
};

window.publishDraft = async function(id, platform) {
    if (!confirm(`Опубликовать черновик в ${platform === 'telegram' ? 'Telegram' : 'VK'}?`)) return;
    try {
        await fetch(`/api/drafts/publish/${id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ platform })
        });
        showToast(`Черновик опубликован в ${platform}`, 'success');
        loadDraftsList();
    } catch (e) {
        showToast('Ошибка публикации', 'error');
    }
};
