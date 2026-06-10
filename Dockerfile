FROM python:3.11-slim

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

# ПРИНУДИТЕЛЬНО копируем config.json в правильное место
# (твой код ищет его именно здесь)
COPY dialogue/data/config.json /app/dialogue/data/config.json

# Создаём символическую ссылку в корне (для старых обращений)
RUN ln -s /app/dialogue/data/config.json /app/config.json

# Запускаем бота
CMD ["python", "bot.py"]
