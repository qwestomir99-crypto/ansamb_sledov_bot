#!/usr/bin/env python3
# ==========================================
# Файл: bot.py
# Задача: TG-прокси для Render
# Версия: 1.0 — приёмник постов
# ==========================================

import os
import telebot
from flask import Flask, request, jsonify

# ===== КОНФИГУРАЦИЯ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ =====
TG_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
SECRET_KEY = os.getenv("TG_PROXY_SECRET")

# ===== ПРОВЕРКА КОНФИГУРАЦИИ =====
if not TG_TOKEN:
    print("❌ TG_BOT_TOKEN не задан")
    exit(1)
if not TG_CHAT_ID:
    print("❌ TG_CHAT_ID не задан")
    exit(1)
if not SECRET_KEY:
    print("❌ TG_PROXY_SECRET не задан")
    exit(1)

# ===== ИНИЦИАЛИЗАЦИЯ =====
bot = telebot.TeleBot(TG_TOKEN)
app = Flask(__name__)

# ===== ЭНДПОИНТ ДЛЯ ПУБЛИКАЦИИ =====
@app.route("/publish", methods=["POST"])
def publish():
    data = request.json
    
    # Проверка секретного ключа
    if data.get("secret") != SECRET_KEY:
        return jsonify({"status": "error", "message": "unauthorized"}), 403
    
    text = data.get("text", "")
    if text:
        try:
            bot.send_message(TG_CHAT_ID, text)
            return jsonify({"status": "ok"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    return jsonify({"status": "error", "message": "empty"}), 400

# ===== ЗАПУСК =====
if __name__ == "__main__":
    print(f"🚀 TG-прокси запущен на порту 8080")
    print(f"📡 TG_CHAT_ID: {TG_CHAT_ID}")
    app.run(host="0.0.0.0", port=8080)
