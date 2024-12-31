# Telegram-бот DodoIS

Телеграм-бот для получения информации о пиццериях Dodo Pizza с использованием старого публичного API Dodo IS.

## Стек

-   **Фреймворк бота**: `aiogram`
-   **База данных**: `PostgreSQL` с использованием `AsyncPG` и `SQLAlchemy`
-   **Запросы к API**: `aiohttp`
-   **Кэширование**: `aiocache`
-   **Планировщик**: `APScheduler`

## Установка и запуск

1. **Клонирование репозитория**  
   Склонируйте репозиторий проекта:
    ```bash
    gh repo clone damirTAG/dodobot
    cd <куда сохранили>
    ```
2. **.env файл**  
   Создайте файл `.env`, указав в нём все параметры, описанные в `.env.example`.
   Обязательно создайте базу данных в PostgreSQL и правильно укажите имя базы данных в переменной `PGNAME`.

3. **Установка зависимостей**
    ```bash
    pip install -r requirements.txt
    ```
4. **Запуск**
    ```bash
    python main.py
    ```

## Деплой на Railway

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/template/jwt-u-?referralCode=SBFsUi)
