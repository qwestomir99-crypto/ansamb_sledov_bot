# ==========================================
# Файл: render_ws_tunnel.py (для Render)
# Справка: README.md → Туннель / WebSocket
# Задача: WebSocket-туннель для SOCKS5-подобного прокси
# Комментарий: проверяет, что Cloudflare пропускает WebSocket
# Зависит от: flask_socketio, requests
# Вызывается из: bot.py (Render)
# Версия: 1.0 — разведка WebSocket-прохода
# ==========================================

import requests
from flask_socketio import SocketIO, emit

def register_ws_tunnel(app):
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    @socketio.on('connect')
    def handle_connect():
        print('[WS_TUNNEL] Клиент подключился')
        emit('status', {'message': 'connected'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print('[WS_TUNNEL] Клиент отключился')
    
    @socketio.on('proxy_request')
    def handle_proxy(data):
        url = data.get('url', '')
        method = data.get('method', 'GET').upper()
        
        print(f'[WS_TUNNEL] Запрос: {method} {url[:80]}')
        
        try:
            if method == 'GET':
                r = requests.get(url, timeout=20, headers={'User-Agent': 'Mozilla/5.0'})
            elif method == 'POST':
                r = requests.post(url, data=data.get('body', {}), timeout=20)
            else:
                r = requests.get(url, timeout=20)
            
            emit('proxy_response', {
                'status': r.status_code,
                'headers': dict(r.headers),
                'content': r.text[:10000]
            })
        except Exception as e:
            emit('proxy_response', {
                'status': 0,
                'error': str(e)
            })
    
    print('[WS_TUNNEL] WebSocket-туннель зарегистрирован')
    return socketio
