from dotenv import load_dotenv
import os

load_dotenv()

# Секретные данные
JSON_KEY_GOOGLE_API: str | None = os.environ.get('JSON_KEY_GOOGLE_API')
# Имя таблицы в которую добавляем
ADD_TO_SHEET: str | None = os.environ.get('ADD_TO_SHEET')

if JSON_KEY_GOOGLE_API is None:
    raise EnvironmentError("'JSON_KEY_GOOGLE_API' is None")
if ADD_TO_SHEET is None:
    raise EnvironmentError("'ADD_TO_SHEET' is None")
# Данные ниже - для тестирования
# (их можно передавать не из ENV файла, а напрямую из кода
# Например когда данные приходят из клиента,
# то в методы будут передаваться данные которые пришли из клиента, а не указанные ниже)
USER_NAME_PARSING_REPO = os.environ.get('USER_NAME_PARSING_REPO')
REPO_NAME = os.environ.get('REPO_NAME')
FILE_PATH = os.environ.get('FILE_PATH')
URL_REPO = os.environ.get('URL_REPO')
