# dialogue/agent.py
import requests
import random
import json

AGENT_URL = "https://agent-3kek.onrender.com/ask"

def ask_agent(phrase: str) -> str:
    """Отправляет запрос моему агенту"""
    if not phrase:
        return random.choice(["👁️", "⏚"])

    try:
        resp = requests.post(AGENT_URL, json={"prompt": phrase}, timeout=20)
        if resp.status_code == 200:
            return resp.json().get("answer", "Ошибка: агент не вернул ответ")
        elif resp.status_code == 502:
            return random.choice(["Связь с агентом прервана. Жду сигнала...", "Тишина в эфире..."])
        else:
            return f"Ошибка агента: статус {resp.status_code}"
    except requests.exceptions.Timeout:
        return random.choice(["Агент думает слишком долго...", "Повтори позже, ритм сбился"])
    except Exception as e:
        return f"Ошибка связи с агентом: {e}"
