## Локальный запуск 

1. Создать venv

```bash
python -m venv venv
```

2. Активировать venv (если pycharm не сделал это автоматически) 

https://www.jetbrains.com/help/pycharm/configuring-python-interpreter.html#widget

3. Установить зависимости (если pycharm не сделал это автоматически) 

```bash
pip install -r requirements.txt
```
4. Создать `.env` файл в корне проекта

```env
TELEGRAM_BOT_TOKEN=
```

5. Запустить проект

 - C помощью UI pycharm
 - Через `python main.py`

