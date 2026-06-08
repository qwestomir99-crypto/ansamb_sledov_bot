// ==========================================
// Файл: static/js/drafts.js
// Справка: README.md → Веб-морда / Черновики
// Задача: управление черновиками
// Комментарий: исправлены пути на /api/drafts/..., добавлен импорт escapeHtml
// Зависит от: ui.js (showToast), helpers.js (escapeHtml)
// Вызывается из: main.js (импорт)
// ==========================================

import { showToast } from './ui.js';
import { escapeHtml } from './helpers.js';

export function initDrafts() {
    // Проверяем, есть ли элементы черновиков на странице
    const draftsList = document.getElementById('drafts-list');
    const draftTitle = document.getElementById('draft-title');
    const draftContent = document.getElementById('draft-content');
    
    if (!draftsList) {
        // Черновики не используются на этой странице — просто выходим
        return;
    }
    
    // Загружаем черновики при инициализации
    loadDrafts();
}

async function loadDrafts() {
    const listDiv = document.getElementById('drafts-list');
    if (!listDiv) return;
    
    try {
        const resp = await fetch('/api/drafts/list');
        const data = await resp.json();
        
        if (data.drafts && data.drafts.length) {
            let html = '';
            for (const draft of data.drafts) {
                html += `
                    <div style="padding: 0.5rem; border-bottom: 1px solid var(--border); margin-bottom: 0.5rem;">
                        <strong>${escapeHtml(draft.title)}</strong><br>
                        <small>${escapeHtml(draft.content.substring(0, 100))}${draft.content.length > 100 ? '...' : ''}</small><br>
                        <button onclick="window.deleteDraft('${draft.id}')" style="margin-top: 0.5rem;">🗑️ Удалить</button>
                    </div>
                `;
            }
            listDiv.innerHTML = html;
        } else {
            listDiv.innerHTML = '<div style="color: var(--text-secondary);">Нет черновиков. Создайте первый.</div>';
        }
    } catch(e) {
        console.error('Ошибка загрузки черновиков:', e);
        listDiv.innerHTML = '<div style="color: #f00;">❌ Ошибка загрузки черновиков</div>';
        showToast('Ошибка загрузки черновиков: ' + e.message, 'error');
    }
}

window.saveDraft = async function() {
    const titleInput = document.getElementById('draft-title');
    const contentInput = document.getElementById('draft-content');
    
    if (!titleInput || !contentInput) {
        showToast('Элементы черновиков не найдены на странице', 'error');
        return;
    }
    
    const title = titleInput.value.trim();
    const content = contentInput.value.trim();
    
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
            showToast('✅ Черновик сохранён', 'success');
            titleInput.value = '';
            contentInput.value = '';
            loadDrafts();
        } else {
            showToast('❌ Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch(e) {
        showToast('❌ Ошибка: ' + e.message, 'error');
    }
};

window.deleteDraft = async function(id) {
    if (!id) return;
    if (!confirm('Удалить черновик?')) return;
    
    try {
        const resp = await fetch(`/api/drafts/delete/${id}`, { method: 'DELETE' });
        const data = await resp.json();
        
        if (data.status === 'ok') {
            showToast('✅ Черновик удалён', 'success');
            loadDrafts();
        } else {
            showToast('❌ Ошибка: ' + (data.error || 'неизвестная ошибка'), 'error');
        }
    } catch(e) {
        showToast('❌ Ошибка: ' + e.message, 'error');
    }
};
