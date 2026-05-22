# ==========================================
# Файл: web_server.py
# Задача: веб-морда для управления ботом и проброс сообщений из VK
# Комментарий: запускается отдельным потоком из bot.py.
#              Предоставляет:
#              - админ-панель для смены режимов, добавления цитат, постов в VK
#              - WebSocket для реального времени (новые сообщения из VK)
#              - REST API для отправки ответов и получения истории
#              Требует пароль из переменной окружения ADMIN_PASSWORD.
# ==========================================

import os
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from threading import Thread
import uvicorn
from fastapi import FastAPI, Request, Form, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger(__name__)

app = FastAPI(title="Ансамбль Следов 6 — Веб-морда")

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

admin_session = False

# ==========================================
# Аутентификация
# ==========================================
def check_auth(request: Request):
    global admin_session
    if admin_session:
        return True
    if request.query_params.get('password') == bot_handlers['admin_password']:
        admin_session = True
        return True
    raise HTTPException(status_code=401, detail="Не авторизован")

# ==========================================
# Веб-интерфейс
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def admin_panel(request: Request, password: str = None):
    global admin_session
    if password == bot_handlers['admin_password']:
        admin_session = True
    if not admin_session:
        return HTMLResponse("""
        <html>
            <body style="background:#0a0a0a; color:#00ffcc; font-family:monospace; padding:2rem;">
                <h2>🔐 Вход в веб-морду</h2>
                <form method="get">
                    <input type="password" name="password" placeholder="Админ-пароль" style="padding:8px; width:200px;">
                    <button type="submit">Войти</button>
                </form>
            </body>
        </html>
        """, status_code=401)
    
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

# ==========================================
# API для управления ботом
# ==========================================
@app.post("/set_mode")
async def set_mode(mode: str = Form(...), _=Depends(check_auth)):
    if bot_handlers['set_mode']:
        bot_handlers['set_mode'](mode)
    return RedirectResponse(url="/", status_code=303)

@app.post("/add_quote")
async def add_quote(quote: str = Form(...), _=Depends(check_auth)):
    if bot_handlers['add_quote']:
        bot_handlers['add_quote'](quote)
    return RedirectResponse(url="/", status_code=303)

@app.post("/vk_post")
async def vk_post(text: str = Form(...), _=Depends(check_auth)):
    if bot_handlers['vk_post']:
        bot_handlers['vk_post'](text)
    return RedirectResponse(url="/", status_code=303)

# ==========================================
# Логи
# ==========================================
@app.get("/logs/admin")
async def admin_log(_=Depends(check_auth)):
    log_path = BASE_DIR / "admin.log"
    content = log_path.read_text(encoding='utf-8', errors='ignore')[-5000:] if log_path.exists() else "Лог не найден"
    return HTMLResponse(f"<pre style='background:#111; color:#0f0; padding:1rem; overflow:auto'>{content}</pre>")

@app.get("/logs/error")
async def error_log(_=Depends(check_auth)):
    log_path = BASE_DIR / "error.log"
    content = log_path.read_text(encoding='utf-8', errors='ignore')[-5000:] if log_path.exists() else "Лог не найден"
    return HTMLResponse(f"<pre style='background:#111; color:#f00; padding:1rem; overflow:auto'>{content}</pre>")

# ==========================================
# WebSocket для real-time сообщений
# ==========================================
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket для получения новых сообщений из VK в реальном времени"""
    await websocket.accept()
    _active_websockets.append(websocket)
    
    # Отправляем последние 50 сообщений при подключении
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
            elif data.startswith("read:"):
                # Можно добавить логику отметки прочитанного
                pass
    except WebSocketDisconnect:
        if websocket in _active_websockets:
            _active_websockets.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket ошибка: {e}")
        if websocket in _active_websockets:
            _active_websockets.remove(websocket)

def broadcast_vk_message(message: Dict):
    """Широковещательная рассылка нового сообщения всем веб-мордам"""
    # Добавляем в очередь
    _pending_messages.append(message)
    if len(_pending_messages) > 1000:
        _pending_messages.pop(0)
    
    # Отправляем всем активным соединениям
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
# REST API для сообщений VK
# ==========================================
@app.get("/api/vk/messages")
async def get_vk_messages(limit: int = 50, _=Depends(check_auth)):
    """Получить историю сообщений из VK"""
    return {"messages": _pending_messages[-limit:]}

@app.post("/api/vk/send")
async def send_vk_message_api(data: dict, _=Depends(check_auth)):
    """Отправить ответ в VK от имени сообщества"""
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
def run_web_server(host="0.0.0.0", port=8080):
    """Запуск FastAPI сервера"""
    uvicorn.run(app, host=host, port=port, log_level="warning")

def start_web_thread(handlers_dict, host="0.0.0.0", port=8080):
    """Интеграция с ботом: передаём функции-обработчики и запускаем поток"""
    global bot_handlers
    bot_handlers.update(handlers_dict)
    thread = Thread(target=run_web_server, args=(host, port), daemon=True)
    thread.start()
    logger.info(f"Веб-морда запущена на http://{host}:{port}")
    return thread
