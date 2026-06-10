FROM python:3.11-slim

# Работаем в /usr/src/app вместо /app
WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запускаем бота
CMD ["python", "bot.py"]
