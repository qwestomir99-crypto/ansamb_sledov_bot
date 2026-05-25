# ==========================================
# Файл: services/app.py
# Справка: README.md → Веб-морда
# Задача: единый веб-интерфейс для VK, Telegram и YouTube (прокси)
# Комментарий: тема оформления задаётся переменной WEB_THEME
# Зависит от: flask, flask-socketio, vk_api, telebot, yt-dlp, python-dotenv
# Вызывается из: Render (web service, start command: gunicorn app:app)
# ==========================================

import os
import json
import datetime
from threading import Thread
from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for, Response, send_from_directory
from flask_socketio import SocketIO, emit
from functools import wraps
import telebot
import requests
import yt_dlp

# ==========================================
# НАСТРОЙКИ
# ==========================================
VK_TOKEN = os.environ.get("VK_TOKEN")
try:
    VK_GROUP_ID = int(os.environ.get("VK_GROUP_ID", 0))
except (ValueError, TypeError):
    VK_GROUP_ID = 0

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
if not ADMIN_PASSWORD:
    raise ValueError("ADMIN_PASSWORD не задан")

SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "secret_traces_key_6")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
THEME_CSS = os.environ.get("WEB_THEME", "macos.css")

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True

socketio = SocketIO(app, cors_allowed_origins="*")

# Telegram бот для отправки ответов
bot = telebot.TeleBot(BOT_TOKEN) if BOT_TOKEN else None

# Хранилище сообщений (в памяти)
messages = []

# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================
QUOTES_FILE = "dialogue/data/quotes.txt"

def get_quotes():
    try:
        with open(QUOTES_FILE, "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()][-10:]
    except:
        return []

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('authenticated'):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"error": "Unauthorized"}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ==========================================
# СТАТИЧЕСКИЕ ФАЙЛЫ
# ==========================================
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# ==========================================
# YOUTUBE ПРОКСИ
# ==========================================
def get_youtube_info(url):
    ydl_opts = {
        'format': 'best[height<=720]',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = None
            for fmt in info.get('formats', []):
                if fmt.get('height') and fmt['height'] <= 720 and fmt.get('ext') == 'mp4':
                    if fmt.get('acodec') and fmt['acodec'] != 'none':
                        video_url = fmt['url']
                        break
            if not video_url:
                video_url = info.get('url') or info['formats'][0]['url']
            return {
                'title': info.get('title', 'YouTube видео'),
                'video_url': video_url,
                'duration': info.get('duration', 0)
            }
    except Exception as e:
        print(f"[YOUTUBE] Ошибка: {e}")
        return None

@app.route('/youtube')
@login_required
def youtube_page():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>YouTube через Ансамбль — прокси и поиск</title>
        <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext x='10' y='65' font-family='monospace' font-size='50' fill='%2300ffcc'%3E0.8%3C/text%3E%3C/svg%3E">
        <link rel="stylesheet" href="/static/css/{{ theme }}">
    </head>
    <body>
        <div class="container">
            <h1>🎬 YouTube через Ансамбль</h1>
            <p>Поиск, каталог, прокси — без VPN и рекламы.</p>
            <div class="card">
                <div class="search-row">
                    <input type="text" id="search-query" placeholder="Поиск: квантовая физика, философия, нейросети..." onkeypress="if(event.key==='Enter') searchVideos()">
                    <button onclick="searchVideos()">🔍 Поиск</button>
                </div>
                <div id="catalog" class="video-grid">
                    <div style="color: var(--text-secondary);">Введите запрос для поиска.</div>
                </div>
                <div id="player-container" style="margin-top: 20px;"></div>
            </div>
            <p><a href="/">← Назад в веб-морду</a></p>
        </div>
        <script>
        async function searchVideos() {
            const query = document.getElementById('search-query').value.trim();
            if (!query) return;
            const catalogDiv = document.getElementById('catalog');
            catalogDiv.innerHTML = '<div style="color: var(--accent);">⏳ Поиск...</div>';
            try {
                const resp = await fetch(`/youtube_search?q=${encodeURIComponent(query)}`);
                const data = await resp.json();
                if (data.error) {
                    catalogDiv.innerHTML = `<div style="color: #f00;">❌ ${data.error}</div>`;
                    return;
                }
                if (!data.length) {
                    catalogDiv.innerHTML = '<div style="color: var(--text-secondary);">Ничего не найдено</div>';
                    return;
                }
                catalogDiv.innerHTML = '';
                data.forEach(video => {
                    const card = document.createElement('div');
                    card.className = 'video-card';
                    card.innerHTML = `
                        <div class="video-title">${escapeHtml(video.title)}</div>
                        <div class="video-channel">${escapeHtml(video.author)} • ${video.views_short || ''}</div>
                    `;
                    card.onclick = () => loadVideo(video.video_url);
                    catalogDiv.appendChild(card);
                });
            } catch(e) {
                catalogDiv.innerHTML = '<div style="color:#f00;">Ошибка поиска</div>';
            }
        }
        
        async function loadVideo(videoUrl) {
            const container = document.getElementById('player-container');
            container.innerHTML = '<div style="color: var(--accent);">⏳ Загрузка видео...</div>';
            try {
                const resp = await fetch('/youtube_info', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: videoUrl})
                });
                const data = await resp.json();
                if (data.error) {
                    container.innerHTML = `<div style="color:#f00;">❌ ${data.error}</div>`;
                    return;
                }
                container.innerHTML = `
                    <video controls autoplay>
                        <source src="${data.stream_url}" type="video/mp4">
                        Ваш браузер не поддерживает видео.
                    </video>
                    <div style="margin-top: 10px;">🎵 ${escapeHtml(data.title)} | Длительность: ${Math.floor(data.duration/60)}:${(data.duration%60).toString().padStart(2,'0')}</div>
                `;
            } catch(e) {
                container.innerHTML = '<div style="color:#f00;">❌ Ошибка загрузки видео</div>';
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
    ''', theme=THEME_CSS)

@app.route('/youtube_search', methods=['GET'])
@login_required
def youtube_search():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'Empty query'}), 400
    
    invidious_api = "https://yewtu.be/api/v1/search"
    try:
        resp = requests.get(invidious_api, params={
            'q': query,
            'type': 'video',
            'sort': 'relevance',
            'fields': 'videoId,title,author,viewCount,lengthSeconds,publishedText'
        }, timeout=10)
        data = resp.json()
        videos = []
        for item in data.get('items', []):
            videos.append({
                'video_url': f"https://youtube.com/watch?v={item.get('videoId')}",
                'title': item.get('title', 'Без названия'),
                'author': item.get('author', 'Неизвестный канал'),
                'views_short': item.get('viewCount', '0'),
                'duration': item.get('lengthSeconds', 0)
            })
        return jsonify(videos[:20])
    except Exception as e:
        print(f"[YOUTUBE_SEARCH] Ошибка: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/youtube_info', methods=['POST'])
@login_required
def youtube_info():
    data = request.json
    url = data.get('url', '').strip()
    if not url:
        return jsonify({'error': 'URL не указан'}), 400
    
    try:
        info = get_youtube_info(url)
        if not info:
            return jsonify({'error': 'Не удалось загрузить видео'}), 500
        return jsonify({
            'title': info['title'],
            'stream_url': f"/youtube_stream?url={url}",
            'duration': info['duration']
        })
    except Exception as e:
        print(f"[YOUTUBE_INFO] Ошибка: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/youtube_stream')
@login_required
def youtube_stream():
    url = request.args.get('url')
    if not url:
        return "URL не указан", 400
    
    try:
        info = get_youtube_info(url)
        if not info or not info.get('video_url'):
            return "Не удалось получить видео", 500
        video_url = info['video_url']
        
        def generate():
            try:
                r = requests.get(video_url, stream=True, timeout=30)
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk
            except Exception as e:
                print(f"[YOUTUBE_STREAM] Ошибка: {e}")
        
        return Response(generate(), content_type='video/mp4')
    except Exception as e:
        print(f"[YOUTUBE_STREAM] Ошибка: {e}")
        return f"Ошибка потока: {e}", 500

# ==========================================
# WEBSOCKET СОБЫТИЯ
# ==========================================
@socketio.on('connect')
def handle_connect():
    print("[WS] Клиент подключён")
    emit('message_history', messages[-50:])

@socketio.on('disconnect')
def handle_disconnect():
    print("[WS] Клиент отключён")

@socketio.on('new_message')
def handle_new_message(data):
    data['timestamp'] = datetime.datetime.now().isoformat()
    messages.append(data)
    emit('message_updated', data, broadcast=True)
    print(f"[WS] {data.get('source')}: {data.get('text', '')[:50]}")

# ==========================================
# ОСНОВНЫЕ МАРШРУТЫ
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session.clear()
            session['authenticated'] = True
            session.permanent = True
            return redirect(url_for('index'))
        else:
            error = 'Неверный пароль'
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Вход — Ансамбль Следов 6</title>
        <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext x='10' y='65' font-family='monospace' font-size='50' fill='%2300ffcc'%3E0.8%3C/text%3E%3C/svg%3E">
        <style>
            body { background: #0a0a0a; color: #00ffcc; font-family: monospace; display: flex; justify-content: center; align-items: center; height: 100vh; }
            .login-card { background: #111; border-left: 3px solid #00ffcc; padding: 2rem; border-radius: 8px; width: 300px; }
            input, button { background: #222; color: #00ffcc; border: 1px solid #00ffcc; padding: 8px; width: 100%; margin: 10px 0; border-radius: 4px; }
            button:hover { background: #00ffcc; color: #000; cursor: pointer; }
            .error { color: #f00; }
        </style>
    </head>
    <body>
        <div class="login-card">
            <h2>🔐 Вход</h2>
            <form method="post">
                <input type="password" name="password" placeholder="Админ-пароль" autofocus>
                <button type="submit">Войти</button>
                <div class="error">''' + (error if error else '') + '''</div>
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

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
        <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext x='10' y='65' font-family='monospace' font-size='50' fill='%2300ffcc'%3E0.8%3C/text%3E%3C/svg%3E">
        <script src="https://cdn.socket.io/4.6.0/socket.io.min.js"></script>
        <style>
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

# ==========================================
# API МАРШРУТЫ
# ==========================================
@app.route('/ping')
def ping():
    return {"status": "ok", "service": "web-morda + youtube proxy"}, 200

@app.route('/vk_post', methods=['POST'])
@login_required
def vk_post():
    text = request.form.get('text', '').strip()
    if not text:
        return jsonify({"status": "error", "error": "Текст пуст"}), 400
    if not VK_TOKEN or not VK_GROUP_ID:
        return jsonify({"status": "error", "error": "VK_TOKEN или VK_GROUP_ID не заданы"}), 500
    try:
        import vk_api
        vk_session = vk_api.VkApi(token=VK_TOKEN)
        vk = vk_session.get_api()
        post = vk.wall.post(owner_id=-VK_GROUP_ID, message=text, from_group=1)
        post_id = post.get('post_id')
        post_url = f"https://vk.com/wall-{abs(VK_GROUP_ID)}_{post_id}"
        return jsonify({"status": "ok", "post_id": post_id, "url": post_url}), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/state', methods=['GET'])
@login_required
def api_state():
    return jsonify({
        "quotes": get_quotes()
    })

@app.route('/logs/<name>')
@login_required
def view_log(name):
    log_file = f"{name}.log"
    if not os.path.exists(log_file):
        return f"Лог не найден", 404
    with open(log_file, 'r') as f:
        return f"<pre>{f.read()}</pre>"

@app.route('/send_reply', methods=['POST'])
def send_reply():
    data = request.json
    chat_id = data.get('chat_id')
    text = data.get('text')
    source = data.get('source')
    
    if source == 'telegram' and bot:
        try:
            bot.send_message(chat_id, text)
            socketio.emit('message_updated', {
                'source': 'admin',
                'text': text,
                'timestamp': datetime.datetime.now().isoformat(),
                'own': True
            })
            return jsonify({"status": "ok"})
        except Exception as e:
            return jsonify({"status": "error", "error": str(e)})
    elif source == 'vk':
        return jsonify({"status": "error", "error": "VK replies not implemented"})
    else:
        return jsonify({"status": "error", "error": "Unknown source"})

# ==========================================
# ЗАПУСК
# ==========================================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
