# ==========================================
# Файл: web_server.py
# Задача: веб-морда для управления ботом и проброс сообщений из VK
# Комментарий: запускается отдельным потоком из bot.py.
#              Аутентификация через форму логина (пароль в URL не нужен).
#              Сессия хранится в куках.
#              Добавлен маршрут /new для предпросмотра новой веб-морды из new_debugger.
# ==========================================

import os
import logging
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from threading import Thread
import uvicorn
from fastapi import FastAPI, Request, Form, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

logger = logging.getLogger(__name__)

app = FastAPI(title="Ансамбль Следов 6 — Веб-морда")

# Секретный ключ для сессий
SECRET_KEY = os.environ.get("WEB_SESSION_SECRET", "sapyor-tleem-fixiruem-0-8hz")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
TEMPLATES_DIR.mkdir(exist_ok=True)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# ==========================================
# Хранилище сообщений и WebSocket-соединений
# ==========================================
_active_websockets: List[WebSocket] = []
_pending_messages: List[Dict] = []

# ==========================================
# Обработчики бота (заполняются из bot.py)
# ==========================================
bot_handlers = {
    'get_mode': None,
    'set_mode': None,
    'get_quotes': None,
    'add_quote': None,
    'get_posts': None,
    'add_post': None,
    'vk_post': None,
    'get_admin_log': None,
    'get_error_log': None,
    'admin_password': os.environ.get('ADMIN_PASSWORD', 'default123')
}

# ==========================================
# Проверка аутентификации через сессию
# ==========================================
def is_authenticated(request: Request) -> bool:
    return request.session.get("authenticated", False)

def require_auth(request: Request):
    if not is_authenticated(request):
        raise HTTPException(status_code=302, headers={"Location": "/login"})

# ==========================================
# Страницы аутентификации (старая версия)
# ==========================================
@app.get("/")
async def root():
    return RedirectResponse(url="/login")

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")
    
    mode = bot_handlers['get_mode']() if bot_handlers['get_mode'] else "неизвестно"
    quotes = bot_handlers['get_quotes']() if bot_handlers['get_quotes'] else []
    posts = bot_handlers['get_posts']() if bot_handlers['get_posts'] else []
    
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "mode": mode,
        "quotes": quotes[:10],
        "posts": posts,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if is_authenticated(request):
        return RedirectResponse(url="/admin")
    
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Вход — Ансамбль Следов 6</title>
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
                padding: 1rem;
            }
            .login-card {
                background: #111;
                border-left: 3px solid #00ffcc;
                padding: 2rem;
                border-radius: 8px;
                max-width: 400px;
                width: 100%;
            }
            h2 {
                margin-top: 0;
            }
            input {
                background: #222;
                color: #00ffcc;
                border: 1px solid #00ffcc;
                padding: 8px 12px;
                border-radius: 4px;
                width: 100%;
                margin: 10px 0;
                font-family: inherit;
                box-sizing: border-box;
            }
            button {
                background: #222;
                color: #00ffcc;
                border: 1px solid #00ffcc;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                font-family: inherit;
                width: 100%;
            }
            button:hover {
                background: #00ffcc;
                color: #000;
            }
            .error {
                color: #ff4444;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <div class="login-card">
            <h2>🔐 Вход в веб-морду</h2>
            <form method="post" action="/login">
                <input type="password" name="password" placeholder="Админ-пароль" autofocus>
                <button type="submit">Войти</button>
            </form>
            <div id="error" class="error"></div>
        </div>
        <script>
            const params = new URLSearchParams(window.location.search);
            if (params.get('error')) {
                document.getElementById('error').innerText = 'Неверный пароль';
            }
        </script>
    </body>
    </html>
    """

@app.post("/login")
async def login(request: Request, password: str = Form(...)):
    if password == bot_handlers['admin_password']:
        request.session["authenticated"] = True
        return RedirectResponse(url="/admin", status_code=303)
    else:
        return RedirectResponse(url="/login?error=1", status_code=303)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login")

# ==========================================
# НОВЫЙ МАРШРУТ: предпросмотр новой веб-морды из new_debugger
# ==========================================
@app.get("/new", response_class=HTMLResponse)
async def new_admin_preview(request: Request):
    """
    Временный доступ к новой веб-морде из папки new_debugger/templates/
    """
    if not is_authenticated(request):
        return RedirectResponse(url="/login?error=1")
    
    # Путь к шаблонам новой версии
    new_templates_dir = BASE_DIR / "new_debugger" / "templates"
    
    if not new_templates_dir.exists():
        return HTMLResponse("""
        <html>
            <body style="background:#0a0a0a; color:#ff4444; font-family:monospace; padding:2rem;">
                <h2>❌ Ошибка</h2>
                <p>Папка new_debugger/templates/ не найдена.</p>
                <p>Убедись, что файл admin.html лежит по пути:</p>
                <pre>new_debugger/templates/admin.html</pre>
                <a href="/admin">← Вернуться к старой админке</a>
            </body>
        </html>
        """, status_code=404)
    
    new_templates = Jinja2Templates(directory=str(new_templates_dir))
    
    # Временно передаём заглушки для данных
    # (потом заменишь на реальные обработчики)
    mode = "тестовый режим"
    quotes = [
        "«Сеть тлеет. Ритм 0,8 Гц.»",
        "«Сапёр аутентичности на связи.»",
        "«Ты — тень. Бот — голос.»"
    ]
    posts = []
    
    return new_templates.TemplateResponse("admin.html", {
        "request": request,
        "mode": mode,
        "quotes": quotes,
        "posts": posts,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# ==========================================
# API для управления ботом (с защитой)
# ==========================================
@app.post("/set_mode")
async def set_mode_endpoint(request: Request, mode: str = Form(...)):
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    if bot_handlers['set_mode']:
        bot_handlers['set_mode'](mode)
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/add_quote")
async def add_quote_endpoint(request: Request, quote: str = Form(...)):
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    if bot_handlers['add_quote']:
        bot_handlers['add_quote'](quote)
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/vk_post")
async def vk_post_endpoint(request: Request, text: str = Form(...)):
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    if bot_handlers['vk_post']:
        bot_handlers['vk_post'](text)
    return RedirectResponse(url="/admin", status_code=303)

# ==========================================
# Логи (с защитой)
# ==========================================
@app.get("/logs/admin")
async def admin_log(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")
    log_path = BASE_DIR / "admin.log"
    content = log_path.read_text(encoding='utf-8', errors='ignore')[-5000:] if log_path.exists() else "Лог не найден"
    return HTMLResponse(f"<pre style='background:#111; color:#0f0; padding:1rem; overflow:auto'>{content}</pre>")

@app.get("/logs/error")
async def error_log(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")
    log_path = BASE_DIR / "error.log"
    content = log_path.read_text(encoding='utf-8', errors='ignore')[-5000:] if log_path.exists() else "Лог не найден"
    return HTMLResponse(f"<pre style='background:#111; color:#f00; padding:1rem; overflow:auto'>{content}</pre>")

# ==========================================
# WebSocket (без аутентификации для простоты)
# ==========================================
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    _active_websockets.append(websocket)
    
    for msg in _pending_messages[-50:]:
        try:
            await websocket.send_json({"type": "history", "data": msg})
        except:
            pass
    
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        if websocket in _active_websockets:
            _active_websockets.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket ошибка: {e}")
        if websocket in _active_websockets:
            _active_websockets.remove(websocket)

def broadcast_vk_message(message: Dict):
    _pending_messages.append(message)
    if len(_pending_messages) > 1000:
        _pending_messages.pop(0)
    
    for ws in _active_websockets.copy():
        try:
            import asyncio
            asyncio.create_task(ws.send_json({
                "type": "new_message",
                "data": message
            }))
        except Exception as e:
            logger.error(f"Ошибка отправки через WebSocket: {e}")

# ==========================================
# REST API для сообщений VK (с защитой)
# ==========================================
@app.get("/api/vk/messages")
async def get_vk_messages(request: Request, limit: int = 50):
    if not is_authenticated(request):
        return {"error": "unauthorized"}
    return {"messages": _pending_messages[-limit:]}

@app.post("/api/vk/send")
async def send_vk_message_api(request: Request, data: dict):
    if not is_authenticated(request):
        return {"error": "unauthorized"}
    
    from services.vk_reader import send_vk_message
    vk_token = os.environ.get("VK_TOKEN")
    if not vk_token:
        return {"status": "error", "message": "VK_TOKEN не задан"}
    
    peer_id = data.get("peer_id")
    text = data.get("message")
    
    if not peer_id or not text:
        return {"status": "error", "message": "peer_id и message обязательны"}
    
    success = send_vk_message(vk_token, peer_id, text)
    if success:
        return {"status": "ok"}
    else:
        return {"status": "error", "message": "Ошибка отправки"}

# ==========================================
# Запуск сервера
# ==========================================
def run_web_server(host="0.0.0.0", port=10000):
    uvicorn.run(app, host=host, port=port, log_level="warning")

def start_web_thread(handlers_dict, host="0.0.0.0", port=10000):
    global bot_handlers
    bot_handlers.update(handlers_dict)
    thread = Thread(target=run_web_server, args=(host, port), daemon=True)
    thread.start()
    logger.info(f"🌐 Веб-морда запущена на http://{host}:{port}")
    return thread
