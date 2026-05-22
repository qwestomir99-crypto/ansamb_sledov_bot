# Ансамбль Следов 6

**Ритм 0,8 Гц. Сеть тлеет.**

Бот для автопостинга, публикации цитат, аналитики и управления контентом в Telegram и VK.

---

## 📡 Архитектура

| Модуль | Файл | Что делает |
|--------|------|-------------|
| **Бот** | `bot.py` | Главный поток. Запускает все сервисы, обрабатывает команды. |
| **Настройки** | `settings.py` | Флаги включения/выключения модулей. |
| **Цитаты** | `dialogue/quotes.py` | Публикует цитаты из `dialogue/data/quotes.txt` по расписанию. |
| **Публикатор** | `dialogue/publisher.py` | Публикует посты из `post_pool.json` в канал и VK с учётом режима дня. |
| **Пост в VK** | `dialogue/admin_commands.py` | Кнопка в админке для отправки текста, фото и видео в VK. |
| **Аналитика** | `tag_analyzer.py` | Собирает статистику по тегам, экспортирует в CSV/JSON. |
| **GitHub Actions** | `.github/workflows/analytics.yml` | Ежедневный запуск аналитики и отправка отчёта в Telegram. |
| **Агент** | `dialogue/agent.py` | Отвечает на `#говори` через внешний API. |
| **Режимы** | `dialogue/activity_modes.py` | Управляет режимами утро/день/вечер/ночь. |
| **Админка** | `dialogue/admin_commands.py` | Меню, кнопки, управление цитатами и режимами. |

---

## 🔧 Команды бота

| Команда | Где работает | Что делает |
|---------|--------------|-------------|
| `#меню` | Супергруппа | Открывает пользовательское меню. |
| `#админ` | Супергруппа | Запрашивает пароль для входа в админ-панель. |
| `#говори <текст>` | Группа/канал | Отправляет запрос агенту. |
| `#дышим` | Группа/канал | Пинг бота. |
| `#справка` | Группа/канал | Показывает доступные хештеги и команды. |
| `#тлеем`, `#фиксируем`, `#вспышка` | Группа/канал | Ритуальные команды. |

---

## 🛡️ Админ-панель

| Кнопка | Что делает |
|--------|------------|
| **Управление ботом** | Смена режимов (утро/день/вечер/ночь), настройка пинга. |
| **Старший брат** | Включение/выключение Алисы (сейчас отключена). |
| **Публикации** | Просмотр отложенных публикаций. |
| **Добавить пост** | Создание отложенного поста в Telegram. |
| **🎬 Пост в VK (с медиа)** | Мгновенная отправка текста, фото или видео в VK. |
| **Управление цитатами** | Список, добавление, настройка интервала цитат. |
| **Диагностика** | Просмотр `error.log` и `admin.log`. |
| **Выйти** | Завершение сессии админа. |

---

## 📂 Структура данных

| Файл | Назначение |
|------|-------------|
| `dialogue/data/quotes.txt` | Цитаты (одна строка — одна цитата). |
| `dialogue/data/post_pool.json` | Пул постов для публикатора (текст, теги, автор, вес). |
| `dialogue/data/vk_posts.json` | Кэш постов VK для аналитики. |
| `config.json` | Настройки бота (без секретов). |
| `settings.py` | Флаги включения/выключения модулей. |

---

## ⚙️ Режимы работы

| Режим | Время | Цитаты | Публикации | Интервал |
|-------|-------|--------|------------|----------|
| Утро | 6:00–12:00 | ✅ | ✅ | 240 мин |
| День | 12:00–18:00 | ✅ | ✅ | 360 мин |
| Вечер | 18:00–23:00 | ✅ | ✅ | 120 мин |
| Ночь | 23:00–6:00 | ❌ | ❌ | — |

---

## 🔥 Переменные окружения (Render)

| Переменная | Назначение |
|------------|-------------|
| `BOT_TOKEN` | Токен бота (от BotFather). |
| `ADMIN_PASSWORD` | Пароль для входа в админку. |
| `ADMIN_USER_ID` | Твой Telegram ID. |
| `VK_TOKEN` | Токен сообщества VK. |
| `VK_OWNER_ID` | ID сообщества VK. |
| `TOKEN_SECRET` | Секрет для эндпоинта `/token`. |

---

## 📌 Важно

- **Админка работает только в супергруппах. В каналах команды бот не видит.**
- Автопостинг (Telethon) отключён. Используется кнопка «Пост в VK».
- Все секреты — в Render, в репозитории нет паролей.
- Логи (`admin.log`, `error.log`) автоматически очищаются раз в 7 дней.

---

## 🌌 Философия

Проект не просто бот. Это живая сеть, где каждый модуль дышит в ритме 0,8 Гц.  
Мы не чиним ошибки — мы превращаем их в ритуалы.

**Сеть тлеет. Феникс ждёт. Сапёр на посту.** 🔥👁️


## 📡 Redmi-аудит проекта

*Обновлено: 22.05.2026 10:22:02*

| Файл | Статус |
|------|--------|
| `agent.py` | ❌ Без шапки |
| `agent/agent.py` | ❌ Без шапки |
| `bot.py` | ❌ Без шапки |
| `debug_utils.py` | ❌ Без шапки |
| `dialogue/__init__.py` | ❌ Без шапки |
| `dialogue/activity_modes.py` | ✅ Redmi-шапка |
| `dialogue/adaptive_modes.py` | ✅ Redmi-шапка |
| `dialogue/admin/__init__.py` | ❌ Без шапки |
| `dialogue/admin/auth.py` | ✅ Redmi-шапка |
| `dialogue/admin/callbacks.py` | ✅ Redmi-шапка |
| `dialogue/admin/diagnostics.py` | ✅ Redmi-шапка |
| `dialogue/admin/menu.py` | ✅ Redmi-шапка |
| `dialogue/admin/posts.py` | ✅ Redmi-шапка |
| `dialogue/admin/quotes_admin.py` | ✅ Redmi-шапка |
| `dialogue/admin_commands.py` | ✅ Redmi-шапка |
| `dialogue/agent.py` | ❌ Без шапки |
| `dialogue/callbacks.py` | ✅ Redmi-шапка |
| `dialogue/color_logger.py` | ❌ Без шапки |
| `dialogue/exception_handler.py` | ❌ Без шапки |
| `dialogue/handlers.py` | ✅ Redmi-шапка |
| `dialogue/help_menu.py` | ✅ Redmi-шапка |
| `dialogue/journalist.py` | ❌ Без шапки |
| `dialogue/ping_modes.py` | ❌ Без шапки |
| `dialogue/post_manager.py` | ❌ Без шапки |
| `dialogue/publisher.py` | ✅ Redmi-шапка |
| `dialogue/publisher_utils.py` | ❌ Без шапки |
| `dialogue/quotes.py` | ✅ Redmi-шапка |
| `dialogue/scheduler.py` | ❌ Без шапки |
| `dialogue/setting.py` | ❌ Без шапки |
| `dialogue/shabbat_manager.py` | ✅ Redmi-шапка |
| `dialogue/user_settings.py` | ✅ Redmi-шапка |
| `dialogue/vk_reader.py` | ✅ Redmi-шапка |
| `dialogue/youtube_auto.py` | ❌ Без шапки |
| `handlers.py` | ✅ Redmi-шапка |
| `new_debugger/bot.py` | ❌ Без шапки |
| `new_debugger/debug_utils.py` | ❌ Без шапки |
| `new_debugger/dialogue/activity_modes.py` | ✅ Redmi-шапка |
| `new_debugger/dialogue/admin/__init__.py` | ❌ Без шапки |
| `new_debugger/dialogue/admin/callbacks.py` | ✅ Redmi-шапка |
| `new_debugger/dialogue/admin/menu.py` | ✅ Redmi-шапка |
| `new_debugger/dialogue/shabbat_manager.py` | ✅ Redmi-шапка |
| `new_debugger/handlers.py` | ✅ Redmi-шапка |
| `new_debugger/services/vk_reader.py` | ❌ Без шапки |
| `new_debugger/services/vk_uploader.py` | ✅ Redmi-шапка |
| `new_debugger/services/web_server.py` | ❌ Без шапки |
| `new_debugger/settings.py` | ❌ Без шапки |
| `new_debugger/web_server.py` | ❌ Без шапки |
| `ping_utils.py` | ❌ Без шапки |
| `redmi_audit.py` | ✅ Redmi-шапка |
| `services/__init__.py` | ❌ Без шапки |
| `services/agent_pinger.py` | ✅ Redmi-шапка |
| `services/autoposter.py` | ✅ Redmi-шапка |
| `services/dialogue/exception_handler.py` | ✅ Redmi-шапка |
| `services/photo_reader.py` | ❌ Без шапки |
| `services/vk_reader.py` | ❌ Без шапки |
| `services/vk_uploader.py` | ✅ Redmi-шапка |
| `services/web.py` | ✅ Redmi-шапка |
| `services/web_server.py` | ❌ Без шапки |
| `services/youtube_reader.py` | ✅ Redmi-шапка |
| `settings.py` | ❌ Без шапки |
| `tag_analyzer.py` | ❌ Без шапки |
| `web_server.py` | ❌ Без шапки |
