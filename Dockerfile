# Базовый образ с Node.js
FROM node:20-slim

# Устанавливаем Python и pip
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем и устанавливаем зависимости для Node.js (если нужны)
COPY package*.json ./
RUN npm install

# Копируем и устанавливаем зависимости для Python
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

# Запускаем бота через Node.js обёртку
CMD ["node", "bot.js"]
