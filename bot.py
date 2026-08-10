#!/usr/bin/env python3
# ==========================================
# Файл: bot.py
# Задача: TG-прокси через SecureSecrets
# Версия: 2.0 — секреты из базы
# ==========================================

import os
import sys
import telebot
from flask import Flask, request, jsonify

# ===== ПОДКЛЮЧЕНИЕ К БАЗЕ =====
sys.path.insert(0, '/home/c/ch756438/public_html/ansamb_sledov_bot-dump')
from login_auth.SecureSecrets import SecureSecrets

secrets = SecureSecrets()
TG_BOT_TOKEN = secrets.get('TG_BOT_TOKEN')
TG_CHAT_ID = secrets.get('TG_CHAT_ID')
TG_PROXY_SECRET = secrets.get('TG_PROXY_SECRET')

# ===== ПРОВЕРКА =====
if not TG_BOT_TOKEN:
    print("❌ TG_BOT_TOKEN не найден в SecureSecrets")
    exit(1)
if not TG_CHAT_ID:
    print("❌ TG_CHAT_ID не найден в SecureSecrets")
    exit(1)
if not TG_PROXY_SECRET:
    print("❌ TG_PROXY_SECRET не найден в SecureSecrets")
    exit(1)

# ===== ИНИЦИАЛИЗАЦИЯ =====
bot = telebot.TeleBot(TG_BOT_TOKEN)
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

if __name__ == "__main__":
    print(f"🚀 TG-прокси запущен (секреты из базы)")
    print(f"📡 TG_CHAT_ID: {TG_CHAT_ID}")
    app.run(host="0.0.0.0", port=8080)
