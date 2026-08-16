# ==========================================
# Файл: render_udp_tunnel.py (для Render)
# Справка: README.md → Туннель / UDP
# Задача: UDP-туннель (заготовка для AmneziaWG)
# Комментарий: проверяет поддержку UDP/HTTP3 на Render
# Зависит от: flask, socket
# Вызывается из: bot.py (Render)
# Версия: 1.0 — разведка UDP-прохода
# ==========================================

import socket
from flask import jsonify

def register_udp_tunnel(app):
    
    @app.route('/udp_test', methods=['GET'])
    def udp_test():
        """Проверяет, доступен ли UDP наружу"""
        result = {
            'udp_available': False,
            'note': 'Render обычно режет UDP на уровне PaaS'
        }
        
        # Пробуем открыть UDP-сокет
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(2)
            # Пробуем достучаться до публичного DNS
            s.sendto(b'\x00' * 8, ('8.8.8.8', 53))
            try:
                data, addr = s.recvfrom(512)
                result['udp_available'] = True
                result['note'] = 'UDP работает'
            except socket.timeout:
                result['note'] = 'UDP уходит, но ответ не пришёл'
            s.close()
        except Exception as e:
            result['note'] = f'UDP недоступен: {e}'
        
        return jsonify(result)
    
    print('[UDP_TUNNEL] UDP-туннель зарегистрирован')
