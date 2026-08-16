# ==========================================
# Файл: render_http_tunnel.py (для Render)
# Справка: README.md → Туннель / HTTP
# Задача: HTTP CONNECT-туннель (простой прокси)
# Комментарий: работает уже сейчас через /youtube?url=
# Зависит от: flask, requests
# Вызывается из: bot.py (Render)
# Версия: 1.0 — HTTP-прокси для статики и API
# ==========================================

import requests
from flask import request, Response

def register_http_tunnel(app):
    
    @app.route('/proxy', methods=['GET', 'POST'])
    def proxy():
        url = request.args.get('url') or request.json.get('url', '')
        
        if not url:
            return 'No url', 400
        
        print(f'[HTTP_TUNNEL] Проксирую: {url[:80]}')
        
        try:
            if request.method == 'POST':
                r = requests.post(url, json=request.json.get('body', {}), timeout=20)
            else:
                r = requests.get(url, timeout=20, headers={'User-Agent': 'Mozilla/5.0'})
            
            return Response(r.content, status=r.status_code, content_type=r.headers.get('Content-Type', 'text/html'))
        except Exception as e:
            return f'Proxy error: {e}', 500
    
    print('[HTTP_TUNNEL] HTTP-туннель зарегистрирован')
