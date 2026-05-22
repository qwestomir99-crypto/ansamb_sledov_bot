# ==========================================
# Файл: services/web_server.py
# Задача: веб-морда (FastAPI) для новой админки
# Комментарий: слушает порт из переменной PORT (Render).
#              Маршрут /new отдаёт HTML из new_debugger/templates/admin.html
# ==========================================

import os
import sys
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

# Секретный ключ для сессий (из переменной окружения или стандартный)
SECRET_KEY = os.environ.get("WEB_SESSION_SECRET", "sapyor-tleem-fixiruem-0-8hz")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Пароль админа из переменной окружения
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "default123")

# ==========================================
# Вспомогательные функции
# ==========================================
def is_authenticated(request: Request) -> bool:
    """Проверяет, авторизован ли пользователь по сессии"""
    return request.session.get("authenticated", False)

# ==========================================
# Маршруты аутентификации
# ==========================================
@app.get("/")
async def root():
    """Корень — редирект на новую веб-морду"""
    return RedirectResponse(url="/new")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Страница входа с формой"""
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
    """Обработка формы входа"""
    if password == ADMIN_PASSWORD:
        request.session["authenticated"] = True
        return RedirectResponse(url="/new", status_code=303)
    else:
        return RedirectResponse(url="/login?error=1", status_code=303)

@app.get("/logout")
async def logout(request: Request):
    """Выход из системы"""
    request.session.clear()
    return RedirectResponse(url="/login")

# ==========================================
# Новая веб-морда (из new_debugger/templates/admin.html)
# ==========================================
@app.get("/new", response_class=HTMLResponse)
async def new_admin_panel(request: Request):
    """Новая веб-морда — предпросмотр из new_debugger/templates/admin.html"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login?error=1")
    
    # Ищем файл admin.html в new_debugger/templates/
    base_path = Path(__file__).parent.parent  # поднимаемся из services/ в корень
    html_path = base_path / "new_debugger" / "templates" / "admin.html"
    
    if not html_path.exists():
        return HTMLResponse(f"""
        <html>
            <body style="background:#0a0a0a; color:#ff4444; font-family:monospace; padding:2rem;">
                <h2>❌ admin.html не найден</h2>
                <p>Искали по пути: <code>{html_path}</code></p>
                <p>Текущая директория: <code>{Path.cwd()}</code></p>
                <p>Расположение web_server.py: <code>{Path(__file__).parent}</code></p>
                <hr>
                <p>Убедись, что файл существует:<br>
                <code>new_debugger/templates/admin.html</code></p>
                <a href="/logout">← Выйти</a>
            </body>
        </html>
        """, status_code=404)
    
    # Читаем HTML как статический файл
    html_content = html_path.read_text(encoding='utf-8')
    
    # Замена переменных Jinja2 на тестовые значения (потом подключишь реальные данные)
    html_content = html_content.replace("{{ mode }}", "🌙 режим (новая веб-морда)")
    html_content = html_content.replace("{{ time }}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    return HTMLResponse(html_content)

# ==========================================
# Health check для Render
# ==========================================
@app.get("/health")
async def health_check():
    """Для Render — проверка, что сервис жив"""
    return {"status": "ok", "service": "ansamb-sledov-web-morda"}

# ==========================================
# WebSocket (для будущих real-time обновлений)
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

# ==========================================
# Запуск сервера
# ==========================================
def run_web_server():
    """Запускает FastAPI на порту из переменной PORT"""
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")

def start_web_thread():
    """Запускает веб-сервер в отдельном потоке (из bot.py)"""
    thread = Thread(target=run_web_server, daemon=True)
    thread.start()
    print(f"[WEB] 🌐 Веб-морда запущена на порту {os.environ.get('PORT', 10000)}")
    return thread
