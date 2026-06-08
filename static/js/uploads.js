// ==========================================
// Файл: static/js/uploads.js
// Справка: README.md → Веб-морда / Загрузка на YouTube
// Задача: загрузка видео на YouTube через веб-морду
// Комментарий: добавлена проверка элементов, обработка отмены ввода
// Зависит от: ui.js (showToast)
// Вызывается из: main.js (импорт)
// ==========================================

import { showToast } from './ui.js';

export function initUploads() {
    // Проверяем, есть ли элементы для YouTube загрузки
    const statusDiv = document.getElementById('youtube-upload-status');
    if (!statusDiv) {
        console.log('⚠️ YouTube upload элемент не найден, модуль загрузки YouTube пропущен');
        return;
    }
    
    console.log('✅ Модуль загрузки YouTube инициализирован');
}

window.uploadToYouTube = async function() {
    const statusDiv = document.getElementById('youtube-upload-status');
    
    // Получаем URL видео
    let fileUrl = prompt('📹 Введите URL видео для загрузки на YouTube:\n(Поддерживаются: mp4, avi, mov, youtube.com, youtu.be)');
    if (!fileUrl || fileUrl.trim() === '') {
        if (fileUrl === null) showToast('❌ Загрузка отменена', 'info', 2000);
        return;
    }
    fileUrl = fileUrl.trim();
    
    // Получаем название видео
    let title = prompt('📝 Название видео:', 'Видео из Ансамбля Следов 6');
    if (!title || title.trim() === '') {
        if (title === null) showToast('❌ Загрузка отменена', 'info', 2000);
        return;
    }
    title = title.trim();
    if (title.length > 100) {
        showToast('⚠️ Название слишком длинное (макс. 100 символов). Будет обрезано.', 'warning');
        title = title.substring(0, 100);
    }
    
    // Получаем описание видео (необязательно)
    let description = prompt('📄 Описание видео (необязательно):', 'Загружено через Ансамбль Следов 6 | Ритм 0,8 Гц');
    if (description === null) description = '';
    description = description.trim();
    if (description.length > 5000) {
        showToast('⚠️ Описание слишком длинное (макс. 5000 символов). Будет обрезано.', 'warning');
        description = description.substring(0, 5000);
    }
    
    // Блокируем кнопку на время загрузки
    const uploadBtn = document.querySelector('#youtube-upload-status button, button[onclick="uploadToYouTube()"]');
    const originalBtnText = uploadBtn ? uploadBtn.textContent : '';
    if (uploadBtn) {
        uploadBtn.disabled = true;
        uploadBtn.textContent = '⏳ Загрузка...';
    }
    
    if (statusDiv) {
        statusDiv.innerHTML = '<div style="color: var(--accent);">⏳ Начинаем загрузку на YouTube... Это может занять несколько минут.</div>';
    }
    
    try {
        showToast('⏳ Загрузка на YouTube...', 'info', 5000);
        
        const resp = await fetch('/api/youtube_upload/upload', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                file_url: fileUrl,
                title: title,
                description: description
            })
        });
        
        const data = await resp.json();
        
        if (resp.status === 401) {
            if (statusDiv) {
                statusDiv.innerHTML = `
                    <div style="color: var(--warning);">
                        ⚠️ Требуется авторизация в YouTube.<br>
                        <a href="/api/youtube_upload/authorize" target="_blank">🔑 Нажмите для авторизации</a>
                    </div>
                `;
            }
            showToast('⚠️ Требуется авторизация в YouTube. Открываю страницу входа...', 'warning', 5000);
            window.open('/api/youtube_upload/authorize', '_blank');
        } else if (data.status === 'ok') {
            const videoId = data.video_id;
            const videoUrl = `https://youtube.com/watch?v=${videoId}`;
            
            if (statusDiv) {
                statusDiv.innerHTML = `
                    <div style="color: var(--success);">
                        ✅ Видео успешно загружено!<br>
                        <a href="${videoUrl}" target="_blank">📺 Смотреть на YouTube</a>
                    </div>
                `;
            }
            showToast(`✅ Видео "${title}" загружено на YouTube!`, 'success');
        } else {
            const errorMsg = data.error || data.message || 'неизвестная ошибка';
            if (statusDiv) {
                statusDiv.innerHTML = `<div style="color: var(--error);">❌ Ошибка загрузки: ${escapeHtml(errorMsg)}</div>`;
            }
            showToast(`❌ Ошибка загрузки: ${errorMsg}`, 'error');
        }
    } catch (e) {
        console.error('Ошибка при загрузке на YouTube:', e);
        if (statusDiv) {
            statusDiv.innerHTML = `<div style="color: var(--error);">❌ Ошибка сети: ${escapeHtml(e.message)}</div>`;
        }
        showToast(`❌ Ошибка: ${e.message}`, 'error');
    } finally {
        if (uploadBtn) {
            uploadBtn.disabled = false;
            uploadBtn.textContent = originalBtnText || '📤 Загрузить видео';
        }
        // Очищаем статус через 30 секунд, если он об успехе или ошибке
        setTimeout(() => {
            if (statusDiv && (statusDiv.innerHTML.includes('✅') || statusDiv.innerHTML.includes('❌'))) {
                if (!statusDiv.innerHTML.includes('Смотреть на YouTube')) {
                    statusDiv.innerHTML = '';
                }
            }
        }, 30000);
    }
};

// Простой escape для HTML
function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>]/g, function(m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}
