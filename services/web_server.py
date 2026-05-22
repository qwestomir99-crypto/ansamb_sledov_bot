# ==========================================
# Файл: services/web_server.py
# Задача: веб-морда (FastAPI) — единый сервер
# Комментарий: слушает порт из переменной PORT.
#              Маршрут /new отдаёт HTML из new_debugger/templates/admin.html
#              Добавлены /health, /token, /ping для обратной совместимости
# ==========================================

import os
from datetime import datetime
from pathlib import Path
from threading import Thread
from typing import List, Dict

import uvicorn
from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

# ==========================================
# Инициализация FastAPI
# ==========================================
app = FastAPI(title="Ансамбль Следов 6 — Веб-морда")

# Секретный ключ для сессий
SECRET_KEY = os.environ.get("WEB_SESSION_SECRET", "sapyor-tleem-fixiruem-0-8hz")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Пароль админа
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "default123")
TOKEN = os.environ.get("BOT_TOKEN", "")
TOKEN_SECRET = os.environ.get("TOKEN_SECRET", "tleem2026")

# ==========================================
# Вспомогательные функции
# ==========================================
def is_authenticated(request: Request) -> bool:
    return request.session.get("authenticated", False)

# ==========================================
# Маршруты аутентификации
# ==========================================
@app.get("/")
async def root():
    return RedirectResponse(url="/new")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if is_authenticated(request):
        return RedirectResponse(url="/new")
    
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
            h2 { margin-top: 0; }
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
            .error { color: #ff4444; margin-top: 10px; }
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
    if password == ADMIN_PASSWORD:
        request.session["authenticated"] = True
        return RedirectResponse(url="/new", status_code=303)
    else:
        return RedirectResponse(url="/login?error=1", status_code=303)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login")

# ==========================================
# Новая веб-морда (из new_debugger/templates/admin.html)
# ==========================================
@app.get("/new", response_class=HTMLResponse)
async def new_admin_panel(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/login?error=1")
    
    # Ищем файл admin.html
    base_path = Path(__file__).parent.parent
    html_path = base_path / "new_debugger" / "templates" / "admin.html"
    
    if not html_path.exists():
        return HTMLResponse(f"""
        <html>
            <body style="background:#0a0a0a; color:#ff4444; font-family:monospace; padding:2rem;">
                <h2>❌ admin.html не найден</h2>
                <p>Искали: <code>{html_path}</code></p>
                <p>Текущая директория: <code>{Path.cwd()}</code></p>
                <a href="/logout">← Выйти</a>
            </body>
        </html>
        """, status_code=404)
    
    html_content = html_path.read_text(encoding='utf-8')
    
    # Замена переменных
    html_content = html_content.replace("{{ mode }}", "🌙 новая веб-морда")
    html_content = html_content.replace("{{ time }}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    return HTMLResponse(html_content)

# ==========================================
# Health check для Render
# ==========================================
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "ansamb-sledov-bot", "rhythm": "0.8 Hz"}

# ==========================================
# /token — для внешних сервисов
# ==========================================
@app.get("/token")
async def get_token(secret: str = None):
    if secret != TOKEN_SECRET:
        return {"error": "Forbidden"}, 403
    return {"token": TOKEN}

# ==========================================
# /ping — для проверки доступности
# ==========================================
@app.get("/ping")
async def ping():
    return {"status": "pong", "timestamp": datetime.now().isoformat()}

# ==========================================
# WebSocket (для real-time обновлений)
# ==========================================
_active_websockets: List[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    _active_websockets.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        if websocket in _active_websockets:
            _active_websockets.remove(websocket)

def broadcast_vk_message(message: Dict):
    for ws in _active_websockets.copy():
        try:
            import asyncio
            asyncio.create_task(ws.send_json({"type": "new_message", "data": message}))
        except:
            pass

# ==========================================
# Запуск сервера
# ==========================================
def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")

def start_web_thread():
    thread = Thread(target=run_web_server, daemon=True)
    thread.start()
    port = os.environ.get("PORT", 10000)
    print(f"[WEB] 🌐 Веб-морда запущена на порту {port}")
    return thread
