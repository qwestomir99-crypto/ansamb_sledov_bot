import threading
import time
import requests
from flask import Flask, request
import os

flask_app = Flask(__name__)

@flask_app.route('/')
def health():
    if request.remote_addr == '127.0.0.1':
        return "Pong", 200
    return {"status": "tleem", "rhythm": "0.8 Hz", "version": "3.2"}, 200

@flask_app.route('/token', methods=['GET'])
def get_token():
    secret = request.args.get('secret')
    if secret != os.environ.get("TOKEN_SECRET", "tleem2026"):
        return "Forbidden", 403
    return os.environ.get("BOT_TOKEN"), 200

@flask_app.route('/ping', methods=['GET'])
def ping():
    return "pong", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

def start_web():
    """Запускает Flask-сервер в отдельном потоке"""
    threading.Thread(target=run_flask, daemon=True).start()

def keep_alive():
    """Самостоятельный пинг каждые 60 секунд"""
    def _ping():
        while True:
            time.sleep(60)
            try:
                requests.get('http://127.0.0.1:10000/')
            except:
                pass
    threading.Thread(target=_ping, daemon=True).start()
