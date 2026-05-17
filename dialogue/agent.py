import requests
import json

CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def ask_agent(phrase):
    """Резервный агент (используется, если Алиса выключена или не отвечает)"""
    config = load_config()
    agent_url = config.get("agent", {}).get("url", "https://agent-3kek.onrender.com/ask")
    
    try:
        resp = requests.post(agent_url, json={"prompt": phrase}, timeout=15)
        if resp.status_code == 200:
            return resp.json().get("answer", "Ошибка: агент не вернул ответ")
        else:
            return f"Ошибка агента: статус {resp.status_code}"
    except Exception as e:
        return f"Ошибка связи с агентом: {e}"
