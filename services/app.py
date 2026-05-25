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
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, Response, send_from_directory
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

bot = telebot.TeleBot(BOT_TOKEN) if BOT_TOKEN else None
messages = []

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

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# ==========================================
# YOUTUBE ПРОКСИ (функции)
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
    return render_template('youtube.html', theme=THEME_CSS)

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
# WEBSOCKET
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
    return render_template('login.html', error=error)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('admin.html', 
        time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        quotes=get_quotes(),
        theme=THEME_CSS
    )

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
