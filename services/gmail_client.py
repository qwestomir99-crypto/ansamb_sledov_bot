# ==========================================
# Файл: services/gmail_client.py
# Справка: README.md → Почта / Клиент
# Задача: подключение к Gmail через IMAP и SMTP
# Комментарий: использует переменные окружения
# Зависит от: os, imaplib, smtplib, email, debug_utils
# Вызывается из: services.web_api.mail
# ==========================================

import os
import imaplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
from datetime import datetime
from debug_utils import debug_log

GMAIL_EMAIL = os.environ.get("GMAIL_EMAIL")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

IMAP_SERVER = "imap.gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def log_gm(level, message):
    debug_log("GMAIL_CLIENT", message, level)

def connect_imap():
    """Подключается к Gmail через IMAP"""
    if not GMAIL_EMAIL or not GMAIL_APP_PASSWORD:
        log_gm("ERROR", "Не заданы GMAIL_EMAIL или GMAIL_APP_PASSWORD")
        return None
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
        mail.select("INBOX")
        log_gm("INFO", "Подключено к IMAP")
        return mail
    except Exception as e:
        log_gm("ERROR", f"Ошибка подключения IMAP: {e}")
        return None

def connect_smtp():
    """Подключается к Gmail через SMTP"""
    if not GMAIL_EMAIL or not GMAIL_APP_PASSWORD:
        log_gm("ERROR", "Не заданы GMAIL_EMAIL или GMAIL_APP_PASSWORD")
        return None
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
        log_gm("INFO", "Подключено к SMTP")
        return server
    except Exception as e:
        log_gm("ERROR", f"Ошибка подключения SMTP: {e}")
        return None

def fetch_emails(limit=10):
    """Забирает последние limit писем из INBOX"""
    mail = connect_imap()
    if not mail:
        return []
    try:
        mail.select("INBOX")
        _, data = mail.search(None, "ALL")
        ids = data[0].split()
        # Берём последние limit писем
        email_ids = ids[-limit:]
        emails = []
        for eid in email_ids:
            _, data = mail.fetch(eid, "(RFC822)")
            email_data = data[0][1]
            import email
            msg = email.message_from_bytes(email_data)
            emails.append({
                "id": eid.decode(),
                "from": msg.get("From"),
                "subject": msg.get("Subject"),
                "date": msg.get("Date"),
                "body": msg.get_payload(decode=True).decode(errors="ignore")[:200]
            })
        mail.logout()
        return emails
    except Exception as e:
        log_gm("ERROR", f"Ошибка получения писем: {e}")
        return []

def send_email(to, subject, body):
    """Отправляет письмо через SMTP"""
    server = connect_smtp()
    if not server:
        return False
    try:
        msg = MIMEMultipart()
        msg["From"] = formataddr(("Ансамбль Следов 6", GMAIL_EMAIL))
        msg["To"] = to
        msg["Subject"] = Header(subject, "utf-8")
        msg.attach(MIMEText(body, "plain", "utf-8"))
        server.send_message(msg)
        server.quit()
        log_gm("INFO", f"Письмо отправлено {to}")
        return True
    except Exception as e:
        log_gm("ERROR", f"Ошибка отправки письма: {e}")
        return False
