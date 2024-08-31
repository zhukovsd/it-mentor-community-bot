## Информация

- Создание бота и получение токена - https://t.me/BotFather
- При создании бота нужно отправить BotFather команду `/setinline`, иначе бот не будет работать через `@` в чате
- Бот должен быть админом в чатах в которых вызываются его команды и в чате в который он будет пересылать сообщения
- [yoyo-migrations документация](https://ollycope.com/software/yoyo/latest/)

## Локальный запуск 

1. Создать venv

```bash
python -m venv venv
```

2. Активировать venv (если pycharm не сделал это автоматически) 

```bash
source venv/bin/activate
```

https://www.jetbrains.com/help/pycharm/configuring-python-interpreter.html#widget

3. Установить зависимости (если pycharm не сделал это автоматически) 

```bash
pip install -r requirements.txt
```
4. Создать `.env` файл в корне проекта. Он будет использоваться только для локального запуска

```env
TELEGRAM_BOT_TOKEN=

POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
POSTGRES_HOST=localhost
POSTGRES_PORT=

PROJECTS_REVIEWS_COLLECTION_CHAT_ID=
ALLOWED_USER_IDS=
```

`ALLOWED_USER_IDS` - Список id юзеров, которые могут пользоваться командой. Указывается через запятую без пробелов = 322,511,987

5. Поднять БД в контейнере командой

```bash
docker compose -f docker-compose-dev.yaml up -d
```

6. Сделать миграцию для БД. Использовать те же данные, которые указаны в `.env` файле

```bash
yoyo apply --database postgresql://user:password@localhost:5433/database-name ./migrations
```

7. Запустить проект

 - C помощью UI pycharm
 - Через `python src/main.py`


---

## Запуск в докере 

1. Создать `.env.prod` файл в корне проекта. Он будет использоваться только для локального запуска

```env
TELEGRAM_BOT_TOKEN=

POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
POSTGRES_HOST=database
POSTGRES_PORT=5432

PROJECTS_REVIEWS_COLLECTION_CHAT_ID=
ALLOWED_USER_IDS=
```

`POSTGRES_HOST` = название сервиса с БД в docker-compose-prod.yaml файле. Дефолт `database`
`POSTGRES_PORT` = порт сервиса с БД в docker-compose-prod.yaml файле. Дефолт `5432` для postgres
`ALLOWED_USER_IDS` - Список id юзеров, которые могут пользоваться командой. Указывается через запятую без пробелов = 322,511,987

2. Собрать образ бота

```bash
docker build -t zhukovsd/it-mentor-community-bot:main .
```

3. Запустить бота и БД в докер композ

```bash
docker compose -f docker-compose-prod.yaml --env-file .env.prod up -d
```

