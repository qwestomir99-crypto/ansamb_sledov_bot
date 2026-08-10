#!/usr/bin/env python3
# ==========================================
# Файл: bot.py
# Задача: TG-прокси с безопасным получением ключей
# Версия: 5.0 — через эндпоинт, без env
# ==========================================

import os
import telebot
import requests
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

if __name__ == "__main__":
    print(f"🚀 TG-прокси запущен (секреты через эндпоинт)")
    app.run(host="0.0.0.0", port=8080)
