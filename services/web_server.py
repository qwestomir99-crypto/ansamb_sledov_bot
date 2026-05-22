# ==========================================
# Файл: services/web_server.py
# Задача: два сервера — старый Flask (keep-alive) и новый FastAPI (веб-морда)
# Комментарий: Flask на порту 10000 (для Render), FastAPI на порту 8080 (для новой веб-морды).
#              Маршрут /new на FastAPI отдаёт новую админку из new_debugger/templates/
# ==========================================

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from threading import Thread
import uvicorn
from flask import Flask, request

# ==========================================
# СТАРЫЙ FLASK-СЕРВЕР (порт 10000)
# ==========================================
flask_app = Flask(__name__)
TOKEN = os.environ.get("BOT_TOKEN")

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
    return TOKEN, 200

@flask_app.route('/ping', methods=['GET'])
def ping():
    return "pong", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port, debug=False)

# ==========================================
# НОВЫЙ FASTAPI-СЕРВЕР (порт 8080)
# ==========================================
from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

fastapi_app = FastAPI(title="Ансамбль Следов 6 — Новая веб-морда")

# Секретный ключ для сессий
SECRET_KEY = os.environ.get("WEB_SESSION_SECRET", "sapyor-tleem-fixiruem-0-8hz")
fastapi_app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

BASE_DIR = Path(__file__).parent.parent

# ==========================================
# Аутентификация для FastAPI
# ==========================================
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "default123")

def is_authenticated(request: Request) -> bool:
    return request.session.get("authenticated", False)

# ==========================================
# Страницы FastAPI
# ==========================================
@fastapi_app.get("/")
async def root():
    return RedirectResponse(url="/new")

@fastapi_app.get("/new", response_class=HTMLResponse)
async def new_admin_preview(request: Request):
    """Предпросмотр новой веб-морды из папки new_debugger/templates/"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login?error=1")
    
    # Ищем файл admin.html
    possible_paths = [
        Path("new_debugger/templates/admin.html"),
        Path(__file__).parent.parent / "new_debugger" / "templates" / "admin.html",
        Path.cwd() / "new_debugger" / "templates" / "admin.html",
    ]
    
    found_path = None
    for path in possible_paths:
        if path.exists():
            found_path = path
            break
    
    if not found_path:
        return HTMLResponse(f"""
        <html>
            <body style="background:#0a0a0a; color:#ff4444; font-family:monospace; padding:2rem;">
                <h2>❌ admin.html не найден</h2>
                <p>Искали по путям:</p>
                <ul>
                    {''.join(f'<li>{p}</li>' for p in possible_paths)}
                </ul>
                <p>Текущая директория: {Path.cwd()}</p>
                <a href="/login">← Выйти</a>
            </body>
        </html>
        """, status_code=404)
    
    html_content = found_path.read_text(encoding='utf-8')
    
    # Замена переменных
    html_content = html_content.replace("{{ mode }}", "🌙 тестовый режим (новая веб-морда)")
    html_content = html_content.replace("{{ time }}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    return HTMLResponse(html_content)

@fastapi_app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if is_authenticated(request):
        return RedirectResponse(url="/new")
    
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Вход — новая веб-морда</title>
        <style>
            body {
                background: #0a0a0a;
                color: #00ffcc;
                font-family: 'Courier New', monospace;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .card {
                background: #111;
                border-left: 3px solid #00ffcc;
                padding: 2rem;
                border-radius: 8px;
            }
            input, button {
                background: #222;
                color: #00ffcc;
                border: 1px solid #00ffcc;
                padding: 8px 12px;
                margin: 10px 0;
                font-family: inherit;
            }
            button:hover {
                background: #00ffcc;
                color: #000;
                cursor: pointer;
            }
            .error { color: #ff4444; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🔐 Вход</h2>
            <form method="post" action="/login">
                <input type="password" name="password" placeholder="Админ-пароль">
                <button type="submit">Войти</button>
            </form>
            <div class="error"></div>
        </div>
        <script>
            const params = new URLSearchParams(window.location.search);
            if (params.get('error')) {
                document.querySelector('.error').innerText = 'Неверный пароль';
            }
        </script>
    </body>
    </html>
    """

@fastapi_app.post("/login")
async def login(request: Request, password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        request.session["authenticated"] = True
        return RedirectResponse(url="/new", status_code=303)
    else:
        return RedirectResponse(url="/login?error=1", status_code=303)

@fastapi_app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login")

# ==========================================
# WebSocket для новой веб-морды
# ==========================================
_active_websockets: List[WebSocket] = []

@fastapi_app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    _active_websockets.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        _active_websockets.remove(websocket)

def broadcast_vk_message(message: Dict):
    for ws in _active_websockets.copy():
        try:
            import asyncio
            asyncio.create_task(ws.send_json({"type": "new_message", "data": message}))
        except:
            pass

# ==========================================
# Запуск FastAPI в отдельном потоке
# ==========================================
def run_fastapi():
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8080, log_level="warning")

def start_fastapi_thread():
    thread = Thread(target=run_fastapi, daemon=True)
    thread.start()
    print("[WEB] 🌐 Новая веб-морда (FastAPI) запущена на порту 8080")
    return thread
