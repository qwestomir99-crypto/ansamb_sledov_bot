FROM python:3.11-slim

WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

# ==========================================
# ДИАГНОСТИКА: проверяем, что попало в контейнер
# ==========================================
RUN echo "=== СОДЕРЖИМОЕ /app ===" && ls -la /app
RUN echo "=== СОДЕРЖИМОЕ /app/dialogue ===" && ls -la /app/dialogue || echo "Папка dialogue отсутствует"
RUN echo "=== СОДЕРЖИМОЕ /app/dialogue/data ===" && ls -la /app/dialogue/data || echo "Папка dialogue/data отсутствует"
# ==========================================

# ПРИНУДИТЕЛЬНО копируем config.json (если есть в репозитории)
COPY dialogue/data/config.json /app/dialogue/data/config.json

# Создаём символическую ссылку в корне для старых обращений
RUN ln -s /app/dialogue/data/config.json /app/config.json

# Запускаем бота
CMD ["python", "bot.py"]
