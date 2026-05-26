// ==========================================
// Файл: static/js/main.js
// Веб-морда Ансамбля Следов 6
// ==========================================

// Подключение к Socket.IO
const socket = io();

// ==========================================
// СОКЕТ: ВХОДЯЩИЕ СООБЩЕНИЯ
// ==========================================
socket.on('message_history', function(messages) {
    renderMessages(messages);
});

socket.on('message_updated', function(data) {
    // Добавляем новое сообщение в список
    const messagesDiv = document.getElementById('messages');
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message-item';
    
    // Определяем иконку источника
    let icon = '📨';
    if (data.source === 'telegram') icon = '✈️';
    else if (data.source === 'vk') icon = '📘';
    else if (data.source === 'admin') icon = '👤';
    
    // Форматируем время
    const time = data.timestamp ? new Date(data.timestamp).toLocaleTimeString() : '';
    
    msgDiv.innerHTML = `
        <div class="message-header">
            <span class="message-source">${icon} ${data.source || 'неизвестно'}</span>
            <span class="message-time">${time}</span>
        </div>
        <div class="message-text">${escapeHtml(data.text || '')}</div>
        ${data.chat_id ? `<div class="message-chat-id">ID: ${data.chat_id}</div>` : ''}
        <div class="message-actions">
            ${data.source === 'telegram' || data.source === 'vk' ? 
                `<button onclick="openReply('${data.chat_id}', '${data.source}')">✏️ Ответить</button>` : ''}
            ${data.source === 'vk' ? 
                `<button onclick="openComment('${data.chat_id}')">💬 Комментарий</button>` : ''}
        </div>
    `;
    
    // Если сообщений много, удаляем старые
    while (messagesDiv.children.length > 100) {
        messagesDiv.removeChild(messagesDiv.firstChild);
    }
    
    messagesDiv.appendChild(msgDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
});

// Отрисовка истории сообщений
function renderMessages(messages) {
    const messagesDiv = document.getElementById('messages');
    messagesDiv.innerHTML = '';
    
    if (!messages || messages.length === 0) {
        messagesDiv.innerHTML = '<div style="color: var(--text-secondary); padding: 1rem;">Сообщений пока нет</div>';
        return;
    }
    
    messages.forEach(data => {
        let icon = '📨';
        if (data.source === 'telegram') icon = '✈️';
        else if (data.source === 'vk') icon = '📘';
        else if (data.source === 'admin') icon = '👤';
        
        const time = data.timestamp ? new Date(data.timestamp).toLocaleTimeString() : '';
        
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message-item';
        msgDiv.innerHTML = `
            <div class="message-header">
                <span class="message-source">${icon} ${data.source || 'неизвестно'}</span>
                <span class="message-time">${time}</span>
            </div>
            <div class="message-text">${escapeHtml(data.text || '')}</div>
            ${data.chat_id ? `<div class="message-chat-id">ID: ${data.chat_id}</div>` : ''}
            <div class="message-actions">
                ${data.source === 'telegram' || data.source === 'vk' ? 
                    `<button onclick="openReply('${data.chat_id}', '${data.source}')">✏️ Ответить</button>` : ''}
                ${data.source === 'vk' ? 
                    `<button onclick="openComment('${data.chat_id}')">💬 Комментарий</button>` : ''}
            </div>
        `;
        messagesDiv.appendChild(msgDiv);
    });
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// ==========================================
# ОТВЕТЫ И КОММЕНТАРИИ
// ==========================================
let currentReplyChatId = null;
let currentReplySource = null;

function openReply(chatId, source) {
    currentReplyChatId = chatId;
    currentReplySource = source;
    document.getElementById('reply-area').classList.remove('hidden');
    document.getElementById('reply-text').focus();
    document.getElementById('comment-area').classList.add('hidden');
}

function closeReply() {
    document.getElementById('reply-area').classList.add('hidden');
    currentReplyChatId = null;
    currentReplySource = null;
}

async function sendReply() {
    const text = document.getElementById('reply-text').value.trim();
    if (!text) return;
    
    try {
        const resp = await fetch('/send_reply', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                chat_id: currentReplyChatId,
                text: text,
                source: currentReplySource
            })
        });
        const data = await resp.json();
        if (data.status === 'ok') {
            document.getElementById('reply-text').value = '';
            closeReply();
        } else {
            alert('Ошибка: ' + (data.error || 'неизвестная ошибка'));
        }
    } catch(e) {
        alert('Ошибка отправки: ' + e.message);
    }
}

function openComment(chatId) {
    currentReplyChatId = chatId;
    document.getElementById('comment-area').classList.remove('hidden');
    document.getElementById('comment-text').focus();
    document.getElementById('reply-area').classList.add('hidden');
}

function closeComment() {
    document.getElementById('comment-area').classList.add('hidden');
    currentReplyChatId = null;
}

async function sendComment() {
    const text = document.getElementById('comment-text').value.trim();
    if (!text) return;
    
    try {
        const resp = await fetch('/api/vk/comment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                peer_id: currentReplyChatId,
                text: text
            })
        });
        const data = await resp.json();
        if (data.status === 'ok') {
            document.getElementById('comment-text').value = '';
            closeComment();
        } else {
            alert('Ошибка: ' + (data.error || 'неизвестная ошибка'));
        }
    } catch(e) {
        alert('Ошибка комментария: ' + e.message);
    }
}

// ==========================================
# СОЗДАТЬ ПОСТ
// ==========================================
function createPost(platform) {
    const text = prompt(`Введите текст поста для ${platform === 'telegram' ? 'Telegram' : 'VK'}:`);
    if (!text) return;
    
    fetch('/api/create_post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ platform: platform, text: text })
    })
    .then(resp => resp.json())
    .then(data => {
        if (data.status === 'ok') {
            alert(`✅ Пост опубликован в ${platform === 'telegram' ? 'Telegram' : 'VK'}`);
        } else {
            alert('❌ Ошибка: ' + (data.error || 'неизвестная ошибка'));
        }
    })
    .catch(e => alert('Ошибка: ' + e.message));
}

// ==========================================
# УПРАВЛЕНИЕ БОТОМ (РЕЖИМЫ)
// ==========================================
async function setMode(mode) {
    try {
        const resp = await fetch('/api/set_mode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: mode })
        });
        const data = await resp.json();
        if (data.status === 'ok') {
            document.getElementById('current-mode').textContent = mode;
        } else {
            alert('Ошибка: ' + (data.error || 'неизвестная ошибка'));
        }
    } catch(e) {
        alert('Ошибка: ' + e.message);
    }
}

async function togglePing() {
    try {
        const resp = await fetch('/api/ping_bot');
        const data = await resp.json();
        if (data.status === 'ok') {
            alert('✅ Бот отвечает: ' + data.message);
        } else {
            alert('❌ Бот не отвечает: ' + (data.error || 'неизвестная ошибка'));
        }
    } catch(e) {
        alert('Ошибка: ' + e.message);
    }
}

// ==========================================
# НАСТРОЕНИЕ АГЕНТА
// ==========================================
async function setMood(mood) {
    try {
        const resp = await fetch('/api/set_mood', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mood: mood })
        });
        const data = await resp.json();
        if (data.status === 'ok') {
            document.getElementById('current-mood').textContent = mood;
        } else {
            alert('Ошибка: ' + (data.error || 'неизвестная ошибка'));
        }
    } catch(e) {
        alert('Ошибка: ' + e.message);
    }
}

// ==========================================
# ЦИТАТЫ
// ==========================================
async function addQuote() {
    const text = document.getElementById('new-quote').value.trim();
    if (!text) return;
    
    try {
        const resp = await fetch('/api/add_quote', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });
        const data = await resp.json();
        if (data.status === 'ok') {
            document.getElementById('new-quote').value = '';
            // Перезагружаем список цитат
            const quotesResp = await fetch('/api/get_quotes');
            const quotesData = await quotesResp.json();
            const quotesList = document.getElementById('quotes-list');
            quotesList.innerHTML = '';
            quotesData.quotes.forEach(q => {
                const li = document.createElement('li');
                li.textContent = q;
                quotesList.appendChild(li);
            });
        } else {
            alert('Ошибка: ' + (data.error || 'неизвестная ошибка'));
        }
    } catch(e) {
        alert('Ошибка: ' + e.message);
    }
}

// ==========================================
# ПОСТ В VK
// ==========================================
async function sendPost() {
    const text = document.getElementById('post-text').value.trim();
    if (!text) return;
    
    const statusSpan = document.getElementById('post-status');
    statusSpan.textContent = '⏳ Отправка...';
    
    try {
        const resp = await fetch('/vk_post', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({ text: text })
        });
        const data = await resp.json();
        if (data.status === 'ok') {
            statusSpan.innerHTML = `✅ <a href="${data.url}" target="_blank">Пост опубликован</a>`;
            document.getElementById('post-text').value = '';
        } else {
            statusSpan.textContent = '❌ ' + (data.error || 'Ошибка');
        }
    } catch(e) {
        statusSpan.textContent = '❌ Ошибка: ' + e.message;
    }
}

// ==========================================
# ДЕБАГГЕР
// ==========================================
async function fetchDebugLogs() {
    const reportDiv = document.getElementById('debug-report');
    reportDiv.innerHTML = '⏳ Загрузка логов...';
    
    try {
        const resp = await fetch('/api/debug/logs');
        const data = await resp.json();
        reportDiv.innerHTML = `<pre style="max-height: 300px; overflow-y: auto; background: #f8f8fa; padding: 1rem; border-radius: 12px;">${escapeHtml(JSON.stringify(data, null, 2))}</pre>`;
    } catch(e) {
        reportDiv.innerHTML = '❌ Ошибка загрузки логов: ' + e.message;
    }
}

async function sendDebugReport() {
    const reportDiv = document.getElementById('debug-report');
    reportDiv.innerHTML = '⏳ Отправка отчёта...';
    
    try {
        const resp = await fetch('/api/debug/send_report', { method: 'POST' });
        const data = await resp.json();
        if (data.status === 'ok') {
            reportDiv.innerHTML = '✅ Отчёт отправлен в Telegram';
        } else {
            reportDiv.innerHTML = '❌ Ошибка: ' + (data.error || 'неизвестная ошибка');
        }
    } catch(e) {
        reportDiv.innerHTML = '❌ Ошибка: ' + e.message;
    }
}

async function runAudit() {
    const resultDiv = document.getElementById('audit-result');
    resultDiv.innerHTML = '⏳ Аудит запущен...';
    
    try {
        const resp = await fetch('/api/audit/run', { method: 'POST' });
        const data = await resp.json();
        if (data.status === 'ok') {
            resultDiv.innerHTML = '✅ Аудит завершён. Проверьте README.md';
        } else {
            resultDiv.innerHTML = '❌ Ошибка аудита: ' + (data.error || 'неизвестная ошибка');
        }
    } catch(e) {
        resultDiv.innerHTML = '❌ Ошибка: ' + e.message;
    }
}

async function showAuditStatus() {
    const resultDiv = document.getElementById('audit-result');
    resultDiv.innerHTML = '⏳ Загрузка статуса...';
    
    try {
        const resp = await fetch('/api/audit/status');
        const data = await resp.json();
        if (data.status === 'ok') {
            resultDiv.innerHTML = `<pre style="max-height: 300px; overflow-y: auto; background: #f8f8fa; padding: 1rem; border-radius: 12px;">${escapeHtml(JSON.stringify(data, null, 2))}</pre>`;
        } else {
            resultDiv.innerHTML = '❌ Ошибка: ' + (data.error || 'неизвестная ошибка');
        }
    } catch(e) {
        resultDiv.innerHTML = '❌ Ошибка: ' + e.message;
    }
}

async function showDebugIndex() {
    const resultDiv = document.getElementById('index-result');
    resultDiv.innerHTML = '⏳ Загрузка индекса...';
    
    try {
        const resp = await fetch('/api/debug/index');
        const data = await resp.json();
        if (data.status === 'ok') {
            resultDiv.innerHTML = `<pre style="max-height: 300px; overflow-y: auto; background: #f8f8fa; padding: 1rem; border-radius: 12px;">${escapeHtml(JSON.stringify(data, null, 2))}</pre>`;
        } else {
            resultDiv.innerHTML = '❌ Ошибка: ' + (data.error || 'неизвестная ошибка');
        }
    } catch(e) {
        resultDiv.innerHTML = '❌ Ошибка: ' + e.message;
    }
}

// ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
// ==========================================
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Инициализация: запрос текущего режима и настроения
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const modeResp = await fetch('/api/get_mode');
        const modeData = await modeResp.json();
        if (modeData.status === 'ok') {
            document.getElementById('current-mode').textContent = modeData.mode;
        }
        
        const moodResp = await fetch('/api/get_mood');
        const moodData = await moodResp.json();
        if (moodData.status === 'ok') {
            document.getElementById('current-mood').textContent = moodData.mood;
        }
    } catch(e) {
        console.log('Ошибка загрузки настроек:', e);
    }
});
