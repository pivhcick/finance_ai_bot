# Trading Signals Telegram Bot

Telegram-бот для автоматической рассылки торговых сигналов на основе технического анализа для криптовалют, акций США и ETF.

## Текущий статус проекта

✅ **Этап 0: Подготовка окружения** - Завершен
✅ **Этап 1: Базовый Telegram бот** - Завершен
✅ **Этап 2: База данных и управление пользователями** - Завершен

### Реализованный функционал:

- ✅ Подписка/отписка пользователей (`/subscribe`, `/unsubscribe`)
- ✅ Проверка статуса подписки (`/status`)
- ✅ Справка по боту (`/help`)
- ✅ База данных SQLite для хранения пользователей
- ✅ Логирование всех операций

### В разработке:

- ⏳ Технические индикаторы (RSI, MACD, SMA, EMA, OBV, VROC)
- ⏳ Алгоритмы генерации сигналов
- ⏳ Автоматическая рассылка сигналов
- ⏳ Планировщик задач

## Быстрый старт

### 1. Установка зависимостей

```bash
# Создание виртуального окружения
python3 -m venv venv

# Активация виртуального окружения
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate  # для Windows

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Регистрация Telegram бота

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям (придумайте имя и username для бота)
4. Сохраните полученный токен

### 3. Настройка переменных окружения

```bash
# Скопируйте пример файла
cp .env.example .env

# Откройте .env и добавьте ваш токен
nano .env
```

Минимальная конфигурация в `.env`:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
DATABASE_URL=sqlite:///./bot_database.db
```

### 4. Запуск бота

```bash
# Убедитесь, что виртуальное окружение активировано
source venv/bin/activate

# Запустите бота
python main.py
```

Вы должны увидеть:

```
2024-12-16 12:00:00 - finance_ai_bot - INFO - Starting Trading Signals Bot...
2024-12-16 12:00:00 - finance_ai_bot - INFO - Initializing database...
2024-12-16 12:00:00 - src.database.repository - INFO - Database connection initialized
2024-12-16 12:00:00 - src.database.repository - INFO - Database tables created successfully
2024-12-16 12:00:00 - __main__ - INFO - Bot handlers registered successfully
2024-12-16 12:00:00 - __main__ - INFO - Bot is starting to poll...
```

### 5. Тестирование бота

Откройте Telegram и найдите вашего бота, затем протестируйте команды:

1. `/start` - Приветственное сообщение
2. `/subscribe` - Подписаться на рассылку
3. `/status` - Проверить статус подписки
4. `/unsubscribe` - Отписаться от рассылки
5. `/help` - Справка

## Структура проекта

```
finance_ai_bot/
├── src/
│   ├── bot/
│   │   ├── handlers.py          # Обработчики команд бота
│   │   └── messages.py          # Шаблоны сообщений
│   ├── database/
│   │   ├── models.py            # Модели БД (User, Signal)
│   │   └── repository.py        # Работа с БД
│   └── utils/
│       ├── config.py            # Конфигурация
│       └── logger.py            # Логирование
├── .env                         # Переменные окружения (не в git)
├── .env.example                 # Пример настроек
├── main.py                      # Точка входа
├── requirements.txt             # Зависимости
├── CLAUDE.md                    # Архитектурная документация
└── tasks.md                     # План работ
```

## Конфигурация

Все настройки в `.env` файле:

```env
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Database
DATABASE_URL=sqlite:///./bot_database.db

# Settings
ANALYSIS_INTERVAL_HOURS=1
MIN_CONFIDENCE=60
TIMEZONE=UTC
LOG_LEVEL=INFO

# Assets to track (будет использоваться на следующих этапах)
CRYPTO_SYMBOLS=BTC-USD,ETH-USD,SOL-USD,DOGE-USD
STOCK_SYMBOLS=AAPL,TSLA,MSFT,NVDA,AMZN
ETF_SYMBOLS=VTI,TQQQ,SPY,QQQ
```

## Технологии

- **Python 3.11+** - Основной язык
- **python-telegram-bot 20.7** - Telegram Bot API
- **SQLAlchemy 2.0** - ORM для работы с БД
- **SQLite** - База данных (для разработки)
- **PostgreSQL** - База данных (для продакшн)

## Следующие этапы разработки

Согласно [tasks.md](tasks.md):

1. **Этап 3:** Технические индикаторы (RSI, MACD, SMA, EMA, OBV, VROC)
2. **Этап 4:** Алгоритм генерации сигналов для криптовалют
3. **Этап 5:** Форматирование и рассылка сигналов
4. **Этап 6:** Планировщик задач (автоматический анализ)
5. **Этап 7:** Алгоритмы для акций и ETF
6. **Этап 8:** Улучшения и оптимизация
7. **Этап 9:** Деплой на Railway.app

## Документация

- [CLAUDE.md](CLAUDE.md) - Полная архитектурная документация
- [tasks.md](tasks.md) - Детальный план работ с чек-поинтами

## Лицензия

Проект разработан для личного использования.

## Дисклеймер

⚠️ **Важно:** Сигналы носят информационный характер и не являются инвестиционной рекомендацией. Торгуйте на свои риски.
