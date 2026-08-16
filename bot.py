#!/usr/bin/env python3
# ==========================================
# Файл: bot.py (для Render)
# Справка: README.md → Telegram прокси / Render
# Задача: TG-прокси + кнопки + callback'и + YouTube-туннели
# Комментарий: работает на Render. Туннели в отдельных модулях.
# Зависит от: flask, telebot, requests, render_callbacks, render_*_tunnel
# Вызывается из: services/tg_api.py (через HTTPS POST)
# Версия: 15.0 — добавлены туннели: HTTP, WebSocket, UDP
# ==========================================

import os
import telebot
import requests
import threading
import time
import traceback
from flask import Flask, request, jsonify
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ===== ИМПОРТ CALLBACK'ОВ =====
from render_callbacks import register_callbacks

# ===== ИМПОРТ ТУННЕЛЕЙ =====
from render_http_tunnel import register_http_tunnel
from render_ws_tunnel import register_ws_tunnel
from render_udp_tunnel import register_udp_tunnel

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

# ===== РЕГИСТРАЦИЯ CALLBACK'ОВ =====
register_callbacks(bot)
print("✅ Callback'и зарегистрированы из render_callbacks.py")

# ===== РЕГИСТРАЦИЯ ТУННЕЛЕЙ =====
register_http_tunnel(app)
print("✅ HTTP-туннель зарегистрирован")

register_udp_tunnel(app)
print("✅ UDP-тест зарегистрирован")

socketio = register_ws_tunnel(app)
print("✅ WebSocket-туннель зарегистрирован")

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def build_keyboard(buttons_data):
    """Строит InlineKeyboardMarkup из JSON-структуры кнопок"""
    keyboard = InlineKeyboardMarkup()
    for row in buttons_data:
        buttons_row = []
        for btn in row:
            buttons_row.append(InlineKeyboardButton(
                text=btn.get("text", "?"),
                callback_data=btn.get("callback_data", "none")
            ))
        keyboard.row(*buttons_row)
    return keyboard

# ============================================================
# ЭНДПОИНТЫ
# ============================================================

@app.route("/", methods=["GET"])
def index():
    return "TG-прокси работает!"

@app.route("/publish", methods=["POST"])
def publish():
    try:
        data = request.json
        if data.get("secret") != TG_PROXY_SECRET:
            return jsonify({"status": "error", "message": "unauthorized"}), 403
        
        text = data.get("text", "")
        if text:
            try:
                bot.send_message(TG_CHAT_ID, text)
                return jsonify({"status": "ok"}), 200
            except Exception as e:
                print(f"[RENDER] ❌ Ошибка отправки сообщения: {e}")
                return jsonify({"status": "error", "message": str(e)}), 500
        return jsonify({"status": "error", "message": "empty"}), 400
    except Exception as e:
        print(f"[RENDER] ❌ Критическая ошибка /publish: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/publish_with_buttons", methods=["POST"])
def publish_with_buttons():
    try:
        data = request.json
        if data.get("secret") != TG_PROXY_SECRET:
            return jsonify({"status": "error", "message": "unauthorized"}), 403
        
        text = data.get("text", "")
        buttons_data = data.get("buttons", [])
        
        if not text:
            return jsonify({"status": "error", "message": "empty"}), 400
        
        try:
            keyboard = build_keyboard(buttons_data) if buttons_data else None
            if keyboard:
                bot.send_message(TG_CHAT_ID, text, reply_markup=keyboard)
            else:
                bot.send_message(TG_CHAT_ID, text)
            return jsonify({"status": "ok"}), 200
        except Exception as e:
            print(f"[RENDER] ⚠️ Ошибка с кнопками: {e}. Отправляю без кнопок.")
            try:
                bot.send_message(TG_CHAT_ID, text)
                return jsonify({"status": "ok", "warning": "sent without buttons"}), 200
            except Exception as e2:
                return jsonify({"status": "error", "message": str(e2)}), 500
    except Exception as e:
        print(f"[RENDER] ❌ Критическая ошибка /publish_with_buttons: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/publish_photo", methods=["POST"])
def publish_photo():
    try:
        data = request.json
        if data.get("secret") != TG_PROXY_SECRET:
            return jsonify({"status": "error", "message": "unauthorized"}), 403
        
        photo_url = data.get("photo_url")
        caption = data.get("caption", "")
        
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
                    
                    try:
                        with open(temp_path, "rb") as f:
                            bot.send_photo(TG_CHAT_ID, f, caption=caption[:200])
                        os.remove(temp_path)
                        return jsonify({"status": "ok"}), 200
                    except Exception as e:
                        print(f"[RENDER] ⚠️ Ошибка отправки файла: {e}")
                        try:
                            os.remove(temp_path)
                        except:
                            pass
                        try:
                            bot.send_message(TG_CHAT_ID, f"{caption[:200]}\n\n📸 {photo_url}")
                            return jsonify({"status": "ok", "warning": "sent as URL"}), 200
                        except Exception as e2:
                            return jsonify({"status": "error", "message": str(e2)}), 500
                else:
                    print(f"[RENDER] ❌ Не удалось скачать фото (HTTP {resp.status_code})")
                    return jsonify({"status": "error", "message": "download failed"}), 500
            except Exception as e:
                print(f"[RENDER] ❌ Ошибка скачивания фото: {e}")
                return jsonify({"status": "error", "message": str(e)}), 500
        
        return jsonify({"status": "error", "message": "no photo"}), 400
    except Exception as e:
        print(f"[RENDER] ❌ Критическая ошибка /publish_photo: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/publish_video", methods=["POST"])
def publish_video():
    try:
        data = request.json
        if data.get("secret") != TG_PROXY_SECRET:
            return jsonify({"status": "error", "message": "unauthorized"}), 403
        
        video_url = data.get("video_url")
        caption = data.get("caption", "")
        
        if video_url:
            message = f"{caption[:200]}\n\n🎬 Видео: {video_url}"
            bot.send_message(TG_CHAT_ID, message)
            return jsonify({"status": "ok"}), 200
        return jsonify({"status": "error", "message": "empty"}), 400
    except Exception as e:
        print(f"[RENDER] ❌ Критическая ошибка /publish_video: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/publish_audio", methods=["POST"])
def publish_audio():
    try:
        data = request.json
        if data.get("secret") != TG_PROXY_SECRET:
            return jsonify({"status": "error", "message": "unauthorized"}), 403
        
        audio_url = data.get("audio_url")
        caption = data.get("caption", "")
        
        if audio_url:
            message = f"{caption[:200]}\n\n🎵 Аудио: {audio_url}"
            bot.send_message(TG_CHAT_ID, message)
            return jsonify({"status": "ok"}), 200
        return jsonify({"status": "error", "message": "empty"}), 400
    except Exception as e:
        print(f"[RENDER] ❌ Критическая ошибка /publish_audio: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================================
# ЭНДПОИНТЫ ДЛЯ YOUTUBE-ПРОКСИ
# ============================================================

@app.route("/youtube", methods=["GET"])
def youtube_domain():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "missing url"}), 400
    try:
        response = requests.get(url, stream=True, timeout=20)
        return response.content, response.status_code, {
            "Content-Type": response.headers.get("Content-Type", "application/octet-stream")
        }
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/youtube_ip", methods=["GET"])
def youtube_ip():
    ip = request.args.get("ip")
    if not ip:
        return jsonify({"error": "missing ip"}), 400
    try:
        response = requests.get(f"http://{ip}", stream=True, timeout=20)
        return response.content, response.status_code, {
            "Content-Type": response.headers.get("Content-Type", "application/octet-stream")
        }
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================
# АВТО-ПИНГ
# ============================================================

def keep_alive():
    my_url = "https://ansamb-sledov-bot-p56x.onrender.com"
    while True:
        try:
            requests.get(my_url, timeout=5)
        except:
            pass
        time.sleep(30)

threading.Thread(target=keep_alive, daemon=True).start()

# ============================================================
# ЗАПУСК ПОЛЛИНГА (для приёма callback'ов)
# ============================================================

def start_polling():
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            print(f"[POLLING] Ошибка: {e}")
            time.sleep(5)

threading.Thread(target=start_polling, daemon=True).start()
print("[POLLING] Приём callback'ов запущен")

# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == "__main__":
    print("🚀 TG-прокси + туннели + кнопки + callback'и + YouTube запущен")
    # Используем socketio.run вместо app.run для WebSocket
    socketio.run(app, host="0.0.0.0", port=8080, allow_unsafe_werkzeug=True)
