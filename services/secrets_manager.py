# ==================================================
# @file: services/secrets_manager.py
# @author: Ансамбль Следов
# @version: 1.0
# @description:
#   Чтение зашифрованных секретов из SQLite.
# ==================================================

import sqlite3
import os
from cryptography.fernet import Fernet

DB_PATH = 'data/ansambl.db'
KEY_FILE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/../encryption_key.txt'

class SecretsManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        if not os.path.exists(KEY_FILE):
            raise Exception(f"Ключ шифрования не найден: {KEY_FILE}")
        with open(KEY_FILE, 'r') as f:
            key = f.read().strip()
        self.cipher = Fernet(key.encode())
        
    def _get_connection(self):
        return sqlite3.connect(DB_PATH)
    
    def get(self, key):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("SELECT value FROM secrets WHERE key = ?", (key,))
        row = c.fetchone()
        conn.close()
        if row:
            encrypted = row[0].encode()
            decrypted = self.cipher.decrypt(encrypted)
            return decrypted.decode()
        return None
    
    def get_all(self):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("SELECT key, value FROM secrets")
        rows = c.fetchall()
        conn.close()
        result = {}
        for key, encrypted in rows:
            decrypted = self.cipher.decrypt(encrypted.encode())
            result[key] = decrypted.decode()
        return result

# Глобальный экземпляр
secrets = SecretsManager()

def get_secret(key, default=None):
    value = secrets.get(key)
    return value if value is not None else default
