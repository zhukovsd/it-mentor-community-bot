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

JSON_KEY_GOOGLE_API='{JSON-string}'
ADD_TO_SHEET='name_sheet'
```

`ADD_TO_SHEET` - Строка без пробелов содержащая в себе имя файла google sheet из google drive который подключается с помощью google api.  
`ALLOWED_USER_IDS` - Список id юзеров, которые могут пользоваться командой. Указывается через запятую без пробелов = 322,511,987
`PROJECTS_REVIEWS_COLLECTION_CHAT_ID` - ID Чата куда пересылаем ответное сообщение. Указывать можно в виде списка по аналогии с `ALLOWED_USER_IDS`
- **Не добавлять сюда** ID другого **чат бота** или того же самого который используется

`JSON_KEY_GOOGLE_API` - JSON строка формата:
```json
{
  "type": "service_account",
  "project_id": "it-menthor-community-bot",
  "private_key_id": "",
  "private_key": "",
  "client_email": "",
  "client_id": "",
  "auth_uri": "",
  "token_uri": "",
  "auth_provider_x509_cert_url": "",
  "client_x509_cert_url": "",
  "universe_domain": ""
}
```
4.1. Как Получить JSON токен google API для подключения?
Для этого Нужно перейти на:
- https://console.cloud.google.com/projectselector2/apis/dashboard?supportedpurview=project
- Далее в: API & Services > Переходим: Credentials > Создаем: Create credentials > Service account key
- Заполняем все необходимые поля
- Нажимаем Done 
- Нажимаем “Manage service accounts” над Service Accounts.
- В открывшейся таблице кликаем 3 точки > Manage Keys
- ADD KEY > Create new key > JSON
Мы получим JSON файл с API Key
##### Обязательно
Нужно будет добавить к пользователям Email из API Key в ключе `client_email`
Делать это стоит конкретно к таблице с которой мы будем работать, либо к папке с таблицами в которой мы будем работать

Так же надо перейти в 
- API & Servises > Library
- Ввести `Google Drive API` и `Google Sheets API` в поиск
- И включить эти две либы (Нажать Enable) 
- Для работы с google docks надо будет 

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

JSON_KEY_GOOGLE_API='{JSON-string}'
ADD_TO_SHEET='name_sheet'
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

