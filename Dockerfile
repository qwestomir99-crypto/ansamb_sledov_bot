# Используем официальный образ Node.js
FROM node:20-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем package.json и устанавливаем зависимости (если появятся)
COPY package*.json ./
RUN npm install

# Копируем всё остальное
COPY . .

# Запускаем бота через Node.js
CMD ["node", "bot.js"]
