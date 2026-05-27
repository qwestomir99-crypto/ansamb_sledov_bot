# ==========================================
# Файл: services/app_modules/youtube.py
# Справка: README.md → Веб-морда / YouTube
# Задача: YouTube-прокси (поиск, стрим, инфо)
# Комментарий: вынесено из app.py
# Зависит от: flask, debug_utils, services.youtube_api
# Вызывается из: app_modules/__init__.py
# ==========================================

from flask import Blueprint, request, jsonify, render_template, Response
from debug_utils import debug_log
from services.youtube_api import get_youtube_info, youtube_search, youtube_stream_generator
from .auth import login_required

youtube_bp = Blueprint('youtube', __name__)

def log_y(level, message):
    debug_log("APP_YOUTUBE", message, level)

@youtube_bp.route('/')
@login_required
def youtube_page():
    log_y("INFO", "Страница YouTube загружена")
    return render_template('youtube.html', theme=THEME_CSS)

@youtube_bp.route('/info', methods=['POST'])
@login_required
def youtube_info():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({'error': 'URL не указан'}), 400
    try:
        info = get_youtube_info(url)
        if not info:
            return jsonify({'error': 'Не удалось загрузить видео'}), 500
        return jsonify({
            'title': info['title'],
            'stream_url': f"/youtube/stream?url={url}",
            'duration': info['duration']
        })
    except Exception as e:
        log_y("ERROR", str(e))
        return jsonify({'error': str(e)}), 500

@youtube_bp.route('/stream')
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
        log_y("ERROR", str(e))
        return f"Ошибка потока: {e}", 500

@youtube_bp.route('/search', methods=['GET'])
@login_required
def youtube_search():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'Поисковый запрос пуст'}), 400
    try:
        results = youtube_search(query)
        return jsonify(results)
    except Exception as e:
        log_y("ERROR", str(e))
        return jsonify({'error': str(e)}), 500
