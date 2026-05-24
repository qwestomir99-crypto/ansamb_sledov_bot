# ==========================================
# Файл: app.py
# Справка: README.md → Веб-морда
# Задача: веб-интерфейс для управления ботом, постинга в VK и ответов на сообщения
# Комментарий: работает независимо от bot.py, использует общие файлы и переменные окружения
# Зависит от: flask, flask-socketio, vk_api, python-dotenv
# Вызывается из: Render (web service)
# ==========================================

import os
import datetime
from threading import Thread
from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO
from dotenv import load_dotenv

# Автоматически ищет .env в корне проекта, если запуск идет не из Docker
load_dotenv()

# Попытка импорта VK API для отказоустойчивости панели
try:
    import vk_api
    from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
    VK_AVAILABLE = True
except ImportError:
    VK_AVAILABLE = False

# =====================================================================
# НАСТРОЙКИ (Переменные окружения контейнера)
# =====================================================================
VK_TOKEN = os.environ.get("VK_TOKEN")
try:
    VK_GROUP_ID = int(os.environ.get("VK_GROUP_ID", 0))
except (ValueError, TypeError):
    VK_GROUP_ID = 0

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY", "secret_traces_key_6")
socketio = SocketIO(app, async_mode='gevent', cors_allowed_origins="*")

# Внутреннее состояние бота
bot_state = {
    "mode": "день",
    "quotes": [
        "Ритм задает движение, следы оставляют историю.",
        "Тестовая цитата ансамбля №6."
    ]
}

# Глобальный объект для работы с методами VK API
vk = None

# Встроенный HTML-интерфейс (веб-морда)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Ансамбль Следов 6 — веб-морда</title>
    <!-- Клиент Socket.io для связи с Flask-SocketIO на сервере -->
    <script src="https://socket.io"></script>
    <style>
        * { box-sizing: border-box; }
        body {
            background: #0a0a0a;
            color: #00ffcc;
            font-family: 'Courier New', monospace;
            padding: 1rem;
            margin: 0;
        }
        .container { max-width: 900px; margin: 0 auto; }
        .card {
            background: #111;
            border-left: 3px solid #00ffcc;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 8px;
        }
        button, input, textarea, select {
            background: #222;
            color: #00ffcc;
            border: 1px solid #00ffcc;
            padding: 6px 12px;
            border-radius: 4px;
            font-family: inherit;
        }
        button:hover { background: #00ffcc; color: #000; cursor: pointer; }
        hr { border-color: #00ffcc33; }
        a { color: #00ffcc; }
        .message-item { border-bottom: 1px solid #333; padding: 8px; margin-bottom: 5px; }
        .message-item.own { background-color: #1a3a3a; border-left: 2px solid #00ffcc; }
        #vk-messages { max-height: 400px; overflow-y: auto; border: 1px solid #00ffcc33; padding: 10px; margin-bottom: 10px; }
        .status-ok { color: #0f0; }
        .status-error { color: #f00; }
        .hidden { display: none; }
        .inline { display: inline-block; margin-left: 10px; }
    </style>
</head>
<body>
<div class="container">
    <h1>🔥 Ансамбль Следов 6</h1>
    <p>Ритм 0,8 Гц. Управление ботом из браузера. Время: {{ time }}</p>
    <p>
        <a href="/logs/admin" target="_blank">📋 admin.log</a> |
        <a href="/logs/error" target="_blank">❌ error.log</a>
    </p>

    <!-- Блок управления режимом -->
    <div class="card">
        <h2>🤖 Текущий режим: <strong id="current-mode">{{ mode }}</strong></h2>
        <form method="post" action="/set_mode" onsubmit="return false">
            <select name="mode" id="mode-select">
                <option value="утро">🌅 Утро</option>
                <option value="день">☀️ День</option>
                <option value="вечер">🌙 Вечер</option>
                <option value="ночь">🌌 Ночь</option>
            </select>
            <button type="button" onclick="setMode()">Сменить режим</button>
        </form>
    </div>

    <!-- Блок добавления цитаты -->
    <div class="card">
        <h2>📜 Добавить цитату</h2>
        <form method="post" action="/add_quote" onsubmit="return false">
            <textarea name="quote" id="quote-text" rows="2" cols="50" placeholder="Текст цитаты..."></textarea><br>
            <button type="button" onclick="addQuote()">➕ Добавить</button>
        </form>
        <details>
            <summary>📖 Последние цитаты (10)</summary>
            <ul id="quotes-list">
                {% for q in quotes %}
                    <li>{{ q[:100] }}</li>
                {% else %}
                    <li>Нет цитат</li>
                {% endfor %}
            </ul>
        </details>
    </div>

    <!-- Блок поста в VK (текст) -->
    <div class="card">
        <h2>🎬 Пост в VK (текст)</h2>
        <form method="post" action="/vk_post" onsubmit="return false">
            <textarea name="text" id="vk-post-text" rows="3" cols="50" placeholder="Текст поста..."></textarea><br>
            <button type="button" onclick="sendVkPost()">📤 Отправить</button>
        </form>
        <div id="vk-post-status" class="inline"></div>
    </div>

    <!-- Блок сообщений из VK -->
    <div class="card">
        <h2>💬 Входящие сообщения (VK)</h2>
        <div id="vk-messages">
            <div style="color: #666;">Сообщения будут появляться здесь...</div>
        </div>
        <div id="vk-reply-area" class="hidden">
            <textarea id="vk-reply-text" rows="2" cols="50" placeholder="Ваш ответ..."></textarea>
            <button onclick="sendVkReply()">📤 Отправить ответ</button>
            <button onclick="closeVkReply()">❌ Отмена</button>
        </div>
    </div>
</div>

<script>
    let currentReplyPeer = null;
    let ws = null;

    // Автоматический старт при загрузке страницы в мобильном браузере
    document.addEventListener("DOMContentLoaded", () => {
        connectWebSocket();
        fetchState();
    });

    // API: Переключение режима работы
    async function setMode() {
        const mode = document.getElementById("mode-select").value;
        try {
            const response = await fetch('/set_mode', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ mode })
            });
            const data = await response.json();
            document.getElementById("current-mode").innerText = data.mode;
        } catch (e) { console.error("Ошибка смены режима:", e); }
    }

    // API: Добавление цитаты в список
    async function addQuote() {
        const quoteText = document.getElementById("quote-text").value;
        if (!quoteText.trim()) return alert("Текст цитаты пуст!");
        try {
            const response = await fetch('/add_quote', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ quote: quoteText })
            });
            const data = await response.json();
            document.getElementById("quote-text").value = '';
            if (data.quotes) updateQuotesList(data.quotes);
        } catch (e) { console.error("Ошибка добавления цитаты:", e); }
    }

    // API: Публикация записи на стену сообщества (ОБНОВЛЕНО: подробный ответ)
    async function sendVkPost() {
        const text = document.getElementById("vk-post-text").value;
        if (!text.trim()) {
            alert("Текст поста не может быть пустым");
            return;
        }
        const statusDiv = document.getElementById("vk-post-status");
        statusDiv.innerText = "⏳ Отправка...";
        try {
            const response = await fetch('/vk_post', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ text })
            });
            const data = await response.json();
            if (data.status === "ok") {
                statusDiv.innerHTML = `✅ Опубликовано! <a href="${data.url}" target="_blank">Ссылка на пост</a>`;
                document.getElementById("vk-post-text").value = '';
            } else {
                statusDiv.innerText = `❌ Ошибка: ${data.error}`;
            }
        } catch (e) {
            statusDiv.innerText = "❌ Ошибка сети";
        }
    }

    // Рендеринг обновленного списка цитат
    function updateQuotesList(quotes) {
        const list = document.getElementById("quotes-list");
        list.innerHTML = quotes.map(q => {
            const truncated = q.length > 100 ? q.substring(0, 100) + '...' : q;
            return `<li>${truncated}</li>`;
        }).join('') || '<li>Нет цитат</li>';
    }

    // Синхронизация интерфейса с текущим статусом бэкенда
    async function fetchState() {
        try {
            const response = await fetch('/api/state');
            const data = await response.json();
            document.getElementById("current-mode").innerText = data.mode;
            if (data.quotes) updateQuotesList(data.quotes);
        } catch(e) { console.error("Ошибка получения состояния:", e); }
    }

    // Инициализация WebSocket канала через библиотеку socket.io
    function connectWebSocket() {
        ws = io('/ws/messages');
        ws.on('message', (data) => { appendMessage(data); });
    }

    // Добавление нового сообщения в ленту
    function appendMessage(msg) {
        const container = document.getElementById("vk-messages");
        if (container.querySelector("div[style*='color: #666']")) container.innerHTML = '';

        const div = document.createElement('div');
        div.className = `message-item ${msg.own ? 'own' : ''}`;
        div.innerHTML = `<strong>${msg.sender}:</strong> ${msg.text} <br><small>${msg.time}</small>`;
        
        if (!msg.own) {
            div.innerHTML += `<br><button onclick="openVkReply(${msg.peer_id}, '${msg.sender}')" style="font-size:0.7rem; padding: 3px 6px; margin-top: 5px;">Ответить</button>`;
        }
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
    }

    function openVkReply(peerId, sender) {
        currentReplyPeer = peerId;
        document.getElementById("vk-reply-area").classList.remove("hidden");
        document.getElementById("vk-reply-text").placeholder = `Ответ для ${sender}...`;
    }

    function closeVkReply() {
        currentReplyPeer = null;
        document.getElementById("vk-reply-area").classList.add("hidden");
        document.getElementById("vk-reply-text").value = '';
    }

    async function sendVkReply() {
        if (!currentReplyPeer) return;
        const text = document.getElementById("vk-reply-text").value;
        if (!text.trim()) return;
        
        // Здесь нужно будет реализовать отправку ответа через бэкенд
        console.log("Отправка ответа", currentReplyPeer, text);
        closeVkReply();
    }
</script>
</body>
</html>
"""

# =====================================================================
# ИНИЦИАЛИЗАЦИЯ VK (как при отправке сообщения)
# =====================================================================
def init_vk():
    global vk
    if not VK_AVAILABLE:
        return None
    if VK_TOKEN:
        session = vk_api.VkApi(token=VK_TOKEN)
        vk = session.get_api()
    return vk

# =====================================================================
# ЗАПУСК ПОЛЛИНГА СООБЩЕНИЙ (через Long Poll)
# =====================================================================
def start_vk_polling():
    global vk
    if not VK_AVAILABLE:
        print("[VK Polling] VK API не доступен")
        return
    if not VK_TOKEN or not VK_GROUP_ID:
        print("[VK Polling] VK_TOKEN или VK_GROUP_ID не заданы")
        return
    try:
        session = vk_api.VkApi(token=VK_TOKEN)
        longpoll = VkBotLongPoll(session, VK_GROUP_ID)
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                msg = event.object.message
                peer_id = msg['peer_id']
                from_id = msg['from_id']
                text = msg.get('text', '')
                
                # Отправляем сообщение через WebSocket
                socketio.emit('message', {
                    'peer_id': peer_id,
                    'sender': f"user_{from_id}",
                    'text': text,
                    'time': datetime.datetime.now().strftime("%H:%M:%S"),
                    'own': False
                }, namespace='/ws/messages')
    except Exception as e:
        print(f"[VK Polling] Ошибка: {e}")

# =====================================================================
# FLASK МАРШРУТЫ (ОБНОВЛЕНЫ)
# =====================================================================
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, mode=bot_state['mode'], time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), quotes=bot_state['quotes'][-10:])

@app.route('/set_mode', methods=['POST'])
def set_mode():
    new_mode = request.form.get('mode', 'день')
    bot_state['mode'] = new_mode
    return jsonify({"mode": new_mode})

@app.route('/add_quote', methods=['POST'])
def add_quote():
    new_quote = request.form.get('quote', '').strip()
    if new_quote:
        bot_state['quotes'].append(new_quote)
        if len(bot_state['quotes']) > 100:
            bot_state['quotes'] = bot_state['quotes'][-100:]
    return jsonify({"quotes": bot_state['quotes'][-10:]})

@app.route('/vk_post', methods=['POST'])
def vk_post():
    """
    ОБНОВЛЕНО: публикация поста на стену сообщества VK с разбором ошибок и возвратом ссылки.
    """
    global vk
    text = request.form.get('text', '').strip()
    if not text:
        return jsonify({"status": "error", "error": "Текст поста пуст"}), 400
    if not VK_TOKEN or not VK_GROUP_ID:
        return jsonify({"status": "error", "error": "VK_TOKEN или VK_GROUP_ID не заданы в переменных окружения"}), 500
    try:
        if vk is None:
            init_vk()
        # Публикуем запись
        post = vk.wall.post(owner_id=-VK_GROUP_ID, message=text, from_group=1)
        post_id = post.get('post_id')
        if not post_id:
            return jsonify({"status": "error", "error": "VK API не вернул post_id"}), 500
        post_url = f"https://vk.com/wall-{abs(VK_GROUP_ID)}_{post_id}"
        return jsonify({"status": "ok", "post_id": post_id, "url": post_url}), 200
    except Exception as e:
        # Возвращаем текст ошибки для отладки
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/state', methods=['GET'])
def api_state():
    return jsonify({
        "mode": bot_state['mode'],
        "quotes": bot_state['quotes'][-10:]
    })

@app.route('/logs/<name>')
def view_log(name):
    """
    Просмотр логов (admin.log, error.log) через веб-морду.
    """
    log_file = f"{name}.log"
    if not os.path.exists(log_file):
        return f"Лог-файл {log_file} не найден", 404
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
    return f"<pre>{content}</pre>"

# =====================================================================
# ЗАПУСК
# =====================================================================
if __name__ == '__main__':
    # Запускаем поток для Long Polling VK сообщений
    Thread(target=start_vk_polling, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
