# bot.py — TG-прокси для Render
import os
import telebot
from flask import Flask, request, jsonify

TG_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
SECRET_KEY = os.getenv("TG_PROXY_SECRET")

bot = telebot.TeleBot(TG_TOKEN)
app = Flask(__name__)

@app.route("/publish", methods=["POST"])
def publish():
    data = request.json
    if data.get("secret") != SECRET_KEY:
        return jsonify({"status": "error", "message": "unauthorized"}), 403
    
    text = data.get("text", "")
    if text:
        bot.send_message(TG_CHAT_ID, text)
        return jsonify({"status": "ok"}), 200
    return jsonify({"status": "error", "message": "empty"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
