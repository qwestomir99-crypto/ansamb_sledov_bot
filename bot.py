#!/usr/bin/env python3
# ==========================================
# Файл: bot.py (для Render)
# Задача: TG-прокси + YouTube-прокси (домен + IP)
# Версия: 12.1 — два способа проверки YouTube
# ==========================================

import os
import telebot
import requests
import threading
import time
import traceback
from flask import Flask, request, jsonify

# ===== АДРЕС ЭНДПОИНТА =====
SECRET_ENDPOINT = "https://ch756438.tw1.ru/api/secret/index.php"

def get_secret(key):
    try:
        r = requests.get(f"{SECRET_ENDPOINT}?key={key}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data.get("value")
    except:
        pass
    return None

# ===== ПОЛУЧЕНИЕ КЛЮЧЕЙ =====
BOT_TOKEN = get_secret("BOT_TOKEN")
TG_CHAT_ID = get_secret("TG_CHAT_ID")
TG_PROXY_SECRET = get_secret("TG_PROXY_SECRET")

# ===== ПРОВЕРКА =====
if not BOT_TOKEN:
    print("❌ BOT_TOKEN не получен")
    exit(1)
if not TG_CHAT_ID:
    print("❌ TG_CHAT_ID не получен")
    exit(1)
if not TG_PROXY_SECRET:
    print("❌ TG_PROXY_SECRET не получен")
    exit(1)

# ===== ИНИЦИАЛИЗАЦИЯ =====
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ============================================================
# ЭНДПОИНТЫ
# ============================================================

@app.route("/", methods=["GET"])
def index():
    return "TG-прокси работает!"

@app.route("/publish", methods=["POST"])
def publish():
    data = request.json
    if data.get("secret") != TG_PROXY_SECRET:
        return jsonify({"status": "error", "message": "unauthorized"}), 403
    
    text = data.get("text", "")
    if text:
        try:
            bot.send_message(TG_CHAT_ID, text)
            return jsonify({"status": "ok"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    return jsonify({"status": "error", "message": "empty"}), 400

@app.route("/publish_photo", methods=["POST"])
def publish_photo():
    data = request.json
    if data.get("secret") != TG_PROXY_SECRET:
        return jsonify({"status": "error", "message": "unauthorized"}), 403
    
    photo_url = data.get("photo_url")
    caption = data.get("caption", "")
    
    # ===== СКАЧИВАЕМ ФОТО НА RENDER =====
    if photo_url:
        try:
            resp = requests.get(photo_url, timeout=15)
            if resp.status_code == 200:
                ext = photo_url.split('.')[-1].split('?')[0]
                if len(ext) > 5:
                    ext = "jpg"
                temp_path = f"/tmp/photo_{int(time.time())}.{ext}"
                with open(temp_path, "wb") as f:
                    f.write(resp.content)
                photo_url = temp_path
                print(f"[RENDER] ✅ Фото скачано: {temp_path}")
            else:
                print(f"[RENDER] ❌ Не удалось скачать фото (HTTP {resp.status_code})")
                return jsonify({"status": "error", "message": "download failed"}), 500
        except Exception as e:
            print(f"[RENDER] ❌ Ошибка скачивания фото: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
    # ======================================

    if not photo_url:
        return jsonify({"status": "error", "message": "no photo"}), 400

    try:
        if not os.path.exists(photo_url):
            print(f"[RENDER] ❌ Файл {photo_url} не найден!")
            return jsonify({"status": "error", "message": "file not found"}), 500

        bot.send_photo(TG_CHAT_ID, photo_url, caption=caption)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"[RENDER] ❌ Ошибка отправки фото: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/publish_video", methods=["POST"])
def publish_video():
    data = request.json
    if data.get("secret") != TG_PROXY_SECRET:
        return jsonify({"status": "error", "message": "unauthorized"}), 403
    
    video_url = data.get("video_url")
    caption = data.get("caption", "")
    
    if video_url:
        message = f"{caption}\n\n🎬 Видео: {video_url}"
        bot.send_message(TG_CHAT_ID, message)
        return jsonify({"status": "ok"}), 200
    return jsonify({"status": "error", "message": "empty"}), 400

@app.route("/publish_audio", methods=["POST"])
def publish_audio():
    data = request.json
    if data.get("secret") != TG_PROXY_SECRET:
        return jsonify({"status": "error", "message": "unauthorized"}), 403
    
    audio_url = data.get("audio_url")
    caption = data.get("caption", "")
    
    if audio_url:
        message = f"{caption}\n\n🎵 Аудио: {audio_url}"
        bot.send_message(TG_CHAT_ID, message)
        return jsonify({"status": "ok"}), 200
    return jsonify({"status": "error", "message": "empty"}), 400

# ============================================================
# ЭНДПОИНТЫ ДЛЯ YOUTUBE-ПРОКСИ
# ============================================================

@app.route("/youtube", methods=["GET"])
def youtube_domain():
    """Прокси для YouTube через доменное имя"""
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "missing url"}), 400

    try:
        response = requests.get(url, stream=True, timeout=20)
        return response.content, response.status_code, {
            "Content-Type": response.headers.get("Content-Type", "application/octet-stream")
        }
    except Exception as e:
        print(f"[RENDER] ❌ Ошибка YouTube (домен): {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/youtube_ip", methods=["GET"])
def youtube_ip():
    """Прокси для YouTube через IP-адрес"""
    ip = request.args.get("ip")
    if not ip:
        return jsonify({"error": "missing ip"}), 400

    # Используем IP-адрес вместо домена
    url = f"http://{ip}"
    try:
        response = requests.get(url, stream=True, timeout=20)
        return response.content, response.status_code, {
            "Content-Type": response.headers.get("Content-Type", "application/octet-stream")
        }
    except Exception as e:
        print(f"[RENDER] ❌ Ошибка YouTube (IP): {e}")
        return jsonify({"error": str(e)}), 500

# ============================================================
# АВТО-ПИНГ (чтобы Render не засыпал)
# ============================================================

def keep_alive():
    my_url = "https://ansamb-sledov-bot-p56x.onrender.com"
    while True:
        try:
            requests.get(my_url, timeout=5)
            print(f"[PING] ✅ Render пинганул себя: {my_url}")
        except Exception as e:
            print(f"[PING] ❌ Ошибка пинга: {e}")
        time.sleep(30)

threading.Thread(target=keep_alive, daemon=True).start()
print("[PING] 🛡️ Авто-пингер запущен (ждём 30 сек между ударами)")

# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == "__main__":
    print(f"🚀 TG-прокси + YouTube-прокси (домен/IP) запущен")
    app.run(host="0.0.0.0", port=8080)
