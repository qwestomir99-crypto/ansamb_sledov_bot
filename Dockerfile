FROM python:3.11-slim

WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код
COPY . .

# !!! ЭТО ГЛАВНОЕ !!!
# Создаем символическую ссылку. Когда код обратится к /app/config.json,
# он будет автоматически перенаправлен на реальный файл в /app/dialogue/data/config.json
RUN ln -s /app/dialogue/data/config.json /app/config.json

# Запускаем бота
CMD ["python", "bot.py"]
