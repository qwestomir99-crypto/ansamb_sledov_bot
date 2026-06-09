# Берём за основу официальный образ Python
FROM python:3.11-slim

# Указываем рабочую папку внутри контейнера
WORKDIR /app

# Копируем список с зависимостями и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код в папку /app
COPY . .

# Запускаем бота
CMD ["python", "bot.py"]
