# ==========================================
# Файл: services/web_api/mail.py
# Справка: README.md → Веб-морда / API / Почта
# Задача: эндпоинты для работы с почтой
# Комментарий: использует gmail_client для чтения и отправки
# Зависит от: flask, services.gmail_client, debug_utils
# Вызывается из: web_api/__init__.py
# ==========================================

from flask import Blueprint, request, jsonify
from services.gmail_client import fetch_emails, send_email
from debug_utils import debug_log

mail_bp = Blueprint('mail', __name__)

def log_m(level, message):
    debug_log("WEB_API_MAIL", message, level)

@mail_bp.route('/inbox', methods=['GET'])
def inbox():
    return jsonify(fetch_emails(limit=10))

@mail_bp.route('/send', methods=['POST'])
def send():
    data = request.json
    to = data.get('to')
    subject = data.get('subject')
    body = data.get('body')
    if not to or not subject or not body:
        return jsonify({"error": "To, subject and body required"}), 400
    success = send_email(to, subject, body)
    if success:
        return jsonify({"status": "ok"})
    return jsonify({"error": "Failed to send email"}), 500
