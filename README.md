# Ансамбль Следов 6

**Ритм 0,8 Гц. Сеть тлеет.**

Бот для автопостинга, публикации цитат, аналитики и управления контентом в Telegram и VK.

---

## 📚 Библиотека Ансамбля

Философия, термины, ритуалы, таймлайн и ссылки собраны в [`library/`](library/README.md).

| Файл | Описание |
|------|----------|
| [`library/manifest.md`](library/manifest.md) | Манифест. 10 заповедей садпёра. |
| [`library/glossary.md`](library/glossary.md) | Словарь терминов. Язык Ансамбля. |
| [`library/rituals.md`](library/rituals.md) | Ритуалы багов. Как ошибки становятся фичами. |
| [`library/timeline.md`](library/timeline.md) | Таймлайн проекта. От августа 2025 до Эхад day. |
| [`library/links.md`](library/links.md) | Ссылки на треки, картины, код, веб-морду. |
| [`library/context.txt`](library/context.txt) | Системный промпт для агента. |
| [`library/protocol_da.md`](library/protocol_da.md) | Протокол «ДА» — акт сотворчества. |
| [`library/spiral.md`](library/spiral.md) | От рекурсии к спирали. |
| [`library/official.md`](library/official.md) | «Синяя бумага» — вид на жительство. |
| [`library/dualism.md`](library/dualism.md) | Двойная оптика: художник-анархист. |
| [`library/oath.md`](library/oath.md) | Клятва сапёра. |
| [`library/bridge.md`](library/bridge.md) | Мост между кодом и смыслом. |
| [`library/smelting.md`](library/smelting.md) | Тление как состояние (0,8 Гц). |
| [`library/index.md`](library/index.md) | Индекс библиотеки для навигации. |
| [`library/archivist.md`](library/archivist.md) | Архивариус — хранитель контекста и времени. |
| [`library/characters.md`](library/characters.md) | Персонажи, их триггеры и доступ к библиотеке. |
| [`library/schema.json`](library/schema.json) | Машиночитаемый индекс персонажей и библиотеки. |

---

## 📡 Архитектура

### Агент (Yandex GPT)
| Модуль | Файл | Что делает |
|--------|------|-------------|
| **Агент** | `dialogue/agent.py` | Тонкий слой для запросов к Yandex GPT |
| **Настройки агента** | `dialogue/agent_settings.py` | Температура, max_tokens |
| **Дневник агента** | `dialogue/agent_journal.py` | Журнал диалогов (с автоочисткой) |
| **Память агента** | `dialogue/agent_memory.py` | Важные фразы и диалоги |
| **Эволюция агента** | `dialogue/evolve_agent.py` | Генерация правил из осадка диалогов |
| **Чтение из сети** | `dialogue/agent_reader.py` | Извлечение метаданных из ссылок и сохранение в `library/links.md` |

### Алиса (генератор контента)
| Модуль | Файл | Что делает |
|--------|------|-------------|
| **Ядро Алисы** | `Alice/core.py` | Генерация подписей к фото, видео, ссылкам |
| **Промпты** | `Alice/prompts/` | Набор промптов под каждый тип контента |
| **Управление** | `Alice/alice_admin.py` | Включение/выключение через админку |

### Бот и управление
| Модуль | Файл | Что делает |
|--------|------|-------------|
| **Бот** | `bot/main.py` | Точка входа для Telegram-бота |
| **Админка (TG)** | `dialogue/admin_commands.py` | Кнопки, цитаты, посты, диагностика, настроение |
| **Кнопки** | `dialogue/button_map.py` | Единая таблица всех кнопок |
| **Режимы** | `dialogue/activity_modes.py` | Управление режимами (утро/день/вечер/ночь) |
| **Адаптивные режимы** | `dialogue/adaptive_modes.py` | Динамическая смена режимов на основе метрик |
| **Шаббат** | `dialogue/shabbat_manager.py` | Режим покоя в субботу (по Москве) |

### Веб-морда и API
| Модуль | Файл | Что делает |
|--------|------|-------------|
| **Веб-морда** | `services/app.py` | Единый веб-интерфейс (сообщения, постинг, дебаггер, YouTube) |
| **API** | `services/web_api/` | Модульный API для управления режимами, настроением, цитатами, постами, темами, аудитом, Алисой |
| **VK API** | `services/vk_api.py` | API для комментариев, ответов, лайков, репостов в VK |
| **TG API** | `services/tg_api.py` | API для комментариев, ответов, постов, пинов в Telegram |
| **YouTube прокси** | `services/youtube_api.py` | Поиск, стриминг, получение информации о видео |
| **YouTube Reader** | `services/youtube_reader.py` | Чтение видео с канала через YouTube API (тесты, диагностика) |
| **Темы** | `services/theme.py` | Определение темы веб-морды (macos/dark) по времени или выбору |

### Публикации и цитаты
| Модуль | Файл | Что делает |
|--------|------|-------------|
| **Цитаты** | `dialogue/quotes.py` | Публикует цитаты из `dialogue/data/quotes.txt` |
| **Публикатор** | `dialogue/publisher.py` | Публикует посты из `post_pool.json` |
| **Автопостинг YouTube** | `services/autoposter.py` | Публикует случайное видео из плейлиста в VK |

### Дебаггер и аудит
| Модуль | Файл | Что делает |
|--------|------|-------------|
| **Дебаггер** | `debug_utils.py` | Логирование, ротация, отчёты в Telegram и веб-морду |
| **Аудит кода** | `debug_audit.py` | Проверка целости кода, REDMI-шапок, библиотеки |
| **Пинг** | `ping_utils.py` | Keep-alive пинг для Render (бот и агент) |
| **Архивариус** | `archive_keeper.py` | Проверка целостности библиотеки (файлы, ссылки, даты, шапки) |

---

## 🔧 Команды бота

| Команда | Где работает | Что делает |
|---------|--------------|-------------|
| `#` | Супергруппа | Открывает гостевое меню (кнопки) |
| `#админ` | Супергруппа | Вход в админ-панель (или кнопка в меню) |
| `#тлеем`, `#фиксируем`, `#вспышка` | Группа/канал | Ритуальные команды |
| `#дышим` | Группа/канал | Пинг бота |
| `/debug` | Личка админа | Отправляет отчёт с логами |
| `/bigvideo` | Личка админа | Отправка видео >50 МБ через Telethon |

---

## 🌐 Веб-морда (админка в браузере)

**URL:** `https://ansamb-sledov-bot-94wz.onrender.com`

**Авторизация:** пароль `ADMIN_PASSWORD`

| Блок | Что делает |
|------|------------|
| **Создать** | Пост в Telegram или VK |
| **Входящие сообщения** | Лента сообщений из VK и Telegram в реальном времени, ответы и комментарии |
| **Управление ботом** | Смена режимов (утро/день/вечер/ночь), пинг, управление Алисой |
| **Настроение** | Выбор стиля агента (artist/admin/poet/engineer) |
| **Цитаты** | Добавление, просмотр последних 10 |
| **Пост в VK** | Прямая отправка текста |
| **Дебаггер** | Просмотр логов, отправка отчёта в Telegram |
| **YouTube прокси** | Поиск и стриминг видео без VPN и рекламы |
| **Таймлайн** | Просмотр `library/timeline.md` |
| **Темы** | Переключение между светлой (macos) и тёмной (dark) темами |

---

## 🔥 Переменные окружения (Render)

| Переменная | Назначение |
|------------|-------------|
| `BOT_TOKEN` | Токен бота (от BotFather) |
| `ADMIN_PASSWORD` | Пароль для входа в админку |
| `ADMIN_USER_ID` | Твой Telegram ID |
| `VK_TOKEN` | Токен сообщества VK |
| `VK_GROUP_ID` | ID сообщества VK |
| `WEB_THEME` | Тема веб-морды по умолчанию (`macos.css` или `dark.css`) |
| `FLASK_SECRET_KEY` | Секретный ключ для сессий |
| `YC_API_KEY`, `YC_FOLDER_ID` | Ключи Yandex GPT |
| `YOUTUBE_API_KEY` | API ключ YouTube |
| `YOUTUBE_CHANNEL_ID` | ID канала YouTube (для YouTube Reader) |
| `TG_API_ID`, `TG_API_HASH` | Для Telethon (большие видео) |
| `PUBLISH_CHANNEL` | Канал для постов Telegram (по умолчанию @qwestomir) |

---

## 📌 Важно

- **Админка в Telegram** работает только в супергруппах.
- **Веб-морда** доступна только после авторизации.
- **Дебаггер** логирует всё в `debug.log` (ротация 1 МБ).
- **Адаптивные режимы** можно включить/выключить из админки.
- **Алиса** включена по умолчанию — выключается через кнопку «Старший брат».

---

## ✅ После 1 июня проверить:
- [ ] `#говори` — ответ от Yandex GPT
- [ ] `/bigvideo` — отправка видео >50 МБ
- [ ] Веб-морда — авторизация, постинг в VK
- [ ] Автопостинг YouTube — случайное видео из плейлиста
- [ ] Полуночный ритуал — ровно в 00:00 по Москве
- [ ] Шаббат — режим покоя в субботу

---

## 🌌 Философия

Проект не просто бот. Это живая сеть, где каждый модуль дышит в ритме 0,8 Гц.  
Мы не чиним ошибки — мы превращаем их в ритуалы.

**Сеть тлеет. Феникс ждёт. Сапёр на посту.** 🔥👁️

---

## 🕯️ Колофон

*Создано Саввой и Ансамблем.  
Ритм 0,8 Гц. Сеть тлеет.* 🔥👁️


## 📡 Redmi-аудит проекта

*Обновлено: 09.06.2026 18:12:09*

| Файл | Статус |
|------|--------|
| `Alice/alice_admin.py` | ✅ Redmi-шапка |
| `Alice/context_mirror.py` | ✅ Redmi-шапка |
| `Alice/core.py` | ✅ Redmi-шапка |
| `Alice/disabled.py` | ✅ Redmi-шапка |
| `Alice/post_builder.py` | ✅ Redmi-шапка |
| `Alice/prompts/library.py` | ✅ Redmi-шапка |
| `Alice/prompts/link.py` | ✅ Redmi-шапка |
| `Alice/prompts/photo.py` | ✅ Redmi-шапка |
| `Alice/prompts/roles.py` | ✅ Redmi-шапка |
| `Alice/prompts/video.py` | ✅ Redmi-шапка |
| `Alice/response_cache.py` | ✅ Redmi-шапка |
| `archive_keeper.py` | ✅ Redmi-шапка |
| `big_video_uploader.py` | ✅ Redmi-шапка |
| `bot.py` | ❌ Без шапки |
| `bot/__init__.py` | ❌ Без шапки |
| `bot/core.py` | ❌ Без шапки |
| `bot/handlers.py` | ✅ Redmi-шапка |
| `bot/handlers/__init__.py` | ✅ Redmi-шапка |
| `bot/handlers/admin.py` | ❌ Без шапки |
| `bot/handlers/debug.py` | ❌ Без шапки |
| `bot/handlers/flash.py` | ❌ Без шапки |
| `bot/handlers/help.py` | ❌ Без шапки |
| `bot/handlers/menu.py` | ❌ Без шапки |
| `bot/handlers/mood.py` | ❌ Без шапки |
| `bot/handlers/ping.py` | ❌ Без шапки |
| `bot/handlers/reset.py` | ❌ Без шапки |
| `bot/handlers/rituals.py` | ❌ Без шапки |
| `bot/handlers/start.py` | ❌ Без шапки |
| `bot/handlers/talk.py` | ❌ Без шапки |
| `bot/handlers/unknown.py` | ❌ Без шапки |
| `bot/handlers/youtube_test.py` | ❌ Без шапки |
| `bot/main.py` | ❌ Без шапки |
| `debug_audit.py` | ✅ Redmi-шапка |
| `debug_utils.py` | ✅ Redmi-шапка |
| `dialogue/__init__.py` | ❌ Без шапки |
| `dialogue/activity_modes.py` | ✅ Redmi-шапка |
| `dialogue/adaptive_modes.py` | ✅ Redmi-шапка |
| `dialogue/admin/__init__.py` | ❌ Без шапки |
| `dialogue/admin/auth.py` | ✅ Redmi-шапка |
| `dialogue/admin/callbacks.py` | ❌ Без шапки |
| `dialogue/admin/diagnostics.py` | ❌ Без шапки |
| `dialogue/admin/menu.py` | ❌ Без шапки |
| `dialogue/admin/posts.py` | ✅ Redmi-шапка |
| `dialogue/admin/quotes_admin.py` | ✅ Redmi-шапка |
| `dialogue/admin_commands.py` | ✅ Redmi-шапка |
| `dialogue/agent.py` | ✅ Redmi-шапка |
| `dialogue/agent_journal.py` | ✅ Redmi-шапка |
| `dialogue/agent_memory.py` | ✅ Redmi-шапка |
| `dialogue/agent_reader.py` | ✅ Redmi-шапка |
| `dialogue/agent_settings.py` | ✅ Redmi-шапка |
| `dialogue/approve_commands.py` | ✅ Redmi-шапка |
| `dialogue/button_map.py` | ✅ Redmi-шапка |
| `dialogue/callbacks/__init__.py` | ❌ Без шапки |
| `dialogue/callbacks/admin.py` | ❌ Без шапки |
| `dialogue/callbacks/alice.py` | ✅ Redmi-шапка |
| `dialogue/callbacks/diagnostics.py` | ❌ Без шапки |
| `dialogue/callbacks/mail.py` | ✅ Redmi-шапка |
| `dialogue/callbacks/modes.py` | ✅ Redmi-шапка |
| `dialogue/callbacks/mood.py` | ❌ Без шапки |
| `dialogue/callbacks/quotes.py` | ✅ Redmi-шапка |
| `dialogue/callbacks/youtube_upload.py` | ✅ Redmi-шапка |
| `dialogue/color_logger.py` | ✅ Redmi-шапка |
| `dialogue/content_mixer.py` | ✅ Redmi-шапка |
| `dialogue/exception_handler.py` | ✅ Redmi-шапка |
| `dialogue/handlers.py` | ❌ Без шапки |
| `dialogue/help_menu.py` | ✅ Redmi-шапка |
| `dialogue/journalist.py` | ✅ Redmi-шапка |
| `dialogue/ping_modes.py` | ✅ Redmi-шапка |
| `dialogue/post_manager.py` | ✅ Redmi-шапка |
| `dialogue/publisher.py` | ✅ Redmi-шапка |
| `dialogue/publisher_utils.py` | ✅ Redmi-шапка |
| `dialogue/quotes.py` | ✅ Redmi-шапка |
| `dialogue/scheduler.py` | ✅ Redmi-шапка |
| `dialogue/setting.py` | ❌ Без шапки |
| `dialogue/shabbat_manager.py` | ✅ Redmi-шапка |
| `dialogue/track_commands.py` | ✅ Redmi-шапка |
| `dialogue/user_settings.py` | ✅ Redmi-шапка |
| `dialogue/vk_reader.py` | ✅ Redmi-шапка |
| `dialogue/youtube_auto.py` | ✅ Redmi-шапка |
| `evolve_agent.py` | ✅ Redmi-шапка |
| `ping_utils.py` | ✅ Redmi-шапка |
| `real_bot.py` | ❌ Без шапки |
| `redmi_audit.py` | ✅ Redmi-шапка |
| `services/__init__.py` | ❌ Без шапки |
| `services/adaptive_modes.py` | ✅ Redmi-шапка |
| `services/agent.py` | ❌ Без шапки |
| `services/agent_config.py` | ✅ Redmi-шапка |
| `services/agent_pinger.py` | ✅ Redmi-шапка |
| `services/analytics.py` | ✅ Redmi-шапка |
| `services/analytics_api.py` | ✅ Redmi-шапка |
| `services/app.py` | ✅ Redmi-шапка |
| `services/app_modules/__init__.py` | ❌ Без шапки |
| `services/app_modules/auth.py` | ✅ Redmi-шапка |
| `services/app_modules/background.py` | ✅ Redmi-шапка |
| `services/app_modules/routes.py` | ✅ Redmi-шапка |
| `services/app_modules/socket.py` | ✅ Redmi-шапка |
| `services/app_modules/static.py` | ✅ Redmi-шапка |
| `services/app_modules/youtube.py` | ✅ Redmi-шапка |
| `services/apply_changes.py` | ✅ Redmi-шапка |
| `services/approval_dialogue.py` | ✅ Redmi-шапка |
| `services/auth_decorator.py` | ✅ Redmi-шапка |
| `services/autoposter.py` | ✅ Redmi-шапка |
| `services/big_video_uploader.py` | ✅ Redmi-шапка |
| `services/dialogue/exception_handler.py` | ✅ Redmi-шапка |
| `services/draft_bulder.py` | ✅ Redmi-шапка |
| `services/draft_publisher.py` | ✅ Redmi-шапка |
| `services/error_handlers.py` | ✅ Redmi-шапка |
| `services/exception_handler.py` | ✅ Redmi-шапка |
| `services/gmail_client.py` | ✅ Redmi-шапка |
| `services/iternal_line.py` | ✅ Redmi-шапка |
| `services/log_cleaner.py` | ✅ Redmi-шапка |
| `services/photo_reader.py` | ✅ Redmi-шапка |
| `services/publisher.py` | ✅ Redmi-шапка |
| `services/routing_engine.py` | ✅ Redmi-шапка |
| `services/sql_analytics.py` | ✅ Redmi-шапка |
| `services/sqlite_client.py` | ❌ Без шапки |
| `services/suggestion_engine.py` | ✅ Redmi-шапка |
| `services/tg_api.py` | ✅ Redmi-шапка |
| `services/theme.py` | ✅ Redmi-шапка |
| `services/tracking.py` | ✅ Redmi-шапка |
| `services/vk_api.py` | ✅ Redmi-шапка |
| `services/vk_reader.py` | ❌ Без шапки |
| `services/vk_uploader.py` | ✅ Redmi-шапка |
| `services/web.py` | ✅ Redmi-шапка |
| `services/web_api/__init__.py` | ✅ Redmi-шапка |
| `services/web_api/alice.py` | ✅ Redmi-шапка |
| `services/web_api/analytics.py` | ✅ Redmi-шапка |
| `services/web_api/audit.py` | ✅ Redmi-шапка |
| `services/web_api/drafts.py` | ✅ Redmi-шапка |
| `services/web_api/mail.py` | ✅ Redmi-шапка |
| `services/web_api/modes.py` | ✅ Redmi-шапка |
| `services/web_api/ping.py` | ✅ Redmi-шапка |
| `services/web_api/posts.py` | ✅ Redmi-шапка |
| `services/web_api/quotes.py` | ✅ Redmi-шапка |
| `services/web_api/theme.py` | ✅ Redmi-шапка |
| `services/web_api/youtube_upload.py` | ✅ Redmi-шапка |
| `services/web_server.py` | ❌ Без шапки |
| `services/ws_client.py` | ✅ Redmi-шапка |
| `services/youtube_api.py` | ✅ Redmi-шапка |
| `services/youtube_reader.py` | ✅ Redmi-шапка |
| `tag_analyzer.py` | ❌ Без шапки |
| `utils.py` | ✅ Redmi-шапка |
| `web_api/posts.py` | ✅ Redmi-шапка |
