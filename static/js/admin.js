// ==========================================
// Файл: static/js/admin.js
// Справка: README.md → Веб-морда / Клиентская логика
// Задача: управление веб-мордой (сообщения, ответы, комментарии, режимы, настроение)
// Комментарий: работает с API из services/app.py
// Зависит от: socket.io
// Вызывается из: templates/admin.html
// ==========================================

// ==========================================
// ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
// ==========================================
let socket = null;
let currentReply = null;       // { chatId, source }
let currentComment = null;     // { postId, platform }

// ==========================================
// ИНИЦИАЛИЗАЦИЯ
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
    connectSocket();
    fetchState();
    fetchMood();
    setInterval(() => {
        fetchState();
        fetchMood();
    }, 60000); // обновляем каждую минуту
});

// ==========================================
// WEBSOCKЕТ (сообщения в реальном времени)
// ==========================================
function connectSocket() {
    socket = io();
    socket.on('message_history', (msgs) => {
        const container = document.getElementById('messages');
        if (!container) return;
        container.innerHTML = '';
        if (msgs && msgs.length) {
            msgs.forEach(msg => appendMessage(msg));
        } else {
            container.innerHTML = '<div style="color: var(--text-secondary);">Нет сообщений</div>';
        }
    });
    socket.on('message_updated', (msg) => {
        if (msg) appendMessage(msg);
    });
    socket.on('connect', () => console.log('Socket connected'));
    socket.on('disconnect', () => console.log('Socket disconnected'));
}

// ==========================================
// ОТОБРАЖЕНИЕ СООБЩЕНИЯ
// ==========================================
function appendMessage(msg) {
    const container = document.getElementById('messages');
    if (!container) return;
    
    if (container.innerHTML === '<div style="color: var(--text-secondary);">Загрузка...</div>' || 
        container.innerHTML === '<div style="color: var(--text-secondary);">Нет сообщений</div>') {
        container.innerHTML = '';
    }
    
    const div = document.createElement('div');
    let sourceClass = '';
    if (msg.source === 'telegram') sourceClass = 'message-telegram';
    else if (msg.source === 'vk') sourceClass = 'message-vk';
    div.className = `message ${sourceClass} ${msg.own ? 'own' : ''}`;
    
    const sourceName = msg.source === 'telegram' ? '📱 Telegram' : (msg.source === 'admin' ? '🤖 Админ' : '📘 VK');
    const sender = msg.sender || msg.username || 'unknown';
    const time = msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString() : new Date().toLocaleTimeString();
    
    const chatId = msg.chat_id || msg.user_id || '';
    const postId = msg.post_id || '';
    
    div.innerHTML = `
        <div><strong>${escapeHtml(sourceName)} | ${escapeHtml(sender)}</strong></div>
        <div>${escapeHtml(msg.text || '')}</div>
        <small>${escapeHtml(time)}</small>
        <div class="message-actions" style="margin-top: 8px;">
            <button onclick="openReply('${escapeHtml(String(chatId))}', '${msg.source}', '${escapeHtml(sender)}')">💬 Ответить</button>
            <button onclick="openComment('${escapeHtml(String(postId || chatId))}', '${msg.source}')">✏️ Комментировать</button>
        </div>
    `;
    container.prepend(div);
}

// ==========================================
// ОТВЕТ НА СООБЩЕНИЕ
// ==========================================
function openReply(chatId, source, sender) {
    currentReply = { chatId: chatId, source: source };
    const replyArea = document.getElementById('reply-area');
    const replyText = document.getElementById('reply-text');
    if (replyArea) replyArea.classList.remove('hidden');
    if (replyText) replyText.placeholder = `Ответ для ${sender}...`;
    if (replyText) replyText.focus();
}

function closeReply() {
    currentReply = null;
    const replyArea = document.getElementById('reply-area');
    const replyText = document.getElementById('reply-text');
    if (replyArea) replyArea.classList.add('hidden');
    if (replyText) replyText.value = '';
}

async function sendReply() {
    if (!currentReply) return;
    const text = document.getElementById('reply-text')?.value.trim();
    if (!text) return;
    
    const response = await fetch('/send_reply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            chat_id: currentReply.chatId,
            text: text,
            source: currentReply.source
        })
    });
    const data = await response.json();
    if (data.status === 'ok') {
        appendMessage({
            source: 'admin',
            text: text,
            timestamp: new Date().toISOString(),
            own: true
        });
        closeReply();
    } else {
        alert('Ошибка: ' + (data.error || 'неизвестная'));
    }
}

// ==========================================
// КОММЕНТАРИЙ К ПОСТУ
// ==========================================
function openComment(postId, platform) {
    currentComment = { postId: postId, platform: platform };
    const commentArea = document.getElementById('comment-area');
    const commentText = document.getElementById('comment-text');
    if (commentArea) commentArea.classList.remove('hidden');
    if (commentText) commentText.placeholder = `Комментарий к посту ${postId}...`;
    if (commentText) commentText.focus();
}

function closeComment() {
    currentComment = null;
    const commentArea = document.getElementById('comment-area');
    const commentText = document.getElementById('comment-text');
    if (commentArea) commentArea.classList.add('hidden');
    if (commentText) commentText.value = '';
}

async function sendComment() {
    if (!currentComment) return;
    const text = document.getElementById('comment-text')?.value.trim();
    if (!text) return;
    
    let url = '/api/comment';
    if (currentComment.platform === 'vk') {
        url = '/api/vk/comment';
    } else if (currentComment.platform === 'telegram') {
        url = '/api/tg/comment';
    }
    
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            post_id: currentComment.postId,
            text: text,
            chat_id: currentComment.postId
        })
    });
    const data = await response.json();
    if (data.status === 'ok') {
        appendMessage({
            source: 'admin',
            text: `💬 Комментарий: ${text}`,
            timestamp: new Date().toISOString(),
            own: true
        });
        closeComment();
    } else {
        alert('Ошибка: ' + (data.error || 'неизвестная'));
    }
}

// ==========================================
// НОВЫЙ ПОСТ / СООБЩЕНИЕ
// ==========================================
async function createPost(platform) {
    const text = prompt(`Введите текст для публикации в ${platform === 'vk' ? 'VK' : 'Telegram'}:`);
    if (!text) return;
    
    const response = await fetch('/api/create_post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ platform: platform, text: text })
    });
    const data = await response.json();
    if (data.status === 'ok') {
        alert('✅ Опубликовано!');
        if (data.url) {
            appendMessage({
                source: 'admin',
                text: `📢 Пост: ${text}<br><a href="${data.url}" target="_blank">Ссылка</a>`,
                timestamp: new Date().toISOString(),
                own: true
            });
        }
    } else {
        alert('❌ Ошибка: ' + (data.error || 'неизвестная'));
    }
}

// ==========================================
// УПРАВЛЕНИЕ РЕЖИМАМИ
// ==========================================
async function setMode(mode) {
    const response = await fetch('/api/set_mode', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: mode })
    });
    const data = await response.json();
    if (data.status === 'ok') {
        const modeSpan = document.getElementById('current-mode');
        if (modeSpan) modeSpan.innerText = mode;
    }
}

async function fetchState() {
    try {
        const response = await fetch('/api/state');
        const data = await response.json();
        if (data.mode) {
            const modeSpan = document.getElementById('current-mode');
            if (modeSpan) modeSpan.innerText = data.mode;
        }
        if (data.quotes && data.quotes.length) {
            const quotesList = document.getElementById('quotes-list');
            if (quotesList) {
                quotesList.innerHTML = data.quotes.map(q => `<li>${escapeHtml(q)}</li>`).join('');
            }
        }
    } catch(e) {
        console.error('Ошибка загрузки состояния:', e);
    }
}

// ==========================================
// НАСТРОЕНИЕ
// ==========================================
async function setMood(mood) {
    const response = await fetch('/api/set_mood', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mood: mood })
    });
    const data = await response.json();
    if (data.status === 'ok') {
        const moodNames = { 'artist': 'Художник', 'admin': 'Администратор', 'poet': 'Поэт', 'engineer': 'Инженер' };
        const moodSpan = document.getElementById('current-mood');
        if (moodSpan) moodSpan.innerText = moodNames[mood] || mood;
    }
}

async function fetchMood() {
    try {
        const response = await fetch('/api/get_mood');
        const data = await response.json();
        if (data.mood) {
            const moodNames = { 'artist': 'Художник', 'admin': 'Администратор', 'poet': 'Поэт', 'engineer': 'Инженер' };
            const moodSpan = document.getElementById('current-mood');
            if (moodSpan) moodSpan.innerText = moodNames[data.mood] || data.mood;
        }
    } catch(e) {
        console.error('Ошибка загрузки настроения:', e);
    }
}

// ==========================================
// ПИНГ
// ==========================================
async function togglePing() {
    const response = await fetch('/api/toggle_ping', { method: 'POST' });
    const data = await response.json();
    alert(data.message || 'Пинг переключён');
}

// ==========================================
// ЦИТАТЫ
// ==========================================
async function addQuote() {
    const quote = document.getElementById('new-quote')?.value.trim();
    if (!quote) return alert("Введите текст цитаты");
    const response = await fetch('/api/add_quote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quote: quote })
    });
    const data = await response.json();
    if (data.status === 'ok') {
        const newQuoteInput = document.getElementById('new-quote');
        if (newQuoteInput) newQuoteInput.value = '';
        fetchState();
    } else {
        alert('Ошибка: ' + (data.error || 'неизвестная'));
    }
}

// ==========================================
// ПОСТ В VK (прямая отправка)
// ==========================================
async function sendPost() {
    const text = document.getElementById('post-text')?.value.trim();
    if (!text) return alert("Введите текст поста");
    const statusSpan = document.getElementById('post-status');
    if (statusSpan) statusSpan.innerText = '⏳ Отправка...';
    const response = await fetch('/vk_post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'text=' + encodeURIComponent(text)
    });
    const data = await response.json();
    if (data.status === 'ok') {
        if (statusSpan) statusSpan.innerHTML = `✅ Опубликовано! <a href="${data.url}" target="_blank">Ссылка</a>`;
        const postText = document.getElementById('post-text');
        if (postText) postText.value = '';
    } else {
        if (statusSpan) statusSpan.innerText = '❌ ' + (data.error || 'Ошибка');
    }
    setTimeout(() => {
        if (statusSpan) statusSpan.innerText = '';
    }, 5000);
}

// ==========================================
// ДЕБАГГЕР
// ==========================================
async function fetchDebugLogs() {
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
        container.innerHTML = '<div style="color: #f00;">❌ Ошибка загрузки логов</div>';
    }
}

async function sendDebugReport() {
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
        container.innerHTML = '<div style="color: #f00;">❌ Ошибка отправки</div>';
    }
    setTimeout(() => {
        if (container.innerHTML.includes('✅') || container.innerHTML.includes('❌')) {
            container.innerHTML = '';
        }
    }, 5000);
}

// ==========================================
// ВСПОМОГАТЕЛЬНЫЕ
// ==========================================
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
                                                      }
