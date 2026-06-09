FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Проверяем, существует ли реальный config.json
RUN if [ -f /app/dialogue/data/config.json ]; then \
        echo "✅ config.json найден, создаю ссылку..."; \
        ln -s /app/dialogue/data/config.json /app/config.json; \
    else \
        echo "❌ config.json НЕ НАЙДЕН по пути /app/dialogue/data/config.json"; \
        exit 1; \
    fi

CMD ["python", "bot.py"]
