# ==========================================
# Файл: services/app.py
# Справка: README.md → Веб-морда
# Задача: запуск, маршруты страниц, WebSocket, подключение blueprint'ов
# Комментарий: вся логика вынесена во внешние модули
# Зависит от: flask, flask-socketio, debug_utils, theme
# Вызывается из: Render (web service, start command: gunicorn app:app)
# ==========================================

import os
import datetime
import threading
import time
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory, Response
from flask_socketio import SocketIO, emit

# ==========================================
# ВНЕШНИЕ МОДУЛИ
# ==========================================
from debug_utils import debug_log
from services.theme import get_current_theme
from services.youtube_api import get_youtube_info, youtube_search, youtube_stream_generator
from services.web_api import web_api
from services.tg_api import tg_api_bp
from services.vk_api import vk_api_bp
from services.analytics_api import analytics_api

# ==========================================
# НАСТРОЙКИ
# ==========================================
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
if not ADMIN_PASSWORD:
    raise ValueError("ADMIN_PASSWORD не задан")

SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "secret_traces_key_6")

# ==========================================
# ИНИЦИАЛИЗАЦИЯ
# ==========================================
THEME_CSS = os.environ.get("WEB_THEME") or get_current_theme()

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

socketio = SocketIO(app, cors_allowed_origins="*")

messages = []

def log_web(level, message):
    debug_log("WEB_MORDA", message, level)

# ==========================================
# ПОДКЛЮЧЕНИЕ BLUEPRINTS
# ==========================================
app.register_blueprint(web_api, url_prefix='/api')
app.register_blueprint(tg_api_bp, url_prefix='/api/tg')
app.register_blueprint(vk_api_bp, url_prefix='/api/vk')
app.register_blueprint(analytics_api, url_prefix='/api/analytics')

# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================
QUOTES_FILE = "dialogue/data/quotes.txt"

def get_quotes():
    try:
        with open(QUOTES_FILE, "r", encoding='utf-8') as f:
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
# YOUTUBE (через внешний модуль youtube_api.py)
# ==========================================
@app.route('/youtube')
@login_required
def youtube_page():
    log_web("INFO", "Страница YouTube загружена")
    return render_template('youtube.html', theme=THEME_CSS)

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
        log_web("ERROR", f"YouTube info ошибка: {e}")
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
        return Response(youtube_stream_generator(info['video_url']), content_type='video/mp4')
    except Exception as e:
        log_web("ERROR", f"YouTube stream ошибка: {e}")
        return f"Ошибка потока: {e}", 500

@app.route('/youtube_search', methods=['GET'])
@login_required
def youtube_search():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'Поисковый запрос пуст'}), 400
    try:
        results = youtube_search(query)
        return jsonify(results)
    except Exception as e:
        log_web("ERROR", f"YouTube search ошибка: {e}")
        return jsonify({'error': str(e)}), 500

# ==========================================
# WEBSOCKET
# ==========================================
@socketio.on('connect')
def handle_connect():
    log_web("INFO", "WebSocket клиент подключён")
    emit('message_history', messages[-50:])

@socketio.on('disconnect')
def handle_disconnect():
    log_web("INFO", "WebSocket клиент отключён")

@socketio.on('new_message')
def handle_new_message(data):
    data['timestamp'] = datetime.datetime.now().isoformat()
    messages.append(data)
    emit('message_updated', data, broadcast=True)
    log_web("INFO", f"Новое сообщение от {data.get('source')}: {data.get('text', '')[:50]}")

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
            log_web("INFO", "Админ авторизован")
            return redirect(url_for('index'))
        else:
            error = 'Неверный пароль'
            log_web("WARNING", "Неудачная попытка входа")
    return render_template('login.html', error=error)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    log_web("INFO", "Админ вышел")
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    log_web("INFO", "Главная страница загружена")
    return render_template('admin.html', 
        time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        quotes=get_quotes(),
        theme=THEME_CSS
    )

@app.route('/timeline')
@login_required
def timeline():
    timeline_path = os.path.join(os.path.dirname(__file__), '..', 'library', 'timeline.md')
    try:
        with open(timeline_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        content = f"# Таймлайн\n\nОшибка загрузки: {e}"
    return render_template('timeline.html', 
        time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        content=content,
        theme=THEME_CSS
    )

@app.route('/ping')
def ping():
    return {"status": "ok", "service": "web-morda + youtube proxy"}, 200

# ==========================================
# ФОНОВЫЙ ПОТОК: ПОЛУЧЕНИЕ СООБЩЕНИЙ ИЗ VK И TG
# ==========================================
def fetch_messages_periodically():
    """Периодически получает сообщения из VK и Telegram для веб-морды"""
    try:
        from services.tg_api import get_telegram_messages
        from services.vk_api import get_vk_messages
    except ImportError:
        log_web("WARNING", "tg_api.py или vk_api.py не найдены, фоновый поток сообщений отключён")
        return
    
    while True:
        try:
            global messages
            
            # Telegram
            tg_msgs = get_telegram_messages(10)
            for msg in tg_msgs:
                if not any(m.get('chat_id') == msg['chat_id'] and 
                          m.get('text') == msg['text'] and 
                          m.get('timestamp') == msg['timestamp'] for m in messages):
                    socketio.emit('message_updated', msg)
                    messages.append(msg)
            
            # VK
            vk_msgs = get_vk_messages(10)
            for msg in vk_msgs:
                if not any(m.get('chat_id') == msg['chat_id'] and 
                          m.get('text') == msg['text'] and 
                          m.get('timestamp') == msg['timestamp'] for m in messages):
                    socketio.emit('message_updated', msg)
                    messages.append(msg)
            
            # Ограничиваем историю (сохраняем последние 200)
            if len(messages) > 200:
                messages[:] = messages[-200:]
            
            time.sleep(10)  # Проверка каждые 10 секунд
        except Exception as e:
            log_web("ERROR", f"Ошибка получения сообщений: {e}")
            time.sleep(30)

# ==========================================
# ЗАПУСК
# ==========================================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    log_web("INFO", f"Запуск веб-морды на порту {port}")
    
    # Запускаем фоновый поток для сообщений
    message_thread = threading.Thread(target=fetch_messages_periodically, daemon=True)
    message_thread.start()
    
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
