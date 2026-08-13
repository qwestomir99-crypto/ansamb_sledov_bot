#!/usr/bin/env python3
# ==========================================
# Файл: bot.py (для Render)
# Справка: README.md → Telegram прокси / Render
# Задача: TG-прокси (сообщения, фото, кнопки) + обработка callback'ов + YouTube-прокси
# Комментарий: работает на Render. Принимает запросы от сервера.
#              Кнопки передаются в JSON. Callback'и обрабатываются на Render.
# Зависит от: flask, telebot, requests, threading
# Вызывается из: services/tg_api.py (через HTTPS POST)
# Версия: 13.1 — добавлена обработка callback'ов на Render
# ==========================================

import os
import telebot
import requests
import threading
import time
import traceback
from flask import Flask, request, jsonify
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

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

def get_admin_buttons():
    """Кнопки админ-меню"""
    return [
        [{"text": "📝 Посты", "callback_data": "admin_posts"}],
        [{"text": "📜 Цитаты", "callback_data": "admin_quotes"}],
        [{"text": "🎛️ Миксер", "callback_data": "admin_mixer"}],
        [{"text": "📅 Расписание", "callback_data": "admin_schedule"}],
        [{"text": "⚙️ Настройки", "callback_data": "admin_settings"}],
        [{"text": "🩺 Диагностика", "callback_data": "admin_diag"}],
        [{"text": "🚪 Выйти", "callback_data": "admin_logout"}]
    ]

# ============================================================
# ОБРАБОТКА CALLBACK'ОВ (на Render)
# ============================================================

@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    """Обрабатывает все нажатия на кнопки"""
    try:
        data = call.data
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        
        print(f"[CALLBACK] {data} от {call.from_user.id}")
        
        if data == "admin_posts":
            text = "📝 *Посты*\n\nУправление пулом постов:"
            buttons = [
                [{"text": "📋 Список", "callback_data": "admin_posts_list"}],
                [{"text": "➕ Добавить", "callback_data": "admin_posts_add"}],
                [{"text": "◀️ Назад", "callback_data": "admin_back"}]
            ]
            bot.edit_message_text(text, chat_id, message_id, reply_markup=build_keyboard(buttons))
        
        elif data == "admin_quotes":
            text = "📜 *Цитаты*\n\nУправление цитатами:"
            buttons = [
                [{"text": "📖 Список", "callback_data": "admin_quotes_list"}],
                [{"text": "➕ Добавить", "callback_data": "admin_quotes_add"}],
                [{"text": "◀️ Назад", "callback_data": "admin_back"}]
            ]
            bot.edit_message_text(text, chat_id, message_id, reply_markup=build_keyboard(buttons))
        
        elif data == "admin_mixer":
            bot.edit_message_text("🎛️ Миксер запущен...", chat_id, message_id)
            # Отправляем запрос на наш сервер для запуска миксера
            try:
                requests.post(
                    "https://ch756438.tw1.ru/ansamb_sledov_bot-dump/api/mixer_trigger.php",
                    json={"secret": TG_PROXY_SECRET},
                    timeout=5
                )
            except:
                pass
        
        elif data == "admin_schedule":
            text = "📅 *Расписание*\n\nРежимы:"
            buttons = [
                [{"text": "🌅 Утро", "callback_data": "admin_sched_morning"}],
                [{"text": "☀️ День", "callback_data": "admin_sched_day"}],
                [{"text": "🌆 Вечер", "callback_data": "admin_sched_evening"}],
                [{"text": "🌙 Ночь", "callback_data": "admin_sched_night"}],
                [{"text": "◀️ Назад", "callback_data": "admin_back"}]
            ]
            bot.edit_message_text(text, chat_id, message_id, reply_markup=build_keyboard(buttons))
        
        elif data == "admin_settings":
            bot.edit_message_text("⚙️ *Настройки*\n\nЗдесь будут настройки.", chat_id, message_id)
        
        elif data == "admin_diag":
            bot.edit_message_text("🩺 Запускаю диагностику...", chat_id, message_id)
            try:
                r = requests.post(
                    "https://ch756438.tw1.ru/ansamb_sledov_bot-dump/api/diag_trigger.php",
                    json={"secret": TG_PROXY_SECRET},
                    timeout=10
                )
                bot.send_message(chat_id, "✅ Аудит завершён. Смотрите logs/audit.log")
            except:
                bot.send_message(chat_id, "❌ Не удалось запустить диагностику")
        
        elif data == "admin_logout":
            bot.edit_message_text("✅ Вы вышли из админ-режима.", chat_id, message_id)
        
        elif data == "admin_back":
            bot.edit_message_text(
                "🛡️ Админ-меню:",
                chat_id,
                message_id,
                reply_markup=build_keyboard(get_admin_buttons())
            )
        
        elif data == "admin_posts_list":
            # Запрашиваем список постов с нашего сервера
            try:
                r = requests.get(
                    "https://ch756438.tw1.ru/ansamb_sledov_bot-dump/api/posts_list.php",
                    timeout=10
                )
                posts_text = r.text[:3000] if r.status_code == 200 else "❌ Ошибка получения постов"
            except:
                posts_text = "❌ Ошибка получения постов"
            
            buttons = [[{"text": "◀️ Назад", "callback_data": "admin_posts"}]]
            bot.edit_message_text(posts_text, chat_id, message_id, reply_markup=build_keyboard(buttons))
        
        elif data == "admin_quotes_list":
            try:
                r = requests.get(
                    "https://ch756438.tw1.ru/ansamb_sledov_bot-dump/api/quotes_list.php",
                    timeout=10
                )
                quotes_text = r.text[:3000] if r.status_code == 200 else "❌ Ошибка получения цитат"
            except:
                quotes_text = "❌ Ошибка получения цитат"
            
            buttons = [[{"text": "◀️ Назад", "callback_data": "admin_quotes"}]]
            bot.edit_message_text(quotes_text, chat_id, message_id, reply_markup=build_keyboard(buttons))
        
        else:
            bot.edit_message_text("❓ Неизвестная команда.", chat_id, message_id)
        
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"[CALLBACK] ❌ Ошибка: {e}")
        try:
            bot.answer_callback_query(call.id, "Ошибка обработки")
        except:
            pass

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
    print("🚀 TG-прокси + кнопки + callback'и + YouTube запущен")
    app.run(host="0.0.0.0", port=8080)
