from dotenv import load_dotenv
import os

load_dotenv()

# Секретные данные
API_FGP_GITHUB = os.environ.get("API_FGP_GITHUB")
# Данные ниже - для тестирования
# (их можно передавать не из ENV файла, а напрямую из кода
# Например когда данные приходят из клиента,
# то в методы будут передаваться данные которые пришли из клиента, а не указанные ниже)
USER_NAME_PARSING_REPO = os.environ.get('USER_NAME_PARSING_REPO')
REPO_NAME = os.environ.get('REPO_NAME')
FILE_PATH = os.environ.get('FILE_PATH')
