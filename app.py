import datetime
from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_traces_key_6'
# Настройка асинхронного режима для стабильной работы веб-сокетов
socketio = SocketIO(app, async_mode='gevent', cors_allowed_origins="*")

# Имитация внутренней базы данных бота
bot_state = {
    "mode": "день",
    "quotes": [
        "Ритм задает движение, следы оставляют историю.",
        "Тестовая цитата ансамбля №6."
    ]
}

# Встроенный HTML-шаблон (ваш интерфейс + исправленный скрипт)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Ансамбль Следов 6 — веб-морда</title>
    <!-- Подключаем Socket.io клиент для стабильной связи со смартфоном -->
    <script src="https://socket.io"></script>
    <style>
        * { box-sizing: border-box; }
        body {
            background: #0a0a0a;
            color: #00ffcc;
            font-family: 'Courier New', monospace;
            padding: 1rem;
            margin: 0;
        }
        .container { max-width: 900px; margin: 0 auto; }
        .card {
            background: #111;
            border-left: 3px solid #00ffcc;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 8px;
        }
        button, input, textarea, select {
            background: #222;
            color: #00ffcc;
            border: 1px solid #00ffcc;
            padding: 6px 12px;
            border-radius: 4px;
            font-family: inherit;
        }
        button:hover {
            background: #00ffcc;
            color: #000;
            cursor: pointer;
        }
        hr { border-color: #00ffcc33; }
        a { color: #00ffcc; }
        pre {
            background: #111;
            padding: 0.5rem;
            overflow-x: auto;
            font-size: 0.8rem;
        }
        .message-item {
            border-bottom: 1px solid #333;
            padding: 8px;
            margin-bottom: 5px;
        }
        .message-item.own {
            background-color: #1a3a3a;
            border-left: 2px solid #00ffcc;
        }
        #vk-messages {
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #00ffcc33;
            padding: 10px;
            margin-bottom: 10px;
        }
        .status-ok { color: #0f0; }
        .status-error { color: #f00; }
        .hidden { display: none; }
        .inline { display: inline-block; margin-left: 10px; }
    </style>
</head>
<body>
<div class="container">
    <h1>🔥 Ансамбль Следов 6</h1>
    <p>Ритм 0,8 Гц. Управление ботом из браузера. Время: {{ time }}</p>
    <p>
        <a href="/logs/admin">📋 admin.log</a> |
        <a href="/logs/error">❌ error.log</a>
    </p>

    <!-- Блок управления режимом -->
    <div class="card">
        <h2>🤖 Текущий режим: <strong id="current-mode">{{ mode }}</strong></h2>
        <form method="post" action="/set_mode" onsubmit="return false" id="mode-form">
            <select name="mode" id="mode-select">
                <option value="утро">🌅 Утро</option>
                <option value="день">☀️ День</option>
                <option value="вечер">🌙 Вечер</option>
                <option value="ночь">🌌 Ночь</option>
            </select>
            <button type="button" onclick="setMode()">Сменить режим</button>
        </form>
    </div>

    <!-- Блок добавления цитаты -->
    <div class="card">
        <h2>📜 Добавить цитату</h2>
        <form method="post" action="/add_quote" onsubmit="return false" id="quote-form">
            <textarea name="quote" id="quote-text" rows="2" cols="50" placeholder="Текст цитаты..."></textarea><br>
            <button type="button" onclick="addQuote()">➕ Добавить</button>
        </form>
        <details>
            <summary>📖 Последние цитаты (10)</summary>
            <ul id="quotes-list">
                {% for q in quotes %}
                    <li>{{ q[:100] }}{% if q|length > 100 %}...{% endif %}</li>
                {% else %}
                    <li>Нет цитат</li>
                {% endfor %}
            </ul>
        </details>
    </div>

    <!-- Блок поста в VK -->
    <div class="card">
        <h2>🎬 Пост в VK (текст)</h2>
        <form method="post" action="/vk_post" onsubmit="return false" id="vk-post-form">
            <textarea name="text" id="vk-post-text" rows="3" cols="50" placeholder="Текст поста..."></textarea><br>
            <button type="button" onclick="sendVkPost()">📤 Отправить</button>
        </form>
        <div id="vk-post-status" class="inline"></div>
    </div>

    <!-- Блок сообщений из VK -->
    <div class="card">
        <h2>💬 Входящие сообщения (VK)</h2>
        <div id="vk-messages">
            <div style="color: #666;">Сообщения будут появляться здесь...</div>
        </div>
        <div id="vk-reply-area" class="hidden">
            <textarea id="vk-reply-text" rows="2" cols="50" placeholder="Ваш ответ..."></textarea>
            <input type="hidden" id="vk-reply-peer">
            <button onclick="sendVkReply()">📤 Отправить ответ</button>
            <button onclick="closeVkReply()">❌ Отмена</button>
        </div>
    </div>
</div>

<script>
    let currentReplyPeer = null;
    let ws = null;
    let wsConnected = false;

    // Инициализация при загрузке страницы
    document.addEventListener("DOMContentLoaded", () => {
        connectWebSocket();
        fetchState();
    });

    // Изменение режима работы бота
    async function setMode() {
        const mode = document.getElementById("mode-select").value;
        try {
            const response = await fetch('/set_mode', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ mode })
            });
            const data = await response.json();
            document.getElementById("current-mode").innerText = data.mode;
        } catch (error) {
            console.error("Ошибка при смене режима:", error);
        }
    }

    // Добавление новой цитаты
    async function addQuote() {
        const quoteText = document.getElementById("quote-text").value;
        if (!quoteText.trim()) return alert("Текст цитаты пуст!");
        
        try {
            const response = await fetch('/add_quote', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ quote: quoteText })
            });
            const data = await response.json();
            
            document.getElementById("quote-text").value = '';
            if (data.quotes) {
                updateQuotesList(data.quotes);
            }
        } catch (error) {
            console.error("Ошибка при добавлении цитаты:", error);
        }
    }

    // Публикация нового поста в группу
    async function sendVkPost() {
        const text = document.getElementById("vk-post-text").value;
        const statusDiv = document.getElementById("vk-post-status");
        statusDiv.innerText = "Отправка...";
        statusDiv.className = "inline";

        try {
            const response = await fetch('/vk_post', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ text })
            });
            
            if (response.ok) {
                statusDiv.innerText = "Пост опубликован!";
                statusDiv.className = "inline status-ok";
                document.getElementById("vk-post-text").value = '';
            } else {
                statusDiv.innerText = "Ошибка отправки";
                statusDiv.className = "inline status-error";
            }
        } catch (error) {
            statusDiv.innerText = "Ошибка сети";
            statusDiv.className = "inline status-error";
        }
    }

    // Обновление раскрывающегося списка цитат на экране
    function updateQuotesList(quotes) {
        const list = document.getElementById("quotes-list");
        list.innerHTML = quotes.map(q => {
            const truncated = q.length > 100 ? q.substring(0, 100) + '...' : q;
            return `<li>${truncated}</li>`;
        }).join('') || '<li>Нет цитат</li>';
    }

    // Синхронизация состояния интерфейса с базой данных бэкенда
    async function fetchState() {
        try {
            const response = await fetch('/api/state');
            const data = await response.json();
            document.getElementById("current-mode").innerText = data.mode;
            if (data.quotes) updateQuotesList(data.quotes);
        } catch(e) { console.error(e); }
    }

    // Подключение к WebSocket каналу через библиотеку socket.io
    function connectWebSocket() {
        ws = io('/ws/messages');

        ws.on('connect', () => {
            wsConnected = true;
            console.log("WS соединение установлено");
        });

        ws.on('message', (data) => {
            appendMessage(data);
        });

        ws.on('disconnect', () => {
            wsConnected = false;
            console.log("WS соединение разорвано");
        });
    }

    // Отрисовка нового сообщения в ленте чата
    function appendMessage(msg) {
        const container = document.getElementById("vk-messages");
        if (container.querySelector("div[style*='color: #666']")) {
            container.innerHTML = '';
        }

        const div = document.createElement('div');
        div.className = `message-item ${msg.own ? 'own' : ''}`;
        div.innerHTML = `<strong>${msg.sender || 'Неизвестный'}:</strong> ${msg.text} <br>
                         <small>${msg.time || ''}</small>`;
        
        if (!msg.own) {
