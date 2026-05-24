# ==========================================
# Файл: app.py
# Справка: README.md → Веб-морда
# Задача: веб-интерфейс для управления ботом, постинга в VK и ответов на сообщения
# Комментарий: работает как отдельный web-сервис на Render (или в фоне с ботом)
# Зависит от: flask, vk_api, python-dotenv
# Вызывается из: Render (web service, start command: gunicorn app:app)
# ==========================================

import os
import datetime
from threading import Thread
from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
from functools import wraps

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
    raise ValueError("ADMIN_PASSWORD не задан в переменных окружения")

SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "secret_traces_key_6")

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True

# ==========================================
# ВНУТРЕННЕЕ СОСТОЯНИЕ (общее с ботом)
# ==========================================
# Для простоты читаем из файлов, которые обновляет бот
QUOTES_FILE = "dialogue/data/quotes.txt"
MODE_FILE = "dialogue/data/mode.txt"

def get_current_mode():
    try:
        with open(MODE_FILE, "r") as f:
            return f.read().strip()
    except:
        return "день"

def get_quotes():
    try:
        with open(QUOTES_FILE, "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()][-10:]
    except:
        return []

# ==========================================
# ДЕКОРАТОР АВТОРИЗАЦИИ
# ==========================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"error": "Unauthorized"}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# МАРШРУТЫ
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
        <title>Ансамбль Следов 6 — веб-морда</title>
        <style>
            body { background: #0a0a0a; color: #00ffcc; font-family: monospace; padding: 2rem; }
            .card { background: #111; border-left: 3px solid #00ffcc; padding: 1rem; margin: 1rem 0; border-radius: 8px; }
            button, input, textarea { background: #222; color: #00ffcc; border: 1px solid #00ffcc; padding: 6px 12px; border-radius: 4px; }
            button:hover { background: #00ffcc; color: #000; cursor: pointer; }
            a { color: #00ffcc; }
        </style>
    </head>
    <body>
        <h1>🔥 Ансамбль Следов 6</h1>
        <p>Ритм 0,8 Гц. Управление ботом из браузера. Время: {{ time }}</p>
        <p><a href="/logs/admin">📋 admin.log</a> | <a href="/logs/error">❌ error.log</a></p>
        
        <div class="card">
            <h2>🎬 Пост в VK</h2>
            <textarea id="post-text" rows="3" cols="50" placeholder="Текст поста..."></textarea><br>
            <button onclick="sendPost()">Отправить</button>
            <span id="status"></span>
        </div>
        
        <div class="card">
            <h2>📜 Цитаты (последние 10)</h2>
            <ul id="quotes-list">
                {% for q in quotes %}<li>{{ q[:100] }}</li>{% endfor %}
            </ul>
        </div>
        
        <script>
        async function sendPost() {
            const text = document.getElementById('post-text').value;
            if (!text.trim()) return;
            const status = document.getElementById('status');
            status.innerText = '⏳ Отправка...';
            const resp = await fetch('/vk_post', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'text=' + encodeURIComponent(text)
            });
            const data = await resp.json();
            if (data.status === 'ok') {
                status.innerHTML = `✅ Опубликовано! <a href="${data.url}" target="_blank">Ссылка</a>`;
                document.getElementById('post-text').value = '';
            } else {
                status.innerText = '❌ ' + data.error;
            }
        }
        </script>
    </body>
    </html>
    ''', time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), quotes=get_quotes())

@app.route('/ping')
def ping():
    return {"status": "ok", "service": "web-morda"}, 200

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

@app.route('/logs/<name>')
@login_required
def view_log(name):
    log_file = f"{name}.log"
    if not os.path.exists(log_file):
        return f"Лог не найден", 404
    with open(log_file, 'r') as f:
        return f"<pre>{f.read()}</pre>"

# ==========================================
# ЗАПУСК (для gunicorn)
# ==========================================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
