# ==========================================
# Файл: login_auth/SecureSecrets.py
# Задача: заглушка для Render
# ==========================================

import os
import requests

class SecureSecrets:
    def __init__(self):
        self.base_url = os.getenv("MAIN_SITE_URL", "https://ch756438.tw1.ru")

    def get(self, key, default=None):
        try:
            url = f"{self.base_url}/api/secret/{key}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get("value", default)
        except:
            pass
        return default
