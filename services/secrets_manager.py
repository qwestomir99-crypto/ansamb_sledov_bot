#!/usr/bin/env python3
# ==================================================
# @file: services/secrets_manager.py
# @author: Ансамбль Следов
# @version: 1.7
# @description:
#   Чтение зашифрованных секретов из SQLite.
# ==================================================

import os
import sqlite3
import base64
from cryptography.fernet import Fernet

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, 'data/ansambl.db')
KEY_PATH = os.path.join(PROJECT_ROOT, 'tools', 'encryption_key.txt')

class SecretsManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        if not os.path.exists(KEY_PATH):
            raise Exception(f"Ключ шифрования не найден: {KEY_PATH}")
        with open(KEY_PATH, 'r') as f:
            key = f.read().strip()
        if len(key) == 32 and not key.endswith('='):
            key = base64.urlsafe_b64encode(key.encode()).decode()
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
            encrypted = row[0]
            if isinstance(encrypted, str):
                encrypted = encrypted.encode()
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
            if isinstance(encrypted, str):
                encrypted = encrypted.encode()
            decrypted = self.cipher.decrypt(encrypted)
            result[key] = decrypted.decode()
        return result

secrets = SecretsManager()

def get_secret(key, default=None):
    value = secrets.get(key)
    return value if value is not None else default
