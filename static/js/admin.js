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
    setInterval(fetchState, 60000); // обновляем цитаты каждую минуту
});

// ==========================================
// WEBSOCKЕТ (сообщения в реальном времени)
// ==========================================
function connectSocket() {
    socket = io();
    socket.on('message_history', (msgs) => {
        const container = document.getElementById('messages');
        container.innerHTML = '';
        msgs.forEach(msg => appendMessage(msg));
        if (msgs.length === 0) {
            container.innerHTML = '<div style="color: var(--text-secondary);">Нет сообщений</div>';
        }
    });
    socket.on('message_updated', (msg) => { appendMessage(msg); });
    socket.on('connect', () => console.log('Socket connected'));
}

// ==========================================
// ОТОБРАЖЕНИЕ СООБЩЕНИЯ
// ==========================================
function appendMessage(msg) {
    const container = document.getElementById('messages');
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
    
    let postId = msg.post_id || msg.chat_id || msg.user_id || '';
    
    div.innerHTML = `
        <div><strong>${sourceName} | ${escapeHtml(sender)}</strong></div>
        <div>${escapeHtml(msg.text || '')}</div>
        <small>${time}</small>
        <div class="message-actions" style="margin-top: 8px;">
            <button onclick="openReply('${postId}', '${msg.source}', '${escapeHtml(sender)}')">💬 Ответить</button>
            <button onclick="openComment('${postId}', '${msg.source}')">✏️ Комментировать</button>
        </div>
    `;
    container.prepend(div);
}

// ==========================================
// ОТВЕТ НА СООБЩЕНИЕ
// ==========================================
function openReply(chatId, source, sender) {
    currentReply = { chatId: chatId, source: source };
    document.getElementById('reply-area').classList.remove('hidden');
    document.getElementById('reply-text').placeholder = `Ответ для ${sender}...`;
    document.getElementById('reply-text').focus();
}

function closeReply() {
    currentReply = null;
    document.getElementById('reply-area').classList.add('hidden');
    document.getElementById('reply-text').value = '';
}

async function sendReply() {
    if (!currentReply) return;
    const text = document.getElementById('reply-text').value.trim();
    if (!text) return;
    
    const response = await fetch('/send_reply', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
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
        alert('Ошибка: ' + data.error);
    }
}

// ==========================================
// КОММЕНТАРИЙ К ПОСТУ
// ==========================================
function openComment(postId, platform) {
    currentComment = { postId: postId, platform: platform };
    document.getElementById('comment-area').classList.remove('hidden');
    document.getElementById('comment-text').placeholder = `Комментарий к посту ${postId}...`;
    document.getElementById('comment-text').focus();
}

function closeComment() {
    currentComment = null;
    document.getElementById('comment-area').classList.add('hidden');
    document.getElementById('comment-text').value = '';
}

async function sendComment() {
    if (!currentComment) return;
    const text = document.getElementById('comment-text').value.trim();
    if (!text) return;
    
    let url = '/api/comment';
    const response = await fetch(url, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            post_id: currentComment.postId,
            text: text,
            platform: currentComment.platform
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
        alert('Ошибка: ' + data.error);
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
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ platform: platform, text: text })
    });
    const data = await response.json();
    if (data.status === 'ok') {
        alert('✅ Опубликовано!');
    } else {
        alert('❌ Ошибка: ' + data.error);
    }
}

// ==========================================
// УПРАВЛЕНИЕ РЕЖИМАМИ
// ==========================================
async function setMode(mode) {
    const response = await fetch('/api/set_mode', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ mode: mode })
    });
    const data = await response.json();
    if (data.status === 'ok') {
        document.getElementById('current-mode').innerText = mode;
    }
}

async function fetchState() {
    const response = await fetch('/api/state');
    const data = await response.json();
    if (data.mode) document.getElementById('current-mode').innerText = data.mode;
    if (data.quotes) {
        const list = document.getElementById('quotes-list');
        list.innerHTML = data.quotes.map(q => `<li>${escapeHtml(q)}</li>`).join('');
    }
}

// ==========================================
// НАСТРОЕНИЕ
// ==========================================
async function setMood(mood) {
    const response = await fetch('/api/set_mood', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ mood: mood })
    });
    const data = await response.json();
    if (data.status === 'ok') {
        const moodNames = { 'artist': 'Художник', 'admin': 'Администратор', 'poet': 'Поэт', 'engineer': 'Инженер' };
        document.getElementById('current-mood').innerText = moodNames[mood] || mood;
    }
}

async function fetchMood() {
    const response = await fetch('/api/get_mood');
    const data = await response.json();
    if (data.mood) {
        const moodNames = { 'artist': 'Художник', 'admin': 'Администратор', 'poet': 'Поэт', 'engineer': 'Инженер' };
        document.getElementById('current-mood').innerText = moodNames[data.mood] || data.mood;
    }
}

// ==========================================
// ПИНГ
// ==========================================
async function togglePing() {
    const response = await fetch('/api/toggle_ping', { method: 'POST' });
    const data = await response.json();
    alert(data.message);
}

// ==========================================
// ЦИТАТЫ
// ==========================================
async function addQuote() {
    const quote = document.getElementById('new-quote').value.trim();
    if (!quote) return alert("Введите текст цитаты");
    const response = await fetch('/api/add_quote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quote: quote })
    });
    const data = await response.json();
    if (data.status === 'ok') {
        document.getElementById('new-quote').value = '';
        fetchState();
    } else {
        alert('Ошибка: ' + data.error);
    }
}

// ==========================================
// ПОСТ В VK
// ==========================================
async function sendPost() {
    const text = document.getElementById('post-text').value.trim();
    if (!text) return alert("Введите текст поста");
    const statusSpan = document.getElementById('post-status');
    statusSpan.innerText = '⏳ Отправка...';
    const response = await fetch('/vk_post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'text=' + encodeURIComponent(text)
    });
    const data = await response.json();
    if (data.status === 'ok') {
        statusSpan.innerHTML = `✅ Опубликовано! <a href="${data.url}" target="_blank">Ссылка</a>`;
        document.getElementById('post-text').value = '';
    } else {
        statusSpan.innerText = '❌ ' + data.error;
    }
    setTimeout(() => { statusSpan.innerText = ''; }, 5000);
}

// ==========================================
// ДЕБАГГЕР
// ==========================================
async function fetchDebugLogs() {
    const container = document.getElementById('debug-report');
    container.innerHTML = '<div style="color: var(--accent);">⏳ Загрузка...</div>';
    const response = await fetch('/api/debug/logs?limit=100');
    const data = await response.json();
    if (data.logs && data.logs.length) {
        let html = '<details><summary>🐛 Логи (' + data.logs.length + ')</summary><pre>';
        data.logs.forEach(log => { html += `[${log.level}] ${log.module} | ${log.message}\n`; });
        html += '</pre></details>';
        container.innerHTML = html;
    } else {
        container.innerHTML = '<div style="color: var(--text-secondary);">Логов нет</div>';
    }
}

async function sendDebugReport() {
    const container = document.getElementById('debug-report');
    container.innerHTML = '<div style="color: var(--accent);">⏳ Отправка...</div>';
    const response = await fetch('/api/debug/send', { method: 'POST' });
    const data = await response.json();
    if (data.status === 'ok') {
        container.innerHTML = '<div style="color: var(--success);">✅ Отчёт отправлен в Telegram</div>';
    } else {
        container.innerHTML = '<div style="color: #f00;">❌ Ошибка: ' + data.message + '</div>';
    }
    setTimeout(() => { container.innerHTML = ''; }, 5000);
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
