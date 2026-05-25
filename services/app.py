@app.route('/')
@login_required
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Ансамбль Следов 6 — веб-морда</title>
        <!-- Favicon: частота сети 0,8 Гц -->
        <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext x='10' y='65' font-family='monospace' font-size='50' fill='%2300ffcc'%3E0.8%3C/text%3E%3C/svg%3E">
        <script src="https://cdn.socket.io/4.6.0/socket.io.min.js"></script>
        <style>
            /* Стили (можно оставить свои или использовать макросы) */
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { background: #0a0a0a; color: #00ffcc; font-family: 'Courier New', monospace; padding: 2rem; }
            .container { max-width: 1100px; margin: 0 auto; }
            .card { background: #111; border-left: 3px solid #00ffcc; padding: 1rem; margin: 1rem 0; border-radius: 8px; }
            button, input, textarea, select { background: #222; color: #00ffcc; border: 1px solid #00ffcc; padding: 6px 12px; border-radius: 4px; font-family: inherit; }
            button:hover { background: #00ffcc; color: #000; cursor: pointer; }
            a { color: #00ffcc; }
            .message { border-bottom: 1px solid #333; padding: 8px; margin: 5px 0; }
            .message.own { background: #1a3a3a; border-left: 2px solid #00ffcc; }
            .message-telegram { border-left: 2px solid #26a5e4; }
            .message-vk { border-left: 2px solid #4c75a3; }
            .messages { max-height: 400px; overflow-y: auto; margin-bottom: 20px; }
            .source-tag { font-size: 0.7rem; margin-left: 8px; padding: 2px 6px; border-radius: 4px; }
            .source-telegram { background: #26a5e4; color: #000; }
            .source-vk { background: #4c75a3; color: #fff; }
            .hidden { display: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h1>🔥 Ансамбль Следов 6</h1>
                <form method="post" action="/logout">
                    <button type="submit" style="background: transparent; border: 1px solid #00ffcc;">🚪 Выйти</button>
                </form>
            </div>
            <p>Ритм 0,8 Гц. Управление ботом из браузера. Время: {{ time }}</p>
            <p>
                <a href="/logs/admin">📋 admin.log</a> |
                <a href="/logs/error">❌ error.log</a> |
                <a href="/youtube">🎬 YouTube без VPN</a>
            </p>
            
            <div class="card">
                <h2>📨 Входящие сообщения (VK + Telegram)</h2>
                <div id="messages" class="messages">
                    <div style="color: #666;">Загрузка...</div>
                </div>
                <div id="reply-area" class="hidden" style="margin-top: 1rem;">
                    <textarea id="reply-text" rows="2" cols="50" placeholder="Ваш ответ..." style="width: 100%; margin-bottom: 0.5rem;"></textarea>
                    <button onclick="sendReply()">📤 Отправить ответ</button>
                    <button onclick="closeReply()" style="background: transparent; border: 1px solid #00ffcc;">❌ Отмена</button>
                </div>
            </div>
            
            <div class="card">
                <h2>🎬 Пост в VK (текст)</h2>
                <textarea id="post-text" rows="3" cols="50" placeholder="Текст поста..."></textarea><br>
                <button onclick="sendPost()">Отправить</button>
                <span id="post-status"></span>
            </div>
            
            <div class="card">
                <h2>📜 Цитаты (последние 10)</h2>
                <ul id="quotes-list">
                    {% for q in quotes %}<li>{{ q[:100] }}</li>{% endfor %}
                </ul>
            </div>
        </div>
        
        <script>
            let socket = null;
            let currentReply = null;
            
            document.addEventListener("DOMContentLoaded", () => {
                connectSocket();
                fetchState();
            });
            
            function connectSocket() {
                socket = io();
                socket.on('message_history', (msgs) => {
                    const container = document.getElementById('messages');
                    container.innerHTML = '';
                    msgs.forEach(msg => appendMessage(msg));
                    if (msgs.length === 0) {
                        container.innerHTML = '<div style="color: #666;">Нет сообщений</div>';
                    }
                });
                socket.on('message_updated', (msg) => {
                    appendMessage(msg);
                });
                socket.on('connect', () => console.log('Socket connected'));
            }
            
            function appendMessage(msg) {
                const container = document.getElementById('messages');
                if (container.innerHTML === '<div style="color: #666;">Загрузка...</div>' || 
                    container.innerHTML === '<div style="color: #666;">Нет сообщений</div>') {
                    container.innerHTML = '';
                }
                const div = document.createElement('div');
                const sourceClass = msg.source === 'telegram' ? 'message-telegram' : (msg.source === 'admin' ? '' : 'message-vk');
                div.className = `message ${sourceClass} ${msg.own ? 'own' : ''}`;
                const sourceName = msg.source === 'telegram' ? '📱 Telegram' : (msg.source === 'admin' ? '🤖 Админ' : '📘 VK');
                const sender = msg.sender || msg.username || 'unknown';
                const time = msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString() : new Date().toLocaleTimeString();
                div.innerHTML = `
                    <div>
                        <strong>${sourceName} | ${escapeHtml(sender)}</strong>
                    </div>
                    <div>${escapeHtml(msg.text || '')}</div>
                    <small>${time}</small>
                `;
                if (!msg.own && msg.source !== 'admin') {
                    const chatId = msg.chat_id || msg.user_id;
                    if (chatId) {
                        div.innerHTML += `<br><button onclick="openReply('${chatId}', '${msg.source}', '${escapeHtml(sender)}')" style="font-size:0.7rem; padding: 3px 6px;">Ответить</button>`;
                    }
                }
                container.prepend(div);
            }
            
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
            
            async function sendPost() {
                const text = document.getElementById('post-text').value.trim();
                if (!text) return;
                const statusSpan = document.getElementById('post-status');
                statusSpan.innerText = '⏳ Отправка...';
                const response = await fetch('/vk_post', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
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
            
            async function fetchState() {
                const response = await fetch('/api/state');
                const data = await response.json();
                if (data.quotes) {
                    const list = document.getElementById('quotes-list');
                    list.innerHTML = data.quotes.map(q => `<li>${escapeHtml(q)}</li>`).join('');
                }
            }
            
            function escapeHtml(text) {
                if (!text) return '';
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
        </script>
    </body>
    </html>
    ''', time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), quotes=get_quotes())
