#!/usr/bin/env python3
# ==========================================
# Файл: bot.py (для Render)
# Задача: TG-прокси с безопасным получением ключей + авто-пинг (keep-alive)
# Версия: 6.0 — с фоновым пингером
# ==========================================

import os
import telebot
import requests
import threading
import time
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
    if photo_url:
        try:
            bot.send_photo(TG_CHAT_ID, photo_url, caption=caption)
            return jsonify({"status": "ok"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    return jsonify({"status": "error", "message": "empty"}), 400

@app.route("/publish_video", methods=["POST"])
def publish_video():
    data = request.json
    if data.get("secret") != TG_PROXY_SECRET:
        return jsonify({"status": "error", "message": "unauthorized"}), 403
    
    video_url = data.get("video_url")
    caption = data.get("caption", "")
    if video_url:
        try:
            bot.send_video(TG_CHAT_ID, video_url, caption=caption)
            return jsonify({"status": "ok"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    return jsonify({"status": "error", "message": "empty"}), 400

@app.route("/publish_audio", methods=["POST"])
def publish_audio():
    data = request.json
    if data.get("secret") != TG_PROXY_SECRET:
        return jsonify({"status": "error", "message": "unauthorized"}), 403
    
    audio_url = data.get("audio_url")
    caption = data.get("caption", "")
    if audio_url:
        try:
            bot.send_audio(TG_CHAT_ID, audio_url, caption=caption)
            return jsonify({"status": "ok"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    return jsonify({"status": "error", "message": "empty"}), 400

# ============================================================
# АВТО-ПИНГ (чтобы Render не засыпал)
# ============================================================

def keep_alive():
    """Фоновый поток: пингует свой собственный URL каждые 30 секунд"""
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
    print(f"🚀 TG-прокси запущен (с авто-пингером)")
    app.run(host="0.0.0.0", port=8080)
