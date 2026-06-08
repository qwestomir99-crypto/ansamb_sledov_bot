# ==========================================
# Файл: services/web_api/youtube_upload.py
# Справка: README.md → Веб-морда / API / YouTube Upload
# Задача: загрузка видео на YouTube из веб-морды
# Комментарий: добавлена защита @login_required
# Зависит от: flask, os, json, google.oauth2.credentials, google_auth_oauthlib.flow, googleapiclient
# Вызывается из: web_api/__init__.py
# ==========================================

import os
import json
import tempfile
from flask import Blueprint, request, jsonify, redirect, url_for
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from debug_utils import debug_log
from services.app import login_required

youtube_upload_bp = Blueprint('youtube_upload', __name__)

# ==========================================
# НАСТРОЙКИ
# ==========================================
TOKEN_VAR = "YOUTUBE_UPLOAD_TOKEN"
CLIENT_SECRET_JSON = os.environ.get("YOUTUBE_CLIENT_SECRET")

def get_credentials():
    """Возвращает credentials из переменной окружения"""
    token_json = os.environ.get(TOKEN_VAR)
    if token_json:
        return Credentials.from_authorized_user_info(json.loads(token_json))
    return None

def save_credentials(creds):
    """Сохраняет credentials в переменную окружения"""
    # На Render это не работает напрямую, но мы будем обновлять через API
    # Пока сохраняем в файл (для отладки)
    with open("youtube_token.json", "w") as f:
        f.write(creds.to_json())
    debug_log("YOUTUBE_UPLOAD", "Токен сохранён в youtube_token.json", "INFO")

def get_flow():
    """Возвращает Flow для OAuth 2.0"""
    if not CLIENT_SECRET_JSON:
        raise ValueError("YOUTUBE_CLIENT_SECRET не задан")
    client_config = json.loads(CLIENT_SECRET_JSON)
    return Flow.from_client_config(
        client_config,
        scopes=['https://www.googleapis.com/auth/youtube.upload']
    )

# ==========================================
# ЭНДПОИНТЫ
# ==========================================
@youtube_upload_bp.route('/authorize')
@login_required
def authorize():
    """Начинает OAuth 2.0 авторизацию"""
    flow = get_flow()
    flow.redirect_uri = url_for('youtube_upload.oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    return redirect(authorization_url)

@youtube_upload_bp.route('/oauth2callback')
@login_required
def oauth2callback():
    """Обрабатывает callback после авторизации"""
    flow = get_flow()
    flow.redirect_uri = url_for('youtube_upload.oauth2callback', _external=True)
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    save_credentials(creds)
    return "✅ Авторизация завершена. Токен сохранён."

@youtube_upload_bp.route('/upload', methods=['POST'])
@login_required
def upload_video():
    """Загружает видео на YouTube"""
    creds = get_credentials()
    if not creds:
        return jsonify({"error": "Не авторизован"}), 401
    
    data = request.json
    file_url = data.get('file_url')
    title = data.get('title', 'Видео из Ансамбля')
    description = data.get('description', '')
    
    if not file_url:
        return jsonify({"error": "file_url обязателен"}), 400
    
    # Скачиваем видео во временный файл
    import requests
    response = requests.get(file_url, stream=True)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    for chunk in response.iter_content(chunk_size=8192):
        temp_file.write(chunk)
    temp_file.close()
    
    # Загружаем на YouTube
    youtube = build("youtube", "v3", credentials=creds)
    body = {
        "snippet": {
            "title": title,
            "description": description
        },
        "status": {
            "privacyStatus": "unlisted"
        }
    }
    media = MediaFileUpload(temp_file.name)
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )
    response = request.execute()
    
    # Удаляем временный файл
    os.unlink(temp_file.name)
    
    return jsonify({"status": "ok", "video_id": response['id']})
