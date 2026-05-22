# ==========================================
# Файл: web_server.py
# Задача: веб-морда для управления ботом, альтернатива телеграм-админке
# Комментарий: запускается отдельным потоком из bot.py через start_web_thread().
#              Предоставляет интерфейс для смены режимов, добавления цитат,
#              отправки постов в VK и просмотра логов. Требует пароль из ADMIN_PASSWORD.
# ==========================================

import os
import logging
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from threading import Thread
import uvicorn

logger = logging.getLogger(__name__)

app = FastAPI(title="Ансамбль Следов 6 — Веб-морда")

BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
TEMPLATES_DIR.mkdir(exist_ok=True)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

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

def check_auth(request: Request):
    global admin_session
    if admin_session:
        return True
    if request.query_params.get('password') == bot_handlers['admin_password']:
        admin_session = True
        return True
    raise HTTPException(status_code=401, detail="Не авторизован")

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

def run_web_server(host="0.0.0.0", port=8080):
    uvicorn.run(app, host=host, port=port, log_level="warning")

def start_web_thread(handlers_dict, host="0.0.0.0", port=8080):
    global bot_handlers
    bot_handlers.update(handlers_dict)
    thread = Thread(target=run_web_server, args=(host, port), daemon=True)
    thread.start()
    logger.info(f"Веб-морда запущена на http://{host}:{port}")
    return thread
